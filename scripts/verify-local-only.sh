#!/bin/bash
set -e

echo "=== Local-Only Safety Scan ==="

FOUND_ISSUES=0

if rg ':latest' docker-compose.yml; then
    echo "FAIL: Docker 'latest' tag found"
    FOUND_ISSUES=1
fi

if rg 'amazonaws\.com' docker-compose.yml apps/api apps/web missions scripts; then
    echo "FAIL: Real AWS endpoint reference found"
    FOUND_ISSUES=1
fi

if rg '\^|~' apps/web/package.json; then
    echo "FAIL: Unpinned dependency ranges found in package.json"
    FOUND_ISSUES=1
fi

FAKE_KEYS="AKIAIOSFODNN7EXAMPLE|aws-access-key-id|aws-secret-access-key"
if rg -i "$FAKE_KEYS" apps/api apps/web scripts --glob '!*.example' 2>/dev/null | rg -v 'test|fake|_test'; then
    echo "FAIL: Suspicious AWS key pattern found"
    FOUND_ISSUES=1
fi

if [ $FOUND_ISSUES -eq 0 ]; then
    echo "PASS: No local-only violations found"
    exit 0
else
    exit 1
fi