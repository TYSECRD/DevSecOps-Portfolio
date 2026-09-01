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

def test_get_security_events():
    event = {
        "source_ip": "10.0.0.25",
        "event_type": "malware_detected",
        "severity": "critical",
        "description": "Suspicious executable detected"
    }

    client.post("/api/events", json=event)
    response = client.get("/api/events")

    assert response.status_code == 200

    data = response.json()

    assert data["total"] >= 1
    assert isinstance(data["events"], list)
    assert data["events"][-1]["event_type"] == "malware_detected"
    assert data["events"][-1]["severity"] == "critical"

def test_reject_invalid_severity():
    event = {
        "source_ip": "172.16.0.10",
        "event_type": "port_scan",
        "severity": "extremely_bad",
        "description": "Invalid severity test"
    }

    response = client.post("/api/events", json=event)

    assert response.status_code == 422

def test_reject_invalid_ip_address():
    event = {
        "source_ip": "not-an-ip-address",
        "event_type": "failed_login",
        "severity": "high",
        "description": "Invalid IP address test"
    }

    response = client.post("/api/events", json=event)

    assert response.status_code == 422