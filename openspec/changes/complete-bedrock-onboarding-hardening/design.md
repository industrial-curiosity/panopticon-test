# Complete Bedrock onboarding hardening design

## Context

The current rollout branch has a four-gate operating process and caller-side
credential timeout reporting. The remaining issue-#15 paths are concentrated at
the instance boundary:

- The fixed instance-managed credential action has a known path but no reviewed
  example.
- Template sync derives merge protection from `docs/architecture.md` and the
  instance's explicit `protected_paths`; it does not derive the fixed action
  path from the trusted provider contract.
- Bedrock model resolution still classifies the model name as required even
  though the reusable workflow input is optional.
- Recovery text omits the example, protection fragment, and exact access-policy
  mutation command.

The public repository is copied into private instances, so examples must be
safe to publish and organization-specific identity, role, region, model, and
credential values must remain instance-owned.

## Goals / Non-Goals

**Goals:**

- Give instance owners a checked-in, copyable credential-action skeleton.
- Preserve the fixed credential-action path automatically during template sync
  for valid Bedrock `instance-managed` configuration.
- Make missing-action recovery self-contained and copy/paste friendly.
- Allow Bedrock to source its model from a non-secret instance default without
  selecting a public organization-specific model.
- Complete the Gate-1 and Bedrock IAM guidance with executable, safe commands.
- Lock the behavior with contract, structural, recovery, and documentation
  tests.

**Non-Goals:**

- Implementing an organization's credential broker, IAM role registration, or
  model-selection policy.
- Automatically changing GitHub Actions access policy.
- Accepting, persisting, or printing credential values.
- Allowing an instance or child to select an arbitrary workflow or action path.
- Changing the existing caller-side timeout and surviving recovery boundary.

## Decisions

### Keep the fixed credential-action path canonical at each runtime boundary

The provider registry remains the canonical Python owner of the fixed
instance-managed credential-action path. Recovery formatters import that value
instead of redeclaring it. The reusable workflow keeps one workflow-level
binding for its self-contained import fallback; shell validation reads that
binding, while the local-action invocation remains the literal GitHub Actions
step path required by the workflow syntax. This removes drift between Python
formatters and the fallback's local variable without making the path
configurable.

### Ship a public example at the fixed action path's documented source

Add `docs/examples/panopticon-aws-credentials/action.yml` as the canonical
skeleton. It will be a composite action with a placeholder reference to an
organization-approved credential broker and a documented region-output
contract. The example will contain no real organization, role, account, region,
or credential value. Setup and workflow recovery will link to the file at the
stable public template URL.

The example is preferred over an inline-only guide because the target path,
composite-action shape, and output boundary remain reviewable as a file and can
be copied into an instance without reconstructing YAML from prose.

### Derive protection from the trusted instance-managed contract

Centralize the sync path calculation so it starts with the template-owned
generated path, adds the fixed credential-action path only when the raw
instance configuration selects `bedrock` and `instance-managed`, and then adds
explicit organization `protected_paths`. The derived path is a fixed constant
from the provider registry; no configuration value can supply or redirect it.

Write the derived path to `.git/info/attributes` with the existing
`merge.ours` driver. Report it in a separate step-summary section from
organization-declared customizations. Reuse the same calculation in the local
recovery commands so a failed hosted sync and its local repair protect the same
paths.

An unconfigured instance remains syncable. Provider-dependent validation keeps
its existing responsibility for rejecting an invalid provider contract; sync
protection only reacts to the exact trusted provider/mode pair.

### Make the Bedrock model optional without inventing a universal model

Extend the Bedrock provider contract's optional logical names to include
`model`. Add a non-secret `model_default` input to the provider configuration
workflow and persist it as the instance contract's `defaults.model` when
provided. The runtime resolution order for Bedrock model is organization
Actions variable, instance configuration default, then any declared provider
workflow default. This change does not add a public fixed Bedrock model;
without an effective value, the resolver fails before provider preflight and
names the model logical name and the sources checked.

The configured Actions name remains available for organizations that prefer an
organization variable, but it is omitted from the required-variable report.
The model default is treated as a non-secret model identifier and is validated
as a non-empty string using the existing provider configuration rules.

Alternatives considered:

- Hard-code a Bedrock model identifier in the public provider registry. This
  would make availability, region, access, and lifecycle assumptions that belong
  to each organization.
- Keep the organization variable required and improve only the error text. That
  would leave the instance-default path unavailable and would not close the
  onboarding gap described by the issue.

### Make the CLI's provider boundary explicit

Keep `--model-default` available in the shared parser so provider-specific
configuration commands retain a consistent interface, but reject a non-empty
value before calling provider configuration for LiteLLM or OpenAI. The CLI
error names Bedrock as the supported provider; this is the smallest change
that makes the existing provider contract boundary clear without duplicating
provider-specific parsers.

### Scope stale-caller revisions to caller-visible compatibility

The revision embedded in a generated child caller is a compatibility check for
that rendered caller, not a release marker for the entire provider registry.
The caller renderer will therefore construct the canonical compatibility
payload alongside the caller invocation it renders. The payload contains only
values that alter the reusable-workflow target, caller permissions, or supplied
inputs and secrets. The caller passes only organization variable expressions;
instance-resolved operational defaults (`timeout_seconds`, `max_attempts`,
`max_correction_attempts`, and Bedrock `model`) are not caller inputs. The
reusable workflow owns their resolution, while cosmetic default comments in
generated callers do not make them part of the ABI. The reusable workflow owns
its pre-job fallback so that fallback is not embedded in child YAML. A legacy
persisted `job_timeout_minutes` default may
remain in instance configuration for schema compatibility, but it is ignored
for job timeout resolution.
Hashing this renderer-owned semantic payload makes rendered caller compatibility
the source of truth and prevents a manually maintained provider-contract field
list from accidentally turning an internal provider change into organization-
wide child churn. Runtime provider behavior, including optional-value
classification, resolution-source ordering, dependencies, and template
defaults, remains in the full trusted provider contract but does not
invalidate an otherwise compatible caller.

An intentional caller ABI change—such as a new required input or secret,
changed permission, credential mode, workflow target, or caller-passed
default—must alter the renderer-owned payload. The provider workflow then
rejects the stale caller before provider work and supplies the exact bootstrap
recovery command. This preserves fail-closed behavior at the caller boundary
without using re-bootstrap as a general provider workflow release mechanism.

The existing global contract-version mechanism is not a rollout switch. A
global caller-revision schema bump is reserved for a rendering-contract change
that affects every provider. Provider-specific caller-visible changes naturally
alter only that provider's caller revision. This lets the Bedrock model-default
path refresh the affected Bedrock callers when a default is configured without
forcing LiteLLM, OpenAI, or unchanged Bedrock callers to rerun bootstrap.

The renderer is versioned with the reusable workflow it describes. Bootstrap
and local sync therefore fetch the caller renderer at the effective
`workflow_ref` before deriving a revision or rendering caller YAML. They may
still refresh child-safe tooling from the default branch, but that tooling copy
is not authoritative for a caller pinned to another ref. This prevents a newer
default-branch renderer from creating a revision the pinned reusable workflow
cannot validate.

Reusable workflow contracts normally contain only inputs consumed by their
workflow bodies. During the migration window, the three provider workflows
retain the obsolete `configuration_defaults` input as an optional,
default-`{}` compatibility declaration and ignore it. This dispatch-level
shim is required because GitHub rejects undeclared reusable-workflow inputs
before any job can reach the legacy compatibility gate. The caller renderer
still omits the mapping for new callers; after the migration window, a
coordinated change may remove the shim. The job-timeout value remains an
explicit organization-variable mapping and the reusable workflow owns its
fallback.

The persisted `llm` block remains the narrow instance configuration schema.
The shared configuration action resolves that persisted block through the
trusted provider resolver when it needs derived reporting metadata such as
optional-variable classification; it does not serialize those derived fields.
Instance administrators retain child-independent control of job duration
through the mapped organization Actions variable. Because GitHub evaluates a
job timeout before any Action runs, the legacy instance job-timeout default is
accepted only for migration and is omitted from newly persisted effective
contracts.

The migration fingerprint is computed from the raw validated defaults captured
before effective-default filtering. The legacy view restores any
`job_timeout_minutes` value an old caller could have embedded, while removing
the newly introduced Bedrock `model` default and optionality metadata. This
keeps the compatibility shim faithful to the actual pre-change contract without
adding a new caller input or requiring child regeneration.

### Make recovery sections self-contained

Extend the shared credential recovery formatter with the example URL and a
JSON-compatible `protected_paths` fragment. Keep the small inline workflow
fallback aligned with the formatter so older child checkouts receive the same
instructions when the vendored module cannot be imported. The recovery section
will continue to name the child repository, the fixed action path, the
registration boundary, the rerun command, and the timeout outcome.

Add the exact Gate-1 mutation command as an explicitly privileged instance-owner
operation after the read-only access check:

```bash
gh api -X PUT repos/YOUR-ORG/YOUR-INSTANCE-REPO/actions/permissions/access -f access_level=organization
```

The guide will state that the command changes the instance's reusable-workflow
access policy and requires the documented administration permission. The
existing UI and read-only verification remain the source of truth when an
administrator chooses a different policy.

### Keep bootstrap renderer failures source-safe

Bootstrap loads the caller renderer from the effective workflow ref before any
managed child writes. A missing file (HTTP 404) or connection-level retrieval
failure uses the bundled renderer, workflow-name tuple, and compatibility
callback so a transient instance fetch failure does not strand installation
after validation. Authentication and other HTTP/API failures remain controlled
hard failures; they must not silently substitute code that can differ from the
selected workflow ref. The fallback assignment is positional because
`wire_workflows` requires the first value to be the iterable workflow-name
tuple. Compilation and required-symbol failures in a fetched copy remain
controlled errors; the bootstrap boundary also validates and guards the
selected renderer's compatibility callback before provider resolution, then
previews every managed caller before skills or tooling are written. Renderer
failures therefore cannot fall through as provider `TypeError`s or leave
partial managed resources, while
provider-contract errors remain on their existing provider configuration
remediation path.

### Complete inference-profile permission guidance

Update the Bedrock setup and provider-configuration guidance to state that an
application inference profile request needs `bedrock:InvokeModel` on both the
selected profile ARN and the underlying foundation-model ARN. Keep
`bedrock:GetInferenceProfile` as the separate discovery/metadata permission
when the integration uses it. Use placeholder ARNs in public documentation.

## Risks / Trade-offs

- [An organization's broker does not match the example's output contract] →
  Keep the example explicit about the region environment output and require
  instance owners to adapt only the broker-specific step.
- [A raw but malformed provider configuration triggers no automatic path] →
  Keep the derived path closed to the exact provider/mode pair and retain the
  existing provider validation and recovery failure.
- [An instance omits both the Bedrock model variable and default] → Fail before
  provider preflight with source-safe recovery naming the model and rerun path.
- [A fixed model default becomes unavailable] → Keep the public template free
  of a universal Bedrock model and make the instance's non-secret default
  explicit in its provider contract.
- [The access-policy mutation command is run with insufficient privilege] →
  Document the required administrator token permissions and retain the 403
  reauthentication path.

## Migration Plan

1. Sync the updated template into an instance. Existing callers remain valid
   when the rollout changes only Bedrock runtime optionality or effective
   values; do not rerun child bootstrap solely for those changes. During the
   migration window, the provider workflows retain the ignored
   `configuration_defaults` declaration so pre-change callers dispatch and
   reach the legacy gate.
2. For `instance-managed` instances, copy the example into the fixed action
   path, replace the broker placeholder, verify its region output, and commit
   the action.
3. Run template sync and confirm the fixed action appears in the derived
   protected-path summary without requiring a manual `protected_paths` entry.
4. Configure either the organization model variable or the instance's
   non-secret model default. Changing instance-resolved defaults does not
   require child bootstrap; rerun it only when the rendered caller ABI changes.
5. Exercise Gate 1, missing-action recovery, credential timeout recovery, and a
   real structured provider request in a sandbox.

Rollback is a template revert. Existing explicit `protected_paths` entries and
existing caller contracts remain valid; callers with a genuinely changed ABI
receive an explicit bootstrap recovery message. Removal of the compatibility
shim requires a later coordinated migration in which all affected children
have regenerated their callers.

## Open Questions

None. The public template deliberately leaves the concrete credential broker,
IAM policy, region, and Bedrock model selection to each instance owner.
