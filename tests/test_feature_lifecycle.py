import json
import tempfile
import unittest
from pathlib import Path

from panopticon.bootstrap import reconcile_feature_artifacts
from panopticon.init_repo import validate_feature_state
from panopticon.features import (
    FeatureConfigError,
    build_receipt,
    cleanup_retired,
    load_manifest,
    load_receipt,
    selected_artifacts,
    stage_artifacts,
)
from panopticon.sync import _feature_updates


class FeatureLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).parents[1]
        self.manifest = load_manifest(self.root)
        self.enabled = {"okf": "advisory"}
        self.disabled = {"okf": "disabled"}

    def test_disabled_selection_stages_no_okf_artifacts(self):
        calls = []
        staged = stage_artifacts(self.manifest, self.disabled, lambda path: calls.append(path))
        self.assertEqual(staged, [])
        self.assertEqual(calls, [])

    def test_enabled_artifacts_are_installed_and_receipted(self):
        with tempfile.TemporaryDirectory() as tmp:
            staged = [
                {**entry, "content": f"{entry['feature']}:{entry['destination']}".encode()}
                for entry in selected_artifacts(self.manifest, self.enabled)
            ]
            receipt = reconcile_feature_artifacts(
                None, staged, self.enabled, self.manifest, tmp, interactive=False
            )
            self.assertEqual(len(receipt["artifacts"]), 4)
            self.assertTrue((Path(tmp) / ".agents/skills/panopticon-feature-okf/SKILL.md").is_file())
            self.assertEqual(load_receipt(tmp, self.manifest)["modes"]["okf"], "advisory")

    def test_interactive_decline_retains_pending_then_accept_deletes(self):
        with tempfile.TemporaryDirectory() as tmp:
            entry = {"feature": "okf", "destination": ".agents/skills/panopticon-feature-okf/SKILL.md"}
            path = Path(tmp) / entry["destination"]
            path.parent.mkdir(parents=True)
            path.write_text("old")
            previous = build_receipt(self.manifest, self.enabled, [entry])
            from panopticon.features import write_receipt
            write_receipt(previous, tmp)

            declined = reconcile_feature_artifacts(
                load_receipt(tmp, self.manifest), [], self.disabled, self.manifest, tmp,
                interactive=True, prompt=lambda _: "n", print_fn=lambda _: None,
            )
            self.assertTrue(path.is_file())
            self.assertEqual(declined["pending_removals"], [entry])

            accepted = reconcile_feature_artifacts(
                load_receipt(tmp, self.manifest), [], self.disabled, self.manifest, tmp,
                interactive=True, prompt=lambda _: "Y", print_fn=lambda _: None,
            )
            self.assertFalse(path.exists())
            self.assertEqual(accepted["artifacts"], [])

    def test_noninteractive_cleanup_deletes_only_receipt_owned_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            owned = Path(tmp) / ".agents/skills/panopticon-feature-okf/SKILL.md"
            unrelated = Path(tmp) / ".agents/skills/panopticon-feature-okf/child.md"
            owned.parent.mkdir(parents=True)
            owned.write_text("owned")
            unrelated.write_text("child-owned")
            deleted, pending = cleanup_retired(
                [{"feature": "okf", "destination": str(owned.relative_to(tmp))}],
                tmp, interactive=False, print_fn=lambda _: None,
            )
            self.assertEqual(len(deleted), 1)
            self.assertEqual(pending, [])
            self.assertFalse(owned.exists())
            self.assertTrue(unrelated.exists())

    def test_malformed_receipt_rejects_before_cleanup_and_staging_is_all_or_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            receipt_path = Path(tmp) / "panopticon/feature-receipt.json"
            receipt_path.parent.mkdir()
            receipt_path.write_text(json.dumps({"artifacts": [{"destination": "../../outside"}]}))
            with self.assertRaises(FeatureConfigError):
                load_receipt(tmp, self.manifest)
            outside = Path(tmp).parent / "outside"
            self.assertFalse(outside.exists())

            writes = []
            def fetch(path):
                writes.append(path)
                if len(writes) == 2:
                    raise FeatureConfigError("second source is invalid")
                return b"first"

            with self.assertRaises(FeatureConfigError):
                stage_artifacts(self.manifest, self.enabled, fetch)
            self.assertFalse((Path(tmp) / ".agents").exists())

    def test_sync_dry_run_reports_feature_changes_without_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            staged = [
                {**entry, "content": b"new"}
                for entry in selected_artifacts(self.manifest, self.enabled)
            ]
            findings = _feature_updates(tmp, staged, [], None)
            self.assertTrue(any("would be created" in finding for finding in findings))
            self.assertFalse((Path(tmp) / ".agents").exists())

    def test_initialization_reports_advisory_findings_but_blocks_on_blocking_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            helper = root / "panopticon" / "feature_okf.py"
            helper.parent.mkdir()
            helper.write_bytes((self.root / "features/okf/okf.py").read_bytes())
            docs = root / "docs"
            docs.mkdir()
            (docs / "index.md").write_text("# Index\n\n- [Component](component.md)\n")
            (docs / "log.md").write_text("# Log\n\n## 2026-08-21\n\n- Added.\n")
            (docs / "component.md").write_text("# Missing type\n")
            from panopticon.features import write_receipt
            entry = {"feature": "okf", "destination": "panopticon/feature_okf.py"}
            write_receipt(build_receipt(self.manifest, {"okf": "advisory"}, [entry]), tmp)
            findings, blocking = validate_feature_state(tmp, "docs")
            self.assertTrue(findings)
            self.assertFalse(blocking)

            write_receipt(build_receipt(self.manifest, {"okf": "blocking"}, [entry]), tmp)
            findings, blocking = validate_feature_state(tmp, "docs")
            self.assertTrue(findings)
            self.assertTrue(blocking)


if __name__ == "__main__":
    unittest.main()
