# Four-gate rollout process delta

## MODIFIED Requirements

### Requirement: Four-gate operating sequence is explicit

Public setup and getting-started guidance SHALL define an ordered sequence of
four gates: reusable-workflow access, effective provider configuration,
caller-repository identity and credentials, and real provider-request
compatibility. For each gate it SHALL state the observable symptom,
authoritative evidence, ownership boundary, exact recovery action, and proof
required to advance. Generated instance and child onboarding guides SHALL
preserve this sequence and SHALL distinguish instance-wide access/configuration
from per-child identity provisioning.

#### Scenario: Maintainer locates the last proven gate

- **WHEN** a child run fails during onboarding or a pull request
- **THEN** the maintainer can identify the last successful gate from the setup
  or generated onboarding guide without reading implementation source

#### Scenario: Generated guidance separates ownership

- **WHEN** an organization generates onboarding guidance for a new child
- **THEN** instance-wide workflow access and provider configuration are shown
  separately from child-specific caller identity and credential provisioning,
  with proof required at each boundary
