# Instance feature packages tasks

## 1. Feature registry and configuration

- [ ] 1.1 Define the versioned template-owned `features/` registry format, approved child destination namespaces, supported feature modes, and strict validation errors.
- [ ] 1.2 Add the `features/okf/` package with its skill, templates, deterministic helpers, and registry mappings; ensure it cannot collide with core managed resources.
- [ ] 1.3 Extend instance configuration loading, validation, and revision/reporting to preserve generic `features.<id>.mode` entries while rejecting unregistered IDs and modes.
- [ ] 1.4 Add the generic `Configure Panopticon — Features` workflow and composite action with validated `feature` and `mode` inputs, existing-state defaults, branch-targeted commits, and actionable failure summaries.
- [ ] 1.5 Add focused configuration and workflow tests for enable, disable, preservation of unrelated settings, invalid feature/mode rejection, and no secret-value handling.

## 2. Feature-aware child delivery and cleanup

- [ ] 2.1 Add core feature-selection and receipt logic that resolves one instance config and registry revision before staging feature artifact bytes.
- [ ] 2.2 Update bootstrap to install enabled feature artifacts alongside core skills/tooling and expose effective feature state to local initialization without writing `panopticon/config.json` early.
- [ ] 2.3 Add interactive bootstrap cleanup: explain the instance-disabled feature, list receipt-owned paths, prompt `Delete these files? [Y/n]`, and retain pending receipt entries when declined.
- [ ] 2.4 Add noninteractive bootstrap and `panopticon.sync` cleanup that deletes only valid receipt-owned retired paths, reports each deletion, and never stages, commits, or pushes.
- [ ] 2.5 Extend sync dry-run, tooling-currency comparison, and unmanaged-file reporting for selected, pending, and retired feature artifacts without deleting ordinary managed or child-owned files.
- [ ] 2.6 Add hermetic bootstrap/sync tests for disabled-by-default delivery, enabled artifact installation, interactive accept/decline, noninteractive deletion, malformed receipt rejection, and no partial writes.

## 3. Workflow behavior and pinned-ref visibility

- [ ] 3.1 Add a fixed feature dispatcher or environment contract in the shared provider workflows that loads effective modes without new caller inputs, secrets, or selectable workflows.
- [ ] 3.2 Implement disabled, advisory, and blocking execution semantics for feature checks and integrate blocking failures into existing final gating.
- [ ] 3.3 Add an advisory first-summary caution when the child caller's actual reusable-workflow ref differs from the instance `workflow_ref`; name both refs and exact refresh recovery without guessing a latest tag.
- [ ] 3.4 Add reusable-workflow and caller compatibility tests for feature dispatch, mode behavior, and pinned tag, branch, and commit-SHA warnings.

## 4. OKF documentation feature

- [ ] 4.1 Convert the template `docs/` bundle to constrained OKF Markdown, add root and nested indexes/log behavior, and relocate Markdown test fixtures outside the bundle.
- [ ] 4.2 Update core documentation templates and deterministic interface rendering to support installed OKF frontmatter without changing index-derived interface content.
- [ ] 4.3 Implement the stdlib-only OKF helper and tests for constrained frontmatter, non-empty types, reserved index/log files, and precise conformance diagnostics.
- [ ] 4.4 Integrate OKF generation and validation into local initialization and shared PR checks only when the effective feature mode enables them; ensure advisory mode reports and blocking mode gates without CI rewrites.
- [ ] 4.5 Add end-to-end fixtures proving an OKF-enabled child bootstraps, generates, validates, syncs, disables, and removes its feature artifacts while a disabled child remains compatible.

## 5. Documentation and validation

- [ ] 5.1 Update setup, testing, feature configuration, bootstrap recovery, and documentation-generation guidance with enable, advisory migration, blocking, disable, and cleanup instructions.
- [ ] 5.2 Update README.md and docs/spec.md to reflect any user-facing or architectural changes introduced by this change.
- [ ] 5.3 Run the full standard-library test suite, strict OpenSpec validation, and Markdownlint for all changed artifacts.
