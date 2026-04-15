# Answer Asset Specification

**Version**: 2

* * *

## Purpose

This specification defines the folder structure, metadata format, and answer-document requirements
for answer assets in the project.

An answer asset represents one free-form question together with a concise answer and a fully
researched long-form answer. The asset is generic: the question may be answered through existing
papers, internet sources, prior project findings, new code experiments, or a combination of these
methods.

**Producer**: The implementation subagent of a task whose goal is answering one or more questions.

**Consumers**:

* **Planning and implementation subagents** — reuse prior answers instead of repeating the same
  research
* **Aggregator scripts** — combine answer metadata and summaries across tasks
* **Human reviewers** — browse direct answers and supporting evidence at checkpoints
* **Verificator scripts** — validate structure, completeness, and source traceability

Downstream task skills should consume answer assets in two passes:

1. Run `uv run python -m arf.scripts.aggregators.aggregate_answers --format json --detail short` to
   scan all questions and metadata without answer bodies.

2. Re-run the aggregator for only the relevant answer IDs:

   ```bash
   uv run python -m arf.scripts.aggregators.aggregate_answers \
     --format json --detail full --include-full-answer \
     --ids <answer_id_1> <answer_id_2>
   ```

   This reads the full researched answers for the selected IDs.

This question-first workflow keeps planning and implementation focused while preserving full answer
reuse when the task actually needs it.

* * *

## Asset Folder Structure

Answer assets are created **inside the task folder** that produces them. Each answer is stored in
its own subfolder under the task's `assets/answer/` directory:

````text
tasks/<task_id>/assets/answer/<answer_id>/
├── details.json       # Structured metadata (required)
├── short_answer.md    # Example canonical short answer document
└── full_answer.md     # Example canonical full answer document
````

The top-level `assets/answer/` directory is reserved for aggregated views produced by aggregator
scripts — tasks must never write directly to it.

The canonical answer document paths are stored in `details.json` `short_answer_path` and
`full_answer_path`. New v2 assets must declare these fields explicitly. Historical v1 assets may
omit them; in that case consumers fall back to `short_answer.md` and `full_answer.md`.

* * *

## Answer ID

The answer ID determines the folder name and serves as the canonical identifier throughout the
project.

### Rules

1. Lowercase alphanumeric characters and hyphens only.
2. Must match the regex: `^[a-z0-9]+(-[a-z0-9]+)*$`
3. Derive the slug from the question text. Remove punctuation, lowercase the words, and join them
   with hyphens.
4. Keep the slug concise but recognizable. Aim for 4-10 words where practical.

### Do:

```text
tasks/t0042_answer_remote_execution_tradeoffs/assets/answer/when-to-use-remote-machines/
tasks/t0042_answer_remote_execution_tradeoffs/assets/answer/how-to-verify-source-claims/
```

### Don't:

````text
assets/answer/when-to-use-remote-machines/  # Wrong: top-level, not in task folder
assets/answer/WhenToUseRemoteMachines/      # Wrong: uppercase
assets/answer/when_to_use_remote_machines/  # Wrong: underscores
assets/answer/when-to-use-remote-machines?/ # Wrong: punctuation
````

* * *

## details.json

The metadata file contains all structured information about the answer. All field names use
`snake_case`.

### Fields

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `spec_version` | string | yes | Specification version (e.g., `"1"`) |
| `answer_id` | string | yes | Folder name slug |
| `question` | string | yes | The full free-form question this asset answers |
| `short_title` | string | yes | Short display title for overview pages |
| `short_answer_path` | string | yes in v2, no in v1 | Canonical short answer path |
| `full_answer_path` | string | yes in v2, no in v1 | Canonical full answer path |
| `categories` | list[string] | yes | Category slugs from `meta/categories/` |
| `answer_methods` | list[string] | yes | Allowed methods; see rules below |
| `source_paper_ids` | list[string] | yes | Paper asset IDs used as evidence |
| `source_urls` | list[string] | yes | External URLs used as evidence |
| `source_task_ids` | list[string] | yes | Supporting task IDs |
| `confidence` | string | yes | One of: `"high"`, `"medium"`, `"low"` |
| `created_by_task` | string | yes | Task ID that created this answer |
| `date_created` | string | yes | ISO 8601 date when created |

### Rules

* At least one evidence reference must be present across `source_paper_ids`, `source_urls`, and
  `source_task_ids`.
* `answer_methods` must align with the evidence used in the canonical full answer document.
* `short_title` should be readable in overview listings and should not simply repeat the full
  question verbatim unless the question is already short.

### Example

```json
{
  "spec_version": "2",
  "answer_id": "when-to-use-remote-machines",
  "question": "When should a research task use remote machines instead of local execution?",
  "short_title": "When to use remote machines",
  "short_answer_path": "short_answer.md",
  "full_answer_path": "full_answer.md",
  "categories": [
    "evaluation"
  ],
  "answer_methods": [
    "internet",
    "code-experiment"
  ],
  "source_paper_ids": [],
  "source_urls": [
    "https://docs.vast.ai/",
    "https://docs.docker.com/engine/reference/commandline/stats/"
  ],
  "source_task_ids": [
    "t0013_test_remote_machine_system"
  ],
  "confidence": "medium",
  "created_by_task": "t0042_answer_remote_execution_tradeoffs",
  "date_created": "2026-04-02"
}
```

* * *

## Short Answer Document

A concise answer artifact that a human can read in under a minute. It must answer the question
directly, explain the reasoning briefly, and identify the evidence basis.

### YAML Frontmatter

````yaml
---
spec_version: "2"
answer_id: "when-to-use-remote-machines"
answered_by_task: "t0042_answer_remote_execution_tradeoffs"
date_answered: "2026-04-02"
---
````

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `spec_version` | string | yes | Specification version |
| `answer_id` | string | yes | Must match the folder name |
| `answered_by_task` | string | yes | Task ID that produced the answer |
| `date_answered` | string | yes | ISO 8601 date |

### Mandatory Sections

The short answer must contain these sections in this order, each as an `##` heading:

#### `## Question`

Repeat the exact question from `details.json`. The verificator normalizes whitespace before
comparing, so Flowmark line-wrapping of long questions is handled automatically.

#### `## Answer`

**Requirement**: 2-5 sentences total.

State the answer directly. The same short block must also explain why this answer is supported and
what kind of evidence it relies on.

**Style rules**:

* Write in a direct, clear, authoritative tone. No evasive language, filler, or diplomatic hedging.
* If the question is yes/no, begin the answer with "Yes", "No", or "The evidence is insufficient to
  answer definitively" — never with "maybe" or "it depends" unless factually required.
* Be decisive. State the conclusion first, then the supporting reason. Do not bury the answer inside
  qualifications.
* Professional and utilitarian. Every sentence must carry information; remove words that do not
  change the meaning.
* **NEVER** use inline citations such as `[AuthorYear]` or `[tNNNN]` in this section. References
  belong exclusively in the `## Sources` section.

#### `## Sources`

Bullet list of the specific paper IDs, task IDs, and/or URLs that support the answer.

### Example

```markdown
## Question

When should a research task use remote machines instead of local execution?

## Answer

Use remote machines when the task requires more compute, memory, or runtime isolation
than the local workstation can provide reliably. The tradeoff is justified when local
execution would be too slow, unstable, or would block other work for long periods.
This answer is based on remote-compute documentation and the project's prior machine
setup task.

## Sources

* Task: `t0013_test_remote_machine_system`
* URL: https://docs.vast.ai/
```

* * *

## Full Answer Document

A full researched answer written as a mini-paper. A reader should be able to understand the
question, the research process, the evidence base, the final synthesis, and the limitations without
opening any other file.

### YAML Frontmatter

````yaml
---
spec_version: "2"
answer_id: "when-to-use-remote-machines"
answered_by_task: "t0042_answer_remote_execution_tradeoffs"
date_answered: "2026-04-02"
confidence: "medium"
---
````

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `spec_version` | string | yes | Specification version |
| `answer_id` | string | yes | Must match the folder name |
| `answered_by_task` | string | yes | Task ID that produced the answer |
| `date_answered` | string | yes | ISO 8601 date |
| `confidence` | string | yes | Must match the confidence level in `details.json` |

### Mandatory Sections

The full answer must contain these sections in this order, each as an `##` heading:

#### `## Question`

Repeat the full question exactly. The verificator normalizes whitespace before comparing, so
Flowmark line-wrapping of long questions is handled automatically.

#### `## Short Answer`

Restate the concise answer in 2-5 sentences so the long document starts with the direct answer.

The same style rules from the short answer document `## Answer` section apply here: direct,
decisive, conclusion-first, no hedging, no inline citations. References belong in `## Sources`.

#### `## Research Process`

Describe how the answer was produced: what was searched, which assets were reviewed, what
experiments were run, and how conflicting evidence was handled.

#### `## Evidence from Papers`

Summarize evidence from paper assets. If the `papers` method was not used, state that explicitly in
one sentence.

#### `## Evidence from Internet Sources`

Summarize evidence from external URLs. If the `internet` method was not used, state that explicitly
in one sentence.

#### `## Evidence from Code or Experiments`

Summarize evidence from tasks, scripts, logs, or new experiments. If `code-experiment` was not used,
state that explicitly in one sentence.

#### `## Synthesis`

Integrate the evidence into a single answer. Resolve disagreements between sources, state
uncertainty, and explain why the conclusion follows from the evidence.

#### `## Limitations`

State what remains uncertain, what evidence was missing, and what would improve the answer.

#### `## Sources`

List every paper ID, task ID, and URL cited in the answer.

**Markdown reference links**: Include markdown reference link definitions at the end of this section
so that inline citations in the body sections render as clickable links when the file is viewed on
GitHub. Use citation keys in the prose (e.g., `[Raganato2017]`) and define link targets here:

```text
## Sources

* Paper: `10.18653_v1_E17-1010`
* Task: `t0019_mfs_baseline_raganato`

[Raganato2017]: <paper-summary-path>
[t0019]: ../../../t0019_mfs_baseline_raganato/
```

The relative path must resolve from the answer asset folder to the target. Paper citations link to
the paper asset's canonical summary document path. Historical papers may still use `summary.md`.
Task citations link to the task folder. External-only references link to the URL.

**Note**: Inline citations are allowed in the body sections of the full answer document (e.g.,
`## Evidence from Papers`, `## Synthesis`) but **NEVER** in the `## Short Answer` section. The
`## Short Answer` and `## Answer` sections in the canonical short answer document must remain
citation-free.

### Quality Criteria

* The document must be detailed enough to audit the research process.
* Links and identifiers must be specific enough for a reviewer to trace every source.
* The document should explain both the final answer and how that answer was reached.

* * *

## Verification Rules

### Errors

| Code | Description |
| --- | --- |
| `AA-E001` | `details.json` does not exist or is not valid JSON |
| `AA-E002` | A canonical answer document is missing |
| `AA-E003` | `answer_id` does not match the folder name |
| `AA-E004` | `answer_id` format is invalid |
| `AA-E005` | A required metadata field is missing |
| `AA-E006` | `answer_methods` contains an unknown value |
| `AA-E007` | `confidence` is not one of the allowed values |
| `AA-E008` | A referenced task ID does not exist |
| `AA-E009` | A referenced paper ID does not exist |
| `AA-E010` | A referenced URL is not a valid HTTP or HTTPS URL |
| `AA-E011` | The canonical short answer document is missing a mandatory section |
| `AA-E012` | The canonical full answer document is missing a mandatory section |
| `AA-E013` | `## Answer` in the canonical short answer document is not 2-5 sentences |
| `AA-E014` | No evidence references are provided in `details.json` |

### Warnings

| Code | Description |
| --- | --- |
| `AA-W001` | A category slug does not exist in `meta/categories/` |
| `AA-W002` | The question is suspiciously short |
| `AA-W003` | A required evidence section is present but too shallow |
| `AA-W004` | The full answer is very short for a research artifact |
