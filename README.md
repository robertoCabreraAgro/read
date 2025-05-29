# AI Dungeon Master CLI

This repository contains a small command line tool that uses an AI model and a SQLAlchemy database to manage a role playing game world.

## Setup

1. **Create a virtual environment** for Python 3.10 or later and activate it.
2. Run `pip install -r requirements.txt` to install the dependencies. This
   includes the `psycopg2-binary` driver required for connecting to PostgreSQL
   databases.
3. Copy `.env.example` to `.env` and fill in the values for `DATABASE_URL` and `OPENAI_API_KEY`.
4. Seed the database with `python populate_db.py`.
5. Start the interactive CLI with `python main.py`.

If you plan to use PostgreSQL, make sure the PostgreSQL client libraries are
installed on your system so that SQLAlchemy and `psycopg2-binary` can connect
properly.
