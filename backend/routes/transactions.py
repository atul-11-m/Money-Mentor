from flask import Blueprint, jsonify, request
from db import get_conn

transactions_bp = Blueprint("transactions", __name__)


def _date_filter(query: str, start: str | None, end: str | None) -> tuple[str, list]:
    """Append optional posting_date range filters and return (query, params)."""
    params: list = []
    if start:
        query += " AND posting_date >= ?"
        params.append(start)
    if end:
        query += " AND posting_date <= ?"
        params.append(end)
    return query, params


@transactions_bp.route("/transactions", methods=["GET"])
def get_transactions():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM transactions ORDER BY posting_date DESC").fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])


@transactions_bp.route("/summary", methods=["GET"])
def get_summary():
    start, end = request.args.get("start_date"), request.args.get("end_date")
    query = "SELECT category, SUM(ABS(amount)) as total FROM transactions WHERE amount < 0"
    query, params = _date_filter(query, start, end)
    query += " GROUP BY category ORDER BY total DESC"
    conn = get_conn()
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])


@transactions_bp.route("/total", methods=["GET"])
def get_total():
    start, end = request.args.get("start_date"), request.args.get("end_date")
    query = "SELECT SUM(amount) as total FROM transactions WHERE amount < 0"
    query, params = _date_filter(query, start, end)
    conn = get_conn()
    total = conn.execute(query, params).fetchone()["total"] or 0
    conn.close()
    return jsonify({"total_spending": total})


@transactions_bp.route("/timeline", methods=["GET"])
def get_timeline():
    start, end = request.args.get("start_date"), request.args.get("end_date")
    query = "SELECT posting_date, SUM(ABS(amount)) as total FROM transactions WHERE amount < 0"
    query, params = _date_filter(query, start, end)
    query += " GROUP BY posting_date ORDER BY posting_date ASC"
    conn = get_conn()
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])


@transactions_bp.route("/timeline/<category>", methods=["GET"])
def get_timeline_by_category(category):
    start, end = request.args.get("start_date"), request.args.get("end_date")
    query = (
        "SELECT posting_date, SUM(ABS(amount)) as total FROM transactions "
        "WHERE category = ? AND amount < 0"
    )
    params = [category]
    query, extra = _date_filter(query, start, end)
    params += extra
    query += " GROUP BY posting_date ORDER BY posting_date ASC"
    conn = get_conn()
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])


@transactions_bp.route("/categories/bar", methods=["GET"])
def get_category_bar():
    start, end = request.args.get("start_date"), request.args.get("end_date")
    query = "SELECT category, SUM(amount) as total FROM transactions WHERE 1=1"
    query, params = _date_filter(query, start, end)
    query += " GROUP BY category ORDER BY total DESC"
    conn = get_conn()
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])


@transactions_bp.route("/income", methods=["GET"])
def get_income():
    start, end = request.args.get("start_date"), request.args.get("end_date")
    query = "SELECT SUM(amount) as total FROM transactions WHERE amount > 0"
    query, params = _date_filter(query, start, end)
    conn = get_conn()
    total = conn.execute(query, params).fetchone()["total"] or 0
    conn.close()
    return jsonify({"net_income": total})


@transactions_bp.route("/balance", methods=["GET"])
def get_balance():
    start, end = request.args.get("start_date"), request.args.get("end_date")
    query = "SELECT SUM(amount) as total FROM transactions WHERE 1=1"
    query, params = _date_filter(query, start, end)
    conn = get_conn()
    total = conn.execute(query, params).fetchone()["total"] or 0
    conn.close()
    return jsonify({"net_balance": total})
