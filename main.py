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
    """Converts a database path or connection string into a valid SQLAlchemy URL."""
    if "://" in db_input:
        return db_input
    # Assume SQLite file if no protocol is provided
    # For relative paths, we need 3 slashes, for absolute 4. sqlite:///path
    return f"sqlite:///{db_input}"

def get_db_schema(db_url: str) -> str:
    """Discovers the database schema using SQLAlchemy inspector."""
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
        typer.secho(f"Schema Discovery Error: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)

def run_sql(db_url: str, sql: str):
    """Execute SQL and display results in a formatted table."""
    try:
        engine = create_engine(db_url)
        with engine.connect() as connection:
            result = connection.execute(text(sql))
            
            # For SELECT queries
            if result.returns_rows:
                rows = result.fetchall()
                if rows:
                    # Convert rows to dictionaries using ._mapping
                    data = [dict(row._mapping) for row in rows]
                    typer.secho(f"
✓ Query Results:
", fg=typer.colors.GREEN, bold=True)
                    typer.echo(tabulate(data, headers="keys", tablefmt="grid"))
                else:
                    typer.secho(f"
✓ Query executed successfully (0 rows returned).", fg=typer.colors.GREEN)
            else:
                # For non-SELECT (INSERT, UPDATE, DELETE)
                connection.commit()
                typer.secho(f"
✓ Command executed successfully. Affected rows: {result.rowcount}", fg=typer.colors.GREEN)
    except SQLAlchemyError as e:
        typer.secho(f"Database Error: {e}", fg=typer.colors.RED)
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED)

def refine_query_with_ai(db_url: str, schema: str, previous_sql: str, refinement_request: str) -> Optional[str]:
    """Use AI to refine a previous query based on user feedback."""
    context = f"""
{schema}

Previous Generated SQL:
{previous_sql}

Refinement Request:
{refinement_request}

Please refine the SQL query based on the refinement request. Return ONLY the SQL query in a code block (between ```sql and ```).
"""
    agent_prompt = f"You are a SQL expert. {context}"
    agent_cmd = f'gh copilot -p "{agent_prompt}"'

    try:
        result = subprocess.run(agent_cmd, shell=True, capture_output=True, text=True)
        output = result.stdout

        sql_match = re.search(r"```sql
([\s\S]*?)
```", output, re.DOTALL)
        if sql_match:
            generated_sql = sql_match.group(1).strip()
            typer.secho(f"
✓ Refined SQL: {generated_sql}", fg=typer.colors.GREEN, bold=True)
            return generated_sql
        else:
            typer.secho(f"
⚠ Could not find a SQL block in the response.", fg=typer.colors.YELLOW)
            return None
    except Exception as e:
        typer.secho(f"Error during refinement: {e}", fg=typer.colors.RED)
        return None

def multi_turn_conversation(db_url: str):
    """Interactive multi-turn conversation mode for iterative query refinement."""
    schema = get_db_schema(db_url)
    typer.secho(f"
🔄 Entering Multi-Turn Conversation Mode", fg=typer.colors.CYAN, bold=True)
    typer.secho(f"Type 'exit' or 'quit' to end the session.
", fg=typer.colors.CYAN)

    current_sql = None

    while True:
        user_input = typer.prompt("You").strip()

        if user_input.lower() in ["exit", "quit"]:
            typer.secho(f"
👋 Goodbye! Session ended.", fg=typer.colors.CYAN)
            break

        if not current_sql:
            # First turn: Generate initial SQL from natural language
            agent_prompt = f"You are a SQL expert. {schema}

Request: {user_input}

Return ONLY the SQL query in a code block (between ```sql and ```)."
            agent_cmd = f'gh copilot -p "{agent_prompt}"'

            try:
                result = subprocess.run(agent_cmd, shell=True, capture_output=True, text=True)
                output = result.stdout

                sql_match = re.search(r"```sql
([\s\S]*?)
```", output, re.DOTALL)
                if sql_match:
                    current_sql = sql_match.group(1).strip()
                    typer.secho(f"
✓ Generated SQL: {current_sql}", fg=typer.colors.GREEN, bold=True)
                    run_sql(db_url, current_sql)
                else:
                    typer.secho(f"
⚠ Could not find a SQL block in the response.", fg=typer.colors.YELLOW)
            except Exception as e:
                typer.secho(f"Error: {e}", fg=typer.colors.RED)
        else:
            # Subsequent turns: Refine the query
            refined_sql = refine_query_with_ai(db_url, schema, current_sql, user_input)
            if refined_sql:
                current_sql = refined_sql
                run_sql(db_url, refined_sql)
            else:
                typer.secho(f"
Could not process refinement. Please try again.", fg=typer.colors.YELLOW)

@app.command()
def query(
    db: str = typer.Option(..., help="Path to SQLite file or Database URL (e.g., postgresql://user:pass@host/db)"),
    query_text: Optional[str] = typer.Option(None, help="Natural language query"),
    multi_turn: bool = typer.Option(False, "--multi-turn", help="Enable interactive multi-turn conversation mode"),
    execute: bool = typer.Option(True, help="Automatically run the query after generation")
):
    """Convert natural language to SQL and execute on any SQLAlchemy-supported database."""
    
    db_url = get_db_url(db)
    
    if multi_turn:
        multi_turn_conversation(db_url)
    else:
        if not query_text:
            query_text = typer.prompt("Enter your database query in plain English")

        schema = get_db_schema(db_url)
        agent_prompt = f"You are a SQL expert. {schema}

Request: {query_text}

Return ONLY the SQL query in a code block (between ```sql and ```)."
        
        agent_cmd = f'gh copilot -p "{agent_prompt}"'
        result = subprocess.run(agent_cmd, shell=True, capture_output=True, text=True)
        output = result.stdout

        typer.secho(f"
--- COPILOT RESPONSE ---", fg=typer.colors.CYAN, bold=True)
        typer.echo(output)

        sql_match = re.search(r"```sql
([\s\S]*?)
```", output, re.DOTALL)

        if sql_match:
            generated_sql = sql_match.group(1).strip()
            typer.secho(f"
✓ Extracted SQL: {generated_sql}", fg=typer.colors.GREEN, bold=True)

            if execute:
                if typer.confirm("🔍 Run this query?"):
                    run_sql(db_url, generated_sql)
            else:
                typer.secho(f"
Skipping execution as requested.", fg=typer.colors.YELLOW)
        else:
            typer.secho(f"
⛔ Could not find a SQL block in the response.", fg=typer.colors.YELLOW)
            if typer.confirm("Do you want to paste the SQL manually?"):
                manual_sql = typer.prompt("Please paste the SQL manually", show_default=False)
                if manual_sql:
                    run_sql(db_url, manual_sql)

if __name__ == "__main__":
    app()
