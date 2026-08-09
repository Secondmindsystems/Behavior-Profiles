# Behavior Profile Reference Format

This document defines a small, public reference shape for Behavior Profiles.

It is a convention used by this repository. It is not a universal standard, compliance framework, certification, or guarantee of agent behavior.

## Required Fields

### Identity

Give the profile a stable name and version.

### Failure Addressed

Name the recurring observable behavior the profile is intended to change.

### Expected Conduct

State what the agent is expected to do in observable terms.

### Installation Location

Name the durable instruction surface where the profile should be placed.

### Observable Expectations

List what a reviewer should be able to see before, during, or after work.

### Pressure Test

Provide a bounded prompt or fixture that exercises the expected conduct.

### Completion Evidence

Define what should be recorded after the test or work episode.

### Bypass

State how the profile can be removed, overridden, ignored, or otherwise fail to govern behavior.

### Limitations

State what the profile and its evidence do not prove.

### Version

Identify the exact profile revision used in an evidence episode.

## Reference Lifecycle

```text
describe expected conduct
-> install profile
-> run bounded pressure test
-> observe behavior
-> record PASS / FAIL / CONFUSED
-> revise, retain, or escalate to enforcement
```

## Evidence Rule

Package completeness and agent behavior are different claims.

A package verifier can establish that required artifacts and fields are present. Only an observed episode can report how an agent behaved in a declared environment.
