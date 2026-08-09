# Protected Paths

Behavior Profiles shape expected conduct.

Protected Paths adds a deliberate local checkpoint at one specific boundary: the normal Git commit path for marked files.

```text
Behavior
-> reviewability
-> enforcement
```

## What It Adds

- a local pre-commit gate;
- a local approval checkpoint;
- a proof packet;
- single-use local approval;
- explicit bypass disclosure.

## Important Boundary

Protected Paths is local Git governance. It is not security software, tamper-proofing, remote enforcement, branch protection, or protection against hook removal or `git commit --no-verify`.

Use an instruction-layer profile when visible conduct is enough. Use deterministic enforcement when the boundary must not depend on voluntary instruction following.

Learn more from the [Second Mind Systems front door](https://github.com/Secondmindsystems/second-mind-systems).
