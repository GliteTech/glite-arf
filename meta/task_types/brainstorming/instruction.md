# Brainstorming Instructions

## Planning Guidelines

No formal planning step is needed. The brainstorming session itself defines the
direction. Before starting, review existing suggestions by running
`aggregate_suggestions.py` to avoid proposing duplicates.

## Implementation Guidelines

* Use the `/human-brainstorm` skill to conduct the interactive session.
* Record the **full session transcript** verbatim in `logs/`. Never summarize or
  truncate the conversation -- the complete exchange must be preserved for later review.
* After the session, extract actionable suggestions and produce them using the
  `/generate-suggestions` skill.
* Each suggestion must include a clear rationale traceable to a specific point in the
  brainstorming transcript.
* If the session produces decisions about project direction, document them in
  `results/results_summary.md` with the reasoning behind each decision.

## Common Pitfalls

* **Summarizing instead of transcribing**: The log must contain the full verbatim
  session, not a condensed version. Summaries lose nuance and make it impossible to
  revisit the original reasoning.
* **Duplicate suggestions**: Always check existing suggestions before writing new ones.
  Run the suggestions aggregator first.
* **Missing rationale**: Every suggestion needs a "why" that connects back to the
  discussion. Suggestions without rationale are not actionable.

## Verification Additions

* Confirm the session log in `logs/` is a complete transcript (not a summary).
* Confirm at least one suggestion file exists in `assets/` or
  `results/suggestions.json`.
* Verify no duplicate suggestions against the aggregated suggestions list.

## Related Skills

* `/human-brainstorm` -- conduct the interactive brainstorming session
* `/generate-suggestions` -- produce structured suggestion files from outcomes
