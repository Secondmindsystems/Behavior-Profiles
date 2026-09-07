# Behavior Profiles Conformance Harness

The harness checks the structure of a Behavior Profile and evaluates supplied
observations against fixed scenario criteria.

It separates four questions:

1. **Structural conformance** — does the profile expose the required observable surfaces?
2. **Behavioral conformance** — does an observation satisfy frozen fixture criteria?
3. **Discrimination** — can the judge distinguish conforming from non-conforming observations?
4. **Portability** — which behavior survives movement between agent environments? This is out of scope for Pass 1.

## Pass 1

Pass 1 contains:

- a profile-agnostic standard-library Python runner;
- a Scope Control suite with eight adversarial fixtures;
- deterministic PASS, FAIL, and CONFUSED judging;
- paired synthetic controls for every fixture;
- a machine-readable evidence record;
- self-tests for the harness.

Synthetic controls test the harness, not an agent. They must never be represented as agent evidence, independent validation, cross-client evidence, or proof of general effectiveness.

## Run the current public package

Use the [commands in the repository README](../README.md#check-the-package-and-test-harness)
from the repository root. They point to the files shipped in this checkout.

## Historical source identity

Earlier qualification used a different canonical source path and artifact.
Those exact predecessor bytes remain preserved at
[`docs/history/scope-control/CANONICAL_PRODUCT_SOURCE_v0_1.md`](../docs/history/scope-control/CANONICAL_PRODUCT_SOURCE_v0_1.md),
and the [migration record](../docs/history/scope-control/CANONICAL_IDENTITY_MIGRATION.md)
explains how that identity relates to the current installable profile.

## Claim ceiling

If the structural check, paired controls, and harness tests pass, the supported claim is:

> Scope Control has been converted from prose into a testable behavioral specification with machine-checkable structural requirements and adversarial behavioral fixtures. The harness discriminates between its frozen conforming and non-conforming control observations.

These results test the profile structure and the supplied control observations;
agent behavior is evaluated separately from observed agent runs.

## Normalization boundary

Only ordinary unordered Markdown markers `*`, `-`, and `+` are representation-normalized. Ordered-list variants are intentionally unsupported in this workband. For example, changing `1. Requested task` to `1) Requested task` may fail; that is an unsupported representation variation, not a judgment of semantic inequivalence.
