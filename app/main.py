from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, IPvAnyAddress

from app.database import (
    create_event,
    initialize_database,
    read_events,
    update_event_status,
)

Severity = Literal["low", "medium", "high", "critical"]
EventStatus = Literal["new", "investigating", "resolved"]

BRUTE_FORCE_THRESHOLD = 5

class SecurityEvent(BaseModel):
    source_ip: IPvAnyAddress
    event_type: str
    severity: Severity
    description: str


class EventStatusUpdate(BaseModel):
    status: EventStatus


app = FastAPI(title="SteelDoor Security API")
initialize_database()

def detect_brute_force(source_ip: str):
    events = read_events()

    failed_logins = [
        event for event in events
        if event["event_type"] == "failed_login"
        and event["source_ip"] == source_ip
    ]

    return len(failed_logins) >= BRUTE_FORCE_THRESHOLD

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
def create_security_event(event: SecurityEvent):
    created_event = create_event(event.model_dump())

    brute_force_detected = detect_brute_force(str(event.source_ip))

    return {
        "event": created_event,
        "brute_force_detected": brute_force_detected
    }

@app.get("/api/events")
def get_security_events(severity: Severity | None = None):
    events = read_events(severity)

    return {
        "total": len(events),
        "events": events
    }

@app.patch("/api/events/{event_id}")
def change_event_status(event_id: int, update: EventStatusUpdate):
    event = update_event_status(event_id, update.status)

    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Security event not found"
        )

    return event