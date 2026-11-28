def test_health_check(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "message": "Сервер работает"
    }


def test_version_reports_image_revision(client, monkeypatch):
    revision = "a" * 40
    monkeypatch.setenv("APP_REVISION", revision)

    response = client.get("/version")

    assert response.status_code == 200
    assert response.json() == {"version": "0.1.0", "revision": revision}
