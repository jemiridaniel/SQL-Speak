SQL-Speak: AI-Powered Natural Language Interface for Databases

SQL-Speak is a terminal-native utility that bridges the gap between natural language and structured data. It leverages the GitHub Copilot CLI as an intelligent translation layer, allowing developers to query databases (SQLite, PostgreSQL, MySQL) using plain English.

## Features

- **Agentic AI Integration:** Uses GitHub Copilot CLI v0.0.394 with the new `-p` prompt syntax for advanced reasoning
- **Multi-Engine Support:** Connect to SQLite, PostgreSQL, and MySQL using SQLAlchemy
- **Schema Auto-Discovery:** Automatically scans your database schema to provide context to the AI
- **Natural Language Queries:** Ask questions in plain English, get SQL automatically generated
- **Interactive Multi-Turn Mode:** Refine and iterate on queries with natural language feedback
- **Pretty Output:** Uses tabulate to display results in a clean, readable table format

## Installation

### Prerequisites

- Python 3.8+
- GitHub Copilot CLI installed and authenticated
- GitHub Copilot subscription (required for the CLI)

### Setup Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/jemiridaniel/SQL-Speak.git
   cd SQL-Speak
   ```

2. **Create a Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### SQLite (Default)
```bash
python3 main.py --db hospital.db "Show me all patients older than 30"
```

### PostgreSQL
```bash
python3 main.py --db "postgresql://user:password@localhost:5432/dbname" "How many appointments are scheduled for today?"
```

### MySQL
```bash
python3 main.py --db "mysql+mysqlconnector://user:password@localhost:3306/dbname" "List all prescriptions for patient ID 101"
```

### Interactive Multi-Turn Mode
Refine your queries interactively with natural language feedback:
```bash
python3 main.py --db hospital.db --multi-turn
```

## How It Works

1. **Schema Discovery:** Uses SQLAlchemy's Inspector to fetch table definitions and column types
2. **Agentic Prompt:** Constructs a detailed prompt including the schema and dialect info for Copilot
3. **SQL Generation:** Runs `gh copilot -p "Your prompt"` to generate engine-specific SQL
4. **Execution:** Executes the SQL via SQLAlchemy and formats results with `tabulate`

## Requirements
- `typer[all]`
- `tabulate`
- `sqlalchemy`
- `psycopg2-binary` (for PostgreSQL)
- `mysql-connector-python` (for MySQL)

## License
MIT License - see the LICENSE file for details.

## Acknowledgments
Built for the GitHub Copilot CLI Challenge (Jan 22 - Feb 15, 2026). Powered by the new Copilot CLI Agent.
