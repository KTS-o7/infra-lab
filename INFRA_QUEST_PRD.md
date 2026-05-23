# Infra Quest PRD

## Purpose

Infra Quest is a local-first, zero-cost, gamified AWS learning lab for beginners. It lets learners practice AWS concepts through guided missions while all infrastructure calls run against Floci locally instead of real AWS.

This PRD is written to be executable by a coding agent. It defines user flows, product behavior, edge cases, acceptance criteria, and validation rules. Technical architecture and version pinning live in `INFRA_QUEST_SPEC.md`. Build sequencing lives in `INFRA_QUEST_PLAN.md`.

## Product Outcome

A beginner should be able to:

1. Start the lab with Docker.
2. Open the web app.
3. Understand that everything is local.
4. Complete an AWS-style mission.
5. Validate the result from the browser.
6. Receive clear pass/fail feedback.
7. Earn XP once per mission.
8. Reset the mission and try again.

No real AWS account, credentials, cloud resources, or paid services are required.

## Target Users

### Primary User: Beginner Cloud Learner

Profile:

- knows basic terminal usage
- may not know AWS concepts
- may not understand endpoints, regions, credentials, or resource names
- wants hands-on practice without cost risk

Needs:

- copyable commands
- short explanations
- immediate feedback
- safe reset path
- no hidden cloud dependency

### Secondary User: Instructor or Workshop Host

Profile:

- wants a repeatable local lab for students
- needs predictable setup
- wants clear progress and reset behavior

Needs:

- deterministic missions
- reproducible environment
- easy troubleshooting
- local-only guarantee

### Secondary User: Contributor

Profile:

- adds new missions or validators
- works with the codebase directly

Needs:

- strict mission schema
- reusable validation primitives
- clear tests and acceptance criteria

## MVP Scope

The MVP includes:

- local Docker Compose runtime
- Floci local AWS emulator
- Next.js web app
- FastAPI backend
- SQLite progress storage
- local-only safety guardrails
- mission map
- mission detail page
- copyable CLI commands
- validation results
- XP tracking
- hint usage
- reset behavior
- S3 mission
- SQS mission
- smoke tests

## Out of Scope for MVP

- real AWS deployment
- user accounts or authentication
- cloud-hosted leaderboards
- multiplayer features
- EC2, EKS, RDS, or VPC-heavy missions
- payment, billing, or usage metering
- production SaaS hosting
- remote telemetry

## Product Principles

- The app should teach by doing, not by long explanations.
- Every command must be safe to run locally.
- Validation should inspect actual local infrastructure state.
- Failure feedback should tell the learner what is missing.
- Reset should be reliable and visible.
- The first screen should be the lab, not a marketing page.
- The learner should never need to understand Docker internals to complete a mission.

## Glossary

| Term | Meaning |
| --- | --- |
| Mission | A guided learning task with instructions, commands, checks, XP, and reset behavior. |
| Check | A single validation assertion, such as "bucket exists". |
| Validation | The backend process that inspects Floci state and returns pass/fail results. |
| XP | Points awarded for completing missions. |
| Hint | Optional guidance that may reduce maximum XP. |
| Reset | Action that removes or restores resources for a mission. |
| Floci | Local AWS-compatible emulator used instead of real AWS. |
| Local-only | Product guarantee that no AWS calls go to real AWS endpoints. |

## Core User Flows

### Flow 1: First Launch Happy Path

Preconditions:

- Docker is installed.
- Ports `3000`, `8000`, and `4566` are available.
- User is in the repository root.

User actions:

1. Runs `docker compose up --build`.
2. Opens `http://localhost:3000`.

System behavior:

1. Floci starts on port `4566`.
2. API starts on port `8000`.
3. Web app starts on port `3000`.
4. Web app loads mission list from API.
5. Web app displays local runtime status.

Expected UI:

- mission map is visible
- first mission is available
- locked missions are visibly disabled
- runtime status shows API and Floci online
- local-only banner is visible in the app shell

Acceptance criteria:

- user sees the mission map without manual configuration
- no real AWS credentials are requested
- no command examples omit `--endpoint-url http://localhost:4566`

### Flow 2: Runtime Unhealthy on Launch

Preconditions:

- Web app is running.
- API or Floci is unavailable.

User actions:

1. Opens `http://localhost:3000`.

System behavior:

1. Web app requests runtime status.
2. Request fails or reports unhealthy dependency.
3. Web app displays actionable runtime error.

Expected UI:

- runtime offline banner is visible
- mission validation actions are disabled
- user sees which service is unavailable: API, Floci, or both
- copyable troubleshooting command is shown:

```bash
docker compose ps
```

Acceptance criteria:

- UI does not crash
- validation cannot be triggered while backend is unavailable
- error copy does not suggest real AWS setup

### Flow 3: Browse Mission Map

Preconditions:

- Runtime is healthy.
- Missions are loaded by API.

User actions:

1. Opens the app.
2. Scans mission map.
3. Clicks an available mission.

System behavior:

1. Web app calls `GET /missions`.
2. App renders missions in curriculum order.
3. Available mission cards navigate to mission detail.
4. Locked mission cards show locked state.

Expected UI:

- each card shows title, service, difficulty, XP, and status
- completed missions show completed state
- started missions show in-progress state
- locked missions are non-primary and explain prerequisite

Acceptance criteria:

- mission order is deterministic
- missing mission list shows empty state, not a crash
- duplicate mission IDs are rejected by backend

### Flow 4: Start Mission

Preconditions:

- Mission exists.
- Mission status is `available`.

User actions:

1. Opens mission detail.
2. Clicks Start.

System behavior:

1. Web app calls `POST /missions/{mission_id}/start`.
2. Backend changes status from `available` to `started`.
3. Backend records `started_at` if not already set.
4. Web app refreshes mission detail.

Expected UI:

- command panel becomes prominent
- Validate button is enabled if runtime is healthy
- Reset button is visible
- mission status shows Started

Acceptance criteria:

- starting an already started mission is idempotent
- starting a completed mission does not remove completion
- starting a locked mission returns an error

### Flow 5: Copy and Run Commands

Preconditions:

- Mission is started.
- Runtime is healthy.

User actions:

1. Clicks copy on a command.
2. Pastes and runs command in terminal.

System behavior:

1. UI copies the exact command.
2. Command targets `http://localhost:4566`.
3. User-created resources appear in Floci.

Expected UI:

- copy button changes to copied state briefly
- command remains visible
- command includes local endpoint

Acceptance criteria:

- every AWS CLI command includes `--endpoint-url http://localhost:4566`
- command copy state does not shift layout
- commands are shell-safe and deterministic

### Flow 6: Validate Successful Mission

Preconditions:

- Mission is started.
- Learner has created the expected resources in Floci.

User actions:

1. Clicks Validate.

System behavior:

1. Web app calls `POST /missions/{mission_id}/validate`.
2. Backend runs all mission checks.
3. All checks pass.
4. Backend marks mission completed.
5. Backend awards XP if not previously awarded.
6. Backend unlocks next mission if applicable.
7. Web app displays success state.

Expected UI:

- success message is shown
- all checks are marked passed
- XP awarded is shown
- next mission CTA is visible when applicable
- Validate button remains available for recheck

Acceptance criteria:

- XP is awarded exactly once per mission completion
- repeated validation does not duplicate XP
- validation result includes check-level details
- mission remains completed after browser refresh

### Flow 7: Validate Partial Failure

Preconditions:

- Mission is started.
- Learner completed only some required actions.

User actions:

1. Clicks Validate.

System behavior:

1. Backend runs all checks.
2. Some checks pass and some fail.
3. Mission remains started.
4. Backend records validation attempt.
5. No XP is awarded.

Expected UI:

- failed checks are visible
- passed checks are visible
- feedback explains what is missing
- user can run more commands and validate again

Acceptance criteria:

- partial results are returned in stable order
- no destructive reset happens during validation
- no XP is awarded until all required checks pass

### Flow 8: Validate Before Starting

Preconditions:

- Mission exists.
- Mission status is `available`.

User actions:

1. Opens mission detail.
2. Clicks Validate if button is visible, or calls endpoint manually.

System behavior:

1. UI should normally hide or disable Validate before Start.
2. Backend rejects manual validation before start.

Expected API result:

```json
{
  "error": {
    "code": "MISSION_NOT_STARTED",
    "message": "Start this mission before validating it."
  }
}
```

Acceptance criteria:

- backend enforces state even if frontend is bypassed
- UI explains the required next action

### Flow 9: Use Hint

Preconditions:

- Mission is started.
- Mission has at least one unused hint.

User actions:

1. Clicks Show Hint.

System behavior:

1. Web app calls hint endpoint or local mission interaction endpoint.
2. Backend records hint usage.
3. Backend applies XP penalty once per hint.
4. Web app reveals hint text.

Expected UI:

- hint text becomes visible
- possible XP updates
- used hint remains visible after refresh

Acceptance criteria:

- same hint cannot apply penalty twice
- used hints persist after restart
- completed mission XP is not recalculated downward after completion

### Flow 10: Reset Started Mission

Preconditions:

- Mission exists.
- Mission status is `started`.

User actions:

1. Clicks Reset.
2. Confirms reset if confirmation is required.

System behavior:

1. Web app calls `POST /missions/{mission_id}/reset`.
2. Backend runs mission reset logic.
3. Backend removes mission-owned resources from Floci.
4. Backend keeps mission available or started according to reset policy.
5. Web app refreshes mission state.

Expected UI:

- reset progress is shown
- validation results are cleared
- commands remain available

Acceptance criteria:

- reset is idempotent
- reset succeeds even if resources are already missing
- reset never deletes resources outside the mission namespace

### Flow 11: Reset Completed Mission

Preconditions:

- Mission status is `completed`.

User actions:

1. Clicks Reset.

System behavior:

1. Backend runs mission reset logic.
2. Completion history remains recorded.
3. XP is not removed.
4. Mission can be practiced again.

Expected UI:

- mission still shows completed badge
- practice state can show resources reset
- XP remains unchanged

Acceptance criteria:

- resetting completed mission does not reduce total XP
- repeated completion after reset does not award duplicate XP

### Flow 12: App Restart with Existing Progress

Preconditions:

- User completed at least one mission.
- Docker services are restarted.

User actions:

1. Runs `docker compose down`.
2. Runs `docker compose up`.
3. Opens app.

System behavior:

1. API reads existing SQLite data.
2. Web app shows persisted progress.

Expected UI:

- completed missions remain completed
- XP remains accurate
- used hints remain visible

Acceptance criteria:

- progress persists across normal restart
- Floci resources may or may not persist depending on configured volume, but progress state remains consistent

## Mission State Machine

Allowed states:

```text
locked
available
started
completed
```

Allowed transitions:

```text
locked -> available
available -> started
started -> completed
started -> available
completed -> completed
completed -> available
```

Rules:

- `locked -> available` happens when prerequisite missions are completed.
- `available -> started` happens when learner starts a mission.
- `started -> completed` happens only when all checks pass.
- `started -> available` can happen on reset if reset policy chooses available.
- `completed -> completed` happens on repeated validation.
- `completed -> available` can happen on reset for practice mode.
- No transition should duplicate XP.

## Error Handling

All API errors should use this shape:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message.",
    "details": {}
  }
}
```

Required error codes:

```text
RUNTIME_UNAVAILABLE
FLOCI_UNAVAILABLE
MISSION_NOT_FOUND
MISSION_LOCKED
MISSION_NOT_STARTED
MISSION_SCHEMA_INVALID
VALIDATION_FAILED
RESET_FAILED
LOCAL_ONLY_VIOLATION
```

Error copy must never instruct the learner to configure real AWS.

## Edge Case Matrix

| Case | Expected Behavior |
| --- | --- |
| Floci is down | Runtime status unhealthy; validation disabled; API returns `FLOCI_UNAVAILABLE`. |
| API is down | Web shows runtime offline banner; mission actions disabled. |
| Web cannot load missions | Show error state with retry. |
| Mission YAML invalid | Backend startup or mission load fails visibly with `MISSION_SCHEMA_INVALID`. |
| Duplicate mission IDs | Backend rejects mission load. |
| Learner uses wrong bucket name | S3 bucket check fails with specific message. |
| Learner uploads wrong object body | Body check fails and reports expected object content mismatch. |
| Learner validates before start | Backend returns `MISSION_NOT_STARTED`. |
| Learner resets missing resources | Reset succeeds idempotently. |
| Learner refreshes during validation | UI can recover by fetching latest mission progress. |
| SQLite DB missing | Backend creates schema automatically. |
| SQLite DB corrupt | Backend fails with clear local data reset guidance. |
| Port `4566` in use | Docker Compose fails; README troubleshooting covers it. |
| Real AWS endpoint configured | Backend refuses to start with `LOCAL_ONLY_VIOLATION`. |

## Acceptance Test Matrix

### Product Tests

| ID | Scenario | Expected Result |
| --- | --- | --- |
| PRD-001 | Fresh launch | Mission map loads and runtime is healthy. |
| PRD-002 | API unavailable | Web shows offline state and disables mission actions. |
| PRD-003 | Floci unavailable | API reports unhealthy dependency. |
| PRD-004 | Start available mission | Mission status changes to started. |
| PRD-005 | Start locked mission | API returns `MISSION_LOCKED`. |
| PRD-006 | Validate before start | API returns `MISSION_NOT_STARTED`. |
| PRD-007 | Validate partial S3 mission | Failed check explains missing resource. |
| PRD-008 | Validate successful S3 mission | Mission completes and XP is awarded once. |
| PRD-009 | Repeat successful validation | XP is not duplicated. |
| PRD-010 | Reset started mission | Mission resources are removed idempotently. |
| PRD-011 | Reset completed mission | XP remains and mission can be practiced again. |
| PRD-012 | Restart app | Progress persists. |

### Safety Tests

| ID | Scenario | Expected Result |
| --- | --- | --- |
| SAFE-001 | `AWS_ENDPOINT_URL` missing | API refuses to start. |
| SAFE-002 | endpoint contains `amazonaws.com` | API refuses to start. |
| SAFE-003 | CLI command missing endpoint | verification script fails. |
| SAFE-004 | Docker image uses `latest` | verification script fails. |
| SAFE-005 | real-looking AWS key appears | verification script fails unless in explicit denylist test fixture. |

## MVP Completion Definition

MVP is complete when:

- `docker compose up --build` starts all services.
- `http://localhost:3000` loads mission map.
- runtime status reports API and Floci healthy.
- learner can complete S3 mission.
- learner can complete SQS mission.
- XP is awarded once per mission.
- reset works for started and completed missions.
- progress persists across restart.
- `make verify` passes.
- safety tests prove real AWS endpoints are rejected.

## Copy Requirements

Required global copy:

```text
This lab runs locally. It does not use real AWS.
```

Required CLI note:

```text
Every AWS CLI command in this lab must include --endpoint-url http://localhost:4566.
```

Forbidden copy:

- instructions to create an AWS account
- instructions to configure real AWS credentials
- instructions to remove local endpoint targeting

## Agent Implementation Notes

When implementing from this PRD:

- Build backend enforcement before relying on frontend disabled states.
- Keep validation idempotent.
- Keep reset idempotent.
- Add tests for every edge case that can be automated.
- Prefer deterministic local resource names.
- Do not introduce external services.
- Do not add telemetry.
- Do not add auth unless explicitly requested later.
