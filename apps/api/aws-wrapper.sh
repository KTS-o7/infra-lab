#!/bin/bash
# Transparent aws CLI wrapper for the in-browser terminal.
#
# Mission commands are authored with --endpoint-url http://localhost:4566
# so they work when a learner runs them in their own terminal on the host.
# Inside the API container, localhost:4566 is unreachable — Floci is only
# accessible at http://floci:4566 on the Docker internal network.
#
# This wrapper rewrites any --endpoint-url http://localhost:4566 argument
# to http://floci:4566 before delegating to the real aws CLI, making
# copy-pasted mission commands work transparently in the in-browser terminal.
#
# The real aws binary is renamed to aws-real in the venv by the Dockerfile.
REAL_AWS=/app/.venv/bin/aws-real

args=()
for arg in "$@"; do
    if [ "$arg" = "http://localhost:4566" ]; then
        args+=("http://floci:4566")
    else
        args+=("$arg")
    fi
done

exec "$REAL_AWS" "${args[@]}"
