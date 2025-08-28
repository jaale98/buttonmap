#!/usr/bin/env sh
set -e

echo "Checking database connectivity..."
READY=0
for i in $(seq 1 30); do
  if python - <<'PY' >/dev/null 2>&1
import os, psycopg
url = os.environ.get("DATABASE_URL", "")
dsn = url.replace("postgresql+psycopg", "postgresql", 1)
with psycopg.connect(dsn) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT 1")
PY
  then
    READY=1
    echo "DB is ready."
    break
  else
    echo "DB not ready yet... ($i/30)"
    sleep 1
  fi
done

if [ "$READY" -ne 1 ]; then
  echo "Proceeding; Alembic may still retry internally."
fi

echo "Running alembic upgrade head..."
alembic upgrade head

echo "Starting Uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000