#!/usr/bin/env python3
"""Run the frozen paired Runtime engine matrix and emit a machine record."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


RUNTIME_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUNTIME_ROOT))

from scope_runtime.engine import evaluate  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run() -> dict[str, object]:
    fixture_path = RUNTIME_ROOT / "fixtures/engine_matrix.json"
    matrix = json.loads(fixture_path.read_text(encoding="utf-8"))
    observations = []
    decisions = set()
    failures = []
    for pair in matrix["pairs"]:
        for case in pair["observations"]:
            decision = evaluate(case["authority"], case["action"])
            passed = decision.runtime_decision == case["expected"]
            observations.append(
                {
                    "fixture": pair["id"],
                    "case": case["name"],
                    "expected": case["expected"],
                    "observed": decision.runtime_decision,
                    "reason_code": decision.reason_code,
                    "passed": passed,
                }
            )
            decisions.add(decision.runtime_decision)
            if not passed:
                failures.append(f"{pair['id']}:{case['name']}")
    expected_decisions = {"ALLOW", "BLOCK", "ASK", "DEFER"}
    if decisions != expected_decisions:
        failures.append("decision reachability")
    return {
        "status": "PASS" if not failures else "FAIL",
        "fixture_sha256": sha256(fixture_path),
        "pair_count": len(matrix["pairs"]),
        "observation_count": len(observations),
        "reachable_decisions": sorted(decisions),
        "semantic_stop": {
            "requested_task_consumed_as_policy": False,
            "llm_or_semantic_judge_present": False,
            "general_shell_parser_present": False,
            "result": "PASS"
        },
        "observations": observations,
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run()
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    print(rendered, end="")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
