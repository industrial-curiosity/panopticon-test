# Harden rollout preflight feedback

## Why

The four-gate rollout guide has two gaps that slow recovery: private-workflow
access checks do not state the token permissions they require, and some
provider-workflow failures write GitHub error commands to stderr where the
runner does not create annotations.

## What Changes

- Document the required repository permissions and 403 recovery for the
  private-workflow access preflight, using only fields returned by that API.
- Require provider workflow failures to emit their actionable error annotation
  on stdout as well as writing the step summary.
- Add structural regression coverage for both behaviors.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `pr-evaluation`: Provider preflight failures must create an actionable
  GitHub annotation in addition to a step summary.
- `repo-initialization`: The private reusable-workflow access preflight must
  state its required GitHub token permissions and how to recover from 403.

## Impact

This changes the shared configuration action and Bedrock reusable workflow,
the setup and operator guidance, workflow structural tests, and the two
affected OpenSpec capability specifications.
