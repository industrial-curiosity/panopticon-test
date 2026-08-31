# Bootstrap dependency closure design

## Context

The public `install.py` launcher executes an instance installer in the current
process. An uncustomized instance installer delegates to the template's
default bootstrap, which the launcher fetches as Python source and evaluates in
an in-memory synthetic `panopticon` package. The loader currently registers
those modules explicitly, so a new module-scope import in `bootstrap.py` can
create a missing dependency unless the loader and tests are updated together.

The OKF feature package exposed this gap: `bootstrap.py` imported
`panopticon.features`, but the loader registered only the previously known
provider, recovery, and caller modules. Existing tests used partial fakes and
did not exercise this import in a clean module environment.

## Goals / Non-Goals

**Goals:**

- Make dependency closure and topological evaluation an explicit bootstrap
  contract.
- Require real-source, clean-process coverage for the fetched default payload.
- Cover enabled feature-package startup through the public installer boundary.
- Preserve checkout-and-run execution with no disk installation, `PYTHONPATH`
  mutation, or third-party dependency.

**Non-Goals:**

- Redesign the installer around a package archive or dependency resolver.
- Change feature modes, artifact selection, or bootstrap configuration
  semantics.
- Require customized instance installers to use the template's loader.

## Decisions

### Keep explicit in-memory registration, but specify its completeness

The loader will continue to register fetched modules in the synthetic package.
This preserves the existing authentication, decoding, and no-filesystem
execution boundary. The specification will require every module imported at
module scope by the default bootstrap, including transitive relative imports,
to be registered before bootstrap evaluation.

An automatic import-graph resolver was considered, but it would add parser and
execution complexity to a standard-library-only launcher and could obscure the
validated GitHub fetch boundary. Explicit registration remains simpler; the
real-source smoke test is the guard against omissions.

### Test the dependency boundary with real source

The installer regression fixture will provide the real source for the default
bootstrap and its direct dependencies, while using transport fakes for GitHub.
The test will clear or isolate `panopticon.*` modules so ambient imports cannot
hide a missing registration. A small fake bootstrap remains appropriate for
asserting load order, but it must import the newly covered dependency.

### Exercise feature startup through the launcher

The feature-package requirement will include a scenario in which an
OKF-enabled instance reaches feature artifact installation through the public
installer/default-payload path. This complements local feature lifecycle tests
without duplicating their artifact semantics.

## Risks / Trade-offs

- [Risk] Explicit registration can become incomplete again when bootstrap
  imports change → [Mitigation] require dependency-closure coverage using real
  source and a clean module environment.
- [Risk] A full real-source fixture may be more sensitive to unrelated module
  imports → [Mitigation] keep transport and filesystem inputs hermetic and
  assert only the loader boundary and resulting startup behavior.
- [Risk] Customized installers may have different dependency graphs →
  [Mitigation] scope the contract to the template default payload; customized
  installers retain control of their own execution.

## Migration Plan

Update the existing repository-initialization and instance-feature-packages
requirements, then land the loader and regression-test changes together.
Instances receive the corrected launcher when they sync the template and can
rerun bootstrap; no configuration migration is required.

## Open Questions

None. The existing in-memory loader and standard-library constraints determine
the implementation boundary.
