#!/bin/bash
set -e

echo "=== Release Artifact Check ==="

REQUIRED_FILES=(
    "docs/release/beginner-usability-gate.md"
    "docs/release/clean-machine-checklist.md"
    "docs/release/end-to-end-acceptance-matrix.md"
    "docs/release/known-issues-template.md"
    "docs/privacy/local-data-and-privacy.md"
    "docs/design/embedded-terminal-security.md"
)

MISSING=0

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -s "$file" ]; then
        echo "FAIL: missing or empty $file"
        MISSING=1
    else
        echo "OK: $file"
    fi
done

if [ "$MISSING" -ne 0 ]; then
    exit 1
fi

echo "PASS: Required release artifacts are present"
