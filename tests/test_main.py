from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_app_info():
    response = client.get("/api/info")

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "DevSecOps Portfolio API"
    assert data["version"] == "1.0.0"
    assert data["environment"] == "development"


def test_greet():
    response = client.get("/api/greet?name=Ty")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello, Ty!"}