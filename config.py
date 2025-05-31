import os
from dotenv import load_dotenv

# Load environment variables from a .env file if it exists
# This is good practice for local development.
# The .env file should not be committed to version control.
load_dotenv()

# --- Database Configuration ---
# Default to a local SQLite DB if no specific URL is set in the environment.
# Example for PostgreSQL: "postgresql://user:password@localhost:5432/dbname"
# Example for SQLite: "sqlite:///./your_database_file.db"
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./default_dm_database.db")

# --- OpenAI API Configuration ---
# API key is loaded directly from the environment variable.
# Ensure OPENAI_API_KEY is set in your .env file or system environment.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# --- Other Potential Configurations ---
# Example: Define a default AI model to be used across the application.
# DEFAULT_AI_MODEL = os.getenv("DEFAULT_AI_MODEL", "gpt-3.5-turbo")

# Example: Set a global log level.
# LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# --- Application Behavior Flags ---
# Example: A flag to enable or disable certain debug features.
# DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"


# --- Print loaded configurations for verification (optional, good for debugging startup) ---
# print(f"CONFIG: Database URL = {DATABASE_URL}")
# if OPENAI_API_KEY:
#     print("CONFIG: OpenAI API Key is LOADED.")
# else:
#     print("CONFIG: OpenAI API Key is NOT SET.")
# print(f"CONFIG: Default AI Model = {DEFAULT_AI_MODEL}")
# print(f"CONFIG: Log Level = {LOG_LEVEL}")
# print(f"CONFIG: Debug Mode = {DEBUG_MODE}")
