---
name: "planning"
description: "Synthesize research outputs into a task plan with steps, costs, risks, and checks."
---
# Planning

**Version**: 7

## Goal

Synthesize all research outputs into a comprehensive, self-contained task plan with cost estimates,
step-by-step actions, risk assessment, and verification criteria.

## Inputs

* `$TASK_ID` — the task folder name (e.g., `t0016_baseline_wsd_with_bert`)

## Context

Read before starting:

* `arf/docs/howto/use_aggregators.md` — JSON output structure for all aggregators

* `project/description.md` — project goals and scope

* `project/budget.json` — project budget and per-task spending limits

* `tasks/$TASK_ID/task.json` — task objective, dependencies, expected assets

* `tasks/$TASK_ID/research/research_papers.md` — findings from existing papers

* `tasks/$TASK_ID/research/research_internet.md` — findings from internet research

* `tasks/$TASK_ID/research/research_code.md` — findings from code research (if exists)

* `arf/specifications/plan_specification.md` — authoritative format specification for `plan/plan.md`

* Asset type specifications in `meta/asset_types/` for each expected asset type listed in
  `task.json`

* Task type definitions — run to get all available types:

  ```bash
  uv run python -u -m arf.scripts.aggregators.aggregate_task_types --format json
  ```

* Task type instructions in `meta/task_types/<slug>/instruction.md`

* `arf/styleguide/markdown_styleguide.md` — formatting rules (100-char lines, `*` bullets, heading
  hierarchy)

## Critical Rules

1. Do not commit. The orchestrator owns the step lifecycle — prestep, commit, step log, and poststep
   are handled by the orchestrator, not by this skill.

2. Do not run prestep or poststep.

3. Do not modify files outside the task folder (except `pyproject.toml`, `uv.lock`, `ruff.toml`,
   `.gitignore`, `mypy.ini`).

4. The plan must be self-contained. The implementation agent reads the plan fresh with no prior
   context. Repeat all critical information — do not write "as discussed in research" without
   stating what was discussed. Every term of art, file path, and assumption must be stated
   explicitly in the plan.

## Steps

### Phase 1: Understand the Task and Research

1. Read `tasks/$TASK_ID/task.json`. Extract the objective, dependencies, expected assets, and every
   concrete requirement from the task text.

   * Read the task name, `short_description`, and the resolved long description. If `task.json`
     contains `long_description_file`, read that markdown file from the task root.

   * Split every explicit deliverable, question, analysis dimension, TODO item, constraint, and
     success condition into a separate requirement.

   * Assign stable IDs `REQ-1`, `REQ-2`, ... in the order they appear.

   * Do not merge distinct asks into one vague line item.

2. Determine task types. Check `task.json` for the `task_types` field.

   * If `task_types` is non-empty, read each type's instruction file at
     `meta/task_types/<slug>/instruction.md`. Follow the Planning Guidelines section from each
     matched type.

   * If `task_types` is empty, load all task type descriptions via the aggregator:

     ```bash
     uv run python -u -m arf.scripts.aggregators.aggregate_task_types \
       --format json
     ```

   Select the best-matching type(s) based on the task's name, `short_description`, and resolved long
   description. Read the matching type's `instruction.md` and follow its Planning Guidelines.

   * If no type matches well, proceed without type-specific instructions.
   * If a matched type is `correction`, decide whether this task genuinely needs a plan.
     Straightforward corrections may have no planning step at all. If the planning step is present,
     keep the plan focused on the target artifacts, the chosen correction mechanism (`update`,
     `delete`, `replace`, `file_changes`), and how the corrected effective state will be verified.

3. Read all research files produced by earlier steps:

   * `tasks/$TASK_ID/research/research_papers.md` — key findings, methodology insights,
     recommendations, hypotheses, best practices

   * `tasks/$TASK_ID/research/research_internet.md` — additional findings, tools, libraries, recent
     developments, gap resolutions

   * `tasks/$TASK_ID/research/research_code.md` (if exists) — existing libraries, reusable code,
     lessons learned from prior tasks

4. For each dependency in `task.json`, read its results summary to understand what it produced:

   ```bash
   uv run python -u -m arf.scripts.aggregators.aggregate_tasks \
     --format json --detail full --ids <dep_id_1> <dep_id_2> ...
   ```

5. Read `project/budget.json` to understand spending constraints.

6. Read asset type specifications in `meta/asset_types/` for each expected asset type.

7. Discover registered metrics. Run:

   ```bash
   uv run python -u -m arf.scripts.aggregators.aggregate_metrics --format json --detail full
   ```

   Review every registered metric and decide which ones this task can measure. A metric applies when
   the task performs the activity the metric measures — for example
   `efficiency_training_time_seconds` applies when the task trains a model,
   `efficiency_inference_time_per_item_seconds` applies when the task runs inference. Do not
   force-fit metrics that have no connection to the task's work. Carry the list of applicable
   metrics into Phase 2 so each one gets a measurement step in the plan.

### Phase 2: Design the Approach

1. Synthesize findings from all research files into a concrete technical approach:

   * Which methods to use (informed by research_papers.md recommendations)
   * Which tools and libraries to leverage (informed by research_internet.md)
   * Which existing project libraries to import (informed by research_code.md)
   * Which code to copy from prior tasks (informed by research_code.md)
   * Which prior answer assets already address part of the question space
   * For correction tasks, whether the fix is metadata-only, whole-artifact replacement, or partial
     file overlay

2. Identify the task's non-negotiable core. Determine which steps define the fundamental nature of
   the task — the steps without which the task has not been done. Mark these as critical steps in
   the Step by Step section.

   For reproduction tasks: "reproduce" means re-running the original process to produce fresh
   outputs — training the model, running inference, generating predictions from scratch. Evaluating
   pre-existing predictions from another source (for example, a benchmark) is validation, not
   reproduction. If the task says "reproduce", the plan must define exactly what must be re-executed
   and mark those steps as critical. If a critical step becomes impossible (e.g., model checkpoint
   unavailable), the implementation agent must create an intervention file — not silently substitute
   a different approach.

   For non-reproduction tasks, identify what makes the task meaningfully different from just reading
   existing results. Every task must produce something that didn't exist before.

3. Consider alternative approaches. Before committing to one approach, identify at least one
   alternative and explain why the chosen approach is better. Document the rejected alternatives
   briefly in the Approach section — this prevents tunnel vision and preserves the decision
   rationale.

4. Estimate costs:

   * API call costs (LLM inference, external services)
   * Remote compute costs (GPU rental, cloud instances)
   * Compare total estimated cost against `project/budget.json`

5. Pre-mortem risk identification. Imagine the task has already failed. Work backwards: what went
   wrong? This technique surfaces risks that forward-looking analysis misses. Common failure modes:
   API rate limits, data format mismatches, download failures, model training instability, budget
   overruns, missing dependencies, incorrect assumptions from research.

   For each risk that could block a critical step, the mitigation must include an escalation path
   (intervention file) if no technical workaround preserves the task's core purpose. "Retry" is not
   sufficient mitigation for permanent failures like archived repositories or revoked access.

6. Define concrete verification criteria — exact commands to run and observable outputs that confirm
   the task is complete, including checks that each `REQ-*` item is satisfied by the outputs.

### Phase 3: Write plan.md

1. Read `arf/specifications/plan_specification.md` — the authoritative format spec.

2. Write `tasks/$TASK_ID/plan/plan.md` with YAML frontmatter using the current `spec_version` from
   the specification and all 11 mandatory sections.

   Key quality requirements for each section:

   * `## Objective` — self-contained restatement of the task goal. A reader must understand the goal
     without opening any other file. Include success criteria.

   * `## Task Requirement Checklist` — quote the operative task text verbatim, then list every
     concrete requirement as a separate `REQ-*` item. For each item, state which step(s) will
     satisfy it and what evidence will prove completion.

   * `## Approach` — technical approach grounded in research findings. Repeat the key findings that
     inform the approach — do not just reference research files. Briefly note alternatives
     considered and why they were rejected. Include the recommended task type(s) from
     `meta/task_types/` and explain how the type-specific Planning Guidelines influenced the
     approach. If the task's `task_types` field was empty in `task.json`, state the recommended
     types here so the orchestrator or human can update `task.json`.

   * `## Cost Estimation` — itemized dollar amounts. $0 is valid but must be stated with reasoning.
     Compare against project budget.

   * `## Step by Step` — numbered steps. Each step must name:

     * Specific files to create or modify (e.g., `code/extract.py`)

     * Inputs each step reads and outputs it produces

     * Libraries to import with full import paths

     * Code to copy from prior tasks with source file paths

     * Expected observable output (what to see when it works)

     * The `REQ-*` items it satisfies

     * For answer-question tasks, the exact `assets/answer/<answer_id>/` folders to produce and the
       evidence sources each answer will cite

     * For correction tasks, the exact correction files to create, the target artifact IDs, whether
       replacement assets must also be created in the current task, and how aggregator output will
       confirm the correction. For complex tasks, group steps into milestones. Each milestone should
       be independently verifiable — the agent can confirm that milestone is done before proceeding.
       Steps should be idempotent where possible (safely re-runnable). For risky steps, include
       recovery instructions.

   * For each applicable registered metric identified in Phase 1 step 7, the Step by Step section
     must include a concrete measurement action: which step measures it, what raw values are
     collected, and how they are written to `results/metrics.json`. If a metric seems applicable but
     cannot be measured (e.g., inference time when predictions are backfilled from a prior task),
     state this explicitly in the plan so the omission is deliberate rather than accidental. When
     the plan includes writing `metrics.json`, specify which format to use (legacy flat or explicit
     variant). If the task compares multiple conditions, use the explicit variant format. Read
     `arf/specifications/metrics_specification.md` for the exact structure — do NOT invent a format.

   * **Validation gates for expensive operations**: If a step runs inference, trains a model, calls
     paid APIs, or processes data at scale (more than 100 items), the step must include:

     * The trivial baseline to compare against (e.g., majority class for classification, frequency
       heuristic for tagging, random for retrieval). Name the specific number.

     * A `--limit` setting for the initial validation run (typically 10-20 instances).

     * An explicit failure condition: "if result is at or below [baseline], STOP and debug
       individual predictions — do not proceed to full scale." Use the baseline as the threshold,
       not an arbitrary lower number.

     * An individual-output inspection requirement: "after the small run, read 5 individual
       predictions and verify the input was correctly formatted, the model's response is reasonable,
       and the scoring logic is correct for each case."

   * `## Remote Machines` — compute requirements or "None required" with reasoning.

   * `## Assets Needed` — input assets with sources (dependency tasks, external URLs).

   * `## Expected Assets` — output assets matching `task.json` `expected_assets`.

   * `## Time Estimation` — per-phase wall-clock estimates.

   * `## Risks & Fallbacks` — table with at least 2 rows. Use pre-mortem thinking: imagine the task
     has failed, then list what went wrong and how to prevent it.

   * `## Verification Criteria` — at least 3 testable bullet points. Each criterion must include the
     exact command to run and the expected output. "Verificator passes" is a valid criterion only if
     the specific verificator command is named. Include at least one criterion that explicitly
     checks requirement coverage.

3. Add additional sections wherever they improve clarity (e.g., `## Architecture`, `## Data Flow`,
   `## Alternative Approaches Considered`).

4. Coverage check: compare the finished plan against `task.json` line by line. Confirm every
   concrete ask from the task text appears as a `REQ-*` item and is mapped to one or more execution
   steps. If anything in the task text is not covered, revise the checklist and plan before
   continuing.

5. Self-containment check: re-read the plan as if you have never seen the research files. Does the
   plan make sense on its own? Are all terms defined? Are all file paths explicit? If not, add the
   missing context.

6. Follow the markdown style guide: 100-char line width, `*` bullets, heading hierarchy.

### Phase 4: Verify

1. Run the verificator:

   ```bash
   uv run python -u -m arf.scripts.verificators.verify_plan $TASK_ID
   ```

2. Fix all errors. Address warnings unless there is a documented reason to skip them.

3. Re-run until zero errors.

## Done When

* `tasks/$TASK_ID/plan/plan.md` exists and follows the specification

* Verificator passes with zero errors

* All 11 mandatory sections are present

* Plan is self-contained — makes sense without reading research files

* `## Task Requirement Checklist` covers every concrete requirement from `task.json` with stable
  `REQ-*` IDs

* Step by Step has numbered items naming specific files, inputs, and outputs

* Step by Step explicitly references the `REQ-*` items it satisfies

* Cost Estimation includes dollar amounts

* Risks & Fallbacks has a table with at least 2 risks (informed by pre-mortem)

* Verification Criteria has at least 3 bullet points with exact commands

* Approach section mentions alternatives considered

* Every applicable registered metric has a measurement step or an explicit reason for omission

## Forbidden

* NEVER commit — the orchestrator handles all commits.

* NEVER run `prestep.py` or `poststep.py`.

* NEVER write vague steps like "implement the model" or "process the data" — each step must name
  specific files, inputs, and outputs.

* NEVER skip cost estimation — $0 is valid but must be stated explicitly with reasoning.

* NEVER omit Risks & Fallbacks — every plan has risks; "no risks" is not acceptable.

* NEVER fabricate cost estimates, time estimates, or risk assessments.

* NEVER skip reading research files before writing the plan — the plan must be grounded in research
  findings.

* NEVER use placeholder text like "TBD" or "to be determined" — resolve all unknowns or document
  them as risks.

* NEVER write a Step by Step section with unnamed files or vague actions.

* NEVER include steps for `results_summary.md`, `results_detailed.md`, `costs.json`,
  `suggestions.json`, or `compare_literature.md` in the Step by Step — these are
  orchestrator-managed steps in execute-task. The Step by Step must end at implementation work
  (compute metrics, produce charts).

* NEVER assume the implementation agent has read the research files — embed all critical context
  directly in the plan.

* NEVER omit a concrete requirement from the task text just because it feels minor or inconvenient —
  every explicit ask must appear in the checklist.

* NEVER write verification criteria without exact commands (e.g., "results look correct" is not
  testable; "run `uv run pytest code/ -v` and confirm 0 failures" is testable).
