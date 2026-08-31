# Add instance feature packages

## Why

Panopticon currently distributes every root `panopticon-*` skill and only
performs additive child syncs. Instance maintainers therefore cannot enable an
optional capability for selected organizations, nor can they reliably remove
its child artifacts when it is disabled.

The first optional capability is OKF documentation support. Its passive
Markdown metadata belongs in the template documentation, but its generation,
validation, CI enforcement, skills, templates, and helpers must be explicitly
enabled by an instance maintainer.

## What Changes

- Add a template-owned feature registry and feature package layout under
  `features/`, beginning with an `okf` package.
- Add a generic manual GitHub Actions configuration workflow that validates and
  persists one feature's requested mode while preserving existing instance
  configuration.
- Add `disabled`, `advisory`, and `blocking` feature modes. Disabled features
  do not select child artifacts or run feature checks; advisory features report
  violations; blocking features enforce them.
- Make bootstrap and refresh sync select only enabled feature artifacts, record
  their ownership in a child receipt, and clean up disabled artifacts.
- Prompt during interactive bootstrap before removing disabled feature
  artifacts; remove them automatically in noninteractive bootstrap and sync,
  while reporting every deleted path.
- Add pinned-workflow currency warnings to shared-workflow summaries when a
  child calls a ref other than the instance's configured current workflow ref.
- Add conditional OKF generation and validation behavior, plus OKF metadata and
  indexes for the template documentation bundle.

## Capabilities

### New Capabilities

- `instance-feature-packages`: trusted, instance-configured selection,
  delivery, lifecycle, and cleanup of optional feature packages.
- `okf-documentation`: optional OKF documentation generation and conformance
  validation for Panopticon documentation bundles.

### Modified Capabilities

- `repo-initialization`: bootstrap and finalization consume effective feature
  configuration and feature artifacts.
- `tooling-currency`: child resource reconciliation detects and cleans up
  disabled feature artifacts.
- `pr-evaluation`: shared evaluation workflows conditionally run enabled
  feature checks and warn about stale pinned workflow refs.
- `doc-generation`: generated documentation gains feature-controlled OKF
  structure and validation.

## Impact

Affected areas include instance configuration schema and validation, bootstrap
and sync tooling, child managed-state files, template and reusable GitHub
Actions workflows, documentation-generation skills and templates, test
fixtures, and user-facing setup guidance. The change remains stdlib-first and
does not add an external runtime dependency.
