# Infra Quest Implementation Plan

## Objective

Build a fully local, zero-cost, gamified AWS learning lab for beginners using Floci as the local AWS emulator. The first complete proof should allow a learner to open the browser, complete an S3 mission using AWS CLI commands pointed at Floci, click Validate, earn XP, reset the mission, and repeat the workflow.

## Success Criteria

The MVP is successful when this flow works on a clean machine with Docker:

```bash
docker compose up --build
```

Then:

```text
Open http://localhost:3000
Complete the S3 mission
Click Validate
See XP awarded
Reset the mission
Complete it again
```

No real AWS account, credentials, or cloud resources should be involved.

## Implementation Principles

- Prefer local-only behavior over flexibility.
- Pin every runtime and dependency version.
- Use lockfiles as required build inputs.
- Validate learner work from Floci state, not from user-submitted claims.
- Build one complete mission loop before expanding the curriculum.
- Keep the beginner UI direct and task-focused.

## Phase 1: Runtime Skeleton

### Deliverables

- `docker-compose.yml`
- Floci service pinned to `floci/floci:1.5.13`
- FastAPI service
- Next.js service
- initial repo structure
- `.env.example`
- `.gitignore`
- `README.md` quickstart
- basic `Makefile`

### Tasks

1. Create repository structure.
2. Add Docker Compose services for `floci`, `api`, and `web`.
3. Add `data/` folders to `.gitignore`.
4. Add FastAPI `/health` endpoint.
5. Add Next.js placeholder mission map page.
6. Add startup environment variables for fake AWS credentials.
7. Add backend startup guard for `AWS_ENDPOINT_URL`.

### Acceptance Checks

```bash
docker compose up --build
curl http://localhost:8000/health
curl http://localhost:3000
```

Backend must fail startup if `AWS_ENDPOINT_URL` is missing or points to real AWS.

## Phase 2: Reproducible Tooling

### Deliverables

- root `package.json` with `packageManager: bun@1.3.14`
- committed `bun.lock`
- web `package.json` with exact versions
- API `pyproject.toml`
- committed `uv.lock`
- pinned Dockerfiles
- `scripts/verify-local-only.sh`

### Frontend Versions

Use exact versions:

```json
{
  "next": "16.2.6",
  "react": "19.2.1",
  "react-dom": "19.2.1",
  "typescript": "6.0.3"
}
```

Also pin exact versions for:

```text
tailwindcss
lucide-react
zod
clsx
tailwind-merge
eslint
prettier
```

### Backend Versions

Use exact versions:

```text
python==3.14.5
fastapi==0.136.1
```

Also pin exact versions for:

```text
uvicorn[standard]
boto3
botocore
sqlmodel
pydantic
pyyaml
pytest
ruff
```

### Acceptance Checks

```bash
bun install --frozen-lockfile
cd apps/api && uv sync --frozen
./scripts/verify-local-only.sh
```

The verification script should fail if it finds:

- Docker `latest` tags
- `amazonaws.com`
- real-looking AWS keys
- unpinned dependency versions
- frontend dependency ranges using `^` or `~`

## Phase 3: Backend Mission Engine

### Deliverables

- mission YAML schema
- mission loader
- SQLite models
- profile model
- mission progress model
- mission API routes
- validation result schema

### Tasks

1. Define mission schema in Python.
2. Read all `mission.yml` files from `MISSIONS_DIR`.
3. Add SQLite database connection.
4. Create profile table.
5. Create mission progress table.
6. Add mission list endpoint.
7. Add mission detail endpoint.
8. Add mission start endpoint.
9. Add mission reset endpoint.
10. Add mission validate endpoint stub.

### API Endpoints

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

### Acceptance Checks

```bash
curl http://localhost:8000/missions
curl http://localhost:8000/profile
```

The API should load missions from disk and persist learner progress across API restarts.

## Phase 4: AWS Client and Local Safety

### Deliverables

- `aws_client.py`
- boto3 client factory
- local-only endpoint validation
- Floci health/status check
- backend runtime status endpoint

### Tasks

1. Build a boto3 client factory that always uses `AWS_ENDPOINT_URL`.
2. Force fake credentials in local development.
3. Add guardrails against real AWS endpoints.
4. Add `/runtime/status` endpoint.
5. Verify the backend can call Floci S3.

### Acceptance Checks

Backend should be able to:

```text
create a temporary S3 bucket
list buckets
delete the bucket
```

All calls must go through:

```text
http://floci:4566
```

## Phase 5: First S3 Mission

### Deliverables

- `missions/s3-first-bucket/mission.yml`
- S3 validation primitives
- S3 seed script
- S3 reset script
- mission validation implementation

### Mission Objective

Learner creates a bucket and uploads a file:

```bash
echo "Hello from local AWS" > hello.txt
aws --endpoint-url http://localhost:4566 s3 mb s3://starter-bucket
aws --endpoint-url http://localhost:4566 s3 cp hello.txt s3://starter-bucket/hello.txt
```

### Checks

- bucket `starter-bucket` exists
- object `hello.txt` exists
- object body equals `Hello from local AWS`

### Acceptance Checks

1. Start mission from the API.
2. Run the learner commands.
3. Call validate endpoint.
4. Receive `passed: true`.
5. Confirm XP is awarded once.
6. Reset the mission.
7. Confirm bucket/object are removed.

## Phase 6: Frontend MVP

### Deliverables

- mission map page
- mission detail page
- API client
- validation result panel
- reset button
- XP display
- basic profile display
- runtime status panel

### Tasks

1. Build mission map from `GET /missions`.
2. Build mission detail page from `GET /missions/{id}`.
3. Render command snippets with copy buttons.
4. Add Validate button.
5. Add Reset button.
6. Show check-by-check validation results.
7. Show XP and completion state.
8. Show Floci/API status in settings.

### Acceptance Checks

A beginner can complete the S3 mission without reading backend logs.

The UI should clearly show:

- what to do
- which commands to run
- what passed
- what failed
- how to reset

## Phase 7: SQS Mission

### Deliverables

- `missions/sqs-first-message/mission.yml`
- SQS validation primitives
- SQS reset logic
- frontend mission content

### Mission Objective

Learner creates an SQS queue, sends a message, receives it, and understands queue semantics.

Example commands:

```bash
aws --endpoint-url http://localhost:4566 sqs create-queue --queue-name starter-queue
aws --endpoint-url http://localhost:4566 sqs send-message \
  --queue-url http://localhost:4566/000000000000/starter-queue \
  --message-body "first local queue message"
```

### Checks

- queue exists
- expected message can be observed or was sent
- mission state can be reset cleanly

### Acceptance Checks

Learner can complete the mission from the browser and get XP.

## Phase 8: Gamification Layer

### Deliverables

- XP system
- badge system
- hint tracking
- mission unlock rules
- attempt history

### Tasks

1. Award XP only on first completion.
2. Track validation attempts.
3. Track hints used.
4. Apply hint XP penalties.
5. Add service badges.
6. Unlock missions sequentially.
7. Add boss mission placeholder.

### Acceptance Checks

- Completed missions stay completed after restart.
- XP is not duplicated by repeated validation.
- Hints reduce possible XP.
- Badges appear after required completions.

## Phase 9: DynamoDB Mission

### Deliverables

- `missions/dynamodb-first-table/mission.yml`
- DynamoDB validation primitives
- reset logic
- UI content

### Mission Objective

Learner creates a table, inserts an item, and reads it back.

### Checks

- table exists
- key schema is correct
- item exists
- item has expected attributes

### Acceptance Checks

Learner completes the mission using AWS CLI commands against Floci.

## Phase 10: Lambda and API Gateway Missions

### Deliverables

- Lambda mission
- API Gateway mission
- validation primitives
- seed/reset logic
- documentation for local invocation

### Tasks

1. Validate Floci Lambda behavior in a technical spike.
2. Add a simple Lambda function mission.
3. Add API Gateway route mission.
4. Validate function invocation.
5. Validate HTTP route behavior.

### Acceptance Checks

Learner can invoke a local Lambda and then trigger it through an HTTP route.

If Floci behavior differs from AWS, document the local behavior clearly in mission copy.

## Phase 11: Serverless Boss Mission

### Deliverables

- combined mission using API Gateway, Lambda, DynamoDB, and SQS
- multi-service validator
- richer mission map state

### Mission Objective

Build a small local serverless workflow:

```text
HTTP request
  -> API Gateway
  -> Lambda
  -> DynamoDB write
  -> SQS message
```

### Checks

- API route exists
- Lambda exists
- DynamoDB table exists
- SQS queue exists
- request writes expected item
- request sends expected message

### Acceptance Checks

Learner completes a multi-service workflow locally and earns a larger XP reward.

## Phase 12: Reproducibility Hardening

### Deliverables

- digest-pinned Floci image
- final lockfiles
- smoke test
- `make verify`
- README reproducibility section

### Tasks

1. Resolve Floci image digest.
2. Replace tag-only image with digest-pinned image.
3. Add smoke test for web, API, and Floci.
4. Add dependency pinning checks.
5. Add clean-machine setup docs.

### Acceptance Checks

```bash
make verify
```

passes on a clean machine with Docker installed.

## Phase 13: Documentation

### Deliverables

- README quickstart
- learner setup notes
- contributor guide
- mission authoring guide
- troubleshooting guide

### README Must Include

```bash
docker compose up --build
```

Then:

```text
Open http://localhost:3000
```

And this warning:

```text
This project does not use real AWS.
Do not configure real AWS credentials.
All commands must use --endpoint-url http://localhost:4566.
```

### Mission Authoring Guide Must Include

- folder structure
- `mission.yml` schema
- seed/reset conventions
- validator conventions
- XP and hint rules
- local-only safety requirements

## Suggested Build Order

1. Runtime skeleton
2. Reproducible tooling
3. Backend mission engine
4. AWS client and local safety
5. First S3 mission
6. Frontend MVP
7. SQS mission
8. Gamification layer
9. DynamoDB mission
10. Lambda and API Gateway missions
11. Serverless boss mission
12. Reproducibility hardening
13. Documentation

## MVP Cut Line

The smallest useful MVP includes:

- Docker Compose
- Floci
- FastAPI backend
- Next.js frontend
- SQLite progress
- S3 mission
- SQS mission
- XP
- reset
- local-only guardrails
- smoke test

Everything after that is curriculum expansion and polish.

## Open Technical Spikes

Run these before committing to the advanced curriculum:

1. Confirm Floci Lambda deployment and invocation behavior.
2. Confirm Floci API Gateway routing behavior.
3. Confirm Floci SNS to SQS subscription behavior.
4. Confirm DynamoDB table and item behavior through boto3.
5. Confirm Bun-built Next.js output runs cleanly under Node.js `24.16.0`.

## Final Gate

Before calling the MVP complete:

```bash
docker compose down
rm -rf data
docker compose up --build
make verify
```

Then manually complete:

1. S3 mission
2. SQS mission
3. reset S3 mission
4. complete S3 mission again

The final result should be a beginner-friendly local lab that teaches real AWS concepts without real AWS cost.
