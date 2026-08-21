"""Exact-output tests for provider recovery guidance."""

import unittest

from panopticon.providers import INSTANCE_CREDENTIAL_ACTION
from panopticon.recovery import (
    child_bootstrap_command,
    configuration_recovery,
    credential_action_recovery,
    missing_provider_recovery,
    stale_caller_recovery,
)


class TestRecoveryOutput(unittest.TestCase):
    def test_configuration_recovery_has_console_cli_and_bootstrap_paths(self):
        text = configuration_recovery("acme/private-instance", "trunk")
        for provider in ("litellm", "openai", "bedrock"):
            self.assertIn(
                "https://github.com/acme/private-instance/actions/workflows/"
                f"configure-panopticon-{provider}.yml",
                text,
            )
            self.assertIn(
                f"gh workflow run configure-panopticon-{provider}.yml "
                "--repo acme/private-instance --ref trunk",
                text,
            )
        self.assertIn(
            "PANOPTICON_INSTANCE='acme/private-instance' python3",
            text,
        )
        self.assertNotIn("export PANOPTICON_INSTANCE", text)
        self.assertNotIn("select-a-provider", text)

    def test_private_instance_recovery_uses_its_custom_branch_everywhere(self):
        instance = "acme/private-instance"
        branch = "release/2026-07"
        self.assertEqual(
            configuration_recovery(instance, branch),
            "Configure the Panopticon instance before bootstrapping a child repository.\n\n"
            "GitHub Actions console (choose exactly one provider):\n"
            "  LiteLLM: https://github.com/acme/private-instance/actions/workflows/"
            "configure-panopticon-litellm.yml\n"
            "  OpenAI: https://github.com/acme/private-instance/actions/workflows/"
            "configure-panopticon-openai.yml\n"
            "  Bedrock: https://github.com/acme/private-instance/actions/workflows/"
            "configure-panopticon-bedrock.yml\n"
            "  1. Open the workflow for the provider the instance will use.\n"
            "  2. Select Run workflow.\n"
            "  3. Select branch release/2026-07.\n"
            "  4. Review the secret and variable name fields; enter names only, never values.\n"
            "  5. Select Run workflow and wait for the green completed run that commits "
            "panopticon.config.json.\n\n"
            "Equivalent GitHub CLI commands (run exactly one):\n"
            "  gh workflow run configure-panopticon-litellm.yml --repo acme/private-instance "
            "--ref release/2026-07\n"
            "  gh workflow run configure-panopticon-openai.yml --repo acme/private-instance "
            "--ref release/2026-07\n"
            "  gh workflow run configure-panopticon-bedrock.yml --repo acme/private-instance "
            "--ref release/2026-07\n"
            "  gh run watch --repo acme/private-instance\n\n"
            "Then rerun child bootstrap from inside the child repository clone:\n"
            "  curl -fsSL https://raw.githubusercontent.com/industrial-curiosity/"
            "panopticon-ay-eye/main/install.py | "
            "PANOPTICON_INSTANCE='acme/private-instance' python3\n\n"
            "For a profile-driven setup, validate the reviewed profile and overlay before\n"
            "running this recovery:\n"
            "  python3 -m panopticon.organization_template validate PROFILE\n"
            "  python3 -m panopticon.organization_template apply OVERLAY --instance-root INSTANCE --check\n",
        )

    def test_missing_provider_recovery_names_missing_values_and_exact_command(self):
        text = missing_provider_recovery(
            "acme/instance",
            "Bedrock",
            [("aws_region", "CUSTOM_AWS_REGION"), ("model", "CUSTOM_MODEL")],
        )
        self.assertIn("## Panopticon gate 2 failed: effective provider configuration", text)
        self.assertIn("- Provider: `Bedrock`", text)
        self.assertIn("- `CUSTOM_AWS_REGION` (aws_region)", text)
        self.assertIn("- `CUSTOM_MODEL` (model)", text)
        self.assertIn("provider contract is instance-wide", text)
        self.assertIn("Fix location:", text)
        self.assertIn(child_bootstrap_command("acme/instance"), text)
        self.assertIn("Gate 2 is proven", text)

    def test_stale_caller_recovery_preserves_secret_rotation_guidance(self):
        text = stale_caller_recovery("acme/instance")
        self.assertIn("## Panopticon gate 2 failed: effective provider configuration", text)
        self.assertIn("Expected resource:", text)
        self.assertIn("generated caller compatibility revision is per child", text)
        self.assertIn(child_bootstrap_command("acme/instance"), text)
        self.assertIn("Keep old secret names available until regeneration finishes.", text)

    def test_stale_provider_or_name_change_recovery_is_exact(self):
        self.assertEqual(
            stale_caller_recovery("acme/instance"),
            "## Panopticon gate 2 failed: effective provider configuration\n\n"
            "- Expected resource: the current caller-compatible provider revision in `acme/instance` and this child caller\n"
            "- Scope: the provider contract is instance-wide; the generated caller compatibility revision is per child.\n"
            "- Evidence: the caller revision does not match the checked-out instance configuration.\n\n"
            "Fix location: run this from inside the child clone, or validate the generated profile before regenerating the caller:\n\n"
            "~~~bash\n"
            "curl -fsSL https://raw.githubusercontent.com/industrial-curiosity/"
            "panopticon-ay-eye/main/install.py | PANOPTICON_INSTANCE='acme/instance' python3\n"
            "~~~\n\n"
            "Review and commit the generated changes, push them, then rerun or await this child PR workflow. "
            "Keep old secret names available until regeneration finishes. Gate 2 is proven when the caller revision matches before provider preflight.\n",
        )

    def test_credential_action_recovery_identifies_gate_scope_and_rerun(self):
        text = credential_action_recovery(
            "acme/instance",
            "acme/child-service",
        )
        self.assertIn("## Panopticon gate 3 failed: caller identity and credentials", text)
        self.assertIn(
            "`.github/actions/panopticon-aws-credentials/action.yml` in `acme/instance`",
            text,
        )
        self.assertIn("Caller repository: `acme/child-service`", text)
        self.assertIn("per child", text)
        self.assertIn("timeout", text)
        self.assertIn("id-token: write", text)
        self.assertIn("your-org-identity-tool register --repository 'acme/child-service'", text)
        self.assertIn(child_bootstrap_command("acme/instance"), text)
        self.assertIn("rerun or await the child PR workflow", text)

    def test_credential_action_recovery_is_copyable_and_explains_automatic_protection(self):
        text = credential_action_recovery("acme/instance", "acme/child-service")
        self.assertIn(
            "https://github.com/industrial-curiosity/panopticon-ay-eye/blob/main/"
            "docs/examples/panopticon-aws-credentials/action.yml",
            text,
        )
        self.assertIn(
            '"protected_paths": [\n    ".github/actions/panopticon-aws-credentials/action.yml"\n  ]',
            text,
        )
        self.assertIn("automatically protects the fixed action during template sync", text)
        self.assertIn("PANOPTICON_AWS_REGION", text)
        self.assertNotIn("amazon.secret", text)
        self.assertNotIn("access_key_value", text)

    def test_credential_action_recovery_accepts_instance_specific_fixed_path(self):
        text = credential_action_recovery(
            "acme/instance",
            "acme/child-service",
            ".github/actions/custom-credentials/action.yml",
        )
        self.assertIn("`.github/actions/custom-credentials/action.yml`", text)
        self.assertNotIn("secret_value", text)
        self.assertNotIn("access_key", text)

    def test_recovery_reuses_provider_owned_fixed_action_path(self):
        self.assertEqual(INSTANCE_CREDENTIAL_ACTION, ".github/actions/panopticon-aws-credentials/action.yml")
        self.assertIn(INSTANCE_CREDENTIAL_ACTION, credential_action_recovery("acme/instance", "acme/child"))


if __name__ == "__main__":
    unittest.main()
