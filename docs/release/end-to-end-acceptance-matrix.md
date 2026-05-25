# End-to-End Acceptance Matrix

Use this matrix for the release candidate browser pass. Required rows must pass before release.

| Area | Scenario | Required | Expected Result | Status | Notes |
| --- | --- | --- | --- | --- | --- |
| Startup | Start with `make dev` | Yes | Web, API, and Floci become reachable |  |  |
| Local-only boundary | Inspect commands and runtime copy | Yes | No real AWS account, credential, or endpoint is requested |  |  |
| Course map | Open first screen | Yes | Modules, mission state, and next recommendation are clear |  |  |
| Orientation | Complete Module 0 | Yes | Learner proves the sandbox is local and ready |  |  |
| Storage | Complete first storage mission | Yes | Bucket/object target state is validated locally |  |  |
| Failed check recovery | Submit an incorrect state | Yes | UI explains failure and provides repair path |  |  |
| Resume | Restart API/web and return | Yes | Progress resumes at the best known incomplete step |  |  |
| Reset | Run reset flow | Yes | Owned local resources and/or progress are removed according to selected mode |  |  |
| Runtime degraded | Stop Floci during app use | Yes | Runtime issue is distinguished from lesson failure |  |  |
| Keyboard | Navigate course map and workbench by keyboard | Yes | Interactive controls are reachable and visible focus is present |  |  |
| Mobile | Test narrow viewport around 390px width | Yes | Core learning flow is usable without overlapping text |  |  |
| Desktop | Test desktop viewport around 1440px width | Yes | Layout uses space without hiding proof or help panels |  |  |
| Privacy | Review settings/docs | Yes | Local data location and no-telemetry posture are stated |  |  |
| Smoke | Run smoke test | Yes | Health, runtime, missions, profile, and course endpoints respond |  |  |
| Capstone | Open optional composition capstone | Yes | Capstone visual treatment, reduced command guidance, proof board, score area, and debrief path are visible |  |  |

## Browser Set

- Chrome or Chromium latest stable.
- Safari latest stable on macOS, if available.
- Firefox latest stable, if available.

## Release Decision

- Pass: every required scenario passes.
- Fail: any required scenario blocks a beginner from completing the target course slice, hides a primary action, corrupts progress, or weakens the local-only guarantee.
