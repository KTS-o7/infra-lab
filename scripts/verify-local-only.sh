#!/bin/bash
set -e

echo "=== Local-Only Safety Scan ==="

FOUND_ISSUES=0

if rg ':latest' docker-compose.yml; then
    echo "FAIL: Docker 'latest' tag found"
    FOUND_ISSUES=1
fi

DENYLISTED="apps/api/app/config.py"
if rg 'amazonaws\.com' docker-compose.yml apps/api apps/web missions scripts --glob '!*.example' --glob '!Dockerfile' --glob '!test_*.py' | rg -v "$DENYLISTED"; then
    echo "FAIL: Real AWS endpoint reference found"
    FOUND_ISSUES=1
fi

if rg '\^|~' apps/web/package.json; then
    echo "FAIL: Unpinned dependency ranges found in package.json"
    FOUND_ISSUES=1
fi

FAKE_KEYS="AKIAIOSFODNN7EXAMPLE"
if rg -i "$FAKE_KEYS" apps/api apps/web --glob '!*.example' 2>/dev/null | rg -v 'test|fake|_test|config'; then
    echo "FAIL: Suspicious AWS key pattern found"
    FOUND_ISSUES=1
fi

# Pre-flight: warn if the pinned AWS-emulator image isn't pullable from the
# local Docker registry. This is a warning only — it does not fail the script
# so CI stays green even when the default image is temporarily unavailable.
# Users on a fresh machine can swap in a drop-in via FLOCI_IMAGE (see
# .env.example for the localstack/localstack:3 fallback).
FLOCI_IMAGE="${FLOCI_IMAGE:-floci/floci:1.5.13}"
if docker pull --quiet "$FLOCI_IMAGE" >/dev/null 2>/tmp/pull-err; then
    echo "OK: pre-flight pull succeeded for $FLOCI_IMAGE"
else
    echo "WARN: pre-flight pull failed for $FLOCI_IMAGE."
    echo "      The pinned image is not pullable from the local registry. To use a"
    echo "      drop-in replacement, set FLOCI_IMAGE=localstack/localstack:3 in .env"
    echo "      (see .env.example for details). Continuing — this is a warning, not a failure."
fi
rm -f /tmp/pull-err

if [ $FOUND_ISSUES -eq 0 ]; then
    echo "PASS: No local-only violations found"
    exit 0
else
    exit 1
fi