from fastapi import FastAPI
from pydantic import BaseModel, IPvAnyAddress
from typing import Literal
from app.database import create_event, initialize_database, read_events

Severity = Literal["low", "medium", "high", "critical"]


class SecurityEvent(BaseModel):
    source_ip: IPvAnyAddress
    event_type: str
    severity: Severity
    description: str


app = FastAPI(title="DevSecOps Portfolio API")
initialize_database()



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
    return create_event(event.model_dump())

@app.get("/api/events")
def get_security_events(severity: Severity | None = None):
    events = read_events(severity)

    return {
        "total": len(events),
        "events": events
    }