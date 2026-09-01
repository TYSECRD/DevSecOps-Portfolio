import sqlite3
from datetime import datetime, timezone
from pathlib import Path


DATABASE_PATH = Path(__file__).resolve().parent.parent / "steeldoor.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS security_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_ip TEXT NOT NULL,
                event_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                description TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )


def create_event(event):
    created_at = datetime.now(timezone.utc).isoformat()
    source_ip = str(event["source_ip"])

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO security_events (
                source_ip,
                event_type,
                severity,
                description,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                source_ip,
                event["event_type"],
                event["severity"],
                event["description"],
                created_at,
            ),
        )

    return {
        "id": cursor.lastrowid,
        "source_ip": source_ip,
        "event_type": event["event_type"],
        "severity": event["severity"],
        "description": event["description"],
        "created_at": created_at,
    }


def read_events(severity=None):
    query = "SELECT * FROM security_events"
    parameters = ()

    if severity is not None:
        query += " WHERE severity = ?"
        parameters = (severity,)

    query += " ORDER BY id"

    with get_connection() as connection:
        rows = connection.execute(query, parameters).fetchall()

    return [dict(row) for row in rows]


def clear_events():
    with get_connection() as connection:
        connection.execute("DELETE FROM security_events")
        connection.execute(
            "DELETE FROM sqlite_sequence WHERE name = 'security_events'"
        )