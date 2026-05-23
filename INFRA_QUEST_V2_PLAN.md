# Infra Quest V2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the story-driven Mission Workbench that teaches local AWS resource models before revealing CLI commands.

**Architecture:** Add a learner-facing `steps` layer to mission YAML, expose it through the FastAPI mission API, support scoped step validation, and replace the mission detail command list with a guided workbench and resource proof board. Existing commands, checks, XP, hints, reset, and local-only guardrails remain the foundation.

**Tech Stack:** FastAPI, Pydantic, SQLModel, pytest, Next.js, React, TypeScript, Tailwind CSS, lucide-react, Floci.

---

## Phase 1: Mission Step Schema

### Files

- Modify: `apps/api/app/mission_loader.py`
- Modify: `apps/api/tests/test_mission_loader.py`
- Modify: `missions/s3-first-bucket/mission.yml`
- Modify: `missions/sqs-first-message/mission.yml`
- Modify: `missions/cloud-explorer/mission.yml`

### Tasks

- [ ] Add `TargetStateItem` and `StepSpec` Pydantic models.
- [ ] Add `steps: List[StepSpec] = []` to `MissionDefinition`.
- [ ] Validate step IDs are unique inside each mission.
- [ ] Validate every `command_id` references an existing command.
- [ ] Validate every `check_id` references an existing check.
- [ ] Add loader tests for valid authored steps.
- [ ] Add loader tests for invalid command references.
- [ ] Add loader tests for invalid check references.
- [ ] Add loader tests for missions without steps.
- [ ] Author V2 steps for Cloud Explorer, First Bucket, and Queue the Message.

### Acceptance

- `pytest apps/api/tests/test_mission_loader.py` passes.
- Existing mission files without authored steps still load.
- Invalid authored step references fail during mission loading.

## Phase 2: Mission Detail API

### Files

- Modify: `apps/api/app/routes/missions.py`
- Modify: `apps/api/tests/test_mission_loader.py`
- Add or modify API route tests if a route test file exists.
- Modify: `apps/web/lib/api.ts`

### Tasks

- [ ] Serialize authored `steps` from mission detail.
- [ ] Convert snake_case YAML fields to camelCase API fields:
  - `target_state` -> `targetState`
  - `command_id` -> `commandId`
  - `check_ids` -> `checkIds`
- [ ] Derive fallback steps from `commands` when `steps` is empty.
- [ ] Ensure fallback steps keep `checkIds: []`.
- [ ] Update frontend `MissionDetail` TypeScript types with `MissionStep`.
- [ ] Add route/API tests confirming `steps` exists in mission detail.

### Acceptance

- `GET /missions/s3-first-bucket` returns authored steps.
- A mission without authored steps returns derived fallback steps.
- Existing frontend calls do not break.

## Phase 3: Step-Level Validation

### Files

- Modify: `apps/api/app/routes/missions.py`
- Modify: `apps/api/app/services/progress.py`
- Add or modify API validation tests.
- Modify: `apps/web/lib/api.ts`

### Tasks

- [ ] Accept optional JSON body on `POST /missions/{mission_id}/validate`.
- [ ] Preserve current no-body full validation behavior.
- [ ] Add `stepId` request handling.
- [ ] Select only checks linked to the requested step.
- [ ] Return `scope: "step"` and `stepId` for step validation.
- [ ] Return `scope: "mission"` for full validation.
- [ ] Ensure step validation never awards XP.
- [ ] Ensure step validation never marks mission completed.
- [ ] Add frontend API helper support: `validateMission(id, stepId?)`.

### Acceptance

- Full mission validation still completes missions and awards XP once.
- Step validation returns pass/fail for only that step's checks.
- Step validation leaves mission progress incomplete until full validation passes.

## Phase 4: Workbench Frontend

### Files

- Modify: `apps/web/components/MissionDetail.tsx`
- Create: `apps/web/components/MissionWorkbench.tsx`
- Create: `apps/web/components/MissionBrief.tsx`
- Create: `apps/web/components/MissionStepCard.tsx`
- Create: `apps/web/components/MissionStepList.tsx`
- Create: `apps/web/components/ResourceProofBoard.tsx`
- Modify: `apps/web/components/CommandBlock.tsx`
- Modify: `apps/web/components/ValidationPanel.tsx`
- Modify: `apps/web/components/HintPanel.tsx`
- Modify: `apps/web/components/ResetControl.tsx`

### Tasks

- [ ] Move mission detail layout into `MissionWorkbench`.
- [ ] Add `MissionBrief` for story/request, services, XP, and status.
- [ ] Add `MissionStepList` with active, pending, and checked states.
- [ ] Add `MissionStepCard` with goal, why, target state, action, command reveal, copy, and step check.
- [ ] Keep `CommandBlock`, but render it only after command reveal.
- [ ] Add `ResourceProofBoard` with pending/pass/fail states.
- [ ] Map initial check types to proof-board resource rows.
- [ ] Keep final mission validation in the coach/action panel.
- [ ] Keep hints and reset available without making them the main page.
- [ ] Keep current dark graphite/emerald/lime visual language.

### Acceptance

- Mission detail no longer shows a raw list of commands by default.
- The learner sees the mission request, target state, and active step first.
- `Show CLI syntax` reveals the command for the active step.
- `Check Step` calls step validation and updates the step/proof UI.
- `Complete Mission` calls full validation and awards XP when all checks pass.

## Phase 5: Resource Proof Board Mapping

### Files

- Modify: `apps/web/components/ResourceProofBoard.tsx`
- Add: `apps/web/components/proofBoard.ts` or equivalent helper if needed.

### Tasks

- [ ] Map S3 bucket checks to bucket proof rows.
- [ ] Map S3 object checks to object proof rows.
- [ ] Map S3 object body checks to content proof rows.
- [ ] Map SQS queue checks to queue proof rows.
- [ ] Map SQS message checks to message proof rows.
- [ ] Add generic fallback rows for unmapped check types.
- [ ] Show pending state before validation.
- [ ] Show failed state only after validation has run.

### Acceptance

- S3 mission proof board shows bucket, object, and body proof.
- SQS mission proof board shows queue and message proof.
- Unmapped future validators remain visible as generic proof items.

## Phase 6: Copy And Curriculum Pass

### Files

- Modify: `missions/cloud-explorer/mission.yml`
- Modify: `missions/s3-first-bucket/mission.yml`
- Modify: `missions/sqs-first-message/mission.yml`
- Optionally modify the remaining mission YAML files after the first three are verified.

### Tasks

- [ ] Rewrite Cloud Explorer as a boundary/safety mission.
- [ ] Rewrite First Bucket as durable onboarding-file storage.
- [ ] Rewrite Queue the Message as async background work.
- [ ] Keep copy concise and practical.
- [ ] Keep exact resource names deterministic.
- [ ] Keep all commands local-only.
- [ ] Keep all checks aligned with the target state.

### Acceptance

- First three missions explain why the resource exists.
- First three missions define exact target state before CLI syntax.
- Resource names remain compatible with existing validators.

## Phase 7: Verification

### Commands

- [ ] Run backend tests:

```bash
cd apps/api && uv run pytest
```

- [ ] Run frontend build:

```bash
cd apps/web && bun run build
```

- [ ] Run frontend typecheck:

```bash
cd apps/web && bun run typecheck
```

- [ ] Run local-only verification:

```bash
make verify
```

- [ ] Rebuild local web container if needed:

```bash
docker compose up -d --build web api
```

### Browser Acceptance

- [ ] Open `http://localhost:3000`.
- [ ] Confirm homepage still loads and matches the polished visual direction.
- [ ] Open Cloud Explorer mission.
- [ ] Confirm mission detail shows workbench, not raw command list.
- [ ] Reveal CLI syntax and confirm copy works.
- [ ] Run local command manually in terminal.
- [ ] Click `Check Step` and confirm proof board updates.
- [ ] Complete mission and confirm XP behavior.
- [ ] Open S3 mission and confirm target bucket/object/body proof is visible.
- [ ] Test a failed step before running the command and confirm feedback is useful.

## Rollout Notes

- Keep V1 docs intact for historical context.
- Keep this V2 doc set as the source of truth for the new UX direction.
- Do not add embedded terminal execution until the workbench and proof board are stable.
- If browser terminal execution is added later, it must be a separate design/spec because it changes the security model.
