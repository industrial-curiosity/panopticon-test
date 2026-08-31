# Complex-organization instance template tasks

## 1. Define the profile contract

- [x] 1.1 Add the versioned JSON profile schema and concrete, executable public
  synthetic profiles under a descriptive `templates/` path. Keep the required
  surface to organization-owned choices and place access customization,
  registries, gating, and protected-path debt in optional advanced sections.
- [x] 1.2 Reuse the trusted provider registry to validate provider, credential
  mode, logical names, fixed action paths, region output contracts, and
  effective default sources.
- [x] 1.3 Validate an instance-managed broker action only in the dedicated
  wrapper field, allow a branch, tag, or full commit SHA plus a region output
  name, and reject attempts to replace the fixed wrapper or inject runtime
  structure.
- [x] 1.4 Add profile validation for unresolved placeholders,
  credential-looking values, organization-specific identifiers in public
  fixtures, unknown fields, invalid optional names, incomplete
  organization-debt entries, and attempts to reclassify template-generated or
  provider-derived paths as organization debt.

## 2. Implement deterministic generation

- [x] 2.1 Add the stdlib-only `panopticon.organization_template` command with
  `validate`, `generate`, and `apply` operations, stable serialization, and
  deterministic file order.
- [x] 2.2 Render `panopticon.config.json` through the existing provider
  configuration contract, preserving explicit trusted provider and credential
  mappings.
- [x] 2.3 Render the fixed instance-managed credential wrapper and required
  region output contract without accepting credential values, reusable
  workflow paths, replacement wrapper paths, or action structure beyond the
  bounded broker reference.
- [x] 2.4 Generate protection metadata classified as template-generated,
  provider-derived, or organization-declared. Automatically protect the fixed
  credential wrapper in `instance-managed` mode, reject attempts to
  reclassify derived paths, and require debt records only for
  organization-declared customizations.
- [x] 2.5 Generate separate instance-wide and child onboarding checklists in
  the existing four-gate order, including ownership, evidence, recovery, and
  rerun instructions.
- [x] 2.6 Render the complete overlay in memory, publish it only to an absent or
  empty output directory, and generate a stable manifest with destination and
  preimage digests, protection metadata, and computed revisions outside
  `panopticon.config.json`.
- [x] 2.7 Implement read-only `apply --check` and explicit apply. Validate all
  destination preimages before writing, refuse stale or undeclared collisions,
  write only manifest-declared files, and never replace the instance tree or
  delete unrelated files.

## 3. Integrate trusted runtime boundaries

- [x] 3.1 Load generated configuration through the real provider-contract code
  and preserve caller compatibility revision behavior.
- [x] 3.2 Render generated child callers with explicit mappings, provider
  permissions, and no `secrets: inherit` or profile-supplied workflow steps.
- [x] 3.3 Make tooling-currency and template-sync protection report generated,
  provider-derived, and organization-declared paths with distinct reasons.
- [x] 3.4 Add generated-profile references to provider, initialization,
  tooling-currency, and four-gate recovery summaries without duplicating
  provider runtime logic.

## 4. Add fixture and regression coverage

- [x] 4.1 Add tests proving both concrete synthetic profiles validate and
  generate without placeholder exemptions, including invalid logical names,
  missing defaults, unsupported modes, malformed broker refs, and secret-looking
  values. Cover valid branch, tag, and full-commit-SHA broker references, plus
  rejection of attempts to classify template-generated or provider-derived
  paths as organization debt.
- [x] 4.2 Add tests proving byte-for-byte idempotent generation, revisions only
  in review metadata, and no overlay writes after validation or rendering
  failure.
- [x] 4.3 Add end-to-end offline fixture tests that generate a temporary
  instance, load its provider contract, render child callers, run sync
  protection checks, and exercise bootstrap without network calls.
- [x] 4.4 Add tests proving generated public fixtures contain no
  organization-specific identifiers or credential values and that generated
  onboarding separates instance-wide from per-child work.
- [x] 4.5 Add apply tests proving `--check` is read-only, stale preimages and
  undeclared collisions fail before writes, and unrelated instance files are
  never modified or deleted.

## 5. Document and validate the workflow

- [x] 5.1 Add `docs/complex-organization-template.md` with the schema,
  supported fields, security constraints, generated outputs, and synthetic
  examples, including the rule that derived paths cannot be declared as
  organization debt.
- [x] 5.2 Update setup and provider documentation with the exact validate,
  generate, `apply --check`, apply, rollback, and per-child onboarding commands.
  Put the minimal copy-and-paste path before advanced field reference material.
- [x] 5.3 Run the full stdlib test suite, strict OpenSpec validation, and
  Markdownlint for all changed artifacts.
- [x] 5.4 Update `README.md` and `docs/spec.md` to reflect any user-facing or
  architectural changes introduced by this change.
