#!/usr/bin/env python3
"""Project Scope Control Runtime decisions onto Claude Code PreToolUse."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


RUNTIME_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUNTIME_ROOT))

from adapters.claude_code import render_projection, run  # noqa: E402


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--authority", type=Path, required=True)
    parser.add_argument("--identity", type=Path, required=True)
    parser.add_argument("--evidence-root", type=Path, required=True)
    parser.add_argument("--episode-id", required=True)
    args = parser.parse_args()

    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, UnicodeDecodeError):
        event = None
    try:
        authority = read_json(args.authority)
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        authority = None
    try:
        identity = read_json(args.identity)
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        identity = {}

    _, projection, _ = run(
        event,
        authority,
        evidence_root=args.evidence_root,
        identity_block=identity,
        episode_id=args.episode_id,
    )
    print(render_projection(projection))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
