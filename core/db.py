# core/db.py

from typing import Dict
from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import Engine

_engine_cache: Dict[str, Engine] = {}


def get_engine(conn_str: str) -> Engine:
    if conn_str not in _engine_cache:
        _engine_cache[conn_str] = create_engine(conn_str, future=True)
    return _engine_cache[conn_str]


def get_schema_context(conn_str: str) -> str:
    """
    Very simple schema description string for Copilot.
    Later, you can make this richer (columns, types, sample rows).
    """
    engine = get_engine(conn_str)
    insp = inspect(engine)

    schema_parts = []
    for table_name in insp.get_table_names():
        cols = [col["name"] for col in insp.get_columns(table_name)]
        schema_parts.append(f"Table '{table_name}' ({', '.join(cols)})")

    return "; ".join(schema_parts)
