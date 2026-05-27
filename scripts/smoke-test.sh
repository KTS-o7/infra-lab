#!/bin/bash
set -e

echo "=== Infra Quest Smoke Test ==="

MAX_WAIT=60
INTERVAL=2
ELAPSED=0

check_service() {
    local url=$1
    local name=$2
    while ! curl -sf "$url" > /dev/null 2>&1; do
        if [ $ELAPSED -ge $MAX_WAIT ]; then
            echo "FAIL: $name did not become available within ${MAX_WAIT}s"
            exit 1
        fi
        sleep $INTERVAL
        ELAPSED=$((ELAPSED + INTERVAL))
    done
    echo "OK: $name is available at $url"
}

check_service "http://localhost:3000" "Web"
check_service "http://localhost:8001/health" "API"
check_service "http://localhost:4566/" "Floci"

echo ""
echo "=== API Runtime Status ==="
curl -s http://localhost:8001/runtime/status | python3 -m json.tool || echo "JSON parse failed"

echo ""
echo "=== Mission List ==="
curl -s http://localhost:8001/missions | python3 -m json.tool || echo "JSON parse failed"

echo ""
echo "=== Profile ==="
curl -s http://localhost:8001/profile | python3 -m json.tool || echo "JSON parse failed"

echo ""
echo "=== S3 API Test (create/delete bucket via Floci) ==="
BUCKET="smoke-test-bucket-$(date +%s)"
curl -s -X POST "http://localhost:8001/floci/s3/bucket" \
    -H "Content-Type: application/json" \
    -d "{\"bucket\": \"$BUCKET\"}" | python3 -m json.tool || echo "S3 bucket create failed"

echo ""
echo "=== Smoke Test Complete ==="
