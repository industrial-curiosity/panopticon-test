# Complex-organization instance template

## Why

Panopticon currently documents the pieces needed for an instance-managed
provider, but organizations with centralized credentials, custom Actions, and
per-child identity provisioning must assemble and protect those pieces by
hand. That makes onboarding inconsistent, difficult to review, and vulnerable
to leaking organization-specific identifiers into the public template.

Step 8 of the production rollout hardening plan needs a deterministic,
organization-neutral profile generator before the sandbox rollout can be
executed from a fresh instance.

## What Changes

- Add a versioned, non-secret organization-profile schema with a minimal
  required path for organization-owned choices and optional advanced sections
  for workflow access, registries, gating, and protected-path debt.
- Add deterministic validate, generate, preview, and apply commands that produce
  a reviewable manifest, preflight every destination, and never replace the
  instance tree or accept, print, or persist credential values.
- Generate provider configuration, the fixed instance-managed credential
  wrapper, protection entries, four-gate instance and child onboarding
  checklists, recovery guidance, and a protected-path debt register.
- Provide concrete, executable direct-OIDC and instance-managed synthetic
  profiles and fixture tests covering generation, validation, caller rendering,
  sync protection, bounded application, and offline bootstrap behavior.
- Preserve closed runtime trust: generated callers use explicit mappings,
  provider selection and the credential-wrapper path remain template-owned, and
  the only organization-selected action is a validated broker reference
  (a branch, tag, or full commit SHA) rendered inside that fixed wrapper.
- Classify protection as template-generated, provider-derived, or
  organization-declared; require debt records only for organization-declared
  customizations.
- Document the generate, review, and apply workflow, including the boundary
  between instance-wide setup and per-child identity provisioning.

## Capabilities

### New Capabilities

- `complex-organization-template`: Define and generate a validated,
  organization-neutral instance overlay for complex provider onboarding and
  protected customizations.

### Modified Capabilities

- `llm-provider-configuration`: Require generated profiles to resolve through
  the existing trusted provider contract and preserve non-secret defaults,
  credential modes, and fixed action paths.
- `repo-initialization`: Require generated instance overlays and child callers
  to use explicit trusted mappings and generated four-gate onboarding data.
- `tooling-currency`: Require sync protection to classify the generated
  instance-managed credential wrapper separately from organization-declared
  customizations whose maintenance debt must be reported.
- `four-gate-rollout-process`: Require generated onboarding guidance to
  distinguish instance-wide workflow access from per-child identity and
  credential provisioning.

## Impact

- Adds a deterministic Python profile/generator module, profile fixtures, and
  template assets under a descriptive `templates/` path.
- Adds a manifest-backed command surface under
  `python3 -m panopticon.organization_template` for validation, generation,
  read-only apply preview, and explicit application.
- Adds OpenSpec requirements, generator and integration tests, and public
  documentation for the profile format and workflow.
- Extends existing provider, initialization, tooling-currency, and rollout
  contracts without adding a provider runtime or permitting workflow
  injection.
- Uses only the repository's stdlib-first tooling model; no new runtime
  dependency is required.
