# Accountant Pro

FastAPI accounting demonstration with a bilingual sales workspace.

Production: https://accountant-b7hw.onrender.com/sales

## Features
- Executive dashboard, transactions, customers, suppliers, and invoices
- Itemized quotations, cash/credit sales, conversion, payments, and partial returns
- Pending-refund confirmation, customer statements, sales reports, CSV export, and printable documents
- Local user profiles, Admin/Accountant/Viewer roles, audit logs, and full backup/restore
- Arabic/English, RTL/LTR, and dark/light themes

## Run
```bash
pip install -r requirements.txt
# Optional: set DATABASE_URL to a PostgreSQL connection string.
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Without DATABASE_URL the app uses SQLite. On free Render web services this database is ephemeral. The public service is a demo; use durable database storage and configure authentication/session secrets before storing real business data. It does not provide Saudi e-invoicing integration.

## Test
```bash
pip install pytest httpx
python -m pytest tests -q
```
