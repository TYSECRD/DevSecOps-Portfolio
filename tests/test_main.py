import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from app.database import clear_events, create_event
import os
os.environ["STEELDOOR_API_KEY"] = "steeldoor-dev-key"
from app.main import app
from app.rate_limit import clear_rate_limits, REQUEST_LIMIT, WINDOW_SECONDS


client = TestClient(app)

API_HEADERS = {
    "X-API-Key": "steeldoor-dev-key"
}


@pytest.fixture(autouse=True)
def clear_test_events():
    clear_events()
    clear_rate_limits()

    yield

    clear_events()
    clear_rate_limits()

def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_app_info():
    response = client.get("/api/info")

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "SteelDoor Security API"
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

    response = client.post(
        "/api/events",
        json=event,
        headers=API_HEADERS
    )

    assert response.status_code == 201

    data = response.json()

    assert data["event"]["id"] == 1
    assert data["event"]["source_ip"] == "192.168.1.50"
    assert data["event"]["event_type"] == "failed_login"
    assert data["event"]["severity"] == "high"
    assert data["event"]["description"] == "Multiple failed login attempts detected"
    assert data["event"]["status"] == "new"
    assert "created_at" in data["event"]
    assert data["event"]["created_at"].endswith("+00:00")


def test_get_security_events():
    event = {
        "source_ip": "10.0.0.25",
        "event_type": "malware_detected",
        "severity": "critical",
        "description": "Suspicious executable detected"
    }

    client.post(
        "/api/events",
        json=event,
        headers=API_HEADERS
    )

    response = client.get(
        "/api/events",
        headers=API_HEADERS
    )

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

    response = client.post(
        "/api/events",
        json=event,
        headers=API_HEADERS
    )

    assert response.status_code == 422


def test_reject_invalid_ip_address():
    event = {
        "source_ip": "not-an-ip-address",
        "event_type": "failed_login",
        "severity": "high",
        "description": "Invalid IP address test"
    }

    response = client.post(
        "/api/events",
        json=event,
        headers=API_HEADERS
    )

    assert response.status_code == 422


def test_filter_events_by_severity():
    critical_event = {
        "source_ip": "203.0.113.10",
        "event_type": "ransomware_detected",
        "severity": "critical",
        "description": "Potential ransomware activity detected"
    }

    client.post(
        "/api/events",
        json=critical_event,
        headers=API_HEADERS
    )

    response = client.get(
        "/api/events?severity=critical",
        headers=API_HEADERS
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] >= 1
    assert all(
        event["severity"] == "critical"
        for event in data["events"]
    )
    assert any(
        event["event_type"] == "ransomware_detected"
        for event in data["events"]
    )


def test_detect_brute_force():
    source_ip = "10.10.10.50"

    for _ in range(5):
        response = client.post(
            "/api/events",
            json={
                "source_ip": source_ip,
                "event_type": "failed_login",
                "severity": "high",
                "description": "Failed login attempt"
            },
            headers=API_HEADERS
        )

    assert response.status_code == 201
    assert response.json()["brute_force_detected"] is True
    assert response.json()["alert"] is not None
    assert response.json()["alert"]["rule"] == "BRUTE_FORCE_ATTEMPT"
    assert response.json()["alert"]["source_ip"] == source_ip
    assert response.json()["alert"]["severity"] == "high"
    assert response.json()["alert"]["message"] == "Possible brute-force attack detected"


def test_no_brute_force_below_threshold():
    source_ip = "10.10.10.60"

    for _ in range(4):
        response = client.post(
            "/api/events",
            json={
                "source_ip": source_ip,
                "event_type": "failed_login",
                "severity": "high",
                "description": "Failed login attempt"
            },
            headers=API_HEADERS
        )

    assert response.status_code == 201
    assert response.json()["brute_force_detected"] is False
    assert response.json()["alert"] is None


def test_old_failed_logins_do_not_trigger_brute_force():
    source_ip = "10.10.10.70"

    old_time = (
        datetime.now(timezone.utc) - timedelta(minutes=10)
    ).isoformat()

    for _ in range(5):
        create_event(
            {
                "source_ip": source_ip,
                "event_type": "failed_login",
                "severity": "high",
                "description": "Old failed login attempt"
            },
            created_at=old_time
        )

    response = client.post(
        "/api/events",
        json={
            "source_ip": source_ip,
            "event_type": "login_success",
            "severity": "low",
            "description": "Successful login"
        },
        headers=API_HEADERS
    )

    assert response.status_code == 201
    assert response.json()["brute_force_detected"] is False
    assert response.json()["alert"] is None

def test_reject_missing_api_key():
    response = client.get("/api/events")
    assert response.status_code == 401

def test_reject_invalid_api_key():
    response = client.get(
        "/api/events",
        headers={"X-API-Key": "wrong-key"}
    )

    assert response.status_code == 401

def test_rate_limit_exceeded():
    for _ in range(REQUEST_LIMIT):
        response = client.get(
            "/api/events",
            headers=API_HEADERS
        )

        assert response.status_code == 200

    response = client.get(
        "/api/events",
        headers=API_HEADERS
    )

    assert response.status_code == 429
    assert response.json()["detail"] == "Too many requests"
    assert response.headers["Retry-After"] == str(WINDOW_SECONDS)