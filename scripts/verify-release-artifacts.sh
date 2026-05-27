#!/bin/bash
set -e

echo "=== Release Artifact Check ==="

REQUIRED_FILES=(
    "docs/release/beginner-usability-gate.md"
    "docs/release/clean-machine-checklist.md"
    "docs/release/end-to-end-acceptance-matrix.md"
    "docs/release/final-handoff.md"
    "docs/release/known-issues-template.md"
    "docs/privacy/local-data-and-privacy.md"
    "docs/design/embedded-terminal-security.md"
)

MISSING=0
FAILED=0

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -s "$file" ]; then
        echo "FAIL: missing or empty $file"
        MISSING=1
    else
        echo "OK: $file"
    fi
done

require_text() {
    local file=$1
    local text=$2
    if ! grep -Fq "$text" "$file"; then
        echo "FAIL: $file missing required text: $text"
        FAILED=1
    fi
}

for file in "${REQUIRED_FILES[@]}"; do
    case "$file" in
        docs/release/*)
            require_text "README.md" "$file"
            require_text "docs/release/final-handoff.md" "$file"
            ;;
    esac
done

if grep -R "^Commit: \`" docs/release/*.md > /dev/null; then
    echo "FAIL: release docs must use Latest full local gate or Current PR head, not a generic Commit field"
    FAILED=1
fi

if [ "$MISSING" -ne 0 ]; then
    exit 1
fi

if [ "$FAILED" -ne 0 ]; then
    exit 1
fi

echo "PASS: Required release artifacts are present"
