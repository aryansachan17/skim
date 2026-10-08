def test_health_check_is_ok_when_dependencies_are_up(client):
    response = client.get("/healthCheck")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "version": "dev",
        "checks": {"mongo": "ok", "redis": "ok"},
    }


def test_health_check_reports_a_down_dependency_without_leaking_details(app, client):
    class BrokenRedis:
        async def ping(self):
            raise ConnectionError("redis://admin:hunter2@10.0.0.5:6379 refused")

    app.state.redis = BrokenRedis()

    response = client.get("/healthCheck")

    assert response.status_code == 503
    assert response.json()["status"] == "degraded"
    assert response.json()["checks"] == {"mongo": "ok", "redis": "down"}
    assert "hunter2" not in response.text


def test_liveness_answers_without_touching_dependencies(app, client):
    class Unreachable:
        async def ping(self):
            raise AssertionError("liveness must not call dependencies")

        @property
        def admin(self):
            raise AssertionError("liveness must not call dependencies")

    app.state.mongo = Unreachable()
    app.state.redis = Unreachable()

    response = client.get("/livez")

    assert response.status_code == 200
    assert response.json() == {"status": "alive", "version": "dev"}
