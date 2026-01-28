# api/app.py
from typing import List

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .models import QueryRequest, QueryResponse, SchemaRequest, SchemaResponse
from .dependencies import get_config, get_user_context
from .auth import get_current_user
from core.engine import run_one_shot_query, get_schema_snapshot
from core.models import UserContext
from core.logging import get_user_history
from core.history_db import init_history_db

app = FastAPI(title="SQL-Speak Enterprise API", version="0.1.0")

init_history_db()

# CORS for Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple AAD-protected “who am I” endpoint
@app.get("/me")
def read_me(user: UserContext = Depends(get_current_user)):
    return {
        "id": user.id,
        "display_name": user.display_name,
        "roles": user.roles,
    }

@app.post("/query", response_model=QueryResponse)
def query(
    req: QueryRequest,
    config = Depends(get_config),
    user: UserContext = Depends(get_user_context),
):
    conn_str = config.data_sources.get(req.data_source)
    if not conn_str:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown data_source '{req.data_source}'",
        )

    result = run_one_shot_query(
        user=user,
        data_source=req.data_source,
        profile_name=req.profile,
        nl_query=req.query,
        conn_str=conn_str,
    )

    return QueryResponse(
        sql=result.sql,
        results=result.rows,
        meta=result.meta,
    )

@app.post("/schema", response_model=SchemaResponse)
def schema(
    req: SchemaRequest,
    config = Depends(get_config),
    user: UserContext = Depends(get_user_context),
):
    conn_str = config.data_sources.get(req.data_source)
    if not conn_str:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown data_source '{req.data_source}'",
        )

    schema_info = get_schema_snapshot(
        data_source=req.data_source,
        conn_str=conn_str,
    )
    return SchemaResponse(
        data_source=schema_info.data_source,
        tables=schema_info.tables,
    )

class HistoryItem(BaseModel):
    timestamp: str
    data_source: str
    profile: str
    nl_query: str
    sql: str
    status: str
    row_count: int

@app.get("/history", response_model=List[HistoryItem])
def history(
    config = Depends(get_config),
    user: UserContext = Depends(get_user_context),
):
    events = get_user_history(user.id)
    return [
        HistoryItem(
            timestamp=e.timestamp.isoformat(),
            data_source=e.data_source,
            profile=e.profile,
            nl_query=e.nl_query,
            sql=e.generated_sql,
            status=e.status,
            row_count=e.row_count or 0,
        )
        for e in events
    ]
