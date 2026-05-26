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
http://floci:4566
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

Required frontend package pins:

| Package | Version |
| --- | --- |
| `next` | `16.2.6` |
| `react` | `19.2.1` |
| `react-dom` | `19.2.1` |
| `typescript` | `6.0.3` |
| `tailwindcss` | `4.1.13` |
| `@tailwindcss/postcss` | `4.1.13` |
| `lucide-react` | `1.16.0` |
| `zod` | `4.1.5` |
| `clsx` | `2.1.1` |
| `tailwind-merge` | `3.3.1` |
| `eslint` | `9.35.0` |
| `prettier` | `3.6.2` |

Required backend package pins:

| Package | Version |
| --- | --- |
| `fastapi` | `0.136.1` |
| `uvicorn[standard]` | `0.47.0` |
| `boto3` | `1.43.12` |
| `botocore` | `1.43.12` |
| `sqlmodel` | `0.0.38` |
| `pydantic` | `2.13.4` |
| `pyyaml` | `6.0.3` |
| `pytest` | `9.0.3` |
| `ruff` | `0.15.14` |

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

## Agent Execution Contract

This section is binding for implementation. An agent must not invent alternate schemas, endpoint shapes, state transitions, or validation semantics unless a later change explicitly updates this file.

### API Response Envelope

Successful responses return the resource body directly. Error responses always return:

```json
{
  "error": {
    "code": "MISSION_NOT_FOUND",
    "message": "Mission s3-missing was not found.",
    "details": {
      "missionId": "s3-missing"
    }
  }
}
```

Rules:

- `error.code` is stable and machine-readable.
- `error.message` is concise and safe to show in the UI.
- `error.details` is always an object, even when empty.
- Error messages must never tell users to configure real AWS.

### API Contracts

#### `GET /health`

Purpose: confirm API process is alive.

Response `200`:

```json
{
  "status": "ok",
  "service": "infra-quest-api"
}
```

No external dependency checks are performed here.

#### `GET /runtime/status`

Purpose: report whether local dependencies are ready.

Response `200`:

```json
{
  "api": {
    "status": "online"
  },
  "floci": {
    "status": "online",
    "endpoint": "http://floci:4566",
    "checkedAt": "2026-05-23T13:55:00Z"
  },
  "database": {
    "status": "online"
  },
  "localOnly": {
    "status": "enforced",
    "endpoint": "http://floci:4566"
  }
}
```

If Floci is unavailable, return `200` with `floci.status = "offline"` so the frontend can render a degraded state. Use `503` only if the API cannot evaluate runtime status at all.

#### `GET /missions`

Purpose: list missions in curriculum order.

Response `200`:

```json
{
  "missions": [
    {
      "id": "s3-first-bucket",
      "title": "First Bucket",
      "summary": "Create your first object storage bucket.",
      "difficulty": "beginner",
      "services": ["s3"],
      "xp": 100,
      "status": "available",
      "prerequisites": [],
      "estimatedMinutes": 10
    }
  ]
}
```

Sorting rules:

1. `order` field from mission YAML, ascending.
2. `id` ascending as deterministic tie-breaker.

#### `GET /missions/{mission_id}`

Purpose: return full mission content and learner progress.

Response `200`:

```json
{
  "mission": {
    "id": "s3-first-bucket",
    "order": 2,
    "title": "First Bucket",
    "summary": "Create your first object storage bucket.",
    "difficulty": "beginner",
    "services": ["s3"],
    "xp": 100,
    "estimatedMinutes": 10,
    "status": "started",
    "story": "You are setting up storage for a small app.",
    "learningObjectives": [
      "Understand what an S3 bucket is",
      "Upload and inspect an object"
    ],
    "commands": [
      {
        "id": "create-bucket",
        "label": "Create bucket",
        "command": "aws --endpoint-url http://floci:4566 s3 mb s3://starter-bucket"
      }
    ],
    "hints": [
      {
        "id": "endpoint-url",
        "title": "Check the endpoint",
        "isUsed": false,
        "penaltyXp": 5
      }
    ],
    "progress": {
      "status": "started",
      "attempts": 1,
      "hintsUsed": [],
      "xpAwarded": 0,
      "startedAt": "2026-05-23T13:55:00Z",
      "completedAt": null
    }
  }
}
```

Hint text is omitted until the hint is used. After use, include `text`.

#### `POST /missions/{mission_id}/start`

Purpose: mark a mission as started.

Request body: empty object.

Response `200`:

```json
{
  "missionId": "s3-first-bucket",
  "status": "started",
  "startedAt": "2026-05-23T13:55:00Z"
}
```

Behavior:

- If mission is `available`, transition to `started`.
- If mission is already `started`, return current state.
- If mission is `completed`, keep it completed and return `status = "completed"`.
- If mission is `locked`, return `409 MISSION_LOCKED`.

#### `POST /missions/{mission_id}/hints/{hint_id}/use`

Purpose: reveal and persist a hint.

Request body: empty object.

Response `200`:

```json
{
  "missionId": "s3-first-bucket",
  "hint": {
    "id": "endpoint-url",
    "title": "Check the endpoint",
    "text": "Every AWS CLI command in this lab needs --endpoint-url.",
    "penaltyXp": 5,
    "isUsed": true
  },
  "possibleXp": 95
}
```

Behavior:

- Using the same hint twice is idempotent.
- Hint penalty is applied once.
- Hints cannot reduce possible XP below `0`.
- Using a hint after mission completion reveals the hint but does not change awarded XP.

#### `POST /missions/{mission_id}/validate`

Purpose: inspect Floci state and record a validation attempt.

Request body: empty object.

Response `200`, partial failure:

```json
{
  "missionId": "s3-first-bucket",
  "passed": false,
  "status": "started",
  "xpAwarded": 0,
  "attemptNumber": 2,
  "checks": [
    {
      "id": "bucket-exists",
      "type": "s3_bucket_exists",
      "passed": true,
      "message": "Bucket starter-bucket exists."
    },
    {
      "id": "object-exists",
      "type": "s3_object_exists",
      "passed": false,
      "message": "Object hello.txt was not found in bucket starter-bucket."
    }
  ]
}
```

Response `200`, success:

```json
{
  "missionId": "s3-first-bucket",
  "passed": true,
  "status": "completed",
  "xpAwarded": 100,
  "attemptNumber": 3,
  "checks": [
    {
      "id": "bucket-exists",
      "type": "s3_bucket_exists",
      "passed": true,
      "message": "Bucket starter-bucket exists."
    }
  ],
  "unlockedMissionIds": ["sqs-first-message"]
}
```

Behavior:

- If mission is not started or completed, return `409 MISSION_NOT_STARTED`.
- If Floci is offline, return `503 FLOCI_UNAVAILABLE`.
- Record every validation attempt.
- Preserve check order from mission YAML.
- Award XP only on the first successful completion.
- Revalidating a completed mission returns `passed = true` if checks still pass, but `xpAwarded = 0`.

#### `POST /missions/{mission_id}/reset`

Purpose: remove mission-owned resources and reset practice state.

Request body:

```json
{
  "mode": "practice"
}
```

Allowed `mode` values:

- `practice`: remove resources but keep completion and XP.
- `restart`: remove resources and set progress to `available` unless already locked by prerequisites.

Response `200`:

```json
{
  "missionId": "s3-first-bucket",
  "status": "completed",
  "resourcesRemoved": [
    "s3://starter-bucket/hello.txt",
    "s3://starter-bucket"
  ]
}
```

Behavior:

- Reset is idempotent.
- Missing resources do not cause failure.
- Reset must only target resources listed in the mission's `ownedResources`.
- Completed missions keep historical XP in `practice` mode.
- `practice` mode keeps completed missions in `completed` status.
- `restart` mode returns `available` for missions whose prerequisites are still met.

#### `GET /profile`

Purpose: return local learner profile.

Response `200`:

```json
{
  "profile": {
    "id": "local",
    "displayName": "Local Learner",
    "totalXp": 100,
    "badges": [
      {
        "id": "s3-starter",
        "title": "S3 Starter",
        "awardedAt": "2026-05-23T13:55:00Z"
      }
    ],
    "completedMissionIds": ["s3-first-bucket"]
  }
}
```

The MVP supports exactly one local profile with `id = "local"`.

### Status Codes

| Condition | Status |
| --- | --- |
| Successful request | `200` |
| Invalid request body | `422` |
| Mission not found | `404` |
| Mission locked | `409` |
| Mission not started | `409` |
| Floci unavailable | `503` |
| Local-only violation | process startup failure or `500` if detected at runtime |

### Database Schema

Use SQLite through SQLModel. Timestamps are UTC ISO-8601 strings in API responses and timezone-aware datetimes in Python.

#### `profiles`

| Column | Type | Constraints |
| --- | --- | --- |
| `id` | text | primary key, value `local` |
| `display_name` | text | not null, default `Local Learner` |
| `total_xp` | integer | not null, default `0` |
| `created_at` | datetime | not null |
| `updated_at` | datetime | not null |

#### `mission_progress`

| Column | Type | Constraints |
| --- | --- | --- |
| `profile_id` | text | primary key part, foreign key `profiles.id` |
| `mission_id` | text | primary key part |
| `status` | text | enum: `locked`, `available`, `started`, `completed` |
| `attempts` | integer | not null, default `0` |
| `xp_awarded` | integer | not null, default `0` |
| `started_at` | datetime nullable | |
| `completed_at` | datetime nullable | |
| `created_at` | datetime | not null |
| `updated_at` | datetime | not null |

Indexes:

- `idx_mission_progress_status`
- `idx_mission_progress_profile_status`

#### `validation_attempts`

| Column | Type | Constraints |
| --- | --- | --- |
| `id` | text | primary key, UUID |
| `profile_id` | text | not null |
| `mission_id` | text | not null |
| `attempt_number` | integer | not null |
| `passed` | boolean | not null |
| `checks_json` | text | not null JSON string |
| `created_at` | datetime | not null |

Unique constraint:

- `(profile_id, mission_id, attempt_number)`

#### `hint_usages`

| Column | Type | Constraints |
| --- | --- | --- |
| `profile_id` | text | primary key part |
| `mission_id` | text | primary key part |
| `hint_id` | text | primary key part |
| `penalty_xp` | integer | not null |
| `used_at` | datetime | not null |

#### `badges`

| Column | Type | Constraints |
| --- | --- | --- |
| `profile_id` | text | primary key part |
| `badge_id` | text | primary key part |
| `title` | text | not null |
| `awarded_at` | datetime | not null |

### Mission YAML Schema

Every `mission.yml` must conform to this shape:

```yaml
id: s3-first-bucket
order: 2
title: First Bucket
summary: Create your first object storage bucket.
difficulty: beginner
services:
  - s3
xp: 100
estimated_minutes: 10
prerequisites:
  - cloud-explorer
story: You are setting up storage for a small app.
learning_objectives:
  - Understand what an S3 bucket is
commands:
  - id: create-bucket
    label: Create bucket
    command: aws --endpoint-url http://floci:4566 s3 mb s3://starter-bucket
checks:
  - id: bucket-exists
    type: s3_bucket_exists
    bucket: starter-bucket
hints:
  - id: endpoint-url
    title: Check the endpoint
    text: Every AWS CLI command in this lab needs --endpoint-url.
    penalty_xp: 5
owned_resources:
  - type: s3_bucket
    bucket: starter-bucket
```

Required fields:

- `id`
- `order`
- `title`
- `summary`
- `difficulty`
- `services`
- `xp`
- `estimated_minutes`
- `prerequisites`
- `story`
- `learning_objectives`
- `commands`
- `checks`
- `hints`
- `owned_resources`

Field rules:

- `id` must match `^[a-z0-9]+(-[a-z0-9]+)*$`.
- `order` must be a positive integer and unique.
- `difficulty` must be `beginner`, `intermediate`, or `boss`.
- `services` values must be lowercase AWS service identifiers.
- `xp` must be an integer from `0` to `1000`.
- `estimated_minutes` must be an integer from `1` to `120`.
- `commands[].command` must include `--endpoint-url http://floci:4566` when it starts with `aws `.
- `checks[].id` must be unique within a mission.
- `hints[].id` must be unique within a mission.
- `owned_resources` must include every resource reset logic may delete.

### Validation Primitive Specifications

Each primitive returns:

```json
{
  "id": "bucket-exists",
  "type": "s3_bucket_exists",
  "passed": true,
  "message": "Bucket starter-bucket exists."
}
```

#### `s3_bucket_exists`

Input:

```yaml
id: bucket-exists
type: s3_bucket_exists
bucket: starter-bucket
```

Pass condition: `head_bucket(Bucket=bucket)` succeeds.

Fail condition: bucket does not exist or Floci returns not found.

Fail message:

```text
Bucket starter-bucket was not found.
```

#### `s3_object_exists`

Input:

```yaml
id: object-exists
type: s3_object_exists
bucket: starter-bucket
key: hello.txt
```

Pass condition: `head_object(Bucket=bucket, Key=key)` succeeds.

Fail message:

```text
Object hello.txt was not found in bucket starter-bucket.
```

#### `s3_object_body_equals`

Input:

```yaml
id: object-body
type: s3_object_body_equals
bucket: starter-bucket
key: hello.txt
value: Hello from local AWS
```

Pass condition: object body decoded as UTF-8 equals `value`.

Comparison rules:

- Trim one trailing newline from the actual body.
- Do not trim leading spaces.
- Do not perform case-insensitive comparison.

Fail message:

```text
Object hello.txt exists, but its content does not match the expected value.
```

#### `sqs_queue_exists`

Input:

```yaml
id: queue-exists
type: sqs_queue_exists
queue_name: starter-queue
```

Pass condition: `get_queue_url(QueueName=queue_name)` succeeds.

Fail message:

```text
Queue starter-queue was not found.
```

#### `sqs_message_available`

Input:

```yaml
id: message-available
type: sqs_message_available
queue_name: starter-queue
body: first local queue message
```

Pass condition: a received message body equals `body`.

Implementation rule: use `receive_message` with `MaxNumberOfMessages=10`, `WaitTimeSeconds=1`, and `VisibilityTimeout=0`. Do not delete the message during validation. `VisibilityTimeout=0` is required so repeated validation attempts do not hide the message.

Fail message:

```text
Queue starter-queue does not contain the expected message.
```

#### `runtime_floci_available`

Input:

```yaml
id: floci-available
type: runtime_floci_available
```

Pass condition: backend can complete a lightweight runtime check against Floci using the configured local endpoint.

Recommended implementation: call STS `get_caller_identity` through the shared AWS client factory. If Floci STS behavior differs during implementation, fall back to listing S3 buckets through the shared AWS client factory.

Fail message:

```text
The local AWS emulator is not reachable at http://floci:4566.
```

### Reset Primitive Specifications

Reset must only delete resources declared in `owned_resources`.

Supported MVP resources:

```yaml
- type: none
  reason: orientation mission has no owned resources
- type: s3_object
  bucket: starter-bucket
  key: hello.txt
- type: s3_bucket
  bucket: starter-bucket
- type: sqs_queue
  queue_name: starter-queue
```

Deletion order:

1. S3 objects
2. S3 buckets
3. SQS queues

Missing resources are treated as already reset.

`type: none` is allowed only when a mission has no resources to delete. It is a declaration that reset is a no-op, not permission to skip `owned_resources`.

### UI Component Contract

Required components:

| Component | Required States |
| --- | --- |
| `AppShell` | runtime healthy, runtime degraded, runtime offline |
| `RuntimeBanner` | hidden, warning, error |
| `MissionMap` | loading, loaded, empty, error |
| `MissionCard` | locked, available, started, completed |
| `MissionDetail` | loading, available, started, completed, error |
| `CommandBlock` | idle, copied |
| `HintPanel` | hidden, available, revealed |
| `ValidationPanel` | idle, validating, partial failure, success, runtime error |
| `ResetControl` | idle, confirming, resetting, reset success, reset failure |
| `XpSummary` | zero state, earned state |

UI behavior rules:

- Disable Start, Validate, Reset, and Hint actions when API is offline.
- Disable Validate while a validation request is in flight.
- Keep command blocks fixed-width enough that copy state does not resize them.
- Show check results in backend-provided order.
- A locked mission card must show its prerequisite mission title.
- A completed mission card must remain completed even after practice reset.
- No page should contain instructions to create an AWS account.

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
    command: aws --endpoint-url http://floci:4566 s3 mb s3://starter-bucket
  - label: Upload object
    command: aws --endpoint-url http://floci:4566 s3 cp hello.txt s3://starter-bucket/hello.txt

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
