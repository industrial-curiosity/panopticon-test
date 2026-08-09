# Panopticon

<!-- Downloaded by Panopticon's bootstrap script (install.py) — identical in every child repo of
     this instance. Re-run install.py to update; don't hand-edit, your changes
     will be overwritten
     on the next bootstrap re-run. -->

## Panopticon — getting started

This repo is a **child repo** in a Panopticon setup. Panopticon keeps this
repo's documentation and
interface index current, and merges them into a shared **instance repo** so the
whole organization can
see cross-repo architecture and interfaces in one place.

## How it works

- **Template repo** — the shared tooling and workflows every instance starts
  from.
- **Instance repo** — your org's private knowledge base: every child repo's
  docs, the compiled
  cross-repo interface index, and org-wide configuration. See
  `panopticon/config.json`'s `instance`
  field for which repo that is.
- **This repo (a child repo)** — owns its own docs and interface index, kept
  current by your AI agent
  and verified by CI on every pull request.

On every pull request, Panopticon checks that docs and the interface index are
current and simulates
this repo's interface changes against the instance's compiled index, reporting
conflicts. On every
merge to this repo's default branch, its docs and index are pushed into the
instance repo, and the
org-wide architecture diagram is rebuilt from the fresh compiled index.

## Where to find architecture diagrams

- **This repo's own `README.md`** — links to both diagrams at the top: this
  repo's own (relative,
  resolves once merged into the instance) and the org diagram (a fully-qualified
  GitHub URL, clickable
  immediately, kept current by doc generation).
- **This repo's own diagram** — the `## Architecture diagram` section in this
  repo's own
  `architecture.md`.
- **The org-wide diagram** — `docs/architecture.md` at the instance repo's root,
  rebuilt on every
  merge from every child repo's current interfaces. This repo's own diagram
  section links to its
  place in that org-wide picture once this repo's docs have been merged into the
  instance — that
  link only resolves *after* the merge, not before.

To regenerate an immediately clickable link to the org diagram yourself, before
any merge:

```bash
python3 -m panopticon.org_diagram_link
```

This prints a single resolvable URL, reading `panopticon/config.json` first — no
network call in
the common case. If that config is missing the branch it needs, it falls back to
a live lookup
(using the same `GH_TOKEN`/`GITHUB_TOKEN`/`gh auth token` credentials the rest
of this repo's
tooling already uses) before giving up. No instance repo clone either way.

## Keeping this repo's skills and tooling current

The skills and vendored `panopticon/` tooling in this repo are snapshots taken
at bootstrap time.
Nothing prompts a refresh automatically — pull the instance's current versions
on demand:

```bash
python3 -m panopticon.sync
```

Alternatively, run **Actions → Panopticon resource sync → Run workflow** from
this repository's default branch. It opens or updates one pull request for
managed resource changes, so you can review them before merging. It creates no
pull request when everything is current.

This overwrites this repo's skills and vendored tooling unconditionally from the
instance's current
default branch. There's no per-file protection — review `git diff`/`git status`
before committing,
and don't commit anything you disagree with.

To see what would change without writing anything:

```bash
python3 -m panopticon.sync --check-updates
```

Sync reads the versioned, data-only local-tooling manifest from the instance's
current branch. It can also warn about Python modules under `panopticon/` that
are not in that manifest. **Instance-excluded** modules exist in the instance
but are not child-safe; **child-only and unknown** modules are not in the
instance. Both warnings are advisory and leave files untouched. Review the
module's owner and imports first. Remove an unwanted legacy module only in a
separate reviewed change, then run this repo's tests before committing it.

Every pull request also runs an advisory (never blocking) check that warns when
this repo's wired
workflow ref, skills, or vendored tooling have drifted from the instance's
current default branch —
acting on that warning is at your discretion.

## Provider configuration defaults

Provider credentials and repository access are required organization settings.
LiteLLM and OpenAI model identity remains required; Bedrock model identity may
come from its organization variable or the non-secret instance default
`llm.defaults.model`. Request budgets are optional and have a documented
precedence order; see the instance's `docs/provider-configuration.md` for the
required/optional table, configuration steps, and fixed Action contract. Never
put credentials or tokens in a default.

## Four-gate rollout checks

When a child workflow fails, record the last gate with green evidence. A later
gate is not proven until the earlier one passes:

1. **Reusable-workflow access** — for a private or internal instance, read the
   run-page banner first. Authenticate as an instance administrator with a
   fine-grained token that has `Administration: Read` and `Contents: Read` on
   the instance repository, or use a classic PAT with `repo` scope. Check
   `https://github.com/YOUR-ORG/YOUR-INSTANCE-REPO/settings/actions` and run:

   ```bash
   INSTANCE='YOUR-ORG/YOUR-INSTANCE-REPO'
   gh api "repos/${INSTANCE}/actions/permissions/access" --jq '.access_level'
   ```

   Use the run-page banner and the access check to establish whether the gate
   passed. If it fails, follow the recovery instructions emitted for that run.

2. **Effective provider configuration** — a missing value, missing default, or
   stale caller-compatibility revision belongs to the instance contract or this
   child caller. If it fails, follow the provider workflow or bootstrap summary;
   it identifies whether the instance configuration or child caller needs
   attention.
3. **Caller identity and credentials** — reusable workflow code does not
   transfer identity. GitHub OIDC identifies this child repository, so verify
   the caller's permissions and register this exact child in the organization's
   approved identity system. In Bedrock `instance-managed` mode, the fixed
   credential wrapper remains instance-owned. If the gate fails or times out,
   follow the caller-owned gate-3 summary.
4. **Real provider-request compatibility** — a green provider preflight proves
   credentials and capability, not model request compatibility. Complete one
   real structured inference. Route unsupported fields, model errors, and
   request-shape failures to the provider/model owner rather than changing
   workflow access or IAM.

The instance's [setup guide](docs/setup-guide.md) contains the stable setup
prerequisites and gate evidence definitions. Failure-specific recovery is
emitted by the bootstrap or workflow that detects it.
