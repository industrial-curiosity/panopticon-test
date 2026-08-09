# panopticon-ay-eye

<!-- Centered media uses HTML because Markdown cannot align it; a plain image
would lose the README's intentional visual balance. -->
<!-- markdownlint-disable MD033 -->
<p align="center">
  <img src="https://industrialcuriosity.com/images/panopticon/panopticon-logo-chip.png" alt="Panopticon logo" />
</p>
<!-- markdownlint-enable MD033 -->

## [View the organization architecture](docs/architecture.md)

Panopticon gives an organization a shared view of its system architecture:
repository documentation,
runtime interfaces, and internal package dependencies. It helps teams see
cross-repository changes before
they land.

## Start here

Create a private instance from this template, run its LiteLLM, OpenAI, or Bedrock
configuration workflow, and
initialize child repositories. The [org-owner setup guide](docs/setup-guide.md)
walks through that process,
including the four rollout gates (workflow access, effective configuration,
caller identity/credentials, and real request compatibility), provider choices,
template sync, the reviewed Bedrock credential-action example, customization
protection, and local recovery from failed syncs. Bedrock model identity may be
provided by its organization variable or by the non-secret instance default
`llm.defaults.model`; the public template does not select a universal model.
Runtime-only provider behavior changes do not force child re-bootstrap. A
change to only an effective value also does not require bootstrap. The
caller renderer owns the compatibility fingerprint and hashes only the
semantic reusable-workflow target, caller permissions, configured mappings,
credential mode, and caller-passed values. Instance-resolved operational
defaults and Bedrock model values are runtime-only, even when shown in
cosmetic generated comments; changes to them do not require child
re-bootstrap. Changes to the actual rendered caller ABI require regeneration
of affected callers; an incompatible caller receives a clear bootstrap
recovery path. The reusable workflow owns the pre-job
timeout fallback, so changing that shared default does not require child
re-bootstrap. For a pinned workflow ref, bootstrap and
local sync load that ref's renderer, so the generated fingerprint and reusable
workflow use the same version.
Instance administrators can change the value of the mapped organization
job-timeout variable for existing children without regenerating callers.
Renaming the mapped variable changes the caller compatibility revision and
requires caller regeneration; legacy instance job-timeout defaults are
ignored during migration.
During the migration window, provider workflows retain and ignore the old
optional `configuration_defaults` input so pre-change callers can dispatch and
reach the legacy compatibility gate. Newly generated callers omit it. The
trusted provider contract also exposes a separate full-contract `revision`
for diagnostics and migration checks. The existing reusable-workflow wire input
`configuration_revision` is intentionally retained for caller ABI compatibility,
but carries the semantic `caller_revision`; existing compatible callers may use
`legacy_revision`. Renaming that wire input would require a coordinated caller
migration. A mismatch reports `caller compatibility revision changed` and gives
the child-bootstrap recovery path.
For required values, optional request budgets, defaults, and the exact
organization integration path, use the [provider-configuration guide](docs/provider-configuration.md).

To initialize a child repository, run the public launcher from that repository:

```bash
curl -fsSL https://raw.githubusercontent.com/industrial-curiosity/panopticon-ay-eye/main/install.py | python3
```

Set `PANOPTICON_INSTANCE=YOUR-ORG/YOUR-INSTANCE-REPO` for a non-interactive run;
for example,
`PANOPTICON_INSTANCE=acme/panopticon-instance`. Authenticate every install,
including for a public instance, with `GH_TOKEN`, `GITHUB_TOKEN`, or an existing
`gh auth` session. Authentication provides a much higher GitHub API quota and is
required for private instances. Set a token through your shell or CI secret
environment; never place its value directly in the launcher command.

After the agent runs finalization, review the child repository's
`panopticon-initialization-report.md`. It gives the current outcome and separates
child-repository repairs from organization configuration follow-up. Complete any
listed action, then rerun the exact finalization command from the report.

## How it works

Panopticon has three repository roles:

- **Template** — this public repository provides the shared tooling, workflows,
  and skills.
- **Instance** — one private knowledge-base repository per organization, created
  from the template.
- **Child repository** — an organization repository connected to its instance.

The workflow is intentionally simple:

1. Initialize a child repository to generate its architecture documentation and
   local indexes. During documentation generation, the child compares proposed
   interface names with the instance's existing compiled index and persists
   reviewed naming decisions as source/configuration hints.
2. On pull requests, Panopticon checks behavior-bearing changes against
   documentation, compares likely interface matches with the instance index,
   and predicts interface conflicts; documentation-only changes pass without
   an LLM review.
3. On merge, the instance collects documentation and indexes to build an
   organization-wide view.
4. When planning a change, developers and agents use that shared view to
   understand affected connections.

Panopticon deliberately excludes illustrative directories (`examples`, `samples`, `fixtures`,
`testdata`, `demos`, `scaffolding`, `demo`, and `scaffold`) from analysis while retaining similarly
named production paths such as `src/sample-service`. A child repository's generated
`operations.md` lists the excluded folders actually present and documents the explicit
`panopticon-ignore file` and `panopticon-ignore declaration` escape hatches.

The organization architecture is a complete interface inventory: it includes
interfaces even when only one repository participates, and highlights detected
ownership/type conflicts and potential same-name collisions.

Interface-conflict checks are advisory by default. The instance sets the default
in `panopticon.config.json`, and a child repository may override that check in
its committed `panopticon/config.json` with
`gating.interface-conflict: "advisory"` or `"blocking"`. Both modes publish a
prominent warning; only `blocking` fails the PR check.

Child repositories can also run the manual **Panopticon resource sync** workflow
to refresh their managed skills and local tooling. It opens or updates a
reviewable open pull request instead of changing the default branch directly.
After that pull request is merged or closed, the next changed sync creates a
new pull request.

Run `python3 -m panopticon.sync` in an initialized child repository to refresh
managed skills, local tooling, and Panopticon workflow callers. Use
`python3 -m panopticon.sync --check-updates` to preview the resulting changes.
Each run downloads the versioned, data-only child-safe tooling manifest from
the selected instance branch, so a child repository's vendored manifest cannot
expand the set of files sync manages. It warns, without deleting them, about
Python modules outside the manifest so maintainers can review legacy or
child-owned files.

Child-local documentation links stay relative to the document that contains
them. Generated links from a child README or architecture overview to the
organization architecture use the resolver-produced direct GitHub URL, so they
work from both the child and instance repositories.

## Documentation

- [Set up an organization instance](docs/setup-guide.md)
- [Configure provider defaults](docs/provider-configuration.md)
- [Contribution guidelines](CONTRIBUTING.md)
- [Contribute a parser](docs/parser-contribution.md)
- [Use interface and dependency hints](docs/hint-reference.md)
- [Run the test suite](docs/testing.md)
- [View the organization architecture](docs/architecture.md)

## Repository contents

- `panopticon/` — Python tooling used by the template, instance, and CI
  workflows.
- `.github/workflows/` — shared automation for configuration, evaluation, merge,
  and template sync.
- `interfaces/` and `dependencies/` — organization-wide indexes populated in an
  instance.
- `docs/` — setup, contribution, and reference documentation.
- `.agents/skills/` — skills used by local agents and CI.

For configuration details, supported providers, sync protection rules, and
operational procedures, use the
[org-owner setup guide](docs/setup-guide.md) rather than relying on this
overview.

<!-- Centered media uses HTML because Markdown cannot align it; a plain linked
thumbnail would lose the README's intentional visual balance. -->
<!-- markdownlint-disable MD033 -->
<p align="center">
  <a href="https://www.youtube.com/watch?v=sIJ9XhBSkI8" target="_blank" rel="noopener noreferrer">
    <img src="https://img.youtube.com/vi/sIJ9XhBSkI8/hqdefault.jpg" alt="Watch the Panopticon introduction on YouTube" />
  </a>
</p>
<!-- markdownlint-enable MD033 -->
