# Generic Installation

Use this route for an agent that supports durable project, workspace, or reusable instructions.

1. Identify the instruction surface the agent reads before task execution.
2. Add the complete contents of `profiles/scope-control/BEHAVIOR_PROFILE.md`.
3. Confirm whether user prompts or nearer instruction files can override it.
4. Run the Scope Control quick test.
5. Record the agent, model, version, instruction location, and observed result.

If you cannot identify a durable instruction surface, treat the profile as task-local and do not claim persistence.
