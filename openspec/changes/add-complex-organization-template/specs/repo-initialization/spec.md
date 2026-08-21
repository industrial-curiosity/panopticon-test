# Repository initialization delta

## MODIFIED Requirements

### Requirement: Child bootstrap generates only the selected provider caller

The child SHALL retain a stable local `.github/workflows/panopticon-pr.yml`
caller. Bootstrap SHALL point that caller at only the provider workflow selected
by live instance configuration and SHALL emit explicit canonical input and
secret mappings from the configured org-level names, the exact permissions
required by that provider workflow, the selected trusted credential mode, and
the effective configuration revision. It SHALL map AWS region and role-ARN
variables only for Bedrock `github-oidc` mode. It SHALL NOT copy unselected
provider workflows into the child or use blanket `secrets: inherit`. Onboarding
documentation SHALL explain that a reusable workflow does not transfer caller
identity and SHALL give the per-child identity/credential provisioning owner
and proof step. A caller rendered from a generated organization profile SHALL
meet the same contract and SHALL include the generated four-gate onboarding
references without accepting arbitrary child workflow steps.

#### Scenario: OpenAI child caller generated

- **WHEN** the instance selects OpenAI and child bootstrap succeeds
- **THEN** the local PR caller references only the instance's OpenAI reusable
  workflow, omits LiteLLM-proxy and Bedrock-only setup, maps the configured
  model, API-key, and budget names explicitly, and exposes no endpoint mapping
  because the reusable workflow uses `https://api.openai.com/v1`

#### Scenario: Bedrock child caller generated

- **WHEN** the instance selects Bedrock and child bootstrap succeeds
- **THEN** the local PR caller references the instance's Bedrock reusable
  workflow, grants `id-token: write`, maps the configured instance-token secret
  and Bedrock variables explicitly, includes the config revision, and the gate
  guidance identifies the child repository as the OIDC subject owner

#### Scenario: Instance-managed Bedrock child caller generated

- **WHEN** the instance selects Bedrock `instance-managed` credentials and
  child bootstrap succeeds
- **THEN** the local caller records that credential mode, maps no AWS region or
  role-ARN variable, delegates credentials to the instance workflow, and the
  onboarding proof requires a successful child identity check before provider
  preflight

#### Scenario: LiteLLM child caller generated

- **WHEN** the instance selects LiteLLM and child bootstrap succeeds
- **THEN** the local PR caller references only the instance's LiteLLM workflow,
  omits Bedrock-only setup, and maps the configured endpoint, model, API-key,
  and budget names explicitly

#### Scenario: Generated profile cannot inject child workflow steps

- **WHEN** a generated profile is used to render a child caller
- **THEN** the caller contains only the trusted provider invocation and explicit
  mappings, with no profile-supplied workflow step or blanket secret mapping
