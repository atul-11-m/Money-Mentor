import uuid

import pandas as pd
import requests
from flask import Blueprint, jsonify, request

from config import OPENAI_API_KEY, OPENAI_API_URL, OPENAI_MODEL
from db import get_conn
from llm import (
    build_db_context,
    call_llm,
    categorize_batch,
    generate_sql_for_question,
    normalize_csv_columns,
    run_sql_query,
)
from session_store import session_append, session_get, session_set

upload_bp = Blueprint("upload", __name__)
ai_bp = Blueprint("ai", __name__, url_prefix="/ai")

ADVISOR_SYSTEM_PROMPT = (
    "You are MoneyMentor, a professional and empathetic financial advisor. "
    "You have been given a summary of the user's actual transaction data from their uploaded bank statements. "
    "Your job is to analyze their spending patterns, flag unusual items, identify savings opportunities, "
    "and answer any follow-up questions they have. Be concise, practical, and encouraging."
)


def _normalize_dates(series: pd.Series) -> pd.Series:
    """Convert a date column to ISO YYYY-MM-DD; leave unparseable values as-is."""
    parsed = pd.to_datetime(series, errors="coerce")
    iso = parsed.dt.strftime("%Y-%m-%d")
    return iso.fillna(series.astype(str))


# ---------------------------------------------------------------------------
# CSV upload — rule-based column mapping + categorization
# ---------------------------------------------------------------------------
@upload_bp.route("/upload", methods=["POST"])
def upload_csv():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    df = pd.read_csv(file)
    df = df.dropna(how="all")

    try:
        df = normalize_csv_columns(df)
    except Exception as e:
        return jsonify({"error": f"Could not normalize CSV columns: {e}"}), 400

    available = [c for c in ["posting_date", "description", "amount", "type", "balance"] if c in df.columns]
    df = df[available]
    df["posting_date"] = _normalize_dates(df["posting_date"])

    category_map = categorize_batch(df["description"].tolist())
    df["category"] = df["description"].map(category_map)

    conn = get_conn()
    c = conn.cursor()
    inserted = skipped = 0
    for _, row in df.iterrows():
        try:
            c.execute(
                """INSERT OR IGNORE INTO transactions
                   (posting_date, description, amount, type, balance, category)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    row.get("posting_date"), row.get("description"), row.get("amount"),
                    row.get("type"), row.get("balance"), row.get("category"),
                ),
            )
            if c.rowcount == 1:
                inserted += 1
            else:
                skipped += 1
        except Exception:
            skipped += 1
    conn.commit()
    conn.close()

    return jsonify({"inserted": inserted, "skipped": skipped})


# ---------------------------------------------------------------------------
# AI — start a session seeded with a summary of the user's data
# ---------------------------------------------------------------------------
@ai_bp.route("/start", methods=["POST"])
def ai_start():
    db_context = build_db_context()
    user_content = f"Here is my financial data:\n{db_context}\n\nPlease give me an initial analysis."
    assistant_text = call_llm(ADVISOR_SYSTEM_PROMPT, user_content)

    session_id = str(uuid.uuid4())
    session_set(session_id, [
        {"role": "system", "content": ADVISOR_SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
        {"role": "assistant", "content": assistant_text},
    ])
    return jsonify({"session_id": session_id, "assistant": assistant_text})


# ---------------------------------------------------------------------------
# AI — multi-turn chat with dynamic SQL retrieval
# ---------------------------------------------------------------------------
@ai_bp.route("/chat", methods=["POST"])
def ai_chat():
    body = request.get_json() or {}
    session_id = body.get("session_id")
    message = body.get("message", "")

    if not session_id or session_get(session_id) is None:
        return jsonify({"error": "invalid session_id"}), 400

    # Step 1: generate and run a SQL query tailored to this question.
    sql = generate_sql_for_question(message)
    query_results_text = run_sql_query(sql) if sql else None
    if sql:
        print(f"[ai/chat] SQL: {sql}")
        print(f"[ai/chat] Results (preview): {(query_results_text or '')[:300]}")

    # Step 2: augment the user message with live DB data.
    augmented = message
    if query_results_text:
        augmented = (
            f"{message}\n\n"
            f"[Live data retrieved from the database]\n"
            f"SQL used: {sql}\n"
            f"Results:\n{query_results_text}"
        )

    session_append(session_id, {"role": "user", "content": augmented})

    # Step 3: answer using the full conversation history.
    messages = session_get(session_id) or []
    system_prompt = (
        messages[0]["content"]
        if messages and messages[0].get("role") == "system"
        else "You are a helpful assistant."
    )
    convo = messages[1:] if messages and messages[0].get("role") == "system" else messages

    assistant_text = _chat_completion(system_prompt, convo, fallback_input=augmented)
    session_append(session_id, {"role": "assistant", "content": assistant_text})

    return jsonify({"assistant": assistant_text, "sql": sql})


def _chat_completion(system_prompt: str, convo: list, fallback_input: str) -> str:
    """Send a multi-turn request to the GPT endpoint; fall back to call_llm on error."""
    if not OPENAI_API_KEY or not OPENAI_API_URL:
        return call_llm(system_prompt, fallback_input)
    try:
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": OPENAI_MODEL,
            "messages": [{"role": "system", "content": system_prompt}] + convo,
            "temperature": 0.2,
        }
        r = requests.post(OPENAI_API_URL, json=payload, headers=headers, timeout=30)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        return call_llm(system_prompt, fallback_input)
