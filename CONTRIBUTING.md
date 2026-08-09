# Contributing

Contributions should improve clarity, reproducibility, or evidence without inflating claims.

## Useful Contributions

- report an installation result as `PASS`, `FAIL`, or `CONFUSED`;
- describe one recurring agent behavior you cannot reliably control;
- add a bounded fixture with an explicit expected outcome;
- repair unclear installation guidance;
- identify a bypass or limitation;
- correct an unsupported or stale claim.

## Contribution Requirements

Before opening a pull request:

1. Keep the change inside one declared purpose.
2. State what behavior or package defect the change addresses.
3. Include a pressure test when behavior changes.
4. Distinguish observed results from inference.
5. Do not claim enforcement, safety, compliance, or universal consistency.
6. Run:

   ```powershell
   python -B tools/verify_profile_package.py
   python -B -m unittest discover -s tests -p "test_*.py"
   ```

## Evidence Reports

Remove secrets, private repository content, customer data, and hidden system instructions before sharing evidence.

If this profile saved review time, tell us the recurring agent behavior you still cannot reliably control using the recurring-behavior issue form.
