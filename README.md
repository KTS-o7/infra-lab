# Infra Quest

A local-first, zero-cost, gamified AWS learning lab for beginners.

## Quick Start

```bash
docker compose up --build
```

Then open [http://localhost:3000](http://localhost:3000).

## What is this?

Infra Quest teaches AWS concepts through guided missions. Every AWS API call runs against **Floci**, a local AWS emulator — no real AWS account, credentials, or cloud resources required.

## Missions

- **Cloud Explorer** — Verify your local lab is working
- **First Bucket** — Create an S3 bucket and upload a file
- **Queue the Message** — Create an SQS queue and send a message
- **Publish and Subscribe** — SNS topic with SQS fanout
- **Key-Value Store** — DynamoDB table with partition keys
- **Tiny Function** — Deploy and invoke a Lambda function
- **HTTP Trigger** — Expose Lambda through API Gateway
- **Serverless Boss Mission** — Complete serverless workflow

## Tech Stack

- **Floci** — Local AWS emulator
- **FastAPI** — Mission API and validators
- **Next.js** — Web app frontend
- **SQLite** — Progress persistence
- **Docker Compose** — Local orchestration

## Safety

This project is **local-only**. No real AWS endpoints are used. All CLI commands include `--endpoint-url http://floci:4566` when running inside the web terminal.

## Advanced: Running AI Agent in Local Terminal

By default, the "Ask me anything" chat runs its AI command inside the Docker container. If you want it to run in your **actual local terminal** (e.g. to use tools like `gemini` or `gh copilot` that are only installed on your host), follow these steps:

1.  Start the AMA Host Bridge on your local machine:
    ```bash
    python3 scripts/ama-host-bridge.py
    ```
2.  Set the following in your `.env`:
    ```bash
    AMA_HOST_BRIDGE=http://host.docker.internal:8080
    ```
3.  Restart Docker Compose:
    ```bash
    docker compose up -d
    ```

## Commands

```bash
make dev          # Start all services
make down        # Stop all services
make reset       # Reset lab data
make verify      # Run safety scan, tests, and smoke test
make logs        # Tail Docker logs
```