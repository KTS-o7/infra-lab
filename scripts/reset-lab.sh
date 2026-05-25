#!/bin/bash
set -e

echo "=== Resetting Infra Quest Lab ==="
echo "Stopping services..."
docker compose down

echo "Cleaning data volumes..."
rm -rf data/floci/* data/api/*

echo "Restarting services..."
docker compose up --build -d

echo "Lab reset complete."