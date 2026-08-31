# Assert failure-path diagnostics

## Why

Template validation currently exercises expected operational failures whose
GitHub workflow-command output can appear as misleading annotations. The tests
must prove both that the failure is detected and that the resulting user-facing
diagnostic is clear and actionable, while keeping expected diagnostics out of
the workflow's annotation stream.

## What Changes

- Define a repository-wide testing contract for intentional failure-path tests.
- Require tests to capture and assert the failure signal they claim to test,
  including exceptions, exit statuses, user-facing output, and reports.
- Capture expected CLI diagnostics in validation tests so passing tests do not
  create false GitHub error annotations.
- Add regression coverage for the doc-drift, index-currency,
  diagram-existence, interface-merge, and dependency-merge failure paths.

## Capabilities

### New Capabilities

- `failure-path-diagnostics`: Ensures intentional failure tests verify detected
  failures and actionable diagnostics without polluting successful CI results.

### Modified Capabilities

- None.

## Impact

Affected artifacts include the Python test helpers for validation and merge
checks, their failure-path assertions, and the repository's testing guidance.
No production check exit-code contract, provider behavior, or public API
changes.
