# 🗣️ SQL-Speak

SQL-Speak is a terminal-native, AI-powered tool that lets you query databases using plain English.
It translates natural language into SQL using the GitHub Copilot CLI, executes the query, and displays results — all from your terminal.

Works with:
✅ **SQLite** (local .db files)
✅ **PostgreSQL**
✅ **Large benchmark databases** (10M+ rows) via a safe benchmark profile

## ✨ Features

🧠 **Natural language → SQL** (powered by GitHub Copilot)
🔍 **Automatic schema discovery** (tables + columns)
⚡ **One-shot queries** or interactive **multi-turn conversations**
🧪 **Safe benchmark mode** for large PostgreSQL datasets
📊 Built-in **EXPLAIN ANALYZE preview** for performance insight
🧰 **Zero ORM knowledge** required

## 📦 Installation

1. **Clone the repo**
   ```bash
   git clone https://github.com/jemiridaniel/SQL-Speak.git
   cd SQL-Speak
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install GitHub Copilot CLI**
   SQL-Speak uses the GitHub Copilot CLI to generate SQL.
   Make sure you are authenticated:
   ```bash
   gh auth login
   ```
   And that Copilot CLI works:
   ```bash
   gh copilot -h
   ```

## 🚀 Basic Usage (One-Shot Queries)

Run commands from the repo root.

### 🩺 SQLite example (unchanged)
```bash
python3 main.py --db hospital.db "Show me all patients older than 30"
```

Other examples:
```bash
python3 main.py --db hospital.db "How many patients are in the database?"
python3 main.py --db hospital.db "Show all appointments for patient with id 1"
```

### 🐘 PostgreSQL Usage
You can point SQL-Speak at any PostgreSQL database using a connection string.
```bash
python3 main.py \
  --db "postgresql://username@localhost:5432/my_database" \
  "Show total revenue by country"
```
No code changes required — SQLAlchemy handles the dialect automatically.

## 🏁 PostgreSQL Benchmark Profile (NEW)
For large datasets (millions of rows), SQL-Speak includes a benchmark-safe profile.

**Enable benchmark mode**
```bash
python3 main.py \
  --db "postgresql://username@localhost:5432/sql_speak_benchmark" \
  --profile benchmark-postgres \
  "Show top 10 customers by lifetime spend"
```

### What benchmark mode does
🔒 **Read-only** (SELECT queries only)
⚠️ **Auto-applies LIMIT 100** if missing
📊 Shows **EXPLAIN ANALYZE** before execution
🧠 Prompts Copilot to generate **PostgreSQL-optimized SQL**
🚫 **Prevents accidental full-table scans** in the terminal

This makes SQL-Speak safe for real analytics workloads.

## 🔄 Multi-Turn Interactive Mode
You can have a conversation with your database.

**SQLite**
```bash
python3 main.py --db hospital.db --multi-turn
```

**PostgreSQL benchmark mode**
```bash
python3 main.py \
  --db "postgresql://username@localhost:5432/sql_speak_benchmark" \
  --profile benchmark-postgres \
  --multi-turn
```

**Example interaction:**
*   **You:** Show revenue by country
*   **You:** Only include completed payments
*   **You:** Order by revenue descending
*   **You:** Limit to top 5

Each step refines the previous query.

## 🔍 Schema Exploration
You can ask schema-aware questions to help Copilot understand the database:
```bash
python3 main.py --db hospital.db \
  "What tables exist in this database and what columns do they have?"

python3 main.py \
  --db "postgresql://username@localhost:5432/sql_speak_benchmark" \
  "Show me all columns in the orders table with sample rows"
```

## 🏗️ SQL-Speak Generator (Benchmarks)
SQL-Speak includes a PostgreSQL data generator capable of producing 10M+ rows for benchmarking.

**Example:**
```bash
python -m generator.cli \
  --db "postgresql://username@localhost:5432/sql_speak_benchmark" \
  --scale 1 \
  --truncate
```
This generates: `customers`, `products`, `orders`, `order_items`, `payments`. Perfect for testing analytics queries at scale.

## 🧠 How It Works
1. Inspects your database schema using SQLAlchemy
2. Builds a context-rich prompt
3. Sends it to GitHub Copilot CLI
4. Extracts SQL from the response
5. (Optionally) previews performance
6. Executes and formats results

## 🛡️ Safety Philosophy
*   **SQLite:** full flexibility
*   **PostgreSQL default:** normal execution
*   **PostgreSQL benchmark profile:**
    *   SELECT-only
    *   Auto-LIMIT
    *   EXPLAIN preview
    *   Explicit user confirmation

This keeps experimentation safe and intentional.

## 🏷️ Recommended GitHub Topics
`sql`, `natural-language`, `nl2sql`, `postgresql`, `sqlite`, `copilot`, `cli`, `database`, `benchmarking`

## 📌 Roadmap Ideas
*   `--explain-only` mode
*   Query timing & cost stats
*   Result sampling
*   Saved query packs
*   Read-only production mode
*   Query history & replay

## 📜 License
MIT License.

## 🙌 Author
Built by **Daniel Jemiri**
GitHub: [https://github.com/jemiridaniel](https://github.com/jemiridaniel)
