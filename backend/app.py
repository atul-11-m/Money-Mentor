from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import pandas as pd

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

if __name__ == "__main__":
    app.run(debug=True, port=5000)
