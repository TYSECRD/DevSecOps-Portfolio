from collections import defaultdict
from time import time


REQUEST_LIMIT = 20
WINDOW_SECONDS = 60

request_history = defaultdict(list)


def check_rate_limit(client_id: str) -> bool:
    current_time = time()
    window_start = current_time - WINDOW_SECONDS

    recent_requests = [
        timestamp
        for timestamp in request_history[client_id]
        if timestamp > window_start
    ]

    request_history[client_id] = recent_requests

    if len(recent_requests) >= REQUEST_LIMIT:
        return False

    request_history[client_id].append(current_time)

    return True


def clear_rate_limits():
    request_history.clear()