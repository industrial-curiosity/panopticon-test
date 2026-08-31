# Repository Initialization Specification Delta

## MODIFIED Requirements

### Requirement: Default bootstrap payload loads its import dependencies

The default payload loader SHALL register `panopticon.providers` before
executing any fetched module that imports it, including
`panopticon.recovery`, and SHALL load the modules in dependency order before
executing `panopticon.bootstrap`. The modules SHALL be loaded through the
existing validated, authenticated GitHub-contents path into the in-memory
`panopticon` package; the loader SHALL not require installation to disk or a
`PYTHONPATH` change.

#### Scenario: Real recovery module imports the provider registry

- **GIVEN** an uncustomized instance installer delegates to the template's
  bootstrap payload and the fetched recovery module imports
  `INSTANCE_CREDENTIAL_ACTION` from `panopticon.providers`
- **WHEN** the public launcher loads the default payload
- **THEN** it registers `panopticon.providers` before evaluating
  `panopticon.recovery`, and the bootstrap begins without a
  `ModuleNotFoundError`

#### Scenario: Provider registry retrieval is invalid

- **GIVEN** the default bootstrap requires `panopticon.providers`
- **WHEN** the GitHub contents API returns an invalid provider-module payload
- **THEN** the launcher fails with its controlled invalid-payload error before
  executing the recovery or bootstrap modules

## ADDED Requirements

### Requirement: Bootstrap caller-renderer failures are contained before writes

The bootstrap installer SHALL load the caller renderer from the effective
`workflow_ref`. If that file is missing from the instance or cannot be
retrieved because the contents request returns HTTP 404 or a connection-level
`URLError`, bootstrap SHALL report that it is using the bundled caller renderer
and continue with the bundled `CALLER_WORKFLOWS`, renderer, and compatibility
revision. HTTP 401, 403, and other HTTP/API failures SHALL fail with a
controlled renderer-load diagnostic and SHALL NOT use the bundled renderer.
The fallback binding SHALL preserve the renderer tuple order so the
workflow-name collection remains iterable. Compilation, execution, missing
symbol, compatibility-callback, and workflow-rendering failures in the fetched
or bundled renderer SHALL return before downloading or writing managed child
resources, report `could not load instance caller renderer`, and omit a raw
traceback.

#### Scenario: Missing or unavailable fetched caller renderer uses the bundle

- **GIVEN** the selected instance ref has no retrievable `panopticon/callers.py`
- **WHEN** the bootstrap installer loads the caller renderer
- **THEN** it reports the bundled-renderer fallback and completes caller
  rendering with the bundled workflow-name tuple without a traceback

#### Scenario: Fetched caller renderer cannot be loaded

- **GIVEN** the selected instance ref returns invalid, syntax-invalid, or
  missing-symbol `panopticon/callers.py`
- **WHEN** the bootstrap installer loads the caller renderer
- **THEN** it prints a controlled renderer-load diagnostic without a traceback
  and performs no managed child writes

#### Scenario: Caller renderer authentication failure does not fall back

- **GIVEN** the selected instance ref returns HTTP 401 or 403 while fetching
  `panopticon/callers.py`
- **WHEN** the bootstrap installer loads the caller renderer
- **THEN** it reports a controlled renderer-load diagnostic, performs no
  managed child writes, and does not report or use the bundled-renderer
  fallback

#### Scenario: Caller renderer retrieval failure uses the bundle only when safe

- **GIVEN** the selected instance ref returns HTTP 404 or a connection-level
  `URLError` while fetching `panopticon/callers.py`
- **WHEN** the bootstrap installer loads the caller renderer
- **THEN** it reports the bundled-renderer fallback and continues with the
  bundled renderer tuple

#### Scenario: Fetched renderer exports a non-callable compatibility revision

- **GIVEN** the selected instance ref returns a caller renderer whose
  `caller_compatibility_revision` export is missing or non-callable
- **WHEN** bootstrap resolves the provider contract
- **THEN** it returns a controlled caller-renderer diagnostic and writes no
  managed skills, tooling, or workflow files

#### Scenario: Current bootstrap loads with a contract-complete caller fixture

- **GIVEN** a bootstrap regression fixture provides the current caller module's
  workflow tuple, renderer, and callable compatibility-revision export
- **WHEN** the current bootstrap source is loaded against that fixture without
  a Python-tooling manifest
- **THEN** bootstrap loads the callable entry point without an import error

#### Scenario: Fetched renderer raises while rendering a caller workflow

- **GIVEN** the fetched renderer exports a callable compatibility revision but
  raises while rendering a managed caller workflow
- **WHEN** bootstrap wires the child workflows
- **THEN** it returns a controlled caller-renderer diagnostic, writes no
  managed child resources, and emits no raw traceback

## ADDED Requirements

### Requirement: Instance-managed setup exposes the reviewed credential-action example

The public instance setup guide SHALL link to a reviewed credential-action
skeleton and explain that an instance owner must copy it to the fixed path,
replace only the organization-specific broker step, verify the region output,
and commit the action. The guide SHALL state that the action runs for the child
caller identity and accepts no credential value through Panopticon configuration.

#### Scenario: Instance owner enables instance-managed Bedrock credentials

- **WHEN** an owner selects the `instance-managed` credential mode
- **THEN** the setup guide provides the example link, fixed destination path,
  broker adaptation boundary, region-output contract, and validation step

#### Scenario: Public example is reviewed for secret safety

- **WHEN** the example and setup guide are checked into the public template
- **THEN** they contain placeholders or synthetic values only and do not accept,
  persist, or print credential values
