# LLM provider configuration

## MODIFIED Requirements

### Requirement: Integrator guidance explains effective provider configuration

Provider setup documentation and configuration workflow summaries SHALL present
an organization integrator with a provider-specific table that identifies every
logical value's purpose, required or optional status, allowed source(s) in
precedence order, configured Actions name when applicable, and a concrete next
action. The guide SHALL give an ordered setup path for the organization-variable
only case and a separate, clearly labelled path for the fixed instance default
resolver. It SHALL state that neither path accepts, stores, or displays
credential values. The same guide SHALL place those steps in the four-gate
operating sequence and SHALL identify the evidence that proves effective
defaults before provider preflight.

#### Scenario: Integrator configures a provider with only organization values

- **WHEN** an integrator follows the provider setup guide without an instance
  default or default-resolver action
- **THEN** the guide identifies the required Actions names, verification
  command, expected result, child-bootstrap command, and the effective-
  configuration gate proof without requiring knowledge of implementation source

#### Scenario: Integrator needs dynamic optional defaults

- **WHEN** an integrator chooses the fixed instance default-resolver action
- **THEN** the guide names its fixed path, declared outputs, precedence, safe
  validation command, and recovery for a missing or invalid output without
  exposing credential values

### Requirement: Unconfigured-instance remediation supports console and CLI paths

Every unconfigured-provider failure intended for a maintainer SHALL print direct
GitHub Actions console URLs for the resolved instance's LiteLLM, OpenAI, and
Bedrock configuration workflows and an equivalent copy/paste `gh workflow run`
command for each using the resolved instance slug and default branch. It SHALL
explain that the maintainer must choose exactly one provider path, then print an
exact one-line public installer command with `PANOPTICON_INSTANCE` applied
directly to the Python process, without requiring a preceding `export`. Public
provider guidance SHALL also identify request compatibility as a separate final
gate: a passing credential or capability preflight is not proof that a real
structured request is accepted by the selected model.

#### Scenario: Bootstrap reports an unconfigured private instance

- **WHEN** child bootstrap resolves `acme/panopticon-instance` on default branch
  `main` with no provider
- **THEN** its remediation includes direct URLs ending in
  `configure-panopticon-litellm.yml` and `configure-panopticon-bedrock.yml`,
  corresponding `gh workflow run` commands for both files, ordered
  provider-choice instructions, and
  `curl -fsSL https://raw.githubusercontent.com/industrial-curiosity/panopticon-ay-eye/main/install.py | PANOPTICON_INSTANCE='acme/panopticon-instance' python3`

#### Scenario: Provider preflight passes but the real request fails

- **WHEN** credentials and capability preflight succeed but a real structured
  provider request is rejected
- **THEN** the workflow/report identifies gate 4, names the selected model or
  request-shape resource without printing credentials, assigns the repair to
  the provider/model owner, and instructs the maintainer to rerun the same
  structured-request proof after correcting the adapter or model configuration

### Requirement: Bedrock authentication supports trusted organization choices

The Bedrock provider contract SHALL persist one selected credential mode from a
closed registry. In `github-oidc` mode, it SHALL require configured AWS region
and role-ARN names and the generated caller's `id-token: write` permission. In
`instance-managed` mode, it SHALL require and invoke only the fixed instance-
local credential action `.github/actions/panopticon-aws-credentials/action.yml`
and SHALL document that the action runs under the child caller's identity; an
organization may therefore need to provision every child repository separately.

#### Scenario: Organization uses a GitHub OIDC role

- **WHEN** an organization selects `github-oidc` and configures a region, role
  name, and child trust policy
- **THEN** the caller requests `id-token: write`, the workflow assumes the role
  as the child repository, and gate-3 proof names the child identity rather
  than the instance workflow repository

#### Scenario: Organization manages credentials in its instance

- **WHEN** an organization selects `instance-managed` and provides the fixed
  credential action
- **THEN** its provider workflow invokes only that action, does not require
  AWS region or role-name inputs in the contract, and reports the child
  identity/credential boundary if the action fails

#### Scenario: Instance-managed credential action is absent

- **WHEN** an organization selects `instance-managed` but its instance lacks the
  fixed credential action
- **THEN** bootstrap or provider evaluation fails before LLM work and names the
  required action path

#### Scenario: Configuration attempts to override the credential action

- **WHEN** instance configuration supplies an action path or other
  credential-action override
- **THEN** provider validation rejects the configuration before child bootstrap
  writes a workflow
