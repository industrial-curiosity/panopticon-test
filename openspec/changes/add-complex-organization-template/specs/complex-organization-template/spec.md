# Complex-organization instance template

## ADDED Requirements

### Requirement: Organization profiles expose a minimal non-secret authoring contract

The template SHALL define a versioned JSON organization-profile schema whose
required fields are limited to organization-owned choices that cannot be
derived from the trusted provider registry. Provider workflow paths, the fixed
credential-wrapper path, provider permissions, logical mappings, default
Actions names, and provider contract revisions SHALL be derived rather than
entered by the profile author. Gating overrides, internal registries,
workflow-access customization, and organization-declared protected-path debt
SHALL be optional advanced sections with documented defaults. Profile fields
SHALL contain names, references, or non-secret setup choices only.

#### Scenario: Minimal direct OIDC profile validates

- **WHEN** a profile selects Bedrock direct GitHub OIDC and supplies only the
  required organization-owned role and child-provisioning choices
- **THEN** validation succeeds and derives the trusted workflow, fixed paths,
  provider mappings, defaults, and revisions

#### Scenario: Advanced sections are omitted

- **WHEN** a valid profile omits gating overrides, internal registries,
  workflow-access customization, and protected-path debt
- **THEN** generation uses the documented safe defaults without prompting for
  those sections

### Requirement: Instance-managed profiles use a bounded broker reference

An instance-managed profile SHALL accept an organization broker action
reference only as an implementation input to the fixed template-owned
`.github/actions/panopticon-aws-credentials/action.yml` wrapper. The reference
SHALL use GitHub Action `owner/repository[/path]@revision` syntax with a branch,
tag, or full commit SHA revision. It SHALL NOT replace the fixed wrapper path,
select a reusable workflow, add a child step, or supply credential values. The
profile SHALL declare the non-secret region output name produced by the broker
action. The generated wrapper SHALL preserve the exact validated reference for
review.

#### Scenario: Branch, tag, and commit broker references validate

- **WHEN** a Bedrock `instance-managed` profile supplies a syntactically valid
  broker action reference using a branch, tag, or full commit SHA and a valid
  region output name
- **THEN** generation renders the exact reference inside the fixed credential
  wrapper and keeps the provider workflow and wrapper path template-owned

#### Scenario: Invalid broker reference is rejected

- **WHEN** the broker action reference omits a revision or uses an unresolved
  placeholder, expression, or invalid GitHub Action reference syntax
- **THEN** validation fails with the field path before rendering or writing any
  output

#### Scenario: Broker reference cannot inject runtime structure

- **WHEN** a profile attempts to use the broker field to replace the wrapper
  path, select a workflow, add an action step, or provide action inputs outside
  the schema
- **THEN** validation rejects the profile before rendering or writing any
  output

### Requirement: Public synthetic profiles are concrete and executable

The direct-OIDC and instance-managed public synthetic profiles SHALL use
concrete reserved example values, including reserved domains and synthetic
identifiers, rather than unresolved placeholders. Both profiles SHALL pass the
same validator and generator used for private profiles and SHALL contain no
real organization-specific identifier, private URL, model identifier, role
identifier, or credential value. Synthetic reserved identifiers SHALL be
allowed.

#### Scenario: Public examples generate valid overlays

- **WHEN** the public synthetic profiles are validated and generated
- **THEN** both operations succeed without placeholder exemptions or
  organization-sensitive values

#### Scenario: Unresolved placeholder is rejected uniformly

- **WHEN** any public or private profile contains an unresolved placeholder
- **THEN** validation fails with the field path and writes no overlay

### Requirement: Generation is deterministic and review-first

The template SHALL provide
`python3 -m panopticon.organization_template validate PROFILE` and
`python3 -m panopticon.organization_template generate PROFILE --instance-root INSTANCE --output OVERLAY`.
Generation SHALL validate the complete profile, render all files in memory, and
write a deterministic overlay only to an absent or empty output directory.
Re-running generation with the same profile, generator version, and instance
preimage SHALL produce byte-for-byte identical files. The overlay manifest
SHALL list every destination path, content digest, destination preimage digest
or absence, ownership class, protection reason, and computed provider and
caller revisions. The revisions SHALL NOT be persisted as fields in
`panopticon.config.json`.

#### Scenario: Repeated generation is idempotent

- **WHEN** the same valid profile is generated twice against equivalent
  instance preimages
- **THEN** every generated file and manifest entry has identical bytes and
  stable ordering

#### Scenario: Invalid profile cannot create a partial overlay

- **WHEN** generation fails during schema, contract, default, broker-reference,
  rendering, or secret-safety validation
- **THEN** the output directory contains no partial generated overlay

#### Scenario: Contract revisions are review metadata

- **WHEN** generation resolves the trusted provider contract
- **THEN** the manifest reports the computed provider and caller revisions and
  `panopticon.config.json` contains only accepted instance-configuration fields

### Requirement: Overlay application is bounded and preflighted

The template SHALL provide
`python3 -m panopticon.organization_template apply OVERLAY --instance-root INSTANCE --check`
as a read-only preview and the same command without `--check` as the explicit
write operation. Both forms SHALL validate the manifest and compare every
recorded destination preimage before any write. A mismatch or undeclared
destination collision SHALL fail before writing. Apply SHALL write only
manifest-declared files, SHALL NOT replace the instance directory, and SHALL
NOT delete or modify unrelated files. A validation failure SHALL leave the
instance unchanged.

#### Scenario: Apply preview writes nothing

- **WHEN** an operator runs apply with `--check`
- **THEN** it reports every create, update, protected-path classification, and
  collision without changing the instance

#### Scenario: Instance changed after generation

- **GIVEN** a manifest-recorded destination changed after the overlay was
  generated
- **WHEN** apply runs
- **THEN** preflight names the stale destination and exits before writing any
  overlay file

#### Scenario: Unrelated instance content survives apply

- **WHEN** a validated overlay is applied to an unchanged instance preimage
- **THEN** only manifest-declared destination files change and all unrelated
  files remain byte-for-byte unchanged

### Requirement: Generated output uses closed runtime trust

Generated configuration SHALL load through the existing trusted provider
contract. Generated child callers SHALL contain explicit trusted mappings and
SHALL NOT use `secrets: inherit`. Except for the bounded broker reference used
inside the fixed instance-managed wrapper, a profile SHALL NOT select an
action, workflow, wrapper path, child workflow step, provider runtime, or
provider mapping.

#### Scenario: Generated caller uses explicit mappings

- **WHEN** a valid profile generates an instance overlay and a child caller is
  rendered from its provider contract
- **THEN** the caller references the registered provider workflow and maps
  configured names explicitly without profile-supplied runtime structure

#### Scenario: Arbitrary workflow injection is rejected

- **WHEN** a profile attempts to provide a reusable workflow path, fixed
  credential-wrapper path, child workflow fragment, or provider mapping
- **THEN** generation fails before writing the overlay

### Requirement: Generated onboarding separates four-gate ownership

The generator SHALL produce an executable instance checklist and a child
onboarding checklist ordered by reusable-workflow access, effective provider
configuration, caller identity and credentials, and real provider-request
compatibility. Each checklist SHALL identify observable symptoms,
authoritative evidence, ownership scope, exact recovery action, and proof to
advance. Instance-wide access and configuration guidance SHALL be separate from
per-child identity provisioning guidance. Reference material SHALL follow the
executable checklist.

#### Scenario: Child onboarding identifies per-child identity ownership

- **WHEN** a generated child checklist is reviewed for a new repository
- **THEN** it identifies the child repository as the caller/OIDC subject and
  names the organization-specific provisioning evidence required before
  provider preflight

#### Scenario: Operator starts with the happy path

- **WHEN** an operator opens a generated onboarding guide
- **THEN** the copy-and-paste checklist appears before schema details, field
  references, and troubleshooting background

### Requirement: Protection metadata distinguishes ownership from debt

The generator SHALL classify protected paths as template-generated,
provider-derived, or organization-declared and SHALL expose each path's source
and reason in the overlay manifest. Selecting Bedrock `instance-managed` mode
SHALL automatically classify the fixed credential wrapper as provider-derived
protection without requiring a profile entry or debt record. Every
organization-declared protected customization SHALL have a debt record with an
owner, reason, upstream replacement reference, last reconciliation result, and
removal condition.

#### Scenario: Instance-managed wrapper is protected without debt fields

- **WHEN** a valid profile selects Bedrock `instance-managed` mode
- **THEN** the manifest classifies the fixed wrapper as provider-derived and no
  owner, upstream replacement, reconciliation result, or removal condition is
  required for that wrapper

#### Scenario: Organization customization has complete debt metadata

- **WHEN** a profile declares an organization-protected customization
- **THEN** validation requires and the generated debt register contains its
  path, reason, owner, upstream replacement reference, last reconciliation
  result, and removal condition

#### Scenario: Organization debt is incomplete

- **WHEN** an organization-declared protected customization omits any required
  debt field
- **THEN** validation fails and identifies the missing field before writing an
  overlay
