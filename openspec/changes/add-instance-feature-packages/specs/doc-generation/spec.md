# Doc generation delta

## ADDED Requirements

### Requirement: Feature-controlled OKF generation

Panopticon documentation generation SHALL use the installed OKF skill and
templates when the effective OKF feature mode is advisory or blocking. It SHALL
then produce constrained YAML frontmatter with a non-empty `type` field for each
non-reserved generated concept document, generate required progressive-disclosure
indexes, and preserve deterministic interface-doc content. When the feature is
disabled, existing four-layer generation requirements SHALL continue without
requiring OKF feature artifacts or validation.

#### Scenario: Enabled generation creates an OKF component document

- **WHEN** an OKF-enabled child generates a component document
- **THEN** the document has the feature-defined frontmatter and follows the
  existing component template body structure

#### Scenario: Disabled generation remains compatible

- **WHEN** a child uses an instance with OKF disabled
- **THEN** documentation generation does not require the OKF skill, templates,
  indexes, or validator
