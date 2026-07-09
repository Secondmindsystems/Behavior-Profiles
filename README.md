# Second Mind Systems

AI agents already have skills, tools, prompts, and workflows.

What they often lack is stable conduct.

Behavior Profiles are persistent behavioral overlays for AI agents. They do not add new capabilities. They shape how existing capabilities are used.

Skills expand capability.

Behavior Profiles govern conduct.

This repository introduces a public-safe learning path:

- [Behavior Profiles](papers/behavior-profiles.md)
- [Scope Control](scope-control/)
- [Governance Loops](governance-loops.md)
- [Protected Paths](protected-paths.md)

## Behavior Profiles

A Behavior Profile gives an AI agent standing behavior rules across tasks.

It can define how the agent handles scope, uncertainty, no-touch areas, completion notes, review boundaries, or escalation.

It is not another task skill. It is a behavioral layer around the skills the agent already has.

## Scope Control

[Behavior Profile: Scope Control](scope-control/) is a public-safe example profile for AI coding agents.

It helps make the task boundary visible before work starts, keeps the agent inside authorized scope, and returns a short completion note when the work is done.

## Governance Loops

[Governance Loops](governance-loops.md) describe how behavior can stay stable over time.

Execution loops help agents keep working until a stop condition is met.

Governance loops decide whether, where, and under what authority work may proceed.

## Protected Paths

[Protected Paths](protected-paths.md) is one concrete implementation further along the progression from behavior to reviewability to explicit local boundaries.

Behavior Profiles shape agent conduct.

Protected Paths governs the local commit path for marked files.

## Boundary

These materials are educational patterns and instruction-layer artifacts unless otherwise stated.

They are not enforcement software, security software, compliance systems, runtime authority, customer-validation claims, or replacements for human review.

See [Claim Boundary](CLAIM_BOUNDARY.md) for the public boundary of this shelf.
