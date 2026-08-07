# Implementation tasks

## 1. Provider failure feedback

- [x] 1.1 Emit configuration-action and Bedrock failure annotations on stdout
  before their non-zero exits while retaining step summaries.
- [x] 1.2 Add structural tests that lock in stdout workflow-command emission.

## 2. Private-workflow access preflight

- [x] 2.1 Update public setup and operator guidance with the required token
  permissions, valid response field, and 403 recovery.
- [x] 2.2 Add structural documentation tests for the preflight contract.

## 3. Verification

- [x] 3.1 Run focused workflow tests, contract validation, strict OpenSpec
  validation for this change, and Markdown linting.
