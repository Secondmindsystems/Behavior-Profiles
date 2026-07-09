# Governance Loops

Governance Loops help keep agent behavior stable over time.

They are complementary to execution loops.

Execution loops decide when an agent works.

Governance loops decide whether, where, and under what authority it may work.

## Shape

```text
Intent
-> Authority
-> Context
-> Scope
-> Action
-> Evidence
-> Receipt
-> Stop
```

- Intent: What is being asked?
- Authority: Is the agent allowed to act?
- Context: What information is relevant?
- Scope: What is in bounds and out of bounds?
- Action: What bounded work is performed?
- Evidence: What supports the result?
- Receipt: What changed and why?
- Stop: When does the loop end or escalate?

Governance Loops are not a replacement for execution loops. They describe a behavioral control layer around execution.

## Feedback-to-Decision Loop

```text
Feedback
-> classify
-> accept / revise / reject / escalate
-> record
-> next action
```

Use this when feedback arrives and the agent needs to decide what to do with it.

The key behavior is classification before action.

This is a pattern, not enforcement software.

## Claim Boundary Loop

```text
Before asserting
-> classify status as verified / inferred / remembered / uncertain
-> state appropriately
-> assert or hold
```

Use this when an agent is about to make a claim.

The key behavior is matching claim strength to evidence state.

This is a pattern, not enforcement software.

## Action Receipt Loop

```text
Around consequential work
-> record who / what / sources / boundary / evidence / next review point
```

Use this when work has enough consequence that a human should be able to review what happened.

The key behavior is leaving a useful record after consequential work.

This is a pattern, not enforcement software.

## Agent Brakes Loop

```text
At expansion pressure
-> check authority and scope
-> if outside, stop and flag
```

Use this when the agent notices a useful adjacent task, cleanup, refactor, or broader move.

The key behavior is flagging expansion pressure instead of silently acting on it.

This is a pattern, not enforcement software.
