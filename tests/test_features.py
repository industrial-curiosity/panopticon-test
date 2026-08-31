import json
import tempfile
import unittest
from pathlib import Path

from panopticon.config import ConfigError, load_org_config
from panopticon.configure_instance import configure_feature
from panopticon.features import (
    FeatureConfigError,
    FEATURE_MODES,
    build_receipt,
    load_manifest,
    manifest_revision,
    selected_artifacts,
    validate_manifest,
    validate_receipt,
)


class FeatureRegistryTests(unittest.TestCase):
    def test_template_manifest_is_versioned_and_selects_only_enabled_artifacts(self):
        root = Path(__file__).parents[1]
        manifest = load_manifest(root)
        modes = {"okf": "advisory"}
        selected = selected_artifacts(manifest, modes)
        self.assertEqual(len(selected), 4)
        self.assertTrue(all(entry["feature"] == "okf" for entry in selected))
        self.assertEqual(manifest_revision(manifest), manifest_revision(manifest))

    def test_registry_rejects_unsafe_or_duplicate_destinations(self):
        base = {
            "schema_version": 1,
            "features": {
                "okf": {
                    "modes": list(FEATURE_MODES),
                    "artifacts": [
                        {"source": "okf/helper.py", "destination": "panopticon/feature_okf.py"}
                    ],
                }
            },
        }
        duplicate = json.loads(json.dumps(base))
        duplicate["features"]["okf"]["artifacts"].append(
            {"source": "okf/other.py", "destination": "panopticon/feature_okf.py"}
        )
        with self.assertRaisesRegex(FeatureConfigError, "duplicate feature destination"):
            validate_manifest(duplicate)
        unsafe = json.loads(json.dumps(base))
        unsafe["features"]["okf"]["artifacts"][0]["destination"] = "panopticon/config.json"
        with self.assertRaisesRegex(FeatureConfigError, "outside its approved namespace"):
            validate_manifest(unsafe)

    def test_registry_rejects_core_collision(self):
        document = {
            "schema_version": 1,
            "features": {
                "okf": {
                    "modes": list(FEATURE_MODES),
                    "artifacts": [
                        {"source": "okf/helper.py", "destination": "panopticon/feature_okf.py"}
                    ],
                }
            },
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tooling = root / "panopticon"
            tooling.mkdir()
            (tooling / "local-tooling.json").write_text(
                json.dumps({"schema_version": 1, "modules": ["feature_okf.py"]})
            )
            with self.assertRaisesRegex(FeatureConfigError, "collides with core"):
                validate_manifest(document, root)

    def test_load_org_config_defaults_and_rejects_unregistered_or_invalid_modes(self):
        root = Path(__file__).parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "features").mkdir()
            (Path(tmp) / "features" / "manifest.json").write_bytes(
                (root / "features" / "manifest.json").read_bytes()
            )
            path = Path(tmp) / "panopticon.config.json"
            path.write_text(json.dumps({"features": {"okf": {"mode": "advisory"}}}))
            config = load_org_config(tmp)
            self.assertEqual(config["features"]["okf"]["mode"], "advisory")

            path.write_text(json.dumps({"features": {"not-registered": {"mode": "advisory"}}}))
            with self.assertRaisesRegex(ConfigError, "unregistered feature"):
                load_org_config(tmp)

            path.write_text(json.dumps({"features": {"okf": {"mode": "invalid"}}}))
            with self.assertRaisesRegex(ConfigError, "must be one of"):
                load_org_config(tmp)

    def test_feature_configuration_preserves_unrelated_settings_and_invalid_input_writes_nothing(self):
        source_root = Path(__file__).parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "features").mkdir()
            (root / "features" / "manifest.json").write_bytes(
                (source_root / "features" / "manifest.json").read_bytes()
            )
            original = {
                "schema_version": 1,
                "workflow_ref": "release",
                "llm": {"provider": "openai"},
                "features": {"okf": {"mode": "disabled"}},
                "other": {"keep": True},
            }
            path = root / "panopticon.config.json"
            path.write_text(json.dumps(original))

            self.assertEqual(configure_feature(tmp, "okf", "advisory"), {"mode": "advisory"})
            updated = json.loads(path.read_text())
            self.assertEqual(updated["features"]["okf"]["mode"], "advisory")
            self.assertEqual(updated["llm"], original["llm"])
            self.assertEqual(updated["other"], original["other"])
            self.assertEqual(configure_feature(tmp, "okf"), {"mode": "advisory"})

            before = path.read_bytes()
            with self.assertRaisesRegex(FeatureConfigError, "must be one of"):
                configure_feature(tmp, "okf", "secret-value")
            self.assertEqual(path.read_bytes(), before)


class FeatureReceiptTests(unittest.TestCase):
    def test_receipt_records_revision_and_rejects_unregistered_destinations(self):
        root = Path(__file__).parents[1]
        manifest = load_manifest(root)
        artifacts = selected_artifacts(manifest, {"okf": "advisory"})
        receipt = build_receipt(manifest, {"okf": "advisory"}, artifacts)
        self.assertEqual(validate_receipt(receipt, manifest)["modes"]["okf"], "advisory")
        receipt["artifacts"][0]["destination"] = "panopticon/unknown.py"
        with self.assertRaisesRegex(FeatureConfigError, "not registered"):
            validate_receipt(receipt, manifest)


class FeatureWorkflowTests(unittest.TestCase):
    def test_configuration_workflow_has_generic_inputs_and_no_secret_handling(self):
        root = Path(__file__).parents[1]
        workflow = (root / ".github" / "workflows" / "configure-panopticon-features.yml").read_text()
        action = (root / ".github" / "actions" / "configure-panopticon-features" / "action.yml").read_text()
        self.assertIn("feature:", workflow)
        self.assertIn("mode:", workflow)
        self.assertIn("configure_feature", action)
        self.assertNotIn("secrets:", workflow)
        self.assertNotIn("secrets:", action)
        self.assertNotIn("SECRET_VALUE", action)


if __name__ == "__main__":
    unittest.main()
