# Tooling currency delta

## MODIFIED Requirements

### Requirement: Local sync script
The template repo SHALL provide a script, runnable from an already-bootstrapped
child repo with no instance repo clone (`python3 -m panopticon.sync` or
equivalent), that reconciles complete managed resource directories from the
instance's current default branch. The script SHALL stage each managed directory
before applying it, so every module required by the refreshed sync entrypoint
is available together. It SHALL NOT use a per-module allowlist for the managed
`panopticon/` directory.

The script SHALL preserve protected child paths, including
`panopticon/config.json`, `panopticon/.gitignore`, and child-owned workflow
files. It SHALL create or refresh Panopticon-managed caller workflows from the
single shared caller contract and SHALL NOT overwrite or delete unrecognized
child workflow files. The script SHALL NOT delete any child-repository file,
including a managed resource that no longer exists in the instance source,
except exact receipt-owned artifacts retired by a disabled instance feature.
It SHALL delete those retired feature artifacts noninteractively, report each
deleted path, update the receipt, and never stage, commit, or push a deletion.

Given a `--check-updates` flag, the script SHALL run as a pure dry run: it SHALL
report every directory-derived resource and retired feature artifact that would
change or be deleted, using content-based comparison, and SHALL NOT write or
delete any file.

#### Scenario: New sync dependency arrives with the managed directory

- **GIVEN** the instance adds a module required by a refreshed sync entrypoint
- **WHEN** local sync refreshes the managed `panopticon/` directory
- **THEN** the entrypoint and its new dependency are installed as one staged
  resource set before the refreshed entrypoint is used

#### Scenario: Default run refreshes a missing resource-sync caller

- **GIVEN** an initialized child lacks
  `.github/workflows/panopticon-resource-sync.yml`
- **WHEN** local sync runs without flags
- **THEN** it creates the generated caller without rerunning bootstrap

#### Scenario: Protected child workflow is retained

- **GIVEN** a child repository contains a workflow not managed by Panopticon
- **WHEN** local sync refreshes workflows
- **THEN** it does not modify or delete that workflow

#### Scenario: Removed instance resource remains in the child repository

- **GIVEN** a file previously synchronized into a managed directory is no
  longer present in the instance source and is not a receipt-owned retired
  feature artifact
- **WHEN** local sync runs
- **THEN** it does not delete that child file

#### Scenario: Disabled feature artifact is removed

- **GIVEN** a valid feature receipt identifies an OKF helper that the effective
  instance configuration no longer selects
- **WHEN** local sync runs without flags
- **THEN** it deletes that helper, reports the deleted path, and leaves
  unrelated child files untouched

#### Scenario: --check-updates writes nothing

- **WHEN** the sync script is run with `--check-updates`
- **THEN** it reports which files would change or be removed and exits without
  writing or deleting any file

