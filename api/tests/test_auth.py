"""Provider-independent OIDC token verification tests."""

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import HTTPException
from fastapi.testclient import TestClient

from opsdesk_api import auth
from opsdesk_api.config import Settings
from opsdesk_api.main import create_app
from opsdesk_api.repositories.memory import InMemoryRepository


@pytest.fixture
def signing_keys():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


def _request() -> SimpleNamespace:
    return SimpleNamespace(
        app=SimpleNamespace(
            state=SimpleNamespace(
                settings=Settings(
                    oidc_issuer="https://tenant.example/",
                    oidc_audience="https://opsdesk.example/api",
                    oidc_jwks_url="https://tenant.example/.well-known/jwks.json",
                )
            )
        )
    )


def _token(
    key, *, audience="https://opsdesk.example/api", expires_in=300, issuer="https://tenant.example/"
):
    now = datetime.now(UTC)
    return jwt.encode(
        {
            "iss": issuer,
            "aud": audience,
            "sub": "auth0|user-123",
            "iat": now,
            "exp": now + timedelta(seconds=expires_in),
        },
        key,
        algorithm="RS256",
        headers={"kid": "test-key"},
    )


def _use_key(monkeypatch, key):
    class TestJwksClient:
        def __init__(self, _url, **_kwargs):
            pass

        def get_signing_key_from_jwt(self, _token):
            return SimpleNamespace(key=key.public_key())

    monkeypatch.setattr(auth, "PyJWKClient", TestJwksClient)


def test_valid_signed_access_token_returns_issuer_and_subject(monkeypatch, signing_keys) -> None:
    _use_key(monkeypatch, signing_keys)

    identity = auth.verify_access_token(_token(signing_keys), _request())

    assert identity.issuer == "https://tenant.example/"
    assert identity.subject == "auth0|user-123"


@pytest.mark.parametrize(
    "claims",
    [
        {"audience": "https://different.example/api"},
        {"expires_in": -1},
        {"issuer": "https://attacker.example/"},
    ],
)
def test_wrong_audience_expired_and_wrong_issuer_tokens_are_rejected(
    monkeypatch, signing_keys, claims
) -> None:
    _use_key(monkeypatch, signing_keys)

    with pytest.raises(HTTPException) as caught:
        auth.verify_access_token(_token(signing_keys, **claims), _request())

    assert caught.value.status_code == 401
    assert caught.value.detail["code"] == "invalid_token"


def test_invalid_signature_is_rejected(monkeypatch, signing_keys) -> None:
    _use_key(monkeypatch, signing_keys)
    attacker_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    with pytest.raises(HTTPException) as caught:
        auth.verify_access_token(_token(attacker_key), _request())

    assert caught.value.status_code == 401


def test_identity_provider_must_be_configured() -> None:
    request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(settings=Settings())))
    with pytest.raises(HTTPException) as caught:
        auth.verify_access_token("untrusted", request)
    assert caught.value.status_code == 503
    assert caught.value.detail["code"] == "identity_not_configured"


def test_protected_api_rejects_anonymous_and_malformed_credentials() -> None:
    app = create_app(
        settings=Settings(
            oidc_issuer="https://tenant.example/",
            oidc_audience="https://opsdesk.example/api",
        ),
        repository=InMemoryRepository(),
    )
    with TestClient(app) as client:
        assert client.get("/health").status_code == 200
        anonymous = client.get("/api/v1/projects")
        malformed = client.get("/api/v1/projects", headers={"Authorization": "Bearer invalid"})

    assert anonymous.status_code == 401
    assert anonymous.json()["error"]["code"] == "authentication_required"
    assert malformed.status_code == 401
    assert malformed.json()["error"]["code"] == "invalid_token"
