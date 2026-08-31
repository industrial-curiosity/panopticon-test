# Repository Initialization Spec Delta

## MODIFIED Requirements

### Requirement: Orchestrating init skill

The template repo SHALL include a `panopticon-init` skill (name prefix
`panopticon-`, so the existing skill-download step installs it into the child
repo automatically with no bootstrap script changes) that runs the other Phase
2 skills, enabled feature remediation, and the Phase 3 finalization command in
the correct dependency order from a single invocation, while leaving each
underlying skill independently invocable on its own.

The order SHALL be:

1. `panopticon-interface-naming`
2. `panopticon-interface-extraction` — after step 1, since it depends on the
   naming pass
3. `panopticon-dependency-naming` — after step 2, since a
   `panopticon-dependency-of` hint links a dependency entry to an existing
   interface's canonical name, which requires the interface index built by
   step 2 to already exist
4. `panopticon-dependency-extraction` — after step 3, since it depends on the
   dependency naming pass, mirroring how interface-extraction depends on
   interface-naming
5. `panopticon-doc-generation` — after steps 1–4, since the interface-docs and
   dependency-docs layers are rendered from the local indices
   (`panopticon/index.json` and the dependency shard) that those steps build;
   running doc-generation first has no index to render from
6. Each enabled feature's installed skill, followed by that feature's
   deterministic validator
7. The finalization command (`python3 -m panopticon.init_repo --instance
   <instance>`) — the instance slug SHALL be self-discovered by reading the
   `uses:` line already wired into `.github/workflows/panopticon-pr.yml`, rather
   than requiring the user to supply it

`panopticon-init` SHALL maintain a checkpoint log at `panopticon/.init-log.json`
recording which of the seven steps have completed. Before starting a step, it
SHALL check the log and skip any step already recorded as complete. It SHALL
update the log immediately after each step completes, so an interrupted run —
including one resumed in a new agent session with no memory of the prior one —
continues from the first incomplete step rather than restarting from scratch or
skipping ahead into a step whose prerequisites are not met. It SHALL delete the
checkpoint only when finalization succeeds and no agent-remediable feature
finding remains.

Each of the skills SHALL remain fully usable on its own, independent of
`panopticon-init` and of any checkpoint log state, for users who want to run a
single step directly.

#### Scenario: Fresh run starts at interface naming

- **GIVEN** no checkpoint log exists
- **WHEN** `/panopticon-init` runs
- **THEN** it starts with `panopticon-interface-naming`, then creates the
  checkpoint log recording that step's completion before continuing

#### Scenario: Dependency naming runs only after the interface index exists

- **GIVEN** the checkpoint log shows `panopticon-interface-naming` and
  `panopticon-interface-extraction` complete
- **WHEN** `panopticon-init` continues
- **THEN** it runs `panopticon-dependency-naming` next, with a populated
  interface index available for `panopticon-dependency-of` hints to reference

#### Scenario: Doc generation runs only after both indices exist

- **GIVEN** the checkpoint log shows `panopticon-interface-naming`,
  `panopticon-interface-extraction`, `panopticon-dependency-naming`, and
  `panopticon-dependency-extraction` all complete
- **WHEN** `panopticon-init` continues
- **THEN** it runs `panopticon-doc-generation` next, with a populated interface
  index and dependency shard to render `interfaces.md` and the dependency-docs
  layer from

#### Scenario: Resuming after an interrupted session

- **GIVEN** a checkpoint log recording `panopticon-interface-naming`,
  `panopticon-interface-extraction`, and `panopticon-dependency-naming` as
  complete from a prior agent session that did not finish
- **WHEN** `/panopticon-init` is invoked again in a new agent session with no
  memory of the prior one
- **THEN** it skips the three completed steps and resumes at
  `panopticon-dependency-extraction`

#### Scenario: Checkpoint log deleted on successful completion

- **GIVEN** all seven steps have completed, `panopticon/config.json` has been
  written, and no agent-remediable feature finding remains
- **WHEN** `panopticon-init` finishes
- **THEN** `panopticon/.init-log.json` no longer exists in the repo

#### Scenario: Enabled advisory feature is remediated before finalization

- **GIVEN** the managed feature receipt enables OKF in advisory mode
- **WHEN** `/panopticon-init` reaches feature remediation
- **THEN** it invokes the installed OKF skill, repairs deterministic findings,
  and reruns the OKF validator before finalization

#### Scenario: Advisory feature work remains unresolved

- **GIVEN** an enabled advisory feature still has an agent-remediable finding
- **WHEN** its validator completes
- **THEN** `/panopticon-init` retains its checkpoint and reports the feature
  skill and revalidation command instead of declaring initialization complete

#### Scenario: Individual skills remain independently invocable

- **WHEN** a user invokes `/panopticon-doc-generation` or
  `/panopticon-dependency-naming` directly instead of `/panopticon-init`
- **THEN** it runs as its own standalone skill, unaffected by whether a
  checkpoint log exists

#### Scenario: Finalization instance slug is self-discovered

- **WHEN** `panopticon-init` reaches the finalization step
- **THEN** it determines the instance slug by reading the `uses:` line in
  `.github/workflows/panopticon-pr.yml` rather than asking the user for it

## ADDED Requirements

### Requirement: Finalization preserves advisory feature actions

Finalization SHALL report every enabled advisory feature finding as a
`Child repository` action item. Each item SHALL name the feature, the affected
artifact or validation finding, the installed feature skill, and its
revalidation command. Organization configuration findings SHALL be appended to
the report without replacing feature action items.

#### Scenario: Advisory feature and organization findings coexist

- **GIVEN** finalization finds an advisory OKF violation and cannot verify an
  organization Actions setting
- **WHEN** it writes `panopticon-initialization-report.md`
- **THEN** the report contains the OKF item under `Child repository` and the
  verification item under `Organization configuration`

#### Scenario: Advisory feature finding is resolved

- **GIVEN** a previous report listed an advisory feature action
- **WHEN** the feature validator passes on re-finalization
- **THEN** the refreshed report omits the resolved feature item
