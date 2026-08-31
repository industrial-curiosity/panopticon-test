# Instance Feature Packages Spec Delta

## MODIFIED Requirements

### Requirement: Feature mode semantics

Every registered feature SHALL support `disabled`, `advisory`, and `blocking`
modes. Disabled SHALL omit feature artifact selection and skip feature checks.
Advisory SHALL run feature checks and report findings without failing the
initialization or shared PR gate. Advisory findings SHALL remain mandatory
agent remediation: an agent that invokes a feature-aware workflow SHALL follow
the installed feature skill, repair deterministic findings, and revalidate
before declaring that workflow complete. Blocking SHALL run the same checks and
fail the applicable initialization or shared-workflow gate on a finding.
Feature checks SHALL use fixed internal dispatch or environment state and SHALL
NOT add caller inputs, secrets, or arbitrary workflow selection.

#### Scenario: Disabled feature has no child artifacts

- **WHEN** an instance keeps OKF disabled
- **THEN** a newly bootstrapped child receives no OKF skill, template, or helper
  artifact

#### Scenario: Advisory feature reports without blocking

- **WHEN** an OKF conformance check finds a violation in advisory mode
- **THEN** it records the finding and the containing initialization or PR
  workflow remains successful because of that finding

#### Scenario: Agent receives an advisory feature finding

- **GIVEN** a feature-aware agent workflow finds an OKF advisory violation
- **WHEN** it evaluates the enabled feature package
- **THEN** it treats the installed OKF skill's remediation as required work and
  reruns the validator before reporting its workflow complete
