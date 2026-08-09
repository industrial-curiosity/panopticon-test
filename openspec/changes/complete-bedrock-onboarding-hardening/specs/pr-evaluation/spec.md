# PR evaluation delta

## ADDED Requirements

### Requirement: Missing instance-managed credential recovery is copyable

The Bedrock provider workflow SHALL, when `instance-managed` credential
validation finds that the fixed action is absent, identify the exact
action path, link to the public example skeleton, provide a copyable
`protected_paths` configuration fragment, and state the child-bootstrap rerun
command. The recovery SHALL preserve the instance-owned action boundary and
MUST NOT request or print credential values.

#### Scenario: Fixed action is missing from a configured instance

- **WHEN** a Bedrock `instance-managed` run cannot find
  `.github/actions/panopticon-aws-credentials/action.yml`
- **THEN** the step summary links to the public example, shows the exact path
  to copy, includes the matching `protected_paths` fragment, and gives the
  child-bootstrap command

#### Scenario: Formatter import is unavailable

- **WHEN** the caller-side failure reporter runs before the child can import
  the shared recovery formatter
- **THEN** its inline fallback contains the same example link, protection
  fragment, fixed path, and rerun guidance without exposing credentials

### Requirement: Credential-action recovery distinguishes automatic protection

Bedrock gate-3 recovery SHALL state that a valid `instance-managed` provider
contract automatically protects the fixed credential-action path during
template sync, while `protected_paths` remains available for other custom
instance files.

#### Scenario: Instance owner reviews recovery after a template sync

- **WHEN** a missing-action recovery is shown for a valid
  `instance-managed` contract
- **THEN** it tells the owner that adding the fixed action does not require a
  manual protection entry for that path and identifies the remaining rerun
  steps

## MODIFIED Requirements

### Requirement: Bounded PR-evaluation job duration

Each provider-specific reusable PR-evaluation workflow SHALL set an explicit
timeout for its evaluate job from the canonical workflow input mapped by child
bootstrap from the configured organization-level job-timeout variable name,
using 20 minutes when the mapped value is unset. The setup guide SHALL
document that the value accepts a whole number from 10 through 60 and is
evaluated by GitHub Actions before the job starts. Instance configuration and
the fixed instance default-resolver action SHALL NOT supply this job-level
value, and changing the organization variable or workflow fallback SHALL NOT
require child-repository maintainer action.

#### Scenario: Default evaluate-job duration

- **WHEN** a provider-specific PR workflow receives no mapped job-timeout value
- **THEN** GitHub Actions terminates the evaluate job after 20 minutes if it has
  not completed

#### Scenario: Instance administrators change the evaluate-job duration

- **GIVEN** an instance administrator changes the mapped organization Actions
  variable to a whole number from 10 through 60
- **WHEN** a child repository invokes the reusable workflow
- **THEN** the selected provider workflow uses that number without requiring
  child caller regeneration or a child maintainer commit

#### Scenario: Legacy instance default is not a live timeout source

- **GIVEN** an existing instance configuration contains a legacy
  `job_timeout_minutes` default
- **WHEN** the provider workflow starts
- **THEN** it ignores that legacy value and uses the organization variable or
  the reusable-workflow fallback

### Requirement: Reusable PR workflows expose only consumed caller inputs

Each provider-specific reusable PR-evaluation workflow SHALL omit
`configuration_defaults` from its `workflow_call` contract, and generated PR
callers SHALL NOT pass that input, because timeout resolution is owned by the
organization variable and reusable-workflow fallback.

#### Scenario: Generated caller invokes a provider workflow

- **WHEN** bootstrap renders the provider PR caller
- **THEN** the caller and the selected reusable workflow contain no
  `configuration_defaults` input declaration or mapping
