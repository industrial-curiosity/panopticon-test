# Specify bootstrap dependency closure tasks

## 1. Make default payload dependency loading explicit

- [x] 1.1 Update the default payload loader so every module imported at module
  scope by `panopticon.bootstrap`, including `panopticon.features`, is
  registered and evaluated before bootstrap execution.
- [x] 1.2 Preserve the existing validated GitHub-contents decoding,
  authenticated fetch path, synthetic package, and no-filesystem execution
  boundaries.

## 2. Add dependency-closure regression coverage

- [x] 2.1 Add a clean-process installer test that uses the real default
  bootstrap and direct dependency source and fails when a dependency is not
  registered.
- [x] 2.2 Assert that dependency modules are fetched and evaluated before
  `panopticon.bootstrap`, including the feature registry dependency.
- [x] 2.3 Ensure the test fixture cannot pass because `panopticon.*` modules
  were imported earlier by the test process.

## 3. Cover feature-enabled public bootstrap

- [x] 3.1 Add an OKF-enabled public-installer scenario that reaches feature
  registry loading and feature artifact staging without an import error.
- [x] 3.2 Add a failure-path assertion naming the missing dependency when a
  feature-related default-payload module is omitted.

## 4. Verify and document the contract

- [x] 4.1 Run focused installer and feature tests plus the complete Python test
  suite.
- [x] 4.2 Validate the modified OpenSpec capabilities and all Markdown
  artifacts in strict mode.
- [x] 4.3 Review README.md and update docs/spec.md to reflect any user-facing or architectural changes introduced by this change; README.md required no change because setup and project orientation are unchanged
