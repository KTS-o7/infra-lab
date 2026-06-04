#!/bin/bash
set -e

echo "=== Local-Only Safety Scan ==="

FOUND_ISSUES=0

if grep -q ':latest' docker-compose.yml; then
    echo "FAIL: Docker 'latest' tag found"
    FOUND_ISSUES=1
fi

DENYLISTED="apps/api/app/config.py"
# Search for amazonaws.com references, excluding binary files, venv, and certain patterns
# We also exclude this script itself from the search
if find docker-compose.yml apps/api apps/web missions scripts -type f \
    ! -path "*/.*" \
    ! -path "*/node_modules/*" \
    ! -path "*/.venv/*" \
    ! -path "*/__pycache__/*" \
    ! -name "$(basename "$0")" \
    \( -name "*" ! -name "*.example" ! -name "Dockerfile" ! -name "test_*.py" ! -name "*.pyc" \) \
    -exec grep -I -H 'amazonaws\.com' {} + | grep -v "$DENYLISTED" > /dev/null; then
    echo "FAIL: Real AWS endpoint reference found"
    FOUND_ISSUES=1
fi

if grep -E '\^|~' apps/web/package.json > /dev/null; then
    echo "FAIL: Unpinned dependency ranges found in package.json"
    FOUND_ISSUES=1
fi

FAKE_KEYS="AKIAIOSFODNN7EXAMPLE"
if find apps/api apps/web -type f \
    ! -path "*/.*" \
    ! -path "*/node_modules/*" \
    ! -path "*/.venv/*" \
    ! -path "*/__pycache__/*" \
    ! -name "$(basename "$0")" \
    \( -name "*" ! -name "*.example" ! -name "*.pyc" \) \
    -exec grep -I -Hi "$FAKE_KEYS" {} + | grep -Ev 'test|fake|_test|config' > /dev/null; then
    echo "FAIL: Suspicious AWS key pattern found"
    FOUND_ISSUES=1
fi

if [ $FOUND_ISSUES -eq 0 ]; then
    echo "PASS: No local-only violations found"
    exit 0
else
    exit 1
fi
