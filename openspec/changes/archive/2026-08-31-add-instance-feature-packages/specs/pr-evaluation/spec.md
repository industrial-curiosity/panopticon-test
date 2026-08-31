# PR evaluation delta

## ADDED Requirements

### Requirement: Feature-mode PR evaluation

Each provider-specific reusable PR workflow SHALL load the effective instance
feature modes from its checked-out instance configuration and run feature checks
through fixed conditional steps or fixed environment flags. It SHALL not add a
feature-specific caller input, secret mapping, or selectable workflow path.
Disabled checks SHALL be skipped, advisory checks SHALL report without failing
the workflow, and blocking checks SHALL contribute their validated failure to
the existing final gating outcome.

#### Scenario: Blocking OKF check fails a PR

- **WHEN** the instance enables OKF in blocking mode and a child documentation
  bundle fails OKF validation
- **THEN** the shared PR workflow reports the violation and fails through its
  normal final gating outcome

#### Scenario: Disabled OKF check does not run

- **WHEN** the instance disables OKF
- **THEN** the shared PR workflow does not invoke OKF validation or require OKF
  feature artifacts in the child

### Requirement: Pinned workflow summary warning

The shared PR workflow SHALL compare the child caller's actual reusable
workflow ref with the instance configuration's `workflow_ref`. When the refs
differ, the first section of its step summary SHALL be a non-blocking caution
warning naming the child's pinned ref, the instance's configured current ref,
and the exact bootstrap or sync action that refreshes the child. It SHALL not
infer a latest tag and SHALL not fail the workflow solely because of this
warning.

#### Scenario: Child caller uses a stale pinned ref

- **WHEN** a child caller uses a tag, branch, or commit SHA different from the
  instance's configured `workflow_ref`
- **THEN** the summary begins with a caution warning that names both refs and
  remains non-blocking
