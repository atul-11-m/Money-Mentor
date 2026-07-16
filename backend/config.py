import os
from dotenv import load_dotenv

load_dotenv()

# SQLite database file (created automatically on first run).
# Defaults to finance.db sitting next to this file.
DB_PATH = os.environ.get(
    "DB_PATH",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "finance.db"),
)

# GPT / OpenAI-compatible chat endpoint used by the advisor chatbot.
# Any OpenAI-compatible endpoint works — just point OPENAI_API_URL at it.
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_API_URL = os.environ.get("OPENAI_API_URL", "https://api.openai.com/v1/chat/completions")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
