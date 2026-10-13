#!/usr/bin/env bash
# Usage: bash smoke.sh <base-url>
set -euo pipefail
BASE="${1%/}"
# Wait up to 20 seconds for the app to answer
for i in $(seq 1 20); do
  curl -fs "$BASE/health" > /dev/null 2>&1 && break
  [ "$i" = 20 ] && { echo "No answer from $BASE/health"; exit 1; }
  sleep 1
done
curl -fsS "$BASE/fine?days=5" | jq -e '.fee == 1.5'
curl -fsS "$BASE/fine?days=30&deluxe=1" | jq -e '.fee == 5'
echo "Smoke tests passed against $BASE"
