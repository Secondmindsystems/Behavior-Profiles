import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
TOOL = ROOT / "products/behavior-profiles/runtime/tools/verify_contract.py"
SPEC = importlib.util.spec_from_file_location("verify_contract", TOOL)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class ContractProjectionTests(unittest.TestCase):
    def test_canonical_projection_passes(self):
        self.assertEqual(MODULE.verify(ROOT)["status"], "PASS")

    def test_canonical_sha_is_frozen(self):
        result = MODULE.verify(ROOT)
        self.assertEqual(
            result["actual_constitution_sha256"],
            "769385360202ad58557d52ab1d3b9e1d3419a056b50f513af66d3604dab0e1d6",
        )

    def test_missing_required_constitution_text_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source_contract = ROOT / "products/behavior-profiles/runtime/contracts/scope_control.contract.json"
            contract = json.loads(source_contract.read_text(encoding="utf-8"))
            source_constitution = ROOT / contract["constitution"]["path"]
            target_contract = root / "products/behavior-profiles/runtime/contracts/scope_control.contract.json"
            target_constitution = root / contract["constitution"]["path"]
            target_contract.parent.mkdir(parents=True)
            target_constitution.parent.mkdir(parents=True)
            changed = source_constitution.read_text(encoding="utf-8").replace(
                "Do not silently expand the task.", "Silently expand the task."
            )
            target_constitution.write_text(changed, encoding="utf-8")
            changed_contract = copy.deepcopy(contract)
            changed_contract["constitution"]["sha256"] = MODULE.sha256(target_constitution)
            target_contract.write_text(json.dumps(changed_contract), encoding="utf-8")
            self.assertEqual(MODULE.verify(root)["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
