# core/history_db.py

import sqlite3
from pathlib import Path
from typing import Iterable

from .logging import QueryLogEvent

LOG_DB_PATH = Path("sqlspeak_logs.db")


def init_history_db() -> None:
    conn = sqlite3.connect(LOG_DB_PATH)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS query_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                user_id TEXT NOT NULL,
                data_source TEXT NOT NULL,
                profile TEXT NOT NULL,
                nl_query TEXT NOT NULL,
                generated_sql TEXT NOT NULL,
                status TEXT NOT NULL,
                row_count INTEGER,
                execution_time_ms REAL
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def insert_history_event(event: QueryLogEvent) -> None:
    conn = sqlite3.connect(LOG_DB_PATH)
    try:
        conn.execute(
            """
            INSERT INTO query_history (
                timestamp, user_id, data_source, profile,
                nl_query, generated_sql, status, row_count,
                execution_time_ms
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event.timestamp.isoformat(),
                event.user_id,
                event.data_source,
                event.profile,
                event.nl_query,
                event.generated_sql,
                event.status,
                event.row_count,
                event.execution_time_ms,
            ),
        )
        conn.commit()
    finally:
        conn.close()


def load_user_history(user_id: str, limit: int = 50) -> Iterable[QueryLogEvent]:
    conn = sqlite3.connect(LOG_DB_PATH)
    try:
        cur = conn.execute(
            """
            SELECT
                timestamp, user_id, data_source, profile,
                nl_query, generated_sql, status, row_count,
                execution_time_ms
            FROM query_history
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (user_id, limit),
        )
        rows = cur.fetchall()
    finally:
        conn.close()

    events = []
    from datetime import datetime

    for (
        ts,
        user_id,
        data_source,
        profile,
        nl_query,
        generated_sql,
        status,
        row_count,
        execution_time_ms,
    ) in rows:
        events.append(
            QueryLogEvent(
                timestamp=datetime.fromisoformat(ts),
                user_id=user_id,
                data_source=data_source,
                profile=profile,
                nl_query=nl_query,
                generated_sql=generated_sql,
                status=status,
                row_count=row_count,
                execution_time_ms=execution_time_ms,
                meta={},
            )
        )
    return events
