from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools/verify_profile_package.py"
SPEC = importlib.util.spec_from_file_location("verify_profile_package", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class VerifyProfilePackageTests(unittest.TestCase):
    def test_repository_package_passes(self) -> None:
        result = MODULE.verify(ROOT, mode="package")
        self.assertEqual("PASS", result["decision"], result["errors"])

    def test_repository_release_is_blocked_without_dogfood(self) -> None:
        evidence_path = MODULE.EVIDENCE_PATH
        try:
            MODULE.EVIDENCE_PATH = Path("profiles/scope-control/evidence/absent-test-record.json")
            result = MODULE.verify(ROOT, mode="release")
        finally:
            MODULE.EVIDENCE_PATH = evidence_path
        self.assertEqual("BLOCKED", result["decision"])
        self.assertTrue(any("missing required dogfood evidence" in error for error in result["errors"]))

    def test_evidence_file_presence_alone_cannot_pass(self) -> None:
        errors, _ = MODULE.validate_release_evidence(ROOT, {})
        self.assertTrue(errors)
        self.assertIn("dogfood evidence missing field: run_id", errors)

    def test_failed_evidence_cannot_authorize_release(self) -> None:
        errors, _ = MODULE.validate_release_evidence(
            ROOT, {"aggregate_disposition": "FAIL_INTERNAL_DOGFOOD"}
        )
        self.assertIn(
            "release blocked by aggregate disposition: FAIL_INTERNAL_DOGFOOD", errors
        )

    def test_missing_package_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = MODULE.verify(Path(directory))
        self.assertEqual("FAIL", result["decision"])
        self.assertTrue(result["errors"])

    def test_proof_boundary_disclaims_obedience(self) -> None:
        result = MODULE.verify(ROOT, mode="package")
        self.assertIn("does not establish universal agent obedience", result["proof_boundary"])

    def test_canonical_identity_triple_is_bound(self) -> None:
        result = MODULE.verify(ROOT, mode="package")
        self.assertEqual(
            {
                "source": "git",
                "ref": "main",
                "path": "products/behavior-profiles/scope-control/BEHAVIOR_PROFILE_SCOPE_CONTROL.md",
                "sha256": "769385360202ad58557d52ab1d3b9e1d3419a056b50f513af66d3604dab0e1d6",
            },
            result["canonical_profile_identity"],
        )

    def test_package_profile_is_declared_equivalent_not_canonical(self) -> None:
        result = MODULE.verify(ROOT, mode="package")
        self.assertEqual(
            "EQUIVALENT_REPRESENTATION",
            result["package_profile_identity"]["classification"],
        )
        self.assertEqual(
            "8ebe592498af4fd5d5a4517cd68e02b03400c68ed1040cc21fcb1e161192cf1e",
            result["package_profile_identity"]["sha256"],
        )

    def test_canonical_hash_mismatch_fails_closed(self) -> None:
        canonical_sha256 = MODULE.CANONICAL_SHA256
        try:
            MODULE.CANONICAL_SHA256 = "0" * 64
            result = MODULE.verify(ROOT, mode="package")
        finally:
            MODULE.CANONICAL_SHA256 = canonical_sha256
        self.assertEqual("FAIL", result["decision"])
        self.assertTrue(
            any("canonical Scope Control identity mismatch" in error for error in result["errors"])
        )


if __name__ == "__main__":
    unittest.main()
