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
5. Add a minimal Next.js mission map page that calls `GET /missions` when the API is available and renders loading, error, empty, and loaded states.
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
tailwindcss==4.1.13
@tailwindcss/postcss==4.1.13
lucide-react==1.16.0
zod==4.1.5
clsx==2.1.1
tailwind-merge==3.3.1
eslint==9.35.0
prettier==3.6.2
```

### Backend Versions

Use exact versions:

```text
python==3.14.5
fastapi==0.136.1
```

Also pin exact versions for:

```text
uvicorn[standard]==0.47.0
boto3==1.43.12
botocore==1.43.12
sqlmodel==0.0.38
pydantic==2.13.4
pyyaml==6.0.3
pytest==9.0.3
ruff==0.15.14
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
7. Add a disabled boss mission card that clearly states the required prerequisite missions and does not expose a detail route until the boss mission YAML exists.

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

## Agent Story Catalog

This section breaks the build into small, independently verifiable implementation stories. An agent should complete stories in order unless a story explicitly says it can run in parallel.

### Story RUNTIME-001: Initialize Repository Skeleton

Objective: create the monorepo directories and baseline files.

Files:

```text
.gitignore
README.md
Makefile
docker-compose.yml
apps/web/
apps/api/
missions/
scripts/
```

Acceptance criteria:

- `data/`, `.venv/`, `.next/`, `node_modules/`, `.pytest_cache/`, and `.ruff_cache/` are gitignored.
- `README.md` starts with `docker compose up --build`.
- `docker-compose.yml` defines `floci`, `api`, and `web` services.
- No Docker image uses `latest`.

Tests:

- `git status --short` shows only intended files.
- `rg ':latest|amazonaws.com'` does not find unsafe runtime config except denylist documentation.

### Story RUNTIME-002: Add Docker Compose Runtime

Objective: make all services start locally.

Files:

```text
docker-compose.yml
apps/api/Dockerfile
apps/web/Dockerfile
```

Acceptance criteria:

- Floci uses `floci/floci:1.5.13`.
- API exposes port `8000`.
- Web exposes port `3000`.
- Floci exposes port `4566`.
- API gets `AWS_ENDPOINT_URL=http://floci:4566`.
- API gets fake credentials only.

Tests:

```bash
docker compose config
docker compose up --build
```

Expected:

- Compose config succeeds.
- All services reach running or healthy state.

### Story API-001: Add FastAPI App Shell

Objective: create a minimal API service.

Files:

```text
apps/api/pyproject.toml
apps/api/app/main.py
apps/api/app/routes/health.py
```

Acceptance criteria:

- Python version is pinned to `3.14.5`.
- Dependencies match the pinned backend package list.
- `GET /health` returns the exact contract from `INFRA_QUEST_SPEC.md`.

Tests:

```bash
cd apps/api && uv run pytest
curl http://localhost:8000/health
```

### Story API-002: Enforce Local-Only Configuration

Objective: prevent real AWS access.

Files:

```text
apps/api/app/config.py
apps/api/tests/test_config.py
```

Acceptance criteria:

- Missing `AWS_ENDPOINT_URL` fails app startup.
- Endpoints containing `amazonaws.com` fail app startup.
- Endpoints starting with `https://aws` fail app startup.
- Real-looking access keys fail validation.
- Fake credentials `test/test` pass.

Tests:

- unit tests for every allowed and rejected config.
- process startup test with unsafe endpoint.

### Story API-003: Add Database Models

Objective: create SQLite schema for learner progress.

Files:

```text
apps/api/app/db.py
apps/api/app/models.py
apps/api/tests/test_db.py
```

Acceptance criteria:

- Tables match the schema in `INFRA_QUEST_SPEC.md`.
- API creates the local profile automatically with `id=local`.
- Missing DB file is created automatically.
- Progress persists across API restart.

Tests:

- table creation test
- default profile test
- persistence test using a temp SQLite file

### Story API-004: Add Mission Loader

Objective: read and validate mission YAML files.

Files:

```text
apps/api/app/mission_loader.py
apps/api/tests/test_mission_loader.py
missions/cloud-explorer/mission.yml
```

Acceptance criteria:

- Loader validates required fields.
- Duplicate mission IDs fail load.
- Duplicate order values fail load.
- Invalid command missing endpoint fails load.
- Invalid check type fails load.
- Missions sort by `order`.

Tests:

- valid fixture loads
- missing required field fails
- duplicate ID fails
- command without endpoint fails

### Story API-005: Add Mission List and Detail Routes

Objective: expose mission content to the frontend.

Files:

```text
apps/api/app/routes/missions.py
apps/api/tests/test_mission_routes.py
```

Acceptance criteria:

- `GET /missions` returns exact response shape.
- `GET /missions/{id}` returns exact response shape.
- Unknown mission returns `404 MISSION_NOT_FOUND`.
- Hint text is hidden until used.

Tests:

- snapshot-style JSON shape tests
- unknown mission test
- hint text hidden test

### Story API-006: Add Mission State Transitions

Objective: implement start, unlock, and progress rules.

Files:

```text
apps/api/app/services/progress.py
apps/api/app/routes/missions.py
apps/api/tests/test_progress.py
```

Acceptance criteria:

- First mission is available by default.
- Missions with unmet prerequisites are locked.
- `POST /start` transitions available to started.
- Starting started mission is idempotent.
- Starting locked mission returns `409 MISSION_LOCKED`.
- Starting completed mission keeps completed status.

Tests:

- state transition tests for each allowed and rejected path.

### Story API-007: Add AWS Client Factory

Objective: create boto3 clients that can only talk to Floci.

Files:

```text
apps/api/app/aws_client.py
apps/api/tests/test_aws_client.py
```

Acceptance criteria:

- Client factory always receives `endpoint_url`.
- Region defaults to `us-east-1`.
- Credentials are fake.
- No code path creates a default boto3 client without endpoint.

Tests:

- mock boto3 client creation and assert endpoint.
- scan test for unsafe `boto3.client(` usage outside factory.

### Story API-008: Add Runtime Status Route

Objective: report API, DB, Floci, and local-only health.

Files:

```text
apps/api/app/routes/runtime.py
apps/api/tests/test_runtime.py
```

Acceptance criteria:

- `GET /runtime/status` returns exact response shape.
- Floci offline returns `200` with `floci.status=offline`.
- DB unavailable reports `database.status=offline`.
- Local-only status is always included.

Tests:

- healthy status test
- mocked Floci failure test
- mocked DB failure test

### Story API-009: Add S3 Validation Primitives

Objective: validate S3 bucket and object checks.

Files:

```text
apps/api/app/validators/s3.py
apps/api/tests/test_validators_s3.py
```

Acceptance criteria:

- `s3_bucket_exists` uses `head_bucket`.
- `s3_object_exists` uses `head_object`.
- `s3_object_body_equals` compares UTF-8 body with one trailing newline trimmed.
- Fail messages match the spec.

Tests:

- pass/fail tests for each primitive using botocore stubs or local Floci integration.

### Story API-010: Add SQS Validation Primitives

Objective: validate SQS queue and message checks.

Files:

```text
apps/api/app/validators/sqs.py
apps/api/tests/test_validators_sqs.py
```

Acceptance criteria:

- `sqs_queue_exists` uses `get_queue_url`.
- `sqs_message_available` receives with `VisibilityTimeout=0` and does not delete messages.
- Fail messages match the spec.

Tests:

- queue exists pass/fail
- expected message pass/fail
- validation does not delete received message
- repeated validation can still observe the same message

### Story API-010A: Add Runtime Validation Primitive

Objective: support non-resource orientation missions.

Files:

```text
apps/api/app/validators/runtime.py
apps/api/tests/test_validators_runtime.py
```

Acceptance criteria:

- `runtime_floci_available` uses the shared AWS client factory.
- The primitive passes when Floci is reachable through `AWS_ENDPOINT_URL`.
- The primitive fails with the exact message from the spec when Floci is unavailable.
- The primitive never attempts real AWS endpoints.

Tests:

- reachable runtime pass case.
- unreachable runtime fail case.
- mocked AWS client verifies configured endpoint is used.

### Story API-011: Add Validation Endpoint

Objective: run mission checks and persist attempts.

Files:

```text
apps/api/app/services/validation.py
apps/api/app/routes/missions.py
apps/api/tests/test_validation_endpoint.py
```

Acceptance criteria:

- Validating available mission returns `409 MISSION_NOT_STARTED`.
- Partial failure records attempt and awards no XP.
- Success completes mission and awards XP once.
- Revalidation does not duplicate XP.
- Check order matches YAML order.
- Floci unavailable returns `503 FLOCI_UNAVAILABLE`.

Tests:

- exact JSON response tests for partial and success cases.
- XP idempotency test.

### Story API-012: Add Reset Endpoint

Objective: remove mission-owned resources safely.

Files:

```text
apps/api/app/services/reset.py
apps/api/app/routes/missions.py
apps/api/tests/test_reset.py
```

Acceptance criteria:

- Reset deletes only `owned_resources`.
- Reset is idempotent.
- Missing resources do not fail reset.
- `practice` mode preserves XP and completion.
- `restart` mode sets status to available when prerequisites are met.
- MVP reset supports `none`, `s3_object`, `s3_bucket`, and `sqs_queue`.

Tests:

- missing resource reset succeeds.
- completed mission practice reset keeps XP.
- reset never deletes undeclared resource fixture.

### Story API-012A: Add Advanced Reset Resources

Objective: support reset for all advanced mission resources.

Files:

```text
apps/api/app/services/reset.py
apps/api/tests/test_reset_advanced.py
```

Required owned resource types:

```text
sns_topic
dynamodb_table
lambda_function
apigateway_api
```

Deletion order:

1. API Gateway APIs
2. Lambda functions
3. SNS topics
4. SQS queues
5. DynamoDB tables
6. S3 objects
7. S3 buckets

Acceptance criteria:

- `sns_topic` reset deletes topic by exact topic name.
- `dynamodb_table` reset deletes table by exact table name and treats missing table as success.
- `lambda_function` reset deletes function by exact function name.
- `apigateway_api` reset deletes API by exact API name.
- Reset logs or returns every deleted resource identifier.
- Reset never deletes resources that are not declared in `owned_resources`.

Tests:

- each advanced resource reset succeeds when resource exists.
- each advanced resource reset succeeds when resource is missing.
- reset ordering prevents dependency failures for API Gateway and Lambda.
- undeclared resource fixture survives reset.

### Story API-013: Add Hint Endpoint

Objective: reveal hints and apply penalties once.

Files:

```text
apps/api/app/services/hints.py
apps/api/app/routes/missions.py
apps/api/tests/test_hints.py
```

Acceptance criteria:

- Unused hint can be revealed.
- Reusing hint is idempotent.
- Penalty applies once.
- Possible XP cannot go below zero.
- Hint after completion does not change awarded XP.

Tests:

- first use
- repeated use
- completed mission use

### Story API-014: Add SNS Validation Primitives

Objective: validate SNS topics and SQS subscriptions for fanout missions.

Files:

```text
apps/api/app/validators/sns.py
apps/api/tests/test_validators_sns.py
```

Required check types:

```text
sns_topic_exists
sns_subscription_exists
sns_to_sqs_delivery
```

Acceptance criteria:

- `sns_topic_exists` resolves topics by exact `topic_name`.
- `sns_subscription_exists` verifies a subscription from topic to queue endpoint.
- `sns_to_sqs_delivery` publishes a deterministic message to the topic and verifies the message appears in the target SQS queue.
- Validation uses only the shared AWS client factory.
- Message verification uses `VisibilityTimeout=0` and does not delete messages.
- Fail messages name the missing topic, subscription, or delivered message.

Test fixtures:

```yaml
checks:
  - id: topic-exists
    type: sns_topic_exists
    topic_name: starter-topic
  - id: subscription-exists
    type: sns_subscription_exists
    topic_name: starter-topic
    queue_name: starter-fanout-queue
  - id: fanout-message
    type: sns_to_sqs_delivery
    topic_name: starter-topic
    queue_name: starter-fanout-queue
    body: local fanout works
```

Tests:

- topic exists pass/fail.
- subscription exists pass/fail.
- publish-to-SQS delivery pass/fail.
- repeated validation can observe or republish deterministic test message without destructive side effects.

### Story API-015: Add DynamoDB Validation Primitives

Objective: validate DynamoDB table schema and item content.

Files:

```text
apps/api/app/validators/dynamodb.py
apps/api/tests/test_validators_dynamodb.py
```

Required check types:

```text
dynamodb_table_exists
dynamodb_key_schema_equals
dynamodb_item_exists
dynamodb_item_attribute_equals
```

Acceptance criteria:

- `dynamodb_table_exists` uses `describe_table`.
- `dynamodb_key_schema_equals` compares partition key and optional sort key exactly.
- `dynamodb_item_exists` uses `get_item` with the configured key.
- `dynamodb_item_attribute_equals` compares expected scalar string/number/bool attributes.
- Validation uses only the shared AWS client factory.
- Fail messages name the missing table, key mismatch, missing item, or mismatched attribute.

Test fixtures:

```yaml
checks:
  - id: table-exists
    type: dynamodb_table_exists
    table_name: starter-table
  - id: key-schema
    type: dynamodb_key_schema_equals
    table_name: starter-table
    partition_key:
      name: pk
      type: S
  - id: item-exists
    type: dynamodb_item_exists
    table_name: starter-table
    key:
      pk:
        S: learner#1
  - id: item-name
    type: dynamodb_item_attribute_equals
    table_name: starter-table
    key:
      pk:
        S: learner#1
    attribute: name
    expected:
      S: Local Learner
```

Tests:

- table exists pass/fail.
- key schema pass/fail.
- item exists pass/fail.
- item attribute pass/fail.
- numeric and boolean attribute comparison tests if supported by mission fixtures.

### Story API-016: Add Lambda Validation Primitives

Objective: validate local Lambda function creation and invocation.

Files:

```text
apps/api/app/validators/lambda.py
apps/api/tests/test_validators_lambda.py
```

Required check types:

```text
lambda_function_exists
lambda_invoke_returns
```

Acceptance criteria:

- `lambda_function_exists` uses `get_function`.
- `lambda_invoke_returns` invokes the function with a deterministic JSON payload and compares response JSON.
- Validation uses only the shared AWS client factory.
- Payload and expected response are defined in mission YAML.
- Response comparison ignores JSON object key order.
- Fail messages distinguish missing function, invocation failure, invalid JSON, and response mismatch.

Test fixtures:

```yaml
checks:
  - id: function-exists
    type: lambda_function_exists
    function_name: starter-function
  - id: invoke-result
    type: lambda_invoke_returns
    function_name: starter-function
    payload:
      name: Local Learner
    expected:
      message: Hello, Local Learner
```

Tests:

- function exists pass/fail.
- invoke response pass/fail.
- invalid JSON response returns clear failed check.
- validation does not require real AWS IAM credentials.

### Story API-017: Add API Gateway Validation Primitives

Objective: validate HTTP route wiring to a local Lambda-backed endpoint.

Files:

```text
apps/api/app/validators/apigateway.py
apps/api/tests/test_validators_apigateway.py
```

Required check types:

```text
apigateway_route_exists
apigateway_http_returns
```

Acceptance criteria:

- `apigateway_route_exists` verifies an HTTP API route or REST route by configured API name and route key/path.
- `apigateway_http_returns` sends an HTTP request to the local API Gateway endpoint and compares status code and JSON response.
- Validation must use local Floci endpoint discovery or a mission-provided local URL.
- Validation must not call real AWS API Gateway URLs.
- Fail messages distinguish missing API, missing route, HTTP failure, status mismatch, and body mismatch.

Test fixtures:

```yaml
checks:
  - id: route-exists
    type: apigateway_route_exists
    api_name: starter-api
    route: GET /hello
  - id: http-response
    type: apigateway_http_returns
    api_name: starter-api
    route: GET /hello
    expected_status: 200
    expected_json:
      message: Hello from local API
```

Tests:

- route exists pass/fail.
- HTTP response pass/fail.
- response body comparison ignores JSON object key order.
- validator rejects non-local URLs.

### Story API-018: Add Boss Mission Multi-Service Checks

Objective: validate a full local serverless workflow.

Files:

```text
apps/api/app/validators/workflow.py
apps/api/tests/test_validators_workflow.py
```

Required check types:

```text
workflow_http_writes_dynamodb
workflow_http_sends_sqs
```

Acceptance criteria:

- `workflow_http_writes_dynamodb` sends a deterministic HTTP request and verifies a DynamoDB item exists afterward.
- `workflow_http_sends_sqs` sends a deterministic HTTP request and verifies an SQS message exists afterward.
- Validators reuse existing API Gateway, DynamoDB, and SQS helpers where possible.
- Repeated validation uses deterministic IDs so duplicate requests do not create ambiguous results.
- Fail messages identify which workflow step failed.

Test fixtures:

```yaml
checks:
  - id: http-writes-item
    type: workflow_http_writes_dynamodb
    api_name: starter-api
    route: POST /orders
    request_json:
      orderId: order-001
      item: notebook
    table_name: orders-table
    key:
      pk:
        S: order#order-001
  - id: http-sends-message
    type: workflow_http_sends_sqs
    api_name: starter-api
    route: POST /orders
    request_json:
      orderId: order-001
      item: notebook
    queue_name: orders-queue
    expected_body_contains: order-001
```

Tests:

- workflow DynamoDB write pass/fail.
- workflow SQS message pass/fail.
- repeated validation is deterministic.
- partial workflow failure returns check-level failure without awarding XP.

### Story MISSION-001: Author Cloud Explorer Mission

Objective: create the first non-destructive orientation mission.

Files:

```text
missions/cloud-explorer/mission.yml
```

Acceptance criteria:

- Mission teaches endpoint, region, fake credentials, and local-only model.
- Mission uses no destructive resources.
- Mission is order `1`.
- Mission is available by default.
- Mission uses `runtime_floci_available` as its validation check.
- Mission declares `owned_resources` with `type: none`.

Tests:

- mission loader accepts file.
- mission appears first in `GET /missions`.

### Story MISSION-002: Author S3 First Bucket Mission

Objective: create the first real resource mission.

Files:

```text
missions/s3-first-bucket/mission.yml
```

Acceptance criteria:

- Mission checks bucket, object, and object body.
- Commands are copyable and endpoint-safe.
- `owned_resources` includes object and bucket.
- Prerequisite is `cloud-explorer`.

Tests:

- loader accepts mission.
- validation passes after documented commands.
- reset removes object and bucket.

### Story MISSION-003: Author SQS First Message Mission

Objective: create the second real resource mission.

Files:

```text
missions/sqs-first-message/mission.yml
```

Acceptance criteria:

- Mission checks queue and expected message.
- Commands are endpoint-safe.
- `owned_resources` includes queue.
- Prerequisite is `s3-first-bucket`.

Tests:

- loader accepts mission.
- validation passes after documented commands.
- reset removes queue.

### Story MISSION-004: Author SNS Fanout Mission

Objective: teach topic-to-queue publish/subscribe flow.

Files:

```text
missions/sns-fanout/mission.yml
```

Mission metadata:

```yaml
id: sns-fanout
order: 4
title: Publish and Subscribe
difficulty: beginner
services: [sns, sqs]
xp: 150
estimated_minutes: 15
prerequisites: [sqs-first-message]
```

Required learner commands:

```bash
aws --endpoint-url http://localhost:4566 sns create-topic --name starter-topic
aws --endpoint-url http://localhost:4566 sqs create-queue --queue-name starter-fanout-queue
aws --endpoint-url http://localhost:4566 sns subscribe --topic-arn arn:aws:sns:us-east-1:000000000000:starter-topic --protocol sqs --notification-endpoint arn:aws:sqs:us-east-1:000000000000:starter-fanout-queue
aws --endpoint-url http://localhost:4566 sns publish --topic-arn arn:aws:sns:us-east-1:000000000000:starter-topic --message "local fanout works"
```

Required checks:

```yaml
checks:
  - id: topic-exists
    type: sns_topic_exists
    topic_name: starter-topic
  - id: queue-exists
    type: sqs_queue_exists
    queue_name: starter-fanout-queue
  - id: subscription-exists
    type: sns_subscription_exists
    topic_name: starter-topic
    queue_name: starter-fanout-queue
  - id: fanout-message
    type: sns_to_sqs_delivery
    topic_name: starter-topic
    queue_name: starter-fanout-queue
    body: local fanout works
```

Required `owned_resources`:

```yaml
owned_resources:
  - type: sns_topic
    topic_name: starter-topic
  - type: sqs_queue
    queue_name: starter-fanout-queue
```

Acceptance criteria:

- Mission explains topic, subscription, and fanout.
- All commands include local endpoint.
- Mission validates topic, queue, subscription, and message delivery.
- Reset deletes topic and queue idempotently.

Tests:

- loader accepts mission.
- validation passes after documented commands.
- validation fails clearly when subscription is missing.
- reset removes topic and queue.

### Story MISSION-005: Author DynamoDB Table Mission

Objective: teach local key-value table creation and item retrieval.

Files:

```text
missions/dynamodb-first-table/mission.yml
```

Mission metadata:

```yaml
id: dynamodb-first-table
order: 5
title: Key-Value Store
difficulty: beginner
services: [dynamodb]
xp: 150
estimated_minutes: 15
prerequisites: [sns-fanout]
```

Required learner commands:

```bash
aws --endpoint-url http://localhost:4566 dynamodb create-table --table-name starter-table --attribute-definitions AttributeName=pk,AttributeType=S --key-schema AttributeName=pk,KeyType=HASH --billing-mode PAY_PER_REQUEST
aws --endpoint-url http://localhost:4566 dynamodb put-item --table-name starter-table --item '{"pk":{"S":"learner#1"},"name":{"S":"Local Learner"},"level":{"N":"1"}}'
aws --endpoint-url http://localhost:4566 dynamodb get-item --table-name starter-table --key '{"pk":{"S":"learner#1"}}'
```

Required checks:

```yaml
checks:
  - id: table-exists
    type: dynamodb_table_exists
    table_name: starter-table
  - id: key-schema
    type: dynamodb_key_schema_equals
    table_name: starter-table
    partition_key:
      name: pk
      type: S
  - id: item-exists
    type: dynamodb_item_exists
    table_name: starter-table
    key:
      pk:
        S: learner#1
  - id: item-name
    type: dynamodb_item_attribute_equals
    table_name: starter-table
    key:
      pk:
        S: learner#1
    attribute: name
    expected:
      S: Local Learner
```

Required `owned_resources`:

```yaml
owned_resources:
  - type: dynamodb_table
    table_name: starter-table
```

Acceptance criteria:

- Mission explains table, partition key, item, and attribute.
- Validation catches wrong table name.
- Validation catches wrong key schema.
- Validation catches missing or wrong item attribute.
- Reset deletes table idempotently.

Tests:

- loader accepts mission.
- validation passes after documented commands.
- validation fails for wrong attribute value.
- reset removes table.

### Story MISSION-006: Author Lambda Function Mission

Objective: teach local function deployment and invocation.

Files:

```text
missions/lambda-tiny-function/mission.yml
missions/lambda-tiny-function/function/index.mjs
```

Mission metadata:

```yaml
id: lambda-tiny-function
order: 6
title: Tiny Function
difficulty: beginner
services: [lambda]
xp: 175
estimated_minutes: 20
prerequisites: [dynamodb-first-table]
```

Required function code:

```javascript
export const handler = async (event) => {
  return {
    message: `Hello, ${event.name}`
  };
};
```

Required learner commands:

```bash
cd missions/lambda-tiny-function/function
zip -r function.zip index.mjs
aws --endpoint-url http://localhost:4566 lambda create-function --function-name starter-function --runtime nodejs22.x --handler index.handler --zip-file fileb://function.zip --role arn:aws:iam::000000000000:role/local-lambda-role
aws --endpoint-url http://localhost:4566 lambda invoke --function-name starter-function --payload '{"name":"Local Learner"}' response.json
cat response.json
```

Required checks:

```yaml
checks:
  - id: function-exists
    type: lambda_function_exists
    function_name: starter-function
  - id: invoke-result
    type: lambda_invoke_returns
    function_name: starter-function
    payload:
      name: Local Learner
    expected:
      message: Hello, Local Learner
```

Required `owned_resources`:

```yaml
owned_resources:
  - type: lambda_function
    function_name: starter-function
```

Acceptance criteria:

- Mission includes function source in repo.
- Mission teaches runtime, handler, payload, and invocation.
- Validation confirms function exists and response matches expected JSON.
- Reset deletes Lambda function idempotently.

Tests:

- loader accepts mission.
- validation passes after documented commands.
- validation fails for wrong function response.
- reset removes function.

### Story MISSION-007: Author API Gateway HTTP Mission

Objective: teach exposing a local Lambda through an HTTP endpoint.

Files:

```text
missions/apigateway-http-trigger/mission.yml
missions/apigateway-http-trigger/function/index.mjs
```

Mission metadata:

```yaml
id: apigateway-http-trigger
order: 7
title: HTTP Trigger
difficulty: beginner
services: [apigateway, lambda]
xp: 200
estimated_minutes: 25
prerequisites: [lambda-tiny-function]
```

Required function behavior:

```javascript
export const handler = async () => {
  return {
    statusCode: 200,
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ message: "Hello from local API" })
  };
};
```

Required learner flow:

1. Create Lambda function `starter-api-function`.
2. Create API Gateway API named `starter-api`.
3. Add route `GET /hello`.
4. Integrate route with Lambda.
5. Call local API endpoint.

The exact CLI commands must be verified against Floci during implementation and then committed into `mission.yml`. If Floci's API Gateway CLI compatibility differs from AWS CLI, use the Floci-supported command sequence and document the difference in mission copy.

Required checks:

```yaml
checks:
  - id: function-exists
    type: lambda_function_exists
    function_name: starter-api-function
  - id: route-exists
    type: apigateway_route_exists
    api_name: starter-api
    route: GET /hello
  - id: http-response
    type: apigateway_http_returns
    api_name: starter-api
    route: GET /hello
    expected_status: 200
    expected_json:
      message: Hello from local API
```

Required `owned_resources`:

```yaml
owned_resources:
  - type: apigateway_api
    api_name: starter-api
  - type: lambda_function
    function_name: starter-api-function
```

Acceptance criteria:

- Mission teaches route, integration, and HTTP response.
- Commands are verified against Floci before marking story complete.
- Validation confirms route exists and HTTP response matches.
- Reset deletes API and function idempotently.

Tests:

- loader accepts mission.
- validation passes after documented commands.
- validation fails when route is missing.
- reset removes API and Lambda function.

### Story MISSION-008: Author Serverless Boss Mission

Objective: combine API Gateway, Lambda, DynamoDB, and SQS into one local workflow.

Files:

```text
missions/serverless-boss/mission.yml
missions/serverless-boss/function/index.mjs
```

Mission metadata:

```yaml
id: serverless-boss
order: 8
title: Serverless Boss Mission
difficulty: boss
services: [apigateway, lambda, dynamodb, sqs]
xp: 300
estimated_minutes: 35
prerequisites: [apigateway-http-trigger]
```

Required workflow:

```text
POST /orders
  -> API Gateway
  -> Lambda
  -> DynamoDB item in orders-table
  -> SQS message in orders-queue
```

Required deterministic request:

```json
{
  "orderId": "order-001",
  "item": "notebook"
}
```

Required DynamoDB item:

```json
{
  "pk": { "S": "order#order-001" },
  "item": { "S": "notebook" }
}
```

Required checks:

```yaml
checks:
  - id: api-route
    type: apigateway_route_exists
    api_name: orders-api
    route: POST /orders
  - id: function-exists
    type: lambda_function_exists
    function_name: orders-function
  - id: table-exists
    type: dynamodb_table_exists
    table_name: orders-table
  - id: queue-exists
    type: sqs_queue_exists
    queue_name: orders-queue
  - id: http-writes-item
    type: workflow_http_writes_dynamodb
    api_name: orders-api
    route: POST /orders
    request_json:
      orderId: order-001
      item: notebook
    table_name: orders-table
    key:
      pk:
        S: order#order-001
  - id: http-sends-message
    type: workflow_http_sends_sqs
    api_name: orders-api
    route: POST /orders
    request_json:
      orderId: order-001
      item: notebook
    queue_name: orders-queue
    expected_body_contains: order-001
```

Required `owned_resources`:

```yaml
owned_resources:
  - type: apigateway_api
    api_name: orders-api
  - type: lambda_function
    function_name: orders-function
  - type: dynamodb_table
    table_name: orders-table
  - type: sqs_queue
    queue_name: orders-queue
```

Acceptance criteria:

- Mission gives learners a complete local serverless architecture.
- Commands are verified against Floci before marking story complete.
- Validation checks all resources and full workflow behavior.
- Reset deletes API, function, table, and queue idempotently.
- Repeated validation does not create ambiguous duplicate records.

Tests:

- loader accepts mission.
- validation passes after documented commands.
- validation fails when DynamoDB write is missing.
- validation fails when SQS message is missing.
- reset removes all owned resources.

### Story WEB-001: Add Next.js App Shell

Objective: create usable app frame.

Files:

```text
apps/web/app/layout.tsx
apps/web/app/page.tsx
apps/web/components/AppShell.tsx
apps/web/lib/api.ts
```

Acceptance criteria:

- App renders at `/`.
- App shell includes local-only banner.
- API client reads `NEXT_PUBLIC_API_URL`.
- Runtime status is fetched on load.

Tests:

- component render test.
- API client URL test.

### Story WEB-002: Add Mission Map

Objective: show curriculum state.

Files:

```text
apps/web/app/page.tsx
apps/web/components/MissionMap.tsx
apps/web/components/MissionCard.tsx
```

Acceptance criteria:

- Loading state renders.
- Empty state renders.
- Error state renders with retry.
- Locked, available, started, and completed cards render distinctly.
- Available cards link to detail page.

Tests:

- render each state.
- locked mission is not primary CTA.

### Story WEB-003: Add Mission Detail Page

Objective: render mission content and actions.

Files:

```text
apps/web/app/missions/[id]/page.tsx
apps/web/components/MissionDetail.tsx
apps/web/components/CommandBlock.tsx
```

Acceptance criteria:

- Shows story, objectives, commands, hints, status, and XP.
- Copy button copies exact command.
- Start button calls API.
- Validate and Reset disabled until mission is started.

Tests:

- render mission content.
- copy command behavior.
- disabled action states.

### Story WEB-004: Add Validation UI

Objective: show check-level feedback.

Files:

```text
apps/web/components/ValidationPanel.tsx
apps/web/lib/api.ts
```

Acceptance criteria:

- Validate button shows in-flight state.
- Partial failure shows passed and failed checks.
- Success shows XP awarded and next mission CTA.
- Runtime errors show actionable message.

Tests:

- partial failure render.
- success render.
- request in-flight disables button.

### Story WEB-005: Add Reset and Hint UI

Objective: support retry and guided help.

Files:

```text
apps/web/components/ResetControl.tsx
apps/web/components/HintPanel.tsx
```

Acceptance criteria:

- Reset asks for confirmation.
- Reset success refreshes mission detail.
- Reset failure shows API error.
- Hint reveal persists after refresh.
- Possible XP updates after hint use.

Tests:

- reset confirm flow.
- hint reveal flow.

### Story VERIFY-001: Add Local-Only Verification Script

Objective: make safety machine-checkable.

Files:

```text
scripts/verify-local-only.sh
```

Acceptance criteria:

- Fails on Docker `latest` tags.
- Fails on AWS CLI examples missing endpoint.
- Fails on dependency ranges using `^` or `~`.
- Fails on suspicious AWS keys.
- Allows documentation references to `amazonaws.com` only in explicit denylist sections.

Tests:

- script exits non-zero for fixture violations.
- script exits zero for clean repo.

### Story VERIFY-002: Add Smoke Test

Objective: prove the whole stack works.

Files:

```text
scripts/smoke-test.sh
Makefile
```

Acceptance criteria:

- `make verify` runs local-only scan, API tests, web build, and smoke test.
- Smoke test confirms web, API, and Floci respond.
- Smoke test creates and deletes temporary S3 bucket through API/Floci path.

Tests:

```bash
make verify
```

### Story DOCS-001: Add Complete README

Objective: make setup clear for beginners.

Files:

```text
README.md
```

Acceptance criteria:

- Quickstart is first.
- Explains no real AWS is used.
- Shows fake credential exports.
- Shows endpoint requirement.
- Includes troubleshooting for ports, Docker, API down, and Floci down.
- Links to spec, PRD, and plan.

Tests:

- all commands in README are endpoint-safe.
- local-only verification passes.

## Agent Completion Protocol

For each story, the agent must:

1. Read relevant sections of `INFRA_QUEST_PRD.md` and `INFRA_QUEST_SPEC.md`.
2. Implement only the story scope.
3. Add or update tests listed in the story.
4. Run the narrow test command.
5. Run broader verification if the story touches shared behavior.
6. Commit with message format `<story-id>: <summary>` if asked to commit.

Do not skip tests because the implementation appears simple. If a test cannot run locally, document the exact command attempted and the failure reason.
