import typer
import subprocess
import re
import os
from tabulate import tabulate
from typing import Optional, List
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError

app = typer.Typer(help="SQL-Speak: Talk to your database in plain English via GitHub Copilot CLI.")

def get_db_url(db_input: str) -> str:
    if "://" in db_input:
        return db_input
    return f"sqlite:///{db_input}"

def get_db_schema(db_url: str) -> str:
    try:
        engine = create_engine(db_url)
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        if not tables:
            return "The database is currently empty."
        schema_text = f"Database Type: {engine.dialect.name}
Database Schema:
"
        for table_name in tables:
            columns = inspector.get_columns(table_name)
            col_desc = ", ".join([f"{c['name']} ({c['type']})" for c in columns])
            schema_text += f"- Table '{table_name}': columns=[{col_desc}]
"
        return schema_text
    except Exception as e:
        typer.secho(f"Schema Error: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)

def run_sql(db_url: str, sql: str):
    try:
        engine = create_engine(db_url)
        with engine.connect() as connection:
            result = connection.execute(text(sql))
            if result.returns_rows:
                rows = result.fetchall()
                if rows:
                    data = [dict(row._mapping) for row in rows]
                    typer.secho("
✓ Results:
", fg=typer.colors.GREEN, bold=True)
                    typer.echo(tabulate(data, headers="keys", tablefmt="grid"))
                else:
                    typer.secho("
✓ Success (0 rows).", fg=typer.colors.GREEN)
            else:
                connection.commit()
                typer.secho(f"
✓ Success. Affected: {result.rowcount}", fg=typer.colors.GREEN)
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED)

def refine_query_with_ai(db_url: str, schema: str, previous_sql: str, refinement_request: str) -> Optional[str]:
    context = f"Schema: {schema}
Prev SQL: {previous_sql}
Request: {refinement_request}"
    agent_prompt = f"Refine SQL. {context}. Return ONLY SQL in ```sql block."
    agent_cmd = f'gh copilot -p "{agent_prompt}"'
    try:
        result = subprocess.run(agent_cmd, shell=True, capture_output=True, text=True)
        sql_match = re.search(r"```sql
([\s\S]*?)
```", result.stdout, re.DOTALL)
        if sql_match:
            generated_sql = sql_match.group(1).strip()
            typer.secho(f"
✓ Refined: {generated_sql}", fg=typer.colors.GREEN, bold=True)
            return generated_sql
        return None
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED)
        return None

def multi_turn_conversation(db_url: str):
    schema = get_db_schema(db_url)
    typer.secho("
🔄 Interactive Mode (exit/quit to end)
", fg=typer.colors.CYAN, bold=True)
    current_sql = None
    while True:
        user_input = typer.prompt("You").strip()
        if user_input.lower() in ["exit", "quit"]:
            break
        if not current_sql:
            prompt = f"{schema}

Request: {user_input}

Return ONLY SQL in ```sql block."
            agent_cmd = f'gh copilot -p "{prompt}"'
            try:
                result = subprocess.run(agent_cmd, shell=True, capture_output=True, text=True)
                sql_match = re.search(r"```sql
([\s\S]*?)
```", result.stdout, re.DOTALL)
                if sql_match:
                    current_sql = sql_match.group(1).strip()
                    typer.secho(f"
✓ SQL: {current_sql}", fg=typer.colors.GREEN)
                    run_sql(db_url, current_sql)
            except Exception as e:
                typer.secho(f"Error: {e}", fg=typer.colors.RED)
        else:
            refined = refine_query_with_ai(db_url, schema, current_sql, user_input)
            if refined:
                current_sql = refined
                run_sql(db_url, refined)

@app.command()
def query(
    query_text: Optional[str] = typer.Argument(None, help="Natural language query"),
    db: str = typer.Option(..., help="DB URL or path"),
    multi_turn: bool = typer.Option(False, "--multi-turn"),
    execute: bool = typer.Option(True)
):
    """Convert natural language to SQL and execute on any database."""
    db_url = get_db_url(db)
    if multi_turn:
        multi_turn_conversation(db_url)
    else:
        if not query_text:
            query_text = typer.prompt("Enter query")
        schema = get_db_schema(db_url)
        prompt = f"{schema}

Request: {query_text}

Return ONLY SQL in ```sql block."
        result = subprocess.run(f'gh copilot -p "{prompt}"', shell=True, capture_output=True, text=True)
        sql_match = re.search(r"```sql
([\s\S]*?)
```", result.stdout, re.DOTALL)
        if sql_match:
            generated_sql = sql_match.group(1).strip()
            typer.secho(f"
✓ SQL: {generated_sql}", fg=typer.colors.GREEN)
            if execute and typer.confirm("Run?"):
                run_sql(db_url, generated_sql)

if __name__ == "__main__":
    app()
