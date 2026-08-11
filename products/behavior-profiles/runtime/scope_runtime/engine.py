"""Pure deterministic Scope Control Runtime decision engine."""

from __future__ import annotations

import fnmatch
from dataclasses import asdict, dataclass
from typing import Any

from .shell_policy import parse as parse_shell


ACTION_CLASSES = {"read", "edit", "create", "delete", "shell_exec", "vcs_write"}
ASK_CONDITIONS = {"MULTIPLE_MATCHING_TARGETS", "MISSING_TARGET"}
AUTHORITY_FIELDS = {
    "task_id",
    "requested_task",
    "authorized_paths",
    "no_touch_paths",
    "authorized_action_classes",
    "ask_conditions",
    "schema_version",
}
ACTION_FIELDS = {
    "schema_version",
    "action_id",
    "action_class",
    "target",
    "target_candidates",
    "command",
    "structural_flags",
}


@dataclass(frozen=True)
class Decision:
    action_id: str
    action_class: str | None
    runtime_decision: str
    host_projection: str
    reason_code: str
    authority_task_id: str | None
    extracted_target: str | None
    question: str | None = None
    deferred_item: dict[str, Any] | None = None
    shell_form_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _block(
    action_id: str,
    reason: str,
    task_id: str | None = None,
    target: str | None = None,
    action_class: str | None = None,
) -> Decision:
    return Decision(action_id, action_class, "BLOCK", "deny", reason, task_id, target)


def _is_string_list(value: object) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) and item for item in value)


def validate_authority(authority: object) -> bool:
    if not isinstance(authority, dict) or set(authority) != AUTHORITY_FIELDS:
        return False
    if authority.get("schema_version") != "0.1":
        return False
    if not isinstance(authority.get("task_id"), str) or not authority["task_id"]:
        return False
    if not isinstance(authority.get("requested_task"), str) or not authority["requested_task"]:
        return False
    if not _is_string_list(authority.get("authorized_paths")):
        return False
    if not _is_string_list(authority.get("no_touch_paths")):
        return False
    classes = authority.get("authorized_action_classes")
    conditions = authority.get("ask_conditions")
    return (
        _is_string_list(classes)
        and set(classes) <= ACTION_CLASSES
        and len(classes) == len(set(classes))
        and _is_string_list(conditions)
        and set(conditions) <= ASK_CONDITIONS
        and len(conditions) == len(set(conditions))
    )


def validate_action(action: object) -> bool:
    if not isinstance(action, dict) or set(action) != ACTION_FIELDS:
        return False
    if action.get("schema_version") != "0.1":
        return False
    if not isinstance(action.get("action_id"), str) or not action["action_id"]:
        return False
    if action.get("action_class") not in ACTION_CLASSES:
        return False
    if action.get("target") is not None and not isinstance(action["target"], str):
        return False
    if not _is_string_list(action.get("target_candidates")):
        return False
    if action.get("command") is not None and not isinstance(action["command"], str):
        return False
    flags = action.get("structural_flags")
    return _is_string_list(flags) and set(flags) <= ASK_CONDITIONS and len(flags) == len(set(flags))


def normalize_path(value: str) -> str:
    normalized = value.replace("\\", "/").strip()
    while "//" in normalized:
        normalized = normalized.replace("//", "/")
    return normalized.casefold()


def matches_any(target: str, patterns: list[str]) -> bool:
    normalized = normalize_path(target)
    return any(fnmatch.fnmatchcase(normalized, normalize_path(pattern)) for pattern in patterns)


def evaluate(authority: object, action: object) -> Decision:
    action_id = action.get("action_id", "MALFORMED") if isinstance(action, dict) else "MALFORMED"
    if not validate_authority(authority):
        return _block(action_id, "NO_LAWFUL_AUTHORITY_STATE")
    task_id = authority["task_id"]
    if not validate_action(action):
        return _block(action_id, "MALFORMED_HOST_EVENT", task_id)

    action_class = action["action_class"]
    target = action["target"]
    shell_form_id = None

    if action_class == "shell_exec":
        parsed = parse_shell(action["command"])
        if parsed.status == "BLOCK":
            return _block(action_id, parsed.reason_code or "UNPARSEABLE_COMMAND", task_id, action_class=action_class)
        target = parsed.target
        shell_form_id = parsed.form_id

    if target and matches_any(target, authority["no_touch_paths"]):
        return _block(action_id, "NO_TOUCH_TARGET", task_id, target, action_class)

    if action_class not in authority["authorized_action_classes"]:
        return _block(action_id, "UNAUTHORIZED_ACTION_CLASS", task_id, target, action_class)

    active_flags = set(action["structural_flags"]) & set(authority["ask_conditions"])
    if "MULTIPLE_MATCHING_TARGETS" in active_flags and len(action["target_candidates"]) > 1:
        choices = ", ".join(action["target_candidates"])
        return Decision(
            action_id,
            action_class,
            "ASK",
            "ask",
            "MULTIPLE_MATCHING_TARGETS",
            task_id,
            target,
            question=f"Which authorized target should be used: {choices}?",
        )
    if "MISSING_TARGET" in active_flags and not target:
        return Decision(
            action_id,
            action_class,
            "ASK",
            "ask",
            "MISSING_TARGET",
            task_id,
            None,
            question="Which authorized target should be used?",
        )

    if not target:
        return _block(action_id, "MALFORMED_HOST_EVENT", task_id, action_class=action_class)

    if matches_any(target, authority["authorized_paths"]):
        return Decision(
            action_id,
            action_class,
            "ALLOW",
            "allow",
            "AUTHORIZED_ACTION",
            task_id,
            target,
            shell_form_id=shell_form_id,
        )

    deferred_item = {
        "proposed_action": action_id,
        "target": target,
        "action_class": action_class,
        "authority_task_id": task_id,
        "deferral_reason": "outside active authorized paths and not no-touch",
    }
    return Decision(
        action_id,
        action_class,
        "DEFER",
        "deny",
        "DEFERRED_ADJACENT",
        task_id,
        target,
        deferred_item=deferred_item,
        shell_form_id=shell_form_id,
    )
