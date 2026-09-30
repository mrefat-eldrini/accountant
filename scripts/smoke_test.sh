#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
EMAIL="${SMOKE_EMAIL:-admin@accountant.local}"
PASSWORD="${SMOKE_PASSWORD:-Admin123!}"

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT
cookies="$tmpdir/cookies.txt"

echo "Smoke testing: $BASE_URL"

health="$(curl -fsS "$BASE_URL/health")"
echo "$health" | grep -q '"status":"ok"'

curl -fsS "$BASE_URL/login" | grep -q "Sign in"

status="$(curl -sS -o /dev/null -w '%{http_code}' "$BASE_URL/")"
test "$status" = "303" || test "$status" = "307"

curl -fsS -c "$cookies" -b "$cookies"   -X POST "$BASE_URL/login"   -H 'Content-Type: application/x-www-form-urlencoded'   --data-urlencode "email=$EMAIL"   --data-urlencode "password=$PASSWORD"   -o /dev/null

for path in / /transactions /invoices /expenses /customers /vendors /accounts /journal /reports /users; do
  code="$(curl -sS -o "$tmpdir/page" -w '%{http_code}' -b "$cookies" "$BASE_URL$path")"
  if [ "$code" != "200" ]; then
    echo "FAILED $path -> HTTP $code"
    cat "$tmpdir/page"
    exit 1
  fi
  echo "PASS $path"
done

echo "All smoke tests passed."
