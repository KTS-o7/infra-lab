# Infra Quest

**Build a real SaaS backend in your browser, with zero AWS bill.**

Infra Quest isn't a tour of AWS services — it's the build log for a real project. You join Orbiton as a new engineer, work with tech lead Priya, and ship a piece of the LaunchDesk SaaS backend, mission by mission. Everything runs locally against Floci, our AWS emulator: no account, no bill, no $400 surprise when you forget to tear down a tutorial.

**What you'll actually do:**

- **Stand up an S3 bucket** for the broken-uploads bug that's been blocking customers, and watch the failures roll in.
- **Wire an order flow** API Gateway → Lambda → DynamoDB, end to end, the way a real backend does it.
- **Move a slow PDF job off the request path** by pushing it onto an SQS queue and processing it asynchronously.
- **Fan out a `lead.created` event** to multiple subscribers with SNS, so every team hears about new leads.
- **Diagnose a "production is down"** scenario using the same tools a real on-call would reach for.

**Who this is for:**

- **Beginners** learning AWS or serverless for the first time.
- **Students and career-switchers** who want a portfolio project that looks like a real backend, not a tutorial screenshot.
- **Workshop hosts and bootcamps** who need a zero-setup lab they can hand to a room of learners.

**Who this is NOT for:**

- **AWS Solutions Architect or Professional certification prep** — Infra Quest teaches you to ship, not to pass an exam.
- **Anyone who needs to run workloads in real AWS** — this is a local emulator only.

**Quick start:**

```bash
docker compose up --build
```

Then open [http://localhost:3000](http://localhost:3000) and pick your first mission.

## What is this?

Infra Quest teaches AWS by shipping a real backend, mission by mission. Every AWS call runs against **Floci**, a local AWS emulator — no account, no credentials, no cloud resources required. The pitch above tells you what you'll do; the sections below cover the technical details.

## Tech Stack

- **Floci** — Local AWS emulator
- **FastAPI** — Mission API and validators
- **Next.js** — Web app frontend
- **SQLite** — Progress persistence
- **Docker Compose** — Local orchestration

## Safety

This project is **local-only**. No real AWS endpoints are used. All CLI commands include `--endpoint-url http://floci:4566` when running inside the web terminal.

## Advanced: Running AI Agent in Local Terminal

By default, the "Ask me anything" chat runs its AI command inside the Docker container. If you want it to run in your **actual local terminal** (e.g. to use tools like `gemini` or `gh copilot` that are only installed on your host), follow these steps:

1.  Start the AMA Host Bridge on your local machine:
    ```bash
    python3 scripts/ama-host-bridge.py
    ```
2.  Set the following in your `.env`:
    ```bash
    AMA_HOST_BRIDGE=http://host.docker.internal:8080
    ```
3.  Restart Docker Compose:
    ```bash
    docker compose up -d
    ```

Learner progress and validation history are stored locally by the API service. See [Local Data And Privacy](docs/privacy/local-data-and-privacy.md) for what is stored, what must not be stored, and the reset expectations.

## Commands

```bash
make dev          # Start all services
make down        # Stop all services
make reset       # Reset lab data
make verify      # Run safety scan, tests, build, smoke, and learner e2e
make logs        # Tail Docker logs
```

## Mission Authoring

Create each lesson under `missions/<mission-id>/mission.yml`. Before opening a
change, run:

```bash
./scripts/validate-mission-authoring.py
make verify
```

Authoring checklist:

- Include all release fields: base mission metadata plus `capability`,
  `motivation`, `theory`, `thought_process`, and `debrief`.
- Keep every AWS CLI command local-only with
  `--endpoint-url http://localhost:4566`; never point examples at real AWS.
- Give every command an action-oriented label, and make every guided step
  reference an existing `command_id`.
- Define target state for every step and map it to real validation checks.
- Reference every check from at least one step, and reference only existing
  checks from steps and hints.
- Declare owned resources for resources created by mission commands so reset
  can clean up mission-owned state.
- Provide staged hints for normal lessons: `nudge`, `diagnosis`, and `repair`.
- For capstones, reduce command guidance: leave at least one step for learner
  reasoning instead of providing a copy command for every step.
- In `thought_process`, name the tradeoff or rejected alternative so learners
  understand why this design is being built.

## Release Checks

Release candidate documentation lives in `docs/release/`:

- [Beginner Usability Gate](docs/release/beginner-usability-gate.md)
- [Clean-Machine Release Checklist](docs/release/clean-machine-checklist.md)
- [End-to-End Acceptance Matrix](docs/release/end-to-end-acceptance-matrix.md)
- [Final Release Handoff](docs/release/final-handoff.md)
- [Known Issues Template](docs/release/known-issues-template.md)

The embedded terminal implementation plan is documented in [Embedded Terminal Security Design](docs/design/embedded-terminal-security.md).

```bash
make verify-release-artifacts
make verify
```

`make verify-release-artifacts` checks that required release files exist and
are non-empty. `make verify` is the full local gate for safety scan,
authoring validation, backend tests, API lint, web typecheck/build, smoke, and
browserless learner e2e.

## Troubleshooting

- **Floci image can't be pulled** — if `floci/floci:1.5.13` is unavailable from your network (rate limit, registry hiccup, behind a corporate proxy), set `FLOCI_IMAGE=localstack/localstack:3` in your `.env` and re-run `docker compose up --build`. LocalStack covers the same service APIs Infra Quest uses, so missions continue to work.
- **Something looks broken, but you're not sure what** — run `make verify`. It runs the local-only safety scan, mission authoring validation, backend tests, API lint, web typecheck and build, smoke tests, and the browserless learner end-to-end flow. If `make verify` passes, your local lab is healthy.
- **The "Ask me anything" panel is grayed out or returns an error** — the AMA chat needs `AMA_API_KEY` set in your `.env`. Uncomment the `AMA_API_KEY=your-key-here` line from `.env.example`, paste in your key, and restart with `docker compose up --build`.
