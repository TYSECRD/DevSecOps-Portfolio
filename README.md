![SteelDoor Security Event Defense Platform](./assets/steeldoor-banner.svg)

# SteelDoor Security API

[![CI Pipeline](https://github.com/TYSECRD/DevSecOps-Portfolio/actions/workflows/ci.yml/badge.svg)](https://github.com/TYSECRD/DevSecOps-Portfolio/actions/workflows/ci.yml)

**Security events hit the door. Threats don't get through.**

SteelDoor is a Python security-event monitoring and threat-detection API built to demonstrate secure application development, automated detection logic, database persistence, testing, and DevSecOps pipeline controls.

## Current Features

* Ingest security events through a REST API
* Validate IPv4 and IPv6 source addresses
* Enforce approved severity levels
* Assign unique event IDs
* Record UTC timestamps
* Store security events in SQLite
* Retrieve recorded security events
* Filter events by severity
* Track event status through `new`, `investigating`, and `resolved`
* Detect repeated failed-login activity
* Detect brute-force behavior using a 5-attempt / 5-minute threshold
* Generate structured security alerts when brute-force activity is detected
* Ignore expired failed-login activity outside the detection window
* Reject malformed security data
* Interactive Swagger API documentation

## Detection Engine

SteelDoor includes a dedicated detection module for analyzing security-event activity.

The first implemented detection rule identifies potential brute-force authentication attacks.

### Brute-Force Rule

SteelDoor generates an alert when:

* The same source IP generates at least 5 failed-login events
* Those events occur within a 5-minute window

Activity outside the detection window is excluded from the threshold.

Example detection flow:

```text
Failed login
     |
Failed login
     |
Failed login
     |
Failed login
     |
Failed login
     |
     v
SteelDoor Detection Engine
     |
     v
BRUTE_FORCE_ATTEMPT
Severity: HIGH
```

## Structured Alerts

When the brute-force rule is triggered, SteelDoor generates a structured alert containing:

```json
{
  "rule": "BRUTE_FORCE_ATTEMPT",
  "source_ip": "10.10.10.50",
  "severity": "high",
  "message": "Possible brute-force attack detected"
}
```

This separates raw security-event ingestion from threat-detection results.

## DevSecOps Controls

Every push to GitHub automatically runs:

* Pytest automated testing
* Bandit static application security testing (SAST)
* Pip-audit dependency vulnerability scanning
* GitHub Actions continuous integration pipeline

The automated test suite currently covers event ingestion, validation, filtering, status behavior, brute-force detection, alert generation, threshold behavior, and detection-window expiration.

## Technology Stack

* Python 3.13
* FastAPI
* Pydantic
* SQLite
* Pytest
* GitHub Actions
* Bandit
* Pip-audit

## API Endpoints

| Method  | Endpoint                        | Purpose                                       |
| ------- | ------------------------------- | --------------------------------------------- |
| `GET`   | `/health`                       | Verify service health                         |
| `GET`   | `/api/info`                     | Return application information                |
| `GET`   | `/api/greet`                    | Return a basic API greeting                   |
| `POST`  | `/api/events`                   | Validate, store, and analyze a security event |
| `GET`   | `/api/events`                   | Retrieve security events                      |
| `GET`   | `/api/events?severity=critical` | Filter events by severity                     |
| `PATCH` | `/api/events/{event_id}`        | Update security-event investigation status    |

## Example Security Event

```json
{
  "source_ip": "10.0.0.77",
  "event_type": "failed_login",
  "severity": "high",
  "description": "Authentication failure detected"
}
```

After ingestion, SteelDoor stores the event and evaluates activity from the source IP against its detection rules.

## Run SteelDoor Locally

Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

Start the API:

```bash
python -m uvicorn app.main:app --reload
```

Open the interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

## Run the Tests

```bash
python -m pytest -v
```

Current test suite:

```text
11 passed
```

## Project Structure

```text
DevSecOps-Portfolio/
|-- .github/
|   `-- workflows/
|       `-- ci.yml
|-- app/
|   |-- database.py
|   |-- detection.py
|   `-- main.py
|-- tests/
|   `-- test_main.py
|-- assets/
|   `-- steeldoor-banner.svg
|-- .gitignore
|-- README.md
`-- requirements.txt
```

## Roadmap

* Additional threat-detection rules
* Persistent alert storage and alert-management endpoints
* Authentication and authorization
* API rate limiting
* Structured security logging
* Docker containerization
* Cloud deployment
* Infrastructure as Code
* Application monitoring and observability
* Expanded CI/CD security gates

## Project Status

SteelDoor is under active development as a hands-on DevSecOps portfolio project focused on building, securing, testing, and eventually deploying a production-style security application.
