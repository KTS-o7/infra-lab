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

Learner progress and validation history are stored locally by the API service. See [Local Data And Privacy](docs/privacy/local-data-and-privacy.md) for what is stored, what must not be stored, and the reset expectations.

## Commands

```bash
make dev          # Start all services
make down        # Stop all services
make reset       # Reset lab data
make verify      # Run safety scan, tests, and smoke test
make logs        # Tail Docker logs
```

## Mission Authoring

Create each lesson under `missions/<mission-id>/mission.yml`. Before opening a
change, run:

```bash
./scripts/validate-mission-authoring.py
make verify
```

Authoring checklist:

- Include all release fields: base mission metadata plus `capability`,
  `motivation`, `theory`, `thought_process`, and `debrief`.
- Keep every AWS CLI command local-only with
  `--endpoint-url http://localhost:4566`; never point examples at real AWS.
- Give every command an action-oriented label, and make every guided step
  reference an existing `command_id`.
- Define target state for every step and map it to real validation checks.
- Reference every check from at least one step, and reference only existing
  checks from steps and hints.
- Declare owned resources for resources created by mission commands so reset
  can clean up mission-owned state.
- Provide staged hints for normal lessons: `nudge`, `diagnosis`, and `repair`.
- For capstones, reduce command guidance: leave at least one step for learner
  reasoning instead of providing a copy command for every step.
- In `thought_process`, name the tradeoff or rejected alternative so learners
  understand why this design is being built.

## Release Checks

Release candidate documentation lives in `docs/release/`:

- [Beginner Usability Gate](docs/release/beginner-usability-gate.md)
- [Clean-Machine Release Checklist](docs/release/clean-machine-checklist.md)
- [End-to-End Acceptance Matrix](docs/release/end-to-end-acceptance-matrix.md)
- [Known Issues Template](docs/release/known-issues-template.md)

The embedded terminal implementation plan is documented in [Embedded Terminal Security Design](docs/design/embedded-terminal-security.md).

```bash
make verify-release-artifacts
make verify
```
