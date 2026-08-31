# Repository Initialization Spec Delta

## MODIFIED Requirements

### Requirement: Default bootstrap payload loads its import dependencies

The default payload loader SHALL register every module in the complete relative
import dependency closure of `panopticon.bootstrap` before evaluating the
bootstrap module. It SHALL evaluate those modules in dependency order,
including `panopticon.providers` before modules that import it and
`panopticon.features` before bootstrap. The modules SHALL be loaded through the
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

#### Scenario: Default bootstrap imports the feature registry

- **GIVEN** the default bootstrap imports `panopticon.features` at module
  scope
- **WHEN** the public launcher loads the default payload in a clean process
- **THEN** it fetches and registers `panopticon.features` before evaluating
  `panopticon.bootstrap`, and bootstrap begins without a
  `ModuleNotFoundError`

#### Scenario: A new bootstrap dependency is not silently omitted

- **GIVEN** a module in the default bootstrap dependency closure is absent from
  the loader's registration sequence
- **WHEN** the clean-process real-source bootstrap integration test runs
- **THEN** the test fails with the missing module or dependency diagnostic
  instead of passing because that module was already imported by the test
  process

#### Scenario: Provider registry retrieval is invalid

- **GIVEN** the default bootstrap requires `panopticon.providers`
- **WHEN** the GitHub contents API returns an invalid provider-module payload
- **THEN** the launcher fails with its controlled invalid-payload error before
  executing the recovery or bootstrap modules
