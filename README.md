SQL-Speak: AI-Powered Natural Language Interface for Databases

SQL-Speak is a terminal-native utility that bridges the gap between natural language and structured data. It leverages the GitHub Copilot CLI as an intelligent translation layer, allowing developers to query local databases (like SQLite) using plain English. Instead of context-switching to a heavy GUI or manually writing complex JOINs for a quick data check, you can simply "speak" to your database directly from the command line.

## Features

- **Agentic AI Integration:** Uses GitHub Copilot CLI v0.0.394 with the new `-p` prompt syntax for advanced reasoning
- **Schema Auto-Discovery:** Automatically scans your SQLite database schema and provides context to the AI
- **Natural Language Queries:** Ask questions in plain English, get SQL automatically generated
- **One-Click Execution:** Automatically extracts and executes the generated SQL with user confirmation
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

4. **Verify GitHub Copilot CLI**
   ```bash
   gh copilot --version
   # Should output version 0.0.394 or higher
   ```

## Usage

### Quick Start with Sample Data

1. **Create a Sample Database**
   ```bash
   python3 setup_pro_db.py
   # This creates hospital.db with 4 tables: patients, doctors, appointments, prescriptions
   ```

2. **Run Your First Query**
   ```bash
   python3 main.py hospital.db "Show me all patients older than 30 with their conditions"
   ```

3. **Follow the Prompts**
   - The script will scan the database schema
   - GitHub Copilot CLI will generate the SQL in your terminal
   - Confirm with 'y' to execute the query
   - Results will display in a formatted table

### Advanced Usage

Query your own database:
```bash
python3 main.py your_database.db "Your natural language question here"
```

Skip auto-execution:
```bash
python3 main.py your_database.db "Your question" --no-execute
```

## Example Queries

Once you have `hospital.db` set up:

```bash
# Complex joins
python3 main.py hospital.db "Which patients were prescribed Artemether and who was their doctor?"

# Aggregations
python3 main.py hospital.py hospital.db "Give me a list of doctors and how many appointments each has had"

# Filtering
python3 main.py hospital.db "List all female patients with blood type O-"
```

## Project Structure

```
SQL-Speak/
├── main.py              # Main CLI application
├── setup_pro_db.py      # Creates sample hospital.db
├── setup_sample.py      # Legacy sample data
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── .gitignore          # Git ignore patterns
```

## How It Works

1. **Schema Discovery:** Queries `sqlite_master` to fetch all table definitions
2. **Agentic Prompt:** Constructs a detailed prompt including the schema for Copilot
3. **SQL Generation:** Runs `gh copilot -p "Your prompt"` to generate SQL
4. **Output Parsing:** Uses regex to extract SQL from markdown code blocks
5. **Execution:** Executes the SQL and formats results with `tabulate`

## Technology Stack

- **Python 3:** Core language
- **Typer:** CLI framework for beautiful command-line interfaces
- **SQLite3:** Database interaction (built-in)
- **Tabulate:** Pretty-printing of database results
- **GitHub Copilot CLI v0.0.394:** Agentic reasoning engine

## Requirements

See `requirements.txt` for full list:
```
typer[all]
tabulate
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Feel free to:
- Report issues
- Suggest features
- Submit pull requests

## Acknowledgments

- Built for the **GitHub Copilot CLI Challenge** (Jan 22 - Feb 15, 2026)
- Powered by the new Copilot CLI Agent (v0.0.394)
- Inspired by the need to make database querying more accessible
