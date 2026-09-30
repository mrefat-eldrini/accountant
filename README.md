# Accountant MVP

A lightweight accounting dashboard built with FastAPI and PostgreSQL.

## Features
- Dashboard with income, expenses, profit, customer count, and unpaid invoices
- Transactions
- Customers
- Invoices
- Seed data in AED
- Render-ready health endpoint

## Run locally
```bash
export DATABASE_URL=postgresql://...
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```
