# Scope Control Canonical Identity Migration

On September 7, 2026, Scope Control's public product surface was simplified so
one file serves as both the canonical and installable profile.

## Successor canonical artifact

- Path: `profiles/scope-control/BEHAVIOR_PROFILE.md`
- SHA-256: `8ebe592498af4fd5d5a4517cd68e02b03400c68ed1040cc21fcb1e161192cf1e`
- Role: canonical installable Scope Control profile
- Structural result: 19/19 assertions pass

The internal dogfood campaign already identified and tested these exact bytes.
The migration changes their repository role; it does not rewrite the profile or
transfer evidence from a different artifact.

## Historical canonical artifact

- Former path: `products/behavior-profiles/scope-control/BEHAVIOR_PROFILE_SCOPE_CONTROL.md`
- Preserved path: `docs/history/scope-control/CANONICAL_PRODUCT_SOURCE_v0_1.md`
- SHA-256: `769385360202ad58557d52ab1d3b9e1d3419a056b50f513af66d3604dab0e1d6`
- Role: frozen predecessor and identity anchor for the historical runtime qualification

The predecessor remains byte-identical and continues to identify the artifact
used by the historical runtime qualification. That qualification is not
reassigned to the successor profile.

## Evidence and path continuity

Historical evidence records remain unchanged. The verifier resolves their
original paths through an explicit relocation table and checks the referenced
bytes at their preserved locations. Active documentation and commands use the
successor canonical path.

This migration changes repository topology and canonical product identity. It
does not establish new behavioral, runtime, portability, safety, or production
claims.
