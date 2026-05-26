# Clean-Machine Release Checklist

Release branch: `implement-infra-quest-plan`
Recorded: 2026-05-26

## Automated Clean Start

| Step | Command or Action | Expected Result | Result |
| --- | --- | --- | --- |
| Check release docs | `make verify-release-artifacts` | Required release docs are present | Passed locally |
| Run release gate | `make verify` | Safety scan, authoring gate, release docs, backend tests, API lint, web typecheck, web build, Compose smoke, and learner e2e pass | Passed locally |
| Clean learner DB before Compose gate | `rm -f data/api/lab.db` inside `make verify` | Container smoke and e2e start from clean progress | Passed locally |
| Stop verification stack | Final `docker compose down` in `make verify` | API, web, Floci containers and network stop cleanly on a successful gate run | Passed locally on successful gate run |

## Environment Used

| Item | Value |
| --- | --- |
| Branch | `implement-infra-quest-plan` |
| Commit | `c2b0ce0` |
| OS | macOS 26.5 |
| Docker engine | `28.2.2` |
| Verification command | `make verify` |
| API test result | `44 passed, 1 skipped` |
| Web checks | `bun run typecheck`, `NEXT_TELEMETRY_DISABLED=1 bun run build` |
| Runtime ports | API `18000`, web `13000`, Floci `14566` during verification |
| GitHub PR checks | PR #3 `verify` checks passed for commit `c2b0ce0` |

## Operator Notes

The release gate exercises a clean local learner database before starting Docker Compose, then validates all required target-release lessons and the optional composition capstone workflow through the browserless local e2e. A separate physical clean-machine/browser pass is tracked in the end-to-end matrix.

If `make verify` fails before its final cleanup step, stop the alternate-port verification stack manually with:

```bash
API_PORT=18000 WEB_PORT=13000 FLOCI_PORT=14566 NEXT_PUBLIC_API_URL=http://localhost:18000 docker compose down
```
