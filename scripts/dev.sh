#!/bin/bash
set -e

docker compose up --build -d

echo "Waiting for services to be ready..."
sleep 10

./scripts/smoke-test.sh