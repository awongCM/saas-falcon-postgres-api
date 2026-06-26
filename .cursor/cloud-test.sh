#!/bin/bash
set -euo pipefail

API_URL="${API_URL:-http://localhost:5000}"
MAX_ATTEMPTS="${MAX_ATTEMPTS:-60}"
SLEEP_SECONDS="${SLEEP_SECONDS:-5}"

echo "Waiting for API at ${API_URL} (up to $((MAX_ATTEMPTS * SLEEP_SECONDS))s)..."

for attempt in $(seq 1 "$MAX_ATTEMPTS"); do
  if curl -sf "${API_URL}/" > /dev/null; then
    echo "API is ready (attempt ${attempt})."
    ./validate_poc.bash
    exit 0
  fi

  echo "Attempt ${attempt}/${MAX_ATTEMPTS}: API not ready yet..."
  sleep "$SLEEP_SECONDS"
done

echo "API did not become ready in time."
echo "Check the app-stack terminal for docker compose logs."
exit 1
