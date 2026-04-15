---
name: "check-markdown-style"
description: "Check a Markdown file against the project markdown style guide and report violations. Use after editing `.md` files or when reviewing markdown quality."
---
# Check Markdown Style

**Version**: 3

## Goal

Check a markdown file against the project's markdown style guide and report violations, using
Flowmark-aligned formatting expectations.

## Inputs

* `$ARGUMENTS` — path to the markdown file to check (relative or absolute)

## Context

Read before starting:
* `arf/styleguide/markdown_styleguide.md` — the authoritative style guide

## Steps

1. Read `arf/styleguide/markdown_styleguide.md` to load all current rules.

2. Read the target markdown file specified in `$ARGUMENTS`.

3. **Line length check (highest priority):**

   **Too-long check**: Scan every line for length. Maximum is 100 characters in normal prose.
   Allowed exceptions are the same as in the style guide: URLs, markdown table rows, long file paths
   or inline code spans, YAML frontmatter values, and other cases where Flowmark-style wrapping
   would reasonably keep the line long to preserve markdown structure or readability.

   **Flowmark alignment rule**: Treat Flowmark output as the canonical formatting baseline. Do not
   report a violation merely because a paragraph line does not fully use the available width. Only
   flag line-length issues when the file clearly violates the style guide after accounting for the
   allowed exceptions above.

4. Check all other rules from the style guide:
   * Bullet style (`*` not `-`)
   * Heading hierarchy (no skipped levels, one `#` per file)
   * Blank lines around headings, code blocks, and lists
   * No trailing whitespace or spaces on empty lines
   * Code blocks have language specifiers
   * Bold/emphasis usage
   * One trailing newline at EOF
   * **No multi-line table cells** — every table row must be a single line. If a line starts with
     `|` followed by only whitespace before the next `|`, it is a continuation row and a violation.
     GitHub renders each `|...|` line as its own row, breaking table layout.

5. Report findings as a numbered list of violations. For each violation:
   * State the rule being violated (reference the section name from the style guide).
   * Quote the offending line(s) with line numbers.
   * Show a corrected version. When the issue is formatting, prefer a Flowmark-style fix rather than
     manual width chasing.

6. If the file has no violations, report "No style violations found."

## Line Length Examples

### Do (Flowmark-style wrapping at width 100):

```markdown
This specification defines the format, structure, and quality requirements for the
`research_papers.md` file produced during the "research in existing papers" task stage.
```

### Do (numbered list item wrapped cleanly):

```markdown
3. Cross-reference discovered papers against the existing corpus by comparing DOIs,
   normalized titles (lowercase, stripped punctuation), and author+year combinations.
```

### Don't (manual narrow wrapping — run Flowmark instead):

```markdown
This specification defines the format,
structure, and quality requirements for
the `research_papers.md` file produced
during the "research in existing papers"
task stage.
```

### Don't (too long — exceeds 100 chars without an exception):

```markdown
This specification defines the format, structure, and quality requirements for the `research_papers.md` file produced during the "research in existing papers" task stage.
```

## Output Format

Print results directly to the conversation. Use this structure:

```
## Style Check: <filename>

### Line Length Violations

1. **Too long** (line <N>): <X> chars
   * Found: `<offending line>`
   * Fix: wrap or restructure unless the line is an allowed exception

### Other Violations

1. **<Rule name>** (line <N>)
   * Found: `<offending content>`
   * Fix: `<corrected content>`

### Summary

<N> violation(s) found (<X> line-length, <Y> other).
```

## Done When

* Every line has been checked for line-length violations with Flowmark-aligned exceptions applied.
* Every rule from the style guide has been checked against the file.
* All violations are listed with line numbers, offending content, and fixes.
* A summary count is provided.

## Forbidden

* NEVER require manual reflow of already-acceptable Flowmark-formatted text just because a line does
  not fully use the available width.
* NEVER fabricate line numbers — read the actual file content.
* NEVER duplicate style guide content into this skill file.
* NEVER auto-fix the file unless explicitly asked by the user.
* NEVER treat fenced code blocks, YAML frontmatter, or markdown table rows as ordinary prose for
  line-length reporting.
