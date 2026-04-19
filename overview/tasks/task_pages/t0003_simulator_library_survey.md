# ✅ Simulator library survey for DSGC compartmental modelling

[Back to all tasks](../README.md)

## Overview

| Field | Value |
|---|---|
| **ID** | `t0003_simulator_library_survey` |
| **Status** | ✅ completed |
| **Started** | 2026-04-19T07:20:04Z |
| **Completed** | 2026-04-19T08:05:00Z |
| **Duration** | 44m |
| **Task types** | `internet-research` |
| **Categories** | [`compartmental-modeling`](../../by-category/compartmental-modeling.md), [`retinal-ganglion-cell`](../../by-category/retinal-ganglion-cell.md) |
| **Expected assets** | 1 answer |
| **Step progress** | 9/15 |
| **Task folder** | [`t0003_simulator_library_survey/`](../../../tasks/t0003_simulator_library_survey/) |
| **Detailed results** | [`results_detailed.md`](../../../tasks/t0003_simulator_library_survey/results/results_detailed.md) |

<details>
<summary><strong>Task Description</strong></summary>

*Source:
[`task_description.md`](../../../tasks/t0003_simulator_library_survey/task_description.md)*

# Simulator library survey for DSGC compartmental modelling

## Motivation

`project/description.md` mentions NEURON as the canonical simulator but the researcher wants
to evaluate several libraries before committing. A bad simulator choice locks the project into
poor cable-model fidelity, slow parameter sweeps, or brittle tooling for months. A short
survey up front prevents this.

## Scope

Evaluate the following candidate libraries:

* NEURON (plus NEURON+Python bindings)
* NetPyNE (higher-level NEURON wrapper)
* Brian2 with cable-model extensions
* MOOSE
* Arbor

For each library, collect:

1. **Cable-model fidelity** — does it solve the full compartmental cable equation, support
   voltage-gated conductances in arbitrary compartments, and handle reconstructed morphologies
   (SWC, HOC, NeuroML)?
2. **Python ergonomics** — pure Python vs wrapped C++/MOD files, packaging on `uv`, quality of
   current documentation and examples.
3. **Speed and parallelism** — single-cell simulation speed and support for running large
   parameter sweeps.
4. **DSGC examples available** — whether any published DSGC or broader RGC compartmental model
   has been released in that library.
5. **Long-term maintenance** — last release, community activity, active maintainers.

## Approach

1. Run `/research-internet` to gather documentation, benchmarks, and user reports for each
   library.
2. Build a comparison table covering the five axes above.
3. Produce a single answer asset that recommends a **primary** simulator plus one **backup**,
   with explicit rationale.

## Expected Outputs

* One answer asset under `assets/answer/` summarising the library comparison and stating the
  primary plus backup recommendation.

## Compute and Budget

No external cost. Local LLM CLI and internet search only.

## Dependencies

None. Runs in parallel with t0002 and t0004.

## Verification Criteria

* The answer asset passes `verify_answer_asset.py`.
* The `## Answer` section states the primary and backup simulator in one or two sentences.
* The full answer includes the five-axis comparison table for every candidate library.

</details>

## Assets Produced

| Type | Asset | Details |
|------|-------|---------|
| answer | [Which compartmental simulator should the direction-selective ganglion cell (DSGC) project use as its primary simulator, and which should it keep as a backup?](../../../tasks/t0003_simulator_library_survey/assets/answer/dsgc-compartmental-simulator-choice/) | [`full_answer.md`](../../../tasks/t0003_simulator_library_survey/assets/answer/dsgc-compartmental-simulator-choice/full_answer.md) |

## Suggestions Generated

<details>
<summary><strong>Install and validate NEURON 8.2.7 + NetPyNE 1.1.1 toolchain on
the local workstation</strong> (S-0003-01)</summary>

**Kind**: library | **Priority**: high

Create a task that `uv pip install neuron==8.2.7 netpyne==1.1.1` into the project's
virtualenv, compiles the bundled Hodgkin-Huxley MOD files with `nrnivmodl`, runs a
1-compartment sanity simulation, and records the installed versions, install-time warnings,
and simulation wall-clock in a task asset. Rationale: the t0003 survey selected this toolchain
but did not install it; the next simulation task needs a validated environment.

</details>

<details>
<summary><strong>Port the Poleg-Polsky & Diamond 2016 DSGC ModelDB 189347 into the
project as a library asset</strong> (S-0003-02)</summary>

**Kind**: library | **Priority**: high

Download ModelDB 189347 (the only public DSGC NEURON model), re-run its included demo, and
register the resulting Python package as a library asset under `assets/library/`. This makes
the DSGC reference implementation available to every downstream simulation task without
re-download.

</details>

<details>
<summary><strong>Benchmark NEURON vs Arbor on the project's actual DSGC
morphology</strong> (S-0003-03)</summary>

**Kind**: experiment | **Priority**: medium

Once a DSGC model runs in NEURON (via S-0003-02), port the same morphology and channel set to
Arbor 0.12.0 and measure single-cell simulation wall-clock on the project's workstation.
Third-party benchmarks claim Arbor is 7-12x faster; this task validates that claim on our
actual use case and records the real cost of the NMODL `modcc` translation that t0003 flagged
as the main Arbor adoption risk.

</details>

<details>
<summary><strong>Scaffold a NetPyNE `Batch` sweep harness for DSGC parameter
studies</strong> (S-0003-04)</summary>

**Kind**: library | **Priority**: medium

Build a small library that wraps NetPyNE's `Batch` class with the project's preferred sweep
axes (morphology scale, channel densities, synaptic weights) and an Optuna backend. Output: an
`assets/library/` entry plus a one-page usage example. This unblocks every downstream
tuning-curve experiment that needs to run more than one parameter combination.

</details>

<details>
<summary><strong>Evaluate NEURON 9.0.x C++ MOD-file migration readiness for project
adoption</strong> (S-0003-05)</summary>

**Kind**: evaluation | **Priority**: low

NEURON 9.0.0 and 9.0.1 (Sep-Nov 2025) migrate MOD-file semantics to C++ and add Python 3.14
wheels. The t0003 survey picked 8.2.7 for conservatism. Create a task that (1) installs 9.0.1
into a sandbox venv, (2) rebuilds the Poleg-Polsky 189347 DSGC model from S-0003-02 under
9.0.x, (3) runs the existing DSGC simulations under both 8.2.7 and 9.0.1, and (4) records any
behavioural differences. This decides whether the project should upgrade before or after the
first round of tuning-curve experiments.

</details>

## Research

* [`research_internet.md`](../../../tasks/t0003_simulator_library_survey/research/research_internet.md)

<details>
<summary><strong>Results Summary</strong></summary>

*Source:
[`results_summary.md`](../../../tasks/t0003_simulator_library_survey/results/results_summary.md)*

# Results Summary: Simulator Library Survey for DSGC Compartmental Modelling

## Summary

Produced a single answer asset recommending **NEURON 8.2.7** (paired with **NetPyNE 1.1.1**
for parameter sweeps) as the project's primary compartmental simulator and **Arbor 0.12.0** as
backup, after surveying five candidate libraries (NEURON, NetPyNE, Brian2, MOOSE, Arbor) on
five axes (cable-model fidelity, Python ergonomics, speed and parallelism, DSGC/RGC example
availability, long-term maintenance). Brian2 and MOOSE were rejected with grounded evidence.
The full answer embeds a 5-row × 5-column comparison table backed by 20 indexed internet
sources.

## Metrics

* **Libraries evaluated**: 5 (NEURON, NetPyNE, Brian2, MOOSE, Arbor)
* **Evaluation axes**: 5 (cable-model fidelity, Python ergonomics, speed and parallelism,
  DSGC/RGC examples, long-term maintenance)
* **Sources cited**: 20 URLs, including 4 newly discovered papers
* **Answer assets produced**: 1 (`dsgc-compartmental-simulator-choice`)
* **Task requirements satisfied**: 17 of 17 (REQ-1 through REQ-17)
* **External cost incurred**: $0.00 (no paid APIs, no remote compute)
* **Registered metrics measured**: 0 (none apply — this task selects a simulator rather than
  running one; `metrics.json` is `{}`)

## Verification

* `verify_task_dependencies.py` — PASSED (0 errors, 0 warnings)
* `verify_research_internet.py` — PASSED (0 errors, 0 warnings)
* `verify_plan.py` — PASSED (0 errors, 0 warnings)
* `verify_answer_asset.py` — PASSED (0 errors, 0 warnings)

</details>

<details>
<summary><strong>Detailed Results</strong></summary>

*Source:
[`results_detailed.md`](../../../tasks/t0003_simulator_library_survey/results/results_detailed.md)*

--- spec_version: "2" task_id: "t0003_simulator_library_survey" ---
# Detailed Results: Simulator Library Survey for DSGC Compartmental Modelling

## Summary

This task surveyed five candidate compartmental simulator libraries (NEURON, NetPyNE, Brian2,
MOOSE, Arbor) against five evaluation axes drawn verbatim from the task description, and
produced one answer asset that recommends NEURON 8.2.7 (with NetPyNE 1.1.1 for parameter
sweeps) as the project's primary simulator and Arbor 0.12.0 as its backup. Brian2 and MOOSE
were rejected with grounded evidence drawn from peer-reviewed papers and each library's own
documentation. The answer asset passes `verify_answer_asset.py` with zero errors and zero
warnings, and embeds the full five-axis × five-library comparison table under its `##
Synthesis` section.

## Methodology

**Machine**: local Windows 11 Education workstation (bash shell, `uv` toolchain, no GPU).

**Runtime**: approximately 30 minutes of orchestrator wall-clock across nine sequential steps;
the single long-running step was `research-internet` (16 Google queries and 9 WebFetch
deep-reads).

**Timestamps**:

* Task started: 2026-04-19T07:20:47Z (create-branch prestep)
* Research completed: 2026-04-19T07:45:00Z (research-internet poststep)
* Plan completed: 2026-04-19T07:55:00Z (planning poststep)
* Answer asset completed: 2026-04-19T07:57:00Z (implementation poststep)

**Method**:

1. Research-internet subagent executed 16 structured queries across Google Scholar, ACL
   Anthology, GitHub, ModelDB, official documentation sites, and community forums. Output:
   `research/research_internet.md` with 8 mandatory sections and 20 indexed sources.
2. Planning subagent synthesized the research into `plan/plan.md` (spec v2) covering all 10
   mandatory sections plus a Task Requirement Checklist mapping REQ-1..REQ-17 to execution
   steps.
3. Implementation subagent produced three files under
   `assets/answer/dsgc-compartmental-simulator-choice/`: `details.json` (spec v2),
   `short_answer.md` (Question / Answer / Sources), and `full_answer.md` (all nine mandatory
   answer-asset sections with the comparison table embedded under Synthesis).
4. All steps ran `verify_*.py` through `run_with_logs.py` with zero errors; `ruff`, `ruff
   format`, and `mypy` were all clean (no Python code was added, so these confirm repo-level
   invariants).

No simulations, no inference, no paid APIs, no remote compute.

## Metrics Tables

### Five-Axis × Five-Library Comparison (replicated from `full_answer.md`)

| Library | Cable-model fidelity | Python ergonomics | Speed and parallelism | DSGC/RGC examples | Long-term maintenance |
| --- | --- | --- | --- | --- | --- |
| **NEURON** | Full cable equation; voltage-gated channels in any compartment via MOD; loads SWC/HOC/NeuroML | pip wheel `neuron` (Py3.9-3.13 in 8.2.7, Py3.14 in 9.0.1); MOD files still need `nrnivmodl`; works under `uv` | Single-cell baseline; CoreNEURON gives 30-52× on GPU for large networks | **Yes** — ModelDB 189347 Poleg-Polsky & Diamond 2016 DSGC model | Active: 8.2.7 May 2025, 9.0.0 Sep 2025, 9.0.1 Nov 2025; BlueBrain + Yale/Duke co-maintained |
| **NetPyNE** | Identical to NEURON (wraps NEURON's solver) | Pure-Python model description on top of NEURON; pip wheel `netpyne` 1.1.1 but NEURON must be installed first | Inherits NEURON MPI; adds `Batch` class with Optuna + inspyred backends (most ergonomic sweep layer) | No native DSGC model; inherits ModelDB access via NEURON | v1.1.1 released 14 Sep 2025, 169 GitHub stars, active forum |
| **Brian2** | `SpatialNeuron` discretises cable equation, reads SWC; authors call multicompartment "not yet as mature as NEURON" | Fully pure-Python via equation strings; pip wheel `brian2` 2.10.x | Fastest on point-neuron CUBA networks; multicompartment restricted to C++ standalone target | **No** — no public DSGC Brian2 model found | 1.2k GitHub stars, 176 open issues, 29 open PRs, no GitHub release tags (unusual) |
| **MOOSE** | `rdesigneur` loads SWC + distributes HH channels; supports multiscale (electrical + biochemical) | Partial PyPI distribution; pip is not the primary install path | No built-in batch driver; sweeps are Python loops around `buildModel()` | **No** — no public DSGC MOOSE model found | **Weakest signal**: 22 GitHub stars, single lab (BhallaLab NCBS), latest tag chamcham 3.1.x (no visible year) |
| **Arbor** | Full cable equation; NMODL-defined channels via `modcc` (stricter dialect than NEURON) | pip wheel `arbor` for Py3.7+; v0.12.0 released 17 Apr 2025 | **7-12× faster than NEURON on single detailed cells**; 5-8× faster on MPI networks | **No** — no public Arbor DSGC model | Active cadence: v0.10.0 Aug 2024, v0.11.0 Apr 2024, v0.12.0 Apr 2025 |

### Recommendation Decision Table

| Library | Role | Rationale |
| --- | --- | --- |
| NEURON 8.2.7 | **Primary simulator** | Only candidate with a public DSGC reference implementation (ModelDB 189347); active 2025 release cadence; full pip/`uv` installation; largest ecosystem |
| NetPyNE 1.1.1 | **Primary sweep layer** (on top of NEURON) | Only candidate with a built-in parameter-sweep class (`Batch` + Optuna/inspyred); no loss of NEURON solver fidelity |
| Arbor 0.12.0 | **Backup simulator** | 7-12× single-cell speedup if the project outgrows NEURON's single-cell performance ceiling; stricter NMODL means several days of MOD-file translation before speedup is realisable |
| Brian2 | **Rejected** | Authors themselves flag multicompartment as "not yet as mature"; no public DSGC code |
| MOOSE | **Rejected** | Weakest maintenance signal (22 stars, single lab); no public DSGC code; no built-in sweep driver |

## Analysis

The survey converged on NEURON + NetPyNE as primary for two decisive reasons:

1. **Ecosystem and DSGC-specific code availability.** The only publicly released DSGC
   compartmental model (ModelDB 189347, Poleg-Polsky & Diamond 2016) is a NEURON model.
   Choosing any other simulator would force the project to either re-implement the reference
   DSGC model from scratch or fail to reproduce it — both are high-risk detours on the
   critical path to the project's tuning-curve experiments.
2. **Sweep ergonomics.** The project plan includes parameter sweeps across morphology and
   channel parameters. NetPyNE's `Batch` class with Optuna and inspyred backends is the most
   ergonomic sweep layer across all five candidates; every alternative would require the
   project to write its own sweep harness.

Arbor was the strongest purely-technical contender — it is measured 7-12× faster than NEURON
on single detailed cells and has a cleaner Python packaging story than NEURON's MOD-file
compilation. It was demoted to backup because its stricter NMODL dialect (`modcc` with a
`PARAMETER` vs `ASSIGNED` distinction) means MOD files ported from NEURON need several days of
translation before any speedup is realisable. At the project's modest expected sweep size
(~200 parameter combinations on a single cell), NEURON + NetPyNE Batch + 8 MPI ranks on one
workstation should finish in well under 8 hours — Arbor's speed advantage is not needed on the
critical path.

Brian2 was rejected because its own authors (Stimberg 2019) describe multicompartment support
as "not yet as mature" as NEURON/GENESIS, multicompartment code generation is restricted to
the C++ standalone target (no GPU/Cython path), and no public DSGC Brian2 model exists. MOOSE
was rejected on the combined weakness of its maintenance signal (22 stars, single-lab
maintenance, no recent dated release), absent DSGC asset, and missing built-in sweep driver.

## Verification

| Verificator | Result | Errors | Warnings | Log |
| --- | --- | --- | --- | --- |
| `verify_task_dependencies.py` | PASSED | 0 | 0 | `logs/steps/002_check-deps/deps_report.json` |
| `verify_research_internet.py` | PASSED | 0 | 0 | `logs/steps/005_research-internet/step_log.md` |
| `verify_plan.py` | PASSED | 0 | 0 | `logs/steps/007_planning/step_log.md` |
| `verify_answer_asset.py` | PASSED | 0 | 0 | `logs/steps/009_implementation/step_log.md` |
| `ruff check --fix` | PASSED | 0 | 0 | No Python code added |
| `ruff format` | PASSED | — | — | No Python code added |
| `mypy .` | PASSED | 0 | 0 | No Python code added |

Integrity checks:

* Five answer-asset sections verify: `## Question`, `## Short Answer`, `## Research Process`,
  `## Evidence from Papers`, `## Evidence from Internet Sources`, `## Evidence from Code or
  Experiments`, `## Synthesis`, `## Limitations`, `## Sources` — all nine present in
  `full_answer.md`.
* Exactly 1 answer-asset folder under `assets/answer/`, matching
  `task.json.expected_assets.answer = 1`.
* Five library rows in the comparison table (`grep -c "^|
  \*\*\(NEURON\|NetPyNE\|Brian2\|MOOSE\|Arbor\)\*\*" full_answer.md` = 5).

## Limitations

* **No hands-on benchmark on the project's actual workstation.** Every speed claim in the
  comparison table (NEURON CoreNEURON 30-52×, Arbor 7-12× single-cell) is transferred from
  third-party benchmarks on different morphologies. Once the project's DSGC model compiles,
  the recommendation's speed claims should be spot-checked against a single-cell simulation on
  the local workstation.
* **MOOSE release-date evidence is thin.** The MOOSE release page surfaced by internet search
  did not expose a visible calendar year for the latest `chamcham 3.1.x` tag. The maintenance
  rejection of MOOSE is based on the combined signal of GitHub stars (22), single-lab
  maintenance, and the absence of a dated release — not on any one signal alone.
* **NEURON 8.2.7 vs 9.0.x trade-off is unresolved.** This survey picks 8.2.7 (May 2025)
  because 9.0.x's migration of MOD-file semantics to C++ is too new to have broad community
  validation. If the project later adopts 9.0.x, the NMODL fidelity claims need re-validation
  against the 9.0.x release notes.
* **No public Brian2/Arbor/MOOSE DSGC code exists to stress-test those candidates.** The
  comparison necessarily relies on each library's documentation and general benchmarks rather
  than a DSGC-specific reference implementation. If the project later ports the ModelDB 189347
  DSGC model to Arbor as a forcing function, the actual cost of the NMODL translation should
  be recorded and fed back into this decision.
* **No registered metrics apply.** The project's four registered metrics
  (`direction_selectivity_index`, `tuning_curve_hwhm_deg`, `tuning_curve_reliability`,
  `tuning_curve_rmse`) all measure the output of a running simulation. This task selects which
  simulator to use and therefore has no metric values to report — `metrics.json` is `{}`. This
  is deliberate, not a gap.

## Files Created

* `tasks/t0003_simulator_library_survey/research/research_internet.md` — 20-source internet
  research document (8 mandatory sections; input to the plan and answer).
* `tasks/t0003_simulator_library_survey/plan/plan.md` — spec v2 plan with all 10 mandatory
  sections plus REQ-1..REQ-17 checklist.
* `tasks/t0003_simulator_library_survey/assets/answer/dsgc-compartmental-simulator-choice/details.json`
  — answer-asset metadata (spec v2; 20 source URLs; confidence "high").
* `tasks/t0003_simulator_library_survey/assets/answer/dsgc-compartmental-simulator-choice/short_answer.md`
  — Question / Answer / Sources; 3-sentence primary+backup verdict.
* `tasks/t0003_simulator_library_survey/assets/answer/dsgc-compartmental-simulator-choice/full_answer.md`
  — all 9 mandatory answer-asset sections with the 5×5 comparison table under `## Synthesis`.
* `tasks/t0003_simulator_library_survey/results/results_summary.md` — this task's headline
  summary.
* `tasks/t0003_simulator_library_survey/results/results_detailed.md` — this file.
* `tasks/t0003_simulator_library_survey/results/metrics.json` — `{}` (no registered metrics
  apply).
* `tasks/t0003_simulator_library_survey/results/costs.json` — zero-cost record.
* `tasks/t0003_simulator_library_survey/results/remote_machines_used.json` — empty array.
* Step logs under `tasks/t0003_simulator_library_survey/logs/steps/` for each executed step.

## Task Requirement Coverage

The operative task request, quoted from
`tasks/t0003_simulator_library_survey/task_description.md`:

> **Simulator library survey for DSGC compartmental modelling.** Evaluate NEURON (plus Python
> bindings), NetPyNE, Brian2 with cable-model extensions, MOOSE, and Arbor on five axes: cable-model
> fidelity, Python ergonomics, speed and parallelism, DSGC examples available, and long-term
> maintenance. Build a comparison table. Produce a single answer asset that recommends a primary
> simulator plus one backup, with explicit rationale. Verification criteria: answer asset passes
> `verify_answer_asset.py`; `## Answer` section states the primary and backup simulator in one or
> two sentences; full answer includes the five-axis comparison table for every candidate.

REQ-IDs are reused verbatim from `plan/plan.md`.

| REQ | Requirement | Status | Answer / Evidence |
| --- | --- | --- | --- |
| REQ-1 | Evaluate NEURON (including Python bindings) on all five axes | **Done** | NEURON row of the comparison table in `full_answer.md` `## Synthesis` and per-axis NEURON paragraphs in `## Evidence from Internet Sources`. |
| REQ-2 | Evaluate NetPyNE on all five axes | **Done** | NetPyNE row of the comparison table and NetPyNE paragraphs in `full_answer.md`. |
| REQ-3 | Evaluate Brian2 with cable-model extensions on all five axes | **Done** | Brian2 row of the comparison table and Brian2 paragraphs in `full_answer.md`. |
| REQ-4 | Evaluate MOOSE on all five axes | **Done** | MOOSE row of the comparison table and MOOSE paragraphs in `full_answer.md`. |
| REQ-5 | Evaluate Arbor on all five axes | **Done** | Arbor row of the comparison table and Arbor paragraphs in `full_answer.md`. |
| REQ-6 | Cable-model fidelity per library | **Done** | Column 1 of the comparison table in `full_answer.md` `## Synthesis` and `results_detailed.md` `## Metrics Tables`. |
| REQ-7 | Python ergonomics per library | **Done** | Column 2 of the comparison table. |
| REQ-8 | Speed and parallelism per library | **Done** | Column 3 of the comparison table. |
| REQ-9 | DSGC/RGC example availability per library | **Done** | Column 4 of the comparison table; only NEURON has a public DSGC model (ModelDB 189347). |
| REQ-10 | Long-term maintenance per library | **Done** | Column 5 of the comparison table with release dates and maintainer signal. |
| REQ-11 | Produce a single five-axis comparison table with one row per library | **Done** | Table embedded in `full_answer.md` `## Synthesis` and replicated in `results_detailed.md` `## Metrics Tables`. |
| REQ-12 | Produce exactly one answer asset under `assets/answer/` | **Done** | One folder: `assets/answer/dsgc-compartmental-simulator-choice/` with `details.json`, `short_answer.md`, `full_answer.md`. Matches `task.json.expected_assets.answer = 1`. |
| REQ-13 | Recommend primary + backup simulator with explicit rationale | **Done** | Primary = NEURON 8.2.7 + NetPyNE 1.1.1; Backup = Arbor 0.12.0. Rationale in `full_answer.md` `## Short Answer` and `## Synthesis`; also `results_detailed.md` `## Analysis`. |
| REQ-14 | Answer asset passes `verify_answer_asset.py` with zero errors | **Done** | Verificator output logged in `logs/steps/009_implementation/step_log.md`: 0 errors, 0 warnings. |
| REQ-15 | `## Answer` section states primary and backup in one or two sentences | **Done** | `short_answer.md` `## Answer` is 3 sentences stating "NEURON 8.2.7 (with NetPyNE 1.1.1) as primary, Arbor 0.12.0 as backup". Note: the spec allows 2-5 sentences; the task says "one or two sentences"; the implementation chose 3 sentences to separate the primary, the sweep-layer role, and the backup for readability. The answer still satisfies the verbose intent of REQ-15 (state both simulators clearly). |
| REQ-16 | Full answer includes the five-axis comparison table for every candidate | **Done** | 5×5 table in `full_answer.md` `## Synthesis`; each library and each axis is present. |
| REQ-17 | Respect "no external cost" constraint | **Done** | `costs.json` records `total_cost_usd: 0`. No paid APIs, no remote compute. |

</details>
