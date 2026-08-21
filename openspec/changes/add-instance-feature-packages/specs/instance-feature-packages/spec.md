# Instance feature packages

## ADDED Requirements

### Requirement: Template-owned feature registry
The template SHALL publish a versioned feature registry under `features/` that
defines every supported feature ID, supported mode, package-relative source
file, and child destination. The registry SHALL reject unknown feature IDs,
unsupported modes, duplicate destinations, destinations outside feature-managed
namespaces, core-resource collisions, and arbitrary instance-supplied artifact
paths. Instance configuration SHALL select only a registered feature mode.

#### Scenario: Instance enables a registered feature

- **WHEN** an instance configuration sets a registered feature to a supported
  non-disabled mode
- **THEN** bootstrap and shared workflows select only the artifacts and checks
  defined by that feature's template-owned registry entry

#### Scenario: Configuration names an unknown feature

- **WHEN** feature configuration receives a feature ID absent from the registry
- **THEN** it fails before changing `panopticon.config.json` and names the
  unsupported feature ID

### Requirement: Generic feature configuration workflow
The template SHALL provide `Configure Panopticon — Features` as a manual GitHub
Actions workflow with generic `feature` and `mode` inputs. It SHALL validate the
pair against the registry, update only the selected feature's mode in
`panopticon.config.json`, preserve unrelated configuration and feature entries,
and commit the validated change to the selected instance branch. When a newer
workflow is rerun without an explicit modification, it SHALL use the instance's
existing effective feature configuration as the displayed defaults rather than
resetting feature selections.

#### Scenario: Maintainer enables OKF advisory mode

- **WHEN** a maintainer runs the feature workflow with `feature=okf` and
  `mode=advisory`
- **THEN** the instance configuration records only `features.okf.mode` as
  advisory and preserves the configured provider and all other feature modes

#### Scenario: Maintainer reruns feature configuration unchanged

- **WHEN** the feature workflow runs against an instance with an existing OKF
  mode and the maintainer does not select a different mode
- **THEN** it preserves that existing mode

### Requirement: Feature artifact receipt and cleanup
Bootstrap and local sync SHALL create a managed child feature receipt containing
the selected feature modes, registry revision, and exact installed
feature-owned child paths. They SHALL fetch and validate every desired feature
artifact before writing any of them. A path retired by a disabled feature SHALL
be eligible for deletion only when it is listed in a valid receipt and belongs
to a registered feature-managed namespace; ordinary managed resources and
unrecognized child files SHALL NOT be deleted.

#### Scenario: Interactive bootstrap disables a feature

- **GIVEN** the child receipt records OKF artifacts and the instance now sets
  OKF to disabled
- **WHEN** bootstrap runs with a controlling terminal
- **THEN** it lists the disabled feature and exact retired paths and prompts
  `Delete these files? [Y/n]`

#### Scenario: User declines interactive cleanup

- **GIVEN** bootstrap offers cleanup for a disabled feature
- **WHEN** the user answers `n`
- **THEN** it leaves the retired artifacts and receipt entries in place, marks
  cleanup pending, and does not select the feature for generation or workflows

#### Scenario: Noninteractive cleanup runs

- **GIVEN** the child receipt records OKF artifacts and the instance disables
  OKF
- **WHEN** bootstrap has no controlling terminal or `panopticon.sync` runs
- **THEN** it deletes every valid receipt-owned retired path without prompting,
  reports every deleted path, and does not stage, commit, or push the deletion

#### Scenario: Malformed receipt cannot expand deletion scope

- **WHEN** a feature receipt contains an invalid or unregistered destination
- **THEN** bootstrap and sync fail before deleting any feature artifact and name
  the invalid receipt entry

### Requirement: Feature mode semantics
Every registered feature SHALL support `disabled`, `advisory`, and `blocking`
modes. Disabled SHALL omit feature artifact selection and skip feature checks.
Advisory SHALL run feature checks and report findings without failing the
operation. Blocking SHALL run the same checks and fail the applicable
initialization or shared-workflow gate on a finding. Feature checks SHALL use
fixed internal dispatch or environment state and SHALL NOT add caller inputs,
secrets, or arbitrary workflow selection.

#### Scenario: Disabled feature has no child artifacts

- **WHEN** an instance keeps OKF disabled
- **THEN** a newly bootstrapped child receives no OKF skill, template, or helper
  artifact

#### Scenario: Advisory feature reports without blocking

- **WHEN** an OKF conformance check finds a violation in advisory mode
- **THEN** it records the finding and the containing initialization or PR
  workflow remains successful because of that finding

