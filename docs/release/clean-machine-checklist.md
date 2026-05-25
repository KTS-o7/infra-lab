# Clean-Machine Release Checklist

Run this checklist on a machine or user account that does not already have Infra Quest containers, volumes, or cached build output.

## Prerequisites

- Docker and Docker Compose are installed.
- `make`, `curl`, `python3`, `rg`, `uv`, and `bun` are available.
- No real AWS credentials are required.

## Setup

| Step | Command or Action | Expected Result | Result |
| --- | --- | --- | --- |
| Clone repo | `git clone <repo-url> && cd infra-lab` | Repository is available locally |  |
| Check branch | `git branch --show-current` | Release branch is selected |  |
| Check docs | `make verify-release-artifacts` | Required release docs are present |  |
| Start lab | `make dev` | Web, API, and Floci containers start |  |
| Open web app | `http://localhost:3000` | Course map or mission entry screen loads |  |
| Stop lab | `make down` | Containers stop cleanly |  |

## Release Gate

| Step | Command or Action | Expected Result | Result |
| --- | --- | --- | --- |
| Full verification | `make verify` | Safety scan, artifact check, tests, build, and smoke test pass |  |
| Reset lab | `make reset` | Local lab data is reset without touching real cloud resources |  |
| Restart after reset | `make dev` | App starts and shows clean progress |  |

## Notes

- Record operating system, Docker version, and any non-default ports.
- If `make verify` fails because dependencies are missing, document the missing prerequisite and whether README setup needs to change.
- If ports are occupied, re-run with alternate ports only after recording the default-port failure.
