"""Validate and generate a deterministic, non-secret Panopticon instance overlay.

The profile is deliberately an authoring format, not a second provider contract.  Provider
workflows, mappings, permissions, fixed action paths, and compatibility revisions continue to
come from :mod:`panopticon.providers` and :mod:`panopticon.callers`.
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

from .callers import CALLER_WORKFLOWS, caller_workflow_text
from .config import CHECK_TYPES, DEFAULT_GATING, GENERATED_PROTECTED_PATHS
from .providers import (
    INSTANCE_CREDENTIAL_ACTION,
    RUNTIME_OPTIONAL_VARIABLES,
    TEMPLATE_DEFAULTS,
    ProviderConfigError,
    resolve_provider_contract,
    validate_actions_name,
)


PROFILE_SCHEMA_VERSION = 1
OVERLAY_MANIFEST_VERSION = 1
GENERATOR_VERSION = "1"
PROFILE_SCHEMA_PATH = Path("templates") / "complex-organization" / "profile.schema.json"
INSTANCE_CHECKLIST_PATH = Path("docs") / "complex-organization-instance-checklist.md"
CHILD_CHECKLIST_PATH = Path("docs") / "complex-organization-child-onboarding.md"
DEBT_REGISTER_PATH = Path("docs") / "complex-organization-protected-path-debt.md"

_ACTION_REF_RE = re.compile(
    r"^(?P<owner>[A-Za-z0-9_.-]+)/(?P<repo>[A-Za-z0-9_.-]+)"
    r"(?:/(?P<path>[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*))?@"
    r"(?P<revision>[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*|[0-9a-fA-F]{40})$"
)
_PLACEHOLDER_RE = re.compile(
    r"(?:\$\{|\{\{|<[^>]+>|\b(?:YOUR(?:[-_][A-Z0-9]+)+|REPLACE[-_]?(?:ME|THIS)|CHANGE[-_]?(?:ME|THIS)|TODO|CHANGEME)\b|\.\.\.)",
    re.IGNORECASE,
)
_CREDENTIAL_RE = re.compile(
    r"(?:-----BEGIN [^-]*PRIVATE KEY-----|\b(?:gh[pousr][_-]|github_pat[_-]|glpat-|sk-)[A-Za-z0-9_-]+|"
    r"\b(?:AKIA|ASIA|AIDA|AROA)[0-9A-Z]{16}\b|\b(?:access[_-]?key|secret|token|password|api[_-]?key)\s*[:=]\s*[^\s,}]+)",
    re.IGNORECASE,
)
_PUBLIC_URL_RE = re.compile(r"^https://(?:[A-Za-z0-9-]+\.)?(?:example\.com|example\.org|example\.net|example\.test)(?:/|$)")

_PROFILE_FIELDS = {
    "schema_version",
    "provider",
    "credential_mode",
    "names",
    "defaults",
    "default_sources",
    "identity",
    "broker",
    "workflow_access",
    "child_identity",
    "internal_registries",
    "gating",
    "protected_paths",
    "workflow_ref",
}
_NAMES_FIELDS = {"secrets", "variables"}
_IDENTITY_FIELDS = {"role_reference", "child_provisioning_reference"}
_BROKER_FIELDS = {"action", "region_output"}
_ACCESS_FIELDS = {"policy", "diagnostic_url"}
_CHILD_IDENTITY_FIELDS = {"instructions", "diagnostic_url"}
_DEBT_FIELDS = {
    "path",
    "reason",
    "owner",
    "upstream_replacement",
    "last_reconciliation",
    "removal_condition",
}
_DEFAULT_SOURCES = {
    "organization-variable",
    "instance-action",
    "instance-config",
    "workflow-default",
}


class OrganizationTemplateError(ValueError):
    """A profile, overlay, or apply preflight is invalid."""


def _canonical_json(value):
    return json.dumps(value, indent=2, sort_keys=True, separators=(",", ": ")) + "\n"


def _digest_bytes(value):
    return hashlib.sha256(value).hexdigest()


def _digest_text(value):
    return _digest_bytes(value.encode("utf-8"))


def _unknown_fields(value, allowed, path):
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise OrganizationTemplateError(f"{path} has unknown fields: {unknown}")


def _object(value, path):
    if not isinstance(value, dict):
        raise OrganizationTemplateError(f"{path} must be an object")
    return value


def _nonempty_string(value, path, *, public=False, url=False):
    if not isinstance(value, str) or not value.strip():
        raise OrganizationTemplateError(f"{path} must be a non-empty string")
    if _PLACEHOLDER_RE.search(value):
        raise OrganizationTemplateError(f"{path} contains an unresolved placeholder")
    if _CREDENTIAL_RE.search(value):
        raise OrganizationTemplateError(f"{path} contains a credential-looking value")
    if public and url and not _PUBLIC_URL_RE.match(value):
        raise OrganizationTemplateError(f"{path} must use a reserved example URL in a public profile")
    return value


def _list_of_strings(value, path, *, public=False):
    if not isinstance(value, list):
        raise OrganizationTemplateError(f"{path} must be an array")
    return [_nonempty_string(item, f"{path}[{index}]", public=public) for index, item in enumerate(value)]


def _validate_name(value, path):
    _nonempty_string(value, path)
    try:
        return validate_actions_name(value, path)
    except ProviderConfigError as exc:
        raise OrganizationTemplateError(f"{path}: {exc}") from exc


def _validate_path(value, path):
    value = _nonempty_string(value, path)
    candidate = Path(value)
    if not candidate.parts or candidate.is_absolute() or ".." in candidate.parts or "\\" in value:
        raise OrganizationTemplateError(f"{path} must be a repository-relative path")
    return value


def _validate_action_reference(value, path):
    value = _nonempty_string(value, path)
    match = _ACTION_REF_RE.fullmatch(value)
    if not match:
        raise OrganizationTemplateError(
            f"{path} must be a GitHub Action reference owner/repository[/path]@branch, tag, or 40-character commit SHA"
        )
    return value


def _scan_public_identifiers(value, path):
    if isinstance(value, dict):
        for key, item in value.items():
            _scan_public_identifiers(item, f"{path}.{key}")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _scan_public_identifiers(item, f"{path}[{index}]")
        return
    if not isinstance(value, str):
        return
    if value.startswith("arn:aws:iam::") and "123456789012" not in value:
        raise OrganizationTemplateError(f"{path} contains a non-synthetic AWS account identifier")
    if value.startswith("https://") and not _PUBLIC_URL_RE.match(value):
        raise OrganizationTemplateError(f"{path} contains a non-reserved URL in a public profile")
    lowered = value.lower()
    if any(marker in lowered for marker in ("acme", "yotpo", "private-instance", "industrial-curiosity")):
        raise OrganizationTemplateError(f"{path} contains an organization-specific identifier")


def _profile_provider_input(profile, names, defaults):
    provider = profile["provider"]
    input_config = {
        "provider": provider,
        "secrets": names["secrets"],
        "variables": names["variables"],
        "defaults": defaults,
    }
    if provider == "bedrock":
        input_config["credential_mode"] = profile.get("credential_mode") or "github-oidc"
    return input_config


def _validate_identity(profile, public):
    identity = _object(profile.get("identity"), "identity")
    _unknown_fields(identity, _IDENTITY_FIELDS, "identity")
    mode = profile.get("credential_mode") or "github-oidc"
    if mode == "github-oidc" and not identity.get("role_reference"):
        raise OrganizationTemplateError("identity.role_reference is required for github-oidc")
    if mode == "instance-managed" and identity.get("role_reference") is not None:
        raise OrganizationTemplateError("identity.role_reference is only valid for github-oidc")
    if identity.get("role_reference") is not None:
        _nonempty_string(identity["role_reference"], "identity.role_reference", public=public)
    _nonempty_string(
        identity.get("child_provisioning_reference"),
        "identity.child_provisioning_reference",
        public=public,
    )
    child_identity = _object(profile.get("child_identity"), "child_identity")
    _unknown_fields(child_identity, _CHILD_IDENTITY_FIELDS, "child_identity")
    _nonempty_string(child_identity.get("instructions"), "child_identity.instructions", public=public)
    _nonempty_string(
        child_identity.get("diagnostic_url"),
        "child_identity.diagnostic_url",
        public=public,
        url=True,
    )


def _validate_access(profile, public):
    access = profile.get("workflow_access")
    if access is None:
        return {"policy": "organization-approved", "diagnostic_url": None}
    access = _object(access, "workflow_access")
    _unknown_fields(access, _ACCESS_FIELDS, "workflow_access")
    policy = _nonempty_string(access.get("policy"), "workflow_access.policy", public=public)
    diagnostic_url = access.get("diagnostic_url")
    if diagnostic_url is not None:
        diagnostic_url = _nonempty_string(
            diagnostic_url, "workflow_access.diagnostic_url", public=public, url=True
        )
    return {"policy": policy, "diagnostic_url": diagnostic_url}


def _validate_debt(profile, public, reserved_paths=()):
    entries = profile.get("protected_paths", [])
    if not isinstance(entries, list):
        raise OrganizationTemplateError("protected_paths must be an array")
    normalized = []
    seen = set()
    for index, entry in enumerate(entries):
        path = f"protected_paths[{index}]"
        entry = _object(entry, path)
        _unknown_fields(entry, _DEBT_FIELDS, path)
        item = {
            field: _nonempty_string(entry.get(field), f"{path}.{field}", public=public)
            for field in _DEBT_FIELDS
            if field != "path"
        }
        item["path"] = _validate_path(entry.get("path"), f"{path}.path")
        if any(Path(item["path"]) == Path(reserved) for reserved in reserved_paths):
            raise OrganizationTemplateError(
                f"{path}.path is a derived protected path and cannot be organization-declared"
            )
        if item["path"] in seen:
            raise OrganizationTemplateError(f"{path}.path duplicates another protected path")
        seen.add(item["path"])
        normalized.append({field: item[field] for field in sorted(item)})
    return normalized


def _validate_defaults(profile, contract):
    defaults = profile.get("defaults", {})
    sources = profile.get("default_sources", {})
    if not isinstance(defaults, dict):
        raise OrganizationTemplateError("defaults must be an object")
    if not isinstance(sources, dict):
        raise OrganizationTemplateError("default_sources must be an object")
    allowed = set(contract["optional_variables"])
    for logical in sorted(set(defaults) | set(sources)):
        if logical not in allowed:
            raise OrganizationTemplateError(f"default field {logical!r} is not an optional provider logical name")
        source = sources.get(logical)
        if source not in _DEFAULT_SOURCES:
            raise OrganizationTemplateError(
                f"default_sources.{logical} must name one of {sorted(_DEFAULT_SOURCES)}"
            )
        value = defaults.get(logical)
        if value is not None:
            _nonempty_string(value, f"defaults.{logical}", public=False)
        if source == "instance-config" and value is None:
            raise OrganizationTemplateError(
                f"default_sources.{logical} promises instance-config but defaults.{logical} is absent"
            )
        if source != "instance-config" and value is not None:
            raise OrganizationTemplateError(
                f"defaults.{logical} must be omitted when its source is {source}"
            )
        if source == "instance-action" and logical not in RUNTIME_OPTIONAL_VARIABLES:
            raise OrganizationTemplateError(
                f"default_sources.{logical} promises the fixed instance action, which does not provide that logical value"
            )
        if source == "workflow-default" and logical not in TEMPLATE_DEFAULTS:
            raise OrganizationTemplateError(
                f"default_sources.{logical} promises a workflow default that is not registered"
            )
    for logical, value in defaults.items():
        if logical not in sources:
            raise OrganizationTemplateError(f"default_sources.{logical} is required for defaults.{logical}")
        if logical == "job_timeout_minutes" and sources[logical] == "instance-config":
            raise OrganizationTemplateError(
                "job_timeout_minutes cannot use an instance-config default; GitHub resolves it before steps run"
            )
    return {logical: defaults[logical] for logical in defaults if sources[logical] == "instance-config"}


def _validate_names(profile, contract):
    names = profile.get("names", {})
    if names is None:
        names = {}
    names = _object(names, "names")
    _unknown_fields(names, _NAMES_FIELDS, "names")
    normalized = {"secrets": {}, "variables": {}}
    for kind in normalized:
        values = names.get(kind, {})
        if not isinstance(values, dict):
            raise OrganizationTemplateError(f"names.{kind} must be an object")
        allowed = set(contract[kind])
        unknown = sorted(set(values) - allowed)
        if unknown:
            raise OrganizationTemplateError(
                f"names.{kind} contains unknown logical names: {unknown}"
            )
        normalized[kind] = {
            logical: _validate_name(value, f"names.{kind}.{logical}")
            for logical, value in sorted(values.items())
        }
    return normalized


def validate_profile(profile, *, public=False):
    """Validate a decoded profile and return normalized profile, config, and contract data."""
    profile = _object(profile, "profile")
    _unknown_fields(profile, _PROFILE_FIELDS, "profile")
    if profile.get("schema_version") != PROFILE_SCHEMA_VERSION:
        raise OrganizationTemplateError(
            f"schema_version must be {PROFILE_SCHEMA_VERSION}, got {profile.get('schema_version')!r}"
        )
    provider = profile.get("provider")
    if not isinstance(provider, str) or not provider.strip():
        raise OrganizationTemplateError("provider must be a non-empty trusted provider name")
    mode = profile.get("credential_mode")
    if provider == "bedrock":
        mode = mode or "github-oidc"
    elif mode is not None:
        raise OrganizationTemplateError("credential_mode is supported only for bedrock")

    provisional = {"provider": provider, **({"credential_mode": mode} if mode else {})}
    try:
        base_contract = resolve_provider_contract(provisional)
    except ProviderConfigError as exc:
        raise OrganizationTemplateError(f"provider contract: {exc}") from exc
    names = _validate_names(profile, base_contract)
    raw_defaults = profile.get("defaults", {})
    raw_sources = profile.get("default_sources", {})
    if not isinstance(raw_defaults, dict):
        raise OrganizationTemplateError("defaults must be an object")
    if not isinstance(raw_sources, dict):
        raise OrganizationTemplateError("default_sources must be an object")
    defaults_for_contract = {
        logical: value
        for logical, value in raw_defaults.items()
        if raw_sources.get(logical) == "instance-config"
    }
    try:
        contract = resolve_provider_contract(
            _profile_provider_input(profile, names, defaults_for_contract)
        )
    except (ProviderConfigError, AttributeError, TypeError) as exc:
        raise OrganizationTemplateError(f"provider contract: {exc}") from exc

    normalized_defaults = _validate_defaults(profile, contract)
    _validate_identity(profile, public)
    access = _validate_access(profile, public)
    reserved_paths = list(GENERATED_PROTECTED_PATHS)
    if contract.get("credential_action"):
        reserved_paths.append(contract["credential_action"])
    debt = _validate_debt(profile, public, reserved_paths=reserved_paths)
    internal_registries = _list_of_strings(
        profile.get("internal_registries", []), "internal_registries", public=public
    )
    gating = dict(DEFAULT_GATING)
    configured_gating = profile.get("gating", {})
    configured_gating = _object(configured_gating, "gating")
    for check, value in configured_gating.items():
        if check not in CHECK_TYPES:
            raise OrganizationTemplateError(f"gating.{check} is not a supported check type")
        if value not in {"blocking", "advisory"}:
            raise OrganizationTemplateError(f"gating.{check} must be blocking or advisory")
        gating[check] = value
    workflow_ref = profile.get("workflow_ref")
    if workflow_ref is not None:
        workflow_ref = _nonempty_string(workflow_ref, "workflow_ref", public=public)

    broker = None
    if mode == "instance-managed":
        broker = _object(profile.get("broker"), "broker")
        _unknown_fields(broker, _BROKER_FIELDS, "broker")
        broker = {
            "action": _validate_action_reference(broker.get("action"), "broker.action"),
            "region_output": _validate_name(broker.get("region_output"), "broker.region_output"),
        }
    elif profile.get("broker") is not None:
        raise OrganizationTemplateError("broker is valid only for bedrock instance-managed profiles")

    org_config = {
        "schema_version": 1,
        "gating": gating,
        "workflow_ref": workflow_ref,
        "protected_paths": [entry["path"] for entry in debt],
        "internal_registries": internal_registries,
        "llm": {
            "provider": contract["provider"],
            **({"credential_mode": contract["credential_mode"]} if contract.get("credential_mode") else {}),
            "secrets": contract["secrets"],
            "variables": contract["variables"],
            **({"defaults": normalized_defaults} if normalized_defaults else {}),
        },
    }
    if public:
        _scan_public_identifiers(profile, "profile")
    return {
        "profile": profile,
        "contract": contract,
        "org_config": org_config,
        "workflow_access": access,
        "protected_paths": debt,
        "broker": broker,
    }


def load_profile(path, *, public=False):
    """Load and validate one profile without writing anything."""
    path = Path(path)
    try:
        profile = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise OrganizationTemplateError(f"profile not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise OrganizationTemplateError(f"profile is not valid JSON: {exc}") from exc
    return validate_profile(profile, public=public)


def _render_wrapper(broker):
    action = broker["action"]
    region_output = broker["region_output"]
    return (
        "name: Panopticon AWS credentials (generated instance-managed wrapper)\n"
        "description: >-\n"
        "  Generated fixed-path wrapper. The broker reference is the only organization-selected\n"
        "  runtime action and receives no credential value from Panopticon.\n\n"
        "outputs:\n"
        "  aws_region:\n"
        "    description: AWS region selected by the organization broker\n"
        "    value: ${{ steps.validate-region.outputs.aws_region }}\n\n"
        "runs:\n"
        "  using: composite\n"
        "  steps:\n"
        "    - id: organization-broker\n"
        f"      uses: {action}\n"
        "\n"
        "    - id: validate-region\n"
        "      name: Validate the broker region output\n"
        "      shell: bash\n"
        "      env:\n"
        f"        BROKER_REGION: ${{{{ steps.organization-broker.outputs.{region_output} }}}}\n"
        "      run: |\n"
        "        set -euo pipefail\n"
        "        region=\"${BROKER_REGION:-}\"\n"
        "        if [[ -z \"${region//[[:space:]]/}\" ]]; then\n"
        f"          echo \"::error::The broker must provide its {region_output} output\"\n"
        "          exit 1\n"
        "        fi\n"
        "        echo \"PANOPTICON_AWS_REGION=$region\" >> \"$GITHUB_ENV\"\n"
        "        echo \"aws_region=$region\" >> \"$GITHUB_OUTPUT\"\n"
    )


def _render_instance_checklist(validated):
    profile = validated["profile"]
    contract = validated["contract"]
    access = validated["workflow_access"]
    provider = contract["provider"]
    access_url = access["diagnostic_url"] or "Use the GitHub Actions run and repository settings for the private instance."
    return f"""# Generated instance onboarding checklist

Run this checklist in order. It covers instance-wide work only; child identity
and per-child provisioning are in the separate child checklist.

## Gate 1 — reusable-workflow access

- Symptom: a child cannot create the reusable provider job.
- Evidence: the child run shows the selected `{contract['workflow']}` job and the
  instance repository allows the child repository to call it.
- Owner: instance administrators; access policy: `{access['policy']}`.
- Recovery: verify Actions access and rerun the generated profile validation:
  `python3 -m panopticon.organization_template validate PROFILE`.
- Proof to advance: a disposable child dispatch reaches the provider workflow.
- Rerun: repeat the validation and review the generated overlay before applying it.
- Diagnostic reference: {access_url}

## Gate 2 — effective provider configuration

- Symptom: provider preflight reports missing configured names or a stale caller
  compatibility revision.
- Evidence: `panopticon.config.json` loads through the trusted provider contract;
  configured names are present as Actions names only.
- Owner: instance administrators.
- Recovery: run the provider configuration workflow or generate a fresh overlay,
  then use `python3 -m panopticon.organization_template apply OVERLAY --instance-root INSTANCE --check`.
- Proof to advance: the effective configuration summary resolves values before
  provider preflight without printing values.
- Rerun: re-run `apply --check`, then apply the unchanged reviewed overlay.

## Review and apply

```bash
python3 -m panopticon.organization_template validate PROFILE
python3 -m panopticon.organization_template generate PROFILE --instance-root INSTANCE --output OVERLAY
python3 -m panopticon.organization_template apply OVERLAY --instance-root INSTANCE --check
python3 -m panopticon.organization_template apply OVERLAY --instance-root INSTANCE
```

Review `overlay-manifest.json`, the generated files, protection ownership, and
the computed provider/caller revisions before the explicit apply. Commit the
reviewed instance changes using the normal instance workflow.

## Reference

- Provider: `{provider}`
- Credential mode: `{contract.get('credential_mode') or 'none'}`
- Provider workflow and fixed paths come from the trusted template registry.
- The generated profile contains names and non-secret references only.
- Provider recovery: use `docs/provider-configuration.md` and the selected
  provider workflow; do not create a second provider-resolution path.
- Initialization recovery: inspect `panopticon-initialization-report.md`, then
  rerun `python3 -m panopticon.init_repo --instance INSTANCE` after child fixes.
- Tooling-currency recovery: run `python3 -m panopticon.tooling_currency` and
  keep its generated, provider-derived, and organization-declared path reports
  separate.
- Four-gate recovery: use the child checklist and the source-safe
  `panopticon.recovery` summaries for the last proven gate.
"""


def _render_child_checklist(validated):
    contract = validated["contract"]
    profile = validated["profile"]
    child_identity = profile["child_identity"]
    identity = profile["identity"]
    mode = contract.get("credential_mode") or "none"
    role_line = (
        f"- Direct role reference: `{identity['role_reference']}`.\n"
        if identity.get("role_reference")
        else "- Credential mode delegates the role to the fixed instance-managed wrapper.\n"
    )
    return f"""# Generated child onboarding checklist

Run this checklist for each child repository after the instance checklist has
passed. The caller repository owns its identity; a reusable workflow does not
transfer the caller's identity.

## Gate 1 — reusable-workflow access

- Symptom: the child workflow is rejected before a reusable job starts.
- Evidence: the child run can resolve the instance workflow
  `{contract['workflow']}` at the configured ref.
- Owner: instance administrators for access; child maintainers for the caller.
- Recovery: rerun bootstrap, review the generated caller, and verify the
  instance access policy before pushing it.
- Proof to advance: the reusable workflow job is created for this child.
- Rerun: rerun the child workflow from the default branch.

## Gate 2 — effective provider configuration

- Symptom: provider names, mappings, or `configuration_revision` are rejected.
- Evidence: the caller's explicit mappings match the generated instance
  contract and no `secrets: inherit` appears.
- Owner: instance administrators own the contract; child maintainers own the
  checked-in caller.
- Recovery: run `python3 -m panopticon.organization_template validate PROFILE`,
  regenerate the overlay if needed, and rerun child bootstrap.
- Proof to advance: the effective values resolve before provider preflight.
- Rerun: rerun bootstrap, review the caller diff, commit, and rerun the child.

## Gate 3 — caller identity and credentials

- Symptom: OIDC or the instance-managed credential action cannot identify or
  authorize the child repository.
- Evidence: the provider credential step reports the expected child subject;
  the organization broker writes only its non-secret region output.
- Owner: the organization provisions each child identity; the child maintainer
  supplies the exact repository subject.
- Recovery: {child_identity['instructions']}
- Proof to advance: the child identity check succeeds before provider preflight.
- Rerun: {child_identity['diagnostic_url']} and then rerun the child workflow.
{role_line}
## Gate 4 — real provider-request compatibility

- Symptom: credentials succeed but the real structured provider request fails.
- Evidence: the provider preflight and one real request both complete in the
  selected provider workflow.
- Owner: provider administrators for capability/model access; child maintainers
  for the request and resulting report.
- Recovery: use the provider workflow summary, correct only the named
  non-secret configuration, and rerun the child workflow.
- Proof to advance: the real request succeeds without changing the caller's
  workflow structure.
- Rerun: rerun the same child PR after reviewing the provider summary.

## Reference

- Provider: `{contract['provider']}`
- Credential mode: `{mode}`
- Child provisioning reference: `{identity['child_provisioning_reference']}`
- The caller uses explicit trusted mappings generated by
  `panopticon.callers`; profiles cannot add workflow steps or select workflows.
"""


def _render_debt_register(validated):
    entries = validated["protected_paths"]
    lines = [
        "# Generated protected-path debt register",
        "",
        "The fixed generated path and the provider-derived credential wrapper are",
        "reported in the overlay manifest but are not organization maintenance debt.",
        "",
    ]
    if not entries:
        lines.append("No organization-declared protected-path debt entries.")
        return "\n".join(lines) + "\n"
    lines.extend([
        "| Exact path | Reason | Owner | Upstream replacement | Last reconciliation | Removal condition |",
        "| --- | --- | --- | --- | --- | --- |",
    ])
    for entry in entries:
        lines.append(
            "| " + " | ".join(
                entry[field].replace("|", "\\|")
                for field in (
                    "path",
                    "reason",
                    "owner",
                    "upstream_replacement",
                    "last_reconciliation",
                    "removal_condition",
                )
            ) + " |"
        )
    return "\n".join(lines) + "\n"


def render_child_callers(validated, instance, ref, default_branch="main"):
    """Render the trusted child callers for a validated profile without writing them."""
    contract = validated["contract"] if "contract" in validated else validate_profile(validated)["contract"]
    return {
        name: caller_workflow_text(name, instance, ref, contract, default_branch)
        for name in CALLER_WORKFLOWS
    }


def _render_overlay(validated, instance_root):
    org_config = validated["org_config"]
    files = {
        Path("panopticon.config.json"): _canonical_json(org_config),
        INSTANCE_CHECKLIST_PATH: _render_instance_checklist(validated),
        CHILD_CHECKLIST_PATH: _render_child_checklist(validated),
        DEBT_REGISTER_PATH: _render_debt_register(validated),
    }
    if validated["broker"]:
        files[Path(INSTANCE_CREDENTIAL_ACTION)] = _render_wrapper(validated["broker"])

    protection = [
        {
            "path": "docs/architecture.md",
            "class": "template-generated",
            "reason": "The instance architecture document is generated by Panopticon merge tooling.",
        }
    ]
    if validated["broker"]:
        protection.append(
            {
                "path": INSTANCE_CREDENTIAL_ACTION,
                "class": "provider-derived",
                "reason": "The trusted Bedrock instance-managed contract derives this fixed wrapper path.",
            }
        )
    for entry in validated["protected_paths"]:
        protection.append(
            {
                "path": entry["path"],
                "class": "organization-declared",
                "reason": entry["reason"],
                "owner": entry["owner"],
                "upstream_replacement": entry["upstream_replacement"],
                "last_reconciliation": entry["last_reconciliation"],
                "removal_condition": entry["removal_condition"],
            }
        )

    manifest_files = []
    for relative, content in sorted(files.items(), key=lambda item: str(item[0])):
        destination = Path(instance_root) / relative
        preimage = _digest_bytes(destination.read_bytes()) if destination.is_file() else None
        manifest_files.append(
            {
                "path": str(relative),
                "sha256": _digest_text(content),
                "preimage_sha256": preimage,
                "ownership": "provider-derived" if str(relative) == INSTANCE_CREDENTIAL_ACTION else "template-generated",
                "reason": (
                    "The fixed instance-managed credential wrapper is generated from the trusted provider contract."
                    if str(relative) == INSTANCE_CREDENTIAL_ACTION
                    else "Generated from the validated organization profile."
                ),
            }
        )
    manifest = {
        "schema_version": OVERLAY_MANIFEST_VERSION,
        "generator_version": GENERATOR_VERSION,
        "files": manifest_files,
        "protection": sorted(protection, key=lambda item: item["path"]),
        "provider_revision": validated["contract"]["revision"],
        "caller_revision": validated["contract"]["caller_revision"],
    }
    return files, manifest


def generate(profile_path, instance_root, output, *, public=False):
    """Validate and atomically publish a reviewable overlay into an empty directory."""
    validated = load_profile(profile_path, public=public)
    output = Path(output)
    if output.exists() and any(output.iterdir()):
        raise OrganizationTemplateError(f"output directory must be absent or empty: {output}")
    files, manifest = _render_overlay(validated, instance_root)
    output.parent.mkdir(parents=True, exist_ok=True)
    temp_path = Path(tempfile.mkdtemp(prefix=f".{output.name}.", dir=output.parent))
    try:
        files_root = temp_path / "files"
        for relative, content in files.items():
            destination = files_root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(content, encoding="utf-8", newline="\n")
        (temp_path / "overlay-manifest.json").write_text(
            _canonical_json(manifest), encoding="utf-8", newline="\n"
        )
        if output.exists():
            if any(output.iterdir()):
                raise OrganizationTemplateError(f"output directory became non-empty: {output}")
            output.rmdir()
        os.replace(temp_path, output)
    except Exception:
        shutil.rmtree(temp_path, ignore_errors=True)
        raise
    return manifest


def _validate_manifest(overlay):
    overlay = Path(overlay)
    try:
        manifest = json.loads((overlay / "overlay-manifest.json").read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise OrganizationTemplateError("overlay-manifest.json is missing") from exc
    except json.JSONDecodeError as exc:
        raise OrganizationTemplateError(f"overlay-manifest.json is not valid JSON: {exc}") from exc
    manifest = _object(manifest, "overlay manifest")
    required = {"schema_version", "generator_version", "files", "protection", "provider_revision", "caller_revision"}
    if set(manifest) != required:
        raise OrganizationTemplateError("overlay manifest has an invalid field set")
    if manifest["schema_version"] != OVERLAY_MANIFEST_VERSION:
        raise OrganizationTemplateError("overlay manifest schema_version is unsupported")
    files = manifest["files"]
    if not isinstance(files, list) or not files:
        raise OrganizationTemplateError("overlay manifest files must be a non-empty array")
    paths = []
    for index, entry in enumerate(files):
        entry = _object(entry, f"overlay manifest files[{index}]")
        expected = {"path", "sha256", "preimage_sha256", "ownership", "reason"}
        if set(entry) != expected:
            raise OrganizationTemplateError(f"overlay manifest files[{index}] has invalid fields")
        path = Path(entry["path"])
        if path.is_absolute() or ".." in path.parts or not entry["path"]:
            raise OrganizationTemplateError(f"overlay manifest files[{index}].path is unsafe")
        if path in paths:
            raise OrganizationTemplateError(f"overlay manifest contains duplicate path {path}")
        if not re.fullmatch(r"[0-9a-f]{64}", entry["sha256"]):
            raise OrganizationTemplateError(f"overlay manifest files[{index}].sha256 is invalid")
        if entry["preimage_sha256"] is not None and not re.fullmatch(r"[0-9a-f]{64}", entry["preimage_sha256"]):
            raise OrganizationTemplateError(f"overlay manifest files[{index}].preimage_sha256 is invalid")
        paths.append(path)
        source = overlay / "files" / path
        if source.is_symlink() or not source.is_file() or _digest_bytes(source.read_bytes()) != entry["sha256"]:
            raise OrganizationTemplateError(f"overlay file content does not match manifest for {path}")
    files_root = overlay / "files"
    actual = {
        path.relative_to(files_root)
        for path in files_root.rglob("*")
        if path.is_file()
    } if files_root.is_dir() else set()
    if actual != set(paths):
        raise OrganizationTemplateError("overlay contains files not declared by its manifest")
    return manifest


def apply_overlay(overlay, instance_root, *, check=False):
    """Preflight and optionally apply an overlay; return the planned operations."""
    overlay = Path(overlay)
    instance_root = Path(instance_root)
    manifest = _validate_manifest(overlay)
    operations = []
    for entry in manifest["files"]:
        relative = Path(entry["path"])
        destination = instance_root / relative
        parent = instance_root
        for component in relative.parts[:-1]:
            parent /= component
            if parent.is_symlink():
                raise OrganizationTemplateError(
                    f"destination collision for {relative}: a parent path is a symlink"
                )
        if destination.is_symlink():
            raise OrganizationTemplateError(f"destination collision for {relative}: destination is a symlink")
        if destination.exists() and not destination.is_file():
            raise OrganizationTemplateError(
                f"destination collision for {relative}: expected a file, found a non-file path"
            )
        current = _digest_bytes(destination.read_bytes()) if destination.is_file() else None
        if current != entry["preimage_sha256"]:
            state = "absent" if current is None else "changed"
            raise OrganizationTemplateError(
                f"stale destination preimage for {relative}: expected {entry['preimage_sha256'] or 'absent'}, found {state}"
            )
        operation = "create" if current is None else "update"
        if current == entry["sha256"]:
            operation = "unchanged"
        operations.append({"path": str(relative), "operation": operation, "ownership": entry["ownership"]})
    if check:
        return operations
    for entry in manifest["files"]:
        relative = Path(entry["path"])
        destination = instance_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        source = overlay / "files" / relative
        temporary = destination.with_name(f".{destination.name}.overlay-tmp")
        temporary.write_bytes(source.read_bytes())
        os.replace(temporary, destination)
    return operations


def _format_operations(operations, manifest):
    protection = {entry["path"]: entry for entry in manifest["protection"]}
    lines = []
    for operation in operations:
        lines.append(f"{operation['operation']}: {operation['path']} ({operation['ownership']})")
    for path in sorted(protection):
        entry = protection[path]
        lines.append(f"protect: {path} ({entry['class']}) — {entry['reason']}")
    return "\n".join(lines)


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="operation", required=True)
    validate_parser = subparsers.add_parser("validate", help="validate a profile without writing")
    validate_parser.add_argument("profile")
    validate_parser.add_argument("--public", action="store_true")

    generate_parser = subparsers.add_parser("generate", help="generate a reviewable overlay")
    generate_parser.add_argument("profile")
    generate_parser.add_argument("--instance-root", required=True)
    generate_parser.add_argument("--output", required=True)
    generate_parser.add_argument("--public", action="store_true")

    apply_parser = subparsers.add_parser("apply", help="preflight or apply a reviewed overlay")
    apply_parser.add_argument("overlay")
    apply_parser.add_argument("--instance-root", required=True)
    apply_parser.add_argument("--check", action="store_true")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        if args.operation == "validate":
            validated = load_profile(args.profile, public=args.public)
            print(
                f"valid profile: provider={validated['contract']['provider']} "
                f"credential_mode={validated['contract'].get('credential_mode') or 'none'}"
            )
            return 0
        if args.operation == "generate":
            manifest = generate(
                args.profile,
                args.instance_root,
                args.output,
                public=args.public,
            )
            print(f"generated overlay: {args.output}")
            print(f"provider revision: {manifest['provider_revision']}")
            print(f"caller revision: {manifest['caller_revision']}")
            return 0
        manifest = _validate_manifest(args.overlay)
        operations = apply_overlay(args.overlay, args.instance_root, check=args.check)
        print("read-only apply preview:" if args.check else "applied overlay:")
        print(_format_operations(operations, manifest))
        return 0
    except OrganizationTemplateError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
