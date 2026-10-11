"""Isolated API fixture for each test."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from opsdesk_api.main import create_app
from opsdesk_api.repositories.memory import InMemoryRepository


@pytest.fixture
def app() -> FastAPI:
    return create_app(repository=InMemoryRepository())


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app, raise_server_exceptions=False)
