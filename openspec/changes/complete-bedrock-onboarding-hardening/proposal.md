# Complete Bedrock onboarding hardening

## Why

The rollout-gating branch closes the four operational gates but leaves several
onboarding paths dependent on undocumented, hand-authored instance work. Issue
15 remains open because instance owners must reconstruct the Bedrock credential
action, protect it manually from template sync, and infer recovery details that
the workflow could provide directly.

The follow-up should make the remaining setup and recovery paths copyable and
deterministic while preserving the instance-owned credential boundary. It also
needs to remove the Bedrock-only dependency on an organization Actions model
variable without silently selecting an organization-specific model.

## What Changes

- Ship a public, credential-free example of the fixed
  `.github/actions/panopticon-aws-credentials/action.yml` wrapper and link it
  from setup and failure recovery guidance.
- Automatically protect the fixed credential-action path during template sync
  whenever the trusted provider contract selects Bedrock `instance-managed`
  credentials, while retaining explicit `protected_paths` for other customizations.
- Expand missing-action recovery with the example link and a copyable
  `protected_paths` configuration snippet.
- Treat the Bedrock model as an optional Actions variable whose effective value
  may come from a non-secret instance configuration default; fail clearly when
  neither the organization variable nor an instance default supplies a model.
- Document that Bedrock application inference profiles require
  `bedrock:InvokeModel` on both the profile ARN and its underlying
  foundation-model ARN.
- Add the exact GitHub CLI access-policy mutation command to Gate-1 recovery
  guidance, alongside the existing read-only check and UI path.
- Add structural and contract tests covering the example, automatic protection,
  recovery output, model resolution, IAM guidance, and access-policy command.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `four-gate-rollout-process`: make Gate-1 and Gate-3 recovery executable and
  complete the Bedrock IAM guidance.
- `llm-provider-configuration`: allow a Bedrock model to resolve from an
  instance default instead of requiring an organization Actions variable.
- `pr-evaluation`: provide copyable missing-credential-action recovery and
  preserve the fixed action's instance-owned contract.
- `repo-initialization`: expose the fixed credential-action example and make
  instance-managed setup/recovery complete.
- `tooling-currency`: derive protection for the trusted instance-managed
  credential-action path during template sync.

## Impact

The change affects the Bedrock and template-sync reusable workflows, provider
contract/configuration code, recovery formatting, setup/provider documentation,
the public example asset, structural and unit tests, and the five affected
OpenSpec capability specifications. It adds no runtime provider, dependency, or
credential-value handling, and does not change the fixed provider/action trust
registry.
