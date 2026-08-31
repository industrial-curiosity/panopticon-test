# Simplify the README Start Here section

## Why

The README's `Start here` section has become an implementation-heavy wall of
text. It makes the project difficult to understand at a glance and repeats
details that belong in the linked setup and provider documentation, delaying a
new user's path to the first useful command.

## What Changes

- Replace the implementation-heavy `Start here` content with a short,
  scannable introduction to Panopticon's purpose and repository roles.
- Keep the minimum onboarding path in the README: where to begin, the public
  launcher command, required authentication, and where to find the detailed
  setup guide.
- Move or remove details that are already owned by linked documentation,
  including provider rollout internals, caller compatibility and migration
  behavior, and operational recovery specifics.
- Strengthen the README documentation requirements so future introductions
  prioritize project orientation and getting started over implementation detail.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `repo-initialization`: refine the README orientation requirement to define a
  readable Start Here section with concise purpose, first steps, and links to
  detailed guides, while excluding duplicated implementation and operational
  detail.

## Impact

This affects `README.md` and the repository-initialization OpenSpec
requirements, with corresponding proposal/design/task documentation. It
changes no runtime behavior, APIs, workflows, dependencies, or generated child
repository behavior.
