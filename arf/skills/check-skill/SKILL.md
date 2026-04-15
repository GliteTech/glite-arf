---
name: "check-skill"
description: "Verify an ARF skill's structure, shared metadata, symlinks, and markdown quality. Use after creating or updating any skill under `arf/skills/`."
---

# Check Skill

**Version**: 5

## Goal

Verify that a skill was created correctly by checking its structure,
content, symlinks, and markdown style.

## Inputs

* `$ARGUMENTS` — name of the skill directory to check (e.g.,
  `check-python-style`). If omitted, check all skills in `arf/skills/`.

## Context

Read before starting:
* `arf/specifications/agent_skills_specification.md` — the authoritative
  skill format and symlink specification
* `arf/styleguide/agent_instructions_styleguide.md` — shared authoring guidance

## Steps

1. Read `arf/styleguide/agent_instructions_styleguide.md` to load all current
   rules.
2. Determine which skill(s) to check:
   * If `$ARGUMENTS` is provided, check only `arf/skills/$ARGUMENTS/`.
   * If `$ARGUMENTS` is empty, list all directories in `arf/skills/` and
     check each one.
3. For each skill directory, run these checks:

### Structure checks

4. Confirm `arf/skills/<name>/SKILL.md` exists and is not empty.
5. Confirm `.claude/skills/<name>` exists and is a symlink to
   `../../arf/skills/<name>`.
6. Confirm `.codex/skills/<name>` exists and is a symlink to
   `../../arf/skills/<name>`.
7. Confirm both symlinks resolve correctly (target directory exists and
   contains `SKILL.md`).

### Content checks (against the style guide)

8. Read the `SKILL.md` file and verify the YAML frontmatter:
   * starts at line 1 and is delimited by `---`
   * contains `name`
   * contains `description`
   * `name` matches the skill directory slug
9. Verify the file contains all required body sections:
   * `# <Skill Name>` — top-level heading (exactly one `#` heading)
   * `**Version**: N` — version number present near the top (plain integer,
     not X.Y)
   * `## Goal` — one-sentence goal statement
   * `## Inputs` — defines direct inputs, or states that there are none
   * `## Context` — points to specs, style guides, or files to read first
   * `## Steps` — numbered steps (not bullets) for the workflow
   * `## Done When` — explicit completion criteria
   * `## Forbidden` — explicit list of forbidden actions
10. Verify the file follows the agent instructions style guide:
   * Imperative mood (no "you should", "you might want to", "consider").
   * Concrete file paths where applicable (not abstract descriptions).
   * Emphasis (`**NEVER**`, `**MUST**`) used on at most 5 items.

### Markdown style check

11. Run `/check-markdown-style` on the skill's `SKILL.md` file:
    `arf/skills/<name>/SKILL.md`
12. Report any violations found by the markdown style checker as part of
    the skill check results.

### Registration check

13. Verify the skill appears in `.claude/settings.json` under the `skills`
    key if that key exists, or note that discovery is symlink-based in this
    repository.

## Output Format

Print results directly to the conversation. Use this structure:

```
## Skill Check: <skill-name>

### Structure

* [PASS] SKILL.md exists at `arf/skills/<name>/SKILL.md`
* [PASS] Claude symlink `.claude/skills/<name>` -> `../../arf/skills/<name>`
* [PASS] Codex symlink `.codex/skills/<name>` -> `../../arf/skills/<name>`
* [FAIL] Symlink target is `<actual>`, expected `../../arf/skills/<name>`

### Content

* [PASS] Has YAML frontmatter with `name` and `description`
* [FAIL] Missing YAML frontmatter delimiter at the top of the file
* [FAIL] Frontmatter `name` is `<actual>`, expected `<name>`
* [PASS] Has `# <Title>` heading
* [PASS] Has `**Version**` field
* [PASS] Has `## Inputs` section
* [PASS] Has `## Context` section
* [FAIL] Missing `## Done When` section

### Markdown Style

* [PASS] No violations found by /check-markdown-style
  (or list violations reported by the checker)

### Summary

<N> check(s) passed, <M> failed.
```

When checking multiple skills, repeat the above block for each skill, then
add a final overall summary.

## Done When

* Every skill directory has been checked for structure, symlinks, frontmatter,
  body content, and markdown style.
* `/check-markdown-style` has been run on every `SKILL.md` file.
* All checks are reported with PASS/FAIL status.
* A summary count is provided for each skill.
* Any failures include specific details on what is wrong and how to fix it.

## Forbidden

* NEVER skip the symlink checks — verifying both `.claude` and `.codex`
  symlinks is the primary purpose of this skill.
* NEVER skip the frontmatter checks — `name` and `description` are required
  for shared Claude Code and Codex compatibility.
* NEVER skip the markdown style check — invoke `/check-markdown-style`.
* NEVER fabricate check results — read actual files and verify symlinks
  with `ls -la`.
* NEVER auto-fix issues unless explicitly asked by the user.
* NEVER duplicate the full style guide content into this skill file.
