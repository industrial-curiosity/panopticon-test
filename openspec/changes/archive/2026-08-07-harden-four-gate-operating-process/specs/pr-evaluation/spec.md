# PR evaluation

## MODIFIED Requirements

### Requirement: Bedrock credential modes preserve the evaluation contract

The Bedrock reusable workflow SHALL obtain AWS credentials after checking out
the instance and before provider preflight. In `github-oidc` mode, it SHALL
configure the selected AWS IAM role and region through GitHub OIDC. In
`instance-managed` mode, it SHALL invoke only the fixed checked-out instance
action at `.github/actions/panopticon-aws-credentials/action.yml`, SHALL bound
that action at the calling workflow-step boundary where GitHub Actions supports
the bound, and SHALL run a later caller-owned recovery step when the action
fails or times out. The recovery step SHALL run under an `always()`-style
condition, remain outside the composite action, identify the caller identity
and fixed action resource expected, and preserve the same evaluation,
reporting, gating, and branch-push behavior after successful credentials.

#### Scenario: Instance-managed credentials run provider evaluation

- **WHEN** a Bedrock instance selects `instance-managed` and its fixed
  credential action succeeds
- **THEN** provider preflight and the subsequent PR evaluation use the
  credentials and region it supplied, and the caller-owned recovery step is
  silent because the credential step outcome is successful

#### Scenario: Credential action fails or times out

- **WHEN** the fixed instance-managed credential action returns failure or is
  terminated by its caller-step timeout
- **THEN** a later `always()`-guarded caller step writes a gate-specific summary
  naming `.github/actions/panopticon-aws-credentials/action.yml`, the child
  caller repository, the instance/child ownership boundary, the exact identity
  registration recovery, and the rerun proof, then exits non-zero

#### Scenario: Credential action cannot be redirected

- **WHEN** a provider configuration contains a credential-action path override
- **THEN** the workflow rejects the invalid contract before invoking any action
  or LLM work

### Requirement: Provider workflow failures have actionable summaries

Each provider-specific PR-evaluation workflow SHALL write the detected failure
reason and a corrective action to the GitHub Actions step summary before any
explicit non-zero exit caused by invalid provider configuration, a missing or
timed-out credential action, missing caller identity, or a failed branch-state
index merge. Its concise workflow annotation SHALL direct the maintainer to
the summary. The summary SHALL identify the failed gate, expected configured
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
- **THEN** the Bedrock workflow exits non-zero before provider preflight and its
  step summary identifies the required action path and the available
  credential-mode recovery

#### Scenario: Branch-state merge fails

- **WHEN** either provider workflow cannot merge the PR branch state into the
  instance branch
- **THEN** it exits non-zero and its step summary identifies the failed merge,
  its exit status, the affected instance resource, and the instruction to
  correct the reported index or configuration problem before rerunning
