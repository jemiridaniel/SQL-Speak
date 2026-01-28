# core/logging.py

from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict, deque
from typing import Any, Dict, Optional, Dict as TDict, Deque, List

@dataclass
class QueryLogEvent:
    timestamp: datetime
    user_id: str
    data_source: str
    profile: str
    nl_query: str
    generated_sql: str
    status: str
    row_count: Optional[int]
    execution_time_ms: Optional[float]
    meta: Dict[str, Any]


_HISTORY_LIMIT = 50
_user_history: TDict[str, Deque[QueryLogEvent]] = defaultdict(
    lambda: deque(maxlen=_HISTORY_LIMIT)
)

def log_query(event: QueryLogEvent) -> None:
    from .history_db import insert_history_event  # lazy import to avoid cycles

    print(
        f"[QUERY] {event.timestamp.isoformat()} | user={event.user_id} "
        f"ds={event.data_source} profile={event.profile} "
        f"status={event.status} rows={event.row_count} "
        f"time_ms={event.execution_time_ms}"
    )
    _user_history[event.user_id].appendleft(event)
    insert_history_event(event)


def get_user_history(user_id: str) -> List[QueryLogEvent]:
    # Prefer DB-backed history so it survives restarts
    from .history_db import load_user_history

    return list(load_user_history(user_id, limit=_HISTORY_LIMIT))
