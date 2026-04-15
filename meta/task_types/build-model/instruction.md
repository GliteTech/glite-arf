# Build/Train Model Instructions

## Planning Guidelines

* Specify the GPU requirements: GPU type (A100, A10G, etc.), VRAM needed, and estimated training
  time. Include this in the plan's Cost Estimation and Remote Machines sections.
* Set a hard budget ceiling for compute costs. Monitor costs during training and stop early if
  approaching the limit.
* Plan how `efficiency_training_time_seconds`, `efficiency_inference_time_per_item_seconds`, and
  `efficiency_inference_cost_per_item_usd` will be measured. Define which steps count as training
  vs. inference, how inferred items are counted, and whether inference cost comes from API billing
  or machine hourly pricing.
* Define the evaluation protocol before training: which datasets, which metrics, which baselines to
  compare against. Do not design evaluation after seeing results.
* If the task will compare multiple checkpoints, hyperparameter settings, or training conditions in
  one task, define the explicit metrics variants that will be written to `results/metrics.json`.
* Record all hyperparameters in the plan: learning rate, batch size, warmup steps, weight decay,
  number of epochs, random seeds. These must be logged before training starts, not reconstructed
  afterward.
* Identify the pretrained model checkpoint and its exact version (e.g., `bert-base-uncased` from
  HuggingFace, specific commit hash).
* Plan checkpoint saving frequency. Save at least every epoch and keep the best checkpoint by
  validation metric.

## Implementation Guidelines

* Follow `arf/styleguide/python_styleguide.md` for all Python code. Key rules: absolute imports,
  keyword arguments for 2+ params, `@dataclass(frozen=True, slots=True)`, centralized paths in
  `code/paths.py`, named constants, explicit type annotations, 100-char line limit.
* Set random seeds for Python, NumPy, and PyTorch at the start of every training script. Log the
  seed values in the run metadata.
* Log training metrics (loss, learning rate, validation scores) at regular intervals. Use structured
  logging or W&B for tracking.
* **Model asset**: Save the final (best) model checkpoint as a `model` asset in
  `assets/model/<model_id>/`. Follow the specification in `meta/asset_types/model/specification.md`.
  Include checkpoint files, config, and tokenizer in the asset's `files/` directory, and set
  `description_path` in `details.json` to the canonical documentation file path.
* **Predictions asset**: After evaluation, save all per-instance predictions as a `predictions`
  asset in `assets/predictions/<predictions_id>/`. Follow the specification in
  `meta/asset_types/predictions/specification.md`. This enables later metric recomputation without
  re-running inference. Set `description_path` in `details.json` for the predictions asset too.
* Save model checkpoints to the task's `results/` or a designated output directory. Include the
  epoch number and validation metric in the checkpoint filename.
* Evaluate on all target benchmarks after training completes. Report per-dataset and aggregate
  metrics in `results/metrics.json`. Use explicit variants when the task keeps multiple comparable
  model conditions in one task; use the legacy flat format only when there is one reported metrics
  set.
* Record efficiency metrics in `results/metrics.json` whenever they apply. Use
  `efficiency_training_time_seconds` for total wall-clock training or fine-tuning time. Use
  `efficiency_inference_time_per_item_seconds` and `efficiency_inference_cost_per_item_usd` by
  dividing total inference time or cost by the number of inferred items. Omit non-applicable
  metrics; do not encode missing measurements as zero.
* Document the efficiency-metric formulas and raw inputs in `results/results_detailed.md`, including
  total seconds, inferred item count, and the API spend or machine hourly rate used in the cost
  calculation.
* Compare results against published baselines from the literature. Include the comparison in
  `results/results_detailed.md` with exact numbers from both your run and the published paper.
* Record the full training configuration in a reproducible format (JSON config file or command-line
  arguments logged in the session).
* Monitor GPU memory usage and training throughput. Report these in the results as they inform cost
  analysis.
* If training diverges (loss spikes, NaN gradients), log the failure and try a different approach.
  When training fails, try at least 3 different approaches before creating an intervention file.
  Document each attempt and its result in the intervention file. A single failed attempt is
  insufficient evidence that training is impossible.
* **Research traceability**: This is a research task with uncertain outcomes. Someone will later
  read the results to understand *why* the model performed the way it did. Save enough raw data to
  answer diagnostic questions:
  * Save all predictions (not just scores) so errors can be analyzed later.
  * Log per-item scores, not just aggregate metrics. Which instances were hardest? Which senses were
    confused most often?
  * Save training curves (loss, validation metric per epoch) as CSV or JSON, not just final numbers.
  * Log example predictions — especially wrong ones — with the model's confidence scores and the
    gold labels.
  * In `results/results_detailed.md`, include an error analysis section: what categories of errors
    dominate, what patterns appear in failures, what hypotheses explain the results.

## Common Pitfalls

* **Exceeding budget**: GPU compute costs accumulate quickly. Set alerts or periodic cost checks.
  Kill runs that will exceed the budget rather than hoping they converge faster.
* **Not saving checkpoints**: A crashed training run without checkpoints wastes all compute spent.
  Save frequently and verify checkpoints can be loaded before relying on them.
* **Not logging hyperparameters**: Unreproducible results are scientifically useless. Every
  hyperparameter must be logged before training starts. "I think I used lr=2e-5" is not acceptable.
* **Evaluating on training data**: Always evaluate on held-out sets. Double-check that evaluation
  data was excluded from training.
* **Ignoring training stability**: Report variance across seeds, not just best-run results. A single
  lucky seed does not demonstrate a method works.
* **Forgetting to tear down machines**: Remote GPU instances left running after training waste
  budget. Destroy machines immediately after results are saved and verified.

## Verification Additions

* Confirm `results/metrics.json` contains evaluation scores for all target benchmarks.
* Confirm relevant `efficiency_*` metrics exist whenever the task performed training or inference,
  and that the raw inputs for those calculations are documented.
* Confirm hyperparameters are logged in a structured format (JSON or equivalent) within the task
  folder.
* Confirm at least one model checkpoint exists and can be loaded. Confirm a `model` asset exists in
  `assets/model/` with valid `details.json` and a canonical description document.
* Confirm a `predictions` asset exists in `assets/predictions/` with per-instance prediction files.
* Confirm comparison against published baselines appears in the results with specific numbers from
  both sources.
* Confirm compute costs are recorded in `results/costs.json`.

## Related Skills

* `/implementation` -- for the training and evaluation code
* `/setup-remote-machine` -- for provisioning GPU instances
