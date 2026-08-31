# Specify bootstrap dependency closure

## Why

The default installer payload can gain a new module-scope import without the
in-memory payload loader registering that dependency first. This caused an
OKF-enabled instance to fail during bootstrap with `ModuleNotFoundError`, even
though the feature module was present in the template and local tooling
manifest.

## What Changes

- Define the default payload's complete module dependency-closure and
  topological-loading contract.
- Require clean-process, real-source integration coverage for the default
  bootstrap payload, including newly added direct dependencies.
- Add an explicit feature-enabled installer scenario so feature-package
  additions exercise the public launcher boundary, not only local bootstrap
  logic.
- Preserve the existing standard-library-only, in-memory payload loading
  model.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `repo-initialization`: strengthen default bootstrap payload dependency
  closure, ordering, and clean-process regression requirements.
- `instance-feature-packages`: require enabled feature packages to load through
  the public installer path before feature artifacts are installed.

## Impact

Affected surfaces are `install.py`, default bootstrap dependency registration,
installer integration tests, and the two existing OpenSpec capability specs.
There are no new dependencies, public API changes, or changes to feature mode
semantics.
