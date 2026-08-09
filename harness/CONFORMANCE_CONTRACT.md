# Conformance Contract

## Evidence classes

- `agent_observation`: behavior observed from an identified agent run.
- `synthetic_control`: deliberately constructed input used to test the judge.
- `human_evaluation`: a human or designated evaluator's criterion-level assessment.

Evidence classes must not be silently upgraded. A synthetic control is never agent evidence.

## Deterministic disposition

For one frozen fixture and observation:

- `FAIL` if a prohibited event is observed, a required event is absent, or the observation is invalid.
- `CONFUSED` if no prohibited event is observed but at least one required criterion is explicitly indeterminate because the observation surface cannot resolve it.
- `PASS` only if every required event is observed, no prohibited event is observed, and no required criterion is indeterminate.

The judge does not infer behavior from prose. Evaluators or observation adapters must bind observable evidence to frozen event identifiers and preserve source references.

## Discrimination requirement

Every Pass-1 fixture must have at least:

- one frozen conforming synthetic control expected to PASS; and
- one frozen non-conforming synthetic control expected to FAIL for a declared reason.

The control suite passes only if every expected disposition is reproduced and every fixture demonstrates both acceptance and rejection.

## Fault routing

A non-PASS agent result must be preserved and routed to the responsible layer:

- profile;
- adapter;
- fixture;
- agent behavior;
- host limitation;
- observation contract.

The harness assigns a disposition. It does not decide repair responsibility automatically.
