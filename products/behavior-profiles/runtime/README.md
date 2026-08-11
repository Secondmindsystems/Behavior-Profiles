# Scope Control Runtime v0.1

Scope Control Runtime is an experimental, deterministic pre-action governance layer for Behavior Profile: Scope Control.

The profile remains authoritative. The machine contract projects the profile's structural rules. The host-agnostic engine evaluates declared authority. Host adapters translate host events and project the engine decision without inventing policy.

Runtime v0.1 is local, default-off, non-production, and limited to frozen deterministic inputs. It does not provide semantic intent judgment, arbitrary-shell understanding, universal enforcement, security guarantees, or cross-client compatibility.

Architecture:

```text
canonical profile
→ machine contract
→ host-agnostic engine
→ separately qualified adapter
→ host interception surface
→ decision / effect / receipt
```
