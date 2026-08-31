# Template validation scope

## ADDED Requirements

### Requirement: Template validation is scoped to the canonical repository

The template validation workflow SHALL create its validation job only when
`github.repository` exactly identifies the canonical Panopticon template
repository. It SHALL not check out code, validate workflow contracts, or run
template tests when the workflow file exists in a configured instance repository.

#### Scenario: Canonical template push runs validation

- **WHEN** a push, pull request, or manual dispatch runs the workflow in the
  canonical template repository
- **THEN** GitHub Actions creates the validation job and runs its contract check
  and Python test suite

#### Scenario: Configured instance retains the workflow

- **WHEN** a configured instance repository contains the template validation
  workflow and receives a push, pull request, or manual dispatch
- **THEN** GitHub Actions skips the validation job without running checkout,
  workflow-contract validation, or template tests

### Requirement: Template-validation scope is regression-tested

The template repository SHALL include deterministic tests that verify the
canonical-repository guard and the guarded placement of the template test suite.

#### Scenario: Guard is removed or weakened

- **WHEN** the template-validation job no longer uses the exact canonical
  repository guard
- **THEN** the deterministic workflow tests fail
