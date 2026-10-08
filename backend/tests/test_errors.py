from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from utility.base_exceptions import BadRequestError, ServiceUnavailableError


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    async def bad_request():
        raise BadRequestError("That URL is not valid.")

    async def dependency_down():
        raise ServiceUnavailableError("redis at 10.0.0.5 refused the connection")

    async def crash():
        raise RuntimeError("db password=hunter2")

    async def item(item_id: int):
        return {"item_id": item_id}

    app.add_api_route("/test/bad-request", bad_request)
    app.add_api_route("/test/dependency-down", dependency_down)
    app.add_api_route("/test/crash", crash)
    app.add_api_route("/test/items/{item_id}", item)
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client


def test_client_errors_return_their_message(client):
    response = client.get("/test/bad-request")
    error = response.json()["error"]

    assert response.status_code == 400
    assert error["code"] == "BAD_REQUEST"
    assert error["message"] == "That URL is not valid."
    assert error["request_id"] == response.headers["X-Request-ID"]


@pytest.mark.parametrize(
    ("path", "status", "code", "secret"),
    [
        ("/test/dependency-down", 503, "SERVICE_UNAVAILABLE", "10.0.0.5"),
        ("/test/crash", 500, "INTERNAL_ERROR", "hunter2"),
    ],
)
def test_server_errors_hide_internal_details(client, path, status, code, secret):
    response = client.get(path)
    error = response.json()["error"]

    assert response.status_code == status
    assert error["code"] == code
    assert secret not in response.text
    assert error["request_id"] == response.headers["X-Request-ID"]


def test_validation_errors_explain_what_was_wrong(client):
    response = client.get("/test/items/not-a-number")
    error = response.json()["error"]

    assert response.status_code == 422
    assert error["code"] == "VALIDATION_ERROR"
    assert error["details"][0]["loc"] == ["path", "item_id"]


def test_unknown_routes_use_the_same_error_shape(client):
    response = client.get("/does-not-exist")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"
