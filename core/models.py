
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

@dataclass
class UserContext:
    id: str
    display_name: str
    roles: List[str]

@dataclass
class QueryResult:
    sql: str
    rows: List[Dict[str, Any]]
    meta: Dict[str, Any]

@dataclass
class SchemaInfo:
    data_source: str
    tables: List[Dict[str, Any]]
