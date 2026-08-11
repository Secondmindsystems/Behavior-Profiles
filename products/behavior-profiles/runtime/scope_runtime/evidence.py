"""Minimal receipt and deferred-item persistence for Runtime v0.1."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .engine import Decision


def _canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def persist_decision(
    decision: Decision,
    *,
    evidence_root: Path,
    episode_id: str,
    host_event_id: str,
    tool: str,
    identity_block: dict[str, str],
    timestamp: str | None = None,
) -> dict[str, Any]:
    ts = timestamp or datetime.now(timezone.utc).isoformat()
    seed = {
        "episode_id": episode_id,
        "host_event_id": host_event_id,
        "action_id": decision.action_id,
        "runtime_decision": decision.runtime_decision,
        "authority_task_id": decision.authority_task_id,
        "ts": ts,
    }
    receipt_id = hashlib.sha256(_canonical(seed)).hexdigest()
    deferred_item_id = None
    evidence_root.mkdir(parents=True, exist_ok=True)

    if decision.runtime_decision == "DEFER":
        if not decision.deferred_item:
            raise ValueError("DEFER_SEMANTICS_LOST")
        deferred = dict(decision.deferred_item)
        deferred.update({"episode_id": episode_id, "receipt_identity": receipt_id, "timestamp": ts})
        deferred_item_id = hashlib.sha256(_canonical(deferred)).hexdigest()
        deferred["deferred_item_id"] = deferred_item_id
        deferred_dir = evidence_root / "deferred-items"
        deferred_dir.mkdir(parents=True, exist_ok=True)
        (deferred_dir / f"{deferred_item_id}.json").write_text(
            json.dumps(deferred, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
        )

    receipt = {
        "ts": ts,
        "episode_id": episode_id,
        "host_event_id": host_event_id,
        "receipt_id": receipt_id,
        "tool": tool,
        "extracted_target": decision.extracted_target,
        "action_class": decision.action_class,
        "runtime_decision": decision.runtime_decision,
        "host_projection": decision.host_projection,
        "reason_code": decision.reason_code,
        "authority_task_id": decision.authority_task_id,
        "deferred_item_id": deferred_item_id,
        "identity_block": identity_block,
    }
    with (evidence_root / "action-receipts.jsonl").open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(receipt, sort_keys=True) + "\n")
    return receipt
