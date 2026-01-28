# core/engine.py

from time import perf_counter
from datetime import datetime
from typing import Dict, Any, Optional

from sqlalchemy import text

from .db import get_engine, get_schema_context
from .profiles import get_profile
from .logging import log_query, QueryLogEvent
from .models import UserContext, QueryResult, SchemaInfo
from .copilot import get_sql_from_copilot
from .profiles import get_profile, Profile



def _apply_profile_policies(sql: str, profile: Profile) -> str:
    sql_stripped = sql.strip().rstrip(";")
    upper = sql_stripped.upper()

    # Read-only: only allow SELECT
    if profile.read_only and not upper.startswith("SELECT"):
        raise ValueError("Non-SELECT queries are not allowed in this profile")

    # Auto LIMIT if configured and missing
    if profile.auto_limit is not None and "LIMIT" not in upper:
        sql_stripped = f"{sql_stripped} LIMIT {profile.auto_limit}"

    return sql_stripped + ";"


def _nl_to_sql_via_copilot(nl_query: str, conn_str: str, profile_name: str) -> str:
    schema_context = get_schema_context(conn_str)
    print("SCHEMA CONTEXT:", schema_context)

    sql = get_sql_from_copilot(nl_query, schema_context)
    print("COPILOT RETURNED (cleaned):", repr(sql))

    if not sql:
        print("COPILOT: empty output, falling back to SELECT 1")
        return "SELECT 1 AS value;"

    return sql

def run_one_shot_query(
    user: UserContext,
    data_source: str,
    profile_name: str,
    nl_query: str,
    conn_str: Optional[str] = None,
) -> QueryResult:
    if conn_str is None:
        raise ValueError("conn_str is required until config wiring is done")

    profile = get_profile(profile_name)

    start = perf_counter()
    status = "success"
    rows: list[Dict[str, Any]] = []
    row_count: Optional[int] = None

    try:
        raw_sql = _nl_to_sql_via_copilot(nl_query, conn_str, profile_name)
        sql = _apply_profile_policies(raw_sql, profile)
    except Exception as exc:
        status = "error"
        sql = f"-- ERROR in SQL generation/policies: {exc}"
        duration_ms = (perf_counter() - start) * 1000.0
        log_query(
            QueryLogEvent(
                timestamp=datetime.utcnow(),
                user_id=user.id,
                data_source=data_source,
                profile=profile_name,
                nl_query=nl_query,
                generated_sql=sql,
                status=status,
                row_count=0,
                execution_time_ms=duration_ms,
                meta={},
            )
        )
        return QueryResult(sql=sql, rows=[], meta={
            "profile": profile_name,
            "status": status,
            "execution_time_ms": duration_ms,
            "row_count": 0,
        })

    try:
        engine = get_engine(conn_str)
        with engine.connect() as conn:
            result = conn.execute(text(sql))
            rows = [dict(r._mapping) for r in result]
            row_count = len(rows)
    except Exception as exc:
        status = "error"
        rows = []
        row_count = 0
        sql = f"-- ERROR: {exc}"

    duration_ms = (perf_counter() - start) * 1000.0

    log_query(
        QueryLogEvent(
            timestamp=datetime.utcnow(),
            user_id=user.id,
            data_source=data_source,
            profile=profile_name,
            nl_query=nl_query,
            generated_sql=sql,
            status=status,
            row_count=row_count,
            execution_time_ms=duration_ms,
            meta={},
        )
    )

    meta = {
        "profile": profile_name,
        "status": status,
        "execution_time_ms": duration_ms,
        "row_count": row_count,
    }
    return QueryResult(sql=sql, rows=rows, meta=meta)

def get_schema_snapshot(
    data_source: str,
    conn_str: str,
) -> SchemaInfo:
    engine = get_engine(conn_str)
    tables: list[Dict[str, Any]] = []

    with engine.connect() as conn:
        result = conn.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
            """
        )
        for row in result:
            tables.append({"name": row[0]})

    return SchemaInfo(data_source=data_source, tables=tables)
