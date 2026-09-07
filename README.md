# Behavior Profiles

## The Meta Layer Behind AI Skills

Skills expand what an agent can do. Behavior Profiles describe how the agent is expected to conduct itself while using those skills.

A coding skill, research skill, and deployment skill perform different work. Expectations such as staying within scope, handling uncertainty, asking for permission, and making results reviewable can matter across all three.

A Behavior Profile is a **portable conduct contract** that makes those expectations explicit across changing tasks and capabilities.

**The skill changes. The expected conduct persists.**

An agent may have permission to edit an entire repository while the task calls for changing only one file. Access tells the agent what is available; it does not determine what belongs to the task.

Capabilities describe what is technically possible. Skills provide procedures. Permissions define available operations. **Behavior Profiles describe the conduct expected while using them.**

A profile can remain in an instruction surface such as `AGENTS.md` or `CLAUDE.md` as tasks and skills change. Whether an agent follows it must be observed in the environment where it is used.

Behavior Profiles make expected conduct explicit and reviewable. Where a critical boundary needs enforcement rather than instruction, a separate control can block or require approval for the action.

## The First Profile: Scope Control

Scope Control addresses one recurring failure:

> You asked for one change. The agent completed it, then quietly expanded the task.

The profile asks the agent to make the task boundary visible before acting: the requested task, authorized scope, no-touch boundaries, allowed actions, done condition, and stop condition.

Afterward, it asks for a short completion note showing what changed and what stayed outside the task.

The profile supplies instructions; it does not block files or commands. For a local Git commit checkpoint, see [AI Protected Paths](https://github.com/Secondmindsystems/ai-protected-paths).

## Try Scope Control

Use the [Scope Control installation guide](profiles/scope-control/README.md), then follow [TRY_IT](profiles/scope-control/TRY_IT.md) for the hands-on scenarios and result recording.

The scenarios exercise three situations:

* **ACT** when the requested action and boundary are clear.
* **DEFER** adjacent work that falls outside the request.
* **STOP** when the target or authority is incomplete.

Test the profile with your own agent and environment and record what happens.

## Verify the Package and Harness

From the repository root:

```powershell
python -B tools/verify_profile_package.py --mode release
python -B harness/harness.py check-profile `
  --suite harness/profiles/scope-control/suite.json `
  --profile profiles/scope-control/BEHAVIOR_PROFILE.md
python -B harness/harness.py run-controls `
  --suite harness/profiles/scope-control/suite.json `
  --observations harness/profiles/scope-control/controls.json `
  --profile profiles/scope-control/BEHAVIOR_PROFILE.md
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

Synthetic controls test whether the harness distinguishes the supplied observations. They do not test an agent. The internal dogfood records document a separate bounded agent-observation campaign.

See the [harness guide](harness/README.md) and [dogfood protocol](docs/evidence/scope-control/DOGFOOD_PROTOCOL.md) for the methods and deeper technical checks.

A verifier PASS does not establish that an agent followed the profile. Behavioral evidence comes from observed runs in the environment where the profile is used.

## Profile Format and Feedback

[FORMAT.md](FORMAT.md) describes the reference profile format.

Installation results, reproducible failures, confusing behavior, recurring conduct problems, and documentation corrections are welcome through the repository's issue forms. Remove credentials, private code, customer records, and hidden instructions from anything you submit publicly.

## Experimental Runtime Work

The repository also documents a separate Scope Control Runtime that evaluates proposed actions.

A recorded Windows trial used Claude Code 2.1.137 and its PreToolUse integration. The tested live subset honored ALLOW, BLOCK, and DEFER. ASK was qualified in the deterministic engine only.

The active repository publishes the architecture and qualification records rather than the executable runtime. Earlier implementation commits remain in Git history.

Read the [runtime qualification page](docs/runtime/scope-control/README.md) for the pinned environment, tested grammar, results, and operating conditions.

The runtime experiment is separate from the installable instruction profile above.

## Go Deeper

For the original category argument and publication context, read [**The Meta Layer Behind AI Skills — Public Edition v0.2**](https://github.com/Secondmindsystems/second-mind-systems/blob/main/BEHAVIOR_PROFILES.md).

Related work:

* [AI Protected Paths](https://github.com/Secondmindsystems/ai-protected-paths)
* [Governed Change Demo](https://github.com/Secondmindsystems/governed-change-demo)
* [Engineering Portfolio](https://github.com/Secondmindsystems/governed-ai-systems-portfolio)

## License

MIT. The Second Mind Systems name and logo are not granted by the software license. See [LICENSE](LICENSE) and [TRADEMARKS.md](TRADEMARKS.md).
