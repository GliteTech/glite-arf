# Markdown Style Guide

This document defines formatting and structural rules for all `.md` files in the project.

* * *

## Quick Reference

### Frequently Ignored Rules

1. **Use Flowmark with width 100** — do NOT hand-wrap prose at 60-72 chars or manually chase exact
   column counts after the formatter has run.
2. **Use `*` for bullets, not `-`**
3. **Never skip heading levels** — don't jump from `##` to `####`
4. **Never split table cells across lines** — GitHub renders each `|...|` line as a separate row

* * *

## Line Length

**Target line length: 100 characters.**

Flowmark is the canonical formatter for repository markdown. Run it on edited markdown files instead
of manually reflowing paragraphs:

```bash
uv run flowmark --inplace --nobackup path/to/file.md
```

Flowmark wraps prose to a 100-character target while preserving markdown structure. Keep prose at or
under 100 characters in normal cases, but do not manually stretch or reflow Flowmark-formatted text
just to make every line land in the 80-100 range. Avoid hand-wrapping new prose at 60-72 characters.

### Exceptions

Lines may exceed 100 characters when breaking would reduce readability or break functionality:

* URLs and hyperlink destinations
* Markdown table rows that cannot be shortened
* Long file paths or long inline code spans
* YAML frontmatter values (e.g., long titles)
* Other cases where Flowmark keeps a line long to preserve markdown structure or readability

### Do:

```markdown
This specification defines the format, structure, and quality requirements for
the `research_papers.md` file produced during the "research in existing papers"
task stage.
```

### Don't (too long):

```markdown
This specification defines the format, structure, and quality requirements for the `research_papers.md` file produced during the "research in existing papers" task stage.
```

### Don't (manual narrow wrapping — run Flowmark instead):

```markdown
This specification defines the format,
structure, and quality requirements for
the `research_papers.md` file produced
during the "research in existing papers"
task stage.
```

* * *

## Bullet Points

Use `*` for unordered lists, not `-`.

### Do:

```markdown
* First item
* Second item
  * Nested item
```

### Don't:

```markdown
- First item
- Second item
  - Nested item
```

Use `1.`, `2.`, etc. for ordered lists when sequence matters.

* * *

## Bold and Emphasis

* Use `**bold**` for key terms, important values, and labels that should stand out
* Use `*italic*` sparingly, for titles of works or introducing defined terms
* Never use both (`***bold italic***`)

* * *

## Headings

* Use ATX-style headings (`#`, `##`, `###`)
* One `#` heading per file (the document title)
* Follow heading hierarchy — never skip levels (e.g., don't go from `##` to `####`)
* Leave one blank line before and after headings
* Keep heading text concise (under 70 characters)

### Do:

```markdown
# Document Title

## Major Section

### Subsection
```

### Don't:

```markdown
# Document Title
## Major Section
#### Skipped a level
```

* * *

## Section Separators

Use `---` on its own line to separate major sections. Leave one blank line before and after the
separator.

```markdown
Content of section one.

---

Content of section two.
```

* * *

## Blank Lines

* One blank line between paragraphs
* One blank line before and after headings
* One blank line before and after code blocks
* One blank line before and after lists
* No trailing blank lines at end of file (exactly one newline at EOF)
* No multiple consecutive blank lines

* * *

## Trailing Whitespace

No trailing spaces on any line. No spaces on empty lines.

* * *

## Code Blocks

* Use fenced code blocks with triple backticks
* Always specify the language for syntax highlighting
* Use inline code (`` ` ``) for file names, function names, variable names, and short code
  references

### Do:

````markdown
```python
def example() -> None:
    pass
```
````

### Don't:

````markdown
```
def example():
    pass
```
````

* * *

## Tables

* Use standard markdown table syntax
* Align columns for readability in source
* Use header separators (`|---|---|`)
* Keep cell content concise; use footnotes for long explanations
* **Never split a table cell across multiple lines** — each table row must be a single line. GitHub
  markdown does not support continuation rows; each `|...|` line renders as its own row, breaking
  the table layout. Let the line exceed 100 characters if needed (table rows are exempt from the
  line length limit).

### Do:

```markdown
| Field   | Type   | Description                                                  |
|---------|--------|--------------------------------------------------------------|
| `name`  | string | The display name                                             |
| `count` | int    | Number of occurrences across all datasets in the collection  |
```

### Don't:

```markdown
| Field   | Type   | Description                  |
|---------|--------|------------------------------|
| `count` | int    | Number of occurrences across |
|         |        | all datasets                 |
```

* * *

## Links and References

* Use inline links for single references: `[text](url)`
* Use reference-style links when the same URL appears multiple times:
  ```markdown
  See the [specification][spec] for details.

  [spec]: arf/specifications/example.md
  ```
* For internal project references, use relative paths

* * *

## YAML Frontmatter

When a markdown file uses YAML frontmatter:

* Delimit with `---` on its own line (opening and closing)
* Use lowercase keys with underscores
* Quote string values
* Use ISO 8601 dates (`YYYY-MM-DD`)

```markdown
---
task_id: "t0003_download_training_corpus"
status: "complete"
date_completed: "2026-03-28"
---
```

* * *

## File Structure Conventions

* A Markdown file without frontmatter starts with a `#` title heading
* A Markdown file with frontmatter places the `#` title heading immediately after the closing `---`
* End every file with exactly one trailing newline
* Keep files focused — one topic per file
* Use descriptive file names in `snake_case.md`

* * *

## Numbers and Data

* Bold specific quantitative results: **68.1 F1**, **p < 0.001**
* Use consistent number formatting throughout a document
* Include units where applicable

* * *

## Checklist

When writing or reviewing a `.md` file:

1. All lines under 100 characters (except allowed exceptions)
2. Markdown has been normalized with Flowmark at width 100
3. `*` used for bullet points (not `-`)
4. Heading hierarchy is correct (no skipped levels)
5. One `#` title per file
6. Code blocks have language specifiers
7. No trailing whitespace or spaces on empty lines
8. One trailing newline at end of file
9. Blank lines around headings, code blocks, and lists
10. Table rows are single lines (no multi-line cells)
