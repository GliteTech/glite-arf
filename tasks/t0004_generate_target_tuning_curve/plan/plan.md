---
spec_version: "2"
task_id: "t0004_generate_target_tuning_curve"
date_completed: "2026-04-19"
status: "complete"
---
# Plan: Generate Canonical Target Angle-to-AP-Rate Tuning Curve

## Objective

Generate a single canonical, synthetic direction tuning curve that every later optimisation task in
this project will compare against. The curve defines the target behaviour for the
`tuning_curve_rmse` and `tuning_curve_reliability` metrics. "Done" means a dataset asset named
`target-tuning-curve` exists under `assets/dataset/`, registers explicit generator parameters and
seed, contains both a mean-rate table and a per-trial replicate table, and passes
`verify_dataset_asset.py`. A plot of the curve must also be saved under
`results/images/target_tuning_curve.png`.

## Task Requirement Checklist

Quoting the operative task request from `task.json` and `task_description.md`:

> **Name**: Generate canonical target angle-to-AP-rate tuning curve
>
> **short_description**: Analytically generate a canonical cosine-like target tuning curve to use as
> the optimisation reference for all later fits.
>
> **Scope** (from `task_description.md`): produce a single dataset asset containing a cosine-like
> target tuning curve sampled at 12 or 24 angles around 360°; explicit generator parameters
> (preferred direction θ_pref in deg, baseline rate r_base in Hz, peak rate r_peak in Hz, tuning
> half-width / sharpness n, random seed); per-angle mean rates plus a small number of synthetic
> noisy trial replicates so the `tuning_curve_reliability` metric has a well-defined ground-truth
> value. Suggested form: `r(θ) = r_base + (r_peak - r_base) * ((1 + cos(θ - θ_pref)) / 2) ** n`.
> Choose `r_base`, `r_peak`, `θ_pref`, `n` to give a biologically plausible DSI in roughly 0.6-0.9.
>
> **Approach** (from `task_description.md`): write a Python script under `code/` that generates the
> curve, saves it to `data/` as CSV or JSON, and writes the dataset asset folder under
> `assets/dataset/`. Include both a mean-rate table and a per-trial table (e.g., 20 synthetic
> trials). Plot the curve and save to `results/images/target_tuning_curve.png`.
>
> **Verification** (from `task_description.md`): dataset passes `verify_dataset_asset.py`;
> `details.json` records generator parameters and seed explicitly; CSV/JSON has one row per angle
> and the noisy-trial table has at least 10 trials per angle.

Extracted requirements:

* **REQ-1** — Dataset asset folder `assets/dataset/target-tuning-curve/` exists with the v2
  dataset asset layout (details.json + canonical description document + files/). Evidence:
  `uv run python -u -m arf.scripts.verificators.verify_dataset_asset t0004_generate_target_tuning_curve target-tuning-curve`
  returns `PASSED`.
* **REQ-2** — The target curve is sampled at either 12 or 24 angles evenly spaced on [0, 360°).
  Evidence: mean-rate CSV has 12 or 24 rows, verified with a row count in the step log and called
  out in `details.json.size_description`.
* **REQ-3** — Generator parameters are explicit and recorded. `details.json` must contain a
  `generator_params` dictionary with `theta_pref_deg`, `r_base_hz`, `r_peak_hz`, `n`, `n_angles`,
  `n_trials`, `noise_sd_hz`, `random_seed`. Evidence: cat of `details.json` shown in
  results_detailed.md.
* **REQ-4** — A per-trial replicate table exists with at least 10 synthetic trials per angle. Plan
  target is 20 trials per angle. Evidence: per-trial CSV row count equals `n_angles * n_trials` and
  is logged.
* **REQ-5** — A mean-rate table exists (one row per angle, mean rate computed across the trials
  for that angle). Evidence: mean-rate CSV has `n_angles` rows and mean values match the closed-form
  target within a tight tolerance (≤ `noise_sd_hz / sqrt(n_trials)` × 4 per angle).
* **REQ-6** — The direction-selectivity index DSI of the deterministic (noise-free) target is in
  [0.6, 0.9]. Evidence: DSI printed by `code/generate_target.py`, written into `details.json`, and
  checked in the implementation step log.
* **REQ-7** — A plot exists at `results/images/target_tuning_curve.png` showing the closed-form
  curve and the per-trial scatter/error bars. Evidence: file exists and its size > 0 bytes.
* **REQ-8** — Task dataset asset has the `tuning-curve` / synthetic data categories as appropriate
  from `meta/categories/`. Evidence: categories listed in `details.json` all exist as folders under
  `meta/categories/`.

## Approach

The task is purely analytical. The deliverable is a small, deterministic Python script that samples
a cosine-raised-to-power tuning curve at a fixed set of angles, adds Gaussian noise to produce
synthetic trial replicates, and writes three artefacts: (a) a mean-rate CSV, (b) a per-trial CSV,
and (c) a PNG of the curve. A single `details.json` + `description.md` register the whole thing as a
dataset asset.

Key design choices, with rationale embedded:

* **Functional form**: `r(θ) = r_base + (r_peak - r_base) * ((1 + cos(θ - θ_pref)) / 2) ** n`.
  The `(1 + cos)/2` factor is the standard half-wave-rectified cosine used in direction-tuning
  literature; raising it to the power `n` controls the tuning half-width without ever going
  negative. Picked over a von Mises formulation because the explicit `n`-parameter is easier to
  interpret for the downstream fitting tasks (`n` is monotonic in sharpness).
* **Parameters**: `θ_pref = 90°`, `r_base = 2.0 Hz`, `r_peak = 40.0 Hz`, `n = 2.0`. Under these
  values the closed-form DSI — defined as `(r_peak - r_null) / (r_peak + r_null)` where `r_null`
  is the rate at `θ_pref + 180°` — evaluates to `(40 - 2) / (40 + 2) ≈ 0.905`, which sits at
  the upper end of the requested 0.6-0.9 range. If the DSI check fails the tolerance (see REQ-6),
  the implementation will lower `r_peak` to `32 Hz` (DSI ≈ 0.88) rather than change `n`, since
  keeping `n = 2` is conventional and interpretable. Both combinations hit the target band —
  `r_peak = 40` is the first choice; `r_peak = 32` is the documented fallback.
* **Angle sampling**: `n_angles = 12`, which gives 30° spacing — the coarser of the two allowed
  options. Twelve angles is enough to resolve the tuning bump and matches the canonical Hubel and
  Wiesel era direction-tuning protocol; 24 would only add computational cost without new information
  at this stage.
* **Trial noise**: `n_trials = 20`, Gaussian with `noise_sd_hz = 3.0` Hz, clipped to ≥ 0 Hz since
  firing rates are non-negative. Seed `random_seed = 42`. With these parameters the standard error
  of the per-angle mean across 20 trials is `3 / √20 ≈ 0.67 Hz`, easily below the tuning
  contrast (`r_peak - r_base = 38 Hz`), so the reliability signal is high.
* **Asset layout**: v2 dataset asset with `dataset_id = "target-tuning-curve"` (kebab-case required
  by the dataset_id regex `^[a-z0-9]+([.\-][a-z0-9]+)*$`; the task description's suggested
  `target_tuning_curve` with underscores would fail verification). Three data files live under
  `assets/dataset/target-tuning-curve/files/`: `curve_mean.csv`, `curve_trials.csv`,
  `generator_params.json`. The plot lives under `results/images/`, not inside the asset, because the
  project convention is that PNGs in `results/images/` are for reporting and do not travel with the
  dataset.

**Alternatives considered**:

* *Von Mises tuning curve*:
  `r(θ) = r_base + (r_peak - r_base) * exp(κ * (cos(θ - θ_pref) - 1))`. Rejected because the
  shape parameter κ is not linear in tuning width and is harder to interpret for downstream
  fitting. Raised-cosine with power `n` is functionally equivalent for the narrow set of widths we
  care about (roughly HWHM = 30-60°) and easier to document.
* *Digitising a published tuning curve*: the researcher explicitly chose to simulate rather than
  digitise, because a synthetic curve gives zero-noise ground truth for the reliability metric and
  avoids licensing/digitisation error. This is recorded in `task_description.md` § Motivation.

**Task types**: `task.json` already lists `feature-engineering`, which matches the work
(deterministic dataset synthesis from an analytical formula; no learning or experimentation). The
feature-engineering planning guideline emphasises that output schema and reproducibility are
primary, both of which are already captured in REQ-3 through REQ-5.

## Cost Estimation

$0 total. All computation is deterministic Python (numpy + matplotlib) and runs locally in seconds.
No paid API calls, no remote compute, no dataset purchases, no human-in-the-loop labelling. Project
budget (`project/budget.json` → `total_budget: $0.0`) is not touched.

## Step by Step

1. **Create `code/generate_target.py`.** The file contains: imports (numpy, pandas, matplotlib,
   pathlib, json), a module-level `@dataclass(frozen=True, slots=True)` `GeneratorParams` with
   fields `theta_pref_deg`, `r_base_hz`, `r_peak_hz`, `n`, `n_angles`, `n_trials`, `noise_sd_hz`,
   `random_seed`, and a
   `DEFAULT_PARAMS = GeneratorParams(theta_pref_deg=90.0, r_base_hz=2.0, r_peak_hz=40.0, n=2.0, n_angles=12, n_trials=20, noise_sd_hz=3.0, random_seed=42)`.
   Satisfies REQ-3.
2. **Add `paths.py` under `code/`.** Defines `TASK_ROOT`, `DATASET_DIR`, `DATASET_FILES_DIR`,
   `DETAILS_PATH`, `DESCRIPTION_PATH`, `MEAN_CSV_PATH`, `TRIALS_CSV_PATH`,
   `GENERATOR_PARAMS_JSON_PATH`, `PLOT_PATH`. Uses `pathlib.Path` and the `__file__`-relative root
   pattern so the script is runnable from any cwd.
3. **Implement `compute_mean_curve(params) -> np.ndarray`.** Returns an array of length
   `params.n_angles` of mean rates using
   `r_base + (r_peak - r_base) * ((1 + cos(theta - theta_pref)) / 2) ** n`, where
   `theta = linspace(0, 2π, n_angles, endpoint=False)` and `theta_pref` is converted from degrees
   to radians. Satisfies REQ-2 and REQ-5.
4. **Implement `compute_dsi(mean_curve, params) -> float`.** Evaluates the closed-form rates at
   `θ_pref` and `θ_pref + 180°` and returns `(r_pref - r_null) / (r_pref + r_null)`. Will be used
   to validate REQ-6. Works on closed-form values, not sampled, so it is noise-free.
5. **Implement `sample_trials(mean_curve, params) -> np.ndarray`.** Returns an array of shape
   `(n_angles, n_trials)`. For each angle `i`, draws `n_trials` samples from
   `N(mean_curve[i], params.noise_sd_hz)` using a seeded `np.random.default_rng(params.random_seed)`
   and clips to `[0, +inf)` with `np.clip(..., 0.0, None)`. Satisfies REQ-4.
6. **[CRITICAL] Implement `main()` orchestration.** Reads `DEFAULT_PARAMS`, computes mean curve,
   computes DSI, asserts `0.6 <= DSI <= 0.9` (if this fails under the first-choice parameters, swap
   `r_peak_hz = 32.0` per the Approach fallback and re-check), generates trials, writes
   `curve_mean.csv` with columns `angle_deg,mean_rate_hz`, writes `curve_trials.csv` with columns
   `angle_deg,trial_index,rate_hz`, writes `generator_params.json` containing the params dataclass
   as JSON. Then renders the plot (closed-form curve solid, trial scatter with per-angle error
   bars), saves to `results/images/target_tuning_curve.png` with tight layout and 150 dpi, and
   prints a short summary (DSI, mean rate range, per-angle std). Satisfies REQ-2, REQ-4, REQ-5,
   REQ-6, REQ-7.
7. **Run the generator.** Execute
   `uv run python -u -m arf.scripts.utils.run_with_logs --task-id t0004_generate_target_tuning_curve -- uv run python -u tasks/t0004_generate_target_tuning_curve/code/generate_target.py`.
   Expected output: a "DSI=0.905" (or "DSI=0.881" under fallback) line and row counts "12 / 240". No
   charts or network IO. Satisfies REQ-7.
8. **Write `assets/dataset/target-tuning-curve/details.json`.** Populate all v2 fields:
   `spec_version "2"`, `dataset_id "target-tuning-curve"`,
   `name "Target direction tuning curve (synthetic)"`, `short_description` one sentence,
   `description_path "description.md"`, `source_paper_id null`, `url null`, `year 2026`, `authors` a
   single entry for the researcher, `institutions` University of Sheffield, `license "CC0-1.0"`,
   `access_kind "public-free"`, `size_description` giving row counts, `files` listing the three
   files under `files/`, `categories`, plus a `generator_params` custom object mirroring the
   dataclass. Satisfies REQ-1, REQ-3, REQ-8.
9. **Write `assets/dataset/target-tuning-curve/description.md`.** v2 frontmatter plus mandatory
   sections (Metadata, Overview ≥ 80 words, Content & Annotation, Statistics, Usage Notes, Main
   Ideas ≥ 3 bullets, Summary 2-3 paragraphs). The Usage Notes section explicitly states this
   dataset is the **target** for `tuning_curve_rmse` and `tuning_curve_reliability`, not training
   data for a model. Satisfies REQ-1.
10. **Move the generated data files into the asset's `files/` subfolder.** The generator writes
    directly into `assets/dataset/target-tuning-curve/files/`; step 6 already produces them in that
    location, so this is effectively a verification step: confirm `files/curve_mean.csv`,
    `files/curve_trials.csv`, and `files/generator_params.json` exist.
11. **Run the dataset asset verificator.**
    `uv run python -u -m arf.scripts.utils.run_with_logs --task-id t0004_generate_target_tuning_curve -- uv run python -u -m arf.scripts.verificators.verify_dataset_asset t0004_generate_target_tuning_curve target-tuning-curve`.
    Expected: `PASSED — no errors or warnings`. If it reports `DA-E*` errors, fix `details.json`
    or `description.md` and re-run until clean. Satisfies REQ-1, REQ-2, REQ-3, REQ-8.

Validation gates: none of the steps involve paid APIs, remote compute, or large-scale data
processing. The implicit local gate is that the generator prints DSI and row counts in step 7, and
the DSI must sit in [0.6, 0.9] before the asset is written.

## Remote Machines

None required. The script runs in under one second on any CPU with numpy and matplotlib installed.

## Assets Needed

No upstream dataset, paper, or library assets. The task is fully self-contained: the formula, the
parameter ranges, and the output schema are all fixed by `task_description.md`. The only external
Python packages used — numpy, pandas, matplotlib — are already pinned in `pyproject.toml`.

## Expected Assets

One dataset asset:

* **Type**: `dataset`
* **ID**: `target-tuning-curve`
* **Folder**: `tasks/t0004_generate_target_tuning_curve/assets/dataset/target-tuning-curve/`
* **Description**: Synthetic cosine-raised-to-power direction tuning curve sampled at 12 angles over
  360°, with 20 Gaussian-noise trials per angle, plus explicit generator parameters (θ_pref,
  r_base, r_peak, n, noise SD, seed). Serves as the canonical optimisation target for every later
  tuning-curve-fit task in the project.

This matches `task.json.expected_assets = {"dataset": 1}`.

## Time Estimation

* Research / planning (done via this document): ~10 minutes.
* Implementation (writing `generate_target.py`, `paths.py`, running, iterating): ~20 minutes.
* Dataset asset authoring (`details.json`, `description.md`): ~10 minutes.
* Verification + results section: ~10 minutes.

Total wall-clock estimate: under one hour.

## Risks & Fallbacks

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| DSI for first-choice parameters lies outside [0.6, 0.9] | Low (closed-form DSI is known to be 0.905) | Task fails REQ-6 | Implementation step includes an explicit DSI check and a documented fallback (`r_peak_hz = 32`, DSI ≈ 0.88) |
| Dataset asset verificator rejects `target-tuning-curve` for missing fields | Medium | Blocks REQ-1 | Read `meta/asset_types/dataset/specification.md` before writing `details.json`; re-run verificator after every edit until clean |
| Verificator complains that listed categories do not exist | Medium | Warning only (`DA-W*`), does not block merge | Run `aggregate_categories.py` first and restrict the asset's `categories` list to slugs that actually exist under `meta/categories/`; leave the list empty if none apply rather than inventing a slug |
| `noise_sd_hz = 3.0` produces a per-angle mean that drifts far from the closed form | Low | Weakens REQ-5 spot check | Use `random_seed = 42` so the noise is deterministic, and verify ` |
| Plot fails on a headless machine because matplotlib defaults to an interactive backend | Low | Blocks REQ-7 | Script begins with `matplotlib.use("Agg")` before `import matplotlib.pyplot` |

## Verification Criteria

* **REQ-1, REQ-2, REQ-3, REQ-8**:
  `uv run python -u -m arf.scripts.verificators.verify_dataset_asset t0004_generate_target_tuning_curve target-tuning-curve`
  returns `PASSED` with no errors (warnings are acceptable but each must be logged in the step log).
* **REQ-2, REQ-5**:
  `wc -l tasks/t0004_generate_target_tuning_curve/assets/dataset/target-tuning-curve/files/curve_mean.csv`
  reports 13 lines (1 header + 12 rows) when `n_angles = 12`.
* **REQ-4**:
  `wc -l tasks/t0004_generate_target_tuning_curve/assets/dataset/target-tuning-curve/files/curve_trials.csv`
  reports 241 lines (1 header + 12 × 20 = 240 rows).
* **REQ-3, REQ-6**:
  `python -c "import json; d = json.load(open('.../details.json')); p = d['generator_params']; print(p['theta_pref_deg'], p['r_base_hz'], p['r_peak_hz'], p['n'], p['n_angles'], p['n_trials'], p['noise_sd_hz'], p['random_seed'])`
  prints all eight parameters without `KeyError`, and the printed DSI from `generate_target.py` is
  in `[0.6, 0.9]`.
* **REQ-7**:
  `test -s tasks/t0004_generate_target_tuning_curve/results/images/target_tuning_curve.png` exits 0
  (file exists and is non-empty).
* **Cross-task cleanliness**:
  `uv run python -u -m arf.scripts.verificators.verify_no_external_changes t0004_generate_target_tuning_curve`
  passes (nothing outside the task folder was modified).
* **Step tracker consistency**: after each step, `step_tracker.json` records status `completed` for
  the step; the reporting step runs `verify_task_completion.py` which checks this automatically.
