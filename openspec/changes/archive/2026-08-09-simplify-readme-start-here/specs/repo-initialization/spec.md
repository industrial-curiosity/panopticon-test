# Repository initialization README orientation

## MODIFIED Requirements

### Requirement: README provides concise project orientation

The README SHALL provide a quickly scannable overview of the project's purpose,
repository roles, primary workflow, and links to the setup guide and other
detailed documentation. It SHALL use clear sections that separate at-a-glance
orientation from navigation. Its `Start here` section SHALL be a readable,
user-focused introduction that explains what Panopticon does, identifies the
first setup action, states the supported authentication expectation, and links
to the authoritative setup and provider guides. The `Start here` section SHALL
use short paragraphs and/or lists rather than a dense wall of text. Detailed
setup instructions, configuration reference, implementation inventories,
provider internals, compatibility or migration mechanics, and operational
recovery procedures SHALL live in purpose-named documentation files rather
than in the README. The README SHALL NOT include temporary implementation
status, incomplete-work notes, or feature-wiring details. At the top of the
README, it SHALL retain the project logo and an obvious link to the
organization's architecture documentation. At the end of the README, it SHALL
display a thumbnail for the specified Panopticon YouTube video that opens
`https://www.youtube.com/watch?v=sIJ9XhBSkI8` in a new browser tab or window.

#### Scenario: New maintainer opens the README

- **WHEN** a maintainer reads the README for the first time
- **THEN** they can understand Panopticon's purpose, the template/instance/child
  roles, and the primary lifecycle at a glance, then follow clearly labelled
  links for setup and deeper reference

#### Scenario: Start Here gives a first action

- **WHEN** a prospective user reads the README's `Start here` section
- **THEN** they can identify the first setup action, the public launcher command,
  the supported authentication expectation, and the guide that contains the
  complete setup procedure without reading an implementation reference

#### Scenario: Start Here remains readable

- **WHEN** a reviewer scans the README's `Start here` section
- **THEN** the section is composed of short paragraphs and/or lists with visible
  actions and links, and does not present onboarding as one dense implementation
  detail block

#### Scenario: Detailed setup or implementation is needed

- **WHEN** a reader needs instructions for configuring an instance, selecting a
  provider, synchronizing a template, recovering from an operational failure,
  or understanding caller compatibility
- **THEN** the README directs them to a purpose-named guide instead of embedding
  the detailed procedure or mechanism in `Start here`

#### Scenario: Maintainer finds the organization architecture

- **WHEN** a maintainer opens the README
- **THEN** they see the project logo and an obvious link to
  `docs/architecture.md` before the detailed orientation and navigation sections

#### Scenario: A feature has incomplete automation

- **WHEN** an implementation detail or workflow integration is incomplete
- **THEN** the README does not include its status, workaround, or follow-up
  description

#### Scenario: Reader reaches the end of the README

- **WHEN** a reader reaches the end of the README
- **THEN** they see the thumbnail at
  `https://img.youtube.com/vi/sIJ9XhBSkI8/hqdefault.jpg` in an anchor with
  `target="_blank"` that opens
  `https://www.youtube.com/watch?v=sIJ9XhBSkI8` in a new browser tab or window
