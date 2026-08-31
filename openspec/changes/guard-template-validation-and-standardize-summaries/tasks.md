# Guard template validation and standardize workflow summaries tasks

## 1. Scope template validation

- [x] 1.1 Add the exact canonical-template repository condition to the
  `template-validation.yml` validation job so instances create no runnable
  template-validation job.
- [x] 1.2 Extend workflow-contract tests to reject a missing, altered, or
  misplaced template-validation guard.

## 2. Add workflow-purpose preambles

- [x] 2.1 Inventory every step-bearing job in shipped GitHub Actions workflows
  and add its brief, non-sensitive purpose preamble as the first summary write.
- [x] 2.2 Preserve existing success, failure, and recovery summary content
  after each preamble; do not alter provider credentials, caller contracts, or
  gates.
- [x] 2.3 Add deterministic tests that require the preamble on every
  step-bearing workflow job and exempt only caller-only reusable-workflow
  delegation jobs.

## 3. Verify and document

- [x] 3.1 Run the focused workflow-contract tests and the complete Python test
  suite.
- [x] 3.2 Update README.md and docs/spec.md to reflect any user-facing or
  architectural changes introduced by this change.
