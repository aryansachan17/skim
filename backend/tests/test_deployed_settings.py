from fastapi.testclient import TestClient

FRONTEND = "https://web.example.com"
PREFLIGHT = {"Access-Control-Request-Method": "POST"}


def test_the_configured_frontend_may_call_the_api(set_setting):
    set_setting("CORS_ORIGINS", [FRONTEND])
    from app.app import get_skim_app

    with TestClient(get_skim_app()) as client:
        response = client.options("/graphql", headers={"Origin": FRONTEND, **PREFLIGHT})

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == FRONTEND


def test_other_websites_may_not_call_the_api(set_setting):
    set_setting("CORS_ORIGINS", [FRONTEND])
    from app.app import get_skim_app

    with TestClient(get_skim_app()) as client:
        response = client.options(
            "/graphql", headers={"Origin": "https://evil.example.com", **PREFLIGHT}
        )

    assert "access-control-allow-origin" not in response.headers


def test_hsts_is_sent_when_enabled(client, set_setting):
    set_setting("ENABLE_HSTS", True)

    response = client.get("/healthCheck")

    assert response.headers["Strict-Transport-Security"] == "max-age=31536000; includeSubDomains"
