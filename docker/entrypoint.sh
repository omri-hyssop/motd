#!/usr/bin/env sh
set -eu

# Optional: wait for Postgres if DATABASE_URL points at it
if [ "${WAIT_FOR_DB:-1}" = "1" ] && [ -n "${DATABASE_URL:-}" ]; then
  if echo "$DATABASE_URL" | grep -qiE '^postgres(ql)?://'; then
    echo "Waiting for database..."
    for i in $(seq 1 60); do
      if pg_isready -d "$DATABASE_URL" >/dev/null 2>&1; then
        break
      fi
      sleep 1
      if [ "$i" -eq 60 ]; then
        echo "Database not ready after 60s" >&2
        exit 1
      fi
    done
  fi
fi

# Optional: apply migrations on startup (best for single-instance / controlled deploys)
if [ "${RUN_MIGRATIONS:-1}" = "1" ]; then
  echo "Applying migrations..."
  flask db upgrade
fi

UPLOAD_DIR="${UPLOAD_FOLDER:-uploads}"
mkdir -p "$UPLOAD_DIR" || true

exec "$@"
