# End-to-End Acceptance Matrix

Release branch: `implement-infra-quest-plan`
Recorded: 2026-05-26

| Area | Scenario | Required | Evidence | Status | Notes |
| --- | --- | --- | --- | --- | --- |
| Startup | Start with Compose on alternate ports | Yes | `make verify` Compose stage | Passed | Web, API, and Floci became reachable |
| Local-only boundary | Safety scan and runtime status | Yes | `verify-local-only.sh`, `/runtime/status` smoke output | Passed | No real AWS endpoint or credential path is used |
| Course map | Fetch course and module state | Yes | `smoke-test.sh` `/course` output | Passed | Modules, capabilities, progress, and next mission returned |
| Required lessons | Complete all required target-release lessons | Yes | `e2e-local-flow.py` | Passed | Orientation, S3, Lambda, API Gateway, DynamoDB, SQS, SNS, and operations recovery complete against Floci |
| Failed check recovery | Incorrect state repair path | Yes | Mission hints, failed proof rows, and reset controls reviewed in code and build | Passed | UI exposes nudge, diagnosis, repair, and failed proof messages |
| Resume | Return to started lesson | Yes | Persisted step progress tests and workbench resume logic | Passed | Active step selects first incomplete persisted step |
| Reset | Reset flow | Yes | API reset tests and visible workbench reset summary | Passed | Completed XP/history is preserved; proof can become stale; cleanup failures are shown |
| Runtime degraded | API/Floci/DB issue display | Yes | App shell/settings degraded states and `/runtime/status` diagnostics | Passed | Runtime issue is separated from lesson proof failure |
| Keyboard | Course/workbench controls | Yes | Semantic links/buttons, focus styles, and keyboard-scrollable command blocks in build | Passed | Primary controls are reachable as links or buttons; physical browser keyboard pass remains a public-tag evidence item |
| Mobile | Narrow workbench order | Yes | Mobile DOM order in `MissionWorkbench`, responsive class review, production build | Passed | Brief, active step, proof/coach/continuity, then step list; physical device/browser pass remains a public-tag evidence item |
| Desktop | Wide workbench layout | Yes | Production build route render | Passed | Three-column desktop workbench remains available |
| Privacy | Review settings/docs | Yes | `/settings`, privacy doc, README | Passed | Local DB path and no-telemetry posture are visible |
| Smoke | API/web/Floci smoke | Yes | `smoke-test.sh` in `make verify` | Passed | Health, runtime, missions, profile, and course endpoints respond |
| Capstone | Complete optional composition capstone workflow | Yes | `e2e-local-flow.py`, mission YAML, authoring validator, workflow validator tests, capstone score tests | Passed | API Gateway invokes Lambda; Lambda writes DynamoDB and sends SQS; local safety gate and latest/best score persistence pass |

## Browser Set

The automated gate proves runtime/API behavior, production build output, and source-level accessibility/layout controls. Manual browser verification should use current Chrome or Chromium, Safari on macOS, and Firefox when available before tagging a public release.

## Release Decision

The automated release gate passed locally. Public launch tagging should use this matrix plus a fresh manual browser pass on the target release machine.
