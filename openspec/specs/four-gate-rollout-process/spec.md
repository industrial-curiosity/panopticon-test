# four-gate-rollout-process Specification

## Purpose

Define the supported four-gate operating process for reusable-workflow access,
effective provider configuration, caller identity and credentials, and real
provider-request compatibility.

## Requirements

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
  or getting-started guide without reading implementation source

#### Scenario: Gate evidence is separated by owner

- **WHEN** a failure could be caused by workflow access, configuration, caller
  identity, credentials, or provider request shape
- **THEN** the guide names the authoritative evidence and whether the repair is
  instance-wide or specific to the child repository

#### Scenario: Generated guidance separates ownership

- **WHEN** an organization generates onboarding guidance for a new child
- **THEN** instance-wide workflow access and provider configuration are shown
  separately from child-specific caller identity and credential provisioning,
  with proof required at each boundary

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

### Requirement: Gate-1 recovery includes a safe policy mutation command

Public rollout guidance SHALL provide the exact placeholder-safe command
`gh api -X PUT repos/YOUR-ORG/YOUR-INSTANCE-REPO/actions/permissions/access -f access_level=organization`, identify it as a reusable-workflow access-policy mutation requiring administrator permission, and retain the read-only API check and Settings UI alternative.

#### Scenario: Administrator repairs denied organization access

- **WHEN** the access preflight reports that organization callers are not
  allowed
- **THEN** the guide provides the mutation command and explains its scope and
  required administrator permission

### Requirement: Bedrock inference-profile IAM guidance covers both resources

Public Bedrock guidance SHALL state that application inference-profile requests
need `bedrock:InvokeModel` on both the selected profile ARN and its underlying
foundation-model ARN, while `bedrock:GetInferenceProfile` remains a separate
metadata/discovery permission. Examples SHALL use placeholder or synthetic ARNs.

#### Scenario: IAM policy grants an application inference profile

- **WHEN** an organization configures a Bedrock application inference profile
- **THEN** the guide directs the owner to grant `bedrock:InvokeModel` on the
  profile ARN and the underlying foundation-model ARN

#### Scenario: Operator diagnoses a profile permission failure

- **WHEN** the profile can be discovered but invocation is denied
- **THEN** the guide distinguishes `GetInferenceProfile` from invocation and
  directs the owner to inspect both `InvokeModel` resource entries

### Requirement: Gate-1 recovery includes an executable access-policy mutation

Public rollout guidance SHALL provide the exact GitHub CLI mutation command for
an instance administrator to allow organization callers:
`gh api -X PUT repos/YOUR-ORG/YOUR-INSTANCE-REPO/actions/permissions/access -f access_level=organization`.
The guidance SHALL identify the command as a policy mutation, state the
required administrator permissions, and retain a read-only check and UI
alternative.

#### Scenario: Instance owner repairs denied reusable-workflow access

- **WHEN** the access preflight reports that organization callers are not
  allowed
- **THEN** the guide provides the placeholder-safe `gh api -X PUT` command,
  explains that it changes the instance access policy, and identifies the
  required administrator token permissions

#### Scenario: Administrator verifies the policy without mutating it

- **WHEN** an operator only has read access or chooses not to change policy
- **THEN** the guide provides the read-only API check and Settings UI path and
  does not present the mutation as a required automated step

### Requirement: Bedrock inference-profile permissions cover both resources

Bedrock rollout guidance SHALL state that an application inference-profile
request requires `bedrock:InvokeModel` on both the selected inference-profile
ARN and the underlying foundation-model ARN. It SHALL distinguish that
requirement from `bedrock:GetInferenceProfile` metadata/discovery access and
use placeholder or synthetic ARNs in public examples.

#### Scenario: IAM policy grants an application inference profile

- **WHEN** an organization configures a Bedrock application inference profile
- **THEN** the setup guide directs the owner to grant `bedrock:InvokeModel` on
  the profile ARN and the underlying foundation-model ARN

#### Scenario: Operator diagnoses a profile permission failure

- **WHEN** the profile can be discovered but invocation is denied
- **THEN** the guide distinguishes `GetInferenceProfile` from invocation and
  directs the owner to inspect both `InvokeModel` resource entries

### Requirement: Getting-started guidance links to the authoritative rollout guide

The public `PANOPTICON.md` getting-started guide SHALL direct readers to
`docs/setup-guide.md` as the authoritative source for the four-gate rollout and
troubleshooting process, rather than duplicating that process in a second
document.

#### Scenario: A child maintainer starts from the getting-started guide

- **WHEN** a reader follows the public getting-started guide for onboarding
- **THEN** the guide contains a link to `docs/setup-guide.md` for the complete
  four-gate setup and recovery instructions
