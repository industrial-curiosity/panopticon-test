# Complete Bedrock onboarding hardening tasks

## 1. Bedrock model contract and configuration

- [x] 1.1 Extend the trusted Bedrock provider contract so `model` is optional for prerequisite reporting while preserving explicit organization Actions-name mapping and avoiding a global contract-version rollout.
- [x] 1.2 Add non-secret `model_default` handling to provider configuration workflows, the configuration action, and instance configuration persistence as `llm.defaults.model`; derive optional-name reporting from the trusted effective contract without persisting derived fields.
- [x] 1.3 Keep `job_timeout_minutes` fallback resolution in the reusable workflow, retain `configuration_defaults` as an optional ignored migration input in all provider reusable workflows, omit it from newly generated callers, tolerate legacy persisted defaults without using or re-persisting them, and preserve organization-admin control without child maintainer action.
- [x] 1.4 Add regression coverage proving legacy instance timeout defaults are ignored, old callers with `configuration_defaults` dispatch and reach the legacy gate or receive the designed recovery message, generated callers omit the input, ABI changes require bootstrap, and value-only, instance-resolved default, organization-variable, and shared-workflow fallback changes preserve caller compatibility.
- [x] 1.5 Isolate local sync's fetched caller-renderer loading, compatibility-call, and workflow-rendering boundaries so every non-system renderer exception produces the designed `could not load instance caller renderer` diagnostic before any managed resource writes, without relabeling provider-contract failures; ignore any stale local caller copy.
- [x] 1.6 Add configuration-action and sync regression tests for trusted optionality reporting without schema widening; missing/non-callable, syntax-invalid, execution-invalid, and workflow-rendering-invalid fetched renderers; stale or invalid local caller copies being replaced by the fetched renderer; pinned renderer refs; distinct provider-configuration errors; and non-relabeling unexpected provider-contract failures.
- [x] 1.7 Make bootstrap use the bundled caller workflow tuple, renderer, and compatibility callback only for an HTTP 404 or connection-level retrieval failure, while hard-failing other HTTP/API failures and preserving callback validation and pre-write render preview.
- [x] 1.8 Add bootstrap regression tests for safe fallback retrieval failures and HTTP 401/403 failures that must not use the bundled renderer, alongside the existing renderer failure coverage, asserting readable no-traceback diagnostics and no partial writes.
- [x] 1.9 Reject a non-empty CLI `--model-default` for non-Bedrock providers with a clear Bedrock-only message before configuration persistence, and add regression coverage for rejection and Bedrock acceptance.

## 2. Credential-action example and recovery

- [x] 2.1 Add `docs/examples/panopticon-aws-credentials/action.yml` with the fixed composite-action shape, placeholder organization broker step, and documented region-output contract.
- [x] 2.2 Extend shared credential recovery and the Bedrock workflow fallback with the example URL, fixed destination path, copyable `protected_paths` fragment, child-bootstrap command, and automatic-protection note, using the canonical fixed action path binding.
- [x] 2.3 Add recovery and public-safety tests covering formatter output, inline fallback markers, example content, absence of organization-specific identifiers or credential values, and canonical path binding.
- [x] 2.4 Update the Bedrock workflow and shared recovery code so the provider registry is the canonical Python path source and the workflow fallback uses one workflow-level path binding.
- [x] 2.5 Reuse the shared credential-action recovery formatter from bootstrap's missing-action validation, preserving the trusted provider path and adding regression coverage for the example URL, fixed destination, protection fragment, automatic-protection note, rerun command, and source-safe output.

## 3. Automatic template-sync protection

- [x] 3.1 Centralize derivation of generated, provider-derived, and organization-declared protected paths using the exact Bedrock `instance-managed` contract condition and tolerate a non-object configuration input.
- [x] 3.2 Apply the derived credential-action path through runtime `merge.ours` attributes in hosted sync and generated local recovery instructions, with separate step-summary sections.
- [x] 3.3 Add structural and real-git regression coverage proving the fixed action survives routine and first-time sync only for the trusted instance-managed mode, plus defensive non-object configuration coverage.

## 4. Rollout and provider guidance

- [x] 4.1 Update setup and provider-configuration guides with the credential-action example, model-default path, organization-admin job-timeout control, complete inference-profile IAM permissions, and exact Gate-1 access-policy mutation command.
- [x] 4.2 Update getting-started/testing guidance and workflow summaries so the new recovery paths, ownership boundaries, and source-safe diagnostics are consistent.
- [x] 4.3 Update the affected OpenSpec source specifications with the renderer-owned caller-compatibility requirement, explicit classification of ABI changes versus fallback and value-only changes, dispatch-reachable legacy compatibility during migration, separate full-contract/legacy fingerprints, organization-admin job-timeout control, and shared-workflow timeout fallback boundary, while keeping public examples placeholder-safe.

## 5. Verification

- [x] 5.1 Run focused caller-compatibility and bootstrap fallback regression tests and the relevant standard-library test suite after adding HTTP authentication-failure coverage.
- [x] 5.2 Run strict OpenSpec validation and Markdown structure/lint checks after updating the migration requirements, design, and caller-fixture scenario.
- [x] 5.3 Review README.md and docs/spec.md for the bootstrap/fallback/value-only classification and dispatch-reachable migration behavior, and update them if stale.

## 6. Reviewer follow-up

- [x] 6.1 Add resolver and provider-workflow regression tests proving `legacy_revision` preserves pre-change `job_timeout_minutes` defaults, drops only the newly introduced Bedrock `model` default, equals the pre-change full-contract hash, and lets a pre-change caller with `configuration_defaults` reach the migration gate.
- [x] 6.2 Codify the invariant that instance-owned operational controls must resolve at an instance/reusable-workflow boundary and must not require child-repository maintainer action.
- [x] 6.3 Add a provider-workflow regression assertion that `PANOPTICON.md` links to `docs/setup-guide.md` as the authoritative four-gate rollout guide.

## 7. Default payload import ordering

- [x] 7.1 Register and execute the fetched default payload modules in dependency order so `panopticon.providers` is available before `panopticon.recovery`.
- [x] 7.2 Add a regression test that uses the real `panopticon/recovery.py` source and proves the default payload loads without `ModuleNotFoundError`.
