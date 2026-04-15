# Code Reproduction Instructions

## Planning Guidelines

* **"Reproduce" means training from scratch.** The primary approach must always be to train the
  model independently using the published procedure, data, and hyperparameters. Pre-trained
  checkpoints may be downloaded as validation references (to compare predictions against), but NEVER
  as a substitute for training. Using a pre-trained checkpoint for inference is evaluation, not
  reproduction.
* Use `/research-internet` to find the original code repository, any errata or known issues filed
  against the codebase, and pre-trained checkpoints (as validation references only).
* Use `/research-papers` to read the paper thoroughly before attempting reproduction. Note exact
  hyperparameters, dataset splits, and evaluation protocols.
* Document the exact environment requirements: Python version, CUDA version, library versions. Pin
  all dependencies to match the original setup.
* Plan how to measure `efficiency_training_time_seconds`,
  `efficiency_inference_time_per_item_seconds`, and `efficiency_inference_cost_per_item_usd`. Define
  which reproduction stages count as training vs. inference, how inferred items are counted, and
  whether inference cost comes from API billing or machine hourly pricing.
* If the reproduction task will report more than one comparable run, checkpoint, or configuration in
  the same task, define the explicit metrics variants that will be written to
  `results/metrics.json`.
* If the original code is unavailable, create an intervention file in `intervention/` requesting
  human assistance before proceeding.
* Plan remote machine setup via `/setup-remote-machine` if GPU training or inference is required.

## Implementation Guidelines

* Follow `arf/styleguide/python_styleguide.md` for all Python code. Key rules: absolute imports,
  keyword arguments for 2+ params, `@dataclass(frozen=True, slots=True)`, centralized paths in
  `code/paths.py`, named constants, explicit type annotations, 100-char line limit.
* **[CRITICAL]** The plan must mark the training step as `[CRITICAL]` in the Step by Step section.
  For models that require training, this means training from scratch using the published data and
  hyperparameters — not loading a pre-trained checkpoint for inference. If training becomes blocked
  (environment issues, missing data), create an intervention file — not silently substitute a
  different approach (such as using pre-trained checkpoints or existing predictions).
* Reproduce the exact environment first. Use the same library versions as the original paper.
  Document any version substitutions and their justification.
* Run the original code with minimal modifications. When changes are needed (e.g., path fixes, API
  updates), document every modification in the logs.
* Preserve all logging and debug output from the original code per the plan. Do not strip features
  when copying external code.
* Success criterion: reproduced results within **2 F1 points** of published numbers. If the gap is
  larger, investigate and document the cause before concluding.
* Record the relevant registered efficiency metrics in `results/metrics.json`. Use
  `efficiency_training_time_seconds` for total training or fine-tuning wall-clock time, and use
  `efficiency_inference_time_per_item_seconds` plus `efficiency_inference_cost_per_item_usd` for
  inference by dividing total inference time or cost by the number of inferred items. Omit
  non-applicable metrics instead of writing placeholder zeroes. When multiple comparable conditions
  are reported in one task, use the explicit multi-variant metrics format.
* Document the efficiency-metric formulas and raw inputs in `results/results_detailed.md`, including
  total seconds, inferred item count, and the API spend or machine hourly rate used in the cost
  calculation.
* The compare-literature step is essential. Create a detailed comparison table showing reproduced
  vs. published results for every reported metric.
* **Model asset**: Save the reproduced model as a `model` asset in `assets/model/<model_id>/`.
  Follow the specification in `meta/asset_types/model/specification.md`. Include the final
  checkpoint, config, and any tokenizer files. Set `description_path` in `details.json`. This allows
  future tasks to run inference without re-training.
* **Predictions asset**: Save all per-instance predictions as a `predictions` asset in
  `assets/predictions/<predictions_id>/`. Follow the specification in
  `meta/asset_types/predictions/specification.md`. Include instance IDs, gold labels, predicted
  labels, and confidence scores. Set `description_path` in `details.json`. This enables later metric
  recomputation (e.g., with different sense groupings) without re-running inference.
* **Research traceability**: Reproduction results will be scrutinized closely. Save enough raw data
  to diagnose discrepancies with published numbers:
  * Save all predictions so per-item comparison is possible later.
  * Log per-subset and per-POS breakdowns, not just aggregate scores.
  * When results diverge from published numbers, include a diagnostic section in
    `results/results_detailed.md`: which subsets diverge most, which item categories are affected,
    what environmental differences might explain the gap.
  * Save the full training/inference logs including any warnings or errors from the original code.

## Common Pitfalls

* **Using a pre-trained checkpoint instead of training from scratch.** This is NOT reproduction — it
  is evaluation. Even if the checkpoint produces matching numbers, it proves nothing about
  reproducibility of the training procedure. The entire point of reproduction is to verify that
  independently following the published methodology yields the same results.
* Modifying the original code "for cleanup" and accidentally changing behavior. Keep the original
  code as close to unmodified as possible.
* Using different random seeds, batch sizes, or training epochs than the paper specifies. These can
  cause significant result variation.
* Not checking for errata or updated results. Some papers have corrections posted after publication.
* Assuming the repository's main branch is the version used in the paper. Check for tagged releases
  or paper-specific branches.
* Skipping environment pinning and using latest library versions, which may introduce breaking API
  changes.

## Verification Additions

* Confirm that reproduced metrics are within 2 F1 points of published results, or that the deviation
  is documented with a root-cause analysis.
* Confirm relevant `efficiency_*` metrics exist whenever reproduction performed training or
  inference, and that the raw inputs for those calculations are documented.
* Verify that the comparison table includes all metrics reported in the paper.
* Check that environment details (library versions, hardware specs) are logged.
* Confirm a `model` asset exists in `assets/model/` with valid `details.json` and a canonical
  description document.
* Confirm a `predictions` asset exists in `assets/predictions/` with per-instance prediction files
  matching the specification.
* Validate that the original code modifications are documented in the logs.

## Related Skills

* `/implementation` -- general implementation workflow for coding steps.
* `/setup-remote-machine` -- provision machines matching the original hardware.
* `/research-internet` -- find code repositories and known issues.
