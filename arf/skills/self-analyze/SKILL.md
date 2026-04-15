---
name: "self-analyze"
description: "Analyze a completed Claude Code or Codex session (task execution, brainstorm, project-description, or any other skill invocation) and identify self-corrected mistakes, uncorrected mistakes that affected the result, and human interventions, then propose concrete ARF framework improvements. Prints findings to the chat; does not save reports."
---
# Self-Analyze

**Version**: 2

## Goal

Review the session logs of a recently completed Claude Code or Codex session, categorize every
mistake and human intervention that occurred, and propose concrete improvements to ARF framework
files so the same mistakes do not recur.

## Inputs

* `$ARGUMENTS` — optional target identifier. Accepted forms:
  * A task id such as `t0006_search_learning_analytics` — analyze that task's end-to-end execution.
  * A skill name such as `human-brainstorm`, `create-project-description`, or `execute-task` —
    analyze the most recent session that invoked that skill.
  * The literal string `current`, or empty `$ARGUMENTS` — analyze the live session the skill is
    currently running inside.

## Context

Read before starting:

* `arf/README.md` — framework principles and glossary.
* `arf/styleguide/agent_instructions_styleguide.md` — how skills, verificators, aggregators, and
  specifications are structured. Proposals must point at the right kind of file.
* `arf/specifications/logs_specification.md` — the authoritative schema for `logs/steps/`,
  `logs/commands/`, `logs/sessions/`, and `logs/searches/`.
* `arf/specifications/corrections_specification.md` — how downstream tasks correct upstream
  mistakes. A later correction file is hard evidence that an earlier session shipped a mistake.
* `arf/docs/reference/aggregators.md` — the full aggregator list. Use this when proposing "add an
  aggregator" or "add a flag to an aggregator".
* `arf/scripts/utils/capture_task_sessions.py` — the canonical module for session-log discovery. The
  public CLI (Step 1) covers all three target kinds uniformly; you do not need to re-derive
  `_cwd_to_encoded_path` or hand-walk `~/.claude/projects/` or `~/.codex/sessions/`.
* When `$ARGUMENTS` is a skill name, also read the target skill's own
  `arf/skills/<skill-name>/SKILL.md` so proposals can point at the exact step that failed.

## Steps

### Step 1: Resolve the target to concrete evidence files

Pick one branch based on `$ARGUMENTS` and call the canonical session-discovery CLI:

1. **Task id** — capture the full set of session transcripts into the task folder, then read from
   there:

   ```bash
   uv run python -m arf.scripts.utils.capture_task_sessions \
     --task-id <task_id>
   ```

   After it completes, the primary evidence files are:
   * `tasks/<task_id>/logs/sessions/*.jsonl` and the generated `capture_report.json`
   * `tasks/<task_id>/logs/steps/<NNN>_<step>/step_log.md` for every step
   * `tasks/<task_id>/logs/commands/*.json` — exit codes and stderr for every wrapped CLI call
   * `tasks/<task_id>/intervention/*.md` — hard human intervention points
   * `tasks/<task_id>/corrections/*.json` — corrections applied by this task
   * `tasks/<task_id>/task.json` — `expected_assets` for declared-vs-actual comparison
   * `tasks/<task_id>/results/results_summary.md` and `results/results_detailed.md`

   Also run once, to see downstream corrections applied to this task by later tasks:

   ```bash
   uv run python -u -m arf.scripts.aggregators.aggregate_tasks \
     --ids <task_id> --detail full --format json
   ```

2. **Skill name** — resolve the most recent transcript that invoked that skill. The CLI prints the
   matched jsonl paths to stdout; does not copy files:

   ```bash
   uv run python -m arf.scripts.utils.capture_task_sessions \
     --skill <skill-slug>
   ```

   The CLI content-matches each candidate transcript against both the bare slug and the
   `arf/skills/<slug>/SKILL.md` path, walks the Claude Code project directory for this repo plus
   `~/.codex/sessions/`, and returns the newest matching file (plus any co-located subagent
   transcripts). Read every returned jsonl as the evidence set.

3. **`current` or empty** — resolve the live session:

   ```bash
   uv run python -m arf.scripts.utils.capture_task_sessions --current
   ```

   The CLI uses `CODEX_THREAD_ID` when set and falls back to the newest Claude transcript mtime for
   this repo, returning the main transcript plus co-located subagent transcripts.

### Step 2: Collect evidence

Read every resolved file. Session transcripts are the primary evidence — they show the full sequence
of tool calls, errors, retries, rollbacks, and user-visible messages. For task targets, supplement
with the step logs, command logs, interventions, corrections, results, and `task.json`. When a PR
exists for the target, run:

```bash
gh pr view <pr_number> --comments
```

and include review comments as evidence.

### Step 3: Categorize findings into three buckets

Every mistake or friction point must land in exactly one bucket:

* **A. Self-corrected mistakes** — the agent made a mistake, detected it (via verificator, error, or
  rethink), and fixed it within the session. The end result is correct but time was wasted.
* **B. Uncorrected mistakes that affected the result** — a mistake that shipped or that the session
  ended on. Signals include: downstream corrections applied by a later task, verificator warnings
  left unresolved, declared `expected_assets` not matching produced assets, PR review comments
  pointing at real defects, incomplete results sections. This is the critical bucket.
* **C. Human interventions** — a point where a human had to correct the agent, unblock it, supply
  missing information, or override a decision. Signals include `intervention/*.md` files, user
  messages in the transcript that correct or redirect the agent, and session log passages where the
  agent explicitly asks for help.

### Step 4: Root-cause each finding

Trace each finding to a specific ARF file — or to the absence of one. Typical root causes:

* A skill step was ambiguous or missing a precondition.
* A verificator runs too late, too early, or not at all.
* An aggregator flag is missing, so the agent hand-walked `tasks/`.
* A hook in `settings.json` was not configured to block the bad action.
* A specification under `arf/specifications/` is silent on the edge case.
* A style guide rule exists but was not surfaced near the relevant skill.

If the root cause is genuinely outside the framework (researcher changed their mind, upstream data
was wrong, model limitation), record it under `## Not a framework problem` instead.

### Step 5: Draft concrete improvement proposals

Every proposal must name a specific target file path and describe the exact change. Reject vague
proposals like "improve the execute-task skill". Valid change kinds:

* **Edit**: add a step, add a forbidden rule, tighten wording in an existing file.
* **New file**: a new skill, new specification, new style guide rule file.
* **New verificator rule**: add an error or warning code to an existing verificator under
  `arf/scripts/verificators/`.
* **New or extended aggregator**: add a flag, add an aggregator, or extend the corrections overlay.
* **Hook**: add or change an entry in `.claude/settings.json` to block or require an action
  automatically.

### Step 6: Print the analysis to the chat

Format the full analysis using the `## Output Format` schema below and print it directly into the
conversation. Do not write any file. Do not create a report folder. The only allowed side effect is
the `logs/sessions/` population performed by `capture_task_sessions --task-id` in Step 1 when the
target is a task. The `--skill` and `--current` CLI modes are read-only and copy nothing.

## Output Format

Print these sections in this order, as markdown, directly in the chat:

* `## Target` — what was analyzed, with the resolved evidence file paths.
* `## Evidence Sources` — bullet list of every file read (path only; no line counts required).
* `## Findings`
  * `### A. Self-corrected mistakes` — bullets. Each bullet cites at least one evidence path and
    names a root cause. Write "None detected" if the bucket is empty.
  * `### B. Uncorrected mistakes that affected the result` — same format. Write "No material impact
    on the end result was detected" if the bucket is empty. Never silently omit this bucket.
  * `### C. Human interventions` — same format. Write "None detected" if empty.
* `## Root Causes` — grouped by ARF file or missing-file.
* `## Proposals` — numbered list. Each item has: **File**, **Change kind**, **Concrete change**,
  **Expected benefit**, **Risk**.
* `## Not a framework problem` — issues that were genuine research or researcher decisions, not
  framework flaws.

## Done When

* The target has been resolved to a concrete set of evidence files and every file has been read.
* All three buckets (A, B, C) are addressed in the chat output, even when empty.
* Every finding cites at least one real evidence path.
* Every proposal names a concrete target file and a concrete change kind.
* Nothing has been written to disk except the `tasks/<id>/logs/sessions/` population performed by
  `capture_task_sessions --task-id` when the target is a task.

## Forbidden

* NEVER save the analysis, findings, or proposals to a file on disk. The output is the chat reply.
* NEVER hand-walk `~/.claude/projects/` or `~/.codex/sessions/` or re-derive the cwd encoding rule
  (`/` → `-`). Always use the `capture_task_sessions` CLI (`--task-id`, `--skill`, or `--current`) —
  that module is the single source of truth for session-log discovery.
* NEVER fabricate evidence — every finding must cite a real log line, transcript span, or file path
  the agent actually read.
* NEVER auto-apply proposals; the researcher decides which to implement.
* NEVER propose project-specific (domain, dataset, experiment) changes. The skill is
  framework-generic; proposals target `arf/`, `meta/`, or top-level config only.
* NEVER create a `tasks/tXXXX_*` folder for the self-analyze invocation itself.
