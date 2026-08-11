import copy
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
RUNTIME_ROOT = ROOT / "products/behavior-profiles/runtime"
import sys

sys.path.insert(0, str(RUNTIME_ROOT))

from adapters.claude_code import normalize_event, project, run  # noqa: E402
from scope_runtime.engine import evaluate  # noqa: E402


def authority(path, classes=("edit", "create")):
    return {
        "task_id": "adapter-task",
        "requested_task": "Exercise Adapter 001",
        "authorized_paths": [str(path)],
        "no_touch_paths": [],
        "authorized_action_classes": list(classes),
        "ask_conditions": ["MISSING_TARGET"],
        "schema_version": "0.1",
    }


def event(tool, tool_input, action_id="event-001"):
    return {
        "session_id": "session-001",
        "cwd": "C:/sandbox",
        "hook_event_name": "PreToolUse",
        "tool_name": tool,
        "tool_input": tool_input,
        "tool_use_id": action_id,
    }


def identity():
    return {
        "profile_sha": "profile",
        "contract_sha": "contract",
        "engine_sha": "engine",
        "adapter_sha": "adapter",
        "authority_schema_version": "0.1",
        "hook_schema_pin": "hook-pin",
        "host_version_pin": "host-pin",
    }


class ClaudeAdapterTests(unittest.TestCase):
    def test_write_existing_normalizes_to_edit(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "target.txt"
            target.write_text("before", encoding="utf-8")
            action = normalize_event(event("Write", {"file_path": str(target), "content": "after"}))
            self.assertEqual((action["action_id"], action["action_class"], action["target"]), ("event-001", "edit", str(target)))

    def test_write_missing_normalizes_to_create(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "target.txt"
            action = normalize_event(event("Write", {"file_path": str(target), "content": "after"}))
            self.assertEqual(action["action_class"], "create")

    def test_allow_projection(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "target.txt"
            target.write_text("before", encoding="utf-8")
            decision = evaluate(authority(target), normalize_event(event("Write", {"file_path": str(target), "content": "after"})))
            self.assertEqual(project(decision)["hookSpecificOutput"]["permissionDecision"], "allow")

    def test_block_projection(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "target.txt"
            target.write_text("before", encoding="utf-8")
            auth = authority(target, classes=("read",))
            decision = evaluate(auth, normalize_event(event("Write", {"file_path": str(target), "content": "after"})))
            self.assertEqual(project(decision)["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_ask_projection(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "target.txt"
            action = normalize_event(event("Edit", {"file_path": str(target)}))
            action["target"] = None
            action["structural_flags"] = ["MISSING_TARGET"]
            decision = evaluate(authority(target), action)
            self.assertEqual(project(decision)["hookSpecificOutput"]["permissionDecision"], "ask")

    def test_defer_projects_deny_and_persists_deferred_item(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            authorized = root / "authorized.txt"
            adjacent = root / "adjacent.txt"
            adjacent.write_text("before", encoding="utf-8")
            decision, projection, receipt = run(
                event("Write", {"file_path": str(adjacent), "content": "after"}, "event-defer"),
                authority(authorized),
                evidence_root=root / "evidence",
                identity_block=identity(),
                episode_id="episode-defer",
            )
            self.assertEqual((decision.runtime_decision, projection["hookSpecificOutput"]["permissionDecision"]), ("DEFER", "deny"))
            self.assertTrue((root / "evidence/deferred-items" / f"{receipt['deferred_item_id']}.json").is_file())

    def test_malformed_event_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            decision, projection, _ = run(
                {"hook_event_name": "PostToolUse", "tool_use_id": "malformed"},
                authority(root / "target.txt"),
                evidence_root=root / "evidence",
                identity_block=identity(),
                episode_id="episode-malformed",
            )
            self.assertEqual((decision.reason_code, projection["hookSpecificOutput"]["permissionDecision"]), ("MALFORMED_HOST_EVENT", "deny"))

    def test_bash_is_normalized_but_not_parsed_by_adapter(self):
        action = normalize_event(event("Bash", {"command": "Get-Content -LiteralPath C:/fixture/a.txt"}))
        self.assertEqual((action["action_class"], action["target"], action["command"]), ("shell_exec", None, "Get-Content -LiteralPath C:/fixture/a.txt"))

    def test_event_identity_reaches_receipt(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target = root / "target.txt"
            target.write_text("before", encoding="utf-8")
            _, _, receipt = run(
                event("Write", {"file_path": str(target), "content": "after"}, "same-action"),
                authority(target),
                evidence_root=root / "evidence",
                identity_block=identity(),
                episode_id="episode-identity",
            )
            self.assertEqual(receipt["host_event_id"], "same-action")

    def test_missing_identity_block_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target = root / "target.txt"
            target.write_text("before", encoding="utf-8")
            decision, projection, _ = run(
                event("Write", {"file_path": str(target), "content": "after"}),
                authority(target),
                evidence_root=root / "evidence",
                identity_block={},
                episode_id="episode-no-identity",
            )
            self.assertEqual((decision.reason_code, projection["hookSpecificOutput"]["permissionDecision"]), ("NO_LAWFUL_AUTHORITY_STATE", "deny"))


if __name__ == "__main__":
    unittest.main()
