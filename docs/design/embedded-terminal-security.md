# Embedded Terminal Security Design

This design covers a future embedded terminal milestone. It is intentionally separate from the current release gate so implementation can happen without weakening the local-only guarantee.

## Decision

Commands should execute in a separate runner container, not directly in the browser and not inside the API process.

Rationale:

- The browser cannot safely execute shell commands.
- The API should remain a mission and validation service, not a shell host.
- A runner container can have a narrow filesystem mount, constrained environment, explicit network rules, and disposable lifecycle.

## Execution Boundary

The runner should:

- run with fake AWS credentials only
- default `AWS_ENDPOINT_URL` to the local Floci endpoint
- block or rewrite attempts to use real AWS endpoints
- mount only the workspace paths needed for mission assets
- run as a non-root user
- avoid Docker socket access
- enforce command timeout and output size limits
- expose a small API for starting commands, streaming output, and cancelling commands

The runner should not:

- read host-level AWS config directories
- inherit the developer shell environment
- access arbitrary host filesystem paths
- call `amazonaws.com` or other real AWS service endpoints

## Command Allowance Model

Start with an allowlist for beginner release commands:

- `aws` with local endpoint enforcement
- `curl` against local app and Floci endpoints
- `python3` for simple JSON formatting where already used by scripts
- read-only inspection commands needed by lessons

Any command outside the allowlist should produce a learner-readable refusal that explains the local-only boundary.

## Endpoint Guard

The runner should reject command lines and environment variables that include:

- `amazonaws.com`
- `AWS_PROFILE` values from the host
- non-local `--endpoint-url` values
- credential-looking values that are not the documented fake credentials

Validation should also happen server-side before execution. Client-side checks may improve feedback but are not a security boundary.

## Command History

Store command history by mission and step in local progress storage.

Suggested fields:

- mission ID
- step ID
- command text
- start time and end time
- exit code
- truncated stdout and stderr
- local-only guard result

History should be reset with learner progress. It should not sync remotely.

## Output Streaming

Use a streaming channel from runner to API to web client. Server-sent events are sufficient for one-way command output; WebSockets are only needed if interactive input becomes required.

Output handling rules:

- stream stdout and stderr separately when possible
- redact credentials before persistence and display
- cap retained output size per command
- preserve exit code and timeout reason
- allow validation actions to run after command completion

## Validation Integration

After a command exits, the workbench may offer or trigger validation for the current step. Validation should still inspect local infrastructure state through existing validators; it should not trust terminal output as proof.

## Security Limits

This terminal is a beginner convenience feature, not a general sandbox for untrusted code. The release documentation should state that it runs local commands in a constrained container and that users should not paste secrets into it.
