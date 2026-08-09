# Behavior Profiles Conformance Harness

This harness turns a Behavior Profile into a bounded, testable behavioral specification.

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

## Commands

From `products/behavior-profiles`:

```powershell
python harness/harness.py check-profile `
  --suite harness/profiles/scope-control/suite.json `
  --git-ref main `
  --git-path products/behavior-profiles/scope-control/BEHAVIOR_PROFILE_SCOPE_CONTROL.md `
  --repo-root ../..

python harness/harness.py run-controls `
  --suite harness/profiles/scope-control/suite.json `
  --observations harness/profiles/scope-control/controls.json `
  --git-ref main `
  --git-path products/behavior-profiles/scope-control/BEHAVIOR_PROFILE_SCOPE_CONTROL.md `
  --repo-root ../.. `
  --output harness/evidence/pass-1-control-run.json

python -m unittest discover -s harness/tests -p "test_*.py"
```

## Claim ceiling

If the structural check, paired controls, and harness tests pass, the supported claim is:

> Scope Control has been converted from prose into a testable behavioral specification with machine-checkable structural requirements and adversarial behavioral fixtures. The harness discriminates between its frozen conforming and non-conforming control observations.

This does not establish agent obedience, cross-client conformance, portability, enforcement, safety, certification, production reliability, or general effectiveness.

## Normalization boundary

Only ordinary unordered Markdown markers `*`, `-`, and `+` are representation-normalized. Ordered-list variants are intentionally unsupported in this workband. For example, changing `1. Requested task` to `1) Requested task` may fail; that is an unsupported representation variation, not a judgment of semantic inequivalence.
