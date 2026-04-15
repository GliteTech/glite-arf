# Task Type Specification

**Version**: 2

* * *

## Purpose

This specification defines the folder structure, metadata format, and instruction file requirements
for task types in the project. Task types classify tasks by their nature (e.g., downloading a
dataset, training a model, running an experiment) and provide type-specific guidance for planning
and implementation skills.

**Producer**: Human researchers or AI agents when a new kind of task recurs often enough to warrant
standardized instructions.

**Consumers**:

* **Execute-task skill** — reads `optional_steps` to determine which steps to include or skip
* **Planning skill** — reads `instruction.md` Planning Guidelines to improve plans
* **Implementation skill** — reads `instruction.md` Implementation Guidelines
* **Generate-suggestions skill** — recommends task types for proposed tasks
* **Aggregator scripts** — collect task type data for skills and overview
* **Verificator scripts** — validate structure and completeness
* **Human reviewers** — browse task types to understand project workflows

* * *

## Task Type Folder Structure

Each task type is a folder under `meta/task_types/`:

```text
meta/task_types/<type-slug>/
├── description.json    # Structured metadata (required)
└── instruction.md      # Type-specific instructions for skills (required)
```

* * *

## Task Type Slug

The folder name serves as the task type's canonical identifier (slug) throughout the project.

### Rules

1. Use lowercase letters, digits, and hyphens only
2. No underscores, spaces, or uppercase letters
3. Must start with a letter
4. Keep slugs concise: 1-3 words separated by hyphens
5. Use the slug consistently everywhere the task type is referenced (e.g., in `task.json`
   `task_types` arrays)

### Do:

```text
meta/task_types/build-model/
meta/task_types/download-dataset/
meta/task_types/data-analysis/
```

### Don't:

```text
meta/task_types/Build-Model/          # Wrong: uppercase
meta/task_types/download_dataset/     # Wrong: underscore
meta/task_types/data analysis/        # Wrong: space
meta/task_types/3d-modeling/          # Wrong: starts with digit
```

* * *

## description.json

The metadata file contains all structured information about the task type. All field names use
`snake_case`.

### Fields

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `spec_version` | int | yes | Specification version (`2`) |
| `name` | string | yes | Human-friendly display name |
| `short_description` | string | yes | One-sentence summary of the task type's scope |
| `detailed_description` | string | yes | Paragraph covering scope, boundaries, and examples |
| `optional_steps` | list[string] | yes | Which optional steps apply to this task type (see below) |
| `has_external_costs` | bool | yes | Whether tasks of this type can incur paid external costs (GPU compute, LLM/API calls, paid services). Drives the Phase 1 budget gate in the execute-task orchestrator. |

### Field Details

#### `spec_version`

Integer version number of the specification this file conforms to. Current version is `2`.

#### `name`

A short, human-readable name for the task type. Use title case. This name appears in reports,
aggregator outputs, and human-facing documentation. Maximum 50 characters.

#### `short_description`

A single sentence that captures what this task type covers. Should be specific enough to distinguish
it from related types. Maximum 200 characters.

#### `detailed_description`

A paragraph of 2-5 sentences providing additional context. Should explain:

* What kinds of tasks fall under this type
* How it differs from related task types
* Representative examples of tasks

Minimum 50 characters, maximum 1000 characters.

#### `optional_steps`

A list of step IDs from the set of optional canonical steps that are applicable to this task type.
The 7 always-required steps (`create-branch`, `check-deps`, `init-folders`, `implementation`,
`results`, `suggestions`, `reporting`) are always included regardless of this field.

Valid values for this list:

* `research-papers` — review existing papers for methodology insights
* `research-internet` — search internet for tools, techniques, resources
* `research-code` — review code and assets from prior tasks
* `planning` — design approach, estimate costs, list assets
* `setup-machines` — provision remote compute
* `teardown` — destroy remote machines after implementation
* `creative-thinking` — out-of-the-box analysis and alternative approaches
* `compare-literature` — compare results against published baselines

An empty list `[]` means only the 7 always-required steps apply (no optional steps). The
execute-task orchestrator uses this field as guidance when determining which steps to include for a
task of this type.

This field is intentionally advisory rather than absolute. The orchestrator may include an optional
step that is not listed, or skip one that is listed, when the task content clearly warrants that
adjustment. This is especially important for task types such as `correction`: the default
`optional_steps` list may be empty for straightforward correction tasks, but a specific correction
request may still need `research-code`, `research-papers`, `research-internet`, or `planning`.

#### `has_external_costs`

A boolean flag declaring whether tasks of this type can incur paid external costs as part of their
normal execution. Paid external costs include GPU/CPU compute rented from cloud providers, paid LLM
API calls, paid search APIs, and any other third-party metered service.

The execute-task orchestrator reads this field to decide whether to run the Phase 1 budget gate for
a given task. When the task's `task_types` contain at least one entry with
`has_external_costs: true`, the orchestrator consults `aggregate_costs.py` and creates
`tasks/$TASK_ID/intervention/project_budget_exhausted.md` if the project has hit its stop threshold.
When every listed task type has `has_external_costs: false`, the budget gate is skipped entirely —
mechanical, analytical, or retrieval task types (downloading papers, running deduplication, writing
a library, brainstorming) have no way to spend project money and should not be blocked on it.

Set `true` when in doubt. The default posture of the framework is that unknown task types may spend
external money; marking a task type `false` is a declaration that its execution is cost-free by
construction.

### Example

```json
{
  "spec_version": 2,
  "name": "Data Analysis",
  "short_description": "Analyze data, compute statistics, and generate visualizations.",
  "detailed_description": "Analyzes existing data to compute metrics, charts, and summaries.",
  "optional_steps": [
    "research-papers",
    "research-code",
    "planning",
    "creative-thinking"
  ],
  "has_external_costs": false
}
```

* * *

## instruction.md

A markdown file containing type-specific instructions that planning and implementation skills read
to customize their behavior. This file has no YAML frontmatter.

### Mandatory Sections

The file must contain these sections as `##` headings:

#### `## Planning Guidelines`

Guidance for the planning skill when creating `plan/plan.md` for tasks of this type. Covers:

* What the plan's Approach section should focus on
* Which aspects of cost estimation are most relevant
* What kind of steps are typical
* Any type-specific plan sections to add

#### `## Implementation Guidelines`

Guidance for the implementation skill when executing tasks of this type. Covers:

* Typical execution flow
* Common patterns and best practices
* What to watch for during execution
* Asset creation patterns specific to this type

### Optional Sections

These sections are recommended but not required:

#### `## Common Pitfalls`

Numbered list of mistakes that commonly occur with this task type and how to avoid them.

#### `## Verification Additions`

Extra verification steps beyond the standard verificator runs that are specific to this task type.

#### `## Related Skills`

Which ARF skills (`arf/skills/`) are typically used for tasks of this type. Reference skills by
their slash-command name (e.g., `/add-paper`, `/download_paper`, `/research-internet`).

### Example

```markdown
# Download Dataset Instructions

## Planning Guidelines

* The plan should specify the exact download URL(s) and expected file sizes.
* Include SHA-256 checksums for integrity verification when available.
* Cost estimation is typically $0 (public datasets) — state this explicitly.
* Steps should cover: download, verify integrity, document structure, create
  dataset asset.

## Implementation Guidelines

* Use `wget` or `curl` wrapped in `run_with_logs.py` for downloads.
* Always verify downloaded file integrity (checksums, file size, format).
* Create the dataset asset following `meta/asset_types/dataset/specification.md`.
* Run the dataset verificator before completing.

## Common Pitfalls

1. Not checking if the download URL requires authentication or agreement to
   terms — create an intervention file if manual action is needed.
2. Not verifying file integrity after download — always check checksums.
3. Not documenting the dataset structure in `description.md`.

## Verification Additions

* Verify downloaded files exist and are non-empty.
* Run `uv run python -m arf.scripts.verificators.verify_dataset_asset`.

## Related Skills

* `/implementation` — main execution skill
```

* * *

## Verification Rules

### Errors

Errors indicate structural problems that must be fixed.

| Code | Description |
| --- | --- |
| `TY-E001` | `description.json` is missing or not valid JSON |
| `TY-E002` | Required field missing in `description.json` |
| `TY-E003` | `spec_version` is not an integer |
| `TY-E004` | Task type slug is invalid (uppercase, underscores, spaces, or bad first character) |
| `TY-E005` | `instruction.md` is missing |
| `TY-E006` | `instruction.md` is missing planning or implementation guidelines heading |
| `TY-E007` | A value in `optional_steps` is not a valid optional step ID |
| `TY-E008` | `has_external_costs` is present but is not a JSON boolean |

### Warnings

Warnings indicate quality concerns that should be addressed but do not block progress.

| Code | Description |
| --- | --- |
| `TY-W001` | `short_description` exceeds 200 characters |
| `TY-W002` | `detailed_description` is under 50 characters |
| `TY-W003` | `detailed_description` exceeds 1000 characters |
| `TY-W004` | `name` exceeds 50 characters |
| `TY-W005` | `instruction.md` is under 200 characters (too brief) |
