import typer
import sqlite3
import subprocess
import re
import os
from tabulate import tabulate
from typing import Optional, List

app = typer.Typer(help="SQL-Speak: Talk to your database in plain English via GitHub Copilot CLI.")

def get_db_schema(db_path: str) -> str:
    """Automatically discovers the SQLite schema to provide context to the AI."""
    if not os.path.exists(db_path):
        typer.secho(f"Error: Database file '{db_path}' not found.", fg=typer.colors.RED)
        raise typer.Exit(1)

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        # Fetch all table creation statements
        cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        conn.close()

        if not tables:
            return "The database is currently empty."

        schema_text = "Database Schema:\n"
        for name, sql in tables:
            schema_text += f"- Table '{name}': {sql}\n"
        return schema_text
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)

def run_sql(db: str, sql: str):
    """Execute SQL and display results in a formatted table."""
    try:
        conn = sqlite3.connect(db)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        conn.commit()
        conn.close()

        if results:
            # Convert rows to dictionaries
            data = [dict(row) for row in results]
            typer.secho(f"\n✓ Query Results:\n", fg=typer.colors.GREEN, bold=True)
            typer.echo(tabulate(data, headers="keys", tablefmt="grid"))
        else:
            typer.secho(f"\n✓ Query executed successfully (0 rows returned).", fg=typer.colors.GREEN)
    except sqlite3.Error as e:
        typer.secho(f"Database Error: {e}", fg=typer.colors.RED)
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED)

def refine_query_with_ai(db_path: str, schema: str, previous_sql: str, refinement_request: str) -> Optional[str]:
    """Use AI to refine a previous query based on user feedback."""
    context = f"""
Database Schema:
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

        sql_match = re.search(r"```sql\n([\s\S]*?)\n```", output, re.DOTALL)
        if sql_match:
            generated_sql = sql_match.group(1).strip()
            typer.secho(f"\n✓ Refined SQL: {generated_sql}", fg=typer.colors.GREEN, bold=True)
            return generated_sql
        else:
            typer.secho(f"\n⚠ Could not find a SQL block in the response.", fg=typer.colors.YELLOW)
            return None
    except Exception as e:
        typer.secho(f"Error during refinement: {e}", fg=typer.colors.RED)
        return None

def multi_turn_conversation(db_path: str):
    """Interactive multi-turn conversation mode for iterative query refinement."""
    schema = get_db_schema(db_path)
    typer.secho(f"\n🔄 Entering Multi-Turn Conversation Mode", fg=typer.colors.CYAN, bold=True)
    typer.secho(f"Type 'exit' or 'quit' to end the session.\n", fg=typer.colors.CYAN)

    conversation_history: List[dict] = []
    current_sql = None

    while True:
        user_input = typer.prompt("You").strip()

        if user_input.lower() in ["exit", "quit"]:
            typer.secho(f"\n👋 Goodbye! Session ended.", fg=typer.colors.CYAN)
            break

        if not current_sql:
            # First turn: Generate initial SQL from natural language
            agent_prompt = f"You are a SQL expert. Convert this request to SQLite SQL.\n\nDatabase Schema:\n{schema}\n\nRequest: {user_input}\n\nReturn ONLY the SQL query in a code block (between ```sql and ```)."
            agent_cmd = f'gh copilot -p "{agent_prompt}"'

            try:
                result = subprocess.run(agent_cmd, shell=True, capture_output=True, text=True)
                output = result.stdout

                sql_match = re.search(r"```sql\n([\s\S]*?)\n```", output, re.DOTALL)
                if sql_match:
                    current_sql = sql_match.group(1).strip()
                    typer.secho(f"\n✓ Generated SQL: {current_sql}", fg=typer.colors.GREEN, bold=True)
                    conversation_history.append({"type": "query", "content": user_input, "sql": current_sql})
                    
                    # Execute the query
                    run_sql(db_path, current_sql)
                else:
                    typer.secho(f"\n⚠ Could not find a SQL block in the response.", fg=typer.colors.YELLOW)
            except Exception as e:
                typer.secho(f"Error: {e}", fg=typer.colors.RED)
        else:
            # Subsequent turns: Refine the query
            refined_sql = refine_query_with_ai(db_path, schema, current_sql, user_input)
            if refined_sql:
                current_sql = refined_sql
                conversation_history.append({"type": "refinement", "content": user_input, "sql": refined_sql})
                run_sql(db_path, refined_sql)
            else:
                typer.secho(f"\nCould not process refinement. Please try again.", fg=typer.colors.YELLOW)

@app.command()
def query(
    db: str = typer.Option(..., help="Path to SQLite database file"),
    query_text: Optional[str] = typer.Option(None, help="Natural language query (optional)"),
    multi_turn: bool = typer.Option(False, "--multi-turn", help="Enable interactive multi-turn conversation mode")
):
    """Convert natural language to SQL and execute on SQLite database."""
    
    if multi_turn:
        # Multi-turn conversation mode
        multi_turn_conversation(db)
    else:
        # Single query mode
        if not query_text:
            query_text = typer.prompt("Enter your database query in plain English")

        schema = get_db_schema(db)

        agent_prompt = f"You are a SQL expert. Convert this request to SQLite SQL.\n\nDatabase Schema:\n{schema}\n\nRequest: {query_text}\n\nReturn ONLY the SQL query in a code block (between ```sql and ```)."
        
        # We use -p for the new agentic prompt syntax
        agent_cmd = f'gh copilot -p "{agent_prompt}"'

        # Capture output so we can parse the SQL block
        result = subprocess.run(agent_cmd, shell=True, capture_output=True, text=True)
        output = result.stdout

        # Print AI output for transparency
        typer.secho(f"\n--- COPILOT RESPONSE ---", fg=typer.colors.CYAN, bold=True)
        typer.echo(output)

        # 4. Extract SQL using Regex
        # Matches the first block found between ```sql and ```
        sql_match = re.search(r"```sql\n([\s\S]*?)\n```", output, re.DOTALL)

        if sql_match:
            generated_sql = sql_match.group(1).strip()
            typer.secho(f"\n✓ Extracted SQL: {generated_sql}", fg=typer.colors.GREEN, bold=True)

            # 5. Confirm and Run
            if typer.confirm("🔍 Run this query?"):
                run_sql(db, generated_sql)
            else:
                typer.secho(f"\n⛔ Could not find a SQL block in the response.", fg=typer.colors.YELLOW)
                if execute:
                    manual_sql = typer.prompt("Please paste the SQL manually to execute (or Enter to cancel)", default="")
                    if manual_sql:
                        run_sql(db, manual_sql)
        else:
            typer.secho(f"\n⛔ Could not find a SQL block in the response.", fg=typer.colors.YELLOW)
            if typer.confirm("Do you want to paste the SQL manually?"):
                manual_sql = typer.prompt("Please paste the SQL manually", show_default=False)
                if manual_sql:
                    run_sql(db, manual_sql)

if __name__ == "__main__":
    app()
