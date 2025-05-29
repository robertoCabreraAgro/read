# AI Dungeon Master CLI

This project provides a command line interface for running a small
AI‑assisted Dungeon Master. Game data is stored in a SQL database and the
agent can query OpenAI's API when an API key is configured.

## Setup

1. Create a virtual environment and activate it.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and adjust `DATABASE_URL` and
   `OPENAI_API_KEY`.
4. Populate the database:
   ```bash
   python populate_db.py
   ```
5. Start the CLI:
   ```bash
   python main.py
   ```

See the `help` command inside the CLI for available actions.
