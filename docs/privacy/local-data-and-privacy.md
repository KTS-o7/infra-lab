# Local Data And Privacy

Infra Quest is designed as a local-only learning lab. It should not require a real AWS account, real AWS credentials, or outbound telemetry for the learner flow.

## Local Data

The app stores learner progress in the local API service using SQLite. The database is container-local unless the compose configuration maps it to a host volume. Reset commands are expected to remove Infra Quest-owned local progress and sandbox resources only.

Data that may be stored locally:

- mission completion state
- step progress
- validation attempts
- hint usage
- XP, badges, and course completion state
- local runtime diagnostics

Data that should not be stored:

- real AWS access keys
- real cloud account identifiers
- secrets pasted into terminal output or logs
- remote telemetry identifiers

## Network Boundary

AWS-compatible commands must target the local Floci endpoint:

```bash
--endpoint-url http://localhost:4566
```

Service-to-service calls inside Docker may use the container network host for Floci. Documentation and learner-facing commands should keep the local endpoint explicit.

## Logs

Logs are for local troubleshooting. They should be useful for debugging setup, validation, reset, and mission progress without collecting secrets.

Logging rules:

- redact credentials and token-like values
- do not log full command environments
- do not log real AWS profile data
- prefer local resource names, mission IDs, and validation result codes
- keep telemetry off by default

## Reset Expectations

`make reset` should clean Infra Quest-owned local state. It must not delete user files outside the lab workspace and must not call real AWS services.

Before a release, verify reset behavior through the clean-machine checklist and the end-to-end acceptance matrix.
