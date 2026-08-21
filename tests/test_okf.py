import tempfile
import unittest
from pathlib import Path

from panopticon.docs import render_interface_docs


def _okf_document(kind="component"):
    return f"---\ntype: {kind}\n---\n\n# Document\n\nBody.\n"


class OkfValidationTests(unittest.TestCase):
    def setUp(self):
        import importlib.util

        path = Path(__file__).parents[1] / "features/okf/okf.py"
        spec = importlib.util.spec_from_file_location("test_okf_helper", path)
        self.helper = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.helper)

    def test_valid_constrained_document_and_nonempty_type(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "component.md"
            path.write_text(_okf_document())
            self.assertEqual(self.helper.validate_document(path), [])

            path.write_text("---\ntype:\n---\n\n# Document\n")
            self.assertIn("type must be non-empty", self.helper.validate_document(path)[0])

    def test_rejects_arbitrary_frontmatter_and_missing_frontmatter(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "component.md"
            path.write_text("---\nunknown: value\ntype: component\n---\n")
            self.assertIn("not allowed", self.helper.validate_document(path)[0])
            path.write_text("# Missing metadata\n")
            self.assertIn("must start with ---", self.helper.validate_document(path)[0])

    def test_reserved_index_and_log_require_progressive_disclosure_structures(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "index.md").write_text("# Index\n")
            (root / "log.md").write_text("# Log\n")
            problems = self.helper.validate_bundle(root)
            self.assertTrue(any("index.md" in problem for problem in problems))
            self.assertTrue(any("log.md" in problem for problem in problems))
            (root / "index.md").write_text("# Index\n\n- [Component](component.md)\n")
            (root / "log.md").write_text("# Log\n\n## 2026-08-21\n\n- Added component.\n")
            self.assertEqual(self.helper.validate_bundle(root), [])

    def test_fixture_markdown_is_outside_bundle_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = root / "test-fixtures"
            fixture.mkdir()
            (fixture / "invalid.md").write_text("# Fixture\n")
            self.assertEqual(self.helper.validate_bundle(root), [])


class OkfInterfaceRenderingTests(unittest.TestCase):
    def test_enabled_rendering_adds_frontmatter_without_changing_index_derived_body(self):
        index = {
            "interfaces": {
                "orders": [{
                    "type": "rest",
                    "owner": None,
                    "producer": [],
                    "consumer": [],
                }]
            }
        }
        baseline = render_interface_docs(index, "orders")
        enabled = render_interface_docs(index, "orders", "advisory")
        self.assertTrue(enabled.startswith("---\ntype: interface\n---\n\n"))
        self.assertEqual(enabled.split("---\n\n", 1)[1], baseline)


if __name__ == "__main__":
    unittest.main()
