# Assert failure-path diagnostics design

## Context

Panopticon's deterministic checks intentionally test operational failures as
well as clean and business-verdict outcomes. Several CLI entry points emit
GitHub workflow commands for operational failures; allowing those commands to
escape unit tests creates misleading annotations even when the test suite
passes.

## Goals / Non-Goals

**Goals:**

- Preserve the existing check exit-code and reporting contracts.
- Capture expected CLI output inside tests and assert the diagnostic that the
  user would receive.
- Keep successful template-validation runs free of false GitHub annotations.
- Apply the rule consistently to validation and merge-check failure paths.

**Non-Goals:**

- Change production error handling, exit codes, or report formats.
- Suppress diagnostics from an actual failing test run.
- Add a new test framework or external dependency.

## Decisions

### Retain captured output in CLI test helpers

Each helper that invokes a CLI `main()` function will redirect stdout to an
in-memory buffer, return the exit code, and retain the captured text for the
test assertions. This prevents GitHub workflow commands from reaching the
runner while keeping the user-facing result testable.

### Assert the complete failure contract

Failure-path tests will assert the non-business exit status and the relevant
diagnostic content. Tests that exercise a report file will continue asserting
the report as well. Direct exception tests will continue using explicit
exception assertions. A test must fail if the expected failure signal or
actionable diagnostic disappears.

### Keep production behavior unchanged

The implementation is test-harness-only. Existing `::error::` output remains
available to real CI invocations, where it is needed for operational failures;
only expected output generated during unit tests is captured.

## Risks / Trade-offs

- [A helper captures output but forgets to assert it] → Store the captured text
  on the test fixture and require failure-path tests to assert the relevant
  check and cause.
- [A real test failure becomes hidden] → Redirect only the expected CLI call;
  unittest assertion failures still propagate and the suite retains a
  nonzero exit status.
- [A diagnostic becomes vague] → Assert check-specific, cause-bearing text
  rather than only checking that output is non-empty.

## Migration Plan

1. Update existing failure-path CLI helpers and assertions.
2. Run focused failure-path tests and the complete Python suite.
3. Keep the testing guidance synchronized with the invariant for future
   failure-path tests.

## Open Questions

None.
