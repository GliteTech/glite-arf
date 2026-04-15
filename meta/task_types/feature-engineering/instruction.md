# Feature Engineering Instructions

## Planning Guidelines

* Use `/research-papers` to survey what features have been effective for the target task
  in published literature.
* Define each feature clearly: name, data type, value range, and semantic meaning. Plan
  the output schema before writing extraction code.
* Identify source data dependencies. Confirm that all input datasets and libraries are
  available from completed upstream tasks.
* Estimate computational cost for feature extraction. LLM-based features (embeddings,
  generated annotations) can be expensive; include API cost estimates in the plan.

## Implementation Guidelines

* Follow `arf/styleguide/python_styleguide.md` for all Python code. Key rules: absolute
  imports, keyword arguments for 2+ params, `@dataclass(frozen=True, slots=True)`,
  centralized paths in `code/paths.py`, named constants, explicit type annotations,
  100-char line limit.
* Document every feature in a feature manifest file that lists the feature name,
  description, data type, source, and any parameters used to compute it.
* Handle missing values explicitly using `None`/`null`, never `0.0` or empty strings. A
  missing feature value means "not computed", which is different from a computed value of
  zero.
* Test feature distributions after extraction. Log basic statistics (mean, median, min,
  max, null count) for numeric features and value counts for categorical features.
  Include histograms or distribution charts in the results images folder.
* Store features in standard formats: CSV with explicit dtypes, or JSON with typed
  schemas. Follow the Python style guide for dtype specifications.
* Write feature extraction as deterministic, reproducible functions. Pin random seeds,
  document API model versions, and log all parameters so that re-running the extraction
  produces identical output.
* Keep extraction code generic and reusable. Downstream tasks should be able to import
  the feature extraction functions directly.
* **Research traceability**: Feature quality directly affects downstream model
  performance. Save enough detail so someone can later diagnose why a feature helped or
  hurt:
  * Log the full distribution of each feature (histograms, percentiles) in
    `results/images/` and reference them in `results/results_detailed.md`.
  * For LLM-generated features, save the raw LLM responses alongside the extracted
    values. If a feature looks wrong, the raw response reveals whether the LLM
    misunderstood the prompt or the parsing was faulty.
  * Document feature correlations with the target variable. A feature with zero
    correlation is either uninformative or extracted incorrectly — the detailed results
    should distinguish these cases.
  * Save per-item feature values (not just aggregates) so downstream error analysis can
    check what feature values corresponded to model failures.

## Common Pitfalls

* Using `0.0` for missing feature values instead of `None`. This corrupts downstream
  statistics and model training.
* Not documenting feature semantics. A column named `f1` could mean anything; use
  descriptive names like `sense_frequency_ratio`.
* Generating features that leak target information (data leakage). Verify that no
  feature uses the gold-standard label as input.
* Skipping distribution analysis. Degenerate features (all zeros, all identical values)
  waste model capacity and indicate extraction bugs.

## Verification Additions

* Confirm that a feature manifest file exists documenting all extracted features.
* Verify that no feature column contains only null or only a single value.
* Check that output files have explicit dtype specifications or JSON schemas.
* Validate that re-running extraction on the same input produces identical output.

## Related Skills

* `/implementation` — general implementation workflow for coding steps.
* `/research-papers` — survey effective features in published literature.
