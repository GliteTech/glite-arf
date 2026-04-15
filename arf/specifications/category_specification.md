# Category Specification

**Version**: 1

* * *

## Purpose

This specification defines the folder structure and metadata format for categories in the project.
Categories are tags that can be assigned to papers, tasks, and other assets to enable filtering and
grouping across the project.

**Producer**: Human researchers or AI agents when a new research area or cross-cutting concern needs
to be tracked.

**Consumers**:

* **Paper assets** — reference category slugs in `details.json`
* **Aggregator scripts** — filter data by category
* **Verificator scripts** — validate that referenced categories exist
* **Human reviewers** — browse categories to understand project scope

* * *

## Category Folder Structure

Each category is a folder under `meta/categories/`:

```text
meta/categories/<category-slug>/
└── description.json    # Category metadata (required)
```

* * *

## Category Slug

The folder name serves as the category's canonical identifier (slug) throughout the project.

### Rules

1. Use lowercase letters, digits, and hyphens only
2. No underscores, spaces, or uppercase letters
3. Must start with a letter
4. Keep slugs concise: 1-3 words separated by hyphens
5. Use the slug consistently everywhere the category is referenced (e.g., in paper `details.json`
   `categories` arrays)

### Do:

```text
meta/categories/transformer-models/
meta/categories/supervised-wsd/
meta/categories/psychometrics/
```

### Don't:

```text
meta/categories/Supervised-WSD/         # Wrong: uppercase
meta/categories/supervised_wsd/         # Wrong: underscore
meta/categories/supervised wsd/         # Wrong: space
meta/categories/3d-models/              # Wrong: starts with digit
```

* * *

## description.json

The metadata file contains all structured information about the category. All field names use
`snake_case`.

### Fields

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `spec_version` | int | yes | Specification version (`1`) |
| `name` | string | yes | Human-friendly display name |
| `short_description` | string | yes | One-sentence summary of the category's scope |
| `detailed_description` | string | yes | One paragraph (2-5 sentences) elaborating on what the category covers, its boundaries, and representative examples |

### Field Details

#### `spec_version`

Integer version number of the specification this file conforms to. Current version is `1`. This
field enables future schema migrations.

#### `name`

A short, human-readable name for the category. Use title case. This name appears in reports,
aggregator outputs, and human-facing documentation.

#### `short_description`

A single sentence (no trailing period is acceptable but be consistent) that captures what this
category covers. Should be specific enough to distinguish this category from related ones.

#### `detailed_description`

A paragraph of 2-5 sentences providing additional context. Should explain:

* What types of work fall under this category
* How it differs from related categories
* Representative examples of papers, methods, or resources

### Example

```json
{
  "spec_version": 1,
  "name": "Transformer Models",
  "short_description": "Approaches based on transformer architectures including BERT, GPT, and T5 variants.",
  "detailed_description": "Covers work that uses or adapts transformer-based language models as the core component. This includes fine-tuning pre-trained models, feature extraction from frozen models, and transformer architecture modifications. Papers here focus on how transformers are applied to the research task rather than on the pre-training methodology itself (see pre-training, architecture-search for those)."
}
```

* * *

## Verification Rules

### Errors

Errors indicate structural problems that must be fixed.

| Code | Description |
| --- | --- |
| `CA-E001` | `description.json` is missing or not valid JSON |
| `CA-E002` | Required field missing in `description.json` |
| `CA-E003` | `spec_version` is not an integer |
| `CA-E004` | Category slug format is invalid (uppercase, underscores, spaces, or starts with a non-letter character) |

### Warnings

Warnings indicate quality concerns that should be addressed but do not block progress.

| Code | Description |
| --- | --- |
| `CA-W001` | `short_description` exceeds 200 characters |
| `CA-W002` | `detailed_description` is under 50 characters |
| `CA-W003` | `detailed_description` exceeds 1000 characters |
| `CA-W004` | `name` exceeds 50 characters |
