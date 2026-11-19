def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json()["service"] == "SecureAI"


def test_login_success_and_failure(client):
    good = client.post("/api/auth/login", json={"email": "demo@secureai.local", "password": "Demo@12345"})
    assert good.status_code == 200
    assert good.get_json()["token"]

    bad = client.post("/api/auth/login", json={"email": "demo@secureai.local", "password": "wrong-password"})
    assert bad.status_code == 401


def test_register_and_duplicate(client):
    payload = {"username": "tester", "email": "tester@example.com", "password": "StrongPass123"}
    first = client.post("/api/auth/register", json=payload)
    assert first.status_code == 201
    duplicate = client.post("/api/auth/register", json=payload)
    assert duplicate.status_code == 409


def test_protected_route_requires_token(client):
    assert client.get("/api/auth/me").status_code == 401
    assert client.get("/api/history/stats").status_code == 401


def test_scan_requires_authorization(client, auth_headers):
    response = client.post(
        "/api/scans",
        headers=auth_headers,
        json={"target_url": "http://127.0.0.1:8000", "authorization_confirmed": False},
    )
    assert response.status_code == 403


def test_scan_blocks_metadata_endpoint(client, auth_headers):
    response = client.post(
        "/api/scans",
        headers=auth_headers,
        json={"target_url": "http://169.254.169.254/latest/meta-data", "authorization_confirmed": True},
    )
    assert response.status_code == 400


def test_scan_create_and_delete(client, auth_headers, monkeypatch):
    monkeypatch.setattr(
        "routes.scans.validate_target",
        lambda url: {
            "url": "http://127.0.0.1:8000/",
            "host": "127.0.0.1",
            "port": 8000,
            "scheme": "http",
            "resolved_ips": ["127.0.0.1"],
            "netloc": "127.0.0.1:8000",
        },
    )
    monkeypatch.setattr("routes.scans.start_scan_worker", lambda scan_id: None)

    created = client.post(
        "/api/scans",
        headers=auth_headers,
        json={"target_url": "http://127.0.0.1:8000", "authorization_confirmed": True},
    )
    assert created.status_code == 202
    scan_id = created.get_json()["scan"]["id"]

    detail = client.get(f"/api/scans/{scan_id}", headers=auth_headers)
    assert detail.status_code == 200
    assert detail.get_json()["scan"]["status"] == "queued"

    deleted = client.delete(f"/api/scans/{scan_id}", headers=auth_headers)
    assert deleted.status_code == 200


def test_settings_and_model_info(client, auth_headers):
    settings = client.get("/api/settings", headers=auth_headers)
    assert settings.status_code == 200
    assert settings.get_json()["settings"]["theme"] == "dark"

    updated = client.put(
        "/api/settings",
        headers=auth_headers,
        json={"notifications": False},
    )
    assert updated.status_code == 200
    assert updated.get_json()["settings"]["notifications"] is False

    model = client.get("/api/ai/model", headers=auth_headers)
    assert model.status_code == 200
    assert "scoring_model" in model.get_json()
