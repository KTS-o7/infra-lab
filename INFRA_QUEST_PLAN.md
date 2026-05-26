# Infra Quest Plan

## Product Direction

Infra Quest should teach cloud by having a beginner build one real project in small, cumulative steps.

The course should not be organized as a list of AWS services. Beginners do not wake up wanting to learn S3, SQS, Lambda, or DynamoDB in isolation. They want to know how real applications are hosted, how files are stored, how APIs work, how background jobs run, how data is persisted, and how a system becomes reliable enough to trust.

The product direction is:

```text
Learn cloud by rebuilding a production-style SaaS platform inside a safe local sandbox.
```

Each lesson starts from a practical product need, then introduces the cloud concept and service only when that service solves the need.

Video is intentionally out of scope for now. The first version should focus on written theory, guided reasoning, hands-on implementation, validation, and cumulative project continuity.

## Core Learning Promise

A learner should finish the course able to explain and build:

- a local cloud sandbox boundary
- static/object file storage
- a serverless API
- durable application state
- async job processing
- event fanout
- service composition
- basic reliability and debugging workflows
- a final multi-service SaaS-like platform with clear proof that it works

The learner should not only know which command to run. They should understand why the system needs each capability, what target state they are creating, how to reason about failures, and how individual resources combine into an application.

## Product Principles

- Teach objectives before services.
- Use modules and submodules, but make every submodule part of one growing project.
- Put theory before implementation, but keep theory short and directly tied to the build.
- Explain motivation explicitly: what breaks without this capability?
- Explain thought process explicitly: how should an engineer decide what to build?
- Keep every lesson hands-on.
- Validate real local infrastructure state, not text answers.
- Keep commands available, but reveal them after the learner understands the target state.
- Build confidence through continuity: each completed mission adds a visible platform capability.
- Keep the entire experience local-only until the learner is ready for real cloud deployment.
- Avoid video dependency in the MVP.

## Target Learner

The primary learner is a cloud beginner who:

- knows basic terminal usage
- can install Docker and run a local app
- may not know AWS services
- may not know distributed systems vocabulary
- wants practical confidence, not certification trivia
- benefits from clear modules, submodules, and progressive capstones

The learner needs enough structure to avoid feeling lost, but enough project realism to avoid toy examples.

## Teaching Model

Every submodule should follow the same learning shape.

### 1. Motivation

State the product problem in plain language.

Example:

```text
Users need to upload onboarding files. If files are stored only on the app server,
they disappear when the server is replaced or restarted.
```

### 2. Theory

Explain the cloud concept that solves the problem.

Example:

```text
Object storage gives the application a durable place for files. A bucket is the
storage boundary. An object is the file plus its key.
```

### 3. Thought Process

Show how an engineer reasons from problem to design.

Example:

```text
We need storage that is independent from the web process. We do not need a database
for raw files. We need a named boundary, stable object keys, and a way to verify the
file exists after upload.
```

### 4. Target State

Describe exactly what should exist after the learner finishes.

Example (from Module 1 — durable file storage):

```text
Bucket: launchdesk-assets
Object: launchdesk-assets/welcome.txt
Body: Welcome to LaunchDesk
```

### 5. Build

Give the guided implementation. The command can be revealed after the learner has seen the target state.

### 6. Proof

Validate the real local sandbox state.

Example:

```text
The bucket exists.
The object exists.
The object body matches the expected content.
```

### 7. Debrief

Connect the local exercise to real-world cloud architecture.

Example:

```text
In a production app, this pattern is used for uploads, generated reports, exports,
static assets, data lakes, and media pipelines.
```

## Course Project

The course project should be a small SaaS-style application backend. The exact brand can change, but the project should have these capabilities:

- users or tenants submit requests
- the platform stores files
- the platform exposes HTTP APIs
- the platform saves structured records
- slow work runs asynchronously
- events notify multiple downstream consumers
- final capstones combine all pieces into a working flow

Working project name:

```text
LaunchDesk: a local SaaS operations platform
```

LaunchDesk starts as a simple app with a static page and grows into a multi-service backend with uploads, APIs, background processing, events, persisted records, and operational proof.

## Course Structure

The canonical `course.yml` module IDs (from `INFRA_QUEST_SPEC.md`) that map to each module described below:

| Module title | `course.yml` module ID |
| --- | --- |
| Module 0: Local Cloud Orientation | `orientation` |
| Module 1: Store Files Outside The App | `storage` |
| Module 2: Expose A Backend API | `api` |
| Module 3: Persist Application Records | `database` |
| Module 4: Move Slow Work Out Of Requests | `async_processing` |
| Module 5: Broadcast Platform Events | `events` |
| Module 6: Compose The Platform | `composition` |
| Module 7: Operate And Debug | `operations` |

Use these IDs in `course.yml`, mission YAML `module:` fields, and any frontend module references. Do not invent alternate IDs.

### Module 0: Local Cloud Orientation

Goal: prove the learner is working inside a safe local cloud sandbox.

Motivation:

Real cloud accounts cost money and can create security risk. Beginners need a place where mistakes are cheap and reversible.

Theory:

- local AWS-compatible endpoint
- fake credentials
- regions
- CLI calls
- difference between local emulation and real AWS

Submodules:

1. Start the lab with Docker.
2. Verify the local endpoint.
3. Inspect fake identity and credentials.
4. List empty cloud resources.
5. Reset the sandbox.

Hands-on proof:

- Floci responds locally.
- No real AWS endpoint is used.
- The app can inspect sandbox state.

Capstone:

Given only the endpoint and fake credentials, prove the sandbox is isolated and ready.

### Module 1: Store Files Outside The App

Goal: add durable object storage to LaunchDesk.

Motivation:

Applications should not rely on local server disk for user uploads, generated reports, or static assets. Server disk is temporary and tied to a process.

Theory:

- object storage
- buckets
- keys
- object bodies
- durability boundary
- app storage versus server filesystem

Submodules:

1. Create the storage boundary.
2. Upload a welcome file.
3. Inspect object state.
4. Replace an object.
5. Delete and recreate storage safely.

Hands-on proof:

- S3 bucket exists.
- Object exists.
- Object body matches expected content.
- Reset removes owned resources.

Capstone:

Create a `launchdesk-assets` bucket and upload the files needed for the first LaunchDesk onboarding page.

### Module 2: Expose A Backend API

Goal: create a serverless HTTP entrypoint for LaunchDesk.

Motivation:

Users and frontend apps need a stable HTTP boundary. The backend should receive requests without requiring learners to manage a long-running server.

Theory:

- HTTP APIs
- routes
- methods
- request and response payloads
- serverless functions
- API Gateway to Lambda integration

Submodules:

1. Create a tiny Lambda function.
2. Invoke the function directly.
3. Create an HTTP API.
4. Add a route.
5. Connect the route to the function.
6. Send a real HTTP request.

Hands-on proof:

- Lambda function exists.
- API route exists.
- Route invokes the expected function.
- Response status and body match expected output.

Capstone:

Build `POST /lead` for LaunchDesk. The endpoint accepts a lead payload and returns a normalized response.

### Module 3: Persist Application Records

Goal: store structured LaunchDesk records.

Motivation:

APIs are not useful if every request is forgotten. The platform needs durable state for leads, tasks, tenants, and processing status.

Theory:

- NoSQL table model
- partition keys
- item shape
- reads and writes
- access patterns before schema

Thought process emphasis:

Learners should understand that database design starts from the questions the app must answer. The table shape is not arbitrary.

Submodules:

1. Define the access pattern.
2. Create a table.
3. Write an item.
4. Read an item by key.
5. Connect API request handling to persistence.

Hands-on proof:

- DynamoDB table exists.
- Key schema is correct.
- Expected item can be read.
- API request writes a record.

Capstone:

Create a `launchdesk-leads` table and make `POST /lead` persist a submitted lead.

### Module 4: Move Slow Work Out Of Requests

Goal: add async processing to LaunchDesk.

Motivation:

User-facing requests should not block on slow work like enrichment, email, exports, or downstream notifications. The app needs a handoff point.

Theory:

- queues
- producers and consumers
- message visibility
- async handoff
- retries
- why queue URLs matter

Submodules:

1. Create a queue.
2. Send a message.
3. Receive a message.
4. Connect API submission to queue handoff.
5. Process the queued message with a function.

Hands-on proof:

- SQS queue exists.
- Expected message is available.
- API request creates a queue message.
- Worker function handles the message.

Capstone:

When a lead is submitted, enqueue `lead.created` work for background processing.

### Module 5: Broadcast Platform Events

Goal: notify multiple consumers when important things happen.

Motivation:

One business event often has multiple consequences. A new lead may need analytics, email, audit logging, and workflow assignment. Hard-wiring every consumer into the API creates tight coupling.

Theory:

- topics
- subscriptions
- fanout
- event payloads
- topic versus queue
- publisher versus subscriber responsibilities

Submodules:

1. Create a topic.
2. Subscribe a queue.
3. Publish an event.
4. Verify fanout delivery.
5. Add a second consumer.

Hands-on proof:

- SNS topic exists.
- SQS subscription exists.
- Published event reaches the subscribed queue.
- Multiple subscribers can receive the same event.

Capstone:

Publish `lead.created` and deliver it to both an audit queue and a workflow queue.

### Module 6: Compose The Platform

Goal: wire storage, API, database, queue, events, and functions into one working LaunchDesk flow.

Motivation:

Real cloud work is mostly composition. Knowing each service alone is not enough; learners must understand boundaries, dependencies, and data flow.

Theory:

- service boundaries
- event-driven architecture
- synchronous versus asynchronous paths
- resource dependencies
- end-to-end proof

Submodules:

1. Draw the target architecture.
2. Create required resources in dependency order.
3. Deploy the request handler.
4. Deploy the background worker.
5. Submit a full request.
6. Trace the request through the platform.

Hands-on proof:

- API accepts request.
- Lambda handles request.
- DynamoDB stores record.
- SQS receives async work.
- SNS fans out event.
- S3 stores generated artifact or onboarding asset.

Module capstone:

Build the first complete LaunchDesk flow:

```text
POST /lead
  -> validate request
  -> write lead record
  -> publish lead.created
  -> enqueue workflow task
  -> store generated onboarding artifact
```

### Module 7: Operate And Debug

Goal: teach learners how to reason when cloud systems do not work.

Motivation:

Building resources is only half the job. Engineers must inspect state, identify what is missing, and recover safely.

Theory:

- health checks
- logs
- failed validation
- missing resource state
- idempotent commands
- reset versus repair
- basic SLA thinking

Submodules:

1. Read proof board failures.
2. Diagnose missing resources.
3. Diagnose wrong names and payloads.
4. Retry safely.
5. Reset owned resources.
6. Verify recovery.

Hands-on proof:

- Learner can identify a broken route, missing queue, wrong table key, or incorrect object body.
- Learner repairs the system without restarting the whole course.

Capstone:

Given a partially broken LaunchDesk deployment, restore the system until all proof checks pass.

## Final Capstones

### Final Capstone 1: LaunchDesk MVP

Build the complete LaunchDesk local SaaS backend with limited guidance.

Required behavior:

- accept a tenant-scoped lead submission
- persist the lead
- upload or generate an onboarding artifact
- publish a `lead.created` event
- queue background workflow work
- expose an HTTP endpoint
- pass end-to-end validation

Expected services:

- S3
- API Gateway
- Lambda
- DynamoDB
- SQS
- SNS

Success proof:

- all required resources exist
- full request path works
- persisted record is correct
- event path works
- queue message exists
- artifact exists

### Final Capstone 2: Production Readiness Challenge

Extend LaunchDesk toward a production-style system.

Required behavior:

- tenant-aware records
- clear request IDs
- retry-safe background job behavior
- health/proof checks
- failure recovery task
- simple SLA-style target such as "all proof checks pass after reset and rebuild"

This capstone should have fewer direct commands and more prompts. The learner should decide the order of operations using the thought process learned earlier.

## App Experience Requirements

### Course Map

The home screen should show modules, submodules, capstones, and progress.

Required states:

- locked
- available
- started
- completed
- capstone (UI display variant only — not an API status value; applied to missions where `missionType` is `module_capstone` or `final_capstone`)

The map should show that each module adds a capability to the same LaunchDesk platform.

### Mission Workbench

The mission detail page should be the primary learning surface.

Required sections:

- mission request
- motivation
- theory
- thought process
- target state
- guided build step
- revealable command
- proof board
- hints
- reset
- debrief

The learner should see the reason and target state before seeing CLI syntax.

### Continuity Panel

The app should show what has already been built across the course.

Examples:

```text
Storage: launchdesk-assets bucket online
API: POST /lead route online
Database: launchdesk-leads table online
Queue: lead-workflow queue online
Events: lead-events topic online
Worker: lead-worker function online
```

This panel is important because the course is cumulative. It helps learners understand that each module adds to one platform.

### Embedded Terminal

An embedded terminal is desirable, but it should be introduced after the workbench, proof board, and mission state are stable.

Initial scope:

- show command history per mission
- allow copy/paste commands
- preserve continuity between submodules

Later scope:

- run commands inside a constrained local shell
- block real AWS endpoints
- stream command output into the workbench
- link terminal output to validation results

Security note:

Browser-triggered shell execution changes the security model. It should be designed separately and must stay local-only.

## Mission Authoring Requirements

Each mission YAML should support:

- module ID
- submodule ID
- project capability added
- motivation
- theory
- thought process
- target state
- commands
- steps
- checks
- proof board labels
- debrief
- owned resources
- reset behavior

Example shape (partial — curriculum and step fields only):

```yaml
module: storage
submodule: create-storage-boundary
capability: durable_file_storage
motivation: "The app needs files to survive process restarts."
theory: "Object storage keeps files behind a bucket/key model."
thought_process: "Use object storage when the app needs durable blobs, not relational queries."
target_state:
  - label: Bucket
    value: launchdesk-assets
steps:
  - id: create-bucket
    title: Create the storage boundary
    goal: Create an S3 bucket named launchdesk-assets.
    action: Create the bucket in your local AWS sandbox.
    command_id: create-bucket
    check_ids:
      - bucket-exists
```

This is a partial example showing only curriculum and step fields. See `INFRA_QUEST_SPEC.md` Mission Schema for the complete list of required base fields (`id`, `order`, `mission_type`, `required`, `title`, `summary`, `difficulty`, `services`, `xp`, `estimated_minutes`, `prerequisites`, `story`) that every mission YAML must include. A mission YAML missing required base fields will fail the loader.

## Implementation Roadmap

### Agent Execution Contract

An implementation agent must work phase by phase and keep the repo releasable after each completed phase.

Rules:

- Read `INFRA_QUEST_PRD.md`, `INFRA_QUEST_SPEC.md`, and this plan before coding.
- Implement phases in order unless the user explicitly changes priority.
- Do not invent alternate API contracts, data fields, route names, or status values.
- Add or update tests in the same phase as the behavior.
- Run the narrow tests for the changed area before moving on.
- Run `make verify` before final handoff.
- Stop and update the docs if implementation reveals an unresolved contradiction.
- Leave no release-blocking bug known at final handoff.

Phase completion report format:

```text
Phase:
Files changed:
Behavior implemented:
Tests run:
Manual flows run:
Known issues:
Next phase:
```

### Phase 1: Consolidate Curriculum Structure

Deliverables:

- one canonical PRD document
- one canonical spec document
- one canonical plan document
- module/submodule taxonomy
- project narrative
- capstone definitions
- mission authoring fields for motivation, theory, thought process, and debrief

Tasks:

- Remove stale duplicate documents.
- Keep `INFRA_QUEST_PRD.md` as the canonical PRD.
- Keep `INFRA_QUEST_SPEC.md` as the canonical spec.
- Keep `INFRA_QUEST_PLAN.md` as the canonical plan.
- Define module IDs and ordering.
- Define the LaunchDesk project capabilities.
- Decide which existing missions map to each module.

Acceptance:

- The repo has one PRD, one spec, and one plan.
- The plan clearly explains course structure and product direction.
- No video requirement exists in the MVP plan.

### Phase 2: Update Course And Mission Schema

Deliverables:

- `missions/course.yml`
- course metadata loader
- backend support for curriculum metadata
- mission loader validation
- frontend types for new fields

Tasks:

- Add course-level module metadata.
- Add module and submodule fields.
- Add `mission_type` and `capability`.
- Add required/optional flags for lessons, modules, and capstones.
- Add `motivation`, `theory`, `thought_process`, and `debrief`.
- Validate command and check references.
- Validate mission modules against `course.yml`.
- Validate capstone mission references.
- Validate required capstones are implemented before they block completion.
- Preserve compatibility with existing missions during migration.
- Implement the **runtime loader** as migration-tolerant: curriculum fields (`motivation`, `theory`, `thought_process`, `debrief`, `capability`) are optional at load time; missing fields produce a warning, not a failure.
- Implement the **authoring validator** (used in `make verify` and CI) as release-strict: all curriculum fields are required before a mission can be merged.
- Add tests for course and mission fields.

Acceptance:

- Old missions still load.
- New curriculum-rich missions load.
- Course metadata loads in deterministic module order.
- Invalid module and capstone references fail in tests.
- Future or optional capstones do not block early release completion.
- Invalid step references fail in tests.

### Phase 3: Add Persistence Foundation

**Note: this phase must be completed before Phase 5 (Upgrade Mission Workbench) and Phase 8 (Capstone Mode), both of which depend on persisted step progress, capstone scores, and course completion state. Phase 4 (Build Course Map) also depends on this phase for `GET /course` to return accurate completion state.**

Deliverables:

- SQLite data model: profile, mission_progress, validation_attempt, step_progress, hint_usage, capstone_score, course_completion, schema_migration tables
- idempotent schema migration runner
- step validation attempt persistence
- latest step progress state
- latest proof state resume
- help usage persistence
- course completion state
- replay-safe capstone score history

Tasks:

- Add schema migration table and migration runner.
- Add profile, progress, validation attempt, step progress, hint usage, capstone score, and course completion tables.
- Persist scoped validation attempts.
- Persist latest step status and latest check messages.
- Return `stepProgress` in mission detail.
- Persist help usage by hint level.
- Track course completion from required lessons and capstones. Note: `course_completion.status` uses the value `in_progress` (not `started`) — these enums are intentionally different from `mission_progress.status` which uses `started`. See SPEC data model for the full rationale.
- Preserve best capstone score across replays.
- Initialize profile row on first startup.

Acceptance:

- Existing progress survives migration.
- Restarting the API does not erase step progress.
- Completed courses remain completed.
- Replaying a capstone can improve but not erase best mastery.
- `GET /profile` returns XP, badges, and course progress from persisted data.

### Phase 4: Build Course Map

Deliverables:

- `GET /course` API response
- module-based home screen
- visible progress by module
- capstone markers
- locked/available/completed states
- next recommended mission state
- capability progress summary

Tasks:

- Group missions by course metadata.
- Add `GET /course`.
- Render module cards or rows.
- Show project capability unlocked by each module.
- Show capstones separately from normal submodules.
- Show the next recommended mission in the first viewport.
- Show locked prerequisites.
- Preserve current mission links.

Acceptance:

- Learner can see the whole course path.
- Learner can tell which capability each module adds.
- Learner can identify exactly what to do next.
- Existing progress still works.

### Phase 5: Upgrade Mission Workbench

**Depends on Phase 3 (Persistence Foundation): persisted step progress rendering requires the `step_progress` table and `stepProgress` in mission detail to exist first.**

Deliverables:

- richer mission brief
- theory and thought process sections
- target-state-first learning flow
- debrief after completion
- explicit runtime, mission, step, command, proof, and hint states
- mobile workbench layout
- keyboard-accessible controls
- persisted step progress rendering
- staged help ladder rendering

Tasks:

- Add motivation panel.
- Add theory panel.
- Add thought process panel.
- Keep command reveal behavior.
- Keep step validation.
- Keep proof board.
- Add completion debrief tied to real-world use.
- Model runtime and validation states explicitly.
- Preserve command reveal and copy states.
- Add failed-step recovery behavior.
- Add mobile panel ordering.
- Add accessible labels and status text.
- Render persisted step progress from mission detail.
- Render help levels from nudge to diagnosis to repair.

Acceptance:

- Mission pages no longer feel like command lists.
- Learners see why, what, how, and proof in order.
- Commands are still easy to access when needed.
- Failed checks keep the learner oriented and recoverable.
- Workbench works at desktop and mobile widths.
- Primary controls are keyboard reachable.
- Returning learners resume with meaningful step state.
- Stuck learners can escalate help without leaving the workbench.

### Phase 6: Rewrite Existing Missions

**Depends on Phase 3 (Persistence Foundation): the mission ID rename migration (`serverless-boss` → `launchdesk-compose-capstone`) updates `mission_id` in `mission_progress`, `validation_attempt`, `step_progress`, `hint_usage`, and `capstone_score`. All five tables must exist before Phase 6 runs this migration.**

Deliverables:

- all current missions mapped into the new course arc
- consistent copy style
- cumulative LaunchDesk framing

Mission mapping:

```text
cloud-explorer         -> Module 0  (module ID: orientation)
s3-first-bucket        -> Module 1  (module ID: storage)
lambda-tiny-function   -> Module 2  (module ID: api)
apigateway-http-trigger -> Module 2  (module ID: api)
dynamodb-first-table   -> Module 3  (module ID: database)
sqs-first-message      -> Module 4  (module ID: async_processing)
sns-fanout             -> Module 5  (module ID: events)
serverless-boss        -> renamed to launchdesk-compose-capstone -> Module 6 capstone  (module ID: composition)
```

The canonical mission ID for the Module 6 capstone is `launchdesk-compose-capstone`. This is the value used in `course.yml` `capstone_mission_id` for the `composition` module. The existing `serverless-boss` mission file must be renamed or migrated to `launchdesk-compose-capstone` in Phase 6. This rename must always run as a registered migration entry in `schema_migration`; it is a no-op if no `serverless-boss` records exist, but it must always be registered to maintain idempotency across environments.

Tasks:

- Rewrite Cloud Explorer around sandbox safety.
- Rewrite S3 around durable LaunchDesk assets.
- Rewrite Lambda/API Gateway around HTTP backend capability.
- Rewrite DynamoDB around persisted LaunchDesk records.
- Rewrite SQS around async work.
- Rewrite SNS around platform events.
- Rewrite the legacy serverless capstone as LaunchDesk integration.

Acceptance:

- Every mission has motivation, theory, thought process, build, proof, and debrief.
- Resource names remain deterministic.
- Validators still match authored target state.

### Phase 7: Add Continuity Panel

**Depends on Phase 4 (Build Course Map): capability status data (`capabilities[].status`, `missionIds`) is sourced from `GET /course`. Phase 4 must be complete before Phase 7 builds the Continuity Panel against this endpoint.**

Deliverables:

- project state summary
- cross-module capability tracker
- proof-backed status where possible

Tasks:

- Use the canonical `capability.status` enum from the spec: `locked`, `in_progress`, `unlocked`.
- Map completed missions to capabilities using `course.yml` module metadata.
- Show completed resources and next missing capability.
- Link capabilities back to missions.

Acceptance:

- Learner can see LaunchDesk being built over time.
- Completed modules feel connected to future modules.

### Phase 8: Add Capstone Mode

**Depends on Phase 3 (Persistence Foundation): `capstone_score` table must exist before this phase persists latest and best capstone scores.**

Deliverables:

- capstone mission type
- reduced hints
- less direct command guidance
- broader validation
- capstone mastery scoring

Tasks:

- Add capstone-specific behaviors for `mission_type: module_capstone` and `final_capstone` (hidden/delayed commands, broader proof boards, mastery scoring). Note: the `mission_type` field itself was added to the mission schema in Phase 2; Phase 8 adds the behavioral differences between capstone and lesson types.
- Support hidden or delayed commands.
- Add broader proof boards.
- Add capstone score dimensions.
- Persist latest and best capstone scores.
- Implement required versus optional capstone completion behavior.
- Add final debrief.

Acceptance:

- Capstones test judgment, not copy/paste.
- Capstones return pass/fail completion and mastery level.
- Learners can still recover using hints and proof failures.

### Phase 9: Harden UX Flow Coverage

Deliverables:

- first-launch degraded states
- setup diagnostics for Docker, ports, and services
- locked lesson route handling
- failed check recovery flow
- returning learner resume flow
- reset and reset-failure states
- instructor/workshop recovery copy
- `/settings` route: implemented as a real frontend page (not docs copy only)
- `/profile` route: implemented frontend page showing XP, badges, and course progress

Tasks:

- Implement runtime offline states.
- Implement setup-degraded state and local troubleshooting copy.
- Implement locked mission direct-route state.
- Add retry-before-reset guidance for failed checks.
- Resume started missions at the best known incomplete step.
- Add reset progress, reset success, and reset failure UI.
- Add reset modes for resources, progress, and both.
- Add local-only troubleshooting copy for workshop recovery.
- Implement `/settings` page: runtime status, local data storage path, privacy statement, and reset guidance (read-only, links to workbench reset flows).
- Implement `/profile` page: XP total, capability badges, course progress from `GET /profile`.

Acceptance:

- Every PRD core flow has a matching UI path.
- No runtime or validation failure leaves the learner at a dead end.
- No troubleshooting copy asks for real AWS credentials.
- Setup issues are distinguishable from lesson failures.
- `/settings` is a navigable page with runtime, storage, privacy, and documentation details.
- `/profile` shows data from `GET /profile` and handles the loading/error states.

### Phase 10: Enforce Content Quality Gates

Deliverables:

- mission authoring quality checklist
- content lint or loader warnings for applicable files
- capstone guidance rules
- final manual review checklist
- staged help authoring requirements

Tasks:

- Check every lesson has motivation, theory, thought process, target state, proof, and debrief.
- Check target-state items map to validation checks.
- Check every failed check message is learner-readable.
- Check capstones use reduced command guidance.
- Check hints teach diagnostic moves.
- Check help escalates from nudge to diagnosis to repair.
- Check all command labels are action-oriented.

Acceptance:

- Every existing mission passes the course quality rubric.
- Capstones validate integrated behavior.
- Course copy is beginner-readable without hiding real cloud vocabulary.
- Every mission has a usable help path for common failure states.

### Phase 11: Add Diagnostics And Observability

Deliverables:

- setup diagnostic issue model
- runtime degraded UI integration
- structured local logs
- privacy-safe logging rules
- structured log events for mission lifecycle

Tasks:

- Add setup issue detection for Docker, ports, and services in the release gate.
- Extend runtime status with setup issues.
- Add structured logs for mission start, validation, reset, hint use, and completion.
- Redact credentials and unsafe payloads from logs.
- Document local progress storage path in README (the `/settings` page itself is implemented in Phase 9).

Acceptance:

- Runtime failures are distinguishable from lesson failures.
- Logs are useful for debugging without leaking credentials.
- No remote telemetry is enabled by default.

### Phase 12: Add Authoring And CI Gates

Deliverables:

- mission authoring validator
- local-only scan integration
- `make verify` full sequence
- CI workflow or documented equivalent
- contributor checklist

Tasks:

- Validate course and mission schemas.
- Validate local-only commands.
- Validate target-state proof coverage.
- Validate owned resources for created resources.
- Ensure `make verify` runs local-only scan, authoring validation, release artifact checks, backend tests, backend lint, frontend typecheck/build, smoke test, and local learner e2e.
- Add contributor docs or README section for mission authoring.

Acceptance:

- A bad mission fails before runtime.
- `make verify` is the release gate.
- Contributor can add and preview a lesson without guessing workflow.

### Phase 13: Run Beginner Usability Gate

Deliverables:

- usability test script
- observation checklist
- fixes from at least three beginner sessions

Tasks:

- Run setup, all required target-release lessons, failed-check recovery, restart/resume.
- Record where learners hesitate or misunderstand.
- Fix blocking copy, UX, validation, and layout issues.
- Re-run affected flow after fixes.

Acceptance:

- For PR readiness, the automated proxy gate in `docs/release/beginner-usability-gate.md` passes and the human-session gap is recorded.
- For public launch polish, three beginners complete the gate without source-code help.
- Each learner can explain what capability they added.
- No learner thinks real AWS is being used.

### Phase 14: Run Release Candidate Gate

Deliverables:

- clean-machine verification notes
- end-to-end acceptance matrix results
- known issues list
- final handoff summary

Tasks:

- Run clean-machine setup.
- Run `make verify`.
- Run browser acceptance matrix.
- Test supported responsive widths.
- Confirm no release-blocking bugs remain.
- Update README to match actual commands.
- Keep any remaining public-launch evidence gaps in release docs; after the final code iteration, only docs/plan/spec/PRD updates are allowed.

Acceptance:

- Project starts from documented commands.
- Required course slice and optional composition capstone workflow work end to end in the automated local gate.
- Final handoff contains commands run, flows run, and known non-blocking issues.

### Phase 15: Design Embedded Terminal

Deliverables:

- terminal security design
- local-only execution boundary
- command history model
- output streaming plan

Tasks:

- Decide whether commands execute in web, API, or a separate runner container.
- Block real AWS endpoints.
- Preserve command history by mission.
- Connect command output to validation actions.
- Document security limits.

Acceptance:

- Terminal plan does not weaken the local-only guarantee.
- Implementation is ready to start as a separate milestone.

## Verification Strategy

Backend verification:

```bash
cd apps/api && uv run pytest
```

Frontend verification:

```bash
cd apps/web && bun run build
```

Full local verification:

```bash
make verify
```

Manual learner-flow verification:

1. Start with `docker compose up --build`.
2. Open `http://localhost:3000`.
3. Confirm course map shows modules, capstones, and next recommended mission.
4. Complete all required target-release lessons.
5. Confirm proof board updates for each required service workflow.
6. Confirm continuity panel shows the new capabilities.
7. Trigger a failed step and recover without reset.
8. If the target release includes a required capstone, complete it with fewer hints.
9. Reset and verify local resources are cleaned up.
10. Restart the API and confirm progress resumes.
11. Test runtime offline UI by stopping Floci.
12. Test keyboard navigation through the course map and workbench.
13. Test mobile layout at a narrow viewport.
14. Confirm help escalation reaches a repair path.
15. Confirm course completion state after required lessons and any required capstones in the target release.

## Current Handoff State

The first execution slice has been implemented. The current branch is in PR-ready state for the target release:

1. Canonical PRD, spec, and plan are present.
2. `missions/course.yml` and curriculum metadata are implemented.
3. Persistence tables, migrations, scoped validation attempts, step progress, hint usage, capstone score, and course completion are implemented.
4. `GET /course` and the frontend course map render modules, capabilities, progress, and capstone grouping.
5. Required missions include motivation, theory, thought process, target state, proof checks, staged hints, and debrief.
6. Mission workbench renders explicit runtime, mission, step, command, proof, hint, reset, and completion states.
7. Required course slice and optional composition capstone workflow pass the automated local gate.
8. Remaining public-launch evidence gaps are documented in `docs/release/known-issues-template.md`: three human learner sessions and physical browser/device accessibility notes.

After the final code iteration, only PRD/spec/plan/release-doc updates should be made on this branch unless a new explicit code-change request supersedes this handoff constraint.
