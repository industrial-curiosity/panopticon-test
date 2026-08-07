# PR evaluation delta

## MODIFIED Requirements

### Requirement: Provider workflow failures have actionable summaries

Each provider-specific PR-evaluation workflow SHALL write the detected failure
reason and a corrective action to the GitHub Actions step summary before any
explicit non-zero exit caused by invalid provider configuration, a missing or
timed-out credential action, missing caller identity, or a failed branch-state
index merge. Its concise workflow annotation SHALL direct the maintainer to
the summary and SHALL be emitted on stdout so GitHub Actions creates the
annotation. The summary SHALL identify the failed gate, expected configured
name or resource, whether the repair is instance-wide or per child, where to
fix it, and how to rerun.

#### Scenario: Caller identity is unavailable

- **WHEN** the credential setup succeeds but the caller's cloud identity
  cannot be verified
- **THEN** the workflow fails before provider preflight with a gate-3 summary
  naming the child caller, the configured credential mode/resource, the
  per-child identity owner, and the exact registration or caller-regeneration
  action

#### Scenario: Bedrock credential action is unavailable

- **GIVEN** the instance selects `instance-managed` Bedrock credentials
- **WHEN** the checked-out instance lacks
  `.github/actions/panopticon-aws-credentials/action.yml`
- **THEN** the Bedrock workflow emits its annotation on stdout, exits non-zero
  before provider preflight, and its step summary identifies the required
  action path and the available credential-mode recovery

#### Scenario: Branch-state merge fails

- **WHEN** either provider workflow cannot merge the PR branch state into the
  instance branch
- **THEN** it exits non-zero and its step summary identifies the failed merge,
  its exit status, the affected instance resource, and the instruction to
  correct the reported index or configuration problem before rerunning
