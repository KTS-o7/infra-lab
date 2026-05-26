# Beginner Usability Gate

Release branch: `implement-infra-quest-plan`
Recorded: 2026-05-26
Commit: `c2b0ce0`

## Target Learner

- Has basic terminal familiarity.
- Has Docker installed or can follow the prerequisite.
- Has not contributed to Infra Quest.
- Is not given implementation files or mission source.

## Automated Proxy Result

| Check | Evidence | Result |
| --- | --- | --- |
| Starts lab through Compose gate | `make verify` builds and starts the same Compose stack on alternate ports | Passed |
| Understands local-only posture | README, `/settings`, runtime local-only status | Passed |
| Finds next recommended mission | `/course` and course map next mission state | Passed |
| Completes all required lessons | `e2e-local-flow.py` | Passed |
| Completes optional composition capstone | `e2e-local-flow.py` API Gateway to Lambda to DynamoDB/SQS workflow | Passed |
| Recovers from failed state | Hints, proof rows, reset controls, and validation messages | Passed |
| Restarts and resumes progress | Persisted progress tests and workbench resume logic | Passed |
| Avoids real AWS credentials and endpoints | Local-only scan and command authoring validation | Passed |
| Uses help without reaching a dead end | Authoring validator enforces staged hints | Passed |

## Human Session Script

1. Start from a fresh clone or a clean working tree.
2. Ask the learner to read the README quick start only.
3. Ask the learner to start the lab.
4. Ask the learner to open the web app.
5. Ask the learner to complete the required lesson path through operations.
6. Ask the learner to explain each capability they added: local runtime, storage, function, HTTP API, database, queue, event fanout, and operations recovery.
7. Ask the learner to intentionally run one incorrect step, then recover using the UI.
8. Stop and restart the lab.
9. Ask the learner to confirm progress resumes.
10. Ask whether any real AWS account was used.

## Release Decision

The automated proxy gate passed for all required target-release lessons and the optional composition capstone workflow. Before a public marketing launch, run the human session script with three first-time learners and record the outcomes in the release notes for that tag.
