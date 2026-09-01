from datetime import datetime, timedelta, timezone

from app.database import read_events


BRUTE_FORCE_THRESHOLD = 5
BRUTE_FORCE_WINDOW_MINUTES = 5


def detect_brute_force(source_ip: str):
    events = read_events()

    cutoff_time = datetime.now(timezone.utc) - timedelta(
        minutes=BRUTE_FORCE_WINDOW_MINUTES
    )

    failed_logins = [
        event for event in events
        if event["event_type"] == "failed_login"
        and event["source_ip"] == source_ip
        and datetime.fromisoformat(event["created_at"]) >= cutoff_time
    ]

    return len(failed_logins) >= BRUTE_FORCE_THRESHOLD