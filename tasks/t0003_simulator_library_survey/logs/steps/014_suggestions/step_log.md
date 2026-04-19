---
spec_version: "3"
task_id: "t0003_simulator_library_survey"
step_number: 14
step_name: "suggestions"
status: "completed"
started_at: "2026-04-19T08:02:56Z"
completed_at: "2026-04-19T08:04:30Z"
---
## Summary

Wrote `results/suggestions.json` with 5 follow-up suggestions derived from the t0003 simulator
survey outcome. Each suggestion maps to a concrete next step that the NEURON+NetPyNE primary / Arbor
backup recommendation makes necessary: install & validate the chosen toolchain, port the
Poleg-Polsky 189347 DSGC model as a library asset, benchmark NEURON vs Arbor on the project's actual
morphology, scaffold a NetPyNE Batch sweep harness, and evaluate NEURON 9.0.x readiness. Priorities
reflect critical-path urgency (toolchain install + DSGC port are high; benchmark and sweep scaffold
are medium; 9.0.x readiness evaluation is low).

## Actions Taken

1. Read `arf/specifications/suggestions_specification.md` to confirm the spec v2 JSON schema,
   suggestion ID format `S-XXXX-NN`, allowed `kind` and `priority` values, and category slug
   validation.
2. Listed `meta/categories/` and chose slugs that match existing categories
   (`compartmental- modeling`, `retinal-ganglion-cell`, `direction-selectivity`) so the `SG-W006`
   warning does not fire.
3. Drafted 5 suggestions with IDs S-0003-01 through S-0003-05, each with a title (under 120 chars),
   a description (> 20 chars, grounded in specific t0003 findings),
   `source_task: "t0003_simulator_library_survey"`, and `source_paper: null` (the paper evidence
   lives in research_internet.md, not in a local paper asset).
4. Ran `verify_suggestions.py` via `run_with_logs.py` — PASSED with 0 errors and 0 warnings.

## Outputs

* `tasks/t0003_simulator_library_survey/results/suggestions.json`
* Additional `run_with_logs` command logs under
  `tasks/t0003_simulator_library_survey/logs/commands/`

## Issues

No issues encountered. None of the 5 categories in `meta/categories/` was an exact fit for the
"toolchain / infrastructure" dimension of S-0003-01 and S-0003-05, so those suggestions use
`compartmental-modeling` as the closest available slug; a future task may add a more specific
category like `tooling` or `infrastructure` if the project grows more such suggestions.
