import secrets
import os
from typing import Literal
from fastapi import FastAPI, HTTPException, Security, Request
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, IPvAnyAddress
from app.detection import detect_brute_force
from app.rate_limit import check_rate_limit, WINDOW_SECONDS
from app.security_logger import log_security_event

from app.database import (
    create_event,
    initialize_database,
    read_events,
    update_event_status,
)

Severity = Literal["low", "medium", "high", "critical"]
EventStatus = Literal["new", "investigating", "resolved"]

class SecurityEvent(BaseModel):
    source_ip: IPvAnyAddress
    event_type: str
    severity: Severity
    description: str


class EventStatusUpdate(BaseModel):
    status: EventStatus

class SecurityAlert(BaseModel):
    rule: str
    source_ip: IPvAnyAddress
    severity: Severity
    message: str


app = FastAPI(title="SteelDoor Security API")
initialize_database()

API_KEY = os.getenv("STEELDOOR_API_KEY")

api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False
)

def verify_api_key(
    request: Request,
    api_key: str = Security(api_key_header)
):
    client_ip = request.client.host if request.client else "unknown"

    if not API_KEY or not api_key or not secrets.compare_digest(api_key, API_KEY):
        log_security_event(
            event_type="invalid_api_key",
            message="Invalid or missing API key",
            client_ip=client_ip
        )

        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key"
        )

    if not check_rate_limit(client_ip):
        log_security_event(
            event_type="rate_limit_exceeded",
            message="Client exceeded request limit",
            client_ip=client_ip
        )
        raise HTTPException(
            status_code=429,
            detail="Too many requests",
            headers={"Retry-After": str(WINDOW_SECONDS)}
        )

    return api_key

def create_brute_force_alert(source_ip: str):
    return SecurityAlert(
        rule="BRUTE_FORCE_ATTEMPT",
        source_ip=source_ip,
        severity="high",
        message="Possible brute-force attack detected"
    )

@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/api/info")
def app_info():
    return {
        "name": "SteelDoor Security API",
        "version": "1.0.0",
        "environment": "development"
    }


@app.get("/api/greet")
def greet(name: str):
    return {"message": f"Hello, {name}!"}

@app.post("/api/events", status_code=201)
def create_security_event(
    event: SecurityEvent,
    api_key: str = Security(verify_api_key)
):
    created_event = create_event(event.model_dump())

    brute_force_detected = detect_brute_force(str(event.source_ip))

    alert = None

    if brute_force_detected:
        alert = create_brute_force_alert(str(event.source_ip))

    log_security_event(
        event_type="brute_force_detected",
        message="Possible brute-force attack detected",
        client_ip=str(event.source_ip)
    )

    return {
        "event": created_event,
        "brute_force_detected": brute_force_detected,
        "alert": alert
    }

@app.get("/api/events")
def get_security_events(
    severity: Severity | None = None,
    api_key: str = Security(verify_api_key)
):
    events = read_events(severity)

    return {
        "total": len(events),
        "events": events
    }

@app.patch("/api/events/{event_id}")
def change_event_status(
    event_id: int,
    update: EventStatusUpdate,
    api_key: str = Security(verify_api_key)
):
    event = update_event_status(event_id, update.status)

    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Security event not found"
        )

    return event