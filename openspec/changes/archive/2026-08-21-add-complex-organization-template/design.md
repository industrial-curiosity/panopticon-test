# Complex-organization instance template design

## Context

Step 8 extends existing provider configuration, bootstrap, sync protection,
and four-gate onboarding behavior. The repository already has trusted provider
contracts, a fixed instance-managed Bedrock action path, explicit caller
rendering, protected-path derivation, and provider defaults. It does not yet
have a reusable organization profile format or a deterministic way to produce
the surrounding instance assets.

The public repository must remain organization-neutral. Generated output is
intended for a private instance repository, while the profile schema, example
profiles, and generator tests are safe to publish.

## Goals / Non-Goals

**Goals:**

- Define and validate a versioned JSON profile whose required fields are only
  organization-owned choices; keep access customization, registries, gating,
  and protected-path debt optional.
- Generate a reviewable instance overlay and onboarding materials using the
  existing provider contract, caller renderer, and sync-protection code.
- Reject unresolved placeholders, unknown logical names, absent default
  sources, unprotected generated customizations, credential-looking values,
  and organization-specific identifiers in public fixtures.
- Make generation deterministic and byte-for-byte idempotent.
- Exercise the generated output without network calls.

**Non-Goals:**

- Adding a provider runtime, credential broker, or organization-specific
  workflow.
- Allowing a profile to select arbitrary reusable workflows, wrapper paths,
  provider mappings, action steps, or child workflow steps. The one bounded
  exception is a validated organization broker action reference rendered
  inside the fixed instance-managed credential wrapper.
- Storing, resolving, or transmitting credential values.
- Provisioning GitHub access, cloud roles, or per-child identities.
- Running the real sandbox rollout; that is Step 9.

## Decisions

### Use a versioned JSON profile

The profile uses JSON with a required `schema_version` and explicit nested
objects. JSON matches `panopticon.config.json`, is handled by the standard
library, and gives deterministic serialization. YAML and workflow-dispatch
inputs were rejected because they add parsing or escaping ambiguity and make
secret-safety validation less local.

The schema separates a minimal authoring surface from advanced sections.
Provider workflow paths, wrapper paths, permissions, logical mappings, default
Actions names, and contract revisions are always derived from the trusted
registry. The minimal direct-OIDC profile asks only for the provider choice and
organization-owned identity/provisioning references. Gating overrides,
internal registries, workflow-access customization, and organization-declared
protected paths are optional and use documented safe defaults when omitted.

### Keep trust decisions in the template-owned registry

The profile may select a registered provider and credential mode and may supply
validated names. In `instance-managed` mode it may also supply one organization
broker action reference using a branch, tag, or full commit SHA, and the
broker's non-secret region output name. The generator renders that reference
only inside the fixed template-owned credential wrapper. The generator asks the existing
provider registry for the workflow path, fixed wrapper path, logical variables,
permissions, defaults, and caller mappings. It never accepts a reusable
workflow path, replacement wrapper path, arbitrary action step, provider
mapping, or child-injected workflow fragment.

### Expose one review-first command flow

The public module is `python3 -m panopticon.organization_template` with these
operations:

1. `validate PROFILE` validates without writing.
2. `generate PROFILE --instance-root INSTANCE --output OVERLAY` validates and
   renders a reviewable overlay into an absent or empty directory.
3. `apply OVERLAY --instance-root INSTANCE --check` performs a read-only
   destination preview.
4. `apply OVERLAY --instance-root INSTANCE` explicitly applies the reviewed
   files.

The overlay layout is stable:

- `overlay-manifest.json` records destination paths, content digests,
  destination preimage digests or absence, ownership classes, protection
  reasons, and computed provider/caller revisions.
- `files/` mirrors paths relative to the instance root, including
  `panopticon.config.json`, the fixed credential wrapper when required, and the
  generated Markdown checklists and debt register.

The manifest is review metadata, not provider configuration. In particular,
computed revisions are not persisted in `panopticon.config.json`.

### Validate and preflight before writing

Generation parses and validates the complete profile, resolves effective
defaults, renders all output in memory, and scans rendered text for prohibited
values and unresolved placeholders before atomically publishing the new overlay
directory. It does not replace the instance directory.

Apply validates the manifest and checks every recorded destination preimage
before changing any file. A mismatch or undeclared collision fails before any
write. Apply writes only manifest-declared paths and never deletes or modifies
unrelated instance content. The normal reviewed instance commit flow remains
the rollback boundary for an unexpected filesystem failure after preflight.

### Treat secrets as names, never values

Fields such as instance-token secret name, model variable name, and shared
broker-action reference are identifiers or references. The validator
rejects values matching credential patterns, including token prefixes, AWS
access-key formats, private-key blocks, and likely secret assignments. Public
synthetic profiles use concrete reserved example domains and identifiers. They
pass the same validation and generation path as private profiles; unresolved
placeholders are never exempted.

### Separate protection ownership from maintenance debt

The manifest and generated reports classify protected paths as
template-generated, provider-derived, or organization-declared. The fixed
credential wrapper is provider-derived whenever `instance-managed` mode is
selected, so the profile does not list it and the debt register does not demand
an owner or upstream-removal plan for it. Only organization-declared protected
customizations require a reason, owner, upstream replacement reference, last
reconciliation result, and removal condition.

### Generate instance-wide and child-specific guidance separately

The output contains an instance checklist for workflow access, provider
configuration, and shared credential setup, plus a child checklist for caller
identity and per-child provisioning. Both use the existing four-gate order and
state the authoritative evidence and recovery action for each gate.

## Risks / Trade-offs

- [Risk] A profile can describe a valid name but an organization can still
  configure an incorrect Actions value outside the repository. → Keep the
  generated contract name-only and make runtime configuration validation the
  source of truth.
- [Risk] Secret-looking-value detection can reject an unusual but harmless
  reference. → Report the exact field and rule and allow only schema-approved
  identifier/reference forms; never add a bypass that persists the value.
- [Risk] A branch or tag can move after an overlay is reviewed. → Render and
  review the exact supplied reference in the fixed wrapper; organizations that
  need immutable execution can choose a full commit SHA.
- [Risk] Organization-declared customizations can accumulate maintenance debt.
  → Require a reason, owner, upstream replacement reference, last
  reconciliation field, and removal condition for each organization-declared
  protected path; report provider-derived paths separately.
- [Risk] Provider contracts evolve after an overlay is generated. → Record the
  computed provider and caller revisions in the review manifest, keep them out
  of persisted provider configuration, and use the existing caller
  compatibility/re-bootstrap path when rendered caller semantics change.
- [Risk] A generated wrapper could be overwritten by template sync. → Emit the
  fixed path in the generated protection manifest and rely on the existing
  provider-derived protection for `instance-managed` mode.

## Migration Plan

1. Add the schema, validator, generator, and synthetic profiles to the public
   template.
2. Validate and generate a fresh private instance overlay with the documented
   commands, then review the manifest, rendered files, protected-path classes,
   computed revisions, and checklists.
3. Run the read-only apply preview, then explicitly apply the unchanged overlay
   to the instance repository using the documented review and commit flow; do
   not modify historical instances automatically.
4. For rollback, discard the generated overlay before commit. After commit,
   restore the prior instance configuration and protected wrapper through the
   normal reviewed instance change process.
5. Use the generated fresh instance as the input to Step 9 sandbox validation.
