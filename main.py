import os
from datetime import date
from decimal import Decimal
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from psycopg import connect
from psycopg.rows import dict_row

app = FastAPI(title="Accountant MVP")

def db():
    return connect(os.environ["DATABASE_URL"], row_factory=dict_row)

def init_db():
    with db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id SERIAL PRIMARY KEY,
                txn_date DATE NOT NULL DEFAULT CURRENT_DATE,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                txn_type TEXT NOT NULL CHECK (txn_type IN ('income','expense')),
                amount NUMERIC(12,2) NOT NULL CHECK (amount >= 0)
            );
            CREATE TABLE IF NOT EXISTS customers (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT
            );
            CREATE TABLE IF NOT EXISTS invoices (
                id SERIAL PRIMARY KEY,
                customer_name TEXT NOT NULL,
                issue_date DATE NOT NULL DEFAULT CURRENT_DATE,
                due_date DATE NOT NULL,
                status TEXT NOT NULL DEFAULT 'Unpaid',
                amount NUMERIC(12,2) NOT NULL CHECK (amount >= 0)
            );
            """)
            cur.execute("SELECT COUNT(*) AS c FROM transactions")
            if cur.fetchone()["c"] == 0:
                cur.executemany(
                    "INSERT INTO transactions (txn_date,description,category,txn_type,amount) VALUES (%s,%s,%s,%s,%s)",
                    [
                        (date.today(),"Consulting revenue","Sales","income",Decimal("25000")),
                        (date.today(),"Office rent","Operations","expense",Decimal("6500")),
                        (date.today(),"Software subscriptions","IT","expense",Decimal("1200")),
                        (date.today(),"Support contract","Services","income",Decimal("9800")),
                    ]
                )
            cur.execute("SELECT COUNT(*) AS c FROM customers")
            if cur.fetchone()["c"] == 0:
                cur.executemany(
                    "INSERT INTO customers (name,email,phone) VALUES (%s,%s,%s)",
                    [
                        ("Acme Trading","accounts@acme.example","+971 50 000 0001"),
                        ("Northstar LLC","finance@northstar.example","+971 50 000 0002"),
                        ("Blue Horizon","admin@bluehorizon.example","+971 50 000 0003"),
                    ]
                )
            cur.execute("SELECT COUNT(*) AS c FROM invoices")
            if cur.fetchone()["c"] == 0:
                cur.executemany(
                    "INSERT INTO invoices (customer_name,issue_date,due_date,status,amount) VALUES (%s,%s,%s,%s,%s)",
                    [
                        ("Acme Trading",date.today(),date.today(),"Paid",Decimal("12000")),
                        ("Northstar LLC",date.today(),date.today(),"Unpaid",Decimal("8500")),
                        ("Blue Horizon",date.today(),date.today(),"Unpaid",Decimal("6400")),
                    ]
                )
        conn.commit()

@app.on_event("startup")
def startup():
    init_db()

def money(v):
    return f"AED {Decimal(v or 0):,.2f}"

def page(title, body):
    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} - Accountant</title>
<style>
:root{{--bg:#f5f7fb;--card:#fff;--ink:#172033;--muted:#6b7280;--line:#e5e7eb;--brand:#1f4e79;--good:#198754;--bad:#c0392b}}
*{{box-sizing:border-box}} body{{margin:0;font-family:Inter,Arial,sans-serif;background:var(--bg);color:var(--ink)}}
header{{background:#0f2740;color:white;padding:18px 28px;display:flex;align-items:center;justify-content:space-between}}
header b{{font-size:20px}} nav a{{color:#dbeafe;text-decoration:none;margin-left:18px}}
main{{max-width:1180px;margin:28px auto;padding:0 18px}}
.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}} .card{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px;box-shadow:0 4px 18px rgba(15,39,64,.05)}}
.kpi{{font-size:26px;font-weight:700;margin-top:8px}} .muted{{color:var(--muted);font-size:13px}}
.good{{color:var(--good)}} .bad{{color:var(--bad)}} h1{{margin:0 0 18px}} h2{{font-size:18px;margin-top:0}}
table{{width:100%;border-collapse:collapse;background:white;border-radius:12px;overflow:hidden}} th,td{{padding:12px 14px;border-bottom:1px solid var(--line);text-align:left;font-size:14px}} th{{background:#eef3f8}}
form{{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin:14px 0 22px}} input,select,button{{padding:11px;border:1px solid #cfd6df;border-radius:9px}} button{{background:var(--brand);color:white;border:none;cursor:pointer}}
.section{{margin-top:24px}} .bar{{height:10px;background:#e7edf3;border-radius:10px;overflow:hidden}} .bar span{{display:block;height:100%;background:#5b8db8}}
@media(max-width:800px){{.grid{{grid-template-columns:1fr 1fr}} form{{grid-template-columns:1fr 1fr}} nav{{display:none}}}}
</style></head>
<body>
<header><b>Accountant MVP</b><nav><a href="/">Dashboard</a><a href="/transactions">Transactions</a><a href="/invoices">Invoices</a><a href="/customers">Customers</a></nav></header>
<main>{body}</main></body></html>"""

@app.get("/health")
def health():
    return {"status":"ok"}

@app.get("/", response_class=HTMLResponse)
def dashboard():
    with db() as conn, conn.cursor() as cur:
        cur.execute("SELECT COALESCE(SUM(CASE WHEN txn_type='income' THEN amount END),0) income, COALESCE(SUM(CASE WHEN txn_type='expense' THEN amount END),0) expense FROM transactions")
        s = cur.fetchone()
        cur.execute("SELECT COUNT(*) c FROM invoices WHERE status='Unpaid'")
        unpaid = cur.fetchone()["c"]
        cur.execute("SELECT COUNT(*) c FROM customers")
        customers = cur.fetchone()["c"]
        cur.execute("SELECT * FROM transactions ORDER BY id DESC LIMIT 6")
        tx = cur.fetchall()
    profit = Decimal(s["income"]) - Decimal(s["expense"])
    rows = "".join([f"<tr><td>{x['txn_date']}</td><td>{x['description']}</td><td>{x['category']}</td><td>{x['txn_type'].title()}</td><td>{money(x['amount'])}</td></tr>" for x in tx])
    body = f"""
    <h1>Financial Dashboard</h1>
    <div class="grid">
      <div class="card"><div class="muted">Total income</div><div class="kpi good">{money(s['income'])}</div></div>
      <div class="card"><div class="muted">Total expenses</div><div class="kpi bad">{money(s['expense'])}</div></div>
      <div class="card"><div class="muted">Net profit</div><div class="kpi">{money(profit)}</div></div>
      <div class="card"><div class="muted">Customers / unpaid invoices</div><div class="kpi">{customers} / {unpaid}</div></div>
    </div>
    <div class="section card"><h2>Recent transactions</h2><table><tr><th>Date</th><th>Description</th><th>Category</th><th>Type</th><th>Amount</th></tr>{rows}</table></div>
    """
    return page("Dashboard", body)

@app.get("/transactions", response_class=HTMLResponse)
def transactions():
    with db() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM transactions ORDER BY id DESC")
        items = cur.fetchall()
    rows = "".join([f"<tr><td>{x['txn_date']}</td><td>{x['description']}</td><td>{x['category']}</td><td>{x['txn_type'].title()}</td><td>{money(x['amount'])}</td></tr>" for x in items])
    body = f"""<h1>Transactions</h1>
    <div class="card"><form method="post">
    <input name="txn_date" type="date" required><input name="description" placeholder="Description" required>
    <input name="category" placeholder="Category" required><select name="txn_type"><option value="income">Income</option><option value="expense">Expense</option></select>
    <input name="amount" type="number" step="0.01" min="0" placeholder="Amount" required><button>Add transaction</button>
    </form>
    <table><tr><th>Date</th><th>Description</th><th>Category</th><th>Type</th><th>Amount</th></tr>{rows}</table></div>"""
    return page("Transactions", body)

@app.post("/transactions")
def add_transaction(txn_date: str = Form(...), description: str = Form(...), category: str = Form(...), txn_type: str = Form(...), amount: Decimal = Form(...)):
    with db() as conn, conn.cursor() as cur:
        cur.execute("INSERT INTO transactions (txn_date,description,category,txn_type,amount) VALUES (%s,%s,%s,%s,%s)", (txn_date,description,category,txn_type,amount))
        conn.commit()
    return RedirectResponse("/transactions", status_code=303)

@app.get("/customers", response_class=HTMLResponse)
def customers():
    with db() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM customers ORDER BY id DESC")
        items = cur.fetchall()
    rows = "".join([f"<tr><td>{x['name']}</td><td>{x['email'] or ''}</td><td>{x['phone'] or ''}</td></tr>" for x in items])
    body = f"""<h1>Customers</h1><div class="card"><form method="post" style="grid-template-columns:2fr 2fr 2fr 1fr">
    <input name="name" placeholder="Customer name" required><input name="email" type="email" placeholder="Email"><input name="phone" placeholder="Phone"><button>Add customer</button></form>
    <table><tr><th>Name</th><th>Email</th><th>Phone</th></tr>{rows}</table></div>"""
    return page("Customers", body)

@app.post("/customers")
def add_customer(name: str = Form(...), email: str = Form(""), phone: str = Form("")):
    with db() as conn, conn.cursor() as cur:
        cur.execute("INSERT INTO customers (name,email,phone) VALUES (%s,%s,%s)", (name,email,phone))
        conn.commit()
    return RedirectResponse("/customers", status_code=303)

@app.get("/invoices", response_class=HTMLResponse)
def invoices():
    with db() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM invoices ORDER BY id DESC")
        items = cur.fetchall()
    rows = "".join([f"<tr><td>INV-{x['id']:04d}</td><td>{x['customer_name']}</td><td>{x['issue_date']}</td><td>{x['due_date']}</td><td>{x['status']}</td><td>{money(x['amount'])}</td></tr>" for x in items])
    body = f"""<h1>Invoices</h1><div class="card"><form method="post" style="grid-template-columns:2fr 1fr 1fr 1fr 1fr">
    <input name="customer_name" placeholder="Customer" required><input name="issue_date" type="date" required><input name="due_date" type="date" required>
    <select name="status"><option>Unpaid</option><option>Paid</option></select><input name="amount" type="number" step="0.01" min="0" placeholder="Amount" required><button>Create invoice</button></form>
    <table><tr><th>Invoice</th><th>Customer</th><th>Issue</th><th>Due</th><th>Status</th><th>Amount</th></tr>{rows}</table></div>"""
    return page("Invoices", body)

@app.post("/invoices")
def add_invoice(customer_name: str = Form(...), issue_date: str = Form(...), due_date: str = Form(...), status: str = Form(...), amount: Decimal = Form(...)):
    with db() as conn, conn.cursor() as cur:
        cur.execute("INSERT INTO invoices (customer_name,issue_date,due_date,status,amount) VALUES (%s,%s,%s,%s,%s)", (customer_name,issue_date,due_date,status,amount))
        conn.commit()
    return RedirectResponse("/invoices", status_code=303)
