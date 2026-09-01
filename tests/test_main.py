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

def test_create_security_event():
    event = {
        "source_ip": "192.168.1.50",
        "event_type": "failed_login",
        "severity": "high",
        "description": "Multiple failed login attempts detected"
    }

    response = client.post("/api/events", json=event)

    assert response.status_code == 201

    data = response.json()

    assert data["id"] == 1
    assert data["source_ip"] == "192.168.1.50"
    assert data["event_type"] == "failed_login"
    assert data["severity"] == "high"
    assert data["description"] == "Multiple failed login attempts detected"