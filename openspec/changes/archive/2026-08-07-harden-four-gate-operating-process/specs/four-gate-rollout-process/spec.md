# Four-gate rollout process

## ADDED Requirements

### Requirement: Four-gate operating sequence is explicit

Public setup and getting-started guidance SHALL define an ordered sequence of
four gates: reusable-workflow access, effective provider configuration,
caller-repository identity and credentials, and real provider-request
compatibility. For each gate it SHALL state the observable symptom,
authoritative evidence, ownership boundary, exact recovery action, and proof
required to advance.

#### Scenario: Maintainer locates the last proven gate

- **WHEN** a child run fails during onboarding or a pull request
- **THEN** the maintainer can identify the last successful gate from the setup
  or getting-started guide without reading implementation source

#### Scenario: Gate evidence is separated by owner

- **WHEN** a failure could be caused by workflow access, configuration, caller
  identity, credentials, or provider request shape
- **THEN** the guide names the authoritative evidence and whether the repair is
  instance-wide or specific to the child repository

### Requirement: Private workflow access has a pre-child check

Before a child is bootstrapped against a private or internal instance, the operating process SHALL provide the GitHub Settings → Actions → General → Access URL shape and a deterministic API check for the instance reusable-workflow access policy. The check SHALL inspect access policy before treating a zero-job "workflow was not found" message as missing YAML.

#### Scenario: Access policy denies the child

- **WHEN** the instance Actions access endpoint reports `none` or does not
  include the child organization
- **THEN** the process identifies the instance owner as responsible, gives the
  access-policy UI/API recovery action, and does not direct the maintainer to
  edit the called workflow first

#### Scenario: Access policy allows the child

- **WHEN** the access endpoint allows organization or enterprise callers
- **THEN** the process checks the selected workflow path at the configured ref
  and advances to effective provider configuration only after that content check
  succeeds

### Requirement: Caller identity ownership is documented

The operating process SHALL explain that code from a reusable workflow does not
transfer repository identity. For GitHub OIDC, the subject identifies the
caller repository, and an organization MAY need to provision identity and
credential trust for every child repository independently.

#### Scenario: Child calls an instance workflow

- **WHEN** a child repository invokes an instance-owned Bedrock reusable
  workflow
- **THEN** the guide says the OIDC subject and credential trust are evaluated
  for the child caller, not the repository that stores the reusable workflow,
  and names per-child provisioning as the recovery

### Requirement: Protected-path maintenance debt is reviewable

The setup guide SHALL provide a protected-path debt register with columns for
the exact path, reason, owner, upstream issue or change replacing the
customization, last reconciliation result, and removal condition.

#### Scenario: Protected path is retained temporarily

- **WHEN** an instance protects a template-owned path to keep a necessary
  customization
- **THEN** the register records why it is protected, who owns the follow-up,
  what upstream work replaces it, the latest reconciliation result, and the
  condition for removing the entry

### Requirement: Public rollout guidance contains no organization secrets

The public template's setup, getting-started, testing, and recovery guidance MUST use placeholders or synthetic examples for organization-specific links, account identifiers, role names, model identifiers, and credential values.

#### Scenario: Public docs are inspected for sensitive rollout values

- **WHEN** the documentation and recovery fixtures are checked in the template
  repository
- **THEN** they contain no organization-specific identifiers or credential
  values and still provide actionable placeholder UI/API shapes
