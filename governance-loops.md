# Governance Loops

Execution loops help an agent continue working until a stop condition is met.

Governance loops decide whether, where, and under what authority work may proceed.

## Basic Shape

```text
Intent
-> authority
-> context
-> scope
-> action
-> evidence
-> stop or continue
```

- Intent: What is being requested?
- Authority: Who may authorize the action?
- Context: What information is relevant?
- Scope: What is inside and outside the task?
- Action: What bounded work is performed?
- Evidence: What can a reviewer inspect?
- Stop or continue: Has the done condition been met, or is more authority needed?

## Scope-Control Loop

```text
Task arrives
-> state the boundary
-> act inside it
-> flag expansion pressure
-> return completion evidence
```

## Claim-Boundary Loop

```text
Before asserting
-> identify evidence state
-> match claim strength to evidence
-> assert, qualify, or hold
```

## Boundary

These are public explanatory patterns, not runtime, enforcement software, or proof that an agent followed them.
