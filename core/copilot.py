# core/copilot.py

import subprocess
from typing import Optional

def get_sql_from_copilot(user_query: str, schema_context: str) -> Optional[str]:
    prompt = (
        "You are an assistant that ONLY writes valid SQL queries.\n"
        "Rules:\n"
        "1. Use ONLY the tables and columns from the schema.\n"
        "2. Do NOT return any explanation, comments, or shell commands.\n"
        "3. Return a single SQL statement ending with a semicolon.\n"
        "4. Prefer SELECT queries and avoid DML/DDL unless explicitly asked.\n\n"
        f"Schema:\n{schema_context}\n\n"
        f"User request: {user_query}\n\n"
        "SQL query:"
    )

    cmd = ["gh", "copilot", "-p", prompt]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        raw_out = result.stdout.strip()
        raw_err = result.stderr.strip()

        print("COPILOT STDOUT:", repr(raw_out))
        print("COPILOT STDERR:", repr(raw_err))

        if result.returncode != 0 or not raw_out:
            return None

        cleaned = raw_out.strip()

        # Strip Markdown fences like ```sql ... ```
        if cleaned.startswith("```"):
            # remove leading ```sql or ``` and trailing ```
            cleaned = cleaned.strip("`")
            # After stripping backticks, often looks like "sql\nSELECT ...".
            # Remove leading "sql" token if present.
            if cleaned.lower().startswith("sql"):
                cleaned = cleaned[3:]
            cleaned = cleaned.strip()

        # Final trim of quotes/newlines
        cleaned = cleaned.strip().strip('"').strip("'").strip()
        return cleaned
    except subprocess.SubprocessError as e:
        print(f"Error calling Copilot: {e}")
        return None
