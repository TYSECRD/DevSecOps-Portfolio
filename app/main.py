from fastapi import FastAPI
from pydantic import BaseModel


class SecurityEvent(BaseModel):
    source_ip: str
    event_type: str
    severity: str
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
    security_events.append(event_record)

    return event_record