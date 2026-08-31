# Workflow Purpose Summaries Spec

## Purpose

Define the required purpose preambles for executable Panopticon workflow jobs
and their regression coverage.

## Requirements

### Requirement: Executing workflow jobs begin their summaries with purpose

Every Panopticon GitHub Actions job that contains executable steps SHALL append
to `GITHUB_STEP_SUMMARY` before any other summary content. Its first summary
section SHALL have a stable heading and a brief, non-sensitive sentence that
states the action the job is attempting to perform. A caller-only job that
delegates with `uses:` has no steps; its invoked reusable job owns this summary
requirement.

#### Scenario: A provider PR-evaluation job starts

- **WHEN** a provider-specific PR-evaluation job starts
- **THEN** its summary begins with a brief statement that it is evaluating the
  child pull request against the configured Panopticon instance before any gate
  or failure details

#### Scenario: A sync or configuration job starts

- **WHEN** a Panopticon sync or provider-configuration job starts
- **THEN** its summary begins with a brief statement of the synchronization or
  configuration action before any operational details

### Requirement: Purpose preambles preserve existing diagnostics

Adding a purpose preamble SHALL not remove, reorder after failure output, or
expose secrets through existing success, failure, or recovery summaries.

#### Scenario: A job later fails

- **WHEN** an executing job writes a failure or recovery summary
- **THEN** the purpose preamble remains first and the existing actionable
  failure and recovery information follows it without credential values

### Requirement: Purpose-summary coverage is regression-tested

The template repository SHALL include deterministic tests that inventory
shipped step-bearing workflow jobs and verify their required purpose
preambles.

#### Scenario: A shipped job lacks a preamble

- **WHEN** a step-bearing Panopticon workflow job lacks the required first
  summary preamble
- **THEN** the deterministic workflow tests fail
