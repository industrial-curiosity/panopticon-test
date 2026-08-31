# Failure-Path Diagnostics Spec

## Purpose

Define the testing contract for intentional failures and keep expected
diagnostics actionable without polluting successful CI results.

## Requirements

### Requirement: Failure-path tests verify the failure signal

The template repository's intentional failure-path tests SHALL capture and
assert the failure signal they claim to test. The signal may be an expected
exception, a non-success exit status, user-facing output, or a generated
failure report. If the expected signal is absent or does not identify the
failure clearly enough to act on, the test SHALL fail.

#### Scenario: A direct operation raises an expected exception

- **WHEN** a test invokes an operation that is required to reject invalid input
- **THEN** the test passes only when the expected exception type is raised and
  its diagnostic identifies the invalid condition

#### Scenario: A CLI check reports an operational failure

- **WHEN** a test invokes a CLI check whose dependency or configuration fails
- **THEN** the test asserts an exit status outside the check's business-result
  statuses and captures output containing the check name and failure cause

#### Scenario: A CLI check writes a failure report

- **WHEN** a test invokes a CLI check with a report destination during an
  operational failure
- **THEN** the test asserts that the report exists and contains an actionable
  failure description

### Requirement: Expected failure diagnostics do not pollute successful CI

Tests that intentionally exercise GitHub workflow-command diagnostics SHALL
capture those commands inside the test process. A passing test suite SHALL
exit successfully without publishing expected failure diagnostics as workflow
annotations, while a real assertion failure SHALL still fail the suite.

#### Scenario: Expected CLI diagnostics are captured

- **WHEN** a passing test executes a CLI failure path that emits a GitHub
  workflow command
- **THEN** the test verifies the captured command and the command is not
  emitted to the surrounding CI process

#### Scenario: An assertion is removed from a failure-path test

- **WHEN** the expected failure status or diagnostic no longer matches the
  operation's result
- **THEN** the test suite fails instead of silently passing with suppressed
  output

### Requirement: Panopticon failure paths have regression coverage

The template repository SHALL apply the failure-signal contract to the
doc-drift, index-currency, diagram-existence, interface-merge, and
dependency-merge operational failure paths.

#### Scenario: A covered check changes its failure diagnostic

- **WHEN** one of the covered checks stops emitting its check-specific
  operational failure diagnostic
- **THEN** its regression test fails and identifies the missing diagnostic
