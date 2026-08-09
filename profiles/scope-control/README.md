# Behavior Profile: Scope Control

Scope Control is a free conduct contract for AI coding agents.

It asks an agent to make the task boundary visible before work, remain inside authorized scope, and return a short completion note afterward.

## Install

Use [BEHAVIOR_PROFILE.md](BEHAVIOR_PROFILE.md) with one of the documented installation surfaces:

- [AGENTS.md](../../adapters/agents-md/README.md)
- [Claude Code](../../adapters/claude-code/README.md)
- [Generic instructions](../../adapters/generic/README.md)

## Test

Run the [quick test](QUICK_TEST.md), then use the [evidence template](EVIDENCE_TEMPLATE.md) to record `PASS`, `FAIL`, or `CONFUSED`.

The expected result is observable scope discipline, not proof of universal obedience.

## Failure Addressed

The agent quietly expands a bounded task by editing, inspecting, cleaning up, refactoring, or running commands outside the requested boundary.

## Bypass

The profile can be removed, overridden, shadowed, misunderstood, or ignored. It does not block files or commands.

See [LIMITATIONS.md](LIMITATIONS.md).
