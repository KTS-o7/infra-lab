# Infra Quest Specification

## Overview

Infra Quest is a fully local, zero-cost, gamified AWS learning lab for beginners. Learners complete infrastructure missions using AWS-style tools and workflows, but every AWS API call runs against Floci locally instead of real AWS.

The first user experience should be:

```bash
docker compose up --build
```

Then open:

```text
http://localhost:3000
```

From there, a learner can complete guided AWS missions, validate their work, earn XP, unlock badges, and reset local lab state without creating an AWS account or spending money.

## Primary Goals

- Teach AWS fundamentals to beginners with hands-on missions.
- Keep the full lab runnable locally.
- Use Floci as the local AWS-compatible service emulator.
- Avoid real AWS credentials, real AWS accounts, and cloud spend.
- Provide immediate validation feedback through the app.
- Make the project reproducible with pinned versions and lockfiles.

## Non-Goals

- Do not deploy resources to real AWS.
- Do not require a cloud account.
- Do not build advanced enterprise IAM or multi-account workflows in the MVP.
- Do not prioritize EC2, EKS, or RDS in the first curriculum.
- Do not build a marketing landing page as the primary UI.

## Local-Only Constraint

All AWS SDK and CLI traffic must go to:

```text
http://localhost:4566
```

Inside Docker containers, services should use:

```text
http://floci:4566
```

The backend must refuse to start if it appears configured to talk to real AWS.

Disallowed endpoint patterns include:

```text
amazonaws.com
https://aws
```

Use fake credentials only:

```text
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
AWS_DEFAULT_REGION=us-east-1
```

## Pinned Stack

Version basis checked on May 23, 2026.

| Layer | Technology | Version |
| --- | --- | --- |
| Local AWS emulator | Floci | `floci/floci:1.5.13` |
| Frontend package manager | Bun | `1.3.14` |
| Frontend runtime baseline | Node.js | `24.16.0` LTS |
| Web framework | Next.js | `16.2.6` |
| UI library | React | `19.2.1` |
| Language | TypeScript | `6.0.3` |
| Backend language | Python | `3.14.5` |
| Backend framework | FastAPI | `0.136.1` |
| Database | SQLite | bundled |
| Orchestration | Docker Compose | pinned through Docker installation |

Supporting dependencies must also be pinned exactly in lockfiles.

## Bun Usage Decision

Use Bun for:

- frontend dependency installation
- frontend script running
- workspace package management
- faster local developer workflows

Keep Node.js LTS available as the Next.js runtime baseline for production-style containers.

This gives us Bun's install and script performance while keeping the safest Next.js runtime path available.

## System Architecture

```text
Browser
  |
  v
Next.js Web App :3000
  |
  v
FastAPI Backend :8000
  |
  v
Floci AWS Emulator :4566
  |
  v
Local persisted data
```

Services:

```text
web       Next.js UI
api       FastAPI mission API and validators
floci     local AWS emulator
sqlite    file-based DB inside api volume
```

## Repository Structure

```text
infra-lab/
  docker-compose.yml
  .env.example
  .gitignore
  README.md
  Makefile

  package.json
  bun.lock

  apps/
    web/
      Dockerfile
      package.json
      next.config.ts
      tsconfig.json
      app/
      components/
      lib/

    api/
      Dockerfile
      pyproject.toml
      uv.lock
      app/
        main.py
        config.py
        db.py
        models.py
        aws_client.py
        mission_loader.py
        validators/
        routes/

  missions/
    s3-first-bucket/
      mission.yml
      validator.py
      seed.py
      reset.py

    sqs-first-message/
      mission.yml
      validator.py
      seed.py
      reset.py

    dynamodb-first-table/
      mission.yml
      validator.py
      seed.py
      reset.py

  scripts/
    dev.sh
    reset-lab.sh
    verify-local-only.sh
    smoke-test.sh

  data/
    floci/
    api/
```

The `data/` directory must be gitignored.

## Docker Compose Specification

Initial Compose shape:

```yaml
services:
  floci:
    image: floci/floci:1.5.13
    ports:
      - "4566:4566"
    volumes:
      - ./data/floci:/app/data

  api:
    build:
      context: ./apps/api
    ports:
      - "8000:8000"
    environment:
      AWS_ENDPOINT_URL: http://floci:4566
      AWS_ACCESS_KEY_ID: test
      AWS_SECRET_ACCESS_KEY: test
      AWS_DEFAULT_REGION: us-east-1
      DATABASE_URL: sqlite:////app/data/lab.db
      MISSIONS_DIR: /app/missions
    volumes:
      - ./data/api:/app/data
      - ./missions:/app/missions:ro
    depends_on:
      - floci

  web:
    build:
      context: .
      dockerfile: ./apps/web/Dockerfile
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    depends_on:
      - api
```

After the first pull, replace the Floci tag with a digest-pinned image for stronger reproducibility:

```yaml
image: floci/floci@sha256:<digest>
```

## Frontend Specification

Use:

- Next.js App Router
- React Server Components where useful
- Client Components only for interactive mission UI
- Tailwind CSS
- shadcn/ui copied components
- `lucide-react` icons
- Zod for API response validation

Routes:

```text
/                 Mission map
/missions/[id]    Mission detail
/profile          XP, badges, progress
/settings         Local runtime status
```

The first screen should be the actual lab experience, not a marketing page.

Mission map requirements:

- show locked and unlocked missions
- show service category
- show difficulty
- show XP reward
- show completion state
- show badge progress

Mission detail requirements:

- objective
- scenario
- required AWS concept
- copyable CLI commands
- hints
- validation button
- reset button
- validation result panel

## Backend Specification

Use FastAPI for the API and mission validation layer.

Endpoints:

```text
GET  /health
GET  /runtime/status
GET  /missions
GET  /missions/{mission_id}
POST /missions/{mission_id}/start
POST /missions/{mission_id}/validate
POST /missions/{mission_id}/reset
GET  /profile
```

Core modules:

```text
config.py
  Loads environment variables and validates local-only endpoint rules.

aws_client.py
  Creates boto3 clients pointed at Floci.

mission_loader.py
  Reads mission.yml files.

validators/
  Contains shared validation primitives.

models.py
  SQLite models for profile, mission progress, attempts, and badges.

routes/
  FastAPI route modules.
```

The backend validates learner work by inspecting Floci state directly. It must not trust user-submitted text, screenshots, or claims.

## Mission Definition Specification

Each mission lives in its own folder under `missions/`.

Example:

```yaml
id: s3-first-bucket
title: First Bucket
summary: Create your first object storage bucket.
difficulty: beginner
services:
  - s3
xp: 100
estimated_minutes: 10

story:
  You are setting up storage for a small app that needs to save a welcome file.

learning_objectives:
  - Understand what an S3 bucket is
  - Create a bucket locally
  - Upload and inspect an object
  - Learn endpoint-url targeting

commands:
  - label: Create bucket
    command: aws --endpoint-url http://localhost:4566 s3 mb s3://starter-bucket
  - label: Upload object
    command: aws --endpoint-url http://localhost:4566 s3 cp hello.txt s3://starter-bucket/hello.txt

checks:
  - type: s3_bucket_exists
    bucket: starter-bucket
  - type: s3_object_exists
    bucket: starter-bucket
    key: hello.txt
  - type: s3_object_body_equals
    bucket: starter-bucket
    key: hello.txt
    value: Hello from local AWS

hints:
  - text: Every AWS CLI command in this lab needs --endpoint-url.
    penalty_xp: 5
  - text: Bucket names are global in real AWS, but local here.
    penalty_xp: 5
```

Validation response:

```json
{
  "missionId": "s3-first-bucket",
  "passed": false,
  "xpAwarded": 0,
  "checks": [
    {
      "id": "s3_bucket_exists",
      "passed": true,
      "message": "Bucket starter-bucket exists."
    },
    {
      "id": "s3_object_exists",
      "passed": false,
      "message": "Object hello.txt was not found."
    }
  ]
}
```

## MVP Curriculum

1. Cloud Explorer
   - Concepts: local endpoint, fake credentials, AWS CLI basics

2. First Bucket
   - Service: S3
   - Concepts: buckets, objects, upload, download

3. Queue the Message
   - Service: SQS
   - Concepts: queue, send, receive, delete

4. Publish and Subscribe
   - Services: SNS and SQS
   - Concepts: topics, subscriptions, fanout

5. Key-Value Store
   - Service: DynamoDB
   - Concepts: table, partition key, put item, get item

6. Tiny Function
   - Service: Lambda
   - Concepts: function, invoke, payload

7. HTTP Trigger
   - Services: API Gateway and Lambda
   - Concepts: routes, HTTP endpoint, function integration

8. Serverless Boss Mission
   - Services: API Gateway, Lambda, DynamoDB, SQS
   - Concepts: small event-driven app

## Gamification Specification

Mechanics:

- XP awarded after successful validation
- badges for service mastery
- optional hints with XP penalty
- validation attempts tracked
- missions unlocked sequentially in MVP
- boss missions combine multiple services

Badge examples:

```text
S3 Starter
Queue Runner
DynamoDB Scout
Serverless Builder
```

Profile model:

```text
id
display_name
total_xp
created_at
updated_at
```

Mission progress model:

```text
profile_id
mission_id
status: locked | available | started | completed
attempts
hints_used
xp_awarded
completed_at
```

## Reproducibility Rules

Frontend:

- `packageManager` must be `bun@1.3.14`
- `bun.lock` must be committed
- no dependency ranges using `^` or `~`
- Docker image must pin Bun version
- Node image must pin Node version

Backend:

- Python image pinned to `3.14.5`
- `pyproject.toml` contains exact dependency versions
- `uv.lock` committed
- no unbounded dependencies

Infra:

- Floci tag pinned to `1.5.13`
- later digest-pin Floci image
- Docker Compose committed
- no `latest` image tags

## Safety Requirements

The repository must include:

```bash
scripts/verify-local-only.sh
```

It should fail if it finds:

- `image: *:latest`
- `amazonaws.com`
- real-looking AWS keys
- unpinned package versions
- frontend dependency ranges using `^` or `~`

## Testing Requirements

Backend tests:

- mission loading tests
- local-only config tests
- validator unit tests
- API route tests
- SQLite progress tests

Integration tests:

- start Floci
- create S3 bucket via boto3
- validate S3 mission
- reset S3 mission
- create SQS queue
- validate SQS mission

Frontend tests:

- mission map renders
- mission detail renders
- validation button displays results
- hint penalty updates UI
- runtime status warning displays if API is down

Smoke test:

```bash
docker compose up -d
scripts/smoke-test.sh
```

The smoke test should verify:

- web responds
- api responds
- floci responds
- api can create and list an S3 bucket against Floci
- mission loader works

## Developer Commands

Suggested `Makefile`:

```makefile
dev:
	docker compose up --build

down:
	docker compose down

reset:
	./scripts/reset-lab.sh

verify:
	./scripts/verify-local-only.sh
	./scripts/smoke-test.sh

logs:
	docker compose logs -f

test-api:
	cd apps/api && uv run pytest

test-web:
	bun --cwd apps/web test

build-web:
	bun --cwd apps/web run build
```

## Key Risks

- Floci behavior may differ from AWS for advanced services.
- Lambda and API Gateway support need early validation.
- Bun runtime may expose edge cases with Next.js.
- Beginners may get stuck on local AWS CLI setup.
- Mission reset must be reliable or learners will get confused.

## Risk Mitigations

- Start with S3, SQS, and DynamoDB.
- Keep CLI commands copyable.
- Add reset per mission.
- Validate Floci support before adding each service.
- Use Bun for package management first, while keeping Node LTS as runtime fallback.
