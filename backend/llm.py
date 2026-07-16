"""
llm.py — data ingestion helpers + GPT advisor logic.

Rule-based (no API key required):
  - categorize / categorize_batch : keyword-rule transaction categorization
  - normalize_csv_columns         : map arbitrary bank-CSV headers to the schema

GPT-powered (OpenAI-compatible endpoint):
  - call_llm                  : generic single-turn chat completion
  - build_db_context          : build a text summary of the user's data for the AI
  - generate_sql_for_question : ask the model for a targeted read-only SELECT
  - run_sql_query             : safely execute a SELECT and format the results
"""

import pandas as pd
import requests

from config import OPENAI_API_KEY, OPENAI_API_URL, OPENAI_MODEL
from db import get_conn

# ---------------------------------------------------------------------------
# DB schema description (shared with the SQL-generation prompt)
# ---------------------------------------------------------------------------
DB_SCHEMA = """
Table: transactions
Columns:
  id           INTEGER  (primary key)
  posting_date TEXT     (format: YYYY-MM-DD or MM/DD/YYYY)
  description  TEXT     (merchant / transaction name)
  amount       REAL     (negative = expense, positive = income)
  type         TEXT     (transaction type, may be NULL)
  balance      REAL     (running balance, may be NULL)
  category     TEXT     (one of: Dining, Groceries, Subscriptions, Transportation,
                          Purchases, Necessities, Transfers, Income, Cash, Refunds, Uncategorized)
"""

# ---------------------------------------------------------------------------
# Rule-based transaction categorization
# ---------------------------------------------------------------------------
# Ordered keyword -> category rules. The first keyword found in a (lowercased)
# description wins, so more specific merchants should come before generic terms.
CATEGORY_RULES: list[tuple[str, str]] = [
    # Dining
    ("starbucks", "Dining"), ("mcdonald", "Dining"), ("chipotle", "Dining"),
    ("doordash", "Dining"), ("uber eats", "Dining"), ("grubhub", "Dining"),
    ("restaurant", "Dining"), ("coffee", "Dining"), ("cafe", "Dining"),
    ("pizza", "Dining"), ("taco", "Dining"),
    # Groceries
    ("kroger", "Groceries"), ("whole foods", "Groceries"), ("trader joe", "Groceries"),
    ("safeway", "Groceries"), ("aldi", "Groceries"), ("grocery", "Groceries"),
    ("supermarket", "Groceries"),
    # Subscriptions
    ("spotify", "Subscriptions"), ("netflix", "Subscriptions"), ("hulu", "Subscriptions"),
    ("disney+", "Subscriptions"), ("prime video", "Subscriptions"), ("youtube premium", "Subscriptions"),
    ("icloud", "Subscriptions"), ("subscription", "Subscriptions"),
    # Transportation
    ("uber", "Transportation"), ("lyft", "Transportation"), ("shell", "Transportation"),
    ("chevron", "Transportation"), ("exxon", "Transportation"), ("bp ", "Transportation"),
    ("gas", "Transportation"), ("fuel", "Transportation"), ("parking", "Transportation"),
    ("transit", "Transportation"),
    # Purchases
    ("amazon", "Purchases"), ("target", "Purchases"), ("walmart", "Purchases"),
    ("best buy", "Purchases"), ("walgreens", "Purchases"), ("cvs", "Purchases"),
    ("etsy", "Purchases"), ("ebay", "Purchases"),
    # Necessities (bills / utilities / housing)
    ("rent", "Necessities"), ("mortgage", "Necessities"), ("electric", "Necessities"),
    ("water bill", "Necessities"), ("utility", "Necessities"), ("insurance", "Necessities"),
    ("comcast", "Necessities"), ("verizon", "Necessities"), ("at&t", "Necessities"),
    ("t-mobile", "Necessities"), ("phone", "Necessities"),
    # Transfers
    ("paypal", "Transfers"), ("venmo", "Transfers"), ("zelle", "Transfers"),
    ("cash app", "Transfers"), ("transfer", "Transfers"), ("wire", "Transfers"),
    # Income
    ("direct deposit", "Income"), ("payroll", "Income"), ("paycheck", "Income"),
    ("deposit", "Income"), ("interest", "Income"),
    # Cash
    ("atm", "Cash"), ("cash withdrawal", "Cash"),
    # Refunds
    ("refund", "Refunds"), ("reversal", "Refunds"), ("return", "Refunds"),
]


def categorize(description: str) -> str:
    """Assign a category to a single transaction description using keyword rules."""
    if not description:
        return "Uncategorized"
    text = str(description).lower()
    for keyword, category in CATEGORY_RULES:
        if keyword in text:
            return category
    return "Uncategorized"


def categorize_batch(descriptions: list[str]) -> dict[str, str]:
    """Categorize a list of descriptions. Returns {description: category}."""
    return {d: categorize(d) for d in descriptions}


# ---------------------------------------------------------------------------
# Rule-based CSV column normalization
# ---------------------------------------------------------------------------
# Known header aliases (compared case-insensitively) -> canonical schema field.
COLUMN_ALIASES: dict[str, str] = {
    "posting date": "posting_date", "post date": "posting_date", "date": "posting_date",
    "transaction date": "posting_date", "trans date": "posting_date", "posting_date": "posting_date",
    "description": "description", "desc": "description", "merchant": "description",
    "name": "description", "memo": "description", "payee": "description",
    "transaction description": "description",
    "amount": "amount", "transaction amount": "amount", "amt": "amount",
    "debit": "debit", "withdrawal": "debit", "withdrawals": "debit",
    "credit": "credit", "deposit": "credit", "deposits": "credit",
    "type": "type", "transaction type": "type",
    "balance": "balance", "running balance": "balance", "current balance": "balance",
}


def normalize_csv_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Map an arbitrary bank CSV's columns to the canonical schema.

    Handles a single signed ``amount`` column or separate ``debit``/``credit``
    columns (which are merged into a signed ``amount``). Raises ValueError if the
    required fields (posting_date, description, amount) can't be resolved.
    """
    rename_map: dict[str, str] = {}
    used_targets: set[str] = set()
    for col in df.columns:
        target = COLUMN_ALIASES.get(str(col).strip().lower())
        if target and target not in used_targets:
            rename_map[col] = target
            used_targets.add(target)

    df = df.rename(columns=rename_map)

    # Merge debit/credit into a single signed amount column (credits +, debits -).
    if "amount" not in df.columns and ("debit" in df.columns or "credit" in df.columns):
        debit = pd.to_numeric(df.get("debit", 0), errors="coerce").fillna(0)
        credit = pd.to_numeric(df.get("credit", 0), errors="coerce").fillna(0)
        df["amount"] = credit - debit
        df = df.drop(columns=[c for c in ("debit", "credit") if c in df.columns])

    missing = [f for f in ("posting_date", "description", "amount") if f not in df.columns]
    if missing:
        raise ValueError(
            f"Could not match required columns {missing}. "
            f"Recognized headers: {sorted(set(COLUMN_ALIASES))}"
        )
    return df


# ---------------------------------------------------------------------------
# Generic GPT call (OpenAI-compatible endpoint)
# ---------------------------------------------------------------------------
def call_llm(system_prompt: str, user_input: str) -> str:
    """Call the configured OpenAI-compatible chat endpoint and return the reply text.

    Returns a graceful placeholder if no API key is configured, so the rest of the
    app keeps working without GPT.
    """
    if not OPENAI_API_KEY or not OPENAI_API_URL:
        return (
            "(No GPT API configured — set OPENAI_API_KEY to enable the advisor.) "
            "Based on your data, I would analyze spending patterns and suggest savings."
        )

    try:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": OPENAI_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ],
            "temperature": 0.2,
        }
        r = requests.post(OPENAI_API_URL, json=payload, headers=headers, timeout=30)
        r.raise_for_status()
        data = r.json()

        if isinstance(data, dict):
            if data.get("choices"):
                choice = data["choices"][0]
                if isinstance(choice, dict):
                    msg = (choice.get("message") or {}).get("content") if choice.get("message") else choice.get("text")
                    if isinstance(msg, str):
                        return msg.strip()
            if isinstance(data.get("output"), str):
                return data["output"]
            if isinstance(data.get("message"), str):
                return data["message"]
        return str(data)
    except Exception as e:
        return f"(GPT call failed) {e}"


# ---------------------------------------------------------------------------
# DB context builder (for AI session initialization)
# ---------------------------------------------------------------------------
def build_db_context() -> str:
    """Build a rich textual summary of the user's transactions from the DB."""
    conn = get_conn()
    c = conn.cursor()

    c.execute(
        "SELECT SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) as spent, "
        "SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as income, "
        "COUNT(*) as tx_count, MIN(posting_date) as first_date, MAX(posting_date) as last_date "
        "FROM transactions"
    )
    row = dict(c.fetchone())

    c.execute(
        "SELECT category, SUM(ABS(amount)) as total, COUNT(*) as count FROM transactions "
        "WHERE amount < 0 GROUP BY category ORDER BY total DESC LIMIT 10"
    )
    top_cats = [
        f"  {r['category']}: ${round(r['total'], 2)} ({r['count']} transactions)"
        for r in c.fetchall()
    ]

    c.execute(
        "SELECT description, category, SUM(ABS(amount)) as total, COUNT(*) as count "
        "FROM transactions WHERE amount < 0 "
        "GROUP BY description ORDER BY total DESC LIMIT 20"
    )
    top_merchants = [
        f"  {r['description']} [{r['category']}]: ${round(r['total'], 2)} x{r['count']}"
        for r in c.fetchall()
    ]

    c.execute(
        "SELECT posting_date, description, category, amount FROM transactions "
        "WHERE amount < 0 ORDER BY amount ASC LIMIT 10"
    )
    big_expenses = [
        f"  {r['posting_date']}  {r['description']} [{r['category']}]  ${abs(r['amount']):.2f}"
        for r in c.fetchall()
    ]

    c.execute(
        "SELECT strftime('%Y-%m', posting_date) as month, "
        "SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) as spent "
        "FROM transactions GROUP BY month ORDER BY month DESC LIMIT 6"
    )
    monthly = [f"  {r['month']}: ${round(r['spent'], 2)}" for r in c.fetchall()]

    c.execute(
        "SELECT posting_date, description, category, amount FROM transactions "
        "ORDER BY posting_date DESC LIMIT 30"
    )
    recent = [
        f"  {r['posting_date']}  {r['description']} [{r['category']}]  "
        f"{'-' if r['amount'] < 0 else '+'}${abs(r['amount']):.2f}"
        for r in c.fetchall()
    ]

    conn.close()

    sections = [
        "=== Overview ===",
        f"Period: {row.get('first_date')} -> {row.get('last_date')}  |  {row.get('tx_count')} transactions",
        f"Total spent: ${round(row.get('spent') or 0, 2)}  |  Total income: ${round(row.get('income') or 0, 2)}",
        "",
        "=== Spending by Category ===",
        *top_cats,
        "",
        "=== Top Merchants ===",
        *top_merchants,
        "",
        "=== 10 Biggest Expenses ===",
        *big_expenses,
        "",
        "=== Monthly Totals ===",
        *monthly,
        "",
        "=== 30 Most Recent Transactions ===",
        *recent,
    ]
    return "\n".join(sections)


# ---------------------------------------------------------------------------
# Dynamic SQL generation + execution (grounds chat answers in live data)
# ---------------------------------------------------------------------------
def generate_sql_for_question(user_question: str) -> str | None:
    """Ask the model for a safe read-only SELECT for the user's question.

    Returns the SQL string, or None if no query is needed / GPT is unavailable.
    """
    if not OPENAI_API_KEY or not OPENAI_API_URL:
        return None

    system_prompt = (
        "You are a SQL expert. The user has a personal finance SQLite database with the following schema:\n"
        f"{DB_SCHEMA}\n"
        "Given the user's question, write a single safe SELECT query that retrieves the data needed to answer it.\n"
        "Rules:\n"
        "- Only write SELECT statements. Never use INSERT, UPDATE, DELETE, DROP, or any DDL.\n"
        "- Use ABS(amount) when computing spending totals (amounts are negative for expenses).\n"
        "- Use WHERE amount < 0 to filter expenses; WHERE amount > 0 for income.\n"
        "- Search descriptions case-insensitively with LOWER(description) LIKE '%keyword%'.\n"
        "- The 'category' column holds values like: Dining, Groceries, Subscriptions, Transportation,\n"
        "  Purchases, Necessities, Transfers, Income, Cash, Refunds, Uncategorized.\n"
        "- Limit results to at most 50 rows unless the user asks for more.\n"
        "- If the question is general advice (not data-specific), respond with exactly: NO_QUERY\n"
        "- Respond with ONLY the raw SQL or NO_QUERY. No markdown, no explanation.\n"
        "Examples:\n"
        "  Q: How much did I spend on coffee?\n"
        "  A: SELECT description, posting_date, ABS(amount) as spent FROM transactions WHERE amount < 0 AND (LOWER(description) LIKE '%coffee%' OR LOWER(description) LIKE '%starbucks%') ORDER BY posting_date DESC LIMIT 50;\n"
        "  Q: What are all my Dining transactions?\n"
        "  A: SELECT posting_date, description, ABS(amount) as spent FROM transactions WHERE category = 'Dining' AND amount < 0 ORDER BY posting_date DESC LIMIT 50;\n"
        "  Q: Which merchants do I spend the most on?\n"
        "  A: SELECT description, category, SUM(ABS(amount)) as total, COUNT(*) as count FROM transactions WHERE amount < 0 GROUP BY description ORDER BY total DESC LIMIT 20;\n"
    )
    try:
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": OPENAI_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_question},
            ],
            "temperature": 0,
        }
        r = requests.post(OPENAI_API_URL, json=payload, headers=headers, timeout=20)
        r.raise_for_status()
        sql = r.json()["choices"][0]["message"]["content"].strip()

        # Strip markdown fences if the model included them.
        if sql.startswith("```"):
            sql = "\n".join(
                line for line in sql.splitlines() if not line.strip().startswith("```")
            ).strip()

        if sql.upper() == "NO_QUERY" or not sql.upper().startswith("SELECT"):
            return None
        return sql
    except Exception as e:
        print(f"[generate_sql_for_question] failed: {e}")
        return None


def run_sql_query(sql: str) -> str:
    """Execute a read-only SELECT and return a human-readable table of results."""
    if not sql or not sql.strip().upper().startswith("SELECT"):
        return "(Query blocked: only SELECT statements are allowed)"
    try:
        conn = get_conn()
        c = conn.cursor()
        c.execute(sql)
        rows = [dict(r) for r in c.fetchall()]
        conn.close()

        if not rows:
            return "Query returned no results."

        col_names = list(rows[0].keys())
        header = " | ".join(col_names)
        lines = [header, "-" * max(len(header), 10)]
        for row in rows[:50]:
            lines.append(" | ".join(str(row.get(h, "")) for h in col_names))
        return "\n".join(lines)
    except Exception as e:
        return f"(Query execution error: {e})"
