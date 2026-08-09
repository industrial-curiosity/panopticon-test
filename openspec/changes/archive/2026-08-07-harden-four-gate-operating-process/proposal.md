# Four-gate rollout operating process proposal

## Why

Panopticon's setup guidance describes provider configuration but does not give
maintainers one ordered way to distinguish reusable-workflow access,
effective configuration, caller identity, and provider-request compatibility.
That makes zero-job failures, per-child identity failures, and provider API
failures look interchangeable, and credential-action timeouts can hide the
recovery message needed to clear them.

## What Changes

- Add a public four-gate setup and troubleshooting process with observable
  symptoms, authoritative evidence, ownership, recovery, and proof for each
  gate.
- Add a deterministic private/internal reusable-workflow access check and
  explain caller-repository OIDC identity and per-child provisioning.
- Bound the instance-managed Bedrock credential step at its caller boundary
  and add an always-running recovery step for failure and timeout outcomes.
- Standardize failure summaries around gate, expected resource/name, scope,
  fix location, and rerun instructions.
- Add a protected-path maintenance-debt register and reconcile setup-guide
  wording, generated-caller counts, getting-started guidance, and testing
  documentation.

## Capabilities

### New Capabilities

- `four-gate-rollout-process`: Ordered operating and recovery guidance for
  workflow access, effective provider configuration, caller identity and
  credentials, and real provider-request compatibility.

### Modified Capabilities

- `pr-evaluation`: Provider workflows expose gate-specific recovery summaries
  and preserve credential-action failure guidance outside the action boundary.
- `llm-provider-configuration`: Provider setup documents the four gates,
  access checks, caller identity, and request-compatibility proof.
- `repo-initialization`: Child onboarding documents the pre-child access check
  and per-child identity/credential ownership boundary.

## Impact

Affected files include the public setup and getting-started guides, provider
recovery formatting, the Bedrock reusable workflow, provider-workflow tests,
testing documentation, and the three affected OpenSpec specifications. The
change is documentation- and diagnostics-focused; it does not add a provider,
change the trusted workflow registry, or accept credential values.
