#!/bin/bash
set -euo pipefail

echo "Starting Docker Compose stack..."
docker compose up --build
