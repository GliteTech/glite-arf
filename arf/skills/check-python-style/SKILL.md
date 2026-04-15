---
name: "check-python-style"
description: "Check a Python file against the project Python style guide and report violations. Use after editing Python files or when reviewing code style."
---
# Check Python Style

**Version**: 1

## Goal

Check a Python file against the project's Python style guide and report violations in a way that
fixes underlying problems, not just surface style.

## Inputs

* `$ARGUMENTS` — path to the Python file to check (relative or absolute)

## Context

Read before starting:
* `arf/styleguide/python_styleguide.md` — the authoritative style guide

## Steps

1. Read `arf/styleguide/python_styleguide.md` to load all current rules.
2. Read the target Python file specified in `$ARGUMENTS`.
3. Analyze the file against every rule in the style guide.
4. For each rule, check whether it actually applies in this context and honor any exceptions
   documented in the style guide.
5. Treat each violation as a potential mistake, not just a formatting issue. Check whether it may
   hide a correctness, typing, validation, data integrity, resource cleanup, or maintainability
   problem.
6. Report findings as a numbered list of violations. For each violation:
   * State the rule being violated (reference the section name from the style guide).
   * Quote the offending line(s) with line numbers.
   * Briefly state why the rule matters here.
   * Show a corrected version that fixes the underlying problem, not just the surface.
   * If a local code rewrite would be incomplete, explicitly say what surrounding code, callers, or
     downstream consumers must also be checked.
7. If a rule is stylistic only in this case, keep the explanation brief and do not invent a deeper
   problem.
8. If the file has no violations, report "No style violations found."

## Output Format

Print results directly to the conversation. Use this structure:

```
## Style Check: <filename>

### Violations

1. **<Rule name>** (line <N>)
   - Found: `<offending code>`
   - Why this matters: `<brief risk or reason in this context>`
   - Fix: `<corrected code>`

2. ...

### Summary

<N> violation(s) found.
```

## Done When

* Every rule from the style guide has been checked against the file.
* All violations are listed with line numbers, offending code, why they matter, and fixes.
* A summary count is provided.

## Forbidden

* NEVER skip rules — check the file against the complete style guide.
* NEVER ignore rule-specific exceptions from the style guide.
* NEVER fabricate line numbers — read the actual file content.
* NEVER duplicate style guide content into this skill file.
* NEVER suggest a surface-only rewrite when the rule violation points to a deeper problem in types,
  validation, data meaning, callers, or cleanup logic.
* NEVER auto-fix the file unless explicitly asked by the user.
