# Electrophysiological Basis of Retinal Direction Selectivity

## Goal

Investigate how the internal electrophysiological properties of a single neuron shape its
direction-selective function. Using a compartmental model of a direction-selective retinal ganglion
cell, vary morphology, synaptic input density (AMPA and GABA), EPSP and IPSP amplitude and kinetics,
combinations of somatic voltage-gated sodium and potassium conductances, and the presence or absence
of voltage-gated conductances in the dendrites, then optimise these parameters against a target
relationship between the angle of a spreading excitatory/inhibitory wave and the cell's action
potential (AP) frequency.

## Research Questions

1. Which combinations of somatic voltage-gated sodium and potassium conductances maximise AP
   frequency for a preferred-direction wave while suppressing firing in the null direction?
2. How sensitive is directional AP tuning to morphological parameters such as dendritic branching
   pattern and compartment length and diameter?
3. What effect do the ratio and spatial distribution of AMPA vs GABA input density have on the
   sharpness of directional tuning?
4. Do active dendritic voltage-gated conductances improve, degrade, or have no effect on the match
   to the target angle-frequency curve compared with passive dendrites?
5. How closely can the optimised single-cell model reproduce the target tuning curve, and what
   residual error remains?

## Success Criteria

* A modifiable compartmental model in which morphology, input density, EPSP and IPSP amplitude and
  dynamics, somatic Na/K conductances, and dendritic active conductances can each be varied
  independently
* Identification of a Na/K conductance combination that reproduces the target angle-to-AP-frequency
  relationship within a defined error tolerance
* Systematic comparison of active vs passive dendritic configurations on directional tuning
  sharpness
* Reproducible simulation pipeline (seedable, scripted) that runs end-to-end on the researcher's
  local machine

## Current Phase

The project is just starting. The next step is a literature survey of compartmental models of
direction-selective retinal ganglion cells, together with selection of a published morphology and a
target angle-to-AP-frequency tuning curve to use as the optimisation reference.

## Results Dashboard

See [overview/README.md](overview/README.md) for the latest aggregated results, metrics, and task
status.

## Getting Started

1. Clone this repository.
2. Run `uv sync` to install Python dependencies.
3. Launch Claude Code or Codex CLI in the repo root and run `/setup-project` to configure the local
   environment and review the project description.
4. After setup, run `/create-task` for your first task (typically a literature survey), then
   `/execute-task <task_id>`.

## Daily Workflow

* `/create-task` — scaffold a new task folder and worktree from a suggestion or research question
* `/execute-task <task_id>` — run the full task lifecycle (research → planning →
  implementation → analysis → reporting)
* `/human-brainstorm` — turn suggestions from completed tasks into new task folders
* `uv run python -m arf.scripts.overview.materialize` — regenerate the `overview/` dashboard after
  completing tasks

## Key Rules

* **Every CLI call** is wrapped in `uv run python -m arf.scripts.utils.run_with_logs <cmd>` so logs
  are captured.
* **Tasks only modify files inside their own folder.** The only top-level files a task may touch are
  `pyproject.toml`, `uv.lock`, `ruff.toml`, and `.gitignore`.
* **Every task stage and every action is a separate, well-described commit.**
* **Completed task folders are immutable.** Fix mistakes via correction files in a new task, never
  by editing past folders.
* **Read through aggregators, never walk task folders directly.** Raw globs miss the corrections
  overlay.
* **Metrics must be registered in `meta/metrics/` before a task reports them.** Unregistered metrics
  fail verification.

## Project Structure

```text
arf/            Framework code: scripts, skills, specifications, styleguide, docs, tests
meta/           Project metadata: asset_types/, categories/, metrics/, task_types/
tasks/          One folder per research task (created by the create-task skill)
overview/       Materialized aggregator dashboard (regenerated, committed)
project/        Project-level files: description.md, budget.json
.claude/        Claude Code config (settings.json, rules/, skills/ symlinks)
.codex/         Codex CLI config (agents/, skills/ symlinks)
CLAUDE.md       Project overview loaded at Claude Code session start
pyproject.toml  Python deps and tooling config
doctor.py       Environment validation script
```

## Categories

* `cable-theory` — Cable Theory
* `compartmental-modeling` — Compartmental Modeling
* `dendritic-computation` — Dendritic Computation
* `direction-selectivity` — Direction Selectivity
* `patch-clamp` — Patch Clamp
* `retinal-ganglion-cell` — Retinal Ganglion Cell
* `synaptic-integration` — Synaptic Integration
* `voltage-gated-channels` — Voltage-Gated Channels

## Metrics

* `tuning_curve_rmse` — Tuning Curve RMSE (Hz), unit `none` — **key metric**, primary
  optimisation objective
* `direction_selectivity_index` — Direction Selectivity Index, unit `ratio`
* `tuning_curve_hwhm_deg` — Tuning Curve Half-Width at Half-Max (degrees), unit `none`
* `tuning_curve_reliability` — Tuning Curve Reliability, unit `ratio`

## Task Types

All 17 generic task types shipped with the framework are available; no project-specific task types
were added:

* `answer-question`, `baseline-evaluation`, `brainstorming`, `build-model`, `code-reproduction`,
  `comparative-analysis`, `correction`, `data-analysis`, `deduplication`, `download-dataset`,
  `download-paper`, `experiment-run`, `feature-engineering`, `infrastructure-setup`,
  `internet-research`, `literature-survey`, `write-library`

## Budget and Services

Total budget: **0.00 USD**. No paid services are configured — all work runs on the local machine
using the operator's existing LLM CLI subscription.

## Documentation

* [Autonomy and Safety](arf/docs/explanation/safety.md) — risks and consent model for autonomous
  agent operation
* [`arf/docs/tutorial/`](arf/docs/tutorial/) — walkthrough from empty fork to first results
* [`arf/docs/reference/`](arf/docs/reference/) — glossary, task folder structure, specifications,
  verificators, aggregators, skills, utilities
* [`arf/styleguide/python_styleguide.md`](arf/styleguide/python_styleguide.md) — Python
  conventions
* [`arf/styleguide/markdown_styleguide.md`](arf/styleguide/markdown_styleguide.md) — Markdown
  conventions
* [`arf/styleguide/agent_instructions_styleguide.md`](arf/styleguide/agent_instructions_styleguide.md)
  — conventions for agent instructions, rules, and skills

## License

Released under the [Apache License 2.0](LICENSE).
