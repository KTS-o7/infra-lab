# Infra Quest V2 PRD

## Purpose

Infra Quest V2 turns the local AWS lab from a command-copy workflow into a story-driven cloud apprenticeship.

The learner is not just completing service tutorials. They are rebuilding a small production-style platform inside a safe local AWS-compatible sandbox. Each mission brings one capability online, and the app proves progress by inspecting local infrastructure state.

The core product shift is:

```text
Old flow: command -> copy -> paste -> validate
New flow: request -> reason -> target state -> guided action -> proof -> debrief
```

Commands still exist, but they are tools revealed at the right moment. The lesson is the resource model, the reason a service exists, and the state the learner is trying to create.

## Product Outcome

A beginner should be able to:

1. Start the local lab with Docker.
2. Open the web app.
3. Understand they are working in a local sandbox, not real AWS.
4. Enter a mission framed as a realistic platform request.
5. Understand why the service is useful before seeing CLI syntax.
6. Build the required local resource state.
7. Check each step from the browser.
8. See a resource proof board explain what exists and what is missing.
9. Complete the mission, earn XP, and unlock the next part of the platform.

Success is not "the user copied the right command." Success is "the user understands what they built and can recognize the infrastructure state that proves it works."

## Target Users

### Primary User: Beginner Cloud Learner

Profile:

- knows basic terminal usage
- may not know AWS service models
- may not understand endpoints, regions, credentials, async systems, or resource naming
- wants practical cloud confidence without cost or account risk

Needs:

- plain-English mission context
- clear target architecture/state
- optional CLI syntax
- immediate local validation
- useful failure explanations
- safe reset path

### Secondary User: Instructor or Workshop Host

Profile:

- wants a repeatable local lab for students
- needs predictable lesson flow
- wants students to understand cloud concepts, not only commands

Needs:

- deterministic missions
- strong narrative sequence
- visible progress
- local-only guarantee
- repeatable resets

### Secondary User: Contributor

Profile:

- adds missions, validators, visual proof states, or curriculum copy
- works directly in the repo

Needs:

- mission schema that separates lesson UX from validation primitives
- reusable step and proof-board patterns
- clear authored content expectations
- tests for fallback behavior

## V2 Product Principles

- Lead with intent, not commands.
- Teach why, what, how, and proof in that order.
- Show the target resource state before asking the learner to build it.
- Keep CLI syntax available, but do not make it the first thing on the page.
- Validate actual local infrastructure state, not user-submitted claims.
- Explain failed checks in terms of missing resources or incorrect state.
- Keep the tone serious, operator-like, and premium. Avoid cartoon quest UI.
- Make progression feel like bringing a real platform online one capability at a time.
- Preserve the local-only safety promise everywhere.

## Narrative Model

The learner has joined a small software team whose production cloud is too risky to touch directly. Their job is to reconstruct the team's core platform inside a local AWS-compatible sandbox.

Each mission starts from a practical request:

```text
The app needs durable file storage.
Uploads should not block user requests.
One event needs to notify multiple downstream systems.
A worker should run without a full server.
The platform needs a public API entrypoint.
The app needs durable structured state.
```

The learner builds the local equivalent, checks it from the browser, and unlocks the next capability only when the sandbox proves the state is correct.

## Mission Arc

### 1. Cloud Explorer

Request:

Before changing anything, map the local cloud boundary and confirm the sandbox is isolated.

Teaches:

- local endpoint model
- fake credentials
- runtime safety
- difference between local AWS emulation and real AWS

Proof:

- local AWS endpoint responds
- API sees the emulator
- no real AWS endpoint is involved

### 2. First Bucket

Request:

The app needs durable storage for onboarding files.

Teaches:

- S3 bucket/object model
- durable object storage
- why app file uploads should not rely on local server disk

Proof:

- bucket exists
- object exists
- object body matches expected content

### 3. Queue the Message

Request:

Uploads and background jobs should not block the app. Put work into a queue.

Teaches:

- async job handoff
- queue names and queue URLs
- send and receive semantics

Proof:

- queue exists
- expected message is available

### 4. Publish and Subscribe

Request:

One platform event now needs to notify multiple consumers.

Teaches:

- event fanout
- topic versus queue
- SNS to SQS subscription pattern

Proof:

- topic exists
- queue subscription exists
- published event reaches the queue

### 5. Tiny Function

Request:

The platform needs small units of compute without running a full server.

Teaches:

- Lambda function packaging
- invocation
- request/response payloads

Proof:

- function exists
- function invocation returns expected payload

### 6. HTTP Trigger

Request:

The app needs a controlled public entrypoint for a small workflow.

Teaches:

- API Gateway route model
- Lambda integration
- HTTP request to serverless function path

Proof:

- API route exists
- route invokes the expected function
- response status/body match expected output

### 7. Key-Value Store

Request:

The platform needs durable structured state for application records.

Teaches:

- DynamoDB table model
- partition keys
- item reads/writes

Proof:

- table exists
- expected key schema exists
- expected item can be read

### 8. Serverless Boss

Request:

Wire storage, queues, events, functions, API, and database into one working local platform flow.

Teaches:

- service composition
- resource dependencies
- end-to-end serverless architecture

Proof:

- all required resources exist
- event path works
- API path works
- persisted state is correct

## Mission Detail UX

Each mission page should use a Mission Workbench structure.

### 1. Mission Brief

Shows:

- mission title
- practical request
- service badges
- estimated time
- XP
- local-only banner

The brief should be short. It should orient the learner without hiding the actual task below a wall of text.

### 2. Target State

Shows the local infrastructure state the learner must create.

Examples:

- S3 bucket: `starter-bucket`
- object: `hello.txt`
- expected body: `Hello from local AWS`
- SQS queue: `starter-queue`
- expected message: `first local queue message`

This makes validation transparent before the learner starts.

### 3. Guided Steps

Each step follows this pattern:

```text
Goal
What the learner is trying to make true.

Why this matters
The real system problem this concept solves.

Target state
The exact local resources or values expected after this step.

Try it
A plain-English action prompt.

Need CLI syntax?
Reveal command on demand.

Check
Validate this step and explain what passed or failed.
```

### 4. Proof Board

The proof board visualizes validation state as resources, not as generic test rows.

Examples:

- bucket node
- object row inside bucket
- queue node with message badge
- topic node connected to queue
- function node with invoke result
- API route connected to function
- table node with key/item proof

The board should be compact, serious, and useful. It should feel like an infrastructure control panel, not a decorative diagram.

### 5. Coach Panel

Shows:

- current step status
- validation result
- failed checks in plain language
- attempts
- hints
- reset controls
- final completion action

The coach panel should explain what to fix, not only that something failed.

### 6. Debrief

After completion, the page should show a short debrief:

- what resource model the learner used
- why this service exists in real systems
- what the next mission builds on top of it

## Command Reveal Policy

Commands should be available but not dominant.

Default state:

- show the goal, why, target state, and plain-English action
- hide the raw command behind `Show CLI syntax` or an equivalent compact control

After reveal:

- show the command in a polished code block
- include copy action
- keep the expected result nearby

Do not remove commands entirely. The product still teaches real AWS-style workflows. The change is that CLI syntax supports the concept instead of replacing it.

## Inspiration Patterns

Infra Quest V2 borrows product patterns from proven interactive learning tools:

- Learn Git Branching: structured levels, visual model updates, sandbox exploration.
- Oh My Git: beginner-friendly action cards with a terminal path for advanced users.
- GitLearn: structured lessons, playground, XP, and progress without account requirements.
- Git Immersion: learning by doing instead of passive reading.
- Killercoda: browser-based technical scenarios with a guided task flow.
- Cloud lab platforms: temporary safe environments, step checks, and real resource feedback.

Infra Quest should not copy their visual style. It should adapt the underlying learning patterns to local AWS infrastructure.

## MVP Scope For V2

V2 includes:

- new Mission Workbench detail page
- mission `steps` authoring model
- optional command reveal
- step-level validation
- resource proof board
- revised storyline copy for the current mission arc
- authored steps for at least the first three missions
- fallback generated steps for legacy missions

V2 does not include:

- browser shell execution
- arbitrary command runner
- real AWS credentials
- multiplayer features
- leaderboards
- heavy 3D city UI
- public SaaS hosting

## Acceptance Criteria

- A learner can understand a mission's practical request before seeing any command.
- A learner can inspect the target resource state before starting.
- CLI syntax is available on demand.
- Step validation can show progress before final mission completion.
- Full mission validation still awards XP once.
- Failed validation names the missing or incorrect resource state.
- The page does not feel like a copied documentation article.
- Existing local-only guarantees remain intact.
