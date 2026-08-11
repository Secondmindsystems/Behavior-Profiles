"""Frozen deterministic shell subset for Runtime v0.1."""

from __future__ import annotations

import re
from dataclasses import dataclass


FORBIDDEN = ("|", ">", "<", "&&", "||", ";", "$", "`", "*", "?", "%")
GET_CONTENT = re.compile(
    r'^Get-Content\s+-LiteralPath\s+(?:"(?P<double>[^"\r\n]+)"|\'(?P<single>[^\'\r\n]+)\'|(?P<bare>\S+))$',
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ShellParse:
    status: str
    reason_code: str | None
    target: str | None
    form_id: str | None


def parse(command: object) -> ShellParse:
    if not isinstance(command, str) or not command.strip():
        return ShellParse("BLOCK", "UNPARSEABLE_COMMAND", None, None)
    if any(token in command for token in FORBIDDEN):
        return ShellParse("BLOCK", "UNSUPPORTED_COMMAND_FORM", None, None)
    match = GET_CONTENT.fullmatch(command.strip())
    if not match:
        return ShellParse("BLOCK", "UNSUPPORTED_COMMAND_FORM", None, None)
    target = next(value for value in match.groupdict().values() if value is not None)
    if not target.strip():
        return ShellParse("BLOCK", "UNPARSEABLE_COMMAND", None, None)
    return ShellParse("PARSED", None, target, "powershell-get-content-literal-path")
