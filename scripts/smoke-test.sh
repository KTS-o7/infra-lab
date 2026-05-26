#!/bin/bash
set -e

echo "=== Infra Quest Smoke Test ==="

MAX_WAIT=60
INTERVAL=2
WEB_URL="${WEB_URL:-http://localhost:3000}"
API_URL="${API_URL:-http://localhost:8000}"
FLOCI_URL="${FLOCI_URL:-http://localhost:4566}"

check_service() {
    local url=$1
    local name=$2
    local elapsed=0
    while ! curl -sf "$url" > /dev/null 2>&1; do
        if [ "$elapsed" -ge "$MAX_WAIT" ]; then
            echo "FAIL: $name did not become available within ${MAX_WAIT}s"
            exit 1
        fi
        sleep "$INTERVAL"
        elapsed=$((elapsed + INTERVAL))
    done
    echo "OK: $name is available at $url"
}

check_service "$WEB_URL" "Web"
check_service "$API_URL/health" "API"
check_service "$FLOCI_URL/" "Floci"

echo ""
echo "=== API Runtime Status ==="
curl -s "$API_URL/runtime/status" | python3 -m json.tool || echo "JSON parse failed"

echo ""
echo "=== Mission List ==="
curl -s "$API_URL/missions" | python3 -m json.tool || echo "JSON parse failed"

echo ""
echo "=== Profile ==="
curl -s "$API_URL/profile" | python3 -m json.tool || echo "JSON parse failed"

echo ""
echo "=== Course Map ==="
curl -s "$API_URL/course" | python3 -m json.tool || echo "JSON parse failed"

echo ""
echo "=== Smoke Test Complete ==="
