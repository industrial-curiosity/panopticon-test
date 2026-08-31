# Instance feature packages design

## Context

The template and instance currently treat all root `panopticon-*` skills as
always-on, and child resource refresh is additive. That model cannot express an
optional capability or remove its stale child artifacts. The first feature,
OKF documentation, needs instance-scoped activation while the template's own
documentation remains valid OKF Markdown regardless of activation.

The existing instance configuration workflows already validate inputs, update
only `panopticon.config.json`, and publish a reviewed commit. Bootstrap fetches
that configuration before it writes managed child resources, which makes it the
right authority for feature selection.

## Goals / Non-Goals

**Goals:**

- Let an instance maintainer select a template-defined feature and mode through
  one generic configuration workflow.
- Keep feature source paths, child destinations, modes, and helper code closed
  to template-defined registry entries.
- Deliver enabled feature skills, templates, and helpers to bootstrapped and
  refreshed children; remove them when disabled with the requested interactive
  and noninteractive behavior.
- Make shared workflows honor feature modes without adding feature-specific
  caller inputs or secrets.
- Provide the first feature package for OKF documentation.

**Non-Goals:**

- Arbitrary instance-provided workflow, helper, or artifact-path injection.
- A Codex marketplace plugin or a plugin registry with independently selected
  runtime implementations.
- Automatic documentation rewrites in CI.
- Deleting ordinary managed resources or child-owned files when a feature is
  disabled.
- Adding a third-party YAML dependency to core or child-vendored tooling.

## Decisions

### Template-owned registry and package layout

`features/manifest.json` is a versioned, template-owned registry. Each feature
entry names its supported modes and maps exact package-relative source files to
exact child destinations. Feature files live under `features/<feature-id>/`.
The initial `okf` package contains its opt-in skill, templates, and deterministic
helpers. Registry validation rejects unknown feature IDs, unsupported modes,
duplicate destinations, destinations outside approved managed namespaces, and
any collision with a core managed resource.

The instance configuration stores only a feature ID and mode, for example
`features.okf.mode`. It cannot introduce a source path, destination, command,
workflow, or dependency. This preserves the trusted template-to-instance-to-child
execution boundary. An instance may customize a checked-in feature artifact only
through the existing reviewed template-sync customization mechanisms; children
do not own copied feature artifacts.

Alternative considered: an open instance plugin registry. Rejected because it
would allow code selected by instance configuration to run in CI with instance
credentials and would duplicate the existing instance customization model.

### Generic feature configuration workflow

`Configure Panopticon — Features` is a `workflow_dispatch` workflow with
`feature` and `mode` choice inputs. A dedicated composite action validates the
requested pair against `features/manifest.json`, updates only that feature entry
in `panopticon.config.json`, preserves all unrelated fields and feature entries,
and commits the changed configuration to the selected branch. Rerunning a newer
workflow with no changed inputs uses the current effective configuration as its
defaults rather than resetting other feature selections.

The provider configuration workflows remain provider-specific. Feature
configuration does not accept secrets or provider settings.

### Feature receipt and lifecycle

Bootstrap and local sync derive a desired artifact set from the fetched instance
configuration and registry, fetch and validate the entire set before writing,
and persist a managed receipt under `panopticon/`. The receipt records the
registry revision, selected modes, and exact installed child paths. It exists
solely to identify feature-owned paths; it is not an extension point.

On disable, a path present in the prior receipt but absent from the desired set
is a retired feature artifact. Interactive bootstrap lists the feature and all
retired paths, explains that instance maintainers disabled it, and prompts
`Delete these files? [Y/n]`. Enter and `Y` delete them; `n` retains them and
keeps the receipt entries pending for the next bootstrap. Noninteractive
bootstrap and `panopticon.sync` delete receipt-owned retired paths without a
prompt and report each deletion. No flow stages, commits, or pushes deletions.
Because these paths are feature-owned generated resources, cleanup applies even
when the child copy differs from its installed content; Git history and the
reported diff provide recovery.

Alternative considered: never delete removed resources. Rejected because it
leaves disabled feature skills and helpers active-looking in children.

### Feature mode execution

The core workflow and initialization tooling load the effective feature mode
from the instance configuration and expose it to feature steps through fixed
environment variables or a deterministic feature dispatcher. They do not add
feature-specific reusable-workflow inputs. `disabled` skips feature generation
and checks; `advisory` runs checks and reports findings without changing the
workflow result; `blocking` runs the same checks and makes an unmet feature
requirement fail at the appropriate gate.

The OKF feature uses this dispatcher for local initialization validation and
shared PR workflow validation. Agents perform any documentation migration
locally after the instance is first enabled in advisory mode; CI never rewrites
documentation.

### Pinned workflow currency warning

The instance's configured `workflow_ref` is the authoritative current workflow
ref. Shared workflows compare the child caller's actual `uses: ...@ref` value
with that configured ref. When different, the first summary section is a
non-blocking caution warning identifying the pinned ref and the configured
current ref, with the exact bootstrap/sync recovery action. The warning is not
a feature gate and does not force a working intentionally pinned child to
upgrade.

Alternative considered: infer a newest Git tag. Rejected because tag ordering
is not a reliable instance workflow policy; `workflow_ref` already records the
maintainer's chosen branch, tag, or commit.

### OKF passive format and optional enforcement

The template `docs/` tree is migrated to valid OKF Markdown independently of
feature activation. The OKF package controls the additional agent guidance,
indexes/log maintenance, helper delivery, local conformance validation, and CI
enforcement. The core validator accepts the feature package's constrained,
stdlib-verifiable frontmatter profile, so it never claims to parse arbitrary
YAML. Every generated frontmatter document uses that profile and therefore is
valid YAML.

## Risks / Trade-offs

- [Disabled artifacts are deleted noninteractively] → Limit deletion to exact
  receipt-owned paths, report each one, and never stage or commit changes.
- [A stale receipt could name an unsafe path] → Validate every receipt path
  against the current or historical registry namespace before deletion; reject
  malformed receipts without deleting anything.
- [Feature configuration and artifact source can diverge] → Fetch the
  configuration and registry from one instance ref, record its revision, and
  stage all desired bytes before writes.
- [Existing children have non-OKF docs] → Default OKF to disabled; recommend
  advisory mode and local migration before blocking mode.
- [Pinned children intentionally lag] → Keep the currency warning advisory and
  name both refs rather than guessing a desired tag.

## Migration Plan

1. Ship the feature registry, feature configuration workflow, core dispatcher,
   and receipt support with every feature disabled by default.
2. Convert template `docs/` to passive OKF Markdown and relocate test-only
   Markdown fixtures outside the bundle.
3. An instance maintainer runs `Configure Panopticon — Features` with
   `feature=okf` and `mode=advisory`.
4. Maintainers bootstrap or sync children, run the local OKF migration helper,
   review and commit documentation changes, then select `blocking` when ready.
5. To roll back, select `disabled`; interactive bootstrap offers cleanup and
   noninteractive bootstrap/sync removes receipt-owned feature artifacts.

## Open Questions

- None. Feature source trust, passive documentation format, feature mode
  semantics, deletion behavior, and workflow-ref authority are decided.
