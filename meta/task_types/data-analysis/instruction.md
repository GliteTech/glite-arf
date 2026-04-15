# Data Analysis Instructions

## Planning Guidelines

* Identify the input dataset(s) and confirm they exist from prior tasks.
* Define the specific questions the analysis must answer before writing code.
* List all metrics and chart types to produce upfront so nothing is missed during implementation.
* If the analysis requires statistical tests, decide which tests are appropriate during planning
  (e.g., paired t-test, bootstrap confidence intervals, chi-squared).

## Implementation Guidelines

* Follow `arf/styleguide/python_styleguide.md` for all Python code. Key rules: absolute imports,
  keyword arguments for 2+ params, `@dataclass(frozen=True, slots=True)`, centralized paths in
  `code/paths.py`, named constants, explicit type annotations, 100-char line limit.
* Use `matplotlib` and `seaborn` for all visualizations. Save every chart to `results/images/` as
  PNG files with descriptive filenames.
* Produce structured metrics in `results/metrics.json` using only keys registered in
  `meta/metrics/`. If the analysis reports separate metric sets for multiple compared conditions,
  use the explicit multi-variant format with one variant per condition.
* Include per-subset and per-category breakdowns wherever the data supports them. Aggregate-only
  numbers hide important variation.
* Use explicit dtypes when loading data with pandas. Follow the project Python style guide for all
  DataFrame operations.
* Print summary statistics to stdout so they appear in run logs. Use
  `uv run python -m arf.scripts.utils.run_with_logs` for all script executions.
* When computing percentages or ratios, report both the ratio and the raw counts (e.g., **82.3%**
  (1,234 / 1,500)).
* **Research traceability**: Analysis results will be used to guide project decisions. Save enough
  detail so someone can later verify findings and explore follow-up questions:
  * Save intermediate data (filtered subsets, computed features) as CSV or JSON, not just final
    charts and metrics.
  * Log the exact data transformations applied so the analysis is reproducible from the raw input.
  * In `results/results_detailed.md`, explain surprising findings — don't just report them. Why is a
    distribution skewed? Why does a subset behave differently? Propose hypotheses.

## Common Pitfalls

* **Charts without titles or axis labels**: Every chart must have a descriptive title, labeled axes,
  and a legend when multiple series appear.
* **Missing statistical context**: Report confidence intervals or standard deviations alongside
  point estimates. A single number without variance is not informative.
* **Unlabeled images in results**: Reference every chart in `results/results_summary.md` with a
  description of what it shows.
* **Using 0.0 for missing data**: Use `None`/`null` when data is unavailable. Zero is a valid
  measurement.

## Verification Additions

* Confirm at least one chart exists in `results/images/`.
* Confirm `results/metrics.json` contains only registered metric keys.
* Confirm `results/results_summary.md` references all generated charts.
* Confirm no hardcoded file paths in analysis scripts (use `paths.py` constants).

## Related Skills

* `/implementation` -- execute analysis scripts with logging
* `/research-code` -- review prior task code for reusable loaders or utilities
