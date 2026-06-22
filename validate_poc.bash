#!/bin/bash
set -euo pipefail

API_URL="${API_URL:-http://localhost:5000}"

echo "=== Email/Domain Validator POC ==="
echo "API: $API_URL"
echo

run_validation() {
  local type="$1"
  local value="$2"

  echo "--- Validating $type: $value ---"

  response=$(curl -s -X POST "$API_URL/validate" \
    -H "Content-Type: application/json" \
    -d "{\"type\":\"$type\",\"value\":\"$value\"}")

  echo "Queued: $response"

  job_id=$(echo "$response" | jq -r '.data.job_id')
  status="PENDING"

  while [ "$status" != "SUCCESS" ] && [ "$status" != "FAILURE" ]; do
    sleep 1
    result=$(curl -s "$API_URL/validate/$job_id")
    status=$(echo "$result" | jq -r '.data.status')
    echo "Status: $status"
  done

  echo "$result" | jq .
  echo
}

run_validation "email" "recruiter@google.com"
run_validation "email" "test@mailinator.com"
run_validation "domain" "stripe.com"
run_validation "domain" "this-domain-should-not-exist-12345.invalid"

echo "=== Recent validation jobs ==="
curl -s "$API_URL/validate?limit=5" | jq .
