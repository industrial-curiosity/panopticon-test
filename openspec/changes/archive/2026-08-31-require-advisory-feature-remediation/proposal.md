# Require advisory feature remediation

## Why

Enabled advisory feature findings currently remain non-blocking, but they are
not reliably surfaced as required agent work. An agent can complete
`panopticon-init`, delete its checkpoint, and leave remediable OKF findings in
place, conflating non-gating enforcement with optional work.

## What Changes

- Define advisory feature findings as mandatory agent remediation while keeping
  them non-blocking for initialization and PR gates.
- Require `panopticon-init` to discover enabled feature packages, follow their
  installed skills, remediate deterministic findings, and revalidate before it
  declares initialization complete.
- Preserve unresolved advisory findings as durable child-repository action
  items with the feature skill and revalidation command.
- Prevent organization-verification reporting from discarding feature
  findings.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `repo-initialization`: make feature remediation part of initialization
  orchestration and durable finalization reporting.
- `instance-feature-packages`: distinguish advisory CI enforcement from
  mandatory agent remediation.

## Impact

Affected surfaces include `panopticon.init_repo`, the `panopticon-init` and
feature skill contracts, initialization reports, and their tests. The change
does not alter feature mode names, PR gate outcomes, or organization-level
configuration requirements.
