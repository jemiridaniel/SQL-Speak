import typer
import subprocess
import re
from tabulate import tabulate
from typing import Optional
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError

app = typer.Typer(
    help="SQL-Speak: Talk to your database in plain English via GitHub Copilot CLI."
)

# ------------------------
# Helpers
# ------------------------

def get_db_url(db_input: str) -> str:
    """Converts a database path or connection string into a valid SQLAlchemy URL."""
    if "://" in db_input:
        return db_input
    return f"sqlite:///{db_input}"


def is_postgres(db_url: str) -> bool:
    return db_url.startswith("postgresql://")


def is_benchmark_postgres(profile: str, db_url: str) -> bool:
    return profile == "benchmark-postgres" and is_postgres(db_url)


def get_db_schema(db_url: str) -> str:
    """Discovers the database schema using SQLAlchemy inspector."""
    try:
        engine = create_engine(db_url)
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        if not tables:
            return "The database is currently empty."

        schema_text = f"""Database Type: {engine.dialect.name}
Database Schema:
"""

        for table_name in tables:
            columns = inspector.get_columns(table_name)
            col_desc = ", ".join(
                [f"{c['name']} ({c['type']})" for c in columns]
            )
            schema_text += f"- Table '{table_name}': columns=[{col_desc}]\n"

        return schema_text

    except Exception as e:
        typer.secho(f"Schema Discovery Error: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)


# ------------------------
# SQL Execution
# ------------------------

def run_sql(db_url: str, sql: str, profile: str = "default"):
    try:
        engine = create_engine(db_url)

        # Benchmark safety rules
        if is_benchmark_postgres(profile, db_url):
            if not sql.strip().lower().startswith("select"):
                typer.secho(
                    "⛔ Benchmark profile is READ-ONLY (SELECT only).",
                    fg=typer.colors.RED,
                    bold=True,
                )
                return

            if "limit" not in sql.lower():
                sql = sql.rstrip(";") + " LIMIT 100;"
                typer.secho(
                    "⚠ LIMIT 100 auto-applied (benchmark safety)",
                    fg=typer.colors.YELLOW,
                )

            typer.secho(
                "\n📊 EXPLAIN ANALYZE (preview):",
                fg=typer.colors.CYAN,
                bold=True,
            )
            with engine.connect() as conn:
                plan = conn.execute(
                    text(f"EXPLAIN (ANALYZE, BUFFERS) {sql}")
                ).fetchall()
                for row in plan:
                    typer.echo(row[0])

            if not typer.confirm("\n▶ Run actual query?"):
                typer.secho("Query cancelled.", fg=typer.colors.YELLOW)
                return

        with engine.connect() as connection:
            result = connection.execute(text(sql))

            if result.returns_rows:
                rows = result.fetchall()
                if rows:
                    data = [dict(row._mapping) for row in rows]
                    typer.secho(
                        "\n✓ Query Results:\n",
                        fg=typer.colors.GREEN,
                        bold=True,
                    )
                    typer.echo(tabulate(data, headers="keys", tablefmt="grid"))
                else:
                    typer.secho(
                        "\n✓ Query executed successfully (0 rows returned).",
                        fg=typer.colors.GREEN,
                    )
            else:
                connection.commit()
                typer.secho(
                    f"\n✓ Command executed successfully. Rows affected: {result.rowcount}",
                    fg=typer.colors.GREEN,
                )

    except SQLAlchemyError as e:
        typer.secho(f"Database Error: {e}", fg=typer.colors.RED)
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED)


# ------------------------
# Multi-turn Mode
# ------------------------

def multi_turn_conversation(db_url: str, profile: str):
    schema = get_db_schema(db_url)

    typer.secho(
        "\n🔄 Entering Multi-Turn Conversation Mode",
        fg=typer.colors.CYAN,
        bold=True,
    )
    typer.secho("Type 'exit' or 'quit' to end the session.\n", fg=typer.colors.CYAN)

    current_sql = None

    while True:
        user_input = typer.prompt("You").strip()

        if user_input.lower() in {"exit", "quit"}:
            typer.secho("\n👋 Goodbye!", fg=typer.colors.CYAN)
            break

        if not current_sql:
            if is_benchmark_postgres(profile, db_url):
                prompt = f"""You are a PostgreSQL performance expert.
This is a LARGE benchmark database (10M+ rows).

Rules:
- Prefer aggregates over SELECT *
- Always include LIMIT
- Use PostgreSQL idioms

{schema}

Request:
{user_input}

Return ONLY SQL in ```sql``` blocks.
"""
            else:
                prompt = f"""You are a SQL expert.
{schema}

Request:
{user_input}

Return ONLY SQL in ```sql``` blocks.
"""

            result = subprocess.run(
                f'gh copilot -p "{prompt}"',
                shell=True,
                capture_output=True,
                text=True,
            )

            sql_match = re.search(r"```sql\s*([\s\S]*?)\s*```", result.stdout)

            if sql_match:
                current_sql = sql_match.group(1).strip()
                typer.secho(f"\n✓ Generated SQL:\n{current_sql}", fg=typer.colors.GREEN)
                run_sql(db_url, current_sql, profile)
            else:
                typer.secho("⚠ No SQL found.", fg=typer.colors.YELLOW)
        else:
            typer.secho("Refinement not implemented in benchmark demo.", fg=typer.colors.YELLOW)


# ------------------------
# CLI Command
# ------------------------

@app.command()
def query(
    query_text: Optional[str] = typer.Argument(None),
    db: str = typer.Option(..., help="Path to SQLite DB or Postgres URL"),
    multi_turn: bool = typer.Option(False, "--multi-turn"),
    execute: bool = typer.Option(True),
    profile: str = typer.Option(
        "default",
        help="Execution profile: default | benchmark-postgres",
    ),
):
    db_url = get_db_url(db)

    if multi_turn:
        multi_turn_conversation(db_url, profile)
        return

    if not query_text:
        query_text = typer.prompt("Enter your database query in plain English")

    schema = get_db_schema(db_url)

    if is_benchmark_postgres(profile, db_url):
        prompt = f"""You are a PostgreSQL performance expert.
This is a LARGE benchmark database (10M+ rows).

Rules:
- Prefer aggregates
- Always include LIMIT
- Avoid SELECT *

{schema}

Request:
{query_text}

Return ONLY SQL in ```sql``` blocks.
"""
    else:
        prompt = f"""You are a SQL expert.
{schema}

Request:
{query_text}

Return ONLY SQL in ```sql``` blocks.
"""

    result = subprocess.run(
        f'gh copilot -p "{prompt}"',
        shell=True,
        capture_output=True,
        text=True,
    )

    sql_match = re.search(r"```sql\s*([\s\S]*?)\s*```", result.stdout)

    if sql_match:
        sql = sql_match.group(1).strip()
        typer.secho(f"\n✓ Extracted SQL:\n{sql}", fg=typer.colors.GREEN)

        if execute and typer.confirm("▶ Run this query?"):
            run_sql(db_url, sql, profile)
    else:
        typer.secho("⛔ No SQL block found.", fg=typer.colors.RED)


if __name__ == "__main__":
    app()
# new feature
