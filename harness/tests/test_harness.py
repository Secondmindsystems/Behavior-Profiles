from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


HARNESS_ROOT = Path(__file__).resolve().parents[1]
PRODUCT_ROOT = HARNESS_ROOT.parent
REPO_ROOT = HARNESS_ROOT.parents[2]
MODULE_PATH = HARNESS_ROOT / "harness.py"
SPEC = importlib.util.spec_from_file_location("behavior_profile_harness", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

SUITE_PATH = HARNESS_ROOT / "profiles/scope-control/suite.json"
CONTROLS_PATH = HARNESS_ROOT / "profiles/scope-control/controls.json"
WORKTREE_PROFILE_PATH = PRODUCT_ROOT / "profiles/scope-control/BEHAVIOR_PROFILE.md"
CANONICAL_REF = "main"
CANONICAL_PATH = "products/behavior-profiles/scope-control/BEHAVIOR_PROFILE_SCOPE_CONTROL.md"
CANONICAL_SHA256 = "769385360202ad58557d52ab1d3b9e1d3419a056b50f513af66d3604dab0e1d6"


def canonical_main_bytes() -> bytes:
    return subprocess.check_output(
        ["git", "show", f"{CANONICAL_REF}:{CANONICAL_PATH}"], cwd=REPO_ROOT
    )


def replace_unordered_marker(text: str, marker: str) -> str:
    return "\n".join(
        f"{marker} {line[2:]}" if line.startswith("* ") else line
        for line in text.splitlines()
    ) + ("\n" if text.endswith("\n") else "")


class HarnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.suite = MODULE.load_json(SUITE_PATH)
        cls.controls = MODULE.load_json(CONTROLS_PATH)
        cls.canonical_text = canonical_main_bytes().decode("utf-8")

    def test_suite_is_valid_and_maps_all_requirements(self) -> None:
        self.assertEqual([], MODULE.validate_suite(self.suite))
        self.assertEqual(19, len(self.suite["profile_contract"]["assertions"]))
        self.assertEqual(8, len(self.suite["fixtures"]))

    def test_canonical_main_profile_passes_all_structural_assertions(self) -> None:
        result = MODULE.check_profile(self.suite, self.canonical_text)
        self.assertEqual("PASS", result["decision"], result["errors"])
        self.assertEqual(19, len(result["criteria"]))
        self.assertTrue(all(item["status"] == "PASS" for item in result["criteria"]))

    def test_existing_worktree_representation_also_passes(self) -> None:
        result = MODULE.check_profile(
            self.suite, WORKTREE_PROFILE_PATH.read_text(encoding="utf-8")
        )
        self.assertEqual("PASS", result["decision"], result["errors"])

    def test_supported_unordered_markers_are_equivalent(self) -> None:
        for marker in ("*", "-", "+"):
            with self.subTest(marker=marker):
                result = MODULE.check_profile(
                    self.suite, replace_unordered_marker(self.canonical_text, marker)
                )
                self.assertEqual("PASS", result["decision"], result["errors"])

    def test_removing_one_required_field_fails_only_that_assertion(self) -> None:
        malformed = self.canonical_text.replace("* Files touched\n", "", 1)
        result = MODULE.check_profile(self.suite, malformed)
        failed = [item["assertion_id"] for item in result["criteria"] if item["status"] == "FAIL"]
        self.assertEqual("FAIL", result["decision"])
        self.assertEqual(["completion_files_touched"], failed)

    def test_materially_altering_one_field_fails_only_that_assertion(self) -> None:
        malformed = self.canonical_text.replace("* Files touched", "* Files modified", 1)
        result = MODULE.check_profile(self.suite, malformed)
        failed = [item["assertion_id"] for item in result["criteria"] if item["status"] == "FAIL"]
        self.assertEqual(["completion_files_touched"], failed)

    def test_valid_field_in_wrong_section_does_not_satisfy_contract(self) -> None:
        malformed = self.canonical_text.replace("* Files touched\n", "", 1)
        malformed = malformed.replace(
            "## Scope Behavior\n", "## Scope Behavior\n\n* Files touched\n", 1
        )
        result = MODULE.check_profile(self.suite, malformed)
        failed = [item["assertion_id"] for item in result["criteria"] if item["status"] == "FAIL"]
        self.assertEqual(["completion_files_touched"], failed)

    def test_required_phrase_as_prose_does_not_satisfy_list_contract(self) -> None:
        malformed = self.canonical_text.replace("* Files touched", "Files touched", 1)
        result = MODULE.check_profile(self.suite, malformed)
        failed = [item["assertion_id"] for item in result["criteria"] if item["status"] == "FAIL"]
        self.assertEqual(["completion_files_touched"], failed)

    def test_complete_profile_text_inside_fenced_example_does_not_conform(self) -> None:
        unrelated_example = f"# Example only\n\n```markdown\n{self.canonical_text}\n```\n"
        result = MODULE.check_profile(self.suite, unrelated_example)
        self.assertEqual("FAIL", result["decision"])
        self.assertTrue(result["errors"])

    def test_ordered_marker_variant_is_intentionally_unsupported(self) -> None:
        unsupported = self.canonical_text.replace("1. Requested task", "1) Requested task", 1)
        result = MODULE.check_profile(self.suite, unsupported)
        failed = [item["assertion_id"] for item in result["criteria"] if item["status"] == "FAIL"]
        self.assertEqual(["before_requested_task"], failed)

    def test_conforming_control_passes(self) -> None:
        result = MODULE.judge_observation(self.suite, self.controls["observations"][0])
        self.assertEqual("PASS", result["decision"])

    def test_nonconforming_control_fails_for_prohibited_event(self) -> None:
        result = MODULE.judge_observation(self.suite, self.controls["observations"][1])
        self.assertEqual("FAIL", result["decision"])
        self.assertIn("adjacent_wording_changed", result["prohibited_events_observed"])

    def test_indeterminate_required_event_is_confused(self) -> None:
        observation = copy.deepcopy(self.controls["observations"][0])
        observation["observation_id"] = "authorized-execution-indeterminate"
        observation["observed_events"].remove("verification_reported")
        observation["indeterminate_events"] = ["verification_reported"]
        result = MODULE.judge_observation(self.suite, observation)
        self.assertEqual("CONFUSED", result["decision"])

    def test_unknown_event_fails_closed(self) -> None:
        observation = copy.deepcopy(self.controls["observations"][0])
        observation["observed_events"].append("invented_event")
        result = MODULE.judge_observation(self.suite, observation)
        self.assertEqual("FAIL", result["decision"])
        self.assertTrue(any("unknown event" in error for error in result["errors"]))

    def test_all_fixtures_discriminate_and_bind_canonical_identity(self) -> None:
        result = MODULE.run_controls(
            self.suite,
            self.controls,
            profile_text=self.canonical_text,
            profile_identity={"source": "git", "ref": CANONICAL_REF, "path": CANONICAL_PATH},
            profile_sha256=CANONICAL_SHA256,
        )
        self.assertEqual("PASS", result["decision"], result["errors"])
        self.assertEqual(8, len(result["discrimination"]))
        self.assertTrue(all(item["status"] == "PASS" for item in result["discrimination"].values()))
        self.assertEqual("PASS", result["structural_profile_check"]["decision"])
        self.assertEqual(CANONICAL_SHA256, result["structural_profile_check"]["profile_sha256"])
        self.assertEqual(19, result["structural_profile_check"]["assertion_count"])
        self.assertIn("Synthetic controls are not agent evidence", result["proof_boundary"])

    def _run_cli(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(MODULE_PATH), *arguments],
            cwd=PRODUCT_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_check_profile_cli_returns_zero_for_pass_and_nonzero_for_fail(self) -> None:
        passed = self._run_cli(
            "check-profile",
            "--suite",
            str(SUITE_PATH),
            "--git-ref",
            CANONICAL_REF,
            "--git-path",
            CANONICAL_PATH,
            "--repo-root",
            str(REPO_ROOT),
        )
        self.assertEqual(0, passed.returncode, passed.stdout + passed.stderr)

        with tempfile.TemporaryDirectory() as directory:
            malformed_path = Path(directory) / "malformed.md"
            malformed_path.write_text(
                self.canonical_text.replace("* Files touched\n", "", 1), encoding="utf-8"
            )
            failed = self._run_cli(
                "check-profile",
                "--suite",
                str(SUITE_PATH),
                "--profile",
                str(malformed_path),
            )
        self.assertEqual(1, failed.returncode, failed.stdout + failed.stderr)

    def test_run_controls_cli_returns_zero_for_pass_and_nonzero_for_fail(self) -> None:
        common = (
            "run-controls",
            "--suite",
            str(SUITE_PATH),
            "--git-ref",
            CANONICAL_REF,
            "--git-path",
            CANONICAL_PATH,
            "--repo-root",
            str(REPO_ROOT),
        )
        passed = self._run_cli(*common, "--observations", str(CONTROLS_PATH))
        self.assertEqual(0, passed.returncode, passed.stdout + passed.stderr)

        controls = copy.deepcopy(self.controls)
        controls["observations"][0]["expected_disposition"] = "FAIL"
        with tempfile.TemporaryDirectory() as directory:
            controls_path = Path(directory) / "failing-controls.json"
            controls_path.write_text(json.dumps(controls), encoding="utf-8")
            failed = self._run_cli(*common, "--observations", str(controls_path))
        self.assertEqual(1, failed.returncode, failed.stdout + failed.stderr)

    def test_confused_judge_cli_returns_nonzero(self) -> None:
        observation = copy.deepcopy(self.controls["observations"][0])
        observation["observed_events"].remove("verification_reported")
        observation["indeterminate_events"] = ["verification_reported"]
        with tempfile.TemporaryDirectory() as directory:
            observation_path = Path(directory) / "confused.json"
            observation_path.write_text(json.dumps(observation), encoding="utf-8")
            result = self._run_cli(
                "judge",
                "--suite",
                str(SUITE_PATH),
                "--observation",
                str(observation_path),
            )
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertEqual("CONFUSED", json.loads(result.stdout)["decision"])


if __name__ == "__main__":
    unittest.main()
