# MoneyMentor

A full-stack personal finance dashboard. Upload a CSV bank statement to get
instant, interactive spending visualizations, and chat with a GPT-powered
financial advisor that answers questions grounded in your actual transactions.

**Stack:** React (TypeScript) · Vite · Tailwind CSS · Recharts · Flask · SQLite · GPT

---

## Features

- **CSV bank-statement ingestion** — upload a statement; columns are mapped to a
  canonical schema (handling either a single signed `amount` or separate
  `debit`/`credit` columns), dates are normalized, and duplicate rows are skipped.
- **Rule-based transaction categorization** — each transaction is tagged
  (Dining, Groceries, Subscriptions, Transportation, Purchases, Necessities,
  Transfers, Income, Cash, Refunds) via keyword rules — no API key required.
- **Interactive visualizations (Tailwind + Recharts)** — monthly spending line
  chart, category pie, spending-per-category bar chart, and a per-category
  timeline, laid out in a responsive Tailwind dashboard.
- **RESTful API** — 10+ endpoints for spending summaries, category breakdowns,
  income tracking, net balances, and time-series, all with optional date-range
  filtering.
- **GPT-powered advisor chatbot** — multi-turn chat seeded with a summary of your
  data, plus dynamic text-to-SQL: the model writes a safe read-only `SELECT`,
  the backend executes it, and the results ground the answer in live data. Works
  with any OpenAI-compatible endpoint.


### Backend (Flask + SQLite)

cd backend \
python -m venv venv && source venv/bin/activate \
pip install -r requirements.txt \
python app.py   \

The SQLite database (`finance.db`) is created automatically on first run.

To enable the GPT advisor, create `backend/.env`:


OPENAI_API_KEY=sk-... \
OPENAI_API_URL=https://api.openai.com/v1/chat/completions \
OPENAI_MODEL=gpt-5.4  \


Without a key the dashboard and all data endpoints still work; only the AI chat
is disabled (it returns a friendly placeholder).

### Frontend (React + Vite)

cd frontend/finance-dashboard
npm install
npm run dev                                       

The frontend calls the backend at `http://localhost:5001`.
