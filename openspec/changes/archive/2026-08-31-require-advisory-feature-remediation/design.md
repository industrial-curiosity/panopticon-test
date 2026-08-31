# Advisory feature remediation design

## Context

Feature modes currently control whether a validator withholds the
initialization flag or fails a shared PR gate. That enforcement decision is
separate from an agent's responsibility to perform the feature's documented
work. The current orchestration has no feature-remediation step, and
finalization can overwrite advisory feature findings with organization-check
messages, leaving the agent with a misleading successful completion.

## Goals / Non-Goals

**Goals:**

- Treat enabled advisory feature findings as required agent remediation.
- Keep advisory findings non-gating in CI and finalization's exit contract.
- Make feature remediation generic through the managed receipt and installed
  feature skills rather than hard-coding OKF behavior in the orchestrator.
- Preserve unresolved findings as clear, durable child-repository actions.

**Non-Goals:**

- Change the `disabled`, `advisory`, and `blocking` mode names or PR-gate
  outcomes.
- Make agents fabricate content or bypass a feature validator.
- Turn organization configuration or authentication failures into feature work.

## Decisions

### Advisory separates enforcement from completion

`advisory` means a finding does not fail a PR or withhold the initialization
flag by itself. It does not permit an agent to ignore deterministic work. The
feature skill remains the authority for how to repair its findings; the
orchestrator must invoke it and revalidate before declaring its own workflow
complete.

### Discover features through managed bootstrap state

`panopticon-init` will read the feature receipt written by bootstrap, identify
enabled features, and invoke their installed skills after core documentation
generation and before finalization. This keeps the central skill generic and
ensures a feature's instruction package is the only feature-specific behavior.

### Preserve unresolved agent work distinctly

Finalization will retain advisory feature findings as `Child repository` report
items, with the feature ID, affected path or validator finding, installed skill,
and revalidation command. Organization verification results will be appended,
not replace feature findings. If the orchestrator cannot clear an advisory
finding, it keeps the checkpoint and reports an actionable blocker rather than
claiming completed initialization.

## Risks / Trade-offs

- [Risk] A feature skill can require human judgment → [Mitigation] the agent
  reports the exact unresolved decision and preserves the checkpoint instead of
  silently completing.
- [Risk] Generic dispatch could run untrusted content → [Mitigation] dispatch
  only receipt-owned, template-registered feature skills installed by bootstrap.
- [Risk] Revalidation could duplicate feature work → [Mitigation] run it once
  after remediation and resume from the retained checkpoint on interruption.

## Migration Plan

Update the feature and init skills, finalization reporting, and tests together.
Existing advisory-enabled children rerun `/panopticon-init`; the receipt already
provides the enabled feature state, so no configuration migration is required.

## Open Questions

None. The managed feature receipt and installed feature skill define the
dispatch boundary.
