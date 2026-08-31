# Require advisory feature remediation tasks

## 1. Make advisory remediation an agent contract

- [x] 1.1 Update `panopticon-init` to discover enabled features from the
  managed receipt, invoke their installed skills after documentation generation,
  and revalidate them before finalization.
- [x] 1.2 Update feature skill guidance so advisory means required agent
  remediation with non-blocking CI enforcement, not optional migration work.
- [x] 1.3 Retain the initialization checkpoint when an agent-remediable
  advisory feature finding remains, and give the exact skill and revalidation
  command needed to continue.

## 2. Preserve feature findings in finalization

- [x] 2.1 Keep advisory feature findings in the finalization result while
  appending organization-verification findings instead of overwriting them.
- [x] 2.2 Render unresolved advisory feature findings as `Child repository`
  report items with the feature ID, affected finding, feature skill, and
  revalidation command.
- [x] 2.3 Keep advisory feature findings non-blocking for the initialization
  flag and shared PR gates.

## 3. Add regression coverage

- [x] 3.1 Test that an OKF advisory finding invokes feature remediation and
  revalidation before `panopticon-init` completes.
- [x] 3.2 Test that unresolved advisory findings retain the checkpoint and
  remain actionable even when they do not block a PR or initialization flag.
- [x] 3.3 Test that advisory feature and organization verification findings
  coexist in the durable initialization report.

## 4. Verify and document the behavior

- [x] 4.1 Run focused initialization and feature tests plus the complete Python
  test suite.
- [x] 4.2 Validate the OpenSpec change and all Markdown artifacts in strict
  mode.
- [x] 4.3 Update README.md and docs/spec.md to reflect any user-facing or architectural changes introduced by this change
