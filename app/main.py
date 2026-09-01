from fastapi import FastAPI
from pydantic import BaseModel, IPvAnyAddress
from typing import Literal
from datetime import datetime, timezone

Severity = Literal["low", "medium", "high", "critical"]


class SecurityEvent(BaseModel):
    source_ip: IPvAnyAddress
    event_type: str
    severity: Severity
    description: str


app = FastAPI(title="DevSecOps Portfolio API")
security_events = []


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/api/info")
def app_info():
    return {
        "name": "DevSecOps Portfolio API",
        "version": "1.0.0",
        "environment": "development"
    }


@app.get("/api/greet")
def greet(name: str):
    return {"message": f"Hello, {name}!"}

@app.post("/api/events", status_code=201)
def create_security_event(event: SecurityEvent):
    event_record = event.model_dump()
    event_record["id"] = len(security_events) + 1
    event_record["created_at"] = datetime.now(timezone.utc).isoformat()
    security_events.append(event_record)

    return event_record

@app.get("/api/events")
def get_security_events(severity: Severity | None = None):
    filtered_events = security_events

    if severity is not None:
        filtered_events = [
            event for event in security_events
            if event["severity"] == severity
        ]

    return {
        "total": len(filtered_events),
        "events": filtered_events
    }