import os
from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

os.environ["SKIM_ENV"] = "test"


@pytest.fixture
def app() -> FastAPI:
    from app.app import get_skim_app

    return get_skim_app()


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
