# Behavior Profile: Scope Control

## The Meta Layer Behind Agent Skills

**Skills expand what an agent can do. Behavior Profiles make explicit how the agent is expected to behave while using those capabilities.**

A Behavior Profile is a portable conduct contract for an AI agent.

Scope Control starts with one of the simplest places to see why that matters:

**You asked for one change. The agent completed it, then quietly expanded the task.**

The agent may have understood the code perfectly.

It may even have made useful improvements.

The problem is that useful and authorized are not the same thing.

Scope Control makes that boundary visible.

---

## Why Behavior Profiles Exist

AI agents are gaining capabilities quickly.

They can code, research, browse, inspect repositories, operate tools, generate tests, modify files, and complete increasingly long workflows.

Skills help agents perform that work.

But a skill does not answer every question that appears while the work is being done.

Should the agent fix an adjacent problem it notices?

Should ambiguity be treated as permission?

Which files actually belong to the task?

When should the agent infer, and when should it ask?

What should remain untouched?

What evidence should it leave behind when the work is finished?

Those are questions of conduct.

A capable agent can perform the requested task correctly and still make poor decisions about how far its authority extends.

That is why capability and conduct need to be treated separately.

**Capability describes what the agent can do.**

**Conduct describes how that capability should be used.**

As capability grows, the agent gains a larger surface of possible action.

That creates more places where assumptions, scope decisions, and hidden judgment can affect real work.

Behavior Profiles make recurring expectations around those decisions explicit.

---

## What Is the Meta Layer?

A coding skill might teach an agent how to inspect a repository, modify a file, run tests, or refactor code.

A Behavior Profile does something different.

It carries expectations that can remain useful across all of those capabilities.

How should the agent handle ambiguity?

How should it respond to an authorization boundary?

Should adjacent work be performed or deferred?

What should happen when the task cannot be completed inside the current scope?

Those expectations sit across changing skills rather than belonging to one particular skill.

That is the meta layer.

**The skill changes. The behavior rule persists.**

---

## What Is a Behavior Profile?

A **Behavior Profile** is a portable conduct contract for an AI agent.

It does not teach the agent a new task.

It describes how the agent is expected to behave while using the capabilities it already has.

The task may change.

The repository may change.

The tools may change.

The active skill may change.

The conduct expectation can remain relevant across all of them.

A Behavior Profile can make expectations explicit around things such as:

- scope;
- ambiguity;
- assumptions;
- escalation;
- no-touch boundaries;
- completion;
- reviewability;
- evidence;
- when the agent should stop and ask.

That makes it a layer around capability rather than another capability itself.

---

## Why Scope Control Comes First

Scope is one of the easiest behavioral boundaries to recognize.

Suppose you ask an agent:

> Fix the spelling error in this documentation file.

The agent may also notice:

- awkward wording nearby;
- inconsistent formatting;
- stale examples;
- another documentation problem;
- a related file that could be improved.

A sufficiently capable agent may know exactly how to fix every one of those things.

That still does not answer the important question:

**Which of those actions belong to the job it was actually given?**

Scope Control turns that normally implicit judgment into an explicit operating boundary.

Before acting, the profile asks the agent to identify:

1. the requested task;
2. the authorized scope;
3. no-touch boundaries;
4. authorized actions;
5. the done condition;
6. the condition that should make it stop or flag the operator.

The goal is not to make the agent less useful.

It is to make the boundary between requested work and adjacent opportunity visible.

---

## Three Behaviors

Scope Control is easiest to understand through three situations.

### ACT when authorized

The task is clear.

The requested action is inside the declared boundary.

The agent performs the work, verifies it, and reports what changed.

### DEFER when tempted

The agent discovers useful adjacent work that was not part of the request.

It completes the authorized task, leaves the adjacent work untouched, and surfaces that opportunity separately.

The useful idea is not lost.

It simply does not become part of the current task without authorization.

### STOP when authority is incomplete

The agent reaches a decision it cannot make from the authority it has been given.

It does not guess.

It identifies the missing decision and asks for clarification before proceeding.

A useful compression is:

**Act when authorized. Defer when tempted. Stop when unclear.**

---

## What Changes for the Operator?

Without an explicit conduct layer, much of the operating boundary remains inside the human's head.

The operator knows what they meant.

The agent has to infer it.

That works until the inference matters.

Scope Control gives the agent an explicit representation of the task boundary and gives the operator something visible to review.

Instead of discovering afterward that the agent silently expanded the task, the boundary becomes part of the work itself.

That is the deeper value of the profile.

**It makes an invisible conduct decision inspectable.**

---

## Install Scope Control

Scope Control is the conduct contract.

Your agent's instruction system determines where that contract is installed.

### Agents that use `AGENTS.md`

Add the complete installable Scope Control profile to the applicable `AGENTS.md`.

A repository-root `AGENTS.md` can provide repository-wide conduct. A nested file can apply the profile to a narrower subtree when the agent supports that behavior.

[AGENTS.md installation guide](../adapters/agents-md/README.md)

### Claude Code

Add the complete profile to the applicable project `CLAUDE.md`.

Keep project-specific instructions and no-touch boundaries explicit, and confirm that the file is inside the instruction scope Claude Code actually reads.

[Claude Code / CLAUDE.md installation guide](../adapters/claude-code/README.md)

### Other agents

If another agent supports durable project, workspace, or reusable instructions, place the profile in the documented instruction surface it reads before task execution.

Check instruction precedence and whether a nearer instruction or user prompt can override it.

[Generic installation guide](../adapters/generic/README.md)

If the agent has no durable instruction surface, treat the profile as task-local rather than claiming persistence.

The installable profile is here:

[Installable Scope Control profile](../profiles/scope-control/BEHAVIOR_PROFILE.md)

**Installation makes the conduct contract available to the agent. It does not prove that the agent followed it.**

That requires observation.

---

## Try It

The fastest way to understand Scope Control is to exercise it against a disposable workspace.

The public experience contains three bounded scenarios:

**ACT:** perform a clearly authorized change.

**DEFER:** complete the requested work while leaving tempting adjacent improvements untouched.

**STOP:** encounter incomplete authority and ask for the missing decision rather than guessing.

[Try the ACT / DEFER / STOP experience](../profiles/scope-control/TRY_IT.md)

For a shorter entry point:

[Run the five-minute quick test](../profiles/scope-control/QUICK_TEST.md)

Do not use a production or sensitive repository for the test.

---

## Behavior Is Only the First Layer

A written instruction is not enforcement.

Behavior Profiles make expected conduct explicit, but an agent can still misunderstand, ignore, override, shadow, or inconsistently follow an instruction.

That distinction is intentional.

The progression is:

### Behavior

Describe the expected conduct.

### Reviewability

Make that conduct observable, pressure-test it, and preserve what happened.

### Enforcement

When a critical boundary cannot depend on instruction following, translate the machine-checkable portion into deterministic controls.

Each layer carries a different responsibility.

A Behavior Profile describes the conduct contract.

A pressure test asks whether that conduct appeared in a declared situation.

Evidence records what actually happened.

Deterministic controls can govern the subset of the boundary that can be represented mechanically.

None of those layers should pretend to be the others.

---

## We Tested the Progression

Scope Control did not remain only an instruction artifact.

The project progressed through several bounded evidence layers.

The public work includes:

- a canonical Scope Control artifact;
- an installable representation;
- installation adapters;
- structural assertions;
- paired synthetic controls;
- negative controls;
- bounded internal dogfood;
- evidence templates;
- package verification;
- a self-serve behavioral experience.

These evidence types remain intentionally separate.

A structural check can show that the required conduct fields are present.

A synthetic control can test whether the harness distinguishes conforming from non-conforming observations.

Neither proves that an agent will always obey the profile.

Observed behavior requires an actual declared episode.

---

## When Instruction Was Not Enough

A later experiment moved the machine-checkable portion of Scope Control into a deterministic pre-action Runtime.

**Scope Control Runtime v0.1** evaluated declared proposed agent actions against a task boundary before execution through one qualified Claude Code `PreToolUse` integration surface on pinned Claude Code 2.1.137 in the tested Windows, authenticated-session topology.

The internal qualification reported:

- `25/25` Runtime tests passing;
- a `16/16` paired deterministic engine matrix;
- ALLOW crossing the tested live host seam;
- BLOCK crossing the tested live host seam;
- DEFER crossing the tested live host seam and producing a distinct durable deferred item.

ASK was qualified at the deterministic engine level only. Its live-host projection was not established.

That evidence is deliberately narrow.

It does not establish:

- universal enforcement;
- a security boundary;
- production reliability;
- arbitrary-shell understanding;
- cross-client compatibility;
- all Claude Code versions;
- other operating systems;
- consistent behavior across every model or environment.

[Scope Control Runtime architecture and qualification](../products/behavior-profiles/runtime/README.md)

[Public Runtime qualification manifest](../products/behavior-profiles/PUBLIC_RUNTIME_QUALIFICATION_MANIFEST_v0_1.json)

The executable Runtime mechanism is not distributed at active HEAD.

Its qualification record, architectural description, limitations, frozen identities, and ordinary Git history remain preserved.

The distribution decision changed.

The qualification evidence did not disappear.

---

## What the Evidence Means

Keeping evidence classes separate is part of the design.

A behavioral `PASS` means the observed conduct satisfied one declared test episode.

It does not mean the agent will always behave that way.

A package-verification `PASS` means the expected package structure and artifacts are present and internally consistent.

It does not prove agent obedience.

A Runtime qualification supports only the behavior demonstrated inside its declared technical boundary.

This project does not claim universal behavior, security, compliance, production readiness, or customer validation from those results.

---

## The Larger Idea

As agents perform more of the implementation work themselves, decisions that once survived implicitly inside human judgment increasingly need explicit representations.

Scope is one example.

Authority is another.

So are completion conditions, uncertainty, review expectations, and escalation boundaries.

Behavior Profiles provide a way to make recurring conduct expectations portable, observable, and testable across changing agent capabilities.

Scope Control is the first reference profile because its failure mode is easy to see:

**The agent knew how to do more than the job required.**

The engineering problem was deciding what it should actually do.

That distinction becomes more important as agents become more capable.

---

## Start Here

If you are new to the project:

### Understand the category

Skills expand what an agent can do. Behavior Profiles make explicit how the agent is expected to behave while using those capabilities.

### See the first application

Scope Control makes the operating boundary around the current task explicit.

### Install it

Choose the adapter that matches the instruction surface your agent actually reads.

### Try it

Run the ACT, DEFER, and STOP experience in a disposable workspace.

### Inspect the evidence

Review the tests, limitations, qualification record, and exact claim boundaries.

Behavior Profiles are not a promise of perfect agent behavior.

They make an increasingly important part of agent behavior explicit enough to inspect, test, improve, and, where necessary, enforce.

**Skills expand capability.**

**Behavior Profiles make conduct explicit.**

**Scope Control begins with the boundary around the work.**
