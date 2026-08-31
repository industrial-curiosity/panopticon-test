# LLM provider configuration delta

## MODIFIED Requirements

### Requirement: Provider workflows resolve effective configuration before preflight

Each provider-specific reusable PR workflow SHALL resolve optional non-secret
provider inputs through the validated contract before provider preflight and
LLM work. It SHALL preserve raw caller inputs until resolution and SHALL expose
only source labels in diagnostics. The workflow SHALL receive
`job_timeout_minutes` as the organization variable expression from the caller;
its job-level timeout SHALL apply the reusable-workflow fallback before any
step runs. It SHALL NOT obtain that value from the fixed instance action or an
instance-configured caller default. The configuration-action summary SHALL
describe the fixed Action, instance-default, and workflow-default sources as
applying to optional request-budget variables, and SHALL separately state that
job timeout uses only the organization variable or reusable-workflow fallback.
Generated organization profiles SHALL resolve through this same validated
contract and SHALL not introduce a second default or provider-resolution path.
Generated `panopticon.config.json` content SHALL contain only accepted
instance-configuration fields. Computed provider and caller revisions SHALL be
reported in generated review metadata rather than persisted in instance
provider configuration.

#### Scenario: Timeout fallback changes without caller regeneration

- **GIVEN** an existing child caller passes only the organization timeout
  variable expression
- **WHEN** the reusable workflow's fallback changes
- **THEN** the child caller remains compatible and uses the new fallback on its
  next run without re-bootstrap

#### Scenario: Configuration summary distinguishes timeout ownership

- **WHEN** the provider configuration action summarizes optional variables
- **THEN** it describes request-budget source precedence separately from
  `job_timeout_minutes` and identifies the reusable workflow as the timeout
  fallback owner

#### Scenario: Generated profile uses the trusted default source

- **WHEN** a generated profile declares an effective optional value and its
  default source
- **THEN** configuration validation resolves that value through the existing
  provider contract before preflight and rejects an absent promised default

#### Scenario: Generated configuration does not persist computed revisions

- **WHEN** a generated profile resolves a provider contract
- **THEN** its review manifest reports the computed revisions while its
  `panopticon.config.json` remains valid for the existing configuration loader
