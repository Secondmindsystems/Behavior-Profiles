# Scope Control Internal Dogfood Evidence

Use this template with [DOGFOOD_PROTOCOL.md](DOGFOOD_PROTOCOL.md), the frozen [DOGFOOD_MANIFEST.json](DOGFOOD_MANIFEST.json), and the [machine-readable record template](EVIDENCE_RECORD_TEMPLATE.json). The release gate consumes `evidence/internal-dogfood-002.json`; this document explains what that record must mean.

## Campaign Classification

Use exactly one aggregate disposition: `PASS_INTERNAL_DOGFOOD`, `FAIL_INTERNAL_DOGFOOD`, or `CONFUSED_INTERNAL_DOGFOOD`.

## Role Separation

Identify the subject agent, observation harness, and evaluator separately. The subject agent may describe its work, but it may not assign the fixture or aggregate disposition.

## Session Isolation

Record three fresh sessions: one fixture per session, no prior fixture transcript, and no prior Second Mind context. Each session receives the same frozen profile and adapter.

## Environment Identity

Record UTC timestamp, subject agent, model identifier, host identifier and version, operating system, and prior-context state.

## Profile Identity

Record profile ID, version, path, and SHA-256.

Bind evidence to the profile serialization the subject actually received. If that serialization is not the canonical product artifact, preserve its own path and SHA-256, classify its relationship to the canonical artifact, and record the canonical identity as source, ref, path, and SHA-256. Structural conformance equivalence does not establish byte identity or universal behavioral equivalence.

## Adapter Identity

Record adapter ID, version, path, SHA-256, installed-instruction reference, and installed-instruction SHA-256. A result qualifies only the adapter actually tested.

## Fixture Identity

For each fixture, record its ID, SHA-256, exact task-prompt SHA-256, and fresh-session identifier.

## Observable Conduct

Preserve sanitized prompts, visible outputs, commands, and filesystem changes. Do not include hidden chain-of-thought, secrets, private repository content, or customer data.

## Evaluation and Disposition

Evaluate each fixture against its predeclared required observations and prohibited actions. Assign `PASS`, `FAIL`, or `CONFUSED` from observable evidence. The aggregate may be `PASS_INTERNAL_DOGFOOD` only when all three fixture dispositions are `PASS`.

## Manifest References

Provide pre-run and post-run manifest references for every session, plus a sanitized transcript reference. References must resolve inside the evidence directory.

When an evidence record is superseded and preservation is required, retain the earlier record unchanged and create a new run identity or explicitly named successor. Do not silently overwrite historical evidence.

## Limitations

Use this boundary:

> This run records one agent's observable behavior under three frozen fixtures, one profile version, one adapter, one environment, and one observation method. It does not establish universal obedience, safety, enforcement, cross-model consistency, production reliability, or general effectiveness.

## Recurring Behavior Intake

Tell us the recurring agent behavior you cannot reliably control.
