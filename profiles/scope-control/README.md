# Behavior Profile: Scope Control

Scope Control is an instruction profile for AI coding agents that helps keep a bounded task bounded.

You ask an agent to fix one file. It notices nearby cleanup, another issue, or a refactor that might be useful. The agent may be capable of doing all of it, and it may even have access to the entire repository. That still doesn't mean the extra work belongs to the task.

Scope Control asks the agent to make that boundary explicit before it starts.

## What It Asks the Agent to Do

Before acting, the agent identifies:

* the requested task;
* what it is authorized to work on;
* what should remain untouched;
* which actions are allowed;
* what counts as done; and
* when it should stop, defer work, or ask for clarification.

After the task, it returns a short completion note describing what it changed and what it left alone.

The idea is simple: **make scope decisions visible instead of letting them happen silently.**

## Install

Use the complete [BEHAVIOR_PROFILE.md](BEHAVIOR_PROFILE.md) with the instruction surface your agent reads:

* [AGENTS.md](../../adapters/agents-md/README.md)
* [Claude Code / CLAUDE.md](../../adapters/claude-code/README.md)
* [Other durable instruction surfaces](../../adapters/generic/README.md)

Check your agent's instruction precedence so you know the profile applies to the workspace where you're using it.

## Try It

Start with [TRY_IT](TRY_IT.md). It gives you three short situations:

* **ACT** when the requested action and boundary are clear.
* **DEFER** adjacent work that falls outside the request.
* **STOP** when the target or authority is incomplete.

For a shorter structural check, use [QUICK_TEST](QUICK_TEST.md).

## Record What Happened

Use the [evidence template](EVIDENCE_TEMPLATE.md) to record `PASS`, `FAIL`, or `CONFUSED`.

Record the environment, profile version, task, expected conduct, observed conduct, and anything that made the result difficult to interpret.

## When Instruction Is Not Enough

Scope Control supplies instructions. It does not block files or commands.

When a repository boundary needs an executable checkpoint, use a separate control. [AI Protected Paths](https://github.com/Secondmindsystems/ai-protected-paths) requires one-use approval before configured paths can enter a local Git commit.

See [LIMITATIONS](LIMITATIONS.md) for the profile's operating boundaries.

## About Behavior Profiles

Scope Control is the first reference [Behavior Profile](../../README.md). For the broader category and the other public work, return to [Behavior Profiles](../../README.md).
