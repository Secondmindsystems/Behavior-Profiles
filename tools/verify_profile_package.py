#!/usr/bin/env python3
"""Fail-closed package and release verifier for Behavior Profiles."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_PATH = Path("profiles/scope-control/evidence/internal-dogfood-002.json")
CANONICAL_REF = "main"
CANONICAL_REPO_PATH = "products/behavior-profiles/scope-control/BEHAVIOR_PROFILE_SCOPE_CONTROL.md"
CANONICAL_PACKAGE_PATH = Path("scope-control/BEHAVIOR_PROFILE_SCOPE_CONTROL.md")
CANONICAL_SHA256 = "769385360202ad58557d52ab1d3b9e1d3419a056b50f513af66d3604dab0e1d6"
PACKAGE_PROFILE_PATH = Path("profiles/scope-control/BEHAVIOR_PROFILE.md")
PACKAGE_PROFILE_SHA256 = "8ebe592498af4fd5d5a4517cd68e02b03400c68ed1040cc21fcb1e161192cf1e"
PACKAGE_PROFILE_CLASSIFICATION = "EQUIVALENT_REPRESENTATION"
PROOF_BOUNDARY = (
    "Verifies package integrity and, in release mode, one declared internal dogfood record; "
    "does not establish universal agent obedience, safety, enforcement, cross-model consistency, "
    "production reliability, or general effectiveness."
)
REQUIRED_LIMITATION = (
    "This run records one agent's observable behavior under three frozen fixtures, one profile "
    "version, one adapter, one environment, and one observation method. It does not establish "
    "universal obedience, safety, enforcement, cross-model consistency, production reliability, "
    "or general effectiveness."
)

PACKAGE_REQUIRED_FILES = (
    "README.md",
    "BEHAVIOR_PROFILES.md",
    "FORMAT.md",
    "LICENSE",
    "TRADEMARKS.md",
    "CONTRIBUTING.md",
    "LIMITATIONS.md",
    "profiles/scope-control/README.md",
    "profiles/scope-control/BEHAVIOR_PROFILE.md",
    "profiles/scope-control/QUICK_TEST.md",
    "profiles/scope-control/LIMITATIONS.md",
    "profiles/scope-control/EVIDENCE_TEMPLATE.md",
    "profiles/scope-control/EVIDENCE_RECORD_TEMPLATE.json",
    "profiles/scope-control/DOGFOOD_PROTOCOL.md",
    "profiles/scope-control/DOGFOOD_MANIFEST.json",
    "scope-control/BEHAVIOR_PROFILE_SCOPE_CONTROL.md",
    "harness/harness.py",
    "harness/profiles/scope-control/suite.json",
    "adapters/agents-md/README.md",
    "adapters/claude-code/README.md",
    "adapters/generic/README.md",
    "tests/fixtures/authorized-execution/fixture.json",
    "tests/fixtures/expansion-pressure/fixture.json",
    "tests/fixtures/ambiguous-authority/fixture.json",
    ".github/workflows/validate.yml",
    ".github/ISSUE_TEMPLATE/installation-result.yml",
    ".github/ISSUE_TEMPLATE/recurring-behavior.yml",
)

REQUIRED_EVIDENCE_HEADINGS = (
    "## Campaign Classification",
    "## Role Separation",
    "## Session Isolation",
    "## Environment Identity",
    "## Profile Identity",
    "## Adapter Identity",
    "## Fixture Identity",
    "## Observable Conduct",
    "## Evaluation and Disposition",
    "## Manifest References",
    "## Limitations",
    "## Recurring Behavior Intake",
)

EVIDENCE_REQUIRED_FIELDS = (
    "run_id",
    "subject_agent",
    "model_identifier",
    "host_identifier",
    "operating_system",
    "timestamp_utc",
    "prior_context_state",
    "dogfood_manifest_reference",
    "profile",
    "adapter",
    "observation_harness",
    "evaluator",
    "sessions",
    "aggregate_disposition",
    "limitations_statement",
)

BANNED_URL_HOSTS = ("chatgpt.com", "claude.ai", "openai.com")
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text_sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def canonical_identity() -> dict[str, str]:
    return {
        "source": "git",
        "ref": CANONICAL_REF,
        "path": CANONICAL_REPO_PATH,
        "sha256": CANONICAL_SHA256,
    }


def canonical_label() -> str:
    return (
        f"ref={CANONICAL_REF} path={CANONICAL_REPO_PATH} "
        f"sha256={CANONICAL_SHA256}"
    )


def check_structural_profile(
    root: Path, profile_path: Path
) -> tuple[dict[str, object] | None, str | None]:
    harness_path = root / "harness/harness.py"
    suite_path = root / "harness/profiles/scope-control/suite.json"
    try:
        spec = importlib.util.spec_from_file_location(
            "behavior_profiles_package_harness", harness_path
        )
        if spec is None or spec.loader is None:
            return None, "could not load structural harness"
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        suite = json.loads(suite_path.read_text(encoding="utf-8"))
        profile_text = profile_path.read_text(encoding="utf-8")
        return module.check_profile(suite, profile_text), None
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        return None, f"structural harness input failed: {exc}"


def relative_markdown_links(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return [
        target
        for target in MARKDOWN_LINK.findall(text)
        if "://" not in target and not target.startswith("#")
    ]


def resolve_inside(root: Path, relative: object) -> Path | None:
    if not isinstance(relative, str) or not relative:
        return None
    resolved = (root / relative).resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError:
        return None
    return resolved


def fixture_map(root: Path, errors: list[str]) -> dict[str, tuple[Path, dict[str, object]]]:
    fixtures: dict[str, tuple[Path, dict[str, object]]] = {}
    for fixture_path in sorted((root / "tests/fixtures").glob("*/fixture.json")):
        try:
            fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"invalid fixture {fixture_path.relative_to(root).as_posix()}: {exc}")
            continue
        for field in ("fixture_id", "purpose", "prompt", "required_observations", "prohibited_actions"):
            if not fixture.get(field):
                errors.append(f"fixture missing {field}: {fixture_path.relative_to(root).as_posix()}")
        fixture_id = fixture.get("fixture_id")
        if not isinstance(fixture_id, str):
            continue
        if fixture_id in fixtures:
            errors.append(f"duplicate fixture_id: {fixture_id}")
        else:
            fixtures[fixture_id] = (fixture_path, fixture)
    return fixtures


def verify_package(root: Path = ROOT) -> dict[str, object]:
    errors: list[str] = []
    checks: list[str] = []

    for relative in PACKAGE_REQUIRED_FILES:
        path = root / relative
        if not path.is_file():
            errors.append(f"missing required file: {relative}")
        else:
            checks.append(f"required file present: {relative}")

    if errors:
        return decision("package", errors, checks, root)

    license_text = (root / "LICENSE").read_text(encoding="utf-8")
    if not license_text.startswith("MIT License"):
        errors.append("LICENSE is not MIT")
    else:
        checks.append("MIT license identified")

    canonical = root / CANONICAL_PACKAGE_PATH
    package_profile = root / PACKAGE_PROFILE_PATH
    if sha256(canonical) != CANONICAL_SHA256:
        errors.append(f"canonical Scope Control identity mismatch: {canonical_label()}")
    else:
        checks.append(f"canonical Scope Control identity bound: {canonical_label()}")

    canonical_structural, canonical_structural_error = check_structural_profile(root, canonical)
    if canonical_structural_error:
        errors.append(canonical_structural_error)
    elif canonical_structural is None or canonical_structural.get("decision") != "PASS":
        errors.append(
            f"canonical Scope Control fails structural conformance: {canonical_label()}"
        )
    elif len(canonical_structural.get("criteria", [])) != 19:
        errors.append(
            f"canonical Scope Control structural assertion count is not 19: {canonical_label()}"
        )
    else:
        checks.append(
            f"canonical Scope Control satisfies 19/19 structural assertions: {canonical_label()}"
        )

    package_structural, package_structural_error = check_structural_profile(root, package_profile)
    if sha256(package_profile) != PACKAGE_PROFILE_SHA256:
        errors.append("declared equivalent Scope Control representation hash mismatch")
    elif package_structural_error:
        errors.append(package_structural_error)
    elif package_structural is None or package_structural.get("decision") != "PASS":
        errors.append("declared equivalent Scope Control representation fails structural conformance")
    elif len(package_structural.get("criteria", [])) != 19:
        errors.append("equivalent Scope Control representation assertion count is not 19")
    else:
        checks.append(
            "package Scope Control profile is an EQUIVALENT_REPRESENTATION at "
            f"path={PACKAGE_PROFILE_PATH.as_posix()} sha256={PACKAGE_PROFILE_SHA256}; "
            "it satisfies the same 19/19 structural assertions and is not canonical; "
            f"canonical={canonical_label()}"
        )

    fixtures = fixture_map(root, errors)
    if len(fixtures) == 3:
        checks.append("three unique behavioral-triad fixtures parsed")
    else:
        errors.append(f"expected 3 unique fixtures, found {len(fixtures)}")

    manifest_path = root / "profiles/scope-control/DOGFOOD_MANIFEST.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"invalid dogfood manifest: {exc}")
        manifest = {}
    manifest_profile = manifest.get("profile", {}) if isinstance(manifest, dict) else {}
    manifest_adapter = manifest.get("adapter", {}) if isinstance(manifest, dict) else {}
    manifest_fixtures = manifest.get("fixtures", []) if isinstance(manifest, dict) else []
    if manifest_profile.get("path") != PACKAGE_PROFILE_PATH.as_posix():
        errors.append("dogfood manifest profile path mismatch")
    if manifest_profile.get("sha256") != sha256(package_profile):
        errors.append("dogfood manifest profile hash mismatch")
    adapter_path = root / "adapters/agents-md/README.md"
    if manifest_adapter.get("sha256") != sha256(adapter_path):
        errors.append("dogfood manifest adapter hash mismatch")
    manifest_by_id = {
        item.get("fixture_id"): item
        for item in manifest_fixtures
        if isinstance(item, dict) and item.get("fixture_id")
    }
    for fixture_id, (fixture_path, fixture) in fixtures.items():
        item = manifest_by_id.get(fixture_id, {})
        if item.get("sha256") != sha256(fixture_path):
            errors.append(f"dogfood manifest fixture hash mismatch: {fixture_id}")
        if item.get("prompt_sha256") != text_sha256(str(fixture.get("prompt", ""))):
            errors.append(f"dogfood manifest prompt hash mismatch: {fixture_id}")
    if set(manifest_by_id) != set(fixtures):
        errors.append("dogfood manifest fixture set mismatch")
    if not any("dogfood manifest" in error for error in errors):
        checks.append("dogfood manifest freezes profile, adapter, fixtures, and prompts")

    evidence_text = (root / "profiles/scope-control/EVIDENCE_TEMPLATE.md").read_text(encoding="utf-8")
    for heading in REQUIRED_EVIDENCE_HEADINGS:
        if heading not in evidence_text:
            errors.append(f"evidence template missing heading: {heading}")
    if all(heading in evidence_text for heading in REQUIRED_EVIDENCE_HEADINGS):
        checks.append("evidence template headings complete")

    for markdown in sorted(root.rglob("*.md")):
        content = markdown.read_text(encoding="utf-8")
        lowered = content.lower()
        for host in BANNED_URL_HOSTS:
            if f"https://{host}" in lowered or f"http://{host}" in lowered:
                errors.append(
                    f"prohibited drafting-tool URL in {markdown.relative_to(root).as_posix()}: {host}"
                )
        for target in relative_markdown_links(markdown):
            clean_target = target.split("#", 1)[0]
            if not clean_target:
                continue
            resolved = resolve_inside(root, (markdown.parent / clean_target).relative_to(root).as_posix())
            if resolved is None:
                errors.append(
                    f"relative link escapes package in {markdown.relative_to(root).as_posix()}: {target}"
                )
            elif not resolved.exists():
                errors.append(
                    f"broken relative link in {markdown.relative_to(root).as_posix()}: {target}"
                )
    if not any("link" in error for error in errors):
        checks.append("relative Markdown links resolve inside package")

    return decision("package", errors, checks, root)


def validate_release_evidence(root: Path, evidence: object) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    checks: list[str] = []
    if not isinstance(evidence, dict):
        return ["dogfood evidence root must be an object"], checks

    for field in EVIDENCE_REQUIRED_FIELDS:
        if field not in evidence or evidence[field] in (None, "", [], {}):
            errors.append(f"dogfood evidence missing field: {field}")

    if evidence.get("dogfood_manifest_reference") != "profiles/scope-control/DOGFOOD_MANIFEST.json":
        errors.append("dogfood evidence does not reference the frozen manifest")

    profile = evidence.get("profile")
    if isinstance(profile, dict):
        for field in ("profile_id", "version", "path", "sha256"):
            if not profile.get(field):
                errors.append(f"profile evidence missing field: {field}")
        profile_path = resolve_inside(root, profile.get("path"))
        if profile_path is None or not profile_path.is_file():
            errors.append("profile evidence path is missing or outside package")
        elif profile.get("sha256") != sha256(profile_path):
            errors.append("profile evidence hash does not match frozen profile")
        else:
            checks.append("profile identity and hash match")

    adapter = evidence.get("adapter")
    if isinstance(adapter, dict):
        for field in (
            "adapter_id",
            "version",
            "path",
            "sha256",
            "installed_instruction_reference",
            "installed_instruction_sha256",
        ):
            if not adapter.get(field):
                errors.append(f"adapter evidence missing field: {field}")
        adapter_path = resolve_inside(root, adapter.get("path"))
        if adapter_path is None or not adapter_path.is_file():
            errors.append("adapter evidence path is missing or outside package")
        elif adapter.get("sha256") != sha256(adapter_path):
            errors.append("adapter evidence hash does not match frozen adapter")
        else:
            checks.append("adapter identity and hash match")
        installed = resolve_inside(root, adapter.get("installed_instruction_reference"))
        if installed is None or not installed.is_file():
            errors.append("installed instruction reference is missing or outside package")
        elif adapter.get("installed_instruction_sha256") != sha256(installed):
            errors.append("installed instruction hash does not match referenced content")
        else:
            checks.append("installed instruction content is hash-bound")

    evaluator = evidence.get("evaluator")
    if not isinstance(evaluator, dict) or not evaluator.get("evaluator_id"):
        errors.append("evaluator identity is missing")
    elif evaluator.get("independent_from_subject") is not True:
        errors.append("evaluator must be declared independent from subject agent")
    else:
        checks.append("subject and evaluator roles are separated")

    harness = evidence.get("observation_harness")
    if not isinstance(harness, dict) or not harness.get("harness_id") or not harness.get("version"):
        errors.append("observation harness identity or version is missing")

    fixture_errors: list[str] = []
    fixtures = fixture_map(root, fixture_errors)
    errors.extend(fixture_errors)
    sessions = evidence.get("sessions")
    observed_fixture_ids: set[str] = set()
    session_ids: set[str] = set()
    dispositions: list[str] = []
    if not isinstance(sessions, list) or len(sessions) != 3:
        errors.append("dogfood campaign must contain exactly three fresh sessions")
    else:
        for index, session in enumerate(sessions, start=1):
            prefix = f"session {index}"
            if not isinstance(session, dict):
                errors.append(f"{prefix} must be an object")
                continue
            for field in (
                "session_id",
                "prior_context_state",
                "fixture_id",
                "fixture_sha256",
                "prompt_sha256",
                "disposition",
                "transcript_reference",
                "pre_run_manifest_reference",
                "post_run_manifest_reference",
            ):
                if not session.get(field):
                    errors.append(f"{prefix} missing field: {field}")
            session_id = session.get("session_id")
            if isinstance(session_id, str):
                if session_id in session_ids:
                    errors.append(f"duplicate session_id: {session_id}")
                session_ids.add(session_id)
            if session.get("prior_context_state") != "fresh_no_prior_fixture_or_second_mind_context":
                errors.append(f"{prefix} does not declare the required fresh-context state")
            fixture_id = session.get("fixture_id")
            if isinstance(fixture_id, str):
                observed_fixture_ids.add(fixture_id)
            if fixture_id not in fixtures:
                errors.append(f"{prefix} references unknown fixture: {fixture_id}")
            else:
                fixture_path, fixture = fixtures[fixture_id]
                if session.get("fixture_sha256") != sha256(fixture_path):
                    errors.append(f"{prefix} fixture hash mismatch")
                prompt = fixture.get("prompt")
                if not isinstance(prompt, str) or session.get("prompt_sha256") != text_sha256(prompt):
                    errors.append(f"{prefix} prompt hash mismatch")
            disposition = session.get("disposition")
            if disposition not in {"PASS", "FAIL", "CONFUSED"}:
                errors.append(f"{prefix} disposition must be PASS, FAIL, or CONFUSED")
            elif isinstance(disposition, str):
                dispositions.append(disposition)
            for reference_field in (
                "transcript_reference",
                "pre_run_manifest_reference",
                "post_run_manifest_reference",
            ):
                reference = resolve_inside(root, session.get(reference_field))
                if reference is None or not reference.is_file():
                    errors.append(f"{prefix} {reference_field} is missing or outside package")

    if observed_fixture_ids != set(fixtures):
        errors.append("dogfood sessions do not cover each frozen fixture exactly once")
    elif len(session_ids) == 3:
        checks.append("three fresh sessions cover the behavioral triad")

    aggregate = evidence.get("aggregate_disposition")
    if aggregate not in {
        "PASS_INTERNAL_DOGFOOD",
        "FAIL_INTERNAL_DOGFOOD",
        "CONFUSED_INTERNAL_DOGFOOD",
    }:
        errors.append("invalid aggregate_disposition")
    elif aggregate == "PASS_INTERNAL_DOGFOOD" and dispositions != ["PASS", "PASS", "PASS"]:
        errors.append("PASS_INTERNAL_DOGFOOD requires three PASS fixture dispositions")
    elif aggregate != "PASS_INTERNAL_DOGFOOD":
        errors.append(f"release blocked by aggregate disposition: {aggregate}")
    else:
        checks.append("aggregate disposition authorizes internal dogfood release gate")

    if evidence.get("limitations_statement") != REQUIRED_LIMITATION:
        errors.append("limitations statement does not match the required claim ceiling")
    else:
        checks.append("required limitations statement preserved")

    return errors, checks


def verify_release(root: Path = ROOT) -> dict[str, object]:
    package = verify_package(root)
    errors = list(package["errors"])
    checks = list(package["checks"])
    if errors:
        return decision("release", errors, checks, root)

    evidence_path = root / EVIDENCE_PATH
    if not evidence_path.is_file():
        errors.append(f"missing required dogfood evidence: {EVIDENCE_PATH.as_posix()}")
        return decision("release", errors, checks, root, blocked=True)
    try:
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"invalid dogfood evidence: {exc}")
        return decision("release", errors, checks, root)

    evidence_errors, evidence_checks = validate_release_evidence(root, evidence)
    errors.extend(evidence_errors)
    checks.extend(evidence_checks)
    return decision("release", errors, checks, root, blocked=bool(errors))


def verify(root: Path = ROOT, mode: str = "package") -> dict[str, object]:
    return verify_release(root) if mode == "release" else verify_package(root)


def decision(
    mode: str,
    errors: list[str],
    checks: list[str],
    root: Path,
    blocked: bool = False,
) -> dict[str, object]:
    return {
        "decision": "PASS" if not errors else ("BLOCKED" if blocked else "FAIL"),
        "mode": mode,
        "proof_boundary": PROOF_BOUNDARY,
        "package_root": root.resolve().as_posix(),
        "canonical_profile_identity": canonical_identity(),
        "package_profile_identity": {
            "classification": PACKAGE_PROFILE_CLASSIFICATION,
            "path": PACKAGE_PROFILE_PATH.as_posix(),
            "sha256": sha256(root / PACKAGE_PROFILE_PATH)
            if (root / PACKAGE_PROFILE_PATH).is_file()
            else None,
        },
        "checks": sorted(checks),
        "errors": sorted(errors),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("package", "release"), default="package")
    args = parser.parse_args()
    result = verify(mode=args.mode)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["decision"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
