# Limitations

Behavior Profiles are instruction-layer conduct contracts.

They can make expected behavior explicit and give reviewers a repeatable way to test and discuss it. They cannot guarantee that a model, agent, tool, or user will follow those instructions.

## This Package Does Not Establish

- security or tamper resistance;
- safety or compliance;
- remote enforcement;
- production readiness;
- cross-model or cross-version consistency;
- persistent model memory;
- prevention of unauthorized file access or edits;
- effectiveness outside the declared evidence environment;
- independent or customer validation unless explicitly recorded.

## Known Bypass Paths

A user or tool can remove, override, shadow, or ignore the profile. Instruction precedence can differ between products. Models can misunderstand or inconsistently follow the same text. A task can also be framed too vaguely for scope control to resolve safely.

## Evidence Boundary

A `PASS` describes one declared evaluation episode. It does not establish universal behavior.

A package-verifier `PASS` establishes package completeness and consistency only. It does not establish agent obedience.

## When Instruction Is Not Enough

Use deterministic enforcement for boundaries that cannot depend on voluntary instruction following. [Governed Repo](https://github.com/Secondmindsystems/governed-change-demo) demonstrates that stronger layer with explicit gates and receipts.
