# Compare Literature Specification

**Version**: 1

---

## Purpose

This specification defines the format, structure, and quality requirements for the
`results/compare_literature.md` file produced during the optional `compare-literature`
task step. The file documents how a task's quantitative results relate to published
results and prior work.

**Producer**: The `compare-literature` step skill.

**Consumers**:

* **Results subagents** — integrate comparison findings into `results_detailed.md`
* **Suggestion subagents** — identify gaps and follow-up experiments
* **Aggregator scripts** — collect comparisons across tasks
* **Human reviewers** — evaluate task outcomes relative to literature
* **Verificator scripts** — validate structure and completeness

---

## When to Produce This File

This file is **optional**. Produce it only when the task includes the `compare-literature`
step — i.e., when the task generates quantitative results comparable to published
work. Tasks that do not produce performance metrics (downloads, data processing,
infrastructure) skip this file entirely.

---

## File Location

```text
tasks/<task_id>/results/compare_literature.md
```

---

## YAML Frontmatter

Every `compare_literature.md` must begin with YAML frontmatter.

| Field           | Type   | Required | Description                          |
|-----------------|--------|----------|--------------------------------------|
| `spec_version`  | string | yes      | Specification version (`"1"`)        |
| `task_id`       | string | yes      | Task folder name                     |
| `date_compared` | string | yes      | ISO 8601 date (`YYYY-MM-DD`)         |

### Example

```yaml
---
spec_version: "1"
task_id: "t0019_mfs_baseline_raganato"
date_compared: "2026-04-01"
---
```

---

## Mandatory Sections

The file must contain these sections in this order, each as an `##` heading. Additional
sections may be added between them where useful.

| Section                       | Description                                           |
|-------------------------------|-------------------------------------------------------|
| `## Summary`                  | 2-4 sentences: what was compared, headline finding    |
| `## Comparison Table`         | Markdown table comparing results to published values  |
| `## Methodology Differences`  | Bullet list of key differences vs published methods   |
| `## Analysis`                 | Interpretation of gaps, agreements, surprising results|
| `## Limitations`              | Caveats, missing references, non-comparable conditions|

---

## Comparison Table Format

The `## Comparison Table` section must contain at least one markdown table with the
following columns:

| Column            | Description                                            |
|-------------------|--------------------------------------------------------|
| Method / Paper    | Name or citation key of the compared method            |
| Metric            | The evaluation metric (e.g., F1, accuracy)             |
| Published Value   | The value reported in the original paper               |
| Our Value         | The value measured in this task                        |
| Delta             | Our Value minus Published Value (positive = better)    |
| Notes             | Context: different test set, model size, etc.          |

### Rules

* Minimum **2 data rows** (excluding the header and separator rows)
* Every data row must have numeric values in Published Value and Our Value
* Delta must equal Our Value minus Published Value
* Use the Notes column to flag non-comparable conditions (e.g., "different training
  data", "few-shot vs zero-shot")

### Example

```markdown
| Method / Paper   | Metric | Published Value | Our Value | Delta  | Notes                |
|------------------|--------|-----------------|-----------|--------|----------------------|
| MFS (Raganato2017) | F1 ALL | 65.5          | 65.5      | +0.0   | Exact reproduction   |
| IMS+emb (Raganato2017) | F1 ALL | 71.3     | —         | —      | Not reproduced       |
| SANDWiCH (Bejgu2025) | F1 ALL | 89.0       | —         | —      | Current SOTA target  |
```

---

## Quality Criteria

* **Minimum word count**: 150 words total
* **Minimum comparison entries**: 2 data rows in the comparison table
* Every comparison entry should have specific numeric values — avoid vague qualifiers
  like "similar" or "comparable"
* Use `**bold**` for specific quantitative values in the Summary and Analysis sections
* Include citation keys (e.g., `Raganato2017`) when referencing published results

---

## Verification Rules

The verificator (`verify_compare_literature.py`) only runs when `compare_literature.md`
exists. Absence of the file is not an error since the `compare-literature` step is
optional.

### Errors

| Code      | Description                                              |
|-----------|----------------------------------------------------------|
| `CL-E001` | File exists but has no YAML frontmatter                  |
| `CL-E002` | Frontmatter missing required field (`spec_version`, `task_id`, or `date_compared`) |
| `CL-E003` | Missing mandatory section                                |
| `CL-E004` | `## Comparison Table` section has no markdown table       |
| `CL-E005` | Comparison table has fewer than 2 data rows               |

### Warnings

| Code      | Description                                              |
|-----------|----------------------------------------------------------|
| `CL-W001` | Total word count is under 150                            |
| `CL-W002` | Table data rows missing numeric values in Published Value or Our Value columns |
| `CL-W003` | No citation keys or paper references found in the document |

---

## Complete Example

```markdown
---
spec_version: "1"
task_id: "t0019_mfs_baseline_raganato"
date_compared: "2026-04-01"
---

# Comparison with Published Results

## Summary

Our MFS baseline implementation achieves **65.5 F1** on the Raganato ALL
concatenation, exactly matching the published MFS result from Raganato2017.
Per-dataset results match within **0.1 F1** for all five evaluation sets,
confirming faithful reproduction.

## Comparison Table

| Method / Paper           | Metric   | Published Value | Our Value | Delta | Notes              |
|--------------------------|----------|-----------------|-----------|-------|--------------------|
| MFS (Raganato2017)       | F1 ALL   | 65.5            | 65.5      | +0.0  | Exact match        |
| MFS (Raganato2017)       | F1 SE2   | 66.8            | 66.8      | +0.0  | Exact match        |
| MFS (Raganato2017)       | F1 SE3   | 66.2            | 66.2      | +0.0  | Exact match        |
| MFS (Raganato2017)       | F1 SE07  | 55.2            | 54.9      | -0.3  | Minor rounding     |
| MFS (Raganato2017)       | F1 SE13  | 63.0            | 63.0      | +0.0  | Exact match        |
| MFS (Raganato2017)       | F1 SE15  | 67.8            | 67.8      | +0.0  | Exact match        |

## Methodology Differences

* **Sense inventory**: Both use WordNet 3.0 synsets via the Raganato unified
  framework — no difference.
* **MFS source**: Both derive most-frequent-sense counts from SemCor 3.0 —
  no difference.
* **Evaluation scorer**: We use the unified Java scorer provided by
  Raganato2017 — same tool.
* **SE07 delta**: The -0.3 difference on SemEval-2007 likely stems from
  rounding in sense-count tie-breaking.

## Analysis

The reproduction is highly faithful. Five of six comparisons yield exact
matches. The only deviation is a **-0.3 F1** on SE07, the smallest dataset
(455 instances), where tie-breaking order in equally-frequent senses can
shift a handful of predictions. This is within expected variance for MFS
implementations.

The result confirms that our evaluation pipeline (data loading, sense
mapping, scoring) is correctly aligned with the Raganato framework and
can serve as a reliable baseline for subsequent experiments.

## Limitations

* Only the MFS baseline was compared — no supervised or knowledge-based
  systems were reproduced in this task.
* Per-POS breakdowns were not compared because Raganato2017 does not
  report MFS results stratified by part of speech.
* The SE07 discrepancy has not been root-caused beyond the tie-breaking
  hypothesis.
```
