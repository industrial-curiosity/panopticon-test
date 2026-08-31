# OKF Documentation Spec

## Purpose

Define the template documentation bundle and the feature-controlled OKF
generation and validation behavior.

## Requirements

### Requirement: Template documentation is an OKF bundle

The template `docs/` tree SHALL be maintained as an OKF v0.1 bundle regardless
of instance feature mode. Every non-reserved Markdown concept document SHALL
start with constrained YAML frontmatter containing a non-empty `type` field.
Root and nested `index.md` files SHALL provide progressive-disclosure
listings, and any `log.md` SHALL use date-grouped update entries. Test-only
Markdown fixtures SHALL live outside the documentation bundle.

#### Scenario: Disabled instance inherits template documentation

- **WHEN** an instance has the OKF feature disabled
- **THEN** its forked template documentation remains valid OKF Markdown without
  enabling OKF generation, validation, or CI enforcement

### Requirement: OKF feature controls generation and enforcement

The registered OKF feature SHALL provide feature-owned agent skills, templates,
and deterministic helpers for generated child documentation. In enabled modes,
generated concept documents SHALL use the feature's constrained YAML
frontmatter profile and deterministic interface documentation SHALL preserve
its index-derived content beneath that frontmatter. The feature SHALL not cause
CI to rewrite documentation.

#### Scenario: OKF-enabled child generates interface documentation

- **WHEN** a child bootstrapped from an OKF-enabled instance regenerates
  interface documentation
- **THEN** `interfaces.md` has valid feature frontmatter and its body reflects
  exactly the local interface index

#### Scenario: OKF is disabled after prior enablement

- **WHEN** an instance disables OKF
- **THEN** shared workflows and initialization skip OKF conformance enforcement
  even if a child retains its prior Markdown until cleanup or a later migration

### Requirement: OKF conformance validation is deterministic

The OKF helper SHALL validate the feature's constrained frontmatter grammar,
required non-empty `type` field, and reserved index/log structures using only
the Python standard library. It SHALL not claim to parse arbitrary YAML or
accept malformed frontmatter as conformant.

#### Scenario: Missing type fails blocking validation

- **GIVEN** a non-reserved Markdown concept lacks a non-empty `type` field
- **WHEN** an OKF-enabled instance runs blocking validation
- **THEN** validation fails and names the offending document
