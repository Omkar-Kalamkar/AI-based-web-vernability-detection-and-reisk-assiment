import os
import tempfile

TEST_DB = os.path.join(tempfile.gettempdir(), "secureai_pytest.db")
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"
os.environ["LOCAL_LAB_MODE"] = "true"

import pytest  # noqa: E402

from app import create_app  # noqa: E402


@pytest.fixture(scope="session")
def app():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    application = create_app()
    application.config["TESTING"] = True
    return application


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_headers(client):
    response = client.post("/api/auth/login", json={"email": "demo@secureai.local", "password": "Demo@12345"})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.get_json()['token']}"}
