# Four-gate rollout operating process design

## Context

Panopticon has separate controls for child callers, private instance
workflows, provider contracts, GitHub OIDC, and provider preflight. The setup
guide currently presents those controls in provider-specific fragments, while
the Bedrock reusable workflow invokes an instance-owned composite credential
action without a caller-side timeout or a surviving recovery step. A reusable
workflow can also fail before a job exists, so job logs are not authoritative
for access or workflow-compilation failures.

The template is public and is copied into private instances. All guidance and
recovery text must therefore use placeholders and synthetic examples only. The
trusted provider registry and explicit caller mappings remain closed; this
change adds operating evidence without adding runtime extension points.

## Goals / Non-Goals

**Goals:**

- Define four ordered gates and the evidence required to advance from each.
- Give maintainers a deterministic access-policy check before child bootstrap
  and distinguish access denial from a missing or invalid workflow file.
- Make caller identity and credential ownership explicit, including the fact
  that an OIDC subject identifies the child caller repository.
- Bound the instance-managed credential action at the workflow step boundary
  and report failure or timeout from a later `always()` step.
- Standardize recovery summaries and public setup/getting-started/testing docs.
- Track protected-path customizations as reviewable maintenance debt.

**Non-Goals:**

- No new provider, credential action implementation, IAM policy, or provider
  endpoint is introduced.
- No organization-specific links, account IDs, role names, model IDs, or
  credential values are committed to the public template.
- No real sandbox run or live provider inference is claimed by local tests.
- No child-specific workflow path, action path, or arbitrary workflow step is
  accepted from configuration.

## Decisions

### Use a four-gate table as the public operating contract

The setup guide will contain one ordered table with symptom, authoritative
evidence, owner/scope, recovery, and proof columns. A shorter copy in
`PANOPTICON.md` keeps the last-proven-gate procedure available in a child
repository. This is preferred to four disconnected provider checklists because
the same boundaries apply to all providers and the failure sequence is
serial: a later gate is not observable until earlier gates pass.

### Check workflow access before checking workflow content

The guide will use the instance Actions access endpoint
`repos/{owner}/{repo}/actions/permissions/access` and the corresponding
Settings → Actions → General → Access page before asking a maintainer to edit
YAML. A separate contents lookup may confirm the selected workflow at the
selected ref. This preserves the distinction between an inaccessible private
workflow and a missing/invalid file, both of which can present as a zero-job
"workflow was not found" failure.

### Keep credential recovery outside the composite action

The Bedrock workflow will assign an ID to the instance-managed credential
step, set a one-minute step timeout (a supported caller-step boundary), and
follow it with a shell step guarded by `always()` and a non-success,
non-skipped outcome. The reporter writes the summary and exits non-zero. It is
outside the composite action because cancellation can prevent code inside that
action from writing recovery guidance. The reporter will name the fixed action
path, caller repository, expected identity boundary, registration owner, and
rerun path without printing credentials.

### Prefer shared formatter text with a self-contained fallback

`panopticon/recovery.py` will provide the credential-failure section used by
the workflow when the child-vendored formatter is available. The workflow will
retain a small inline fallback for older children that fail before the
formatter is available. Existing stale/missing-provider recovery remains
compatible and gains gate labels where appropriate.

### Treat provider compatibility as a real-request proof

Preflight remains a capability/credential check, not proof that the selected
model accepts the full request. The guide and testing docs will require one
real structured inference after preflight, and will direct request-shape or
model errors to the provider adapter/model owner rather than to IAM or workflow
access owners.

### Keep protected paths as a debt register

The setup guide will require each `protected_paths` entry to carry reason,
owner, upstream issue/change, last reconciliation result, and removal
condition in a nearby table. The field remains the existing exact-path list;
the table is operational metadata and does not alter sync semantics.

## Risks / Trade-offs

- [A timeout may be too short for an organization's credential wrapper] → Use
  a documented one-minute starting bound, keep it at the caller boundary, and
  raise it only when a measured successful wrapper needs more time.
- [A later `always()` step may not run after the whole job timeout] → Keep the
  credential bound below the job timeout and state that a job-level timeout
  still requires run-page evidence; do not place the recovery inside the
  cancellable composite action.
- [Generic recovery text cannot prescribe every IAM or registration system]
  → Name the ownership boundary and give an exact placeholder command/UI
  shape; require the instance owner to substitute its approved registration
  mechanism.
- [A public guide can drift from workflow structure] → Add structural tests
  for the timeout, outcome guard, expected recovery markers, caller count, and
  gate text, then run the full stdlib test suite and OpenSpec validation.

## Migration Plan

1. Sync the template into an instance and run the workflow-contract validator.
2. Add the four-gate documentation and access check to the instance's
   onboarding checklist.
3. In Bedrock `instance-managed` mode, review the caller timeout and test a
   successful credential action plus a deliberately unregistered child in a
   non-production sandbox.
4. Reconcile each protected path using the debt-register columns; retain a
   path only while its upstream replacement is unresolved.
5. Re-bootstrap children after provider contract or caller changes, then prove
   gates in order with a real provider request.

Rollback is limited to reverting the template workflow/docs change. An
instance may temporarily keep its prior caller while the change is reverted,
but the provider contract revision and explicit caller mappings remain the
source of truth.

## Open Questions

- Each organization must choose its own per-child identity registration system
  and the owner who can approve it; the public template cannot choose one.
- A sandbox rollout must choose a supported model and safe test repository
  before step 9 can be marked operationally proven.
