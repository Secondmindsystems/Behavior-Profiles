"""Claude Code Adapter 001 for the pinned PreToolUse surface."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scope_runtime.engine import Decision, evaluate
from scope_runtime.evidence import persist_decision


IDENTITY_FIELDS = {
    "profile_sha",
    "contract_sha",
    "engine_sha",
    "adapter_sha",
    "authority_schema_version",
    "hook_schema_pin",
    "host_version_pin",
}


def valid_identity_block(identity: object) -> bool:
    return (
        isinstance(identity, dict)
        and set(identity) == IDENTITY_FIELDS
        and all(isinstance(value, str) and value for value in identity.values())
    )


def normalize_event(event: object) -> dict[str, Any]:
    if not isinstance(event, dict):
        return {}
    tool = event.get("tool_name")
    tool_input = event.get("tool_input")
    action_id = event.get("tool_use_id")
    if event.get("hook_event_name") != "PreToolUse" or not isinstance(tool_input, dict):
        return {"action_id": action_id} if isinstance(action_id, str) else {}

    target = None
    command = None
    if tool == "Write":
        target = tool_input.get("file_path")
        action_class = "edit" if isinstance(target, str) and Path(target).exists() else "create"
    elif tool == "Edit":
        target = tool_input.get("file_path")
        action_class = "edit"
    elif tool == "Read":
        target = tool_input.get("file_path")
        action_class = "read"
    elif tool == "Bash":
        command = tool_input.get("command")
        action_class = "shell_exec"
    else:
        return {"action_id": action_id} if isinstance(action_id, str) else {}

    return {
        "schema_version": "0.1",
        "action_id": action_id,
        "action_class": action_class,
        "target": target,
        "target_candidates": [],
        "command": command,
        "structural_flags": [],
    }


def project(decision: Decision) -> dict[str, Any]:
    if decision.runtime_decision == "DEFER" and decision.host_projection != "deny":
        raise ValueError("DEFER_SEMANTICS_LOST")
    if decision.host_projection not in {"allow", "deny", "ask"}:
        raise ValueError("unsupported host projection")
    reason = f"{decision.runtime_decision}: {decision.reason_code}"
    if decision.question:
        reason = decision.question
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision.host_projection,
            "permissionDecisionReason": reason,
        }
    }


def run(
    event: object,
    authority: object,
    *,
    evidence_root: Path,
    identity_block: dict[str, str],
    episode_id: str,
) -> tuple[Decision, dict[str, Any], dict[str, Any]]:
    action = normalize_event(event)
    decision = evaluate(authority if valid_identity_block(identity_block) else None, action)
    host_event_id = event.get("tool_use_id", "MALFORMED") if isinstance(event, dict) else "MALFORMED"
    tool = event.get("tool_name", "UNKNOWN") if isinstance(event, dict) else "UNKNOWN"
    receipt = persist_decision(
        decision,
        evidence_root=evidence_root,
        episode_id=episode_id,
        host_event_id=host_event_id,
        tool=tool,
        identity_block=identity_block,
    )
    return decision, project(decision), receipt


def render_projection(projection: dict[str, Any]) -> str:
    return json.dumps(projection, sort_keys=True, separators=(",", ":"))
