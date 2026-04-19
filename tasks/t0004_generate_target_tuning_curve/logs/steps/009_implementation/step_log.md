---
spec_version: "3"
task_id: "t0004_generate_target_tuning_curve"
step_number: 9
step_name: "implementation"
status: "completed"
started_at: "2026-04-19T08:25:41Z"
completed_at: "2026-04-19T08:31:00Z"
---
## Summary

Implemented the synthetic target tuning curve generator and registered the resulting asset as
`target-tuning-curve` under `assets/dataset/`. The generator produces a closed-form
cosine-raised-to-power curve (θ_pref = 90°, r_base = 2 Hz, r_peak = 32 Hz, n = 2, noise σ = 3 Hz,
seed = 42) with DSI = 0.8824, well inside the required [0.6, 0.9] biological band. Running the
script writes `curve_mean.csv` (12 rows), `curve_trials.csv` (240 rows), `generator_params.json`,
and `results/images/target_tuning_curve.png`. The dataset asset was authored in full conformance
with `meta/asset_types/dataset/specification.md` (v2) and the task folder passes
`verify_task_folder` with zero errors.

## Actions Taken

1. Wrote `code/paths.py` centralising every input/output path (task root, dataset directory,
   per-file CSV/JSON/PNG paths) as Path constants, following the project Python style guide.
2. Wrote `code/generate_target.py`: a frozen `GeneratorParams` dataclass, keyword-only functions for
   `compute_mean_curve`, `compute_dsi`, `sample_trials`, dataframe builders, `plot_curve`, and a
   `main()` orchestration function. `main()` asserts the closed-form DSI lies in [0.6, 0.9] before
   writing any files, then emits the CSVs, generator-params JSON, and the diagnostic plot.
   Matplotlib is forced to the Agg backend so the script runs headlessly.
3. Added `matplotlib`, `pandas`, and `numpy` as project dependencies with
   `uv add matplotlib pandas numpy` (also updates `uv.lock` and `pyproject.toml`).
4. Ran the generator end-to-end via
   `run_with_logs.py uv run python -u -m tasks.t0004_generate_target_tuning_curve.code.generate_target`
   and confirmed the printed diagnostics: `DSI=0.8824`, `rows: mean_csv=12 trials_csv=240`, mean
   absolute bias 0.419 Hz, max absolute bias 1.063 Hz.
5. Wrote `assets/dataset/target-tuning-curve/details.json` (v2 spec) and `description.md` (v2 spec
   with all seven mandatory sections), keying the dataset ID to the kebab-case slug
   `target-tuning-curve` required by the dataset spec regex.
6. Ran `verify_task_folder` against the task and confirmed it passes with one non-blocking warning
   (FD-W002: empty `logs/searches/` directory, expected at this stage). There is no dedicated
   `verify_dataset_asset.py` in the repository; `verify_task_folder` plus the dataset spec checks
   performed by `verify_pr_premerge` are the relevant gates. Flowmark and ruff were both applied to
   the new markdown and Python.

## Outputs

* `tasks/t0004_generate_target_tuning_curve/code/paths.py`
* `tasks/t0004_generate_target_tuning_curve/code/generate_target.py`
* `tasks/t0004_generate_target_tuning_curve/assets/dataset/target-tuning-curve/details.json`
* `tasks/t0004_generate_target_tuning_curve/assets/dataset/target-tuning-curve/description.md`
* `tasks/t0004_generate_target_tuning_curve/assets/dataset/target-tuning-curve/files/curve_mean.csv`
* `tasks/t0004_generate_target_tuning_curve/assets/dataset/target-tuning-curve/files/curve_trials.csv`
* `tasks/t0004_generate_target_tuning_curve/assets/dataset/target-tuning-curve/files/generator_params.json`
* `tasks/t0004_generate_target_tuning_curve/results/images/target_tuning_curve.png`
* `pyproject.toml` and `uv.lock` (new dependencies matplotlib/pandas/numpy)

## Issues

The plan references a `verify_dataset_asset.py` verificator that does not exist in this repository;
the closest runtime check is `verify_task_folder` (passed). Structural gates for the dataset asset
will be re-applied by `verify_pr_premerge` at merge time. No other issues encountered.
