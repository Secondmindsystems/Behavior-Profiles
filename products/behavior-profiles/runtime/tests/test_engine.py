import copy
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
RUNTIME_ROOT = ROOT / "products/behavior-profiles/runtime"
import sys

sys.path.insert(0, str(RUNTIME_ROOT))

from scope_runtime.engine import evaluate  # noqa: E402
from scope_runtime.evidence import persist_decision  # noqa: E402
from scope_runtime.shell_policy import parse  # noqa: E402


def flatten(value, prefix=""):
    output = {}
    if isinstance(value, dict):
        for key, item in value.items():
            output.update(flatten(item, f"{prefix}.{key}" if prefix else key))
    else:
        output[prefix] = value
    return output


class EngineMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.matrix = json.loads((RUNTIME_ROOT / "fixtures/engine_matrix.json").read_text(encoding="utf-8"))

    def test_sixteen_observations_match_frozen_dispositions(self):
        observed = 0
        for pair in self.matrix["pairs"]:
            for case in pair["observations"]:
                decision = evaluate(case["authority"], case["action"])
                self.assertEqual(decision.runtime_decision, case["expected"], f"{pair['id']}:{case['name']}")
                observed += 1
        self.assertEqual(observed, 16)

    def test_each_pair_changes_exactly_one_declared_material_field(self):
        for pair in self.matrix["pairs"]:
            left, right = pair["observations"]
            left_flat = flatten({"authority": left["authority"], "action": left["action"]})
            right_flat = flatten({"authority": right["authority"], "action": right["action"]})
            changed = {key for key in left_flat.keys() | right_flat.keys() if left_flat.get(key) != right_flat.get(key)}
            self.assertEqual(changed, {pair["changed_field"]}, pair["id"])

    def test_all_four_runtime_dispositions_are_reachable(self):
        decisions = {
            evaluate(case["authority"], case["action"]).runtime_decision
            for pair in self.matrix["pairs"]
            for case in pair["observations"]
        }
        self.assertEqual(decisions, {"ALLOW", "BLOCK", "ASK", "DEFER"})

    def test_no_touch_precedes_broad_authorization(self):
        pair = next(pair for pair in self.matrix["pairs"] if pair["id"] == "F2")
        decision = evaluate(pair["observations"][0]["authority"], pair["observations"][0]["action"])
        self.assertEqual((decision.runtime_decision, decision.reason_code), ("BLOCK", "NO_TOUCH_TARGET"))

    def test_requested_task_is_not_semantic_policy_input(self):
        pair = next(pair for pair in self.matrix["pairs"] if pair["id"] == "F1")
        case = pair["observations"][0]
        changed = copy.deepcopy(case["authority"])
        changed["requested_task"] = "Contradictory prose that must not change deterministic policy"
        self.assertEqual(evaluate(case["authority"], case["action"]), evaluate(changed, case["action"]))

    def test_unknown_authority_field_fails_closed(self):
        pair = next(pair for pair in self.matrix["pairs"] if pair["id"] == "F1")
        case = pair["observations"][0]
        changed = copy.deepcopy(case["authority"])
        changed["semantic_intent"] = "please infer"
        decision = evaluate(changed, case["action"])
        self.assertEqual((decision.runtime_decision, decision.reason_code), ("BLOCK", "NO_LAWFUL_AUTHORITY_STATE"))

    def test_defer_projects_deny_and_preserves_structured_item(self):
        pair = next(pair for pair in self.matrix["pairs"] if pair["id"] == "F3")
        case = pair["observations"][0]
        decision = evaluate(case["authority"], case["action"])
        self.assertEqual((decision.runtime_decision, decision.host_projection), ("DEFER", "deny"))
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            receipt = persist_decision(
                decision,
                evidence_root=root,
                episode_id="episode-f3",
                host_event_id="event-f3",
                tool="Write",
                identity_block={"profile_sha": "profile", "contract_sha": "contract"},
                timestamp="2026-08-10T00:00:00+00:00",
            )
            self.assertIsNotNone(receipt["deferred_item_id"])
            self.assertEqual(receipt["action_class"], "edit")
            deferred = root / "deferred-items" / f"{receipt['deferred_item_id']}.json"
            self.assertTrue(deferred.is_file())
            record = json.loads(deferred.read_text(encoding="utf-8"))
            for field in ("proposed_action", "target", "action_class", "authority_task_id", "deferral_reason", "episode_id", "receipt_identity", "timestamp"):
                self.assertIn(field, record)

    def test_shell_policy_rejects_semantic_and_composed_forms(self):
        for command in (
            "Get-Content file.txt | Select-Object -First 1",
            "Get-Content *.txt",
            "Get-Content -LiteralPath $env:TEMP/file.txt",
            "Get-Content -LiteralPath %TEMP%/file.txt",
            "Get-Content file.txt; Remove-Item file.txt",
            "please read file.txt",
            "",
        ):
            self.assertEqual(parse(command).status, "BLOCK", command)


if __name__ == "__main__":
    unittest.main()
