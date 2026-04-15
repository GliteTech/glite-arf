# Comparative Analysis Instructions

## Planning Guidelines

* Define the comparison dimensions upfront: quality metrics, cost, speed, model size, training data
  requirements, or any other relevant axes.
* Establish fair comparison criteria before running experiments. All compared approaches must use
  the same evaluation data, preprocessing, and scoring.
* Plan statistical significance testing. Decide on the test (paired bootstrap, McNemar's,
  permutation test) and significance threshold (typically p < 0.05) during planning, not after
  seeing results.
* Decide whether the comparison includes new training or inference runs. If it does, define how
  `efficiency_training_time_seconds`, `efficiency_inference_time_per_item_seconds`, and
  `efficiency_inference_cost_per_item_usd` will be measured consistently across all compared
  approaches.
* Define the variant dimensions that will appear in `results/metrics.json` (for example `model`,
  `prompt`, `dataset_size`, `tokenizer`, `preprocessing`). Comparative-analysis tasks should use the
  explicit multi-variant metrics format whenever they compare more than one approach.
* Use `/research-papers` to identify published comparison baselines and ensure the analysis covers
  the approaches that matter most.

## Implementation Guidelines

* Follow `arf/styleguide/python_styleguide.md` for all Python code. Key rules: absolute imports,
  keyword arguments for 2+ params, `@dataclass(frozen=True, slots=True)`, centralized paths in
  `code/paths.py`, named constants, explicit type annotations, 100-char line limit.
* Create structured comparison tables with one row per approach and one column per metric. Include
  confidence intervals or standard deviations where possible.
* Generate visualizations for every comparison. At minimum, produce a bar chart comparing the
  primary metric across approaches. For multi-dimensional comparisons, create Pareto frontier charts
  showing trade-offs (e.g., quality vs. cost, quality vs. speed).
* Run statistical significance tests for all pairwise comparisons on the primary metric. Report
  p-values in the comparison table.
* If the task performs new training or inference, record the relevant registered `efficiency_*`
  metrics in `results/metrics.json` using one explicit variant per compared approach or condition,
  and keep the full per-approach efficiency table in `results/results_detailed.md`.
* Control for confounding variables. When comparing models, use identical preprocessing,
  tokenization, and evaluation splits. Document any differences that could not be controlled.
* **Predictions assets**: If the analysis generates new predictions (not reusing existing prediction
  assets from prior tasks), save per-instance predictions as `predictions` assets in
  `assets/predictions/<predictions_id>/`. Follow the specification in
  `meta/asset_types/predictions/specification.md`. This enables later recomputation with different
  metrics or sense groupings.
* Write a clear recommendation section summarizing which approach is best under which conditions.
  Avoid declaring a single winner when the trade-off depends on use-case constraints.
* **Research traceability**: Comparison results inform major project decisions. Save enough detail
  so someone can later understand *why* one approach beat another:
  * Save per-item predictions for every compared approach so item-level disagreements can be
    inspected.
  * Identify items where approaches disagree most — these reveal what each approach is actually good
    or bad at, beyond aggregate scores.
  * In `results/results_detailed.md`, include qualitative examples: pick representative items where
    approach A succeeds and B fails (and vice versa) and explain what properties of the item drive
    the difference.

## Common Pitfalls

* Unfair comparisons: using different data splits, preprocessing, or evaluation metrics for
  different approaches. This invalidates the entire analysis.
* Reporting only aggregate metrics without per-subset breakdowns. An approach that wins on average
  may lose badly on specific subsets.
* Omitting statistical significance tests. Small differences in F1 may not be meaningful, especially
  on small test sets.
* Cherry-picking metrics that favor a preferred approach. Report all planned metrics regardless of
  which approach they favor.
* Not visualizing results. Tables alone are harder to interpret than charts for multi-dimensional
  comparisons.

## Verification Additions

* Confirm that comparison tables include all planned approaches and metrics.
* Confirm that any new training or inference runs have matching `efficiency_*` metrics in
  `results/metrics.json` and per-approach efficiency tables in `results/results_detailed.md`.
* Verify that statistical significance tests are reported for pairwise comparisons on the primary
  metric.
* Check that at least one visualization (chart or graph) is present in the results images folder.
* Validate that all compared approaches used identical evaluation data and scoring methodology.

## Related Skills

* `/implementation` -- general implementation workflow for coding steps.
* `/research-papers` -- review published comparisons and baselines.
