# Scope Control Runtime v0.1 — Architecture and Qualification

Scope Control Runtime v0.1 is a qualified experimental pre-action governance layer for Behavior Profile: Scope Control.

The public surface records what was built, what was demonstrated, and the limits of that evidence. The executable Runtime engine, causal host adapter, machine contract, shell policy, fixtures, and implementation tests are not distributed at active HEAD.

Architecture:

```text
canonical profile
→ machine contract
→ host-agnostic engine
→ separately qualified adapter
→ host interception surface
→ decision / effect / receipt
```

Qualification result:

> **Scope Control Runtime v0.1 evaluated proposed agent actions against a declared task boundary before execution through one qualified Claude Code PreToolUse integration surface on pinned Claude Code 2.1.137 in the tested Windows, authenticated-session topology. On the tested live subset, the host honored ALLOW, BLOCK, and DEFER decisions, and DEFER produced a distinct durable deferred item. ASK is qualified at the deterministic decision-engine level only; its live host projection remains unproven.**

The internal qualification reported `25/25` Runtime tests and a `16/16` paired engine matrix. ALLOW, BLOCK, and DEFER crossed the tested live host seam. ASK was qualified only at the deterministic engine level.

This evidence does not establish universal enforcement, a security boundary, production reliability, production readiness, arbitrary-shell understanding, cross-client compatibility, all Claude Code versions, other operating systems, unauthenticated topology, or live ASK host behavior.

See [`PUBLIC_RUNTIME_QUALIFICATION_MANIFEST_v0_1.json`](../PUBLIC_RUNTIME_QUALIFICATION_MANIFEST_v0_1.json) for frozen identities, evidence roles, and the complete limitation register.

The implementation appeared in earlier public commits. Those commits remain in ordinary Git history; this forward correction does not rewrite or erase that history.
