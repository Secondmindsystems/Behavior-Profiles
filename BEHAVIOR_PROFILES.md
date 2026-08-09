# Behavior Profiles

## The Persistent Conduct Layer Behind Agent Skills

AI agents already have skills, tools, prompts, and workflows.

What they often lack is stable, reviewable conduct across those capabilities.

Skills describe what an agent knows how to do. A Behavior Profile describes how the agent is expected to conduct itself while doing it.

## Capability Is Not Conduct

A capable coding agent can edit one requested file. The same capability can also rewrite nearby documentation, update tests, run commands, or refactor adjacent code that was never authorized.

The failure is not always intelligence. It is often an invisible conduct decision:

- how the agent interpreted scope;
- whether it treated ambiguity as permission;
- whether it disclosed assumptions;
- whether it separated requested work from optional cleanup;
- whether it stopped at a boundary;
- whether it left enough evidence for review.

## What a Behavior Profile Is

A Behavior Profile is a portable conduct contract delivered through a durable agent-instruction surface.

It does not teach the agent a new task. It defines expected behavior that can remain relevant while tasks and skills change.

> The skill changes. The behavior rule persists.

Persistence belongs to the installed instruction artifact. It is not a claim that a model remembers, obeys, or applies the profile consistently across environments.

## Scope Control

Scope Control is the first reference profile in this repository.

It asks the agent to identify the requested task, authorized scope, no-touch boundaries, allowed actions, done condition, and stop condition before acting. It also asks the agent to return a completion note after work.

The intended result is not a perfect agent. It is a visible scope decision that a person can review.

## Reviewability Before Enforcement

Behavior Profiles make expected conduct explicit.

Fixtures make that conduct testable.

Evidence returns preserve what happened.

When a boundary cannot depend on instruction following, enforcement must take over. [Governed Repo](https://github.com/Secondmindsystems/governed-change-demo) demonstrates that stronger layer.

```text
Behavior
-> reviewability
-> enforcement
```

These layers complement one another. A profile is not enforcement software, and an enforcement gate does not replace the need to describe expected conduct.

## Open Reference, Not Universal Standard

This repository publishes one reference format, one complete free profile, installation guidance, pressure fixtures, an evidence template, and a package verifier.

The format is offered for use and improvement. It is not presented as an industry standard, certification system, safety framework, or proof that one profile behaves consistently across agents.

The first useful question is deliberately smaller:

> Can an outsider install the profile, exercise it, and clearly report PASS, FAIL, or CONFUSED?
