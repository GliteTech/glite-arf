---
paths:
  - "tasks/**"
---

# Task Document Rules

## research.md sections

Objective, Background, Methodology Review, Key Findings, Recommended Approach, References.
Full spec: `arf/specifications/research_papers_specification.md`

## plan.md sections

Objective, Approach, Cost Estimation, Step by Step, Remote Machines, Assets Needed,
Expected Assets, Time Estimation, Risks & Fallbacks, Verification Criteria.

## results.md sections

Summary (2-3 sentences with headline metrics), Methodology (machine, runtime, timestamps),
Metrics Tables (per-category + aggregate + stddev), Comparison vs Baselines (always deltas),
Visualizations (embed charts via `![desc](images/file.png)`), Analysis/Discussion, Limitations, Verification,
Files Created, Next Steps/Suggestions.

## Results standards

* Use consistent metrics across tasks for cross-task comparison
* Always include baselines; report improvements as deltas
* Document negative results with the same rigor as positive results
* Include machine specs, runtime, timestamps, worker count for reproducibility
* All charts/graphs saved to `results/images/` and **embedded** in
  `results_detailed.md` with `![description](images/filename.png)` syntax
  so they render visually on GitHub — never just list filenames as text

## Code organization per task

* `paths.py` for centralized `pathlib.Path` constants
* `constants.py` for column names, dtypes, magic strings as typed constants
