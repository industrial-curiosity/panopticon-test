# Assert failure-path diagnostics tasks

## 1. Define the failure-path testing contract

- [x] 1.1 Document the language-agnostic rule that intentional failure tests
  SHALL capture and assert the expected exception, exit status, user-facing
  output, or failure report.
- [x] 1.2 Document that captured diagnostics SHALL remain actionable and SHALL
  not be discarded solely to suppress test output.

## 2. Apply the contract to CLI failure tests

- [x] 2.1 Update doc-drift and index-currency test helpers to retain captured
  stdout and assert check-specific operational failure diagnostics.
- [x] 2.2 Update diagram-existence test coverage to retain captured stdout and
  assert unsupported-format diagnostics.
- [x] 2.3 Update interface-merge and dependency-merge test helpers to retain
  captured stdout and assert operational failure diagnostics.
- [x] 2.4 Preserve assertions for non-business exit statuses and generated
  failure reports across all covered checks.

## 3. Verify the implementation

- [x] 3.1 Run focused failure-path tests and confirm expected diagnostics are
  captured without becoming CI annotations.
- [x] 3.2 Run the complete Python test suite and confirm real assertion
  failures still produce a nonzero result.
- [x] 3.3 Validate the OpenSpec change and all Markdown artifacts in strict
  mode.
- [x] 3.4 Update README.md and docs/spec.md to reflect any user-facing or architectural changes introduced by this change
