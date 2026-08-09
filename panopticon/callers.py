"""Generate the fixed managed GitHub Actions callers installed in child repositories."""

import hashlib
import json


DEFAULT_BRANCH = "main"
CALLER_WORKFLOWS = (
    "panopticon-pr.yml",
    "panopticon-merge.yml",
    "panopticon-pr-close.yml",
    "panopticon-resource-sync.yml",
)

_CALLER_HEADER = (
    "# Wired by Panopticon install.py — a thin reference to the shared workflow in the instance repo.\n"
    "# Re-run install.py or panopticon.sync to update. Secrets and variables are org-level; "
    "this repo configures none.\n"
)


def _actions_expression(namespace, name):
    return "${{ " + namespace + "." + name + " }}"


def caller_compatibility_payload(contract):
    """Return the semantic reusable-workflow invocation contract."""
    return {
        "workflow": contract["workflow"],
        "permissions": contract["permissions"],
        "secrets": contract["secrets"],
        "variables": contract["variables"],
        "credential_mode": contract.get("credential_mode"),
    }


def caller_compatibility_revision(contract):
    """Return the revision that guards the generated caller's compatibility boundary."""
    serialized = json.dumps(
        caller_compatibility_payload(contract), sort_keys=True, separators=(",", ":")
    ).encode()
    return hashlib.sha256(serialized).hexdigest()


def caller_workflow_text(name, instance, ref, contract, default_branch=DEFAULT_BRANCH):
    """Return the YAML text for one thin managed caller workflow."""
    triggers = {
        "panopticon-pr.yml": "on:\n  pull_request:\n",
        "panopticon-merge.yml": f"on:\n  push:\n    branches: [{default_branch}]\n",
        "panopticon-pr-close.yml": "on:\n  pull_request:\n    types: [closed]\n",
        "panopticon-resource-sync.yml": "on:\n  workflow_dispatch:\n",
    }[name]
    workflow_name = {
        "panopticon-pr.yml": "Panopticon PR checks",
        "panopticon-merge.yml": "Panopticon merge sync",
        "panopticon-pr-close.yml": "Panopticon PR close",
        "panopticon-resource-sync.yml": "Panopticon resource sync",
    }[name]
    remote_name = (
        contract["workflow"]
        if name == "panopticon-pr.yml"
        else "shared-child-resource-sync.yml"
        if name == "panopticon-resource-sync.yml"
        else name
    )
    lines = [
        f"{_CALLER_HEADER}",
        f"name: {workflow_name}\n",
        triggers,
        "jobs:\n",
        "  panopticon:\n",
        f"    uses: {instance}/.github/workflows/{remote_name}@{ref}\n",
    ]
    if name == "panopticon-pr.yml":
        caller_defaults = {
            logical: value
            for logical, value in contract["defaults"].items()
            if logical != "job_timeout_minutes"
        }
        revision = caller_compatibility_revision(contract)
        lines.extend(
            [
                "# Optional provider variables: "
                + json.dumps(contract["optional_variables"], separators=(",", ":"))
                + "\n",
                "# Instance provider defaults: "
                + json.dumps(caller_defaults, sort_keys=True, separators=(",", ":"))
                + "\n",
            ]
        )
        lines.append("    permissions:\n")
        for permission, access in contract["permissions"].items():
            lines.append(f"      {permission}: {access}\n")
        lines.extend(
            [
                "    with:\n",
                f"      instance: {instance}\n",
                f"      workflow_ref: {ref}\n",
                f"      configuration_revision: {revision}\n",
                "      configuration_names: '"
                + json.dumps(
                    {**contract["secrets"], **contract["variables"]},
                    sort_keys=True,
                    separators=(",", ":"),
                )
                + "'\n",
            ]
        )
        if contract.get("credential_mode"):
            lines.append(f"      credential_mode: {contract['credential_mode']}\n")
        for logical, configured_name in contract["variables"].items():
            if logical == "job_timeout_minutes":
                lines.append(f"      {logical}: {_actions_expression('vars', configured_name)}\n")
                lines.append(
                    "      job_timeout_source: ${{ "
                    f"vars.{configured_name} && 'organization variable' || 'workflow default' }}}}\n"
                )
            else:
                lines.append(f"      {logical}: {_actions_expression('vars', configured_name)}\n")
        lines.append("    secrets:\n")
        for logical, configured_name in contract["secrets"].items():
            lines.append(f"      {logical}: {_actions_expression('secrets', configured_name)}\n")
    else:
        if name == "panopticon-resource-sync.yml":
            lines.extend(
                [
                    "    permissions:\n",
                    "      contents: write\n",
                    "      pull-requests: write\n",
                ]
            )
        token_name = contract["secrets"]["instance_token"]
        lines.extend(
            [
                "    secrets:\n",
                f"      instance_token: {_actions_expression('secrets', token_name)}\n",
            ]
        )
    return "".join(lines)
