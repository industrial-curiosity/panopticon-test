# README Start Here design

## Context

The README already has a concise overview requirement and links to focused
guides, but its current `Start here` section has accumulated provider,
compatibility, migration, and recovery details. The change is documentation-only
and should improve the first-read path without changing the existing README
navigation, architecture link, or closing video.

## Goals / Non-Goals

**Goals:**

- Make `Start here` a short orientation and onboarding section.
- Preserve only the information a new user needs to understand what Panopticon
  does and begin setup.
- Make linked documentation the owner of detailed setup, provider, and
  operational procedures.
- Turn the readability and scope expectations into testable documentation
  requirements.

**Non-Goals:**

- Change the project's architecture, provider contracts, bootstrap behavior,
  or generated child repositories.
- Rewrite the detailed guides or remove information that is still needed there.
- Remove the `How it works`, Documentation, Repository contents, or media
  sections unless implementation reveals a direct duplication that must move.

## Decisions

### Keep Start Here as the first user-action section

The section will follow the architecture link and project-purpose orientation.
It will answer, in order: what Panopticon does, what kind of repository the
reader is looking at, what the first setup action is, how to authenticate, and
where the complete setup guide lives.

Alternative considered: remove `Start here` entirely and rely on the
Documentation list. This would make the README shorter but would leave a new
user without a guided first action, so it is not selected.

### Move detail by documentation ownership

Provider selection and configuration belong in the provider-configuration guide;
instance setup, rollout gates, recovery, and synchronization belong in the
org-owner setup guide. The README will link to those documents and retain only
their role in the onboarding path. Caller fingerprints, migration shims, and
runtime-only compatibility rules do not belong in the introduction.

Alternative considered: summarize every implementation detail in shorter
paragraphs. This would preserve the same cognitive burden and continue to
duplicate the guides, so it is not selected.

### Enforce readability through content boundaries

The specification will require a scannable section with short paragraphs or
lists, a clear first command, and explicit links to detailed guides. It will
also prohibit implementation inventories, compatibility/migration mechanics,
and operational recovery procedures in `Start here`. Reviewers can validate the
README directly against these boundaries without inventing a word-count limit.

## Risks / Trade-offs

- [Risk] Removing a detail that a user needs for first setup → [Mitigation]
  retain the launcher, authentication options, initialization outcome/report,
  and direct links to the authoritative guides.
- [Risk] The section grows again as features change → [Mitigation] add the
  explicit scope and readability scenarios to the repository requirement.
- [Risk] Existing links or generated README assumptions are disturbed →
  [Mitigation] keep architecture-diagram and media requirements intact and
  limit the implementation to the content boundary.

## Migration Plan

Rewrite the README section, update the repository-initialization requirement,
validate the OpenSpec change, and review the rendered Markdown. No runtime
migration or rollback procedure is required; reverting the README and spec
edits restores the prior documentation.

## Open Questions

None.
