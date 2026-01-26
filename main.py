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


def get_db_url(db_input: str) -> str:
    """Converts a database path or connection string into a valid SQLAlchemy URL."""
    if "://" in db_input:
        return db_input
    return f"sqlite:///{db_input}"


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


def run_sql(db_url: str, sql: str):
    """Execute SQL and display results in a formatted table."""
    try:
        engine = create_engine(db_url)
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
                    f"\n✓ Command executed successfully. Affected rows: {result.rowcount}",
                    fg=typer.colors.GREEN,
                )

    except SQLAlchemyError as e:
        typer.secho(f"Database Error: {e}", fg=typer.colors.RED)
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED)


def refine_query_with_ai(
    db_url: str,
    schema: str,
    previous_sql: str,
    refinement_request: str,
) -> Optional[str]:
    """Use AI to refine a previous query based on user feedback."""
    context = f"""Schema:
{schema}

Previous Generated SQL:
{previous_sql}

Refinement Request:
{refinement_request}
"""

    agent_prompt = (
        "You are a SQL expert. "
        f"{context}\n"
        "Please refine the SQL query based on the refinement request. "
        "Return ONLY the SQL query in a code block (between ```sql and ```)."
    )

    agent_cmd = f'gh copilot -p "{agent_prompt}"'

    try:
        result = subprocess.run(
            agent_cmd, shell=True, capture_output=True, text=True
        )
        output = result.stdout

        sql_match = re.search(
            r"```sql\s*([\s\S]*?)\s*```", output, re.DOTALL
        )

        if sql_match:
            generated_sql = sql_match.group(1).strip()
            typer.secho(
                f"\n✓ Refined SQL:\n{generated_sql}",
                fg=typer.colors.GREEN,
                bold=True,
            )
            return generated_sql
        else:
            typer.secho(
                "\n⚠ Could not find a SQL block in the response.",
                fg=typer.colors.YELLOW,
            )
            return None

    except Exception as e:
        typer.secho(f"Error during refinement: {e}", fg=typer.colors.RED)
        return None


def multi_turn_conversation(db_url: str):
    """Interactive multi-turn conversation mode for iterative query refinement."""
    schema = get_db_schema(db_url)

    typer.secho(
        "\n🔄 Entering Multi-Turn Conversation Mode",
        fg=typer.colors.CYAN,
        bold=True,
    )
    typer.secho(
        "Type 'exit' or 'quit' to end the session.\n",
        fg=typer.colors.CYAN,
    )

    current_sql = None

    while True:
        user_input = typer.prompt("You").strip()

        if user_input.lower() in {"exit", "quit"}:
            typer.secho(
                "\n👋 Goodbye! Session ended.",
                fg=typer.colors.CYAN,
            )
            break

        if not current_sql:
            prompt = f"""You are a SQL expert.
{schema}

Request:
{user_input}

Return ONLY the SQL query in a code block (between ```sql and ```).
"""
            agent_cmd = f'gh copilot -p "{prompt}"'

            try:
                result = subprocess.run(
                    agent_cmd, shell=True, capture_output=True, text=True
                )
                output = result.stdout

                sql_match = re.search(
                    r"```sql\s*([\s\S]*?)\s*```", output, re.DOTALL
                )

                if sql_match:
                    current_sql = sql_match.group(1).strip()
                    typer.secho(
                        f"\n✓ Generated SQL:\n{current_sql}",
                        fg=typer.colors.GREEN,
                        bold=True,
                    )
                    run_sql(db_url, current_sql)
                else:
                    typer.secho(
                        "\n⚠ Could not find a SQL block in the response.",
                        fg=typer.colors.YELLOW,
                    )

            except Exception as e:
                typer.secho(f"Error: {e}", fg=typer.colors.RED)

        else:
            refined_sql = refine_query_with_ai(
                db_url, schema, current_sql, user_input
            )
            if refined_sql:
                current_sql = refined_sql
                run_sql(db_url, refined_sql)
            else:
                typer.secho(
                    "\nCould not process refinement. Please try again.",
                    fg=typer.colors.YELLOW,
                )


@app.command()
def query(
    query_text: Optional[str] = typer.Argument(
        None, help="Natural language query"
    ),
    db: str = typer.Option(
        ..., help="Path to SQLite file or Database URL"
    ),
    multi_turn: bool = typer.Option(
        False, "--multi-turn", help="Enable interactive mode"
    ),
    execute: bool = typer.Option(
        True, help="Automatically run the query"
    ),
):
    """Convert natural language to SQL and execute on any SQLAlchemy-supported database."""
    db_url = get_db_url(db)

    if multi_turn:
        multi_turn_conversation(db_url)
        return

    if not query_text:
        query_text = typer.prompt(
            "Enter your database query in plain English"
        )

    schema = get_db_schema(db_url)

    prompt = f"""You are a SQL expert.
{schema}

Request:
{query_text}

Return ONLY the SQL query in a code block (between ```sql and ```).
"""

    agent_cmd = f'gh copilot -p "{prompt}"'
    result = subprocess.run(
        agent_cmd, shell=True, capture_output=True, text=True
    )
    output = result.stdout

    typer.secho(
        "\n--- COPILOT RESPONSE ---",
        fg=typer.colors.CYAN,
        bold=True,
    )
    typer.echo(output)

    sql_match = re.search(
        r"```sql\s*([\s\S]*?)\s*```", output, re.DOTALL
    )

    if sql_match:
        generated_sql = sql_match.group(1).strip()
        typer.secho(
            f"\n✓ Extracted SQL:\n{generated_sql}",
            fg=typer.colors.GREEN,
            bold=True,
        )

        if execute and typer.confirm("🔍 Run this query?"):
            run_sql(db_url, generated_sql)
    else:
        typer.secho(
            "\n⛔ Could not find a SQL block in the response.",
            fg=typer.colors.YELLOW,
        )
        if typer.confirm("Do you want to paste the SQL manually?"):
            manual_sql = typer.prompt(
                "Please paste the SQL manually",
                show_default=False,
            )
            if manual_sql:
                run_sql(db_url, manual_sql)


if __name__ == "__main__":
    app()
