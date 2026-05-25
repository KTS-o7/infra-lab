# Infra Quest PRD

## Purpose

Infra Quest is a local-first, zero-cost cloud learning lab for beginners.

The product teaches cloud by having learners build one cumulative project inside a safe local AWS-compatible sandbox. Learners do not study services in isolation. They build practical platform capabilities, understand why each capability exists, implement it hands-on, and prove the resulting infrastructure state from the browser.

The learning contract is:

```text
motivation -> theory -> thought process -> target state -> build -> proof -> debrief
```

Video is out of scope for now. The first product should be strong through written theory, guided reasoning, hands-on implementation, validation, capstones, and project continuity.

Technical architecture and contracts live in `INFRA_QUEST_SPEC.md`. Build sequencing lives in `INFRA_QUEST_PLAN.md`.

## Product Outcome

A beginner should be able to:

1. Start the lab with Docker.
2. Open the web app.
3. Understand that all cloud calls stay local.
4. Follow a course map made of modules, submodules, and capstones.
5. Enter a lesson framed as a realistic platform request.
6. Read the motivation and short theory before touching commands.
7. Understand the thought process behind the design choice.
8. Build the target local infrastructure state.
9. Validate each step from the browser.
10. See a proof board explain what exists and what is missing.
11. Complete every capstone declared required for the target release; the current PR release keeps the composition capstone optional and has no required final capstone.
12. Finish with a working local SaaS-style platform.

Success is not "the learner copied the right command." Success is "the learner understands what they built, why it exists, and what state proves it works."

## AI Agent Handoff Goal

The PRD, spec, and plan must be sufficient for an AI implementation agent to build the project end to end without inventing product behavior, API contracts, data models, curriculum structure, or release criteria.

The handoff is successful only when an agent can:

1. Read `INFRA_QUEST_PRD.md`, `INFRA_QUEST_SPEC.md`, and `INFRA_QUEST_PLAN.md`.
2. Implement the planned phases in order.
3. Run the required verification commands.
4. Start the stack locally.
5. Complete the required browser-guided learner flows while running copyable commands in the local terminal.
6. Demonstrate that local-only safety holds.
7. Deliver a repo with no known release-blocking bugs.

"No bugs" means no known blocker, critical, or high-severity bugs after the required verification and manual learner-flow checks. It does not mean the software is mathematically bug-free; it means the release gate catches the bugs that would prevent a beginner from completing the course safely and reliably.

## Release-Blocking Bug Bar

The implementation is not releasable if any of these are true:

- the stack cannot start from `docker compose up --build`
- the course map cannot load on a healthy runtime
- any local AWS command points to real AWS
- backend can start with a real AWS endpoint
- mission validation trusts user claims instead of local infrastructure state
- required mission progress is lost after API restart
- reset deletes resources not owned by the mission
- XP can be awarded twice for the same mission completion
- a locked mission can be completed by bypassing prerequisites
- a beginner cannot complete Module 0 and the first storage lesson with the browser-guided flow and local terminal commands
- failed validation gives no actionable recovery path
- mobile layout hides primary actions or overlaps text
- keyboard users cannot reach primary controls
- clean-machine verification fails
- tests or local-only scan fail

High-severity bugs must be fixed before handoff. Medium and low-severity bugs may remain only if they are documented with impact, reproduction steps, and follow-up priority.

## Target Users

### Primary User: Beginner Cloud Learner

Profile:

- knows basic terminal usage
- can install Docker and run a local app
- may not know AWS services
- may not understand endpoints, credentials, regions, async systems, or resource naming
- wants practical confidence without cost or account risk

Needs:

- clear modules and submodules
- short theory before implementation
- practical motivation for every concept
- visible thought process
- copyable commands after context is established
- immediate validation
- useful failure explanations
- safe reset path
- cumulative project continuity

### Secondary User: Instructor Or Workshop Host

Profile:

- wants a repeatable local lab for students
- needs predictable setup and reset
- wants learners to understand cloud concepts, not only commands

Needs:

- deterministic missions
- strong lesson sequence
- visible learner progress
- local-only guarantee
- capstone-ready structure

### Secondary User: Contributor

Profile:

- adds missions, validators, proof-board mappings, or curriculum copy
- works directly in the repository

Needs:

- strict mission schema
- reusable validation primitives
- clear authored content standard
- tests for mission loading and validation
- one canonical PRD, spec, and plan

## Course Project

The course project is a small SaaS-style operations platform.

Working name:

```text
LaunchDesk
```

LaunchDesk starts as a minimal local platform and grows across the course. Each module adds one real capability:

- local sandbox boundary
- durable file storage
- HTTP backend API
- persisted application records
- async background work
- platform events and fanout
- composed end-to-end workflow
- debugging and recovery behavior

The learner should feel that every lesson contributes to the same platform, not to a disconnected list of service tutorials.

## Product Principles

- Teach objectives before services.
- Use modules and submodules, but keep them tied to one growing project.
- Put theory before implementation, but keep it short and practical.
- Explain motivation explicitly: what breaks without this capability?
- Explain thought process explicitly: how should an engineer decide what to build?
- Show the target state before showing commands.
- Keep every lesson hands-on.
- Validate actual local infrastructure state, not text answers or screenshots.
- Explain failed checks in terms of missing or incorrect resources.
- Keep commands available, but reveal them at the right moment.
- Make capstones test judgment, not copy/paste.
- Preserve the local-only safety promise everywhere.
- Avoid childish quest visuals; the tone should be serious, practical, and operator-like.

## Coverage Assessment

The current product plan covers the strategic direction, course arc, local safety model, mission workbench, validation model, and capstone direction. That is enough to start implementation, but it is not enough to guarantee a high-quality course or polished UX by itself.

A complete implementation must also cover:

- exact course metadata, not hard-coded module labels
- all learner states, including first launch, offline runtime, locked lessons, failed checks, repeated attempts, completed lessons, and reset recovery
- persisted step progress, so returning learners resume from meaningful state
- schema migrations, so progress survives product upgrades
- a content quality rubric for every lesson
- a capstone scoring model
- a help escalation model for learners who are stuck
- a continuity model that shows what LaunchDesk capability is online
- setup failure handling for Docker, ports, and unavailable local services
- mobile layout behavior
- keyboard and screen-reader accessibility
- useful empty, loading, and error states
- local-only safety enforcement in commands, API errors, hints, and terminal plans
- privacy and observability rules for local logs and progress data
- contributor authoring, review, and regression workflows
- release criteria for clean-machine setup and browser support
- manual acceptance flows that simulate a real beginner, not only unit tests

Implementation should be considered production-quality for the local course only when every item above is explicitly implemented and verified.

## Non-Goals

- Do not deploy learner resources to real AWS.
- Do not require an AWS account.
- Do not require real AWS credentials.
- Do not build video lessons in the first version.
- Do not build multiplayer, leaderboards, or social features.
- Do not build public SaaS hosting.
- Do not execute arbitrary browser-triggered shell commands until the terminal security model is separately designed.
- Do not organize the course primarily as "S3 module, EC2 module, Lambda module." Services are introduced through product objectives.

## Course Structure

### Module 0: Local Cloud Orientation

Goal: prove the learner is working inside a safe local cloud sandbox.

Teaches:

- local AWS-compatible endpoint
- fake credentials
- regions
- CLI calls
- local emulation versus real AWS

Capstone:

Given the endpoint and fake credentials, prove the sandbox is isolated and ready.

### Module 1: Store Files Outside The App

Goal: add durable object storage to LaunchDesk.

Teaches:

- object storage
- buckets
- keys
- object bodies
- app storage versus server filesystem

Capstone:

Create a LaunchDesk assets bucket and upload onboarding files.

### Module 2: Expose A Backend API

Goal: create a serverless HTTP entrypoint for LaunchDesk.

Teaches:

- HTTP APIs
- routes and methods
- serverless functions
- API Gateway to Lambda integration

Capstone:

Build `POST /lead` for LaunchDesk.

### Module 3: Persist Application Records

Goal: store structured LaunchDesk records.

Teaches:

- NoSQL table model
- partition keys
- items
- reads and writes
- access patterns before schema

Capstone:

Persist submitted leads in a LaunchDesk table.

### Module 4: Move Slow Work Out Of Requests

Goal: add async processing to LaunchDesk.

Teaches:

- queues
- producers and consumers
- message visibility
- async handoff
- retry-safe thinking

Capstone:

When a lead is submitted, enqueue background workflow work.

### Module 5: Broadcast Platform Events

Goal: notify multiple consumers when important things happen.

Teaches:

- topics
- subscriptions
- fanout
- topic versus queue
- publisher and subscriber responsibilities

Capstone:

Publish `lead.created` and deliver it to audit and workflow queues.

### Module 6: Compose The Platform

Goal: wire storage, API, database, queues, events, and functions into one working local flow.

Teaches:

- service boundaries
- synchronous versus asynchronous paths
- resource dependencies
- end-to-end proof

Capstone:

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

Teaches:

- proof-board failures
- missing resources
- wrong names and payloads
- retry and repair
- reset versus recovery
- basic SLA-style thinking

Capstone:

Given a partially broken LaunchDesk deployment, restore the system until all proof checks pass.

## Final Capstones

### Final Capstone 1: LaunchDesk MVP

Learner builds the full local SaaS backend with limited guidance.

Required behavior:

- accept a tenant-scoped lead submission
- persist the lead
- upload or generate an onboarding artifact
- publish a `lead.created` event
- queue background workflow work
- expose an HTTP endpoint
- pass end-to-end validation

### Final Capstone 2: Production Readiness Challenge

Learner extends LaunchDesk toward production-style behavior.

Required behavior:

- tenant-aware records
- clear request IDs
- retry-safe background job behavior
- health/proof checks
- failure recovery task
- simple SLA-style target such as "all proof checks pass after reset and rebuild"

This capstone should provide fewer direct commands and more prompts. The learner should decide the order of operations using the thought process learned earlier.

## Capstone Scoring Model

Capstones should remain pass/fail for progression, but they should also give a mastery score that helps the learner understand how independently they completed the work.

Scoring dimensions (four scored, one required gate):

- Infrastructure completeness: required resources exist with correct configuration.
- End-to-end behavior: the full product workflow succeeds.
- Independence: learner used fewer hints and fewer repeated attempts.
- Recovery: learner can repair failed state without full lab reset when applicable.
- Local safety: **not a scored dimension**. It is a required gate. A capstone cannot pass if local-only safety is violated. Represented as `localSafetyPassed: true/false` in the validation response, not as a dimension in the `dimensions[]` array.

Suggested weighting (four scored dimensions total 95 points; local safety is a pass/fail gate):

```text
Infrastructure completeness: 30
End-to-end behavior: 40
Independence: 15
Recovery: 10
Local safety: required gate (not scored; blocks completion if false)
```

Mastery levels (API enum values and numeric thresholds are authoritative in SPEC; descriptions below are summaries for product and UX understanding):

```text
needs_repair      score < 60  — critical checks failed or score too low to demonstrate readiness
complete          60 <= score < 75  — all required checks passed
strong            75 <= score < 90  — passed with limited hints and attempts
production_minded score >= 90  — passed, recovered from failure, and preserved local safety
```

The `needs_repair` level can occur either because critical checks failed (which prevents the capstone from passing) or because the score falls below 60. The SPEC numeric thresholds are the authoritative implementation contract. These qualitative descriptions are for product and copy context only.

The score should never block learning after the learner has passed required checks. It should guide reflection and replay.

## Lesson Model

Every submodule follows the same structure.

### Motivation

State the product problem in plain language.

Example:

```text
Users need to upload onboarding files. If files are stored only on the app server,
they disappear when the server is replaced or restarted.
```

### Theory

Explain the cloud concept that solves the problem.

Example:

```text
Object storage gives the application a durable place for files. A bucket is the
storage boundary. An object is the file plus its key.
```

### Thought Process

Show how an engineer reasons from problem to design.

Example:

```text
We need storage independent from the web process. We do not need a database for
raw files. We need a named boundary, stable object keys, and proof that the file
exists after upload.
```

### Target State

Describe exactly what should exist after the learner finishes.

Example:

```text
Bucket: launchdesk-assets
Object: welcome.txt
Body: Welcome to LaunchDesk
```

### Build

Give the guided implementation. Commands may be hidden behind a reveal control until the learner has seen the problem, theory, thought process, and target state.

### Proof

Validate the real local sandbox state.

Example:

```text
The bucket exists.
The object exists.
The object body matches the expected content.
```

### Debrief

Connect the local exercise to real-world cloud architecture.

Example:

```text
In production, this pattern is used for uploads, generated reports, exports,
static assets, data lakes, and media pipelines.
```

## Core User Flows

### Flow 1: First Launch

Preconditions:

- Docker is installed.
- Ports `3000`, `8000`, and `4566` are available.
- User is in the repository root.

User actions:

1. Runs `docker compose up --build`.
2. Opens `http://localhost:3000`.

Expected behavior:

- Floci starts locally.
- API starts locally.
- Web app starts locally.
- Course map loads.
- Runtime status is visible.
- Local-only guarantee is visible.

Acceptance criteria:

- no real AWS credentials are requested
- no command examples omit `--endpoint-url http://localhost:4566`
- runtime errors are actionable

### Flow 2: Browse Course Map

User actions:

1. Opens the app.
2. Scans modules, submodules, and capstones.
3. Opens an available lesson.

Expected behavior:

- modules appear in deterministic order
- each module shows the LaunchDesk capability it unlocks
- locked lessons explain prerequisites
- completed lessons show completion state

Acceptance criteria:

- learner can tell what they are building over time
- capstones are visually distinct from normal lessons
- missing mission data renders an empty/error state, not a crash

### Flow 3: Complete A Guided Lesson

User actions:

1. Opens a lesson.
2. Reads motivation, theory, and thought process.
3. Reviews target state.
4. Reveals CLI syntax when ready.
5. Runs the command locally.
6. Checks the step.
7. Completes the lesson.

Expected behavior:

- command list is not the primary page body
- step validation checks only linked checks
- full validation awards XP once
- proof board shows pending, passed, and failed states clearly
- debrief appears after completion

Acceptance criteria:

- failed validation names the missing or incorrect resource state
- completing a lesson unlocks the next relevant lesson
- repeated validation does not duplicate XP

### Flow 4: Complete A Capstone

User actions:

1. Opens a module or final capstone.
2. Reads the target product behavior.
3. Decides implementation order.
4. Uses hints only if needed.
5. Runs broader validation.

Expected behavior:

- capstone gives less direct command guidance
- proof board spans multiple resources
- hints reduce possible XP if configured
- learner can recover through failed checks

Acceptance criteria:

- capstone validates integrated behavior, not isolated resources only
- learner can complete without backend logs
- debrief explains the system they composed

### Flow 5: Reset And Recover

User actions:

1. Clicks reset for a lesson or module.
2. Confirms reset.
3. Rebuilds required resources.

Expected behavior:

- owned local resources are removed safely
- unrelated resources are not deleted
- progress state follows the configured reset behavior

Acceptance criteria:

- reset is reliable and visible
- reset never suggests real AWS cleanup
- learner can repeat the lesson after reset

### Flow 6: Runtime Unavailable

User actions:

1. Opens the app while the API, Floci, or database is unavailable.

Expected behavior:

- app shell still renders
- course map renders a degraded state when possible
- validation, start, reset, and hint actions are disabled when the backend cannot perform them
- the UI names the unavailable dependency
- troubleshooting copy uses local Docker commands only

Acceptance criteria:

- UI does not crash
- no error asks the learner to configure AWS
- learner can retry status checks after fixing the runtime

### Flow 7: Locked Lesson

User actions:

1. Opens the course map.
2. Selects a locked lesson or capstone.

Expected behavior:

- locked lesson explains which prerequisite is missing
- locked lesson does not show implementation commands as the primary path
- learner can navigate to the prerequisite lesson

Acceptance criteria:

- locked state is understandable without reading backend errors
- direct navigation to locked mission returns a safe locked state

### Flow 8: Failed Step Recovery

User actions:

1. Runs an incorrect or incomplete command.
2. Clicks `Check Step`.
3. Reads failure feedback.
4. Repairs local state.
5. Checks again.

Expected behavior:

- failed proof item names the missing or wrong resource
- previous successful proof items remain visible
- command reveal state is preserved
- learner is not forced to reset unless repair is impractical

Acceptance criteria:

- failure feedback points to state, not blame
- learner can recover without backend logs
- repeated checks do not award XP until full completion passes

### Flow 9: Returning Learner

User actions:

1. Stops the lab.
2. Starts it again later.
3. Opens the app.

Expected behavior:

- completed missions remain completed
- started missions resume at the first incomplete step when known
- continuity panel shows previously completed capabilities
- course map shows next recommended lesson

Acceptance criteria:

- learner does not lose progress after API restart
- recommended next action is visible within the first viewport

### Flow 10: Mobile Or Narrow Screen

User actions:

1. Opens the app on a narrow viewport.
2. Reads a lesson.
3. Reveals and copies a command.
4. Checks validation output.

Expected behavior:

- course map remains scannable
- workbench panels stack in the order: brief, active step, proof, coach, continuity
- command blocks scroll horizontally without breaking layout
- buttons remain tappable

Acceptance criteria:

- no text overlaps
- no primary action is hidden off-screen
- proof and failure messages remain readable

### Flow 11: Keyboard And Screen Reader Use

User actions:

1. Navigates the course map and mission workbench with keyboard.
2. Reveals commands.
3. Copies commands.
4. Runs validation.

Expected behavior:

- focus order matches visual order
- icon buttons have accessible labels
- proof states are conveyed by text, not only color
- validation updates are announced or placed where screen readers can reach them naturally

Acceptance criteria:

- all interactive controls are keyboard reachable
- color is never the only status signal
- command copy action gives accessible feedback

### Flow 12: Instructor Workshop Reset

User actions:

1. Instructor starts a workshop.
2. Multiple learners run the local setup.
3. A learner breaks local state.
4. Instructor asks learner to reset a lesson or the lab.

Expected behavior:

- reset path is predictable and safe
- troubleshooting copy is concise
- local-only guarantee is visible

Acceptance criteria:

- workshop host can recover a learner without manual database edits
- reset does not delete unrelated local resources

### Flow 13: Setup Failure

User actions:

1. Runs the local setup.
2. Docker is unavailable, a port is occupied, or one service fails to start.
3. Opens the web app or checks logs.

Expected behavior:

- setup docs and runtime UI identify the likely local failure
- troubleshooting uses local commands only
- learner can retry after fixing Docker or ports
- app does not suggest real AWS setup as a fallback

Acceptance criteria:

- port conflicts for `3000`, `8000`, and `4566` have clear guidance
- Docker-not-running guidance is visible in README or runtime troubleshooting
- partial startup does not create a confusing blank app

### Flow 14: Learner Stuck Escalation

User actions:

1. Fails the same step multiple times.
2. Opens help.
3. Uses progressively stronger support.

Expected behavior:

- first help level nudges the learner toward diagnosis
- second help level explains the likely missing resource or wrong value
- final help level can reveal the exact command or repair path
- XP or mastery can reflect help usage, but the learner is not blocked

Acceptance criteria:

- help teaches the reasoning, not only the answer
- final reveal is available for beginners who are truly stuck
- help usage is persisted and visible

### Flow 15: Course Completion

User actions:

1. Completes all required lessons.
2. Completes final capstones only when the target release declares them required.
3. Opens the course map or profile.

Expected behavior:

- course map shows complete state
- final LaunchDesk capability summary is visible
- learner can review what they built by capability
- learner can replay lessons or capstones to improve mastery

Acceptance criteria:

- completion is based on required checks and required capstones, not page visits
- learner can distinguish completed lessons from mastered capstones
- replay does not erase prior completion or best capstone score

### Flow 16: Contributor Adds A Lesson

User actions:

1. Contributor creates a mission folder.
2. Adds mission content, commands, checks, hints, owned resources, and proof mappings.
3. Runs authoring validation.
4. Opens the lesson locally.

Expected behavior:

- invalid command/check references fail before runtime
- missing required copy is reported clearly
- unsafe AWS commands fail local-only checks
- contributor can preview the mission in the course map

Acceptance criteria:

- new lesson cannot merge unless loader tests, local-only checks, and content gates pass
- authoring failure messages identify the file and field to fix

### Flow 17: Upgrade Existing Learner

User actions:

1. Learner has existing local progress.
2. Pulls a newer version of the repo.
3. Starts the lab.

Expected behavior:

- database migrations run safely
- completed progress remains available
- stale proof states are marked stale instead of shown as current
- new lessons appear without corrupting old progress

Acceptance criteria:

- learner does not lose XP, completions, help history, or best capstone score
- migration failure gives local recovery guidance

### Flow 18: Clean-Machine Release Check

User actions:

1. Maintainer clones the repo on a clean machine.
2. Runs documented setup.
3. Completes the first full learning slice.

Expected behavior:

- setup works without hidden global dependencies
- lockfiles are honored
- local-only verification passes
- first course slice is completable with the browser-guided flow and local terminal commands

Acceptance criteria:

- clean-machine run passes before release
- README commands match the tested path

### Flow 19: Privacy And Local Data Review

User actions:

1. Learner or instructor wants to understand stored data.
2. Opens profile/settings or docs.
3. Resets or exports local progress if supported.

Expected behavior:

- product explains that progress is local
- logs do not expose secrets
- no remote telemetry is sent by default
- reset behavior is explicit

Acceptance criteria:

- learner can identify where progress is stored
- privacy copy is truthful and visible
- no real AWS credentials or secrets appear in logs

## App Experience Requirements

### Course Map

The home screen should show:

- modules
- submodules
- capstones
- current progress
- locked, available, started, and completed API status states; capstone visual variant for missions with `missionType: module_capstone` or `final_capstone` (not an API status value)
- capability unlocked by each module

### Mission Workbench

The lesson detail page should show:

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
- completion debrief

### Proof Board

The proof board should visualize resource state, not generic test rows.

Examples:

- bucket node
- object row inside bucket
- queue node with message badge
- topic node connected to queue
- function node with invoke result
- API route connected to function
- table node with key/item proof

### Continuity Panel

The app should show what LaunchDesk capabilities are already online.

Examples:

```text
Storage: launchdesk-assets bucket online
API: POST /lead route online
Database: launchdesk-leads table online
Queue: lead-workflow queue online
Events: lead-events topic online
Worker: lead-worker function online
```

### Embedded Terminal

Initial scope:

- show command history per mission
- allow copy/paste commands
- preserve continuity between submodules

Later scope:

- run commands inside a constrained local shell
- block real AWS endpoints
- stream command output into the workbench
- link terminal output to validation results

Browser-triggered shell execution changes the security model and must be handled as a separate design milestone.

### Help Ladder

Each lesson should support a staged help ladder.

Levels:

1. Nudge: reminds the learner what state to inspect.
2. Diagnosis: explains the likely missing or incorrect resource.
3. Repair: shows the exact command or sequence needed to recover.

The help ladder should be tied to proof failures when possible. A learner who fails `object-body` should not receive generic S3 help first; they should receive help about object content mismatch.

### Review And Replay

Completed lessons should remain useful.

The learner should be able to:

- reopen completed lessons
- view the debrief
- inspect proof history or latest proof state
- reset owned resources
- replay a capstone to improve mastery score
- see best and latest capstone scores separately

### Privacy And Local Data

The product should be honest about what it stores.

Required behavior:

- progress is stored locally
- no remote telemetry is enabled by default
- logs avoid credentials, command secrets, and unnecessary payload bodies
- settings or docs explain how to reset local progress
- any future remote sync must be opt-in and outside the current MVP

### Contributor Experience

Adding a lesson should feel like authoring curriculum, not spelunking through app internals.

Contributor requirements:

- clear mission template
- local content validation
- local-only command validation
- proof-board mapping guidance
- preview path in the browser
- regression checklist for mission validation and reset
- review checklist for pedagogy and UX copy

## Course Quality Rubric

Every lesson must pass this rubric before it is considered complete.

### Concept Coverage

- Motivation explains the product problem.
- Theory explains only the concept needed for the build.
- Thought process explains why this design was chosen over obvious alternatives.
- Target state is concrete and inspectable.
- Build step creates real local infrastructure state.
- Proof validates local state directly.
- Debrief connects the lesson to production cloud architecture.

### Project Continuity

- Lesson adds or repairs a LaunchDesk capability.
- Capability appears in the continuity panel.
- Lesson prerequisites match the real dependency order.
- Resource names are deterministic.
- Reset removes only mission-owned resources.

### Beginner Fit

- No unexplained AWS jargon in the first paragraph.
- Commands are copyable after context is established.
- Failed checks explain what to inspect next.
- Hints help without replacing the lesson.
- Help escalates from reasoning to repair.
- The learner can complete the happy path without reading source code or backend logs.
- Content can be reviewed against the authoring checklist without guessing intent.

### Capstone Fit

- Capstone validates integrated behavior.
- Capstone gives fewer direct commands than lessons.
- Capstone steps may omit `command_id` entirely; commands exist in the mission `commands` list but are not linked to steps, forcing the learner to decide when to use them.
- Capstone steps may use delayed reveal: `command_id` is present but the workbench delays surfacing the "Show CLI syntax" control until after the learner has reviewed the target architecture.
- Capstone still provides recovery hints.
- Capstone debrief explains the system the learner composed.
- Capstone returns a mastery level after completion.

## UX Quality Bar

The UX is complete only when these states are designed and implemented:

- loading
- empty
- runtime offline
- locked
- available
- started
- checking
- check passed
- check failed
- command hidden
- command revealed
- command copied
- hint unused
- hint revealed
- reset pending
- reset complete
- mission completed
- capstone completed
- returning learner resume
- setup failure
- stuck learner help
- course completion
- replay
- contributor authoring
- upgrade/migration
- clean-machine release
- local privacy review
- optional/future lesson visibility

Every state must have:

- clear primary action
- safe secondary action
- no dead ends
- no real AWS instructions
- mobile-safe layout
- keyboard-accessible controls
- status text that does not depend on color alone

## Acceptance Criteria

- The repository has one canonical PRD, one canonical spec, and one canonical plan.
- The product is framed as a cumulative project-based cloud apprenticeship.
- Video is not required for the MVP.
- Every new lesson can include motivation, theory, thought process, target state, build, proof, and debrief.
- A learner can understand a mission's practical request before seeing any command.
- CLI syntax is available on demand.
- Step validation can show progress before full mission completion.
- Full mission validation still awards XP once.
- Failed validation explains missing or incorrect local resource state.
- The course map shows modules, submodules, and capstones.
- The continuity panel shows the platform being built over time.
- Capstones provide pass/fail completion and a mastery score.
- All AWS-style calls remain local-only.
- All flows from first launch through reset, recovery, return, required capstones, and offline runtime are implemented for the target release.
- Every lesson passes the course quality rubric.
- Every UX state in the quality bar is represented in the UI.
- Step progress, help usage, and capstone scores persist across restarts.
- Existing learner progress survives schema migrations.
- Mobile and keyboard accessibility are verified manually before release.
- Clean-machine setup, contributor authoring validation, and privacy/logging checks pass before release.
- At least three beginner usability runs complete the first two modules without source-code help before the course is considered polished.
- Final handoff includes test results, manual-flow results, known non-blocking issues, and exact commands used to verify the project.
