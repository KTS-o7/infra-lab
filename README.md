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

This project is **local-only**. No real AWS endpoints are used. All CLI commands include `--endpoint-url http://localhost:4566`.

## Commands

```bash
make dev          # Start all services
make down        # Stop all services
make reset       # Reset lab data
make verify      # Run safety scan, tests, and smoke test
make logs        # Tail Docker logs
```