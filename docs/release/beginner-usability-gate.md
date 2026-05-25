# Beginner Usability Gate

Use this gate before a release candidate when the target learner is a first-time cloud beginner. The gate is passed only when three beginner sessions complete without source-code help and without believing real AWS is being used.

## Participant Profile

- Has basic terminal familiarity.
- Has Docker installed or can follow the install prerequisite.
- Has not contributed to Infra Quest.
- Is not given implementation files or mission source.

## Session Script

1. Start from a fresh clone or a clean working tree.
2. Ask the learner to read the README quick start only.
3. Ask the learner to start the lab.
4. Ask the learner to open the web app.
5. Ask the learner to complete the orientation mission.
6. Ask the learner to complete the first storage mission.
7. Ask the learner to intentionally run or submit one incorrect step, then recover using the UI.
8. Stop and restart the lab.
9. Ask the learner to confirm their progress resumes.
10. Ask the learner what capability they added and whether any real AWS account was used.

Do not explain AWS concepts unless the learner is blocked after using the in-product help path. Record the help path that failed before intervening.

## Observation Checklist

Record one row per participant.

| Check | Pass/Fail | Notes |
| --- | --- | --- |
| Starts lab from README without source-code help |  |  |
| Understands the lab is local-only |  |  |
| Finds the next recommended mission |  |  |
| Completes Module 0 |  |  |
| Completes first storage mission |  |  |
| Recovers from one failed check without reset |  |  |
| Restarts and resumes progress |  |  |
| Explains the capability added in plain language |  |  |
| Avoids real AWS credentials and endpoints |  |  |
| Uses help without reaching a dead end |  |  |

## Fix Log

Track issues found during the three sessions and link the fixing change.

| Date | Participant | Issue | Severity | Fix | Re-test Result |
| --- | --- | --- | --- | --- | --- |
| YYYY-MM-DD | P1 |  | Blocker/Major/Minor |  |  |
| YYYY-MM-DD | P2 |  | Blocker/Major/Minor |  |  |
| YYYY-MM-DD | P3 |  | Blocker/Major/Minor |  |  |

## Release Decision

- Pass: all three learners complete the gate, can explain the added capability, and do not think real AWS is used.
- Fail: any learner needs source-code help, uses real AWS credentials, cannot recover from a failed check, loses progress after restart, or hits a layout issue that hides a primary action.
