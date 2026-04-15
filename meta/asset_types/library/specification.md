# Library Asset Specification

**Version**: 2

* * *

## Purpose

This specification defines the folder structure, metadata format, and description requirements for
library assets in the project.

A library asset represents a reusable Python library produced by a task. The actual code lives in
`tasks/<task_id>/code/` (per project conventions); the library asset folder contains only metadata
and documentation.

**Producer**: The implementation subagent of a task that builds a library.

**Consumers**:

* **Downstream task subagents** — discover and import library code
* **Aggregator scripts** — combine library metadata across tasks
* **Human reviewers** — evaluate library quality at checkpoints
* **Verificator scripts** — validate structure and completeness

* * *

## Asset Folder Structure

Library assets are created **inside the task folder** that produces them. Each library is stored in
its own subfolder under the task's `assets/library/` directory:

````text
tasks/<task_id>/assets/library/<library_id>/
├── details.json       # Structured metadata (required)
└── description.md     # Example canonical description document
````

There is **no `files/` directory**. Library code lives in `tasks/<task_id>/code/` and is referenced
via `module_paths` in `details.json`. This avoids duplicating code between the asset folder and the
code directory.

The canonical documentation file path is stored in `details.json` `description_path`. New v2 assets
must declare this field explicitly. Historical v1 assets may omit it; in that case consumers fall
back to `description.md`.

* * *

## Library ID

The library ID determines the folder name and serves as the canonical identifier throughout the
project.

### Rules

1. Lowercase letters, digits, and underscores only.
2. Must start with a letter.
3. Must match the regex: `^[a-z][a-z0-9]*(_[a-z0-9]+)*$`
4. No leading or trailing underscores.
5. Use underscores for word separation (Python naming convention).

### Do:

```text
tasks/0012_build_wsd_loader/assets/library/wsd_data_loader/
tasks/0012_build_wsd_loader/assets/library/wsd_scorer/
tasks/0020_build_visualizer/assets/library/results_plotter/
```

### Don't:

````text
assets/library/wsd_data_loader/    # Wrong: top-level, not in task folder
assets/library/WsdDataLoader/      # Wrong: uppercase
assets/library/wsd-data-loader/    # Wrong: hyphens (not valid Python)
assets/library/_private_lib/       # Wrong: leading underscore
````

* * *

## details.json

The metadata file contains all structured information about the library. All field names use
`snake_case`.

### Fields

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `spec_version` | string | yes | Specification version (e.g., `"1"`) |
| `library_id` | string | yes | Folder name slug |
| `name` | string | yes | Display name (e.g., "WSD Data Loader") |
| `version` | string | yes | Version string (e.g., `"0.1.0"`) |
| `short_description` | string | yes | 1-2 sentence description |
| `description_path` | string | yes in v2, no in v1 | Canonical documentation file path relative to the asset root |
| `module_paths` | list[string] | yes | Paths to Python files relative to task root (e.g., `"code/wsd_loader.py"`) |
| `entry_points` | list[EntryPoint] | yes | Main callable functions, classes, or scripts |
| `dependencies` | list[string] | yes | Python package names required (may be `[]`) |
| `test_paths` | list[string] | no | Paths to test files relative to task root |
| `categories` | list[string] | yes | Category slugs from `meta/categories/` |
| `created_by_task` | string | yes | Task ID that created this library |
| `date_created` | string | yes | ISO 8601 date when created |

### EntryPoint Object

Each entry in the `entry_points` list describes a public API element.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `name` | string | yes | Function, class, or script name |
| `kind` | string | yes | One of: `"function"`, `"class"`, `"script"` |
| `module` | string | yes | Module path (e.g., `"code/wsd_loader.py"`) |
| `description` | string | yes | What this entry point does |

### Example

```json
{
  "spec_version": "2",
  "library_id": "wsd_data_loader",
  "name": "WSD Data Loader",
  "version": "0.1.0",
  "short_description": "Unified data loader for Raganato XML datasets, SemCor training data, and Maru 2022 subsets.",
  "description_path": "description.md",
  "module_paths": [
    "code/wsd_loader.py",
    "code/wsd_scorer.py",
    "code/constants.py",
    "code/paths.py"
  ],
  "entry_points": [
    {
      "name": "load_raganato_dataset",
      "kind": "function",
      "module": "code/wsd_loader.py",
      "description": "Parse a Raganato XML dataset into structured WSD instances."
    },
    {
      "name": "WsdScorer",
      "kind": "class",
      "module": "code/wsd_scorer.py",
      "description": "Compute micro-F1 per dataset, per POS, and overall."
    }
  ],
  "dependencies": [
    "lxml"
  ],
  "test_paths": [
    "code/test_wsd_loader.py",
    "code/test_wsd_scorer.py"
  ],
  "categories": [
    "library",
    "evaluation",
    "wsd"
  ],
  "created_by_task": "0012_build_wsd_data_loader_and_scorer",
  "date_created": "2026-04-02"
}
```

* * *

## Description Document

A detailed description of the library written after the code is complete. The canonical description
document is the file referenced by `details.json` `description_path`. Historical v1 assets may omit
that field; in that case the canonical document defaults to `description.md`.

The description must be thorough enough that a developer reading only this file understands the
library's purpose, API, and usage without reading the source code.

### YAML Frontmatter

````yaml
---
spec_version: "2"
library_id: "wsd_data_loader"
documented_by_task: "0012_build_wsd_data_loader_and_scorer"
date_documented: "2026-04-02"
---
````

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `spec_version` | string | yes | Specification version (e.g., `"1"`) |
| `library_id` | string | yes | Must match the folder name |
| `documented_by_task` | string | yes | Task ID that produced this description |
| `date_documented` | string | yes | ISO 8601 date |

### Mandatory Sections

The description must contain these sections in this order, each as an `##` heading. Additional
sections may be added between them where useful.

* * *

### `## Metadata`

Quick-reference block repeating key facts from `details.json`:

```markdown
## Metadata

* **Name**: WSD Data Loader
* **Version**: 0.1.0
* **Task**: `0012_build_wsd_data_loader_and_scorer`
* **Dependencies**: lxml
* **Modules**: `code/wsd_loader.py`, `code/wsd_scorer.py`
```

* * *

### `## Overview`

2-4 paragraphs describing what the library does, why it was built, and what problem it solves. This
section should go beyond the `short_description` in `details.json`.

**Minimum**: 80 words.

* * *

### `## API Reference`

Detailed description of the public API: functions, classes, their parameters, return types, and
behavior. Use code blocks for function signatures. Group by module when the library has multiple
files.

**Minimum**: 100 words.

* * *

### `## Usage Examples`

Concrete Python code examples showing how to import and use the library. At least one complete,
runnable example.

* * *

### `## Dependencies`

List of Python packages required beyond the standard library. For each dependency, briefly explain
why it is needed. State "No external dependencies" if the library uses only the standard library and
packages already in the project.

* * *

### `## Testing`

How to run the library's tests. Include the exact command and describe what the tests cover. If no
tests exist, state "No tests yet" and explain why.

* * *

### `## Main Ideas`

Bullet points of the most important design decisions and constraints relevant to users of this
library.

**Minimum**: 3 bullet points.

* * *

### `## Summary`

A synthesis in 2-3 paragraphs:

1. **What the library does** — scope, capabilities, and purpose
2. **How it fits the project** — which tasks and experiments use it
3. (Optional) **Limitations and future work** — known gaps, planned improvements

**Minimum**: 100 words total across the paragraphs.

* * *

### Quality Criteria

A good description:

* Is self-contained — a reader understands the library without reading source code
* Includes concrete function signatures and type annotations
* Provides runnable code examples
* Documents edge cases and error handling
* Identifies limitations and known issues

A bad description:

* Paraphrases only the short_description
* Uses vague language ("provides utilities", "handles data")
* Omits parameter types and return values
* Has no code examples
* Is under 400 words total

* * *

## Verification Rules

### Errors

Errors indicate structural problems that must be fixed.

| Code | Description |
| --- | --- |
| `LA-E001` | `details.json` is missing or not valid JSON |
| `LA-E002` | The canonical description document is missing |
| `LA-E004` | `library_id` in `details.json` does not match folder name |
| `LA-E005` | Required field missing in `details.json` |
| `LA-E006` | `module_paths` is empty (library must have at least one module) |
| `LA-E008` | A file in `module_paths` does not exist (resolved relative to task root) |
| `LA-E009` | The canonical description document is missing a mandatory section |
| `LA-E010` | `entry_points[].kind` is not one of the allowed values |
| `LA-E011` | Folder name does not match library ID format |
| `LA-E012` | The canonical description document is missing YAML frontmatter |
| `LA-E013` | `spec_version` is missing from `details.json` or the canonical description document frontmatter |
| `LA-E016` | An `entry_points` entry is missing required fields |

### Warnings

Warnings indicate quality concerns that should be addressed but do not block progress.

| Code | Description |
| --- | --- |
| `LA-W001` | The canonical description document total word count is under 400 |
| `LA-W003` | Main Ideas section has fewer than 3 bullet points |
| `LA-W004` | Summary section does not have 2-3 paragraphs |
| `LA-W005` | A category in `details.json` does not exist in `meta/categories/` |
| `LA-W008` | `short_description` is empty or under 10 words |
| `LA-W013` | Overview section word count is under 80 |
| `LA-W014` | No `test_paths` provided (testing is recommended) |
| `LA-W015` | A `test_paths` file does not exist |
| `LA-W016` | API Reference section word count is under 100 |
