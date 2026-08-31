# Instance Feature Packages Spec Delta

## ADDED Requirements

### Requirement: Enabled feature packages load through public bootstrap

An enabled template feature package SHALL be loadable through the public
installer's default-payload path before bootstrap evaluates feature-dependent
logic. The default payload loader SHALL make the feature registry and its
relative dependencies available without requiring a child checkout or a
pre-existing `panopticon` module in the process.

#### Scenario: OKF-enabled instance reaches feature installation

- **GIVEN** an instance configuration enables OKF in advisory or blocking mode
- **WHEN** a child runs the public installer against that instance
- **THEN** the default bootstrap loads the feature registry successfully and
  proceeds to validate and stage the registry-declared OKF artifacts

#### Scenario: Feature dependency is missing from the loader

- **GIVEN** an enabled feature requires a default-bootstrap module that the
  public loader does not register
- **WHEN** the public installer loads the default payload
- **THEN** it fails with a diagnostic naming the missing module rather than
  reporting a misleading feature-configuration or artifact error
