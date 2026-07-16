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

## Project structure

```
backend/
  app.py               Flask app + blueprint registration
  config.py            env-driven config (DB path, GPT keys)
  db.py                SQLite connection + schema init
  session_store.py     in-memory chat session store
  llm.py               rule-based categorization/normalization + GPT helpers
  routes/
    transactions.py    dashboard/data endpoints
    ai.py              CSV upload + AI chat endpoints
  data/                sample Chase CSV
frontend/finance-dashboard/
  src/                 React + TypeScript + Tailwind dashboard
```

## Running locally

### Backend (Flask + SQLite)

```bash
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py                                      # serves http://localhost:5001
```

The SQLite database (`finance.db`) is created automatically on first run.

To enable the GPT advisor, create `backend/.env`:

```
OPENAI_API_KEY=sk-...
OPENAI_API_URL=https://api.openai.com/v1/chat/completions
OPENAI_MODEL=gpt-4o-mini
```

Without a key the dashboard and all data endpoints still work; only the AI chat
is disabled (it returns a friendly placeholder).

### Frontend (React + Vite)

```bash
cd frontend/finance-dashboard
npm install
npm run dev                                        # serves http://localhost:5173
```

The frontend calls the backend at `http://localhost:5001`.

## API endpoints

| Method | Path                     | Purpose                                  |
| ------ | ------------------------ | ---------------------------------------- |
| GET    | `/transactions`          | all transactions                         |
| GET    | `/summary`               | spending totals by category              |
| GET    | `/total`                 | total spending                           |
| GET    | `/income`                | total income                             |
| GET    | `/balance`               | net balance                              |
| GET    | `/timeline`              | spending over time                       |
| GET    | `/timeline/<category>`   | spending over time for one category      |
| GET    | `/categories/bar`        | net amount per category                  |
| POST   | `/upload`                | upload + categorize a CSV                |
| POST   | `/ai/start`              | start an AI session seeded with your data|
| POST   | `/ai/chat`               | multi-turn chat with text-to-SQL         |

Data endpoints accept optional `?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`.
