#!/bin/bash
set -euo pipefail

# Idempotent repo setup for cloud agent sessions.
cp .env.example .env
mkdir -p logs
chmod +x validate_poc.bash .cursor/cloud-start-stack.sh .cursor/cloud-test.sh

echo "Cloud install complete."
