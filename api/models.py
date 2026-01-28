# api/models.py

from typing import Any, Dict, List
from pydantic import BaseModel

class QueryRequest(BaseModel):
    data_source: str
    profile: str
    query: str

class QueryResponse(BaseModel):
    sql: str
    results: List[Dict[str, Any]]
    meta: Dict[str, Any]

class SchemaRequest(BaseModel):
    data_source: str

class SchemaResponse(BaseModel):
    data_source: str
    tables: List[Dict[str, Any]]
