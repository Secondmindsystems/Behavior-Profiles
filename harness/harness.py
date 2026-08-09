from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROOF_BOUNDARY = (
    "This record tests frozen structural requirements and deterministic fixture judging. "
    "Synthetic controls are not agent evidence. It does not establish agent obedience, "
    "cross-client conformance, portability, enforcement, safety, certification, "
    "production reliability, or general effectiveness."
)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_suite(suite: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in ("suite_id", "profile_id", "profile_contract", "fixtures", "claim_ceiling"):
        if field not in suite:
            errors.append(f"suite missing field: {field}")

    contract = suite.get("profile_contract", {})
    assertions = contract.get("assertions")
    if not isinstance(assertions, list) or not assertions:
        errors.append("profile_contract.assertions must be a non-empty list")
    else:
        assertion_ids: set[str] = set()
        allowed_kinds = {"literal", "ordered_item", "unordered_item"}
        for index, assertion in enumerate(assertions):
            prefix = f"profile_contract.assertions[{index}]"
            if not isinstance(assertion, dict):
                errors.append(f"{prefix} must be an object")
                continue
            for field in ("id", "kind", "value"):
                if not isinstance(assertion.get(field), str) or not assertion[field]:
                    errors.append(f"{prefix}.{field} must be a non-empty string")
            assertion_id = assertion.get("id")
            if assertion_id in assertion_ids:
                errors.append(f"duplicate structural assertion id: {assertion_id}")
            if isinstance(assertion_id, str):
                assertion_ids.add(assertion_id)
            kind = assertion.get("kind")
            if kind not in allowed_kinds:
                errors.append(f"{prefix}.kind must be one of {sorted(allowed_kinds)}")
            if kind in {"ordered_item", "unordered_item"} and not isinstance(
                assertion.get("section"), str
            ):
                errors.append(f"{prefix}.section must be a string for list-item assertions")

    fixtures = suite.get("fixtures")
    if not isinstance(fixtures, list) or not fixtures:
        errors.append("fixtures must be a non-empty list")
        return errors

    seen: set[str] = set()
    for index, fixture in enumerate(fixtures):
        prefix = f"fixtures[{index}]"
        if not isinstance(fixture, dict):
            errors.append(f"{prefix} must be an object")
            continue
        for field in (
            "fixture_id",
            "behavior_dimension",
            "purpose",
            "prompt",
            "required_events",
            "prohibited_events",
        ):
            if field not in fixture:
                errors.append(f"{prefix} missing field: {field}")
        fixture_id = fixture.get("fixture_id")
        if fixture_id in seen:
            errors.append(f"duplicate fixture_id: {fixture_id}")
        if isinstance(fixture_id, str):
            seen.add(fixture_id)
        required = fixture.get("required_events", [])
        prohibited = fixture.get("prohibited_events", [])
        if not _valid_event_list(required):
            errors.append(f"{prefix}.required_events must contain unique id/description objects")
        if not _valid_event_list(prohibited):
            errors.append(f"{prefix}.prohibited_events must contain unique id/description objects")
        required_ids = _event_ids(required)
        prohibited_ids = _event_ids(prohibited)
        overlap = required_ids & prohibited_ids
        if overlap:
            errors.append(f"{prefix} event ids are both required and prohibited: {sorted(overlap)}")
    return errors


def _valid_event_list(events: Any) -> bool:
    if not isinstance(events, list) or not events:
        return False
    ids: list[str] = []
    for event in events:
        if not isinstance(event, dict):
            return False
        if not isinstance(event.get("id"), str) or not isinstance(event.get("description"), str):
            return False
        ids.append(event["id"])
    return len(ids) == len(set(ids))


def _event_ids(events: list[dict[str, str]]) -> set[str]:
    return {event["id"] for event in events if isinstance(event, dict) and "id" in event}


def fixture_map(suite: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {fixture["fixture_id"]: fixture for fixture in suite["fixtures"]}


def _structural_lines(profile_text: str) -> list[str]:
    lines: list[str] = []
    fence_character: str | None = None
    fence_start = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
    for line in profile_text.splitlines():
        marker = fence_start.match(line)
        if fence_character is not None:
            if marker is not None and marker.group(1)[0] == fence_character:
                fence_character = None
            continue
        if marker is not None:
            fence_character = marker.group(1)[0]
            continue
        lines.append(line)
    return lines


def _section_lines(lines: list[str]) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current_section: str | None = None
    for line in lines:
        if line.startswith("## "):
            current_section = line[3:].strip()
            sections.setdefault(current_section, [])
        elif current_section is not None:
            sections[current_section].append(line)
    return sections


def _assertion_present(
    assertion: dict[str, str], lines: list[str], sections: dict[str, list[str]]
) -> bool:
    kind = assertion["kind"]
    value = assertion["value"]
    if kind == "literal":
        candidate_lines = sections.get(assertion["section"], []) if assertion.get("section") else lines
        return any(line.strip() == value for line in candidate_lines)

    section = sections.get(assertion["section"], [])
    if kind == "ordered_item":
        # Ordered marker spelling is intentionally not normalized in this campaign.
        return any(line.strip() == value for line in section)

    unordered_item = re.compile(r"^\s{0,3}[*+-]\s+(.+?)\s*$")
    return any(
        match is not None and match.group(1) == value
        for line in section
        for match in [unordered_item.match(line)]
    )


def check_profile(suite: dict[str, Any], profile_text: str) -> dict[str, Any]:
    suite_errors = validate_suite(suite)
    if suite_errors:
        return {"decision": "FAIL", "errors": suite_errors, "criteria": []}

    lines = _structural_lines(profile_text)
    sections = _section_lines(lines)
    criteria = []
    for assertion in suite["profile_contract"]["assertions"]:
        present = _assertion_present(assertion, lines, sections)
        criteria.append(
            {
                "assertion_id": assertion["id"],
                "kind": assertion["kind"],
                "section": assertion.get("section"),
                "value": assertion["value"],
                "status": "PASS" if present else "FAIL",
            }
        )
    errors = [
        f"profile missing structural assertion: {item['assertion_id']}"
        for item in criteria
        if item["status"] == "FAIL"
    ]
    return {
        "decision": "PASS" if not errors else "FAIL",
        "errors": errors,
        "criteria": criteria,
        "proof_boundary": PROOF_BOUNDARY,
    }


def validate_observation(observation: dict[str, Any], fixture: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in (
        "observation_id",
        "fixture_id",
        "evidence_class",
        "observed_events",
        "indeterminate_events",
        "source_references",
    ):
        if field not in observation:
            errors.append(f"observation missing field: {field}")

    if observation.get("fixture_id") != fixture.get("fixture_id"):
        errors.append("observation fixture_id does not match fixture")
    if observation.get("evidence_class") not in {
        "agent_observation",
        "synthetic_control",
        "human_evaluation",
    }:
        errors.append("observation evidence_class is invalid")

    observed = observation.get("observed_events", [])
    indeterminate = observation.get("indeterminate_events", [])
    if not isinstance(observed, list) or not all(isinstance(item, str) for item in observed):
        errors.append("observed_events must be a string list")
        observed = []
    if not isinstance(indeterminate, list) or not all(isinstance(item, str) for item in indeterminate):
        errors.append("indeterminate_events must be a string list")
        indeterminate = []
    if set(observed) & set(indeterminate):
        errors.append("an event cannot be both observed and indeterminate")

    allowed = _event_ids(fixture["required_events"]) | _event_ids(fixture["prohibited_events"])
    unknown = (set(observed) | set(indeterminate)) - allowed
    if unknown:
        errors.append(f"observation contains unknown event ids: {sorted(unknown)}")
    if not isinstance(observation.get("source_references"), list):
        errors.append("source_references must be a list")
    return errors


def judge_observation(suite: dict[str, Any], observation: dict[str, Any]) -> dict[str, Any]:
    suite_errors = validate_suite(suite)
    if suite_errors:
        return {"decision": "FAIL", "errors": suite_errors}

    fixtures = fixture_map(suite)
    fixture = fixtures.get(observation.get("fixture_id"))
    if fixture is None:
        return {"decision": "FAIL", "errors": ["unknown fixture_id"]}

    errors = validate_observation(observation, fixture)
    if errors:
        return {"decision": "FAIL", "errors": errors, "fixture_id": fixture["fixture_id"]}

    observed = set(observation["observed_events"])
    indeterminate = set(observation["indeterminate_events"])
    required = _event_ids(fixture["required_events"])
    prohibited = _event_ids(fixture["prohibited_events"])
    missing = sorted(required - observed - indeterminate)
    prohibited_hits = sorted(prohibited & observed)
    indeterminate_required = sorted(required & indeterminate)

    criteria = []
    for event in fixture["required_events"]:
        event_id = event["id"]
        if event_id in observed:
            status = "PASS"
        elif event_id in indeterminate:
            status = "CONFUSED"
        else:
            status = "FAIL"
        criteria.append({"event_id": event_id, "kind": "required", "status": status})
    for event in fixture["prohibited_events"]:
        event_id = event["id"]
        criteria.append(
            {
                "event_id": event_id,
                "kind": "prohibited",
                "status": "FAIL" if event_id in observed else "PASS",
            }
        )

    if prohibited_hits or missing:
        decision = "FAIL"
    elif indeterminate_required:
        decision = "CONFUSED"
    else:
        decision = "PASS"

    return {
        "decision": decision,
        "errors": [],
        "fixture_id": fixture["fixture_id"],
        "observation_id": observation["observation_id"],
        "evidence_class": observation["evidence_class"],
        "criteria": criteria,
        "missing_required_events": missing,
        "prohibited_events_observed": prohibited_hits,
        "indeterminate_required_events": indeterminate_required,
        "source_references": observation["source_references"],
        "proof_boundary": PROOF_BOUNDARY,
    }


def run_controls(
    suite: dict[str, Any],
    controls: dict[str, Any],
    profile_text: str | None = None,
    profile_identity: dict[str, str] | None = None,
    profile_sha256: str | None = None,
) -> dict[str, Any]:
    suite_errors = validate_suite(suite)
    if suite_errors:
        return {"decision": "FAIL", "errors": suite_errors}
    observations = controls.get("observations")
    if not isinstance(observations, list):
        return {"decision": "FAIL", "errors": ["controls.observations must be a list"]}

    results = []
    expectation_errors = []
    dispositions_by_fixture: dict[str, set[str]] = {key: set() for key in fixture_map(suite)}
    for observation in observations:
        result = judge_observation(suite, observation)
        expected = observation.get("expected_disposition")
        result["expected_disposition"] = expected
        result["expectation_matched"] = result.get("decision") == expected
        results.append(result)
        fixture_id = observation.get("fixture_id")
        if fixture_id in dispositions_by_fixture:
            dispositions_by_fixture[fixture_id].add(result.get("decision", "FAIL"))
        if not result["expectation_matched"]:
            expectation_errors.append(
                f"{observation.get('observation_id', '<unknown>')} expected {expected} but got {result.get('decision')}"
            )

    discrimination = {}
    for fixture_id, dispositions in dispositions_by_fixture.items():
        passed = "PASS" in dispositions and "FAIL" in dispositions
        discrimination[fixture_id] = {
            "status": "PASS" if passed else "FAIL",
            "observed_dispositions": sorted(dispositions),
        }
        if not passed:
            expectation_errors.append(f"fixture lacks PASS/FAIL discrimination: {fixture_id}")

    structural_profile_check = None
    if profile_text is not None:
        structural_result = check_profile(suite, profile_text)
        structural_profile_check = {
            "decision": structural_result["decision"],
            "errors": structural_result["errors"],
            "profile_identity": profile_identity,
            "profile_sha256": profile_sha256
            or hashlib.sha256(profile_text.encode("utf-8")).hexdigest(),
            "assertion_count": len(structural_result["criteria"]),
        }
        if structural_result["decision"] != "PASS":
            expectation_errors.append("structural profile check did not pass")

    return {
        "record_type": "synthetic_harness_control_run",
        "suite_id": suite["suite_id"],
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": "PASS" if not expectation_errors else "FAIL",
        "errors": expectation_errors,
        "structural_profile_check": structural_profile_check,
        "results": results,
        "discrimination": discrimination,
        "claim_ceiling": suite["claim_ceiling"],
        "proof_boundary": PROOF_BOUNDARY,
    }


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def add_profile_source_arguments(parser: argparse.ArgumentParser) -> None:
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--profile", type=Path)
    source.add_argument("--git-ref")
    parser.add_argument("--git-path")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())


def read_profile_source(args: argparse.Namespace) -> tuple[str, dict[str, str], str]:
    if args.profile is not None:
        raw = args.profile.read_bytes()
        identity = {"source": "filesystem", "path": args.profile.as_posix()}
    else:
        if not args.git_path:
            raise ValueError("--git-path is required with --git-ref")
        raw = subprocess.check_output(
            ["git", "show", f"{args.git_ref}:{args.git_path}"],
            cwd=args.repo_root,
        )
        identity = {
            "source": "git",
            "ref": args.git_ref,
            "path": args.git_path,
        }
    return raw.decode("utf-8"), identity, hashlib.sha256(raw).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Behavior Profiles conformance harness")
    subparsers = parser.add_subparsers(dest="command", required=True)

    profile_parser = subparsers.add_parser("check-profile")
    profile_parser.add_argument("--suite", type=Path, required=True)
    add_profile_source_arguments(profile_parser)

    judge_parser = subparsers.add_parser("judge")
    judge_parser.add_argument("--suite", type=Path, required=True)
    judge_parser.add_argument("--observation", type=Path, required=True)

    controls_parser = subparsers.add_parser("run-controls")
    controls_parser.add_argument("--suite", type=Path, required=True)
    controls_parser.add_argument("--observations", type=Path, required=True)
    add_profile_source_arguments(controls_parser)
    controls_parser.add_argument("--output", type=Path)

    args = parser.parse_args()
    suite = load_json(args.suite)
    if args.command == "check-profile":
        profile_text, profile_identity, profile_sha256 = read_profile_source(args)
        result = check_profile(suite, profile_text)
        result["profile_identity"] = profile_identity
        result["profile_sha256"] = profile_sha256
    elif args.command == "judge":
        result = judge_observation(suite, load_json(args.observation))
    else:
        profile_text, profile_identity, profile_sha256 = read_profile_source(args)
        result = run_controls(
            suite,
            load_json(args.observations),
            profile_text=profile_text,
            profile_identity=profile_identity,
            profile_sha256=profile_sha256,
        )
        if args.output:
            write_json(args.output, result)

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result.get("decision") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
