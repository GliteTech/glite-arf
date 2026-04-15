# Research Code Specification

**Version**: 1

---

## Purpose

This specification defines the format, structure, and quality requirements for `research_code.md`.
It is produced during the "research previous tasks" stage.

**Producer**: The research-code subagent, which reviews libraries, code, datasets, answers, and
findings from completed tasks.

**Consumers**:

* **Planning subagent** — uses findings to inform the task plan, decide which libraries to import
  and which code to copy
* **Implementation subagent** — uses the Reusable Code and Assets section to locate existing code
  and avoid reinventing solutions
* **Human reviewers** — evaluate whether prior work was leveraged
* **Verificator** — validates structure, cross-references, and minimum depth programmatically

## Relationship to Other Research Files

This file is produced **after** `research_papers.md` and `research_internet.md`. Its purpose is to
survey the project's own codebase — libraries, task implementations, datasets, answer assets, and
lessons learned — so that the planning and implementation stages can reuse existing work.

When aggregators expose an asset type, they expose the **effective** corrected state, not just the
raw files in the original task folder. Code research should therefore prefer aggregator output when
discovering libraries, answers, datasets, models, predictions, and papers that may already have
correction overlays.

## Cross-Task Code Reuse Rule

Tasks **MUST NOT** import from other tasks' `code/` directories. The only cross-task import
mechanism is libraries (registered in `assets/library/`). Non-library code from other tasks must be
**copied** into the current task's `code/` directory. This section must explicitly label each
reusable piece as either "import via library" or "copy into task".

## File Location

```text
tasks/<task_id>/research/research_code.md
```

## Format

The file is a Markdown document with YAML frontmatter. All content is UTF-8 encoded.

## YAML Frontmatter

The file must begin with a YAML frontmatter block containing the following required fields:

```yaml
---
spec_version: "1"
task_id: "t0016_baseline_wsd_with_bert"
research_stage: "code"
tasks_reviewed: 8
tasks_cited: 5
libraries_found: 2
libraries_relevant: 1
date_completed: "2026-04-01"
status: "complete"
---
```

| Field | Type | Description |
| --- | --- | --- |
| `spec_version` | string | Always `"1"` for this version |
| `task_id` | string | Must exactly match the task folder name |
| `research_stage` | string | Always `"code"` for this file |
| `tasks_reviewed` | int | Total tasks examined (including those not cited) |
| `tasks_cited` | int | Tasks referenced in body and listed in Task Index |
| `libraries_found` | int | Total libraries discovered via the aggregator |
| `libraries_relevant` | int | Libraries deemed relevant to this task |
| `date_completed` | string | ISO 8601 date (YYYY-MM-DD) |
| `status` | string | `"complete"` or `"partial"` (see below) |

If `status` is `"partial"`, the Task Objective section must explain why (e.g., no prior tasks exist
yet in the project).

## Mandatory Sections

The document must contain at least these seven sections in this order, each as an `## ` heading. The
mandatory sections define the minimum structure — authors are encouraged to add additional `## `
sections wherever they would improve clarity (e.g., `## Dataset Landscape`, `## Common Patterns`,
`## Architecture Overview`). Task-specific and project-specific sections are expected; the research
should be as thorough and detailed as the topic demands.

---

### `## Task Objective`

**Minimum**: 30 words

Restate what this task aims to accomplish. Paraphrase or quote from `task.json` and, when present,
the markdown file referenced by `long_description_file`. The purpose is to make this file
self-contained — a reader should not need to open another file to understand why prior code is being
reviewed.

---

### `## Library Landscape`

**Minimum**: 50 words

Document all libraries discovered via the library aggregator. For each library, state:

* Library ID, name, version, and which task created it
* Whether the aggregator output reflects a correction or replacement
* Whether it is relevant to the current task and why
* Import path for relevant libraries

This section makes the library survey auditable — humans can verify that all available libraries
were considered.

---

### `## Key Findings`

**Minimum**: 200 words

The core of the document. Findings must be organized **by topic, not by task**. Each topic is a
`### ` subsection.

This is critical: by-topic organization forces synthesis across tasks. Per-task summaries produce
low-value dumps. The goal is to extract cross-cutting themes about code patterns, what worked, what
failed, and reusable components.

Requirements:

* At least one `### ` subsection
* Every factual claim must cite the source task using `[tXXXX]` notation (e.g., `[t0012]`)
* Each subsection should reference multiple tasks where possible
* Identify what approaches worked well and what did not
* Note code quality patterns — clean implementations vs. workarounds
* Include **specific details** — file paths, function signatures, line counts, performance numbers,
  error rates

---

### `## Reusable Code and Assets`

**Minimum**: 100 words

Specific files, functions, classes, datasets, and utilities that can be reused for the current task.
This is the actionable section — the implementation subagent reads this to know what already exists.

For each reusable item, include:

* **Source**: task ID and file path (e.g., `tasks/t0012_.../code/wsd_loader.py`)
* **What it does**: brief description of functionality
* **Reuse method**: either "**import via library**" (for registered libraries) or "**copy into
  task**" (for non-library code)
* **Function signatures**: key public functions with parameter types and return types
* **Adaptation needed**: what modifications are required, if any
* **Line count**: approximate size of the code to copy

**Cross-task import rule**: Only libraries registered in `assets/library/` may be imported across
tasks. All other code must be copied. This section must explicitly label each item.

---

### `## Lessons Learned`

**Minimum**: 50 words

What worked well and what did not work in prior tasks. This section draws from results files
(`results_summary.md`, `results_detailed.md`) and plans (`plan/plan.md`) of relevant tasks.

Include:

* Successful approaches and why they worked
* Failed approaches, error patterns, and debugging insights
* Performance observations (speed, memory, accuracy)
* Pitfalls to avoid
* Unexpected findings or edge cases discovered

---

### `## Recommendations for This Task`

**Minimum**: 50 words

Concrete, prioritized recommendations derived from the code research. These should directly inform
the planning and implementation stages. Each recommendation should be traceable to findings above.

Focus on:

* Which libraries to import and how
* Which code to copy and what to adapt
* Which approaches to adopt based on prior successes
* Which approaches to avoid based on prior failures
* Any gaps in existing code that require new implementation

---

### `## Task Index`

A structured reference list of all tasks cited in the document. The number of entries must equal
`tasks_cited` in the frontmatter.

Each entry uses the short task reference as a `### ` heading (e.g., `### [t0012]`) and contains
these required fields:

| Field | Required | Description |
| --- | --- | --- |
| Task ID | yes | Full task folder name (e.g., `t0012_build_wsd_data_loader_and_scorer`) |
| Name | yes | Task display name from `task.json` |
| Status | yes | Current task status |
| Relevance | yes | 1-2 sentences on why this task matters for the current task |

## Additional Sections

Beyond the mandatory sections above, authors should add any sections that help communicate the
research thoroughly. Common useful additions include:

* `## Dataset Landscape` — datasets produced by prior tasks, their locations, formats, and sizes
* `## Common Patterns` — recurring code patterns across tasks (path management, data loading,
  evaluation)
* `## Architecture Overview` — how existing libraries and code modules fit together
* `## Test Coverage` — what tests exist for reusable code, how to run them
* Any other task-specific section the author deems valuable

The verificator only checks for mandatory sections. Additional sections are never penalized and are
strongly encouraged.

## Citation Format

Use `[tXXXX]` for inline task references (e.g., `[t0012]`, `[t0015]`). The reference uses the short
task ID prefix (letter `t` + 4-digit number), not the full folder name.

Rules:

* Every `[tXXXX]` in the body must have a matching `### [tXXXX]` entry in the Task Index
* Every Task Index entry should be cited at least once in the body (unused entries indicate padding)

## Quality Criteria

### What makes a good `research_code.md`

* Library Landscape documents all discovered libraries with relevance assessment
* Key Findings are synthesized themes that compare across tasks, not per-task summaries
* Reusable Code section includes specific file paths, function signatures, and line counts
* Each reusable item is explicitly labeled as "import via library" or "copy into task"
* Lessons Learned contains specific, actionable insights from results and plans
* The document is detailed enough that the implementation subagent can locate and use existing code
  without additional research
* Additional sections are added wherever the task demands deeper treatment

### What makes a bad `research_code.md`

* Sequential task summaries presented as Key Findings (no synthesis)
* Vague Reusable Code ("there is useful code in t0012")
* Missing file paths, function signatures, or line counts
* No distinction between library imports and code copying
* Lessons Learned is empty or says "no issues found"
* Too short — a code research document that could have been an email
* No additional sections even when the task clearly warrants them

## Verificator Rules

The verificator produces errors (E) that block the pipeline, and warnings (W) that are logged but do
not halt execution. Agents should have VERY serious reasons to continue if there are errors.

### Errors

| Code | Check |
| --- | --- |
| `RC-E001` | File does not exist at `tasks/<task_id>/research/research_code.md` |
| `RC-E002` | YAML frontmatter is missing or not parseable |
| `RC-E003` | `task_id` in frontmatter does not match the task folder name |
| `RC-E004` | One or more mandatory sections is missing (see list below) |
| `RC-E005` | `tasks_cited` < 1 and `status` is not `"partial"` |
| `RC-E006` | An inline `[tXXXX]` has no matching entry in Task Index |
| `RC-E007` | Task Index entry is missing the Task ID field |
| `RC-E008` | `spec_version` is missing from frontmatter |
| `RC-E009` | Total content (excluding frontmatter) is fewer than 300 words |

The mandatory sections checked by `RC-E004` are: `## Task Objective`, `## Library Landscape`,
`## Key Findings`, `## Reusable Code and Assets`, `## Lessons Learned`,
`## Recommendations for This Task`, `## Task Index`.

### Warnings

| Code | Check |
| --- | --- |
| `RC-W001` | A mandatory section is below its minimum word count |
| `RC-W002` | A task ID in the Task Index does not match an existing task folder |
| `RC-W003` | `## Key Findings` section contains no `### ` subsections |
| `RC-W004` | A Task Index entry is never cited in the body text |
| `RC-W005` | `tasks_reviewed` < `tasks_cited` (likely a frontmatter error) |
