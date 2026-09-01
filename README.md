<p align="center">
  <img src="assets/steeldoor-banner.svg" alt="SteelDoor Security Event Defense Platform" width="100%">
</p>

# SteelDoor Security API

[![CI Pipeline](https://github.com/TYSECRD/DevSecOps-Portfolio/actions/workflows/ci.yml/badge.svg)](https://github.com/TYSECRD/DevSecOps-Portfolio/actions/workflows/ci.yml)

**Security events hit the door. Threats don't get through.**

SteelDoor is a Python security-event monitoring API built to demonstrate secure application development, automated testing, database persistence, and DevSecOps pipeline controls.

## Current Features

- Ingest security events through a REST API
- Validate IPv4 and IPv6 source addresses
- Enforce approved severity levels
- Assign unique event IDs
- Record UTC timestamps
- Store events permanently in SQLite
- Retrieve all recorded events
- Filter events by severity
- Reject malformed security data
- Interactive Swagger API documentation

## DevSecOps Controls

Every push to GitHub automatically runs:

- Pytest automated tests
- Bandit static application security testing
- Pip-audit dependency vulnerability scanning
- GitHub Actions CI pipeline

## Technology Stack

- Python 3.13
- FastAPI
- Pydantic
- SQLite
- Pytest
- GitHub Actions
- Bandit
- Pip-audit

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Verify service health |
| `GET` | `/api/info` | Return application information |
| `POST` | `/api/events` | Validate and store a security event |
| `GET` | `/api/events` | Retrieve security events |
| `GET` | `/api/events?severity=critical` | Filter events by severity |

## Example Security Event

```json
{
  "source_ip": "10.0.0.77",
  "event_type": "brute_force_attack",
  "severity": "critical",
  "description": "Repeated authentication failures detected"
}
```

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

## Project Structure

```text
DevSecOps-Portfolio/
├── .github/
│   └── workflows/
│       └── ci.yml
├── app/
│   ├── database.py
│   └── main.py
├── tests/
│   └── test_main.py
├── .gitignore
├── README.md
└── requirements.txt
```

## Roadmap

- Event status and incident lifecycle tracking
- Authentication and authorization
- Rate limiting
- Structured security logging
- Docker containerization
- Cloud deployment
- Infrastructure as Code
- Monitoring and alerting
- Expanded CI/CD security gates

## Project Status

SteelDoor is under active development as part of a hands-on DevSecOps portfolio.