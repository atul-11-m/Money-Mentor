from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import pandas as pd
import os
import uuid
import requests
import io
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)

DB_FILE = "finance.db"

# --- Category rules ---
CATEGORY_RULES = {
    "Starbucks": "Dining",
    "McDonald": "Dining",
    "Chipotle": "Dining",
    "Shell": "Necessities",
    "Kroger": "Groceries",
    "Target": "Purchases",
    "Amazon": "Purchases",
    "Best Buy": "Purchases",
    "Spotify": "Subscriptions",
    "Netflix": "Subscriptions",
    "Electric": "Necessities",
    "Rent": "Necessities",
    "Uber": "Transportation",
    "Walgreens": "Purchases",
    "PayPal": "Transfers",
    "Venmo": "Transfers",
    "Direct Deposit": "Income",
    "ATM": "Cash",
    "Refund": "Refunds"
}

# --- Database setup ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            posting_date TEXT,
            description TEXT,
            amount REAL,
            type TEXT,
            balance REAL,
            category TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# In-memory session store for AI chats (simple, non-persistent)
AI_SESSIONS = {}

load_dotenv()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_API_URL = os.environ.get("GEMINI_API_URL")  # e.g. user-provided endpoint
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini")

def call_gemini_system(system_prompt: str, user_input: str):
    """
    Generic wrapper to call an external LLM endpoint compatible with a chat API.
    Requires GEMINI_API_URL and GEMINI_API_KEY environment variables to be set.

    The function sends a JSON payload and returns the assistant text.
    If GEMINI_API_URL or GEMINI_API_KEY is not set, returns a placeholder response.
    """
    if not GEMINI_API_KEY or not GEMINI_API_URL:
        return (
            "(No Gemini API configured) would analyze CSV using the following prompt:\n" + system_prompt
        )

    # If the configured URL is the Google Generative Language endpoint, use its expected shape
    def _flatten_candidate_text(cand):
        # Attempt to extract a textual reply from various provider candidate shapes
        try:
            # direct string
            if isinstance(cand, str):
                return cand
            # common direct fields
            if isinstance(cand, dict):
                if "content" in cand and isinstance(cand["content"], str):
                    return cand["content"]
                if "display" in cand and isinstance(cand["display"], str):
                    return cand["display"]
                # 'parts' (Google-like) may be a list of dicts with 'text'
                parts = cand.get("parts") or cand.get("content")
                if isinstance(parts, list):
                    texts = []
                    for p in parts:
                        if isinstance(p, dict):
                            # nested 'text' field
                            if "text" in p and isinstance(p["text"], str):
                                texts.append(p["text"])
                            # sometimes content is nested
                            elif "content" in p and isinstance(p["content"], str):
                                texts.append(p["content"])
                        elif isinstance(p, str):
                            texts.append(p)
                    if texts:
                        return "\n".join(texts)
            # fallback to string representation
            return str(cand)
        except Exception:
            return str(cand)

    try:
        if "generativelanguage.googleapis.com" in (GEMINI_API_URL or ""):
            headers = {
                "X-goog-api-key": GEMINI_API_KEY,
                "Content-Type": "application/json",
            }

            # Build the Google 'generateContent' style payload with a short contents array
            # We'll combine system + user into a single user content for the request body
            combined = f"SYSTEM:\n{system_prompt}\n\nUSER:\n{user_input}"
            payload = {
                "model": GEMINI_MODEL,
                "contents": [
                    {"parts": [{"text": combined}]}
                ],
            }

            r = requests.post(GEMINI_API_URL, json=payload, headers=headers, timeout=60)
            r.raise_for_status()
            data = r.json()

            # Google responses often include 'candidates' or 'output' fields
            if isinstance(data, dict):
                # candidates -> try to flatten the first candidate
                candidates = data.get("candidates") or data.get("candidate")
                if isinstance(candidates, list) and len(candidates) > 0:
                    return _flatten_candidate_text(candidates[0])
                # older/output shapes
                output = data.get("output") or data.get("result")
                if isinstance(output, str):
                    return output
                if isinstance(output, dict):
                    # try to flatten nested structures
                    # some providers return {'output': {'content': [...]}}
                    if "content" in output:
                        return _flatten_candidate_text(output.get("content"))
                    return str(output)
                # Some providers return text in nested fields
                return str(data)

        # Fallback: attempt a generic OpenAI-like call
        headers = {
            "Authorization": f"Bearer {GEMINI_API_KEY}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": GEMINI_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ],
            "temperature": 0.2,
        }

        r = requests.post(GEMINI_API_URL, json=payload, headers=headers, timeout=30)
        r.raise_for_status()
        data = r.json()

        # Try common response shapes (OpenAI-like)
        if isinstance(data, dict):
            if "choices" in data and len(data["choices"]) > 0:
                choice = data["choices"][0]
                # assistant message content
                msg = None
                if isinstance(choice, dict):
                    msg = (choice.get("message") or {}).get("content") if choice.get("message") else choice.get("text")
                if isinstance(msg, str):
                    return msg
            # fallback keys
            if "output" in data and isinstance(data["output"], str):
                return data["output"]
            if "message" in data and isinstance(data["message"], str):
                return data["message"]
            # as last resort, try to flatten the whole payload
            return str(data)

        return str(data)
    except Exception as e:
        return f"(LLM call failed) {str(e)}"

def categorize(description: str) -> str:
    for keyword, category in CATEGORY_RULES.items():
        if keyword.lower() in description.lower():
            return category
    return "Uncategorized"

# --- Upload CSV ---
@app.route("/upload", methods=["POST"])
def upload_csv():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    df = pd.read_csv(file)
    df = df.dropna(how="all")  # drop blank rows

    # Rename columns to match DB schema
    df = df.rename(columns={
        "Posting Date": "posting_date",
        "Description": "description",
        "Amount": "amount",
        "Type": "type",
        "Balance": "balance"
    })

    # Keep only the columns we care about
    df = df[["posting_date", "description", "amount", "type", "balance"]]

    # Assign categories
    df["category"] = df["description"].apply(categorize)

    # Insert into SQLite
    conn = sqlite3.connect(DB_FILE)
    df.to_sql("transactions", conn, if_exists="append", index=False)
    conn.close()

    return jsonify({"inserted": len(df)})

# --- Fetch all transactions ---
@app.route("/transactions", methods=["GET"])
def get_transactions():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM transactions ORDER BY posting_date DESC").fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

# --- Spending by category (pie chart) ---
@app.route("/summary", methods=["GET"])
def get_summary():
    start = request.args.get("start_date")
    end = request.args.get("end_date")

    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    query = """
        SELECT category, SUM(ABS(amount)) as total
        FROM transactions
        WHERE amount < 0
    """
    params = []
    if start:
        query += " AND posting_date >= ?"
        params.append(start)
    if end:
        query += " AND posting_date <= ?"
        params.append(end)

    query += " GROUP BY category ORDER BY total DESC"
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()

    return jsonify([dict(row) for row in rows])

# --- Total spending (big number) ---
@app.route("/total", methods=["GET"])
def get_total():
    start = request.args.get("start_date")
    end = request.args.get("end_date")

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    query = "SELECT SUM(amount) FROM transactions WHERE amount < 0"
    params = []
    if start:
        query += " AND posting_date >= ?"
        params.append(start)
    if end:
        query += " AND posting_date <= ?"
        params.append(end)

    c.execute(query, params)
    total = c.fetchone()[0] or 0
    conn.close()

    return jsonify({"total_spending": total})

# --- Spending over time (line chart) ---
@app.route("/timeline", methods=["GET"])
def get_timeline():
    start = request.args.get("start_date")
    end = request.args.get("end_date")

    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    query = """
        SELECT posting_date, SUM(ABS(amount)) as total
        FROM transactions
        WHERE amount < 0
    """
    params = []
    if start:
        query += " AND posting_date >= ?"
        params.append(start)
    if end:
        query += " AND posting_date <= ?"
        params.append(end)

    query += " GROUP BY posting_date ORDER BY posting_date ASC"
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()

    return jsonify([dict(row) for row in rows])

# --- Spending over time by category ---
@app.route("/timeline/<category>", methods=["GET"])
def get_timeline_by_category(category):
    start = request.args.get("start_date")
    end = request.args.get("end_date")

    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    query = """
        SELECT posting_date, SUM(ABS(amount)) as total
        FROM transactions
        WHERE category = ? AND amount < 0
    """
    params = [category]
    if start:
        query += " AND posting_date >= ?"
        params.append(start)
    if end:
        query += " AND posting_date <= ?"
        params.append(end)

    query += " GROUP BY posting_date ORDER BY posting_date ASC"
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()

    return jsonify([dict(row) for row in rows])

# --- Spending per category (bar chart) ---
@app.route("/categories/bar", methods=["GET"])
def get_category_bar():
    start = request.args.get("start_date")
    end = request.args.get("end_date")

    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    query = """
        SELECT category, SUM(amount) as total
        FROM transactions
        WHERE 1=1
    """
    params = []
    if start:
        query += " AND posting_date >= ?"
        params.append(start)
    if end:
        query += " AND posting_date <= ?"
        params.append(end)

    query += " GROUP BY category ORDER BY total DESC"
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()

    return jsonify([dict(row) for row in rows])

# --- Net income (positive amounts only) ---
@app.route("/income", methods=["GET"])
def get_income():
    start = request.args.get("start_date")
    end = request.args.get("end_date")

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    query = "SELECT SUM(amount) FROM transactions WHERE amount > 0"
    params = []
    if start:
        query += " AND posting_date >= ?"
        params.append(start)
    if end:
        query += " AND posting_date <= ?"
        params.append(end)

    c.execute(query, params)
    total = c.fetchone()[0] or 0
    conn.close()

    return jsonify({"net_income": total})


# --- Net balance (all amounts) ---
@app.route("/balance", methods=["GET"])
def get_balance():
    start = request.args.get("start_date")
    end = request.args.get("end_date")

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    query = "SELECT SUM(amount) FROM transactions WHERE 1=1"
    params = []
    if start:
        query += " AND posting_date >= ?"
        params.append(start)
    if end:
        query += " AND posting_date <= ?"
        params.append(end)

    c.execute(query, params)
    total = c.fetchone()[0] or 0
    conn.close()

    return jsonify({"net_balance": total})


# --- AI integration endpoints ---
@app.route("/ai/analyze", methods=["POST"])
def ai_analyze():
    """Accepts a CSV file upload or uses current DB transactions to build a short summary,
    then calls the LLM with a system prompt that frames the assistant as a financial advisor.
    Returns a session id and the assistant's initial analysis.
    """
    system_prompt = (
        "You are a professional financial advisor. You will be given a user's transaction CSV or a summary of transactions. "
        "Analyze spending patterns, flag unusual items, suggest categories, identify opportunities to save, and provide a concise action plan. "
        "Be empathetic and prioritize practical, achievable suggestions."
    )

    # If a CSV file is provided, read it and produce a small textual summary
    user_content = ""
    if "file" in request.files:
        try:
            df = pd.read_csv(request.files["file"])
            # Basic summarization: total spending, top merchants, recent big transactions
            total_spent = df[df["Amount"] < 0]["Amount"].abs().sum() if "Amount" in df.columns else None
            top = df["Description"].value_counts().head(5).to_dict() if "Description" in df.columns else {}
            user_content += f"CSV uploaded. Total spent (approx): {total_spent}\nTop merchants: {top}\n"
        except Exception as e:
            user_content += f"(Could not parse CSV) {str(e)}\n"
    else:
        # fallback: build a short summary from DB
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT category, SUM(ABS(amount)) as total FROM transactions WHERE amount < 0 GROUP BY category ORDER BY total DESC LIMIT 5")
        rows = c.fetchall()
        conn.close()
        summary = {r["category"]: r["total"] for r in rows}
        user_content += f"Recent spending by category: {summary}\n"

    assistant_text = call_gemini_system(system_prompt, user_content)
    # Ensure assistant_text is a plain string for JSON serialization
    if isinstance(assistant_text, (dict, list)):
        try:
            # try to extract common nested fields
            if isinstance(assistant_text, dict):
                if "content" in assistant_text and isinstance(assistant_text["content"], str):
                    assistant_text = assistant_text["content"]
                elif "output" in assistant_text and isinstance(assistant_text["output"], str):
                    assistant_text = assistant_text["output"]
                else:
                    assistant_text = str(assistant_text)
            else:
                assistant_text = str(assistant_text)
        except Exception:
            assistant_text = str(assistant_text)

    # create a session
    session_id = str(uuid.uuid4())
    AI_SESSIONS[session_id] = [
        {"role": "system", "content": system_prompt},
        {"role": "assistant", "content": assistant_text},
    ]

    return jsonify({"session_id": session_id, "assistant": assistant_text})


@app.route("/ai/chat", methods=["POST"])
def ai_chat():
    """Simple chat endpoint: accepts { session_id, message } and returns assistant reply.
    If session_id is not provided, returns error.
    """
    data = request.get_json() or {}
    session_id = data.get("session_id")
    message = data.get("message", "")
    if not session_id or session_id not in AI_SESSIONS:
        return jsonify({"error": "invalid session_id"}), 400

    # append user message
    AI_SESSIONS[session_id].append({"role": "user", "content": message})

    # create system prompt from session's first system message if present
    system_prompt = AI_SESSIONS[session_id][0].get("content", "You are a helpful assistant.")

    assistant_text = call_gemini_system(system_prompt, message)

    AI_SESSIONS[session_id].append({"role": "assistant", "content": assistant_text})

    return jsonify({"assistant": assistant_text})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
