---
name: "add-metric"
description: >-
  Interactively register one or more project metrics in meta/metrics/, grounded
  in project/description.md. Use during project setup or any time a new
  measurement needs to be tracked across tasks.
---
# Add Metric

**Version**: 2

## Goal

Register one or more project metrics in `meta/metrics/` through an interactive dialogue that
proposes candidates derived from the project description, confirms each with the user, writes the
required files, and passes the metrics verificator.

## Inputs

* `$ARGUMENTS` — optional path to `project/description.md`. If absent, the skill uses
  `project/description.md` by convention; if that file does not exist, the skill asks the user for
  metrics without the grounding proposal step.

## Context

Read before starting:

* `arf/specifications/metrics_specification.md` — folder layout, `description.json` schema, allowed
  `unit` and `value_type` values, verification rules.
* `arf/specifications/task_results_specification.md` — how tasks reference registered metrics in
  `metrics.json`.
* `arf/styleguide/markdown_styleguide.md`, `arf/styleguide/agent_instructions_styleguide.md`.
* `project/description.md` if present.
* Existing entries under `meta/metrics/` so proposals do not duplicate them.

## Steps

1. Read `arf/specifications/metrics_specification.md` to load the contract.

2. Print a 2-4 sentence explanation: registered metrics are project-defined quantitative
   measurements that tasks report in their `metrics.json`; unregistered metric keys fail
   verification. Task-specific operational counts (download sizes, paper counts) do **not** belong
   here — they go in `results_detailed.md`. Point the user to
   `arf/specifications/metrics_specification.md` for full details.

3. Read the project description. If not available, skip step 4 and ask the user to list metrics
   directly.

4. Propose 3-8 candidate metrics based on the project description's success criteria and research
   questions. For each candidate, list:
   * Suggested metric key (`snake_case`, descriptive, namespace-prefixed when useful).
   * Suggested display name.
   * A one-sentence rationale tied to the project description.
   * Recommended `unit` (from the allowed set: `f1`, `accuracy`, `precision`, `recall`, `ratio`,
     `count`, `usd`, `seconds`, `bytes`, `instances_per_second`, `none`).
   * Recommended `value_type` (`float`, `int`, `bool`, `string`).
   * Recommended `higher_is_better` (`true` when larger values rank better — F1, accuracy,
     correlation, throughput; `false` when smaller values rank better — MAE, MSE, latency, cost,
     error rate).

5. Ask the user which candidates to accept, edit, drop, or add. Accept "none for now".

6. For each accepted metric, confirm with the user:
   * `name` — one line, human-readable (≤ 80 characters).
   * `description` — what it measures, including dataset or scope (≥ 20 characters).
   * `unit` and `value_type` from the allowed values.
   * `higher_is_better` — required boolean. Never guess; ask the user explicitly and state the
     consequence (leaderboards and per-task "best variant" selection rank values in the direction
     this flag chooses).
   * Optional: `is_key: true` for headline metrics and a single `emoji` character.
   * Optional: `datasets` — list of dataset asset IDs the metric applies to. Leave empty if unsure;
     the field can be added later.

7. For each accepted metric, write `meta/metrics/<metric_key>/description.json`:

   ```json
   {
     "spec_version": 1,
     "name": "<Display Name>",
     "description": "<what it measures>",
     "unit": "<allowed value>",
     "value_type": "<allowed value>",
     "higher_is_better": <true or false>
   }
   ```

   Add `is_key`, `emoji`, and `datasets` only when the user explicitly confirmed them.

8. Run the verificator:

   ```bash
   uv run python -u -m arf.scripts.verificators.verify_metrics
   ```

   Fix every error reported.

9. Show the user the final list of new metric folders and ask for confirmation.

10. On confirmation, commit with message `Register <N> project metrics` listing the metric keys in
    the body.

## Output Format

One folder per accepted metric under `meta/metrics/<metric_key>/`, each containing a
`description.json` that conforms to `metrics_specification.md`.

## Done When

* For each accepted metric, `meta/metrics/<metric_key>/description.json` exists and passes
  `verify_metrics` with no errors.
* The user explicitly confirmed the list before commit, or chose to add no metrics.
* The commit landed, or the user was told "no changes made" when they chose to add none.

## Forbidden

* NEVER invent a metric without user confirmation.
* NEVER use a `unit` or `value_type` outside the allowed sets in `metrics_specification.md`.
* NEVER write placeholder text like `[TBD]` into `description.json`.
* NEVER commit without showing the user the final list first.
* NEVER silence a `verify_metrics` error — fix the content.
