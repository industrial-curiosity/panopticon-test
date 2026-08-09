# Design: Harden rollout preflight feedback

## Context

Four-gate rollout troubleshooting already requires a step summary and a concise
workflow annotation. Two failure paths construct `SystemExit` with a workflow
command string, which Python writes to stderr. The private-instance access
preflight also treats generic authentication as sufficient even though its API
needs instance-repository administration read permission.

## Goals / Non-Goals

**Goals:**

- Make provider-configuration and Bedrock gate failures visible as GitHub
  annotations and retain their detailed step summaries.
- Make the access preflight's authentication prerequisites and 403 recovery
  deterministic for instance administrators.
- Prevent regression with repository structural tests.

**Non-Goals:**

- Change the instance token's least-privilege permissions for normal CI work.
- Automate Actions access-policy changes or alter GitHub's access policy.
- Change the full OpenSpec validation issue in the unrelated `master-sync`
  capability.

## Decisions

- Emit `::error::` through Python `print()` before the non-zero exit. GitHub
  Actions parses workflow commands from stdout, and the existing step summary
  remains the durable location for recovery detail.
- Document a separate instance-administrator token for the preflight with
  `Administration: Read` and `Contents: Read`, rather than adding
  administration permission to the child runtime token.
- Query only `.access_level`, the documented response field for the access
  endpoint. On HTTP 403, direct the operator to reauthenticate with the stated
  permission instead of interpreting it as the instance access policy.

## Risks / Trade-offs

- [A token with the required access is unavailable] → The guide identifies the
  exact permission and keeps the policy decision with the instance
  administrator.
- [A future workflow emits an error on stderr] → Structural tests require the
  stdout emission pattern in both affected failure paths.
