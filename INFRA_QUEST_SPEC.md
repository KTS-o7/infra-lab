# Infra Quest Specification

## Overview

Infra Quest is a local-first cloud learning lab. Learners build a cumulative SaaS-style project inside a local AWS-compatible sandbox.

The platform remains:

```text
Browser
  -> Next.js Web App
  -> FastAPI Backend
  -> Floci AWS Emulator
  -> local state
```

The technical contract is:

- all AWS SDK and CLI traffic stays local
- missions are authored as structured curriculum
- validation inspects Floci state directly
- the frontend presents lessons through a Mission Workbench
- progress is persisted locally

## Agent Implementation Contract

Implementation agents must treat these documents as binding:

1. `INFRA_QUEST_PRD.md` defines user outcomes, product behavior, learner flows, and release-blocking bugs.
2. `INFRA_QUEST_SPEC.md` defines technical contracts, API shapes, data persistence, validation behavior, and verification gates.
3. `INFRA_QUEST_PLAN.md` defines implementation order and phase acceptance.

Rules:

- Do not invent alternate API shapes when this spec defines one.
- Do not rename persisted fields, mission fields, routes, or status values without updating all three docs.
- Do not skip tests because a change is "docs only" or "small" when implementation behavior changes.
- Do not weaken local-only safety for convenience.
- Do not add real AWS support in the MVP.
- Do not mark a phase complete until its acceptance criteria and verification commands pass.
- If implementation reveals a conflict between docs, update the docs first, then implement.

Every implementation PR or agent handoff must include:

- phases completed
- files changed
- tests run
- manual flows run
- known issues
- screenshots or browser notes for major UX flows when frontend changed

## Local-Only Constraint

All learner-facing AWS CLI commands must use:

```text
--endpoint-url http://localhost:4566
```

All backend AWS SDK calls must use:

```text
http://floci:4566
```

The backend must refuse to start if configured to talk to real AWS.

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

No product copy, command, hint, error, or troubleshooting step may ask the learner to configure real AWS credentials.

## Pinned Stack

Version basis checked on May 23, 2026. These version numbers are forward-projected targets reflecting the expected stable release versions at implementation time. If a listed version is not yet published, resolve to the nearest available stable release and update the pin in the lockfile. Do not use pre-release or alpha versions.

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

Supporting dependencies must be pinned exactly in lockfiles.

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

## Repository Structure

```text
infra-lab/
  docker-compose.yml
  README.md
  Makefile
  package.json
  bun.lock
  INFRA_QUEST_PRD.md
  INFRA_QUEST_SPEC.md
  INFRA_QUEST_PLAN.md

  apps/
    web/
      app/
      components/
      lib/
      package.json
      Dockerfile

    api/
      app/
        main.py
        config.py
        db.py
        models.py
        aws_client.py
        mission_loader.py
        validators/
        routes/
        services/
      pyproject.toml
      Dockerfile

  missions/
    <mission-id>/
      mission.yml
      function/

  scripts/
    dev.sh
    reset-lab.sh
    verify-local-only.sh
    smoke-test.sh
```

The `data/` directory must be gitignored.

## Docker Compose Contract

Services:

```text
floci    local AWS-compatible emulator on 4566
api      FastAPI mission API on 8000
web      Next.js app on 3000
```

Required API environment:

```text
AWS_ENDPOINT_URL=http://floci:4566
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
AWS_DEFAULT_REGION=us-east-1
DATABASE_URL=sqlite:////app/data/lab.db
MISSIONS_DIR=/app/missions
```

Required web environment:

```text
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Setup Diagnostics

The product must distinguish runtime setup failures from lesson failures.

Common setup failures:

```text
docker_not_running
port_3000_in_use
port_8000_in_use
port_4566_in_use
api_unreachable
floci_unreachable
database_unavailable
missions_unavailable
```

Troubleshooting copy may use local commands such as:

```bash
docker compose ps
docker compose logs api
docker compose logs floci
lsof -i :3000
lsof -i :8000
lsof -i :4566
```

Troubleshooting copy must not ask the learner to configure real AWS.

## Data Model

Use SQLite through SQLModel.

Required tables:

```text
profile
mission_progress
validation_attempt
step_progress
hint_usage
capstone_score
course_completion
schema_migration
```

### `profile`

Fields:

```text
id: string primary key
display_name: string nullable
total_xp: integer default 0
created_at: datetime
updated_at: datetime
```

There is one local profile by default.

### `mission_progress`

Fields:

```text
id: string primary key
mission_id: string unique
status: not_started | started | completed
started_at: datetime nullable
completed_at: datetime nullable
attempts: integer default 0
xp_awarded: integer default 0
created_at: datetime
updated_at: datetime
```

Rules:

- `xp_awarded` is written once for first full completion.
- Completed missions remain completed across restarts.
- Replaying a completed mission does not erase `completed_at`.
- XP award and mission completion must be updated in one transaction.
- `profile.total_xp` is a denormalized cache updated atomically in the same transaction that writes `mission_progress.xp_awarded`. It must always equal `SELECT SUM(xp_awarded) FROM mission_progress`. For `GET /profile`, `totalXp` is always derived by summing `xp_awarded` at query time; if the stored `profile.total_xp` ever diverges (e.g., after a migration), the query-time sum is authoritative. An agent should write both fields in the same transaction on XP award but always serve the live sum on `GET /profile`.
- Do not persist `locked` or `available` as authoritative database states.
- API mission status is an effective status derived from stored progress plus prerequisites:
  - stored `completed` -> API `completed`
  - stored `started` -> API `started`
  - stored `not_started` with incomplete prerequisites -> API `locked`
  - stored `not_started` with complete prerequisites -> API `available`

### `validation_attempt`

Fields:

```text
id: string primary key
mission_id: string
scope: mission | step
step_id: string nullable
passed: boolean
checks_json: json text
created_at: datetime
```

Rules:

- store check IDs, types, pass/fail, and messages
- never store secrets or real credentials

### `step_progress`

Fields:

```text
id: string primary key
mission_id: string
step_id: string
status: not_started | active | passed | failed | no_checks | blocked | stale
attempts: integer default 0
latest_checks_json: json text nullable
last_validated_at: datetime nullable
created_at: datetime
updated_at: datetime
```

Unique key:

```text
mission_id + step_id
```

Rules:

- Do not persist `checking`; it is a frontend-only transient state.
- If the API or browser crashes during validation, the previous persisted step status remains authoritative.
- `stale` is written when a resource reset occurs (`POST /missions/{id}/reset`) to indicate the previous proof result is no longer reliable. The frontend must treat `stale` as "proof was valid but resources have since changed; re-validate." `stale` is a persisted status, not a derived state. After a new validation attempt on a `stale` step, the status transitions to `passed` or `failed` like any `active` step.
- `blocked` is written when a step cannot be attempted because a required prior step has not yet passed. A step is `blocked` when the mission's YAML defines an explicit step ordering that requires sequential completion and an earlier step has not passed. In the MVP, step ordering is enforced by UI only; steps are not blocked at the API level unless the mission's YAML explicitly declares step dependencies. A `blocked` step transitions to `active` when its prerequisite step passes. The frontend renders `blocked` steps as inspectable but visually secondary with no validation action available.

### `hint_usage`

Fields:

```text
id: string primary key
mission_id: string
hint_id: string
level: nudge | diagnosis | repair
used_at: datetime
```

Unique key:

```text
mission_id + hint_id
```

Idempotency rule: on a repeated call to `POST /hints/{id}/use` for the same `mission_id + hint_id`, the existing row is returned unchanged. `used_at` retains the timestamp of the first use and is not updated on subsequent calls.

### `capstone_score`

Fields:

```text
id: string primary key
mission_id: string
latest_score: integer nullable
best_score: integer nullable
latest_level: needs_repair | complete | strong | production_minded nullable
best_level: needs_repair | complete | strong | production_minded nullable
dimensions_json: json text nullable
updated_at: datetime
```

### `course_completion`

Fields:

```text
id: string primary key
course_id: string unique
status: not_started | in_progress | completed
required_lessons_completed: integer
required_lessons_total: integer
required_capstones_completed: integer
required_capstones_total: integer
completed_at: datetime nullable
updated_at: datetime
```

Rules:

- `required_*` counts are recomputed from current `course.yml` plus persisted mission completions.
- Stored counts are a snapshot/cache, not the source of truth.
- Staleness detection: on API startup, compute a hash of `course.yml` content and compare it to a stored hash (in a `course_yml_hash` column on the `course_completion` row or in a separate key-value config table). If the hash differs, recompute all `required_*` counts and update the stored hash. If no hash is stored yet, recompute unconditionally. An agent must always serve the recomputed values on `GET /course`, not the stale DB cache, if the hash has changed since the last recompute.
- Orphaned progress for removed or renamed missions must be preserved but not counted toward current course completion.
- Mission IDs should be treated as stable; renaming a mission requires an explicit migration.

### `schema_migration`

Fields:

```text
version: string primary key
applied_at: datetime
description: string
```

Migration rules:

- migrations must be idempotent
- migrations must preserve progress, XP, hint usage, step progress, and capstone scores
- migrations must preserve orphaned progress unless an explicit user-approved cleanup exists
- migration failures must stop startup with a local recovery message
- destructive migrations require an explicit backup/export step first
- the `schema_migration` table itself is created by a one-time bootstrap step before any version-numbered migrations run; the migration runner must handle the case where this table does not yet exist by creating it before running any migrations
- a mission ID rename migration must update `mission_id` in `mission_progress`, `validation_attempt`, `step_progress`, `hint_usage`, and `capstone_score`; it must run idempotently (no-op if the old ID no longer exists). The rename of `serverless-boss` to `launchdesk-compose-capstone` must be handled as such a migration in Phase 6.

`mission_progress.status` uses `started` (not `in_progress`) because a single mission is either actively being worked on or not — there is no partial completion sub-state. `course_completion.status` uses `in_progress` because the course spans many missions and can be partially complete. These enums are intentionally different; do not substitute one for the other.

## Course Metadata Schema

Course-level metadata must be authored separately from individual mission files so module order, capability labels, and capstone grouping are not hard-coded in the frontend.

File:

```text
missions/course.yml
```

Required shape:

```yaml
id: launchdesk-cloud-apprenticeship
title: LaunchDesk Cloud Apprenticeship
summary: Build a local SaaS-style platform while learning cloud fundamentals.
modules:
  - id: orientation
    order: 0
    title: Local Cloud Orientation
    required: true
    capability: safe_local_sandbox
    capability_label: Safe local sandbox
    summary: Prove every cloud call stays inside the local lab.
    capstone_mission_id: null
    capstone_required: false
  - id: storage
    order: 1
    title: Store Files Outside The App
    required: true
    capability: durable_file_storage
    capability_label: Durable file storage
    summary: Add object storage for LaunchDesk assets.
    capstone_mission_id: null
    capstone_required: false
  - id: api
    order: 2
    title: Expose A Backend API
    required: true
    capability: http_api
    capability_label: HTTP backend API
    summary: Create a serverless HTTP entrypoint for LaunchDesk.
    capstone_mission_id: null
    capstone_required: false
  - id: database
    order: 3
    title: Persist Application Records
    required: true
    capability: persisted_records
    capability_label: Persisted application records
    summary: Store structured LaunchDesk records in a NoSQL table.
    capstone_mission_id: null
    capstone_required: false
  - id: async_processing
    order: 4
    title: Move Slow Work Out Of Requests
    required: true
    capability: async_work
    capability_label: Async background work
    summary: Add queue-based async processing to LaunchDesk.
    capstone_mission_id: null
    capstone_required: false
  - id: events
    order: 5
    title: Broadcast Platform Events
    required: true
    capability: event_fanout
    capability_label: Platform event fanout
    summary: Notify multiple consumers when important things happen.
    capstone_mission_id: null
    capstone_required: false
  - id: composition
    order: 6
    title: Compose The Platform
    required: true
    capability: composed_platform
    capability_label: Composed end-to-end platform
    summary: Wire all services into one working LaunchDesk flow.
    capstone_mission_id: launchdesk-compose-capstone
    capstone_required: false
  - id: operations
    order: 7
    title: Operate And Debug
    required: true
    capability: operational_debugging
    capability_label: Operational debugging
    summary: Reason about and recover from cloud system failures.
    capstone_mission_id: null
    capstone_required: false
```

Note: `capstone_mission_id: null` for modules 0–5 and 7 means those capstone missions are planned in the PRD/PLAN but have not yet been authored. Set `capstone_mission_id` to the mission ID and update `capstone_required` only after the mission file exists and has passed authoring validation. Do not set `capstone_required: true` until the mission is part of the current target release.

Loader validation:

- module IDs must be unique
- module order values must be unique
- every mission `module` must exist in `course.yml`
- every non-null `capstone_mission_id` must reference an existing mission
- if `capstone_required` is `true`, `capstone_mission_id` must be non-null and reference an existing mission
- every required module must have at least one required lesson or required capstone before release
- optional modules and optional capstones do not block course completion
- do not set `capstone_required: true` until the referenced mission exists and is in the target release

## Mission Schema

Mission files are YAML files under `missions/<mission-id>/mission.yml`.

Required base fields:

```yaml
id: s3-first-bucket
order: 2
module: storage
submodule: create-storage-boundary
mission_type: lesson
required: true
title: First Bucket
summary: Create durable object storage for LaunchDesk assets.
difficulty: beginner
services:
  - s3
xp: 100
estimated_minutes: 10
prerequisites:
  - cloud-explorer
story: |
  The platform needs durable storage for onboarding files.
learning_objectives:
  - Understand object storage
  - Create and inspect a bucket
```

Curriculum fields:

```yaml
capability: durable_file_storage
motivation: |
  The app needs files to survive process restarts.
theory: |
  Object storage keeps files behind a bucket/key model.
thought_process: |
  Use object storage when the app needs durable blobs, not relational queries.
debrief: |
  Production systems use this pattern for uploads, reports, exports, and static assets.
```

Supported `mission_type` values:

```text
lesson
module_capstone
final_capstone
```

`required` defaults by mission type:

- `lesson`: `true`
- `final_capstone`: `true`
- `module_capstone`: follows the parent module's `capstone_required` value

Completion rules:

- required lessons block course completion until completed
- optional lessons do not block course completion
- module capstones block course completion only when the course module has `capstone_required: true`
- final capstones block course completion only when `required: true`
- future/unimplemented capstones must not be marked required

### Commands

Commands are authored separately from learner-facing steps.

```yaml
commands:
  - id: create-bucket
    label: Create bucket
    command: aws --endpoint-url http://localhost:4566 s3 mb s3://launchdesk-assets
```

Every command must be local-only.

### Checks

Checks define validation primitives.

```yaml
checks:
  - id: bucket-exists
    type: s3_bucket_exists
    bucket: launchdesk-assets
```

Validators must inspect Floci state. They must not trust user-submitted claims.

### Steps

Steps are the learner-facing workbench layer.

```yaml
steps:
  - id: create-storage-boundary
    title: Create the storage boundary
    goal: Create an S3 bucket named launchdesk-assets.
    why: Apps need durable storage for files that must survive app restarts and deployments.
    target_state:
      - label: Bucket
        value: launchdesk-assets
      - label: Service
        value: S3
    action: Create the bucket in your local AWS sandbox.
    command_id: create-bucket
    check_ids:
      - bucket-exists
    success: The launchdesk-assets bucket exists in local S3.
```

Required step fields:

- `id`: unique within the mission
- `title`
- `goal`
- `action`

Optional step fields:

- `command_id`: omit for capstone steps or reasoning steps where command guidance is intentionally withheld or delayed. When absent, the step has no revealable CLI syntax; commands may be added to the mission `commands` list but not linked to a step.
- `check_ids`: omit or leave empty for steps whose completion is verified only by full mission validation (e.g. final capstone end-to-end steps). A step with no `check_ids` renders in `no_checks` state and explains that final validation proves it.
- `why`
- `target_state`
- `success`
- `notes`

Loader validation:

- mission IDs must be unique
- step IDs must be unique inside a mission
- every `command_id` in `steps` must match a command in the same mission (only enforced when `command_id` is present)
- every `check_id` in `steps` must match a check in the same mission (only enforced when `check_ids` is non-empty)
- missions should still load when new curriculum fields are absent during migration
- mission `order` values do not need to be globally unique; the tie-breaker rule (`id` ascending) resolves duplicates when two missions share the same `order`. Module `order` values must be globally unique.
- a mission's `capability` field, when present, must match the `capability` of its parent module as defined in `course.yml`; a mismatch causes the capability tracking to show incorrect missions and must fail loader validation

### Authoring Validator vs Runtime Loader

The mission schema applies in two distinct contexts with different strictness levels:

**Runtime loader (migration-tolerant):** Used when loading missions at API startup. New curriculum fields (`motivation`, `theory`, `thought_process`, `debrief`, `capability`) are optional during loading. Missing curriculum fields produce a warning log, not a startup failure. This ensures old missions continue to work during and after migration.

**Authoring validator (release-strict):** Used by `make verify` and CI. All required base fields plus all curriculum fields are enforced here. A mission that passes the runtime loader but fails the authoring validator cannot be merged or released.

Required base fields (enforced by both loader and authoring validator):

```text
id, order, module, submodule, mission_type, required, title, summary,
difficulty, services, xp, estimated_minutes, prerequisites, story
```

Required curriculum fields (enforced by authoring validator only; loader emits warning if absent):

```text
capability, motivation, theory, thought_process, debrief
```

Optional mission fields (not enforced; included when present; returned in API response when non-null):

```text
learning_objectives, why (step-level), target_state (step-level), success (step-level), notes (step-level)
```

`learning_objectives` is optional. It is not enforced by the loader or the authoring validator. When present it must be a list of strings and is returned in `GET /missions/{id}` as `learningObjectives`.

Step-level `why` is optional and permanently so. It is not enforced by the authoring validator or the content quality gate. The `MissionStepCard` component renders `why` when present; when absent, the step card simply omits the why section. Authoring contributors are encouraged to include `why` for all non-trivial steps, but it is not a release blocker.

This distinction means: existing missions load safely after a schema update, but contributors must add curriculum fields before a mission is considered release-ready.

### Hints

```yaml
hints:
  - id: endpoint-required
    title: Check the endpoint
    level: nudge
    applies_to_checks:
      - bucket-exists
    text: Every AWS CLI command in this lab needs --endpoint-url http://localhost:4566.
    penalty_xp: 5
```

Hint text may be hidden until used.

Supported hint levels:

```text
nudge
diagnosis
repair
```

Rules:

- `nudge` hints point to what to inspect.
- `diagnosis` hints explain the likely missing or incorrect state.
- `repair` hints may reveal exact commands or recovery sequence.
- `applies_to_checks` is optional, but should be used when a hint is tied to a known failure.
- Help usage must be persisted.

### Owned Resources

Owned resources define safe reset behavior.

```yaml
owned_resources:
  - type: s3_bucket
    bucket: launchdesk-assets
```

Reset must delete only owned resources for the mission.

## API Contract

Successful responses return the resource body directly.

Error responses always return:

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
- `error.details` is always an object.
- Error messages must never tell users to configure real AWS.

### Endpoints

```text
GET  /health
GET  /runtime/status
GET  /course
GET  /missions
GET  /missions/{mission_id}
POST /missions/{mission_id}/start
POST /missions/{mission_id}/validate
POST /missions/{mission_id}/reset
POST /missions/{mission_id}/hints/{hint_id}/use
GET  /profile
```

### `GET /health`

Purpose: confirm API process is alive.

Response:

```json
{
  "status": "ok",
  "service": "infra-quest-api"
}
```

### `GET /runtime/status`

Purpose: report whether local dependencies are ready.

Response:

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
  "setup": {
    "status": "ready",
    "issues": []
  },
  "localOnly": {
    "status": "enforced",
    "endpoint": "http://floci:4566"
  }
}
```

If Floci is unavailable, return `200` with `floci.status = "offline"` so the frontend can render a degraded state. Use `503` only if the API cannot evaluate runtime status.

`localOnly.status` valid values:

```text
enforced   local-only constraint is active; no real AWS endpoint is configured or reachable
```

The value `enforced` is the only valid runtime value. The backend refuses to start if a real AWS endpoint is detected, so `localOnly.status` will never show a `violated` state at runtime — a violation causes startup failure, not a runtime status value.

When setup issues are known, include them:

```json
{
  "setup": {
    "status": "degraded",
    "issues": [
      {
        "code": "floci_unreachable",
        "message": "Floci is not reachable at http://floci:4566.",
        "suggestedCommand": "docker compose logs floci"
      }
    ]
  }
}
```

Setup issue object fields:

- `code`: required; machine-readable string from the defined setup failure code list.
- `message`: required; human-readable string safe to display in the UI.
- `suggestedCommand`: optional; a local shell command the learner can run to diagnose or fix the issue. Omit (do not include the field) when no command is relevant. Do not set to `null`.
```

### `GET /course`

Purpose: return the module map, capability progression, capstones, and learner progress summary needed by the course map.

Error behavior:

- If `course.yml` is missing or fails to load at startup, the API must refuse to start (not serve a degraded response). This is treated the same as a fatal configuration error.
- If the database is unavailable at request time: `500 COURSE_ERROR` with `message: "Course data is unavailable."`.
- A missing or empty missions directory does not fail `GET /course`; it returns the course structure from `course.yml` with all missions showing `status: locked` and all progress counts at `0`.

Response:

```json
{
  "course": {
    "id": "launchdesk-cloud-apprenticeship",
    "title": "LaunchDesk Cloud Apprenticeship",
    "summary": "Build a local SaaS-style platform while learning cloud fundamentals.",
    "progress": {
      "status": "in_progress",
      "requiredLessonsCompleted": 0,
      "requiredLessonsTotal": 1,
      "requiredCapstonesCompleted": 0,
      "requiredCapstonesTotal": 0,
      "xp": 0,
      "nextMissionId": "s3-first-bucket",
      "completedAt": null
    },
    "modules": [
      {
        "id": "storage",
        "order": 1,
        "title": "Store Files Outside The App",
        "summary": "Add object storage for LaunchDesk assets.",
        "required": true,
        "capability": "durable_file_storage",
        "capabilityLabel": "Durable file storage",
        "status": "available",
        "requiredLessonsCompleted": 0,
        "requiredLessonsTotal": 1,
        "requiredCapstonesCompleted": 0,
        "requiredCapstonesTotal": 0,
        "capstoneMissionId": null,
        "capstoneRequired": false,
        "missions": [
          {
            "id": "s3-first-bucket",
            "order": 2,
            "title": "First Bucket",
            "missionType": "lesson",
            "required": true,
            "status": "available"
          }
        ]
      }
    ],
    "capabilities": [
      {
        "id": "durable_file_storage",
        "label": "Durable file storage",
        "status": "locked",
        "moduleId": "storage",
        "missionIds": ["s3-first-bucket"]
      }
    ]
  }
}
```

Status values for `module.status` and `module.missions[*].status`:

```text
locked
available
started
completed
```

These four values describe learner progress state for a module or individual mission. They are **not** the same as capability status values. Do not mix the two enums.

The `capstone` state mentioned in the PRD and PLAN course-map required states is **not** an API status value. It is a frontend display variant applied to missions whose `missionType` is `module_capstone` or `final_capstone`. The UI renders these missions differently (e.g., distinct visual marker) while their API status remains one of the four values above. Do not add `capstone` to the module or mission status enum.

Capability status values (`capabilities[*].status`):

```text
locked       no required lessons in this capability's module are started or completed
in_progress  at least one required lesson is completed but the capability is not fully unlocked
unlocked     all required lessons (and required capstone if any) for the module are completed
```

Capability status describes the product capability unlock level, not raw learner progress. It uses a three-value enum (`locked`, `in_progress`, `unlocked`) that is distinct from the four-value module/mission status enum (`locked`, `available`, `started`, `completed`). An agent must never substitute one for the other.

The `pending` value is not valid in either enum. Do not use `online` as a capability status in API responses; `online` is a continuity-panel display label derived from `unlocked` status. The mapping from API status to display label is handled in the frontend only.

The frontend `ContinuityPanel` may display `unlocked` capability status as `online` in copy such as `Storage: launchdesk-assets bucket online`. That label is a UI concern, not an API value.

The frontend should prefer `GET /course` for the course map and use `GET /missions` for simpler mission lists or fallback rendering.

Progress count rules:

Top-level `course.progress` counts:

- `requiredLessonsCompleted` and `requiredLessonsTotal` count required lessons across all modules.
- `requiredCapstonesCompleted` and `requiredCapstonesTotal` count required capstones across all modules.
- Optional lessons and optional capstones may render in the module list, but they do not affect top-level completion counts.
- If a release includes optional progress display, use explicit optional fields rather than overloading required counts.

Per-module counts (fields on each `modules[]` object):

- `requiredLessonsCompleted` and `requiredLessonsTotal` count required lessons within that module only.
- `requiredCapstonesCompleted` and `requiredCapstonesTotal` count required capstones within that module only.
- The field names are identical to the top-level counts; scope is determined by context (top-level object vs module object).
- The old names `completedLessons` and `totalLessons` are not valid; do not use them at any level.

Module status derivation rules (evaluated in priority order — use the first matching condition):

```text
completed   all required lessons in the module are completed (and required capstone if capstone_required is true)
started     at least one mission in the module is started or completed, but the module is not fully completed
available   no mission is started or completed, but at least one mission in the module is available
locked      all missions in the module are locked (prerequisites not met for any)
```

Evaluate `completed` first. If not all required lessons (and required capstone when applicable) are done, evaluate `started`. This prevents a module with only one required lesson from remaining `started` once that lesson is completed.

Course progress status rules:

```text
not_started   no mission in the course has been started or completed
in_progress   at least one required lesson has been started or completed; course not yet complete
completed     all required lessons and all required capstones are completed
```

`nextMissionId` computation rule: `nextMissionId` is the `id` of the first mission (sorted by `order` ascending, then `id` ascending as tie-breaker) whose API status is `available`. If no available mission exists (all are locked or completed), `nextMissionId` is `null`.

`capabilities[*].missionIds` rule: lists the IDs of all **required** missions within the module whose `capability` field matches this capability ID, sorted by `order` ascending. Optional missions with a matching `capability` field are excluded from `missionIds`; they contribute to learning but do not determine the capability unlock state.

### `GET /missions`

Purpose: list missions in curriculum order.

Error behavior:

- If mission data is unavailable (database offline or mission loader failed): `500 MISSIONS_UNAVAILABLE` with `message: "Mission data is unavailable."`.

Response:

```json
{
  "missions": [
    {
      "id": "s3-first-bucket",
      "order": 2,
      "module": "storage",
      "submodule": "create-storage-boundary",
      "missionType": "lesson",
      "capability": "durable_file_storage",
      "title": "First Bucket",
      "summary": "Create durable object storage for LaunchDesk assets.",
      "difficulty": "beginner",
      "services": ["s3"],
      "xp": 100,
      "status": "available",
      "required": true,
      "prerequisites": ["cloud-explorer"],
      "estimatedMinutes": 10
    }
  ]
}
```

Sorting rules:

1. `module.order` ascending (from `course.yml`).
2. `mission.order` ascending within the module.
3. `mission.id` ascending as deterministic tie-breaker within the same module and order.

This ensures missions are grouped by module in the flat list, matching the course map display order.

### `GET /missions/{mission_id}`

Purpose: return full mission content and learner progress.

Error behavior:

- mission not found: `404 MISSION_NOT_FOUND`

Response:

```json
{
  "mission": {
    "id": "s3-first-bucket",
    "order": 2,
    "module": "storage",
    "submodule": "create-storage-boundary",
    "missionType": "lesson",
    "capability": "durable_file_storage",
    "title": "First Bucket",
    "summary": "Create durable object storage for LaunchDesk assets.",
    "difficulty": "beginner",
    "services": ["s3"],
    "xp": 100,
    "estimatedMinutes": 10,
    "required": true,
    "prerequisites": ["cloud-explorer"],
    "status": "started",
    "story": "The platform needs durable storage for onboarding files.",
    "motivation": "The app needs files to survive process restarts.",
    "theory": "Object storage keeps files behind a bucket/key model.",
    "thoughtProcess": "Use object storage when the app needs durable blobs, not relational queries.",
    "debrief": "Production systems use this pattern for uploads, reports, exports, and static assets.",
    "learningObjectives": ["Understand object storage"],
    "commands": [
      {
        "id": "create-bucket",
        "label": "Create bucket",
        "command": "aws --endpoint-url http://localhost:4566 s3 mb s3://launchdesk-assets"
      }
    ],
    "steps": [
      {
        "id": "create-storage-boundary",
        "title": "Create the storage boundary",
        "goal": "Create an S3 bucket named launchdesk-assets.",
        "why": "Apps need durable storage for files that must survive app restarts and deployments.",
        "targetState": [
          {
            "label": "Bucket",
            "value": "launchdesk-assets"
          }
        ],
        "action": "Create the bucket in your local AWS sandbox.",
        "commandId": "create-bucket",
        "checkIds": ["bucket-exists"],
        "success": "The launchdesk-assets bucket exists in local S3."
      }
    ],
    "hints": [],
    "stepProgress": [
      {
        "stepId": "create-storage-boundary",
        "status": "passed",
        "lastValidatedAt": "2026-05-23T13:56:00Z",
        "attempts": 1,
        "latestChecks": [
          {
            "id": "bucket-exists",
            "type": "s3_bucket_exists",
            "passed": true,
            "message": "Bucket launchdesk-assets exists."
          }
        ]
      }
    ],
    "helpUsage": [
      {
        "hintId": "endpoint-required",
        "level": "nudge",
        "usedAt": "2026-05-23T13:57:00Z"
      }
    ],
    "progress": {
      "status": "started",
      "attempts": 1,
      "xpAwarded": 0,
      "startedAt": "2026-05-23T13:55:00Z",
      "completedAt": null
    }
  }
}
```

`stepProgress[].latestChecks` contains the full check result objects from the most recent validation of that step, matching the shape returned by validators. This is stored as `latest_checks_json` in the `step_progress` table and is used to restore the proof board on page resume. All hint data is in `helpUsage[]`; the `progress{}` object does not duplicate it.

The `hints[]` array in the mission detail response contains all hints for the mission. Hint `text` is hidden until the hint has been used. The shape differs by reveal state:

```json
// Unused hint (text hidden):
{
  "id": "endpoint-required",
  "title": "Check the endpoint",
  "level": "nudge",
  "appliesToChecks": ["bucket-exists"],
  "penaltyXp": 5,
  "revealed": false
}

// Used/revealed hint (text visible — after POST /hints/{id}/use):
{
  "id": "endpoint-required",
  "title": "Check the endpoint",
  "level": "nudge",
  "appliesToChecks": ["bucket-exists"],
  "penaltyXp": 5,
  "revealed": true,
  "text": "Every AWS CLI command in this lab needs --endpoint-url http://localhost:4566."
}
```

A hint is considered revealed if it exists in `helpUsage[]` for this mission. The `revealed` boolean is derived from that list; it is not persisted separately.

YAML snake_case fields must be converted to API camelCase.

Serialization rule for DB columns and YAML fields: all multi-word snake_case names (from YAML fields and DB column names) are converted to camelCase in API responses. Single-word names (`id`, `title`, `xp`, `order`, `status`, `level`, `type`, `passed`, `message`) are unchanged. This rule applies to fields inside JSON blob columns (`dimensions_json`, `checks_json`, `latest_checks_json`) — the stored JSON uses snake_case keys and must be deserialized to camelCase before returning in the API response. Example mappings:

```text
DB column / YAML field   -> API field
mission_id               -> missionId
xp_awarded               -> xpAwarded
started_at               -> startedAt
completed_at             -> completedAt
last_validated_at        -> lastValidatedAt
latest_checks_json       -> latestChecks  (array of check objects)
hint_id                  -> hintId
used_at                  -> usedAt
applies_to_checks        -> appliesToChecks
penalty_xp               -> penaltyXp
thought_process          -> thoughtProcess
mission_type             -> missionType
estimated_minutes        -> estimatedMinutes
capability_label         -> capabilityLabel
capstone_mission_id      -> capstoneMissionId
capstone_required        -> capstoneRequired
```

If `steps` is absent, derive one fallback step per command:

- `id` uses the command's `id` (e.g., `create-bucket` becomes the step ID)
- title uses command label
- action is `Run this command in your terminal against the local AWS sandbox.`
- `checkIds` is empty
- full mission validation still works

### `POST /missions/{mission_id}/start`

Purpose: mark a mission as started.

Behavior:

- available -> started
- started -> idempotent current state
- completed -> remain completed
- locked -> `409 MISSION_LOCKED`
- mission not found -> `404 MISSION_NOT_FOUND`

Response (HTTP 200):

```json
{
  "missionId": "s3-first-bucket",
  "status": "started"
}
```

The start response is intentionally minimal. It does not include `startedAt`. Fetch `GET /missions/{id}` for full mission progress state including `startedAt` after starting.

### `POST /missions/{mission_id}/validate`

Purpose: inspect Floci state and record a validation attempt.

Request body is optional.

Full mission validation:

```json
{}
```

Step validation:

```json
{
  "stepId": "create-storage-boundary"
}
```

Validation result (step-scoped example):

```json
{
  "missionId": "s3-first-bucket",
  "passed": true,
  "status": "started",
  "xpAwarded": 0,
  "attemptNumber": 2,
  "checks": [
    {
      "id": "bucket-exists",
      "type": "s3_bucket_exists",
      "passed": true,
      "message": "Bucket launchdesk-assets exists."
    }
  ],
  "unlockedMissionIds": [],
  "scope": "step",
  "stepId": "create-storage-boundary"
}
```

Validation result (full-mission first-completion example):

```json
{
  "missionId": "s3-first-bucket",
  "passed": true,
  "status": "completed",
  "xpAwarded": 100,
  "attemptNumber": 1,
  "checks": [
    {
      "id": "bucket-exists",
      "type": "s3_bucket_exists",
      "passed": true,
      "message": "Bucket launchdesk-assets exists."
    }
  ],
  "unlockedMissionIds": ["lambda-tiny-function"],
  "scope": "mission",
  "stepId": null
}
```

Validation result (full-mission re-validation on already-completed mission):

```json
{
  "missionId": "s3-first-bucket",
  "passed": true,
  "status": "completed",
  "xpAwarded": 0,
  "attemptNumber": 3,
  "checks": [
    {
      "id": "bucket-exists",
      "type": "s3_bucket_exists",
      "passed": true,
      "message": "Bucket launchdesk-assets exists."
    }
  ],
  "unlockedMissionIds": [],
  "scope": "mission",
  "stepId": null
}
```

Re-validating a completed mission: `xpAwarded` is `0` (XP was already awarded), `unlockedMissionIds` is `[]` (unlocks already happened), `status` remains `completed`. The attempt is still persisted. Re-validating a completed mission never duplicates XP.
```

Behavior:

- no body: validate all mission checks
- no body and all checks pass: award XP once and mark mission completed
- `stepId`: validate only checks linked to that step
- `stepId`: never award XP
- `stepId`: never mark mission completed
- every validation attempt is persisted with scope, step ID, check results, and timestamp
- step progress is updated from scoped validation
- mission not found (any scope): return `404 MISSION_NOT_FOUND`
- `stepId` not found in the mission's step list: return `404 STEP_NOT_FOUND`
- `stepId` provided but mission is locked: return `409 MISSION_LOCKED`
- no `stepId` (full-mission scope) but mission is locked: return `409 MISSION_LOCKED`
- mission is in `available` status (not yet started): auto-transition to `started` before running validation, identical to calling `POST /start` first. Do not return an error; proceed with the validation. This prevents a needless round-trip for learners who run validation without explicitly starting.
- step with no checks: return a scoped validation result with `passed: true`, `checks: []`, and a message explaining that final mission validation proves this step. A validation on a `no_checks` step does not change the persisted `step_progress.status`; it remains `no_checks`. Only full mission validation can confirm these steps.
- capstone validation may include `capstoneScore`

Capstone validation result extension:

```json
{
  "capstoneScore": {
    "score": 85,
    "level": "strong",
    "dimensions": [
      {
        "id": "infrastructure_completeness",
        "label": "Infrastructure completeness",
        "score": 30,
        "maxScore": 30
      },
      {
        "id": "end_to_end_behavior",
        "label": "End-to-end behavior",
        "score": 40,
        "maxScore": 40
      },
      {
        "id": "independence",
        "label": "Independence",
        "score": 10,
        "maxScore": 15
      },
      {
        "id": "recovery",
        "label": "Recovery",
        "score": 5,
        "maxScore": 10
      }
    ],
    "localSafetyPassed": true
  }
}
```

Capstone levels:

```text
needs_repair
complete
strong
production_minded
```

Scoring rules:

- `score = sum of all dimension scores`. The maximum possible score is 95 (30 + 40 + 15 + 10). The score is not normalized to 100.
- `localSafetyPassed` is a required gate. It is computed by verifying the `runtime_floci_available` check and confirming no real AWS endpoint was used during the capstone session. If `localSafetyPassed` is `false`, the capstone cannot complete regardless of dimension scores.
- At runtime the backend refuses to start if a real AWS endpoint is detected, so `localSafetyPassed` will be `false` only when the `runtime_floci_available` check fails or a real endpoint pattern is detected in submitted commands. If `localSafetyPassed` is `true` at validation time, it can be treated as always `true` in the MVP since startup blocks real-endpoint configurations.
- A capstone cannot pass if critical checks fail.
- Hint use and repeated failed attempts may reduce independence score.
- Recovery score is awarded only when a repair path is part of the capstone.
- Score should guide replay and reflection, not block progression after required checks pass.

Capstone mastery level thresholds (based on `score` out of 95):

```text
needs_repair      score < 60  (critical checks failed or local safety not passed)
complete          60 <= score < 75
strong            75 <= score < 90
production_minded score >= 90
```

Display labels (frontend only, not API values):

```text
needs_repair     -> "Needs repair"
complete         -> "Complete"
strong           -> "Strong"
production_minded -> "Production-minded"
```

### `POST /missions/{mission_id}/reset`

Purpose: remove mission-owned local resources.

Request:

```json
{
  "mode": "resources"
}
```

Supported modes:

```text
resources
progress
resources_and_progress
```

Behavior:

- delete only `owned_resources`
- do not touch unrelated local resources
- return reset summary
- preserve or update progress according to reset mode
- `resources`: delete owned resources and mark proof state stale, but keep completion history
- `progress`: clear non-completion progress such as step state, attempts, latest proof, and help reveal state, but preserve completed mission history, `xp_awarded`, best capstone score, and course completion
- `resources_and_progress`: reset resources and non-completion progress, but still preserve completed mission history, `xp_awarded`, best capstone score, and course completion
- no reset mode may create duplicate XP eligibility for an already completed mission

Response:

```json
{
  "missionId": "s3-first-bucket",
  "mode": "resources",
  "deleted": [
    {
      "type": "s3_bucket",
      "id": "launchdesk-assets",
      "status": "deleted"
    }
  ],
  "skipped": [],
  "failed": []
}
```

Error behavior:

- mission not found: `404 MISSION_NOT_FOUND`
- `mode` is absent or not one of the three valid values: `422 INVALID_RESET_MODE` with `details.validModes: ["resources", "progress", "resources_and_progress"]`
- Floci unreachable during resource deletion: return HTTP `200` with the affected resource entry placed in `failed[]` with `"status": "error"` and `"message": "Floci unreachable"`; do not return `503` for partial failures. Return `503 FLOCI_UNAVAILABLE` only if Floci is unreachable before any deletion attempt can be started.
- request body is missing or malformed JSON: `422 INVALID_REQUEST_BODY`
```

### `POST /missions/{mission_id}/hints/{hint_id}/use`

Purpose: reveal and persist a hint.

Behavior:

- using the same hint twice is idempotent
- hint penalty is applied once
- hints cannot reduce possible XP below `0`
- using a hint after completion reveals the hint but does not change awarded XP
- help usage is included in mission detail after use

XP penalty formula:

```text
xp_awarded = max(0, mission.xp - sum(penalty_xp for each distinct hint used before completion))
```

The formula is evaluated at the moment of first full mission completion. Each distinct hint can only contribute its `penalty_xp` once, regardless of how many times the hint use endpoint is called (idempotency). Hints used after completion do not affect `xp_awarded`.

Response (HTTP 200):

```json
{
  "hintId": "endpoint-required",
  "title": "Check the endpoint",
  "level": "nudge",
  "text": "Every AWS CLI command in this lab needs --endpoint-url http://localhost:4566.",
  "appliesToChecks": ["bucket-exists"],
  "penaltyXp": 5,
  "usedAt": "2026-05-23T13:57:00Z"
}
```

The `text` field is always included in the response (the hint is considered revealed by the act of calling this endpoint). Do not return `text` in `GET /missions/{id}` hints list until the hint has been used.

Error behavior:

- mission not found: `404 MISSION_NOT_FOUND`
- hint ID not found in the mission's hint list: `404 HINT_NOT_FOUND`
- mission is locked: `409 MISSION_LOCKED` (hints may not be revealed for missions the learner has not yet unlocked)

### `GET /profile`

Purpose: return the learner's XP total, capability badges earned, and overall course progress.

Source of truth:

- `totalXp` is derived by summing `xp_awarded` across all `mission_progress` rows; it must equal `profile.total_xp`.
- `badges` are derived from the set of module capability IDs whose required lessons and required capstones are all completed. There is no separate `badge` or `capability_badge` DB table. Badge data is computed at query time from `mission_progress` and `course_completion`. `earnedAt` is derived as the `completed_at` of the last required mission completed in that module's required set (i.e., the timestamp that caused the module to become fully completed). `earnedAt` is always recomputed from live `mission_progress` data against the current `course.yml` required mission list; it is not cached. If `course.yml` changes the required set, `earnedAt` will reflect the new last-required-mission's `completed_at` on the next query.
- A capability badge is issued exactly when a capability's status transitions to `unlocked`. Every badge corresponds to exactly one `unlocked` capability. There is no state where a capability is `unlocked` but has no badge, or a badge exists for a non-`unlocked` capability.
- `courseProgress` mirrors the full `course.progress` object from `GET /course`, including `status`, `requiredLessonsCompleted`, `requiredLessonsTotal`, `requiredCapstonesCompleted`, `requiredCapstonesTotal`, `xp`, `nextMissionId`, and `completedAt`; do not recompute independently.

Response:

```json
{
  "profile": {
    "id": "local",
    "displayName": null,
    "totalXp": 200,
    "badges": [
      {
        "capability": "safe_local_sandbox",
        "label": "Safe local sandbox",
        "moduleId": "orientation",
        "earnedAt": "2026-05-23T14:00:00Z"
      }
    ],
    "courseProgress": {
      "status": "in_progress",
      "requiredLessonsCompleted": 2,
      "requiredLessonsTotal": 8,
      "requiredCapstonesCompleted": 0,
      "requiredCapstonesTotal": 3,
      "xp": 200,
      "nextMissionId": "dynamodb-first-table",
      "completedAt": null
    },
    "createdAt": "2026-05-23T12:00:00Z",
    "updatedAt": "2026-05-23T14:00:00Z"
  }
}
```

Error behavior:

- Profile is always initialized on first API start; there is no `404` for profile.
- If the profile row does not exist (first-run edge case), the API must create it and return defaults.
- `500` with `PROFILE_ERROR` if the database is unavailable.

### Course Completion

The course is complete when:

- every required lesson mission is completed
- every required module capstone is completed
- every required final capstone is completed

Completion should not require optional replay, optional improved mastery scores, or terminal features.

`GET /course` exposes completion state inside `course.progress`. There is no separate `completion` key.
The canonical fields are:

```text
course.progress.status                    not_started | in_progress | completed
course.progress.requiredLessonsCompleted
course.progress.requiredLessonsTotal
course.progress.requiredCapstonesCompleted
course.progress.requiredCapstonesTotal
course.progress.xp                        integer (sum of xp_awarded across all completed missions)
course.progress.nextMissionId             mission ID string or null
course.progress.completedAt              ISO 8601 datetime or null
```

These fields are the single source of truth for course completion. Do not add a duplicate `completion` wrapper.
The names `completedLessons`, `totalLessons`, `completedCapstones`, and `totalCapstones` are deprecated field names from an earlier schema version. Do not use them. They are not valid field names at any level; use the `required*` variants defined above.

The same `required*` field names also appear on each `modules[]` object in `GET /course`, scoped to that module. The naming is identical; context (top-level vs module object) determines scope.

## Backend Modules

```text
config.py
  Loads environment variables and validates local-only endpoint rules.

aws_client.py
  Creates boto3 clients pointed at Floci.

mission_loader.py
  Reads mission YAML files and validates authoring contracts.

validators/
  Contains shared validation primitives.

models.py
  SQLite models for profile, progress, attempts, step progress, help usage, and scores. Badge data is derived at query time from mission_progress and course_completion; there is no separate badge table.

services/progress.py
  Handles mission status, XP, attempts, and unlock behavior.

services/reset.py
  Deletes owned resources safely.

services/migrations.py
  Applies SQLite schema migrations idempotently.

services/course.py
  Builds course map, completion state, and capability progress.

services/scoring.py
  Computes capstone scores and mastery levels.

services/diagnostics.py
  Produces setup and runtime diagnostic issues.

routes/
  FastAPI route modules.
```

## Privacy, Logging, And Observability

Infra Quest is local-first. No remote telemetry is enabled by default.

Logging rules:

- use structured logs where practical
- log route, mission ID, check type, pass/fail, and duration
- do not log AWS credentials
- do not log full command strings if they may contain secrets in future missions
- do not log request payload bodies unless explicitly safe
- local logs may include deterministic resource names

Useful events:

```text
runtime_status_checked
mission_started
step_validated
mission_validated
mission_completed
hint_used
mission_reset
course_completed
setup_issue_detected
```

Settings or docs must explain:

- progress is local
- where local data is stored
- how reset affects progress and resources
- no remote telemetry is sent by default

## Browser And Performance Support

Supported browsers:

```text
latest Chrome
latest Edge
latest Firefox
latest Safari
```

Minimum responsive widths:

```text
320px mobile
768px tablet
1280px desktop
```

Performance budgets on a healthy local runtime:

- course map usable within 2 seconds after page load
- mission detail usable within 2 seconds after navigation
- step validation response visible within 5 seconds for normal checks
- full mission validation response visible within 10 seconds for integrated checks
- reset response visible within 10 seconds for normal owned resources

If an operation exceeds the budget, UI must show progress and avoid duplicate submissions.

## Authoring Workflow

Every new mission must include:

- `mission.yml`
- deterministic resource names
- local-only commands
- owned resources for reset
- checks for every target state
- at least one nudge, diagnosis, or repair hint for common failures
- debrief copy
- tests for loader validation and validator behavior

Authoring validation must catch:

- missing required fields
- duplicate IDs
- invalid module references
- invalid command references
- invalid check references
- unsafe AWS commands
- target-state items with no proof path
- missing owned resources for created resources

Contributor preview path:

1. Run backend loader tests.
2. Run local-only scan.
3. Start the stack.
4. Open the mission from the course map.
5. Run the happy path.
6. Run reset.
7. Run one failed validation path.

## Validation Primitives

Initial check types:

```text
runtime_floci_available
s3_bucket_exists
s3_object_exists
s3_object_body_equals
sqs_queue_exists
sqs_message_available
sns_topic_exists
sns_subscription_exists
lambda_function_exists
lambda_invoke_matches
apigateway_route_exists
apigateway_invoke_matches
dynamodb_table_exists
dynamodb_item_exists
workflow_http_writes_dynamodb
workflow_http_sends_sqs
```

Every validator returns:

```json
{
  "id": "bucket-exists",
  "type": "s3_bucket_exists",
  "passed": true,
  "message": "Bucket launchdesk-assets exists."
}
```

Failure messages should name the missing or incorrect resource state.

Validator side-effect rules:

- Validators should be read-only whenever possible.
- Validators must be idempotent.
- Validators must not consume learner-created queue messages unless the check explicitly documents that behavior.
- Workflow validators that must send a test HTTP request should use deterministic test IDs and cleanly handle repeated validation.
- Validators must not create real AWS resources.
- Validators must not mutate progress directly; progress changes happen only in the validation service after check results are returned.

## Frontend Routes

```text
/                 Course map
/missions/[id]    Mission workbench
/profile          XP, badges, progress
/settings         Local runtime status, data storage info, and privacy copy
```

The first screen is the actual lab experience, not a marketing landing page.

`/settings` must render:

- runtime status summary (same data as `GET /runtime/status`)
- where local progress is stored (`DATABASE_URL` path)
- how to reset local progress (`POST /missions/{id}/reset` or `reset-lab.sh`)
- privacy statement: no remote telemetry by default
- link to docs or README for advanced recovery

`/settings` is a read-only informational route in the MVP. It does not expose mutation controls beyond linking to the reset flows already in the workbench.

## Frontend Components

### `MissionMap`

Shows modules, submodules, capstones, progress, locked states, and capability unlocks.

### `MissionWorkbench`

Owns mission detail layout.

Responsibilities:

- start mission
- track active step
- call step validation
- call final validation
- pass proof state to child components

### `MissionBrief`

Shows:

- title
- practical request
- services
- XP
- estimated time
- local-only status

### `MissionStepList`

Shows all steps with active, pending, checked, and failed states.

### `MissionStepCard`

Shows:

- title
- goal
- why
- target state
- action
- `Show CLI syntax`
- copy command after reveal
- `Check Step`
- step validation feedback

### `ResourceProofBoard`

Shows current known validation/proof state.

Until validation runs, proof items show pending, not failed.

Initial mapping:

| Check type | Visual resource |
| --- | --- |
| `runtime_floci_available` | Runtime status |
| `s3_bucket_exists` | S3 bucket node |
| `s3_object_exists` | Object row inside bucket |
| `s3_object_body_equals` | Object content proof |
| `sqs_queue_exists` | SQS queue node |
| `sqs_message_available` | Message badge inside queue |
| `sns_topic_exists` | SNS topic node |
| `sns_subscription_exists` | Topic-to-queue connection |
| `lambda_function_exists` | Lambda function node |
| `lambda_invoke_matches` | Invocation result badge |
| `apigateway_route_exists` | API route node |
| `apigateway_invoke_matches` | Route response badge |
| `dynamodb_table_exists` | Table node |
| `dynamodb_item_exists` | Item row inside table |
| `workflow_http_writes_dynamodb` | HTTP-to-DynamoDB workflow proof |
| `workflow_http_sends_sqs` | HTTP-to-SQS workflow proof |

Unmapped check types must render as generic proof rows.

### `CoachPanel`

Shows:

- mission status
- attempts
- hints
- reset
- final validation
- XP after completion

### `ContinuityPanel`

Shows LaunchDesk capabilities already online:

- storage
- API
- database
- queue
- events
- worker
- end-to-end flow

## UI Rules

- Do not show a raw command list as the main mission body.
- Keep command blocks hidden until requested.
- Keep proof states compact and readable.
- Use clear icons and compact badges.
- Keep the dark graphite/emerald/lime visual direction unless the design system changes.
- Avoid childish RPG visuals.
- Do not use large hero copy inside the workbench.
- Text must fit on mobile and desktop.
- Failed checks should be understandable without AWS expertise.

## Persistence Rules

Track:

- profile XP
- stored mission progress status: `not_started`, `started`, or `completed`
- derived API mission status: `locked`, `available`, `started`, or `completed`
- started timestamp
- completed timestamp
- attempts
- hints used
- help usage by level
- step validation attempts
- latest step status
- latest check results per step
- XP awarded
- badges or capability completions
- optional capstone scores

XP rules:

- Award XP only on first full mission completion.
- Step validation never awards XP.
- Re-validating a completed mission never duplicates XP.
- Hint penalties apply once per hint before XP award.

Unlock rules:

- A mission is available when all prerequisites are completed.
- `locked` and `available` are derived API statuses, not authoritative database states.
- Capstones are available when required module lessons are completed.
- Completed missions remain completed after API restart.
- `unlockedMissionIds` in a validation response contains the IDs of all missions whose API status transitions from `locked` to `available` as a direct result of this validation completing the current mission. An agent must compute this by evaluating which missions list the just-completed mission as a prerequisite and now have all prerequisites satisfied. `unlockedMissionIds` is empty when the mission was already previously completed (re-validation), when no missions depend on this mission, or when step-scoped validation is used.
- A prerequisite is considered satisfied if a `mission_progress` row exists with `status: completed`, regardless of whether the mission still exists in the current curriculum. Orphaned prerequisites (missions removed from `course.yml` but with completion records) count as satisfied. This ensures progress is never blocked by curriculum changes alone.

Capstone score persistence:

- Store latest score.
- Store best score.
- Store latest mastery level.
- Store best mastery level.
- Do not erase historical completion when a later replay scores lower.

Step progress persistence:

- Persist latest status per mission step.
- Persist validation attempt history.
- Persist latest check result messages for proof board resume.
- Mark proof state `stale` after resource reset.
- Do not mark mission completed from step progress alone.

Help usage persistence:

- Persist hint ID, level, timestamp, and mission ID.
- Persist repeated use idempotently.
- Include help usage in XP and capstone independence calculations when configured.

## Reset Rules

Reset uses mission `owned_resources`.

Supported owned resource types:

```text
s3_bucket
s3_object
sqs_queue
sns_topic
lambda_function
apigateway_api
dynamodb_table
```

Reset must be idempotent. Missing resources are not fatal.

Reset invariants:

- reset never decreases `profile.total_xp`
- reset never clears `xp_awarded` for a completed mission
- reset never clears best capstone score
- reset may mark latest proof state as `stale`
- reset may clear step-progress rows only according to reset mode

## UX State Machines

The frontend must model UX states explicitly. Do not infer every state from ad hoc booleans inside components.

### Runtime State

```text
checking
online
api_offline
floci_offline
database_offline
setup_degraded
unknown_error
```

Runtime effects:

- `online`: all actions enabled according to mission status
- `api_offline`: render cached/static shell if possible, disable API actions
- `floci_offline`: allow reading content, disable validation and reset
- `database_offline`: allow reading content, disable progress-changing actions
- `setup_degraded`: name the setup issue and show local retry/troubleshooting
- `unknown_error`: show retry and local troubleshooting copy

### Mission State

```text
locked
available
started
completed
resetting
reset_failed
```

Mission state controls:

- `locked`: show prerequisites and link to next required mission
- `available`: show Start as primary action
- `started`: show active step and validation actions
- `completed`: show debrief, proof summary, and next mission
- `resetting`: disable destructive or duplicate actions
- `reset_failed`: show failed resource cleanup details and retry

### Step State

```text
not_started
active
checking
passed
failed
no_checks
blocked
stale
```

Step behavior:

- a passed step can still be reopened
- a failed step remains active until passed or manually changed
- a step with no checks shows `no_checks` and explains that final validation proves it
- future steps are inspectable but visually secondary
- `stale` is shown after a resource reset; it prompts re-validation without implying failure. The persisted `stale` status from `step_progress` maps to this UX state. `checking` is transient frontend-only and is never persisted.

### Command State

```text
hidden
revealed
copied
copy_failed
```

Command behavior:

- hidden is default
- reveal state persists while the learner stays on the mission
- copy feedback must be textual and accessible

### Proof State

```text
pending
passed
failed
unknown
stale
```

Proof behavior:

- pending before validation
- passed or failed after validation
- unknown when the check cannot run
- stale when reset or runtime changes make previous proof unreliable

### Hint State

```text
unused
revealed
applied
unavailable
```

Hint behavior:

- hint penalty applies once
- hint copy is hidden until revealed
- hints remain visible after use

### Completion State

```text
not_started
in_progress
completed
replaying
improving_score
```

Completion behavior:

- completed course state remains visible after restart
- replay does not remove completion
- lower replay scores do not erase best score

## UX Flow Requirements

### First Launch

- Course map loads when API and Floci are online.
- If API is offline, app shell shows local troubleshooting.
- If Floci is offline, course content remains readable but validation is disabled.

### Course Map

- Shows module order from `GET /course`.
- Shows the next recommended mission in the first viewport.
- Shows locked prerequisites.
- Shows module capstones separately from normal lessons.
- Shows capability progress.

### Mission Workbench

- Initial order on desktop: brief, steps, active step, proof board, coach, continuity.
- Initial order on mobile: brief, active step, proof board, coach, continuity, step list.
- Commands are hidden until reveal.
- Step validation updates the active step and proof board.
- Full validation updates mission progress, XP, unlocks, debrief, and continuity.

### Failed Check Recovery

- Keep failed step active.
- Show failed proof row near the related target state.
- Preserve successful proof rows.
- Offer retry before reset.
- Offer reset only as a secondary action.

### Returning Learner

- Use persisted progress to show next recommended mission.
- For a started mission, choose the first step without a passing scoped result when available.
- If scoped step history is unavailable, open the first step and show mission status.

### Capstone Mode

- Capstone missions use the same workbench but with reduced command prominence.
- Capstones may delay command reveal until after the learner reviews target architecture.
- Capstone proof board must group checks by service and end-to-end behavior.
- Capstone completion shows a system debrief, not only XP.

## Accessibility And Responsive Rules

- All buttons and icon controls must have accessible names.
- Focus order must match visual reading order.
- Status must never rely on color alone.
- Validation result changes must be reachable to screen readers without requiring page reload.
- Command blocks must be keyboard focusable and horizontally scrollable on small screens.
- Tap targets should be at least 40px tall.
- Text must not overlap or overflow controls at 320px width.
- Course map and workbench must work at desktop, tablet, and mobile widths.

## Content Quality Gates

Mission content is release-ready only when:

- motivation names a concrete product problem
- theory is shorter than the build section
- thought process includes at least one rejected alternative or tradeoff
- target state maps directly to checks
- every check has learner-readable failure copy
- hints teach the next diagnostic move
- help levels escalate from nudge to diagnosis to repair
- debrief explains real production relevance
- local-only endpoint appears in every AWS CLI command
- command labels are action-oriented
- resource names are deterministic

## Manual Usability Gate

Before the course is considered polished, run at least three beginner usability sessions.

Minimum script:

1. Start the lab from README.
2. Complete Module 0.
3. Complete the first storage lesson.
4. Trigger and recover from one failed check.
5. Stop and restart the lab.
6. Resume from persisted progress.

Pass criteria:

- learner completes without source-code help
- learner can explain what capability was added
- learner can recover from one failed check using UI feedback or help ladder
- learner does not ask whether real AWS is being used
- observed layout has no blocking mobile or keyboard issue

## Verification Strategy

Backend:

```bash
cd apps/api && uv run pytest
```

Frontend:

```bash
cd apps/web && bun run build
```

Full local verification:

```bash
make verify
```

Required `make verify` sequence:

```text
local-only scan
backend tests
frontend typecheck
frontend build
mission authoring validation
smoke test
```

CI must run the same checks where supported by the environment.

Local-only scan must fail on:

- Docker `latest` tags
- AWS CLI examples missing endpoint
- suspicious AWS keys
- unpinned dependency ranges
- real AWS endpoints outside explicit denylist documentation

## End-To-End Acceptance Matrix

The release candidate must pass these manual/browser flows:

| Flow | Required result |
| --- | --- |
| Clean setup | `docker compose up --build` starts web, API, and Floci |
| Runtime degraded | stopping Floci disables validation and shows local troubleshooting |
| Course map | modules, capstones, next mission, and progress render correctly |
| Guided lesson | Module 0 and first storage lesson complete with browser-guided flow and local terminal commands |
| Failed check | learner can recover from one failed step without reset |
| Reset | resource reset deletes only owned resources and marks proof stale |
| Restart/resume | progress and step state survive API restart |
| Locked lesson | direct locked route shows prerequisites |
| Capstone | if target release includes a required capstone, integrated capstone returns completion and mastery level |
| Replay | lower replay score does not erase best score |
| Mobile | 320px layout has no overlap and primary actions are reachable |
| Keyboard | primary course and workbench controls are keyboard reachable |
| Privacy | logs contain no credentials and no remote telemetry is sent |

## Definition Of Done

Implementation is done only when:

- all planned phases required for the target release are complete
- `make verify` passes
- backend tests pass directly
- frontend typecheck and build pass directly
- local-only scan passes
- clean-machine setup passes
- end-to-end acceptance matrix passes
- beginner usability gate passes or is explicitly marked pending for pre-release
- no release-blocking bugs remain
- README matches the actual setup and verification path
- final handoff lists commands run, manual flows run, and known non-blocking issues

## Acceptance Criteria

- There is exactly one PRD, one spec, and one plan document.
- Mission loader supports curriculum fields and steps.
- Existing missions can load during migration.
- Invalid command or check references fail fast.
- `GET /missions` supports module and mission type metadata.
- `GET /course` supports module, capstone, capability, and progress rendering.
- `GET /missions/{id}` includes motivation, theory, thought process, debrief, and steps.
- Step validation scopes checks and never awards XP.
- Full validation still awards XP once.
- Capstone validation returns a mastery score when configured.
- Proof board maps known check types and shows generic rows for unknown checks.
- Reset removes owned local resources only.
- Frontend implements explicit runtime, mission, step, command, proof, and hint states.
- Course map and mission workbench meet accessibility and responsive rules.
- Mission content passes the content quality gates before release.
- Step progress and help usage persist across restarts.
- Setup diagnostics distinguish local runtime failures from lesson failures.
- Course completion and replay preserve historical completion and best capstone score.
- Data model and migrations preserve learner progress across upgrades.
- Logging and privacy rules prevent credential leakage and remote telemetry by default.
- Authoring validation and release verification gates pass.
- All commands and backend AWS calls remain local-only.
