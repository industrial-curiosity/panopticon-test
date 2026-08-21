"""Offline tests for the complex-organization profile and overlay workflow."""

import copy
import json
import tempfile
import unittest
from pathlib import Path

from panopticon.bootstrap import wire_workflows
from panopticon.callers import CALLER_WORKFLOWS
from panopticon.config import load_org_config, protected_path_metadata, provider_contract
from panopticon.organization_template import (
    CHILD_CHECKLIST_PATH,
    INSTANCE_CREDENTIAL_ACTION,
    OrganizationTemplateError,
    apply_overlay,
    generate,
    load_profile,
    render_child_callers,
    validate_profile,
)
from panopticon.tooling_currency import protected_path_report


ROOT = Path(__file__).resolve().parent.parent
PROFILE_ROOT = ROOT / "templates" / "complex-organization"


def profile(name):
    return json.loads((PROFILE_ROOT / name).read_text(encoding="utf-8"))


class TestOrganizationTemplateValidation(unittest.TestCase):
    def test_public_profiles_validate_with_reserved_concrete_values(self):
        for name in ("direct-oidc.json", "instance-managed.json"):
            with self.subTest(name=name):
                validated = load_profile(PROFILE_ROOT / name, public=True)
                self.assertEqual(validated["contract"]["provider"], "bedrock")

    def test_broker_branch_tag_and_commit_references_are_valid(self):
        base = profile("instance-managed.json")
        for revision in ("release/2026-08", "v1.2.3", "0123456789abcdef0123456789abcdef01234567"):
            with self.subTest(revision=revision):
                candidate = copy.deepcopy(base)
                candidate["broker"]["action"] = f"example-org/panopticon-broker@{revision}"
                self.assertEqual(
                    validate_profile(candidate, public=True)["broker"]["action"],
                    candidate["broker"]["action"],
                )

    def test_invalid_logical_name_missing_default_mode_broker_and_secret_are_rejected(self):
        cases = []
        invalid_name = profile("direct-oidc.json")
        invalid_name["names"]["variables"]["not_a_provider_value"] = "PANOPTICON_VALUE"
        cases.append((invalid_name, "unknown logical names"))

        missing_source = profile("instance-managed.json")
        del missing_source["default_sources"]["model"]
        cases.append((missing_source, "default_sources.model"))

        invalid_mode = profile("direct-oidc.json")
        invalid_mode["credential_mode"] = "unsupported"
        cases.append((invalid_mode, "credential mode"))

        invalid_broker = profile("instance-managed.json")
        invalid_broker["broker"]["action"] = "example-org/panopticon-broker"
        cases.append((invalid_broker, "broker.action"))

        credential_value = profile("direct-oidc.json")
        credential_value["names"]["secrets"]["instance_token"] = "ghp_not-a-secret-value"
        cases.append((credential_value, "credential-looking"))

        for candidate, expected in cases:
            with self.subTest(expected=expected):
                with self.assertRaisesRegex(OrganizationTemplateError, expected):
                    validate_profile(candidate, public=True)

    def test_unknown_runtime_injection_fields_and_placeholders_are_rejected(self):
        candidate = profile("instance-managed.json")
        candidate["workflow"] = "arbitrary.yml"
        with self.assertRaisesRegex(OrganizationTemplateError, "unknown fields"):
            validate_profile(candidate)

        candidate = profile("instance-managed.json")
        candidate["broker"]["action"] = "example-org/panopticon-broker@${{ github.ref }}"
        with self.assertRaisesRegex(OrganizationTemplateError, "placeholder"):
            validate_profile(candidate)

    def test_protected_path_debt_requires_all_fields(self):
        candidate = profile("instance-managed.json")
        del candidate["protected_paths"][0]["removal_condition"]
        with self.assertRaisesRegex(OrganizationTemplateError, "removal_condition"):
            validate_profile(candidate, public=True)

    def test_derived_paths_cannot_be_declared_as_organization_debt(self):
        debt = {
            "reason": "Synthetic customization record",
            "owner": "example-platform-team",
            "upstream_replacement": "https://example.com/panopticon/replacement",
            "last_reconciliation": "2026-01-01: synthetic fixture reviewed",
            "removal_condition": "Remove when the upstream path is available.",
        }
        cases = (
            (
                "direct-oidc.json",
                "docs/architecture.md",
            ),
            (
                "instance-managed.json",
                ".github/actions/panopticon-aws-credentials/action.yml",
            ),
        )
        for name, path in cases:
            with self.subTest(path=path):
                candidate = profile(name)
                candidate["protected_paths"] = [{"path": path, **debt}]
                with self.assertRaisesRegex(OrganizationTemplateError, "derived protected path"):
                    validate_profile(candidate, public=True)


class TestOrganizationTemplateGeneration(unittest.TestCase):
    def generate_profile(self, name, root):
        instance = Path(root) / "instance"
        overlay = Path(root) / "overlay"
        instance.mkdir(parents=True)
        generate(PROFILE_ROOT / name, instance, overlay, public=True)
        return instance, overlay

    def test_generated_config_loads_through_real_provider_contract(self):
        with tempfile.TemporaryDirectory() as root:
            instance, overlay = self.generate_profile("instance-managed.json", root)
            apply_overlay(overlay, instance)
            config = load_org_config(instance)
            contract = provider_contract(config)
            self.assertEqual(contract["credential_mode"], "instance-managed")
            self.assertNotIn("revision", json.loads((instance / "panopticon.config.json").read_text()))
            self.assertEqual(
                (overlay / "files" / INSTANCE_CREDENTIAL_ACTION).read_text().count(
                    "example-org/panopticon-broker/.github/actions/aws-credentials@v1.2.3"
                ),
                1,
            )

    def test_generation_is_byte_for_byte_idempotent_for_equivalent_preimages(self):
        with tempfile.TemporaryDirectory() as root:
            first_root = Path(root) / "first"
            second_root = Path(root) / "second"
            first_root.mkdir()
            second_root.mkdir()
            first_instance, first_overlay = self.generate_profile("direct-oidc.json", first_root)
            second_instance, second_overlay = self.generate_profile("direct-oidc.json", second_root)
            first_files = {path.relative_to(first_overlay): path.read_bytes() for path in first_overlay.rglob("*") if path.is_file()}
            second_files = {path.relative_to(second_overlay): path.read_bytes() for path in second_overlay.rglob("*") if path.is_file()}
            self.assertEqual(first_files, second_files)
            self.assertEqual(first_instance.read_bytes() if first_instance.is_file() else b"", b"")
            self.assertEqual(second_instance.read_bytes() if second_instance.is_file() else b"", b"")

    def test_render_failure_does_not_publish_partial_overlay(self):
        with tempfile.TemporaryDirectory() as root:
            instance = Path(root) / "instance"
            instance.mkdir()
            invalid = profile("instance-managed.json")
            invalid["broker"]["action"] = "invalid"
            profile_path = Path(root) / "invalid.json"
            profile_path.write_text(json.dumps(invalid), encoding="utf-8")
            output = Path(root) / "overlay"
            with self.assertRaises(OrganizationTemplateError):
                generate(profile_path, instance, output)
            self.assertFalse(output.exists())

    def test_generated_public_outputs_have_no_placeholders_or_organization_values(self):
        with tempfile.TemporaryDirectory() as root:
            for name in ("direct-oidc.json", "instance-managed.json"):
                instance, overlay = self.generate_profile(name, Path(root) / name)
                del instance
                text = "\n".join(path.read_text(encoding="utf-8") for path in overlay.rglob("*") if path.is_file())
                self.assertNotRegex(text, r"YOUR_|ghp_|AKIA[0-9A-Z]{16}")
                self.assertNotIn("acme", text.lower())
                self.assertNotIn("yotpo", text.lower())

    def test_generated_child_callers_and_bootstrap_use_explicit_trusted_mappings(self):
        validated = load_profile(PROFILE_ROOT / "instance-managed.json", public=True)
        callers = render_child_callers(validated, "example-org/example-instance", "main")
        self.assertEqual(set(callers), set(CALLER_WORKFLOWS))
        pr = callers["panopticon-pr.yml"]
        self.assertIn("panopticon-pr-bedrock.yml@main", pr)
        self.assertIn("credential_mode: instance-managed", pr)
        self.assertNotIn("secrets: inherit", pr)
        self.assertNotIn("steps:", pr)
        with tempfile.TemporaryDirectory() as root:
            paths = wire_workflows(
                "example-org/example-instance",
                "main",
                validated["contract"],
                child_root=root,
                rendered_workflows=callers,
            )
            self.assertEqual(len(paths), len(CALLER_WORKFLOWS))

    def test_protection_metadata_and_tooling_report_distinguish_ownership(self):
        with tempfile.TemporaryDirectory() as root:
            instance, overlay = self.generate_profile("instance-managed.json", root)
            metadata = json.loads((overlay / "overlay-manifest.json").read_text())["protection"]
            classes = {entry["path"]: entry["class"] for entry in metadata}
            self.assertEqual(classes[INSTANCE_CREDENTIAL_ACTION], "provider-derived")
            self.assertEqual(classes["docs/architecture.md"], "template-generated")
            self.assertEqual(classes[".agents/skills/panopticon-example/SKILL.md"], "organization-declared")
            apply_overlay(overlay, instance)
            report = "\n".join(protected_path_report(instance))
            self.assertIn("provider-derived", report)
            self.assertIn("template-generated", report)
            self.assertIn("organization-declared", report)
            self.assertEqual(
                protected_path_metadata(load_org_config(instance))[1]["class"],
                "provider-derived",
            )


class TestOrganizationTemplateApply(unittest.TestCase):
    def test_check_is_read_only_and_unrelated_content_survives_apply(self):
        with tempfile.TemporaryDirectory() as root:
            instance = Path(root) / "instance"
            overlay = Path(root) / "overlay"
            instance.mkdir()
            unrelated = instance / "unrelated.txt"
            unrelated.write_text("keep", encoding="utf-8")
            generate(PROFILE_ROOT / "instance-managed.json", instance, overlay, public=True)
            before = {path: path.read_bytes() for path in instance.rglob("*") if path.is_file()}
            operations = apply_overlay(overlay, instance, check=True)
            self.assertTrue(operations)
            self.assertEqual(before, {path: path.read_bytes() for path in instance.rglob("*") if path.is_file()})
            apply_overlay(overlay, instance)
            self.assertEqual(unrelated.read_text(encoding="utf-8"), "keep")

    def test_stale_preimage_fails_before_any_overlay_write(self):
        with tempfile.TemporaryDirectory() as root:
            instance = Path(root) / "instance"
            overlay = Path(root) / "overlay"
            instance.mkdir()
            generate(PROFILE_ROOT / "direct-oidc.json", instance, overlay, public=True)
            target = instance / "panopticon.config.json"
            target.write_text("changed\n", encoding="utf-8")
            with self.assertRaisesRegex(OrganizationTemplateError, "stale destination preimage"):
                apply_overlay(overlay, instance)
            self.assertEqual(target.read_text(encoding="utf-8"), "changed\n")
            self.assertFalse((instance / str(CHILD_CHECKLIST_PATH)).exists())

    def test_undeclared_overlay_file_is_rejected_before_writes(self):
        with tempfile.TemporaryDirectory() as root:
            instance = Path(root) / "instance"
            overlay = Path(root) / "overlay"
            instance.mkdir()
            generate(PROFILE_ROOT / "direct-oidc.json", instance, overlay, public=True)
            extra = overlay / "files" / "undeclared.txt"
            extra.write_text("collision", encoding="utf-8")
            with self.assertRaisesRegex(OrganizationTemplateError, "not declared"):
                apply_overlay(overlay, instance)
            self.assertFalse((instance / "panopticon.config.json").exists())


if __name__ == "__main__":
    unittest.main()
