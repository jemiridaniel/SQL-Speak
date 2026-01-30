# core/perplexity_sql.py

import os
from typing import Optional

import requests


PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"
PERPLEXITY_MODEL = "sonar-pro"  # or another model you have access to


class PerplexitySQLError(Exception):
    pass


def generate_sql(schema_context: str, nl_query: str, db_type: str = "postgres") -> str:
    """
    Call Perplexity to generate a single SQL statement for the given schema + NL query.
    Returns the SQL string, or raises PerplexitySQLError on failure.
    """

    if not PERPLEXITY_API_KEY:
        raise PerplexitySQLError("PERPLEXITY_API_KEY is not set")

    system_prompt = f"""
You are a senior data engineer acting as a text-to-SQL generator.

You are given the database schema and a natural language question.
Return a single {db_type.upper()} SQL SELECT query that correctly answers the question.

Rules:
- Use ONLY the tables and columns shown in the schema context.
- Do NOT invent tables or columns.
- Use standard {db_type.upper()} SQL syntax.
- Do NOT include explanations, comments, markdown, or language labels.
- Do NOT wrap the SQL in backticks or code fences.
- Output ONLY the SQL statement.
    """.strip()

    user_prompt = (
        f"SCHEMA CONTEXT:\n{schema_context}\n\n"
        f"QUESTION:\n{nl_query}\n\n"
        "Return only the SQL query."
    )

    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": PERPLEXITY_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 512,
    }

    resp = requests.post(PERPLEXITY_API_URL, json=payload, headers=headers, timeout=30)
    if resp.status_code != 200:
        raise PerplexitySQLError(
            f"Perplexity API error {resp.status_code}: {resp.text[:500]}"
        )

    data = resp.json()
    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as e:
        raise PerplexitySQLError(f"Unexpected Perplexity response format: {data}") from e

    sql = content.strip().strip("`").strip()

    # handle ```sql ... ``` or ``` ... ``` blocks
    if sql.lower().startswith("```"):
        sql = sql.strip("`")
        if "\n" in sql:
            sql = "\n".join(sql.split("\n")[1:]).strip()

    # strip a leading language tag like "sql" or "SQL"
    if sql.lower().startswith("sql"):
        # handles "sql\nSELECT ..." or "sql SELECT ..."
        sql = sql[3:].lstrip()

    return sql
