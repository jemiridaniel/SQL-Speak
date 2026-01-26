import typer
import sqlite3
import subprocess
import re
import os
from tabulate import tabulate
from typing import Optional

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
        typer.secho(f"Error reading schema: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)

def run_sql(db_path: str, sql_query: str):
    """Helper to execute SQL and print tabulated results."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        
        if rows:
            headers = [desc[0] for desc in cursor.description]
            typer.echo("\n" + tabulate(rows, headers=headers, tablefmt="grid"))
        else:
            typer.secho("\n✅ Executed successfully. No results returned.", fg=typer.colors.GREEN)
        conn.close()
    except sqlite3.Error as e:
        typer.secho(f"\n❌ SQL Error: {e}", fg=typer.colors.RED)

@app.command()
def ask(
    db: str = typer.Argument(..., help="Path to the SQLite database file."),
    question: str = typer.Argument(..., help="Your question in plain English."),
    execute: bool = typer.Option(True, "--execute/--no-execute", help="Automatically prompt to execute.")
):
    """Query your database using natural language and GitHub Copilot CLI."""
    
    # 1. Scanning Schema
    typer.echo(f"🧠 Scanning database '{db}' for context...")
    schema = get_db_schema(db)
    
    # 2. Build Agentic Prompt
    # We ask for a markdown code block to make extraction reliable
    agent_prompt = (
        f"Act as a SQLite expert. Schema:\n{schema}\n"
        f"Question: '{question}'.\n"
        "Instructions: Provide the valid SQLite query inside a markdown code block (```sql ... ```)."
    )
    
    typer.echo(f"📡 Consulting GitHub Copilot CLI...")
    
    try:
        # 3. Call GitHub Copilot Agent
        # We use -p for the new agentic prompt syntax
        agent_cmd = f'gh copilot -p "{agent_prompt}"'
        
        # Capture output so we can parse the SQL block
        result = subprocess.run(agent_cmd, shell=True, capture_output=True, text=True)
        output = result.stdout
        
        # Print AI output for transparency
        typer.secho("\n--- COPILOT RESPONSE ---", fg=typer.colors.CYAN, bold=True)
        typer.echo(output)
        
        # 4. Extract SQL using Regex
        # Matches the first block found between ```sql and ```
        sql_match = re.search(r"```sql\n(.*?)\n```", output, re.DOTALL)
        
        if sql_match:
            generated_sql = sql_match.group(1).strip()
            typer.secho(f"\n✨ Extracted SQL: {generated_sql}", fg=typer.colors.GREEN, bold=True)
            
            # 5. Confirm and Run
            if execute and typer.confirm("🚀 Run this query?"):
                run_sql(db, generated_sql)
        else:
            typer.secho("\n⚠️ Could not find a SQL block in the response.", fg=typer.colors.YELLOW)
            if execute:
                manual_sql = typer.prompt("Please paste the SQL manually to execute (or Enter to cancel)", default="", show_default=False)
                if manual_sql:
                    run_sql(db, manual_sql)

    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED)

if __name__ == "__main__":
    app()
