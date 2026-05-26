# Clean-Machine Release Checklist

Release branch: `implement-infra-quest-plan`
Recorded: 2026-05-26

## Automated Clean Start

| Step | Command or Action | Expected Result | Result |
| --- | --- | --- | --- |
| Check release docs | `make verify-release-artifacts` | Required release docs are present | Passed locally |
| Run release gate | `make verify` | Safety scan, authoring gate, release docs, backend tests, lint, typecheck, build, Compose smoke, and learner e2e pass | Passed locally |
| Clean learner DB before Compose gate | `rm -f data/api/lab.db` inside `make verify` | Container smoke and e2e start from clean progress | Passed locally |
| Stop verification stack | Final `docker compose down` in `make verify` | API, web, Floci containers and network stop cleanly | Passed locally |

## Environment Used

| Item | Value |
| --- | --- |
| Branch | `implement-infra-quest-plan` |
| Verification command | `make verify` |
| API test result | `44 passed, 1 skipped` |
| Web checks | `bun run typecheck`, `NEXT_TELEMETRY_DISABLED=1 bun run build` |
| Runtime ports | API `18000`, web `13000`, Floci `14566` during verification |

## Operator Notes

The release gate exercises a clean local learner database before starting Docker Compose, then validates all required target-release lessons and the optional composition capstone workflow through the browserless local e2e. A separate physical clean-machine/browser pass is tracked in the end-to-end matrix.
