# LLM provider configuration delta

## ADDED Requirements

### Requirement: CLI model defaults are explicitly Bedrock-only

The instance-configuration CLI SHALL accept `--model-default` as a parsed
option for command-line consistency, but SHALL reject a non-empty value unless
`--provider bedrock` is selected. The rejection SHALL identify that the option
is supported only for Bedrock and SHALL occur before provider configuration or
instance-file persistence.

#### Scenario: Non-Bedrock CLI rejects a model default clearly

- **WHEN** a maintainer invokes the CLI with `--provider litellm` or
  `--provider openai` and a non-empty `--model-default`
- **THEN** the CLI exits non-zero with an actionable Bedrock-only message and
  does not write `panopticon.config.json`

#### Scenario: Bedrock CLI accepts a model default

- **WHEN** a maintainer invokes the CLI with `--provider bedrock` and a
  non-empty `--model-default`
- **THEN** the CLI persists the value as `llm.defaults.model`

### Requirement: Caller renderer version-skew failures are graceful

The local sync tool SHALL always fetch the caller renderer from the instance at
the effective `workflow_ref` and isolate its loading from provider-contract
resolution. Failures while fetching, compiling, executing, or validating the
fetched renderer—including any non-system exception, a missing, non-callable,
or incompatible `caller_compatibility_revision` export—SHALL exit non-zero
before writing managed resources, report `could not load instance caller
renderer`, and include safe diagnostic context without emitting a raw
traceback. Any local `panopticon/callers.py` SHALL be ignored by sync.

The caller-renderer failure handler SHALL cover only those renderer loading and
compatibility-call operations; it SHALL NOT wrap the full
`resolve_provider_contract` call. Valid provider-configuration failures and
unexpected provider-contract failures SHALL remain distinguishable from
caller-renderer loading failures.

#### Scenario: Fetched renderer omits the compatibility revision

- **GIVEN** a child has no local `panopticon/callers.py`
- **WHEN** sync fetches an instance caller renderer that does not export a
  callable `caller_compatibility_revision`
- **THEN** sync exits non-zero, reports `could not load instance caller
  renderer`, and writes no managed skills, tooling, or workflow callers

#### Scenario: Fetched renderer has invalid Python syntax

- **GIVEN** a child has no local `panopticon/callers.py`
- **WHEN** sync fetches an instance caller renderer whose source cannot be
  compiled
- **THEN** sync exits non-zero, reports `could not load instance caller
  renderer`, writes no managed skills, tooling, or workflow callers, and does
  not emit a raw traceback

#### Scenario: Stale local renderer is ignored

- **GIVEN** a child has a stale local `panopticon/callers.py`
- **WHEN** sync fetches the caller renderer at the effective `workflow_ref`
- **THEN** sync ignores the local renderer, uses the fetched renderer, and
  writes the managed resources successfully

#### Scenario: Invalid local renderer is ignored

- **GIVEN** a child has a local `panopticon/callers.py` with invalid Python
  syntax
- **WHEN** sync fetches the caller renderer at the effective `workflow_ref`
- **THEN** sync ignores the local syntax error, uses the fetched renderer, and
  writes the managed resources successfully

#### Scenario: Renderer execution raises an unexpected exception

- **GIVEN** a fetched or local caller renderer whose module initialization or
  compatibility-revision callback raises a non-system exception
- **WHEN** sync loads or invokes that renderer
- **THEN** sync reports `could not load instance caller renderer`, writes no
  managed skills, tooling, or workflow callers, and does not emit a raw
  traceback

#### Scenario: Provider configuration remains distinguishable

- **GIVEN** the caller renderer is available but the instance provider
  configuration is invalid
- **WHEN** sync resolves the provider contract
- **THEN** sync reports the existing provider-configuration error and does not
  relabel it as a caller-renderer loading failure

#### Scenario: Provider-contract failures remain distinguishable

- **GIVEN** renderer loading and its compatibility callback are available
- **WHEN** provider-contract logic raises an unexpected internal failure
- **THEN** sync does not relabel that failure as a caller-renderer loading
  failure

### Requirement: Bedrock model configuration does not require an Actions variable

The trusted Bedrock provider contract SHALL classify the model logical name as
optional for organization Actions-variable prerequisite reporting. Its
effective value SHALL resolve from a non-empty organization Actions variable
or a non-empty non-secret `llm.defaults.model` instance configuration value.
The public template SHALL NOT require a universal Bedrock model identifier as a
template default. If no permitted source supplies a model, provider
configuration SHALL fail before provider preflight with a source-safe recovery
message naming the logical name and the sources checked.

#### Scenario: Bedrock uses an instance model default

- **GIVEN** the Bedrock contract contains `defaults.model` and the configured
  organization model variable is empty
- **WHEN** the provider workflow resolves effective values
- **THEN** it uses the instance default, reports `instance config` as the
  source, and does not report the model Actions name as required

#### Scenario: Bedrock organization variable takes precedence

- **GIVEN** both the configured organization model variable and
  `llm.defaults.model` contain non-empty values
- **WHEN** the provider workflow resolves effective values
- **THEN** it uses the organization variable and reports only
  `organization variable` as the source

#### Scenario: Bedrock model has no effective source

- **GIVEN** the organization model variable and `llm.defaults.model` are both
  empty or absent
- **WHEN** the provider workflow resolves effective values
- **THEN** it fails before Bedrock preflight, names the model logical name and
  checked sources, and does not print either value

### Requirement: Provider configuration workflows accept a non-secret model default

The Bedrock configuration workflow SHALL expose an optional `model_default`
dispatch input described as a model identifier value, pass it through the
trusted configuration action, and persist it only as the non-secret
`llm.defaults.model` field when non-empty. The workflow SHALL continue to
accept the model Actions-name input for organizations that use an organization
variable and SHALL accept no credential values.

#### Scenario: Instance owner configures a model without an organization variable

- **WHEN** an instance owner dispatches Bedrock configuration with a non-empty
  model default and the default model Actions name
- **THEN** the persisted provider contract contains the default and the model
  name is classified as optional for child prerequisite checks

#### Scenario: Model default input is blank

- **WHEN** an instance owner leaves `model_default` blank
- **THEN** the workflow persists no model default, preserves the configured
  Actions name, and leaves resolution to that organization variable or a later
  instance configuration update

### Requirement: Configuration summaries derive optionality from the trusted contract

The shared provider-configuration action SHALL persist only the supported
`llm` configuration fields. When it reports required and optional Actions names,
it SHALL resolve the persisted block through the trusted provider-contract
resolver and use that effective contract's optional-variable classification. It
SHALL NOT persist derived contract fields such as `optional_variables`.

#### Scenario: Configuration action reports optional Bedrock model source

- **WHEN** an owner configures Bedrock through the shared action
- **THEN** the action reports the model as optional using the effective trusted
  contract, persists a schema-valid `llm` block without `optional_variables`,
  and reaches the commit step

### Requirement: Caller staleness tracks caller-visible compatibility only

The generated-caller renderer SHALL own a canonical, semantic compatibility
payload containing only the contract values that alter the invoked reusable
workflow, its caller permissions, or its supplied inputs and secrets. The
caller-staleness revision SHALL be the hash of that payload. Instance-resolved
operational defaults (`timeout_seconds`, `max_attempts`, and
`max_correction_attempts`) and the instance-resolved Bedrock `model` SHALL be
excluded from the payload when the caller passes only organization variable
expressions for those values; cosmetic default comments SHALL not make them
caller-supplied values. Provider-contract fields that the renderer does not
consume, including optional-value classification, effective-value source
resolution, dependencies, and template defaults, SHALL NOT make an existing
caller stale. The provider-contract resolver SHALL NOT maintain a separate
manually curated list of caller-compatibility fields.

A caller ABI change that adds or changes a required reusable-workflow input,
secret mapping, permission, credential mode, workflow target, or
caller-supplied default SHALL change the compatibility payload and require
regeneration. A change that can be handled by a reusable-workflow fallback
SHALL keep that fallback outside the caller ABI and SHALL NOT require child
bootstrap. A change to only an effective value SHALL NOT require child
bootstrap. When a caller ABI change cannot be handled compatibly, provider
workflows SHALL reject the stale caller before provider work and SHALL clearly
direct the maintainer to bootstrap again.

During the migration window for removing an obsolete caller mapping, each
provider reusable workflow SHALL continue to declare the old
`configuration_defaults` input as optional with a default of `{}` and SHALL
ignore its value. This declaration exists only to let pre-change callers
dispatch and reach the compatibility gate; newly generated callers SHALL omit
the input. The workflow SHALL accept `legacy_revision` only for an otherwise
compatible pre-change caller and SHALL report the bootstrap recovery path for
an incompatible caller.

Bootstrap and local sync SHALL derive a generated caller's compatibility
revision from the caller renderer at that caller's effective `workflow_ref`.
They SHALL use the same renderer source to render that caller. The default
branch may remain the source of refreshed child tooling, but it SHALL NOT
determine a caller revision or rendered caller for a distinct pinned
`workflow_ref`.

#### Scenario: Pinned renderer controls the generated revision

- **GIVEN** a child pins its workflow to a ref whose fetched caller renderer
  changes the compatibility payload
- **WHEN** local sync generates the managed callers
- **THEN** the generated caller contains the compatibility revision returned by
  the pinned renderer, rather than the revision from the default-branch
  renderer

#### Scenario: Bedrock runtime optionality preserves existing callers

- **GIVEN** an existing Bedrock child caller whose provider names, permissions,
  credential mode, and instance defaults are unchanged
- **WHEN** the template adds a server-side optional effective-value source for
  the Bedrock model
- **THEN** the caller revision remains valid and the workflow does not require
  the child to rerun bootstrap solely for that runtime behavior change

#### Scenario: A runtime-only provider-contract field does not churn callers

- **GIVEN** an existing child caller and its rendered reusable-workflow
  invocation are unchanged
- **WHEN** the provider contract adds or changes a field that the caller
  renderer does not consume
- **THEN** the caller compatibility revision remains valid and the workflow
  does not require child bootstrap

#### Scenario: Instance operational defaults do not churn callers

- **GIVEN** an existing caller renders organization variable expressions for
  `timeout_seconds`, `max_attempts`, `max_correction_attempts`, and Bedrock
  `model`
- **WHEN** an instance changes any corresponding instance-resolved default
- **THEN** the caller compatibility revision remains unchanged, the rendered
  invocation remains byte-identical, and no child maintainer action is
  required

#### Scenario: Unrelated providers avoid Bedrock-only churn

- **GIVEN** LiteLLM and OpenAI instances have otherwise unchanged caller-visible
  contracts
- **WHEN** a Bedrock-only runtime contract behavior changes
- **THEN** their caller revisions remain unchanged and their children are not
  required to rerun bootstrap

#### Scenario: Required caller permission change rejects a stale caller

- **GIVEN** an existing child caller does not grant a newly required reusable-
  workflow permission
- **WHEN** the provider contract changes the caller permission rendered for
  that workflow
- **THEN** the caller compatibility revision changes and provider evaluation
  fails before provider work with the exact child-bootstrap recovery command

#### Scenario: Shared workflow timeout fallback avoids caller churn

- **GIVEN** an existing child caller passes only the organization variable for
  `job_timeout_minutes`
- **WHEN** the template workflow default changes
- **THEN** the reusable workflow uses the new fallback without requiring child
  bootstrap or changing the caller compatibility revision

#### Scenario: Value-only changes avoid bootstrap

- **GIVEN** an existing caller's rendered target, permissions, mappings, and
  caller-supplied values are unchanged
- **WHEN** an instance administrator changes only an effective provider value
- **THEN** the workflow applies the new value without requiring child
  bootstrap or changing the caller compatibility revision

#### Scenario: Pre-change caller reaches the migration gate

- **GIVEN** a pre-change generated caller passes `configuration_defaults` and
  supplies the legacy compatibility revision
- **WHEN** it dispatches a provider reusable workflow during the migration
  window
- **THEN** GitHub accepts the call, the workflow ignores
  `configuration_defaults`, and the caller reaches the legacy compatibility
  gate

#### Scenario: ABI change gives an explicit bootstrap recovery

- **GIVEN** a caller's rendered invocation no longer satisfies the reusable
  workflow ABI
- **WHEN** the provider workflow evaluates its compatibility revision
- **THEN** it rejects the caller before provider work and clearly instructs the
  maintainer to rerun child bootstrap

#### Scenario: Pinned workflow ref uses its own renderer revision

- **GIVEN** an instance pins `workflow_ref` to a ref whose caller renderer has
  a different compatibility payload from the default branch
- **WHEN** bootstrap or local sync generates a child caller
- **THEN** it uses the pinned renderer's revision and rendered workflow text,
  and the reusable workflow at that pinned ref accepts the caller revision

## MODIFIED Requirements

### Requirement: Provider configuration exposes separate full-contract and caller revisions

The effective provider contract SHALL expose `revision` as a deterministic
full-contract fingerprint for diagnostics and contract-change tests. Generated
callers and reusable workflows SHALL use `caller_revision` for the
caller-visible compatibility boundary. The reusable-workflow input named
`configuration_revision` SHALL remain the canonical wire name for backwards
compatibility, but SHALL carry the semantic `caller_revision` value; it SHALL
not be renamed without a coordinated caller-ABI migration. During migration,
`legacy_revision` SHALL equal the full-contract fingerprint that the
pre-optionality Bedrock contract would have produced, so existing callers
remain accepted without making the full-contract fingerprint a
caller-staleness check. A caller compatibility mismatch SHALL report
`caller compatibility revision changed` and include the child-bootstrap
recovery path.

The legacy fingerprint SHALL be reconstructed from the raw, validated instance
defaults before migration-only fields are removed from the effective contract.
It SHALL preserve a legacy `job_timeout_minutes` default when an existing
caller could have embedded it, and SHALL remove the newly introduced Bedrock
`model` default because pre-optionality callers could not have embedded that
field.

#### Scenario: Legacy revision preserves the pre-optionality Bedrock contract

- **GIVEN** a Bedrock contract adds `model` to its optional runtime values
- **WHEN** the trusted resolver produces the current contract
- **THEN** its `legacy_revision` equals the deterministic full-contract hash
  after removing only the Bedrock `model` optionality and its associated
  template default and any newly introduced Bedrock model default, while
  preserving raw legacy defaults that pre-change callers could have embedded;
  `caller_revision` remains the active caller check

#### Scenario: Legacy job-timeout defaults remain accepted during migration

- **GIVEN** an existing instance configuration contains
  `llm.defaults.job_timeout_minutes`
- **WHEN** the trusted resolver produces the current contract
- **THEN** its `legacy_revision` equals the pre-change full-contract hash that
  includes that timeout default, even though the effective current contract
  omits it

#### Scenario: Bedrock model defaults do not alter the legacy hash

- **GIVEN** an existing Bedrock caller predates Bedrock instance model
  defaults
- **WHEN** the instance later adds `llm.defaults.model`
- **THEN** its `legacy_revision` still equals the pre-optionality full-contract
  hash without the model default, and the existing caller passes the
  compatibility gate without child bootstrap

#### Scenario: Full-contract changes remain diagnostic-only for callers

- **GIVEN** a provider contract changes a runtime-only field that the renderer
  does not consume
- **WHEN** the trusted resolver produces the current contract
- **THEN** `revision` changes as the full-contract fingerprint while
  `caller_revision` remains unchanged

#### Scenario: Legacy wire name carries the caller revision

- **GIVEN** a generated child caller invokes a reusable provider workflow
- **WHEN** the caller supplies its compatibility value
- **THEN** it supplies the semantic `caller_revision` value through the
  existing `configuration_revision` wire input, and the reusable workflow
  accepts that input without requiring callers to rename it

### Requirement: Provider contracts declare effective value sources

The trusted provider registry SHALL declare which selected-provider variable
logical names are optional and which have template workflow defaults. Optional
names SHALL be a subset of the selected provider and credential mode's
registered variables. The instance contract MAY declare non-secret defaults
only for optional runtime values. The instance token, provider credentials,
API keys, and authentication settings SHALL remain required and SHALL NOT be
supplied by an instance default or default-resolver action.

For each optional variable, the effective value SHALL be selected in this
order: an explicit non-empty organization Actions variable, a non-empty output
from the fixed instance default-resolver action, a non-empty non-secret
instance configuration default, then the declared non-empty template workflow
default. If no source supplies a value, provider configuration SHALL fail
before provider preflight or LLM work.

New configuration surfaces SHALL NOT accept or persist an instance default for
`job_timeout_minutes`; a legacy persisted value MAY be read and ignored for
migration. `job_timeout_minutes` SHALL be resolved by the reusable workflow
from the organization Actions variable or its workflow-owned fallback; instance
defaults and the fixed default-resolver action SHALL NOT supply that job-level
value. Changing the organization variable or workflow-owned fallback SHALL NOT
require child bootstrap.

#### Scenario: Shared workflow supplies the timeout fallback

- **GIVEN** the organization Actions variable for `job_timeout_minutes` is
  absent
- **WHEN** the reusable provider workflow starts
- **THEN** GitHub applies the workflow-owned fallback before the evaluate job
  runs, without consulting an instance action or child caller default

#### Scenario: Organization timeout variable takes precedence

- **GIVEN** the organization Actions variable for `job_timeout_minutes` is a
  valid value from 10 through 60
- **WHEN** the generated caller invokes the reusable workflow
- **THEN** the workflow uses the organization value before applying its
  fallback

#### Scenario: Organization administrators change the timeout without child action

- **GIVEN** an instance administrator changes the mapped organization Actions
  variable to a valid value from 10 through 60
- **WHEN** an existing child invokes the reusable workflow
- **THEN** the workflow uses the new value without child caller regeneration or
  a child maintainer commit

#### Scenario: Legacy job-timeout default is ignored without breaking migration

- **GIVEN** an existing instance configuration contains
  `llm.defaults.job_timeout_minutes`
- **WHEN** the trusted resolver loads the configuration
- **THEN** it accepts the configuration for migration, excludes that value from
  the effective persisted contract, and resolves the job timeout only from
  the organization variable or reusable-workflow fallback

#### Scenario: Optional value has no effective source

- **GIVEN** an optional provider variable is absent from every permitted source
- **WHEN** the provider workflow resolves its effective configuration
- **THEN** it fails before provider preflight, names the logical value and
  checked sources, and does not display any credential or value

### Requirement: Provider workflows resolve effective configuration before preflight

Each provider-specific reusable PR workflow SHALL resolve optional non-secret
provider inputs through the validated contract before provider preflight and
LLM work. It SHALL preserve raw caller inputs until resolution and SHALL expose
only source labels in diagnostics. The workflow SHALL receive
`job_timeout_minutes` as the organization variable expression from the caller;
its job-level timeout SHALL apply the reusable-workflow fallback before any
step runs. It SHALL NOT obtain that value from the fixed instance action or an
instance-configured caller default. The configuration-action summary SHALL
describe the fixed Action, instance-default, and workflow-default sources as
applying to optional request-budget variables, and SHALL separately state that
job timeout uses only the organization variable or reusable-workflow fallback.

#### Scenario: Timeout fallback changes without caller regeneration

- **GIVEN** an existing child caller passes only the organization timeout
  variable expression
- **WHEN** the reusable workflow's fallback changes
- **THEN** the child caller remains compatible and uses the new fallback on its
  next run without re-bootstrap

#### Scenario: Configuration summary distinguishes timeout ownership

- **WHEN** the provider configuration action summarizes optional variables
- **THEN** it describes request-budget source precedence separately from
  `job_timeout_minutes` and identifies the reusable workflow as the timeout
  fallback owner
