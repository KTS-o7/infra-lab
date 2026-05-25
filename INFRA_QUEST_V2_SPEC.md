# Infra Quest V2 Specification

## Overview

Infra Quest V2 adds a story-driven Mission Workbench on top of the existing local AWS lab.

The existing platform remains:

```text
Browser -> Next.js Web App -> FastAPI Backend -> Floci AWS Emulator -> local state
```

The V2 change is the learning contract. Missions should no longer present raw commands as the main experience. Missions should expose a structured step model that explains intent, target resource state, optional CLI syntax, and proof.

## Goals

- Add a mission UX layer that supports guided steps.
- Keep existing command and check primitives.
- Add step-level validation without breaking full mission validation.
- Visualize resource state through a proof board.
- Preserve existing XP, hints, reset, progress, and local-only constraints.

## Non-Goals

- Do not execute arbitrary shell commands from the browser in V2.
- Do not require real AWS credentials or accounts.
- Do not replace validators with user-entered answers.
- Do not build a 3D city or game world in this version.
- Do not remove CLI learning.

## Mission Schema

Current missions define:

```yaml
commands:
  - id: create-bucket
    label: Create bucket
    command: aws --endpoint-url http://localhost:4566 s3 mb s3://starter-bucket

checks:
  - id: bucket-exists
    type: s3_bucket_exists
    bucket: starter-bucket
```

V2 adds `steps` as the learner-facing UX layer:

```yaml
steps:
  - id: create-bucket
    title: Create durable storage
    goal: Create an S3 bucket named starter-bucket.
    why: Apps need durable storage for files that must survive app restarts and deployments.
    target_state:
      - label: Bucket
        value: starter-bucket
      - label: Service
        value: S3
    action: Create the bucket in your local AWS sandbox.
    command_id: create-bucket
    check_ids:
      - bucket-exists
    success: The bucket exists in local S3.
```

### Step Fields

Required:

- `id`: unique within the mission
- `title`: short learner-facing title
- `goal`: what should become true
- `action`: plain-English instruction
- `command_id`: command to reveal when requested
- `check_ids`: checks that prove the step

Optional:

- `why`: practical explanation
- `target_state`: list of labels/values for the proof target
- `success`: completion explanation
- `notes`: short additional guidance

### Backward Compatibility

If `steps` is absent:

- API should derive one step per command.
- Derived step title uses command label.
- Derived step action should be `Run this command in your terminal against the local AWS sandbox.`
- Derived step should have empty `check_ids` unless a deterministic mapping is authored later.
- Full mission validation must still work.

## API Contract

### Mission Detail Response

Extend `GET /missions/{mission_id}`:

```ts
interface MissionDetail {
  mission: {
    id: string;
    order: number;
    title: string;
    summary: string;
    difficulty: string;
    services: string[];
    xp: number;
    estimatedMinutes: number;
    status: string;
    story: string;
    learningObjectives: string[];
    commands: MissionCommand[];
    steps: MissionStep[];
    hints?: MissionHint[];
    progress: MissionProgress;
  };
}

interface MissionStep {
  id: string;
  title: string;
  goal: string;
  why?: string;
  targetState: { label: string; value: string }[];
  action: string;
  commandId: string;
  checkIds: string[];
  success?: string;
  notes?: string;
}
```

### Validation Request

Support optional step validation on the existing endpoint:

```http
POST /missions/{mission_id}/validate
Content-Type: application/json

{
  "stepId": "create-bucket"
}
```

Request body is optional.

Behavior:

- no body: validate all mission checks, award XP if all pass and mission is not completed
- `stepId`: validate only checks linked to that step, never award mission XP
- invalid `stepId`: return `404` or `409` with a structured error
- step with no `checkIds`: return an empty scoped validation result with `passed: false` and a clear message

### Validation Result

Extend result shape:

```ts
interface ValidationResult {
  missionId: string;
  passed: boolean;
  status: string;
  xpAwarded: number;
  attemptNumber: number;
  checks: {
    id: string;
    type: string;
    passed: boolean;
    message: string;
  }[];
  unlockedMissionIds: string[];
  scope: "mission" | "step";
  stepId?: string;
}
```

For step validation:

- `xpAwarded` must be `0`
- mission completion state must not change
- attempts may increment because the user asked the system to validate

## Proof Board Model

The proof board should derive visual resource rows from checks and check results.

Initial mapping:

| Check type | Visual resource |
| --- | --- |
| `s3_bucket_exists` | S3 bucket node |
| `s3_object_exists` | Object row inside bucket |
| `s3_object_body_equals` | Object content proof badge |
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

If a check type has no mapping, show a compact generic check row rather than hiding it.

## Frontend Components

### `MissionWorkbench`

Owns the mission detail layout.

Responsibilities:

- load mission detail
- start mission
- track active step
- call step validation
- call final mission validation
- pass result state to child components

### `MissionBrief`

Shows:

- title
- practical request
- services
- XP
- estimated time
- local-only status

### `MissionStepList`

Shows all steps with:

- active step expanded
- completed/validated steps collapsed
- locked future steps visually available but secondary

The UI should allow learners to inspect future steps, but the primary flow should guide them sequentially.

### `MissionStepCard`

Shows:

- title
- goal
- why
- target state
- action
- `Show CLI syntax` control
- copy command after reveal
- `Check Step` button
- step validation feedback

### `ResourceProofBoard`

Shows current known validation/proof state.

Inputs:

- mission checks
- latest validation result
- active step

Until validation runs, proof items should show an unknown/pending state, not failed.

### `CoachPanel`

Shows:

- mission status
- attempts
- hints
- reset
- final validation
- XP award after completion

## UI Rules

- Do not show a raw command list as the main mission body.
- Keep command blocks compact and hidden until requested.
- Use clear icon buttons and compact badges.
- Keep the dark graphite/emerald/lime visual direction.
- Avoid childish RPG visuals.
- Do not use large hero copy inside mission detail.
- Text must fit on mobile and desktop.
- Failed checks should be readable without AWS expertise.

## Backend Implementation Notes

### Mission Loader

Add Pydantic models:

```py
class TargetStateItem(BaseModel):
    label: str
    value: str

class StepSpec(BaseModel):
    id: str
    title: str
    goal: str
    why: Optional[str] = None
    target_state: List[TargetStateItem] = []
    action: str
    command_id: str
    check_ids: List[str] = []
    success: Optional[str] = None
    notes: Optional[str] = None
```

Add to `MissionDefinition`:

```py
steps: List[StepSpec] = []
```

Validation requirements:

- every `command_id` in `steps` must match a command ID in the same mission
- every `check_id` in `steps` must match a check ID in the same mission
- step IDs must be unique
- mission should still load when `steps` is omitted

### Step Validation

Endpoint should:

1. Load mission.
2. Confirm mission is started or completed.
3. If body has no `stepId`, use all checks and existing XP behavior.
4. If body has `stepId`, find step.
5. Select checks whose IDs are in `step.check_ids`.
6. Run existing validator primitives.
7. Return scoped result with `scope: "step"`.

## Authored Mission Copy Standard

Mission copy should be short and concrete.

Bad:

```text
S3 is a scalable object storage service from AWS.
```

Better:

```text
Your app needs a durable place for uploaded files. A bucket gives the app a named storage boundary, and each file becomes an object inside it.
```

Each step should answer:

- What are we making true?
- Why would a real system need it?
- What exact local state proves it?
- What should the learner try next?

## Acceptance Criteria

- Existing missions load without `steps`.
- Missions with invalid step command/check references fail fast in tests.
- `GET /missions/{id}` includes `steps`.
- Step validation runs only linked checks.
- Step validation does not award XP.
- Full validation still awards XP once.
- S3 mission has authored steps for bucket creation, object upload, and object proof.
- SQS mission has authored steps for queue creation, URL discovery, message send, and message receive/proof.
- UI no longer presents the command list as the primary mission experience.
