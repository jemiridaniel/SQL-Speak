# 🗣️ SQL-Speak

SQL-Speak is a terminal-native, AI-powered tool that lets you query databases using plain English.
It translates natural language into SQL using the GitHub Copilot CLI, executes the query, and displays results — all from your terminal.

Works with:
✅ **SQLite** (local .db files)
✅ **PostgreSQL**
✅ **Large benchmark databases** (10M+ rows) via a safe benchmark profile

## ✨ Features

🧠 **Natural language → SQL** (GitHub Copilot, with Perplexity fallback if configured)  
🔍 **Automatic schema discovery** (tables + columns)  
⚡ **One-shot queries** or interactive **multi-turn conversations** (CLI + web)  
🧪 **Safe benchmark mode** for large PostgreSQL datasets  
📊 Built-in **EXPLAIN ANALYZE preview** for performance insight  
🌐 **Web console** (Next.js) with data source/profile selection  
💬 **Multi-turn chat** over your database from the web console  
📥 **Download query results as CSV** directly from the browser  
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

## 🏗️ Project Architecture

SQL-Speak is built as a multi-component system designed to separate concerns and provide flexibility:

```
SQL-Speak/
├── main.py                 # CLI entry point with argument parsing
├── sql_speak.py            # Core CLI orchestration logic
├── core/                   # Core engine modules
│   ├── copilot.py         # GitHub Copilot CLI integration
│   ├── db.py              # Database connection & detection
│   ├── engine.py          # Query execution engine
│   ├── history_db.py      # Query history tracking
│   ├── logging.py         # Logging configuration
│   ├── models.py          # Data models
│   └── profiles.py        # Execution profiles (benchmark, standard)
├── api/                   # REST API backend (Python/Flask)
│   ├── app.py             # API server setup
│   ├── auth.py            # Authentication & authorization
│   ├── models.py          # API data models
│   └── dependencies.py    # Dependency injection
├── web/                   # Web dashboard (Next.js/TypeScript)
│   ├── src/               # React components & pages
│   ├── public/            # Static assets
│   └── package.json       # Node.js dependencies
├── generator/             # PostgreSQL data generator
│   ├── generators/        # Data generation modules
│   ├── cli.py             # Generator CLI
│   ├── postgres.py        # PostgreSQL-specific generator
│   └── schema.sql         # Schema definitions
├── config/                # Configuration management
│   ├── example.toml       # Example configuration
│   └── local.toml         # Local environment config
└── requirements.txt       # Python dependencies
```

### Component Overview

**CLI Layer** (`main.py`, `sql_speak.py`)
- User-facing terminal interface powered by Typer
- Handles argument parsing and command routing
- Manages multi-turn interactive conversations

**Core Engine** (`core/`)
- Database connection management and detection
- Schema introspection using SQLAlchemy
- Copilot CLI integration for natural language → SQL translation
- Query execution and result formatting
- Performance profiling (EXPLAIN ANALYZE)
- Query history tracking

**API Server** (`api/`)
- RESTful endpoints for programmatic access
- Authentication and authorization layer
- Data models for request/response handling
- Dependency injection for service management

**Web Dashboard** (`web/`)
- Modern Next.js application for enterprise use
- TypeScript for type safety
- Real-time query execution and result visualization
- User management and access control
- Query history and favorites

**Data Generator** (`generator/`)
- PostgreSQL data generation for benchmarking
- Supports 10M+ row datasets
- Realistic data models (customers, orders, payments, etc.)
- CLI interface for easy data setup

**Configuration** (`config/`)
- TOML-based configuration files
- Environment-specific settings (local, staging, production)
- Profile definitions (standard, benchmark)

## 💻 Development Setup

### Prerequisites

- Python 3.8+
- Node.js 16+ (for web dashboard)
- GitHub CLI with Copilot extension
- PostgreSQL 12+ (for benchmark datasets)
- SQLite 3 (included by default)

### Backend (CLI & API)

```bash
# Clone the repository
git clone https://github.com/jemiridaniel/SQL-Speak.git
cd SQL-Speak

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify GitHub Copilot CLI
gh auth login
gh copilot -h
```

### Frontend (Web Dashboard)

```bash
cd web

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

Once the dev server is running:

- Open http://localhost:3000
- Sign in with your GitHub account (GitHub Copilot CLI auth)
- Select a **data source** (e.g. `hospital_sqlite`, `benchmark_postgres`)
- Select an execution **profile** (e.g. `sqlite-dev`, `benchmark-postgres`)
- Type a natural language query and click **Run query**
- Use the **Multi-turn chat** panel to ask follow-up questions about the same data
- Click **Download CSV** in the Results card to export the current table as `query_results.csv`

### Running the CLI

```bash
# One-shot query on SQLite
python3 main.py --db hospital.db "Show me all patients older than 30"

# Multi-turn interactive mode
python3 main.py --db hospital.db --multi-turn

# PostgreSQL with benchmark profile
python3 main.py --db "postgresql://user@localhost/mydb" --profile benchmark-postgres "Show revenue by country"
```

### Running the API Server

```bash
# From repo root, in your virtualenv
uvicorn api.app:app --reload

# API will be available at:
#   http://127.0.0.1:8000
# Interactive docs:
#   http://127.0.0.1:8000/docs
```
## 📦 Dependencies

### Python Packages

| Package | Purpose |
|---------|----------|
| `typer[all]` | CLI framework with type hints |
| `tabulate` | Pretty-print database results |
| `pexpect` | Interact with GitHub Copilot CLI |
| `sqlalchemy` | ORM and database toolkit |
| `psycopg2-binary` | PostgreSQL adapter |
| `mysql-connector-python` | MySQL support |

### Node.js Packages (Web)

- `next` - React framework
- `react` - UI library
- `typescript` - Type safety
- `tailwindcss` - CSS framework (optional)

## 🔌 API Endpoints (Planned)

```
POST /api/query           # Execute a query
GET  /api/schema          # Get database schema
POST /api/save-query      # Save a query
GET  /api/history         # Query history
GET  /api/auth/user       # Get current user
POST /api/auth/login      # User login
```

## 🔧 Configuration Guide

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/sql_speak

# API
API_PORT=8000
API_SECRET_KEY=your-secret-key

# Copilot
GH_TOKEN=your-github-token
```

### TOML Configuration

Edit `config/local.toml` for local settings:

```toml
[database]
url = "postgresql://user@localhost/sql_speak"
read_only = false

[profiles]
[profiles.benchmark-postgres]
mode = "benchmark"
read_only = true
auto_limit = 100
explain_analyze = true
```

## 🚀 Deployment

### API Server

```bash
# Using Gunicorn (production)
gunicorn -w 4 -b 0.0.0.0:8000 api.app:app
```

### Web Dashboard

```bash
# Build and start
cd web
npm run build
npm run start

# Or deploy to Vercel
vercel deploy
```

## 🛠️ Contributing

To extend SQL-Speak:

### Adding Database Support

1. Add dialect detection in `core/db.py`
2. Implement connection logic in `core/engine.py`
3. Test with sample database
4. Document in README

### Adding Features

1. Implement in appropriate module
2. Add tests
3. Update relevant component
4. Document API changes

## 📚 Module Documentation

### `core/copilot.py`
Handles interaction with GitHub Copilot CLI. Sends database schema context and user prompts to Copilot, extracts SQL from responses.

### `core/engine.py`
Orchestrates the query pipeline: schema detection → prompt building → Copilot invocation → SQL execution → result formatting.

### `core/db.py`
Manages database connections, schema introspection, and result formatting. Supports SQLite, PostgreSQL, and MySQL.

### `core/profiles.py`
Defines execution profiles (standard, benchmark). Benchmark mode adds safety constraints like auto-LIMIT, read-only enforcement, and EXPLAIN ANALYZE preview.

## 📝 License

MIT License.

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
