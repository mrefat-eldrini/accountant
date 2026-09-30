#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
EMAIL="${SMOKE_EMAIL:-admin@accountant.local}"
PASSWORD="${SMOKE_PASSWORD:-Admin123!}"

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT
admin_cookies="$tmpdir/admin.cookies"
viewer_cookies="$tmpdir/viewer.cookies"
page="$tmpdir/page.html"
backup="$tmpdir/backup.json"

echo "Smoke testing: $BASE_URL"

health="$(curl -fsS "$BASE_URL/health")"
echo "$health" | grep -q '"status":"ok"'
curl -fsS "$BASE_URL/login" | grep -q "Sign in"

status="$(curl -sS -o /dev/null -w '%{http_code}' "$BASE_URL/")"
test "$status" = "303" || test "$status" = "307"

curl -fsS -c "$admin_cookies" -b "$admin_cookies"   -X POST "$BASE_URL/login"   -H 'Content-Type: application/x-www-form-urlencoded'   --data-urlencode "email=$EMAIL"   --data-urlencode "password=$PASSWORD"   -o /dev/null

for path in / /transactions /invoices /expenses /customers /vendors /accounts /journal /reports /users /audit /backup /system /settings; do
  code="$(curl -sS -o "$page" -w '%{http_code}' -b "$admin_cookies" "$BASE_URL$path")"
  test "$code" = "200" || { echo "FAILED $path -> HTTP $code"; cat "$page"; exit 1; }
  echo "PASS admin $path"
done

curl -fsS -b "$admin_cookies" "$BASE_URL/" -o "$page"
grep -q "Users" "$page"
grep -q "Audit Log" "$page"
grep -q "Backup & Restore" "$page"
grep -q "System Status" "$page"
grep -q "Settings" "$page"
echo "PASS admin navigation"

curl -fsS -b "$admin_cookies" "$BASE_URL/backup/download" -o "$backup"
grep -q '"product": "Accountant Pro"' "$backup"
grep -q '"users"' "$backup"
grep -q '"transactions"' "$backup"
echo "PASS backup creation"

restore_code="$(curl -sS -o /dev/null -w '%{http_code}' -b "$admin_cookies"   -F "backup_file=@$backup;type=application/json"   -F "confirm=RESTORE"   "$BASE_URL/backup/restore")"
test "$restore_code" = "303"
echo "PASS backup restore"

viewer_email="viewer-smoke@accountant.local"
curl -sS -o /dev/null -b "$admin_cookies"   -X POST "$BASE_URL/users"   -H 'Content-Type: application/x-www-form-urlencoded'   --data-urlencode "name=Viewer Smoke"   --data-urlencode "email=$viewer_email"   --data-urlencode "password=Viewer123!"   --data-urlencode "role=Viewer"

curl -fsS -c "$viewer_cookies" -b "$viewer_cookies"   -X POST "$BASE_URL/login"   -H 'Content-Type: application/x-www-form-urlencoded'   --data-urlencode "email=$viewer_email"   --data-urlencode "password=Viewer123!"   -o /dev/null

curl -fsS -b "$viewer_cookies" "$BASE_URL/" -o "$page"
if grep -q "ADMINISTRATION" "$page"; then
  echo "FAILED viewer can see Administration"
  exit 1
fi

for path in /users /audit /backup /system /settings; do
  code="$(curl -sS -o /dev/null -w '%{http_code}' -b "$viewer_cookies" "$BASE_URL$path")"
  test "$code" = "303" || { echo "FAILED viewer restriction $path -> $code"; exit 1; }
done

viewer_post="$(curl -sS -o /dev/null -w '%{http_code}' -b "$viewer_cookies"   -X POST "$BASE_URL/transactions"   -H 'Content-Type: application/x-www-form-urlencoded'   --data-urlencode "txn_date=2026-09-30"   --data-urlencode "description=Viewer must not create"   --data-urlencode "category=Test"   --data-urlencode "txn_type=expense"   --data-urlencode "account_code=5000"   --data-urlencode "amount=1"   --data-urlencode "tax=0")"
test "$viewer_post" = "303"
echo "PASS viewer read-only permissions"

curl -fsS -b "$admin_cookies" "$BASE_URL/audit" -o "$page"
grep -q "RESTORE_BACKUP" "$page"
grep -q "CREATE_USER" "$page"
echo "PASS audit trail"

echo "All v0.4.0 smoke tests passed."
