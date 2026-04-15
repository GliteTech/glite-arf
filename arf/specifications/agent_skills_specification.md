# Agent Skills Specification

**Version**: 1

---

## Purpose

This specification defines the shared format and discovery layout for ARF skills. It ensures
that a single authored skill works in both Claude Code and Codex without duplicating content.

**Producer**: Human maintainers editing ARF skills.

**Consumers**:

* **Claude Code** — discovers skills through `.claude/skills/`
* **Codex** — discovers skills through `.codex/skills/`
* **Style guides and checker skills** — reference this specification when validating skills

---

## Canonical Location

ARF skills are authored once under:

```text
arf/skills/<skill_name>/SKILL.md
```

`<skill_name>` is the stable skill slug and directory name. Use lowercase letters, digits, and
hyphens. Do not create separate authored copies for Claude Code and Codex.

---

## Discovery Layout

Both tool-specific discovery directories must point at the canonical skill directory:

```text
.claude/skills/<skill_name> -> ../../arf/skills/<skill_name>
.codex/skills/<skill_name>  -> ../../arf/skills/<skill_name>
```

Each symlink target must resolve to a directory containing `SKILL.md`.

This repository does not treat `.claude/skills/` as the authored source of truth. It is a
discovery layer for Claude Code, just as `.codex/skills/` is a discovery layer for Codex.

---

## File Format

Each `SKILL.md` is a Markdown file with:

1. YAML frontmatter at the top
2. A Markdown body immediately after the closing `---`

### Required Frontmatter

The file must begin with a YAML frontmatter block containing:

* `name` — string, must match the skill directory slug
* `description` — string, must state what the skill does and when it should be used

Example:

```markdown
---
name: "research-internet"
description: "Conduct structured internet research and write research/research_internet.md.
Use during the internet research stage of a task."
---

# Research Internet
```

### Optional Frontmatter

Tool-specific metadata may be added only when it is clearly needed and remains compatible with
both toolchains. Do not require Claude-only metadata for baseline ARF skill validity.

---

## Required Body Structure

The Markdown body must contain:

* exactly one `#` title heading
* `**Version**: N` near the top, using a plain integer
* `## Goal`
* `## Inputs`
* `## Context`
* `## Steps`
* `## Done When`
* `## Forbidden`

Recommended sections:

* `## Output Format` when the skill produces structured output
* additional phase or protocol sections when the workflow is complex

---

## Writing Rules

Skills must follow these rules:

* Use imperative mood
* Use concrete file paths instead of abstract code descriptions
* Keep trigger wording in `description` specific enough for discovery
* Keep the body compatible with both Claude Code and Codex
* Keep symlink layout consistent across `.claude/skills/` and `.codex/skills/`

---

## Verification Rules

### Errors

| Code      | Description                                                     |
|-----------|-----------------------------------------------------------------|
| `SK-E001` | `arf/skills/<skill_name>/SKILL.md` is missing or empty          |
| `SK-E002` | YAML frontmatter is missing or not delimited by `---`           |
| `SK-E003` | `name` is missing from frontmatter                             |
| `SK-E004` | `description` is missing from frontmatter                      |
| `SK-E005` | Frontmatter `name` does not match the skill directory slug      |
| `SK-E006` | Required body section is missing                               |
| `SK-E007` | `.claude/skills/<skill_name>` is missing or has the wrong link |
| `SK-E008` | `.codex/skills/<skill_name>` is missing or has the wrong link  |
| `SK-E009` | A discovery symlink does not resolve to a directory with `SKILL.md` |

### Warnings

| Code      | Description                                                      |
|-----------|------------------------------------------------------------------|
| `SK-W001` | The description is too vague to explain when the skill should run |
| `SK-W002` | `## Output Format` is missing for a skill that produces files     |
| `SK-W003` | Optional tool-specific metadata appears without clear need        |

