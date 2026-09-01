from app.database import read_events

BRUTE_FORCE_THRESHOLD = 5


def detect_brute_force(source_ip: str):
    events = read_events()

    failed_logins = [
        event for event in events
        if event["event_type"] == "failed_login"
        and event["source_ip"] == source_ip
    ]

    return len(failed_logins) >= BRUTE_FORCE_THRESHOLD