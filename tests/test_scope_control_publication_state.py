from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "check_scope_control_publication_state.py"
SPEC = importlib.util.spec_from_file_location("check_scope_control_publication_state", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ScopeControlPublicationStateTests(unittest.TestCase):
    def test_repository_publication_state_passes(self) -> None:
        source = (ROOT / MODULE.CANONICAL_PATH).read_bytes()
        result = MODULE.check(ROOT, source, {"source": "test"})
        self.assertEqual("PASS", result["decision"], result["errors"])

    def test_vocabulary_without_structure_fails(self) -> None:
        suite = MODULE.HARNESS.load_json(ROOT / MODULE.SUITE_PATH)
        decoy = (ROOT / MODULE.NEGATIVE_CONTROL_PATH).read_text(encoding="utf-8")
        self.assertEqual("FAIL", MODULE.HARNESS.check_profile(suite, decoy)["decision"])

    def test_source_to_shelf_drift_fails_closed(self) -> None:
        source = (ROOT / MODULE.CANONICAL_PATH).read_bytes() + b"\n"
        result = MODULE.check(ROOT, source, {"source": "test-altered"})
        self.assertEqual("FAIL", result["decision"])
        self.assertTrue(any("source" in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main()
