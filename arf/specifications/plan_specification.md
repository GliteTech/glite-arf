# Plan Specification

**Version**: 5

* * *

## Purpose

This specification defines the format, structure, and quality requirements for the `plan/plan.md`
file produced during the planning task stage.

**Producer**: The planning subagent, which synthesizes research outputs into a concrete execution
plan with cost estimates, step-by-step actions, risk assessment, and verification criteria.

**Consumers**:

* **Implementation subagent** — follows the Step by Step section to execute the task. The
  implementation agent reads the plan fresh with no prior context — the plan must be fully
  self-contained.
* **Setup-machines subagent** — uses Remote Machines section to provision compute
* **Orchestrator** — uses the plan to determine which optional steps to include
* **Human reviewers** — evaluate whether the plan is realistic and complete
* **Verificator** — validates structure and minimum depth programmatically

## Self-Containment Principle

The plan must be a standalone document. The implementation agent that executes the plan has not read
the research files, does not know the task history, and cannot infer meaning from prior context.
Every assumption, term of art, file path, and design decision must be stated explicitly in the plan.
Do not write "as discussed in research" — state what was discussed. Do not reference "the standard
approach" — name the approach and its parameters.

## File Location

```text
tasks/<task_id>/plan/plan.md
```

## Format

The file is a Markdown document. New plans must include YAML frontmatter; plans created before this
specification may omit it (the verificator treats missing frontmatter as a warning, not an error,
for backwards compatibility).

## YAML Frontmatter

New plans must begin with a YAML frontmatter block containing the following fields:

```yaml
---
spec_version: "2"
task_id: "t0016_baseline_wsd_with_bert"
date_completed: "2026-04-01"
status: "complete"
---
```

| Field | Type | Description |
| --- | --- | --- |
| `spec_version` | string | Current version is `"2"`; `"1"` remains valid for legacy plans |
| `task_id` | string | Must exactly match the task folder name |
| `date_completed` | string | ISO 8601 date (YYYY-MM-DD) |
| `status` | string | `"complete"` or `"draft"` (see below) |

If `status` is `"draft"`, the Objective section must explain what remains to be decided.

## Mandatory Sections

The document must contain these eleven sections in this order, each as an `## ` heading. Additional
sections may be added wherever they would improve clarity (e.g., `## Architecture`, `## Data Flow`,
`## Alternative Approaches Considered`).

* * *

### `## Objective`

**Minimum**: 30 words

Restate the task objective and what the plan aims to accomplish. Must be self-contained — a reader
should not need to open `task.json` to understand the goal. Include success criteria: what does
"done" look like?

* * *

### `## Task Requirement Checklist`

**Minimum**: 60 words

Translate the task description into an explicit requirement checklist before any design or
implementation details. This section is the traceability bridge between `task.json` and the rest of
the plan.

It must:

* Quote the operative task request from `task.json` verbatim using a blockquote or fenced text
  block. Include the task name plus the concrete instructions from `short_description` and the
  resolved long description (`long_description` or the markdown file referenced by
  `long_description_file`).
* Extract **every concrete requirement** mentioned in the task text. Split distinct deliverables,
  questions, analysis dimensions, TODO items, constraints, and success conditions into separate
  checklist items.
* Assign stable IDs `REQ-1`, `REQ-2`, ... to the checklist items. Use these same IDs later in
  `## Step by Step`, implementation completion notes, and `results/results_detailed.md`.
* For each item, state which plan step(s) will satisfy it and what output or evidence will prove it
  is done.

If the task text contains something ambiguous, do not silently merge or discard it. Call out the
ambiguity explicitly and explain how the plan will handle it.

* * *

### `## Approach`

**Minimum**: 50 words

Describe the overall technical approach. Justify key design decisions by embedding the relevant
findings from research (do not just reference file names — state the findings). Mention which
existing libraries to import and which code to copy from prior tasks.

**Alternatives considered**: Briefly note at least one alternative approach and explain why it was
rejected. This prevents tunnel vision and preserves the decision rationale for future reference.
Even "no reasonable alternative exists because X" is acceptable.

**Task types**: State the recommended task type(s) from `meta/task_types/` that apply to this task.
If `task_types` in `task.json` was empty, recommend types here so the orchestrator or human can
update `task.json`. Explain how the type-specific Planning Guidelines influenced the approach.

* * *

### `## Cost Estimation`

**Minimum**: 20 words

Itemized cost estimate covering API calls, remote compute, and any other paid resources. `$0` is a
valid total but must be stated explicitly with reasoning (e.g., "all data is publicly available").
Compare against the project budget in `project/budget.json`.

* * *

### `## Step by Step`

**Minimum**: 100 words

Numbered, sequential steps for the implementation subagent to follow. Each step must specify:

* **What to do** — concrete action, not vague instruction
* **File names** — scripts to create (e.g., `code/extract.py`), assets to produce
* **Inputs and outputs** — what each step reads and writes
* **Libraries to import** — which registered libraries to use and their import paths
* **Code to copy** — which files from prior tasks to copy and what to adapt
* **Expected output** — what to observe when the step completes successfully
* **Requirement coverage** — which `REQ-*` item(s) from `## Task Requirement Checklist` this step
  satisfies

Steps must be specific enough that a different agent could execute them without ambiguity. Vague
steps like "implement the model" or "process the data" are not acceptable — name the files,
functions, and data paths. Each step must begin with `<integer>.` at the start of a line (the
verificator checks for this pattern).

#### Do:

```markdown
1. **Copy and adapt the data loader.** Copy
   `tasks/t0012_.../code/wsd_loader.py` to `code/loader.py`. Change
   the input path constant to read from `assets/dataset/raganato/`.
   Satisfies REQ-1.

2. **Run inference on validation split.** Execute `code/run_inference.py
   --split dev --limit 50` to verify the pipeline end-to-end before the
   full run. Expected: F1 > 60 (MFS baseline). Satisfies REQ-2.
```

#### Don't:

```markdown
**Step 1:** Copy the data loader from a prior task.

**Step 2:** Run inference on the validation split.
```

**Critical steps**: Mark steps that define the fundamental nature of the task with `[CRITICAL]` at
the start of the step description. These are the steps without which the task has not been done —
the task's identity. If a critical step becomes blocked, the implementation agent must create an
intervention file rather than silently substituting a different approach. Example: in a reproduction
task, the step that runs the model to produce fresh predictions is critical — evaluating
pre-existing predictions from another source is not a substitute.

**Milestones**: For complex tasks, group steps into milestones. Each milestone should be
independently verifiable — the agent can confirm it is done before proceeding to the next.

**Idempotence**: Steps should be safely re-runnable where possible. For risky or destructive steps,
include explicit recovery instructions.

**Validation gates**: Steps that involve expensive operations (paid API calls, remote compute,
large-scale data processing) must include explicit validation gates:

* The trivial baseline to compare against (with its numeric value)
* A `--limit` setting for the initial small-scale validation run
* A failure condition: "if result is at or below [baseline], halt and debug individual outputs"
* An individual-output inspection requirement

These gates prevent running expensive operations with a broken pipeline. The implementation agent
uses them during its preflight inspection phase.

The Step by Step covers implementation work only — ending at metric computation and chart
generation. Do not include steps for `results_summary.md`, `results_detailed.md`, `costs.json`,
`suggestions.json`, or `compare_literature.md` — these are orchestrator steps managed by
execute-task.

* * *

### `## Remote Machines`

**Minimum**: 10 words

Whether remote compute is needed. If yes, specify: GPU type, VRAM requirements, estimated runtime,
and provider preferences. Reference `arf/specifications/remote_machines_specification.md` for
machine lifecycle details. "None required" with a brief explanation is valid.

* * *

### `## Assets Needed`

**Minimum**: 10 words

Input assets this task depends on: datasets, libraries, papers, answers, external resources. For
each, state where it comes from (dependency task, external URL, project corpus).

* * *

### `## Expected Assets`

**Minimum**: 20 words

Output assets this task will produce: datasets, libraries, papers, answers, or other asset types.
For each, state: asset type, asset ID, and a brief description. Must match the `expected_assets`
field in `task.json`.

* * *

### `## Time Estimation`

**Minimum**: 10 words

Estimated wall-clock time for each major phase. Include: research (already done), implementation,
remote compute (if any), validation, and asset creation.

* * *

### `## Risks & Fallbacks`

**Minimum**: 30 words

A table with columns: Risk, Likelihood, Impact, Mitigation. Include at least 2 risks. Every plan has
risks — "no risks" is not acceptable.

**Pre-mortem technique**: Imagine the task has already failed. Work backwards from the failure to
identify what went wrong. This surfaces risks that forward-looking analysis misses. Teams using
pre-mortems identify 30% more potential problems.

Common failure modes: API rate limits, data format mismatches, download failures, model training
instability, budget overruns, missing dependencies, incorrect assumptions from research,
incompatible library versions.

Example format:

```markdown
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| API rate limiting | Low | Delays | Exponential backoff, retry logic |
| Dataset URL broken | Medium | Blocking | Mirror URL, contact authors |
```

* * *

### `## Verification Criteria`

**Minimum**: 30 words

Concrete, testable checks that confirm the task is complete. At least 3 bullet points. Each
criterion must include the **exact command to run** and the **expected output** or observable
behavior. "Results look correct" is not testable; "run `uv run pytest code/ -v` and confirm 0
failures" is testable.

Include: file existence checks, verificator commands with full paths, data integrity checks,
expected metric ranges where applicable, and at least one check that confirms the `REQ-*` coverage
is reflected in the produced outputs.

* * *

## Additional Sections

Beyond the mandatory sections, authors should add any sections that improve the plan. Common useful
additions include:

* `## Architecture` — system or data flow diagrams for complex tasks
* `## Alternative Approaches Considered` — what was rejected and why
* `## Data Flow` — input/output pipeline for data processing tasks
* `## Dependencies on Other Tasks` — detailed analysis of what prior tasks provide
* `## Budget Breakdown` — detailed cost analysis for expensive tasks

The verificator only checks for mandatory sections. Additional sections are encouraged.

## Quality Criteria

### What makes a good `plan.md`

* **Self-contained** — the implementation agent can execute it without reading any other file. All
  context, terms, and assumptions are stated explicitly.
* Objective is self-contained — no need to read task.json
* Task Requirement Checklist quotes the task text verbatim and decomposes every concrete requirement
  into a separate `REQ-*` item
* Approach embeds key research findings and notes alternatives considered
* Step by Step names every file, function, and data path with expected outputs and references the
  `REQ-*` items it satisfies
* Steps are grouped into milestones for complex tasks
* Cost estimation includes itemized breakdown, even if all items are $0
* Risks table uses pre-mortem thinking with realistic mitigations
* Verification criteria include exact commands, expected outputs, and direct checks for requirement
  completion
* Libraries to import and code to copy are explicitly listed with full paths

### What makes a bad `plan.md`

* Not self-contained — references "the research" without stating what it found
* Vague steps ("implement the model", "process the data")
* Missing file names in Step by Step
* Cost estimation says only "low cost" without numbers
* Risks section says "no significant risks"
* Verification criteria are vague ("results look correct")
* No connection to research findings — plan ignores what was learned
* No alternatives considered in Approach
* No traceability from the task text to the concrete implementation steps
* Too short — a plan that could have been a sentence

## Verificator Rules

The verificator produces errors (E) that block the pipeline, and warnings (W) that are logged but do
not halt execution.

### Errors

| Code | Check |
| --- | --- |
| `PL-E001` | File does not exist at `tasks/<task_id>/plan/plan.md` |
| `PL-E002` | YAML frontmatter present but not parseable |
| `PL-E003` | `task_id` in frontmatter does not match the task folder name |
| `PL-E004` | One or more mandatory sections is missing |
| `PL-E005` | Total content (excluding frontmatter) is fewer than 200 words |
| `PL-E006` | `## Step by Step` section has no numbered items (no `1.` pattern) |
| `PL-E007` | `spec_version` missing from frontmatter (when frontmatter present) |

The mandatory sections checked by `PL-E004` are: `## Objective`, `## Task Requirement Checklist`,
`## Approach`, `## Cost Estimation`, `## Step by Step`, `## Remote Machines`, `## Assets Needed`,
`## Expected Assets`, `## Time Estimation`, `## Risks & Fallbacks`, `## Verification Criteria`.

Legacy `spec_version: "1"` plans are validated against the older section set and may omit
`## Task Requirement Checklist`.

### Warnings

| Code | Check |
| --- | --- |
| `PL-W001` | A mandatory section is below its minimum word count |
| `PL-W002` | `## Risks & Fallbacks` contains no markdown table |
| `PL-W003` | YAML frontmatter is missing entirely (backwards compatibility) |
| `PL-W004` | `## Cost Estimation` does not mention a dollar amount (`$`) |
| `PL-W005` | `## Verification Criteria` has fewer than 3 bullet points |
| `PL-W006` | `## Task Requirement Checklist` contains no clear `REQ-*` checklist items |
| `PL-W007` | `## Step by Step` does not reference any `REQ-*` items |
| `PL-W008` | `## Step by Step` contains expensive operations but does not reference a baseline comparison or validation gate |
