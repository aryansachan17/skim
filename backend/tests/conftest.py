import os
from collections.abc import Callable, Iterator

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


@pytest.fixture
def set_setting() -> Iterator[Callable[[str, object], None]]:
    from config import settings

    originals: dict[str, object] = {}

    def _set(name: str, value: object) -> None:
        originals.setdefault(name, settings.get(name))
        settings.set(name, value)

    yield _set
    for name, value in originals.items():
        settings.set(name, value)
