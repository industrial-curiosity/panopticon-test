# Tooling currency delta

## MODIFIED Requirements

### Requirement: Template sync automatically protects the fixed instance-managed credential action

The shared template-sync workflow SHALL derive
`.github/actions/panopticon-aws-credentials/action.yml` as a protected path
when the loaded instance configuration selects provider `bedrock` with
credential mode `instance-managed`. It SHALL write the derived path to the
runtime merge attributes using the existing `merge.ours` driver, report it
separately from organization-declared `protected_paths`, and apply the same
derivation in local recovery instructions. No configuration field SHALL be
able to replace the fixed path. Generated overlays SHALL emit compatible
protection metadata that classifies paths as template-generated,
provider-derived, or organization-declared. Only organization-declared
protected customizations SHALL require protected-path debt records.

#### Scenario: Instance-managed action survives routine template sync

- **GIVEN** an instance contract selects Bedrock `instance-managed` credentials
  and the incoming template changes the fixed action path
- **WHEN** shared template sync runs
- **THEN** the instance action remains unchanged, the merge completes, and the
  summary identifies the provider-derived protected path

#### Scenario: Generated protection is visible to review

- **GIVEN** a generated overlay contains an organization-declared protected path
- **WHEN** tooling-currency validation examines the overlay
- **THEN** it reports the path, ownership reason, and debt-removal condition
  separately from template-generated and provider-derived paths

#### Scenario: Provider-derived wrapper is not organization debt

- **GIVEN** a generated overlay selects Bedrock `instance-managed` credentials
- **WHEN** tooling-currency validation examines its protection metadata
- **THEN** it reports the fixed credential wrapper as provider-derived without
  requiring organization-debt ownership or removal fields

#### Scenario: Other provider modes do not protect the Bedrock action

- **GIVEN** the instance is unconfigured, uses another provider, or uses
  Bedrock `github-oidc`
- **WHEN** shared template sync registers protected paths
- **THEN** it does not add the Bedrock credential-action path unless the
  organization explicitly lists it in `protected_paths`

#### Scenario: Non-object configuration remains syncable

- **GIVEN** the protected-path derivation helper receives a non-object
  configuration value
- **WHEN** it derives runtime merge-protected paths
- **THEN** it returns only template-declared generated paths and does not raise
  an attribute error

#### Scenario: Local recovery matches hosted sync protection

- **GIVEN** hosted template sync fails before merging
- **WHEN** an owner follows the generated local recovery commands
- **THEN** the same provider-derived credential-action path is protected before
  the local merge
