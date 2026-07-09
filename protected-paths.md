# Protected Paths

Protected Paths is one concrete implementation further along this progression:

```text
Behavior -> Reviewability -> Enforcement
```

Behavior Profiles shape agent conduct.

Protected Paths governs what agents can commit.

More precisely:

Protected Paths governs the local commit path for marked files.

## What It Adds

Protected Paths is a local Git pre-commit gate with:

- local approval checkpoint
- governance friction
- normal commit-path visibility
- local Proof Packet
- single-use approval
- documented local workflow
- commit boundary

It is designed for developers who want a marked path to require a deliberate local approval checkpoint in the normal commit path.

## How It Fits

Behavior Profiles help describe how an AI agent should behave while working.

Protected Paths adds an explicit local approval checkpoint at one specific boundary: the Git commit path for marked files.

That makes it useful for files or folders where silent change would create review burden.

## Important Boundary

Protected Paths is local Git pre-commit governance.

It is not security software.

It is not tamper-proof.

It does not protect against `git commit --no-verify` or hook removal.

It is not a replacement for branch protection, CODEOWNERS, or CI.

It is Windows-first; native Linux validation is pending.

Each developer environment should install and validate locally.

## Product Page

AI Protected Paths is available here:

https://secondmind.gumroad.com/l/aigtpg

Review the product page and included materials before use.
