# Project Description Specification

**Version**: 1

* * *

## Purpose

This specification defines the structure and content requirements for the project description file
(`project/description.md`). The project description provides project-level context — goals, scope,
research questions, and success criteria — that all skills and agents use to make informed
decisions.

**Producer**: Human researcher (via the `/create-project-description` skill or manually).

**Consumers**:

* **Task execution skills** — read project goals to align task work with project objectives
* **Research skills** — use scope to bound searches and goals to assess paper relevance
* **Suggestion generation** — use research questions and success criteria to prioritize follow-up
  tasks
* **Paper summarization** — connect paper findings to project goals in Main Ideas and Summary
  sections
* **Verificator scripts** — validate structure and completeness
* **Human reviewers** — understand project direction at a glance

* * *

## File Location

```text
project/
└── description.md    # Project description (required)
```

The `project/` directory lives at the repository root alongside `meta/`, `tasks/`, and `overview/`.
It may also hold additional input materials (existing data descriptions, code references, domain
context documents).

* * *

## Mandatory Sections

The file must contain these sections in this order. Each section is an `##` heading except the title
which is `#`. Additional sections may be added between them where useful.

* * *

### `# <Project Title>`

The document title. Exactly one `#` heading per file. Keep under 70 characters.

* * *

### `## Goal`

2-5 sentences describing the overarching research objective. This is the "north star" that every
task should contribute to. Be specific about what the project aims to achieve and why.

**Minimum**: 30 words.

* * *

### `## Scope`

Must contain two subsections:

#### `### In Scope`

Bulleted list of what the project covers — methods, languages, domains, datasets, evaluation
approaches. At least 3 items.

#### `### Out of Scope`

Bulleted list of what is explicitly excluded, so agents do not pursue tangents. At least 2 items.

* * *

### `## Research Questions`

Numbered list of specific, testable research questions the project aims to answer. These guide
suggestion generation and paper relevance assessment.

**Minimum**: 3 questions. **Maximum**: 7 questions.

* * *

### `## Success Criteria`

Bulleted list of concrete, measurable criteria for when the project has achieved its goals. Each
criterion should be verifiable — not vague aspirations.

**Minimum**: 3 criteria.

#### Do:

```markdown
* Reproduce SOTA WSD results on the Raganato2017 benchmark within
  2 F1 points
* Evaluate at least 3 different architectures on SemCor
* Publish comparison of LLM-based vs. fine-tuned approaches with
  statistical significance tests
```

#### Don't:

```markdown
* Get good results
* Try several approaches
* Write a paper
```

* * *

### `## Key References`

Bulleted list of the most important papers, datasets, and benchmarks that anchor the project. Use
citation keys matching the paper corpus where available. This is not a full bibliography — just the
essential starting points.

**Minimum**: 3 references.

* * *

### `## Current Phase`

1-3 sentences describing where the project is now and what comes next. Update this section at each
project checkpoint.

**Minimum**: 15 words.

* * *

## Verification Rules

### Errors

| Code | Description |
| --- | --- |
| `PD-E001` | `project/description.md` does not exist |
| `PD-E002` | Missing mandatory section (`##` heading) |
| `PD-E003` | No `#` heading or multiple `#` headings |
| `PD-E004` | Scope section missing `### In Scope` or `### Out of Scope` subsection |

### Warnings

| Code | Description |
| --- | --- |
| `PD-W001` | Goal section under 30 words |
| `PD-W002` | Research Questions has fewer than 3 numbered items |
| `PD-W003` | Research Questions has more than 7 numbered items |
| `PD-W004` | Success Criteria has fewer than 3 bullet items |
| `PD-W005` | Key References has fewer than 3 bullet items |
| `PD-W006` | Current Phase under 15 words |
