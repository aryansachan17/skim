def test_health_check_is_ok_when_dependencies_are_up(client):
    response = client.get("/healthCheck")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "checks": {"mongo": "ok", "redis": "ok"}}


def test_health_check_reports_a_down_dependency_without_leaking_details(app, client):
    class BrokenRedis:
        async def ping(self):
            raise ConnectionError("redis://admin:hunter2@10.0.0.5:6379 refused")

    app.state.redis = BrokenRedis()

    response = client.get("/healthCheck")

    assert response.status_code == 503
    assert response.json() == {"status": "degraded", "checks": {"mongo": "ok", "redis": "down"}}
    assert "hunter2" not in response.text
