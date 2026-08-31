# Guard template validation and standardize workflow summaries

## Why

Configured instance repositories currently retain the template-validation workflow,
which runs template-only assertions against valid instance configuration. This
creates false CI failures. GitHub Actions summaries also lack a uniform opening
statement, making it harder to tell each job's purpose before reading details.

## What Changes

- Restrict template validation so it creates a runnable job only in the
  canonical template repository; configured instances skip it entirely.
- Require every Panopticon GitHub Actions job summary to start with a brief,
  non-sensitive statement of the action the job is attempting to perform.
- Add deterministic workflow-contract tests for the repository guard and the
  summary preamble convention.

## Capabilities

### New Capabilities

- `template-validation-scope`: Limits template-only validation to the canonical
  template repository.
- `workflow-purpose-summaries`: Provides a consistent first section for every
  Panopticon GitHub Actions job summary.

### Modified Capabilities

- None.

## Impact

Affected artifacts include `.github/workflows/template-validation.yml`, shared
and provider-specific workflow summaries, and workflow-contract tests. No
provider credentials, public APIs, or child-repository caller contracts change.
