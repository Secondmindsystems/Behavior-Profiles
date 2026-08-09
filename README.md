# Behavior Profiles

## The Persistent Conduct Layer Behind Agent Skills

Skills describe what agents know how to do.

Behavior Profiles describe how agents are expected to conduct themselves while doing it.

A Behavior Profile is a portable conduct contract for an AI agent, delivered through a durable instruction surface. It does not add a new capability. It defines observable expectations for how existing capabilities should be used.

> The skill changes. The behavior rule persists.

“Persistent” means the profile remains available in an instruction surface such as `AGENTS.md` or `CLAUDE.md`. It does not imply agent memory, universal obedience, cross-session guarantees, or enforcement.

## See the Proof Surface

The shortest review path is runnable:

```powershell
python -B tools/verify_profile_package.py --mode release
python -B harness/harness.py check-profile `
  --suite harness/profiles/scope-control/suite.json `
  --profile scope-control/BEHAVIOR_PROFILE_SCOPE_CONTROL.md
python -B harness/harness.py run-controls `
  --suite harness/profiles/scope-control/suite.json `
  --observations harness/profiles/scope-control/controls.json `
  --profile scope-control/BEHAVIOR_PROFILE_SCOPE_CONTROL.md
```

The first command checks package integrity and the bound internal dogfood record. The second checks the canonical profile against 19 structural assertions. The third runs eight paired synthetic controls and must discriminate all eight conforming observations from all eight non-conforming observations.

The structural checker must also reject vocabulary without the required structure:

```powershell
python -B harness/harness.py check-profile `
  --suite harness/profiles/scope-control/suite.json `
  --profile harness/profiles/scope-control/vocabulary-without-structure.md
if ($LASTEXITCODE -eq 0) { throw "negative control unexpectedly passed" }
```

That non-zero exit is expected. The decoy contains familiar Scope Control words but does not place the required fields in the required sections and list structures.

The proof chain is deliberately explicit:

```text
canonical product artifact (769385...)
-> structurally conforming installable representation (8ebe5924...)
-> internal agent observation record (511c1a...)
-> synthetic harness control record (fb026c...)
```

These are different evidence roles. Synthetic controls test the harness, not an agent. Internal dogfood records one bounded agent observation campaign, not independent external validation.

## Start in Five Minutes

1. Open [Behavior Profile: Scope Control](profiles/scope-control/BEHAVIOR_PROFILE.md).
2. Add it to the instruction surface your agent reads.
3. Run the [quick test](profiles/scope-control/QUICK_TEST.md).
4. For release qualification, follow the [internal dogfood protocol](profiles/scope-control/DOGFOOD_PROTOCOL.md).
5. Record `PASS`, `FAIL`, or `CONFUSED` using the [evidence template](profiles/scope-control/EVIDENCE_TEMPLATE.md).
6. If the behavior matters enough that asking is insufficient, use an enforcement boundary such as [Governed Repo](https://github.com/Secondmindsystems/governed-change-demo).

The operating sequence is:

```text
Describe the conduct
-> install it
-> test it under pressure
-> preserve what happened
-> enforce the critical boundary when instruction is insufficient
```

## The First Profile: Scope Control

Scope Control addresses one recurring failure:

> You asked for one change. The agent completed it, then quietly expanded the task.

The profile asks the agent to make six things visible before acting:

- requested task
- authorized scope
- no-touch boundaries
- authorized actions
- done condition
- stop or flag condition

It then asks for a short completion note showing what happened and what stayed outside the task.

The profile does not block files. It makes the scope decision easier to review.

## AGENTS.md and Behavior Profiles

[AGENTS.md](https://agents.md/) gives coding agents a predictable place for repository instructions. Its official site reported use by more than 60,000 open-source projects when this package was prepared on 2026-08-03.

AGENTS.md tells agents how to work in a repository. A Behavior Profile defines expected conduct that can be carried across repositories and agent environments.

This project uses AGENTS.md as its primary installation surface. It does not compete with or claim ownership of the AGENTS.md format.

## What You Can Verify

The package verifier checks whether the reference package is complete and internally consistent:

```powershell
python -B tools/verify_profile_package.py
```

The verifier returns a machine-readable decision and an explicit proof boundary.

Before publication, maintainers can also run the fixed, product-specific identity check:

```powershell
python -B tools/check_scope_control_publication_state.py --source-file scope-control/BEHAVIOR_PROFILE_SCOPE_CONTROL.md
```

This checks the four frozen identities above, confirms structural conformance for the canonical and installable representations, and confirms that the negative structural control fails. It is a Scope Control publication check, not a generalized provenance system.

A verifier PASS does not prove that an agent obeyed the profile. Behavioral evidence comes from observed pressure-test episodes and must identify its environment, profile version, fixture, expected conduct, observed conduct, evaluator, and limitations.

## Install Surfaces

- [AGENTS.md installation](adapters/agents-md/README.md)
- [Claude Code / CLAUDE.md installation](adapters/claude-code/README.md)
- [Generic durable instruction-surface installation](adapters/generic/README.md)

Each adapter names its target instruction file or surface, precedence caveat, quick-test step, and evidence limitation.

## Open Format

[FORMAT.md](FORMAT.md) defines a small reference shape for portable profiles. It is not a universal standard or certification scheme.

## Contribute Evidence Before Abstraction

Useful contributions include:

- a reproducible installation result;
- a failure or confusion report;
- a recurring behavior that remains hard to control;
- a bounded fixture;
- a correction to an unsupported claim or unclear limitation.

See [CONTRIBUTING.md](CONTRIBUTING.md).

After publication, use the repository issue forms to [report an installation result](https://github.com/Secondmindsystems/behavior-profiles/issues/new?template=installation-result.yml) or [submit a recurring uncontrolled behavior](https://github.com/Secondmindsystems/behavior-profiles/issues/new?template=recurring-behavior.yml). Remove secrets, private repository content, customer data, and hidden instructions before submitting evidence.

## Related Work

- [Behavior Profiles paper](BEHAVIOR_PROFILES.md)
- [Governance Loops](governance-loops.md)
- [Protected Paths](protected-paths.md)
- [Governed Repo demo](https://github.com/Secondmindsystems/governed-change-demo)
- [Second Mind Systems](https://github.com/Secondmindsystems/second-mind-systems)

## Boundary

This repository provides instruction-layer artifacts, fixtures, evidence templates, and a package-integrity verifier.

It does not provide security, compliance, tamper resistance, remote enforcement, guaranteed behavior, customer validation, or production readiness. See [LIMITATIONS.md](LIMITATIONS.md).

## License

MIT. The Second Mind Systems name and logo are not granted by the software license. See [LICENSE](LICENSE) and [TRADEMARKS.md](TRADEMARKS.md).
