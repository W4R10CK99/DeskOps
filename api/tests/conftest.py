"""Isolated API fixture for each test."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from opsdesk_api.auth import CurrentMembership, current_membership
from opsdesk_api.config import DEFAULT_WORKSPACE_ID
from opsdesk_api.main import create_app
from opsdesk_api.repositories.memory import InMemoryRepository


@pytest.fixture
def app() -> FastAPI:
    application = create_app(repository=InMemoryRepository())
    # These contract tests focus on business/API behavior with the explicit memory adapter.
    # Authentication and membership enforcement have dedicated tests.
    application.dependency_overrides[current_membership] = lambda: CurrentMembership(
        DEFAULT_WORKSPACE_ID,
        None,
        "https://opsdesk-test.example/",
        "contract-test-user",
        "owner",
        "OpsDesk Test",
    )
    return application


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app, raise_server_exceptions=False)
