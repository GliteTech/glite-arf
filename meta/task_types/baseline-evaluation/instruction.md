# Baseline Evaluation Instructions

## Planning Guidelines

* Identify the exact baseline method to implement and the paper that defines it. Use the
  `/research-papers` skill to review relevant literature first.
* Specify which datasets and subsets will be evaluated (e.g., Raganato ALL, per-dataset
  SE2/SE3/SE07/SE13/SE15 breakdowns).
* Plan per-subset and per-POS metric breakdowns from the start. Aggregate F1 alone is insufficient;
  include noun, verb, adjective, and adverb scores.
* If the task compares more than one baseline, prompt, checkpoint, or decoding configuration, plan
  explicit metrics variants rather than collapsing results to one flat metrics object.
* Estimate inference runtime and any API or machine cost before execution. Decide how
  `efficiency_inference_time_per_item_seconds` and `efficiency_inference_cost_per_item_usd` will be
  computed from total runtime, total cost, and inferred item count. If the baseline must be trained
  from scratch, also plan `efficiency_training_time_seconds`.
* Check whether existing WSD libraries in the project (data loaders, scorers) already support the
  needed evaluation. Reuse them rather than reimplementing.
* If GPU compute is needed, plan remote machine setup using `/setup-remote-machine`.

## Implementation Guidelines

* Reproduce the baseline methodology exactly as described in the source paper. Do not add
  improvements or modifications; the goal is a faithful reference point.
* Use the project's existing WSD data loader and scorer when available. Import them via absolute
  paths per the Python style guide.
* Report metrics for every individual dataset subset, not just the concatenated ALL score. Include
  precision, recall, and F1. When multiple compared conditions are reported in one task, use the
  explicit multi-variant metrics format.
* Record the relevant registered efficiency metrics in `results/metrics.json`. Use
  `efficiency_inference_time_per_item_seconds` and `efficiency_inference_cost_per_item_usd` for
  baseline runs that execute inference, and `efficiency_training_time_seconds` only when the
  baseline requires training. Omit non-applicable metrics instead of writing placeholder zeroes.
* Document the efficiency-metric formulas and raw inputs in `results/results_detailed.md`, including
  total seconds, inferred item count, and the API spend or machine hourly rate used in the cost
  calculation.
* The compare-literature step is **critical** for this task type. Create a comparison table showing
  your reproduced numbers alongside published results. Flag any discrepancy greater than 2 F1 points
  and investigate the cause.
* **Predictions asset**: Save all per-instance predictions as a `predictions` asset in
  `assets/predictions/<predictions_id>/`. Follow the specification in
  `meta/asset_types/predictions/specification.md`. Include instance IDs, gold labels, predicted
  labels, and confidence scores. This enables later re-scoring with different sense groupings or
  metrics without re-running the baseline.
* Save all predictions to enable later re-scoring and error analysis.
* **Research traceability**: Baseline results become reference points for all future experiments.
  Save enough detail to diagnose any anomalies:
  * Save per-item predictions with confidence scores (not just correct/wrong).
  * Log which items the baseline gets wrong — these form the "hard set" that future models should
    improve on.
  * In `results/results_detailed.md`, include an error analysis: what POS categories, sense counts,
    or frequency ranges cause the most failures.
  * When results differ from published numbers, document which subsets diverge and hypothesize why.

## Common Pitfalls

* Implementing a modified version of the baseline instead of the exact published method. Even small
  changes (different tokenizer, different back-off strategy) can shift results by several F1 points.
* Reporting only aggregate metrics without per-subset breakdowns. This hides important variation
  across datasets and makes comparison with literature harder.
* Skipping the compare-literature step. Without comparison to published numbers, the baseline has no
  validation of correctness.
* Using a different sense inventory version (e.g., WordNet 3.1 instead of 3.0) or different
  evaluation splits than the reference paper.

## Verification Additions

* Confirm per-subset metrics exist for all evaluated datasets.
* Confirm relevant `efficiency_*` metrics exist for baselines that performed training or inference,
  and that the raw inputs for those calculations are documented.
* Verify that a comparison table with published results is present in the results summary.
* Confirm a `predictions` asset exists in `assets/predictions/` with per-instance prediction files
  matching the specification. Check that instance counts match the dataset sizes.
* Validate that the sense inventory version matches the one used in the reference paper.

## Related Skills

* `/implementation` -- general implementation workflow for coding steps.
* `/setup-remote-machine` -- provision GPU machines for model inference.
* `/research-papers` -- review papers defining the baseline method.
