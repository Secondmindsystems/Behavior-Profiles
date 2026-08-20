from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HARNESS_PATH = ROOT / "harness" / "harness.py"
SPEC = importlib.util.spec_from_file_location("scope_control_harness", HARNESS_PATH)
assert SPEC and SPEC.loader
HARNESS = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = HARNESS
SPEC.loader.exec_module(HARNESS)

CANONICAL_PATH = Path("products/behavior-profiles/scope-control/BEHAVIOR_PROFILE_SCOPE_CONTROL.md")
INSTALLABLE_PATH = Path("profiles/scope-control/BEHAVIOR_PROFILE.md")
AGENT_EVIDENCE_PATH = Path("profiles/scope-control/evidence/internal-dogfood-002.json")
SYNTHETIC_EVIDENCE_PATH = Path("harness/evidence/pass-1-control-run.json")
SUITE_PATH = Path("harness/profiles/scope-control/suite.json")
NEGATIVE_CONTROL_PATH = Path("harness/profiles/scope-control/vocabulary-without-structure.md")

EXPECTED_HASHES = {
    "canonical_product_profile": "769385360202ad58557d52ab1d3b9e1d3419a056b50f513af66d3604dab0e1d6",
    "tested_installable_profile": "8ebe592498af4fd5d5a4517cd68e02b03400c68ed1040cc21fcb1e161192cf1e",
    "internal_agent_evidence": "511c1abfafec0a353e6f61e610a3a1969ace4eb0d70cd7afb61d3a3e31c5c6fb",
    "synthetic_harness_evidence": "fb026c59ffd134857a8008328f084c8b21f856a37a0ac01f836c4329ce86c79a",
}

PROOF_BOUNDARY = (
    "This fixed publication check binds the frozen Scope Control source, shelf, "
    "installable, and evidence identities and checks structural dispositions. It "
    "does not establish agent obedience, independent validation, portability, "
    "enforcement, safety, production reliability, or general effectiveness."
)


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def read_source(args: argparse.Namespace, package_root: Path) -> tuple[bytes, dict[str, str]]:
    if args.source_file:
        source_path = (package_root / args.source_file).resolve()
        return source_path.read_bytes(), {"source": "filesystem", "path": args.source_file}
    raw = subprocess.check_output(
        ["git", "show", f"{args.source_ref}:{CANONICAL_PATH.as_posix()}"],
        cwd=args.repo_root,
    )
    return raw, {
        "source": "git",
        "ref": args.source_ref,
        "path": CANONICAL_PATH.as_posix(),
    }


def check(package_root: Path, source_raw: bytes, source_identity: dict[str, str]) -> dict[str, object]:
    errors: list[str] = []
    files = {
        "canonical_product_profile": CANONICAL_PATH,
        "tested_installable_profile": INSTALLABLE_PATH,
        "internal_agent_evidence": AGENT_EVIDENCE_PATH,
        "synthetic_harness_evidence": SYNTHETIC_EVIDENCE_PATH,
    }
    observed_hashes: dict[str, str] = {}
    for identity, relative_path in files.items():
        path = package_root / relative_path
        if not path.is_file():
            errors.append(f"missing publication artifact: {relative_path.as_posix()}")
            continue
        observed_hashes[identity] = sha256(path.read_bytes())
        if observed_hashes[identity] != EXPECTED_HASHES[identity]:
            errors.append(f"frozen identity mismatch: {identity}")

    source_hash = sha256(source_raw)
    if source_hash != EXPECTED_HASHES["canonical_product_profile"]:
        errors.append("authoritative source hash does not match the frozen canonical identity")
    canonical_path = package_root / CANONICAL_PATH
    if canonical_path.is_file() and canonical_path.read_bytes() != source_raw:
        errors.append("publication shelf bytes differ from the authoritative canonical source")

    suite = HARNESS.load_json(package_root / SUITE_PATH)
    structural_results: dict[str, str] = {}
    for label, path in {
        "canonical_product_profile": canonical_path,
        "tested_installable_profile": package_root / INSTALLABLE_PATH,
        "vocabulary_without_structure": package_root / NEGATIVE_CONTROL_PATH,
    }.items():
        if not path.is_file():
            errors.append(f"missing structural input: {path.relative_to(package_root).as_posix()}")
            continue
        result = HARNESS.check_profile(suite, path.read_text(encoding="utf-8"))
        structural_results[label] = result["decision"]

    if structural_results.get("canonical_product_profile") != "PASS":
        errors.append("canonical product profile failed structural conformance")
    if structural_results.get("tested_installable_profile") != "PASS":
        errors.append("tested installable profile failed structural conformance")
    if structural_results.get("vocabulary_without_structure") != "FAIL":
        errors.append("vocabulary-only negative control did not fail")

    return {
        "check_id": "scope-control-publication-state-v0-1",
        "decision": "PASS" if not errors else "FAIL",
        "errors": errors,
        "source_identity": source_identity,
        "source_sha256": source_hash,
        "expected_hashes": EXPECTED_HASHES,
        "observed_hashes": observed_hashes,
        "structural_results": structural_results,
        "proof_boundary": PROOF_BOUNDARY,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the frozen Scope Control publication state")
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--source-file")
    source.add_argument("--source-ref", default="main")
    parser.add_argument("--package-root", type=Path, default=ROOT)
    parser.add_argument("--repo-root", type=Path, default=ROOT.parents[1])
    args = parser.parse_args()
    package_root = args.package_root.resolve()
    try:
        source_raw, source_identity = read_source(args, package_root)
        result = check(package_root, source_raw, source_identity)
    except (OSError, ValueError, subprocess.CalledProcessError, json.JSONDecodeError) as error:
        result = {
            "check_id": "scope-control-publication-state-v0-1",
            "decision": "FAIL",
            "errors": [str(error)],
            "proof_boundary": PROOF_BOUNDARY,
        }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result.get("decision") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
