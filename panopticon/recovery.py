"""Shared, copy/paste-safe recovery text for provider configuration failures."""

from .providers import INSTANCE_CREDENTIAL_ACTION

PUBLIC_INSTALLER_URL = (
    "https://raw.githubusercontent.com/industrial-curiosity/panopticon-ay-eye/main/install.py"
)
PUBLIC_CREDENTIAL_ACTION_EXAMPLE_URL = (
    "https://github.com/industrial-curiosity/panopticon-ay-eye/blob/main/"
    "docs/examples/panopticon-aws-credentials/action.yml"
)
def child_bootstrap_command(instance):
    """Return the exact installer command for a child bound to ``instance``."""
    return f"curl -fsSL {PUBLIC_INSTALLER_URL} | PANOPTICON_INSTANCE='{instance}' python3"


def configuration_recovery(instance, branch):
    """Return terminal-friendly recovery for an unconfigured instance."""
    workflow_url = f"https://github.com/{instance}/actions/workflows"
    litellm_url = f"{workflow_url}/configure-panopticon-litellm.yml"
    openai_url = f"{workflow_url}/configure-panopticon-openai.yml"
    bedrock_url = f"{workflow_url}/configure-panopticon-bedrock.yml"
    return f"""Configure the Panopticon instance before bootstrapping a child repository.

GitHub Actions console (choose exactly one provider):
  LiteLLM: {litellm_url}
  OpenAI: {openai_url}
  Bedrock: {bedrock_url}
  1. Open the workflow for the provider the instance will use.
  2. Select Run workflow.
  3. Select branch {branch}.
  4. Review the secret and variable name fields; enter names only, never values.
  5. Select Run workflow and wait for the green completed run that commits panopticon.config.json.

Equivalent GitHub CLI commands (run exactly one):
  gh workflow run configure-panopticon-litellm.yml --repo {instance} --ref {branch}
  gh workflow run configure-panopticon-openai.yml --repo {instance} --ref {branch}
  gh workflow run configure-panopticon-bedrock.yml --repo {instance} --ref {branch}
  gh run watch --repo {instance}

Then rerun child bootstrap from inside the child repository clone:
  {child_bootstrap_command(instance)}

For a profile-driven setup, validate the reviewed profile and overlay before
running this recovery:
  python3 -m panopticon.organization_template validate PROFILE
  python3 -m panopticon.organization_template apply OVERLAY --instance-root INSTANCE --check
"""


def missing_provider_recovery(instance, provider, missing):
    """Return a step-summary section for missing provider inputs."""
    lines = [
        "## Panopticon gate 2 failed: effective provider configuration",
        "",
        f"- Provider: `{provider}`",
        "- Expected configured names:",
    ]
    lines.extend(f"  - `{configured_name}` ({logical})" for logical, configured_name in missing)
    lines.extend(
        [
            "- Scope: the provider contract is instance-wide; the generated caller mapping is per child.",
            "- Evidence: one or more required configured names were absent before provider preflight.",
            "",
            "Fix location: run the matching provider configuration workflow in the instance, or regenerate this child caller if the contract is stale. For a generated profile, validate and review its overlay first. Then rerun:",
            "",
            "~~~bash",
            child_bootstrap_command(instance),
            "~~~",
            "",
            "Review and commit the generated changes, push them, then rerun or await this child PR workflow. Gate 2 is proven when effective values resolve before provider preflight.",
            "",
        ]
    )
    return "\n".join(lines)


def stale_caller_recovery(instance):
    """Return a step-summary section for a caller with a stale configuration revision."""
    return "\n".join(
        [
            "## Panopticon gate 2 failed: effective provider configuration",
            "",
            f"- Expected resource: the current caller-compatible provider revision in `{instance}` and this child caller",
            "- Scope: the provider contract is instance-wide; the generated caller compatibility revision is per child.",
            "- Evidence: the caller revision does not match the checked-out instance configuration.",
            "",
            "Fix location: run this from inside the child clone, or validate the generated profile before regenerating the caller:",
            "",
            "~~~bash",
            child_bootstrap_command(instance),
            "~~~",
            "",
            "Review and commit the generated changes, push them, then rerun or await this child PR workflow. "
            "Keep old secret names available until regeneration finishes. Gate 2 is proven when the caller revision matches before provider preflight.",
            "",
        ]
    )


def credential_action_recovery(instance, child_repository, action_path=INSTANCE_CREDENTIAL_ACTION):
    """Return gate-three recovery for an instance-managed credential failure."""
    protected_paths_fragment = (
        '"protected_paths": [\n'
        f'    "{action_path}"\n'
        "  ]"
    )
    return "\n".join(
        [
            "## Panopticon gate 3 failed: caller identity and credentials",
            "",
            f"- Expected resource: `{action_path}` in `{instance}`",
            f"- Caller repository: `{child_repository}`",
            "- Scope: the caller identity and its credential registration are per child; the fixed action and its configuration are instance-owned.",
            "- Evidence: inspect the credential step outcome and its log for the caller's identity or registration error. A timeout is also a credential-gate failure.",
            "",
            "Recovery:",
            "1. In the organization's approved identity system, register the exact child repository for its credential role; do not reuse the instance repository's role.",
            f"   Use the organization's equivalent of `your-org-identity-tool register --repository '{child_repository}'`.",
            "2. Copy the reviewed, credential-free example from:",
            f"   {PUBLIC_CREDENTIAL_ACTION_EXAMPLE_URL}",
            f"   to the exact instance-owned path `{action_path}` and replace only the organization broker step.",
            "3. The action must write `PANOPTICON_AWS_REGION` to `GITHUB_ENV`; verify that the broker selected the intended region before committing.",
            "4. A valid Bedrock `instance-managed` contract automatically protects the fixed action during template sync. Use this copyable fragment for other instance-owned customizations, not as a second requirement for the fixed action:",
            "",
            "~~~json",
            protected_paths_fragment,
            "~~~",
            "5. Confirm the generated child caller grants the permission required by the provider (Bedrock GitHub OIDC requires `id-token: write`) and that the fixed instance action remains at the expected path.",
            "6. If the caller or provider contract is stale, run the child bootstrap command below, review and commit the generated caller, and push it.",
            "",
            "~~~bash",
            child_bootstrap_command(instance),
            "~~~",
            "",
            "After the registration and any caller update are complete, rerun or await the child PR workflow. Gate 3 is proven when the credential step succeeds and the caller identity check reports the expected child identity before provider preflight.",
            "For generated profiles, the overlay manifest identifies this wrapper as provider-derived; do not add it to the organization debt register.",
            "",
        ]
    )
