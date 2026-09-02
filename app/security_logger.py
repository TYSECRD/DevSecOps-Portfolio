import logging
from datetime import datetime, timezone

logger = logging.getLogger("steeldoor.security")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s"
)

handler.setFormatter(formatter)
logger.addHandler(handler)

def log_security_event(
    event_type: str,
    message: str,
    client_ip: str | None = None
):
    timestamp = datetime.now(timezone.utc).isoformat()

    logger.warning(
        f"timestamp={timestamp} "
        f"event={event_type} "
        f"client_ip={client_ip or 'unknown'} "
        f"message={message}"
    )