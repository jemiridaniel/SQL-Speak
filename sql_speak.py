import subprocess
import sqlite3
import sys

def get_sql_from_copilot(user_query, schema_context):
    # Construct the prompt including schema context for better accuracy
    prompt = f"Given this SQLite schema: {schema_context}. Generate ONLY the SQL query for: {user_query}"
    
    # Execute gh copilot suggest
    # We use -t shell because it's the most flexible for raw output
    cmd = ["gh", "copilot", "suggest", "-t", "shell", prompt]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        # Note: You'll need to parse the specific output of gh copilot suggest 
        # to extract just the SQL string from its interactive UI response.
        return result.stdout.strip() 
    except subprocess.CalledProcessError as e:
        print(f"Error calling Copilot: {e}")
        return None

def execute_query(db_path, sql_query):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        for row in rows:
            print(row)
    except sqlite3.Error as e:
        print(f"SQL Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python sql_speak.py 'your natural language query'")
        sys.exit(1)
    
    user_input = sys.argv[1]
    # Example Schema Context (You can automate this with 'SELECT name FROM sqlite_master')
    schema = "Table 'users' (id, name, email); Table 'orders' (id, user_id, total, date)"
    
    sql = get_sql_from_copilot(user_input, schema)
    if sql:
        print(f"Generated SQL: {sql}")
        # execute_query("my_database.db", sql)
