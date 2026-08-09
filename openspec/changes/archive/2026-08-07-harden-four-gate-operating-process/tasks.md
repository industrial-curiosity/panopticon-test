# Four-gate rollout operating process tasks

## 1. Recovery and Bedrock workflow boundary

- [x] 1.1 Extend `panopticon/recovery.py` with gate-labelled
  instance-managed credential failure guidance and add exact-output tests for
  failure, timeout, caller scope, fixed action path, and rerun instructions.
- [x] 1.2 Update the Bedrock reusable workflow to bound the
  instance-managed credential step at the caller boundary, verify the caller
  identity before provider preflight, and add an `always()`-guarded recovery
  step that survives credential-action failure or timeout.
- [x] 1.3 Extend provider-workflow structural tests to cover the timeout,
  outcome guard, identity proof, gate-specific summary markers, and absence of
  organization-specific values.

## 2. Operating and onboarding documentation

- [x] 2.1 Add the ordered four-gate table, private/internal workflow access UI
  and API preflight, caller OIDC identity/per-child provisioning guidance,
  real-request compatibility proof, and protected-path debt-register template
  to `docs/setup-guide.md`.
- [x] 2.2 Update `PANOPTICON.md` with the concise last-proven-gate procedure,
  the child identity boundary, and the exact public-safe recovery commands.
- [x] 2.3 Update `docs/testing.md` with the four-gate static checks, structural
  workflow expectations, and sandbox proof boundary; fix generated-caller
  counts and duplicated setup wording where discovered.

## 3. Contracts, project docs, and verification

- [x] 3.1 Apply the four-gate requirements to the canonical PR-evaluation,
  provider-configuration, and repository-initialization specifications, and
  update `README.md` and `docs/spec.md` for the user-visible operating model.
- [x] 3.2 Update the rollout plan's step-7 status with the local verification
  evidence while preserving the distinction between locally verified and
  operationally proven.
- [x] 3.3 Run focused recovery/workflow tests, the full stdlib suite, affected-
  spec strict OpenSpec validation, and Markdown/style checks; record any
  repository-wide failures outside this change with the exact command, failing
  item, reason, scope, and next action before marking the change complete.

### Validation exception

The repository-wide command `openspec validate --all --strict --no-interactive`
passes 15 of 16 specs. The pre-existing `master-sync` failure is
`requirements.3.text`: its `SHALL` keyword is not on the first physical
requirement line. Follow-up: move `SHALL` onto that line and rerun full
validation.
