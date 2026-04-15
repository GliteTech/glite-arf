# Experiment Run Instructions

## Planning Guidelines

* Define the hypothesis or research question the experiment tests.
* Specify all independent variables (models, hyperparameters, prompting strategies) and dependent
  variables (F1, accuracy, cost, latency).
* Decide which independent variables will become explicit metrics variants in `results/metrics.json`
  when the task reports more than one compared condition.
* List the evaluation benchmarks and subsets to report on (e.g., Raganato ALL, per-dataset
  SE2/SE3/SE07/SE13/SE15).
* Estimate API costs and compute time before running. Include cost caps in the plan to prevent
  budget overruns.
* Decide upfront how to compute `efficiency_training_time_seconds`,
  `efficiency_inference_time_per_item_seconds`, and `efficiency_inference_cost_per_item_usd`. Record
  which stages are counted, how inferred items are counted, and whether inference cost comes from
  API billing or machine hourly pricing.
* Identify baseline results to compare against (MFS baseline, prior task results, published
  numbers).

## Implementation Guidelines

* Follow `arf/styleguide/python_styleguide.md` for all Python code. Key rules: absolute imports,
  keyword arguments for 2+ params, `@dataclass(frozen=True, slots=True)`, centralized paths in
  `code/paths.py`, named constants, explicit type annotations, 100-char line limit.
* **Reproducibility**: Set and record random seeds for all stochastic components. Log the exact
  model versions, API endpoints, and library versions used.
* **Cost tracking**: Record all API call costs in `results/costs.json`. Track token counts and
  per-call costs for LLM experiments.
* **Structured results**: Report per-subset metric breakdowns in `results/metrics.json`. Never
  report only aggregate numbers -- include per-dataset, per-POS, and per-category breakdowns where
  applicable. If the task evaluates multiple models, prompts, hyperparameter settings, or other
  conditions, use the explicit multi-variant metrics format with one variant per condition.
* **Efficiency metrics**: When the task trains a model or prompt-tuned system, record
  `efficiency_training_time_seconds` in `results/metrics.json`. When the task runs inference over
  items, record `efficiency_inference_time_per_item_seconds` and
  `efficiency_inference_cost_per_item_usd` by dividing total inference time or cost by the number of
  inferred items. Omit metrics that do not apply; never encode missing measurements as zero.
* Document the efficiency-metric formulas and raw inputs in `results/results_detailed.md`, including
  total seconds, inferred item count, and the API spend or machine hourly rate used in the cost
  calculation.
* **Charts**: Generate at least 2 matplotlib/seaborn charts during implementation. Save all charts
  to `results/images/` as PNG files. Typical charts: metric comparison across conditions (bar
  chart), per-category breakdown (grouped bar or heatmap), cost vs quality tradeoff (scatter plot).
* **Comparison to baselines**: Include at least the MFS baseline and one prior published result in
  all comparison tables and charts.
* **Error analysis**: When predictions are wrong, sample and categorize errors. Include error
  examples in `results/results_detailed.md`.
* **Predictions asset**: Save all per-instance predictions as a `predictions` asset in
  `assets/predictions/<predictions_id>/`. Follow the specification in
  `meta/asset_types/predictions/specification.md`. Include instance IDs, gold labels, predicted
  labels, and confidence scores. This enables later metric recomputation (e.g., with different sense
  groupings) without re-running inference.
* **Model asset** (when applicable): If the experiment trains or fine-tunes a model, save it as a
  `model` asset in `assets/model/<model_id>/`. Follow the specification in
  `meta/asset_types/model/specification.md`.
* Use `uv run python -m arf.scripts.utils.run_with_logs` for every script execution.
* **Research traceability**: Experiments have uncertain outcomes. Someone will later read the
  results to understand *why* they turned out this way. Save enough raw data to answer diagnostic
  questions:
  * Save all raw model outputs (predictions, confidence scores, LLM responses), not just final
    metrics. For LLM experiments, save the full prompt and full response for every call.
  * Log per-item results so individual failures can be inspected. Which items were hardest? Which
    models disagreed? What patterns appear?
  * Include an error analysis section in `results/results_detailed.md`: sample wrong predictions,
    categorize failure modes, and propose hypotheses for why they occurred.
  * Save intermediate results at each pipeline stage (e.g., after preprocessing, after inference,
    after scoring) so problems can be localized to a specific stage.

## Common Pitfalls

* **Missing seeds**: Without fixed seeds, results are not reproducible. Set seeds for Python
  `random`, `numpy`, and `torch` at minimum.
* **Aggregate-only metrics**: Reporting only ALL F1 hides per-subset variation. Always include
  per-dataset and per-POS breakdowns.
* **No cost tracking**: LLM experiments can exceed budget silently. Log costs per call and check
  cumulative spend against the budget cap.
* **Unfair comparisons**: Ensure all systems are evaluated on identical data splits with identical
  preprocessing and scoring.
* **No baseline reference**: Results without a baseline comparison are uninterpretable. Always
  include MFS and at least one published result.
* **Below-baseline results treated as findings instead of bugs**: If any model scores at or below
  the trivial baseline (MFS for WSD, majority class for classification), the pipeline is broken —
  not the approach. A model with access to context that performs worse than a context-free heuristic
  has a bug in its input construction, output parsing, or evaluation logic. Treat below-baseline as
  a hard stop: inspect individual inputs and outputs, verify the model receives correct data, verify
  scoring logic on known-answer instances, and fix the bug before proceeding. Never run expensive
  full-scale experiments without first validating on a small sample with individual-level
  inspection.
* **Skipping individual-output inspection**: Aggregate metrics (F1, accuracy) hide semantic bugs
  that affect a systematic subset of instances. After every debug or validation run, read 5
  individual predictions: verify the input was correctly formatted, the model response is
  reasonable, and the scoring is correct for each specific case. A single manual inspection of one
  wrong prediction can reveal a bug that aggregate metrics cannot.

## Verification Additions

* Confirm `results/metrics.json` contains per-subset breakdowns, not only aggregate scores.
* Confirm multi-condition experiment tasks use explicit variants rather than collapsing everything
  to one flat metrics object.
* Confirm relevant `efficiency_*` metrics are present whenever the task performed training or
  inference, and that their formulas are documented in `results/results_detailed.md`.
* Confirm `results/costs.json` exists and records non-zero costs for any paid API calls.
* Confirm random seeds are logged in the implementation logs.
* Confirm a `predictions` asset exists in `assets/predictions/` with per-instance prediction files
  matching the specification.
* Confirm baseline comparisons appear in `results/results_summary.md`.

## Related Skills

* `/implementation` -- execute experiment scripts with logging
* `/setup-remote-machine` -- provision GPU machines for training or inference
