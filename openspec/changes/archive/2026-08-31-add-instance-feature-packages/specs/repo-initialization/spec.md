# Repository initialization delta

## ADDED Requirements

### Requirement: Bootstrap installs effective feature artifacts

Bootstrap SHALL resolve the effective feature registry and modes after reading
valid instance configuration and before writing managed child resources. It
SHALL install only artifacts for enabled features, write the feature receipt,
and make the effective feature modes available to local initialization tooling.
The receipt and feature artifacts SHALL be staged and validated before any
feature artifact is written. Bootstrap SHALL preserve the rule that
`panopticon/config.json` is written only by successful finalization.

#### Scenario: Bootstrap installs enabled OKF artifacts

- **WHEN** bootstrap reads an instance configuration with OKF advisory or
  blocking mode
- **THEN** it installs the registry-declared OKF artifacts, records them in the
  child receipt, and does not create `panopticon/config.json`

#### Scenario: Bootstrap receives invalid feature configuration

- **WHEN** bootstrap cannot validate the effective feature configuration or
  registry
- **THEN** it exits before writing feature artifacts and names the invalid
  configuration or registry condition

### Requirement: Initialization honors feature mode

Initialization finalization SHALL obtain effective feature mode from managed
bootstrap state. It SHALL run feature validation only when the feature is
enabled, report advisory findings without withholding the initialization flag,
and withhold `panopticon/config.json` for blocking findings.

#### Scenario: Advisory OKF finding permits finalization

- **WHEN** local initialization finds an OKF violation while the effective mode
  is advisory
- **THEN** it reports the violation and may write `panopticon/config.json` when
  all blocking initialization requirements pass
