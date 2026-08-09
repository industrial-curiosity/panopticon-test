# Four-gate rollout process delta

## ADDED Requirements

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
