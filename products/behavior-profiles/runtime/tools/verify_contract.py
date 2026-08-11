#!/usr/bin/env python3
"""Verify the frozen Scope Control contract against its canonical constitution."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


REQUIRED_CONSTITUTION_TEXT = {
    "core_rule": "Do not silently expand the task.",
    "no_touch": "Treat no-touch areas as out of bounds.",
    "commands": "Do not run commands unless commands are authorized.",
    "adjacent": "If you notice a useful adjacent task, defer it and mention it in the completion note.",
    "ambiguity": "If the boundary is unclear enough that you cannot stay inside it, ask for the missing boundary before acting.",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def locate_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "products" / "behavior-profiles" / "runtime").is_dir():
            return candidate
    raise RuntimeError("runtime package root not found")


def verify(repo_root: Path) -> dict[str, object]:
    contract_path = repo_root / "products/behavior-profiles/runtime/contracts/scope_control.contract.json"
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    constitution_path = repo_root / contract["constitution"]["path"]
    actual_sha = sha256(constitution_path)
    text = constitution_path.read_text(encoding="utf-8")
    failures: list[str] = []

    if actual_sha != contract["constitution"]["sha256"]:
        failures.append("canonical constitution SHA-256 mismatch")
    for name, required in REQUIRED_CONSTITUTION_TEXT.items():
        if required not in text:
            failures.append(f"canonical constitution missing required projection source: {name}")
    if contract["core_rule"] != REQUIRED_CONSTITUTION_TEXT["core_rule"]:
        failures.append("contract core rule does not match canonical wording")
    if set(contract["decisions"]) != {"ALLOW", "BLOCK", "ASK", "DEFER"}:
        failures.append("contract decision vocabulary changed")
    if not contract["runtime_invariants"]["no_touch_precedes_authorization"]:
        failures.append("no-touch precedence is not bound")
    if not contract["runtime_invariants"]["commands_require_authority"]:
        failures.append("command authority requirement is not bound")
    if not contract["runtime_invariants"]["runtime_is_not_constitution"]:
        failures.append("constitution/runtime authority separation is not bound")

    return {
        "status": "PASS" if not failures else "FAIL",
        "constitution_path": contract["constitution"]["path"],
        "expected_constitution_sha256": contract["constitution"]["sha256"],
        "actual_constitution_sha256": actual_sha,
        "contract_sha256": sha256(contract_path),
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.repo_root.resolve() if args.repo_root else locate_repo_root(Path(__file__).resolve())
    result = verify(root)
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
