import re

import pytest

from app.middlewares import resolve_request_id


def test_a_safe_incoming_request_id_is_echoed_back(client):
    response = client.get("/healthCheck", headers={"X-Request-ID": "trace-abc_123"})

    assert response.headers["X-Request-ID"] == "trace-abc_123"


@pytest.mark.parametrize("incoming", [None, "", "has spaces", "x" * 65, "line\nbreak", '{"a":1}'])
def test_missing_or_unsafe_request_ids_are_replaced(incoming):
    request_id = resolve_request_id(incoming)

    assert request_id != incoming
    assert re.fullmatch(r"[0-9a-f]{32}", request_id)


def test_every_response_carries_security_headers(client):
    response = client.get("/does-not-exist")

    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "no-referrer"
    assert "Strict-Transport-Security" not in response.headers
