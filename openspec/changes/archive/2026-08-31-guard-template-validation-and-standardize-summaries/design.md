# Guard template validation and standardize workflow summaries design

## Context

The public template's `template-validation.yml` is retained by configured
instance repositories. Its test suite includes assertions about an unconfigured
template root, so executing that workflow in an instance turns valid provider
configuration into a false CI failure. Panopticon's workflows also write
different styles of GitHub Actions summaries, often only after a later failure.

## Goals / Non-Goals

**Goals:**

- Run template validation only when `github.repository` identifies the canonical
  template repository.
- Make each executing Panopticon job write a concise, non-sensitive purpose
  preamble before any other summary content.
- Keep existing failure reports and recovery guidance intact after the preamble.
- Verify both rules with deterministic repository tests.

**Non-Goals:**

- Remove the template-validation file from existing instances.
- Change provider configuration, caller contracts, job permissions, or gates.
- Require a summary from a caller-only reusable-workflow delegation job, which
  cannot contain steps; its invoked job owns the executable summary.

## Decisions

### Canonical repository guard

The template-validation job will use a job-level GitHub Actions condition that
matches the canonical public template repository exactly. A job-level guard
prevents checkout and test execution in every configured instance while keeping
the workflow file harmless when it is retained by a template-derived repository.

An environment variable or repository-name convention is rejected because an
instance can configure it incorrectly and would weaken the invariant.

### Summary preamble as the first executable step

Every shipped workflow job that contains steps will begin with a summary-writing
step. It will append a stable Markdown heading and one short sentence describing
the job's intended action before checkout, validation, provider work, or any
failure-handling summary writes.

The preamble is local to each workflow rather than a composite action. This
keeps the workflow purpose visible at its definition site and avoids introducing
an action dependency for a two-line, non-secret operation. Delegation-only jobs
that use a reusable workflow have no steps; the reusable job is the execution
and summary owner.

### Deterministic coverage

Repository tests will inspect all shipped workflow definitions. They will assert
the exact template repository guard, ensure the template test command is
reachable only through that guarded job, and require each step-bearing job's
first summary write to be its purpose preamble. Tests will also ensure that the
preamble is not copied from a provider-specific description and does not include
secret values.

## Risks / Trade-offs

- [A fork intentionally used as a template cannot run this validation] → The
  canonical-repository guard expresses the stated policy; maintainers can test
  forks locally or through the canonical template's CI.
- [Workflow edits might place an earlier summary write ahead of the preamble] →
  A full workflow inventory test prevents regression.
- [Preambles become stale as job behavior evolves] → The purpose sentence is
  reviewed alongside the workflow and constrained to a brief description of the
  actual job responsibility.

## Migration Plan

1. Merge the guarded workflow and summary preambles in the template repository.
2. Existing configured instances may retain `template-validation.yml`; the
   guarded job will be skipped and will no longer execute template-only tests.
3. If a regression is found, revert the template change. Existing instance
   provider configuration and caller workflows are unaffected.

## Open Questions

None.
