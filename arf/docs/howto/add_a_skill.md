# How to Add a Skill

## Goal

Create a new ARF skill discoverable by both Claude Code and Codex CLI.

## Prerequisites

* Familiarity with
  [`arf/specifications/agent_skills_specification.md`](../../specifications/agent_skills_specification.md)
* A single-purpose workflow to encapsulate
* A unique kebab-case slug (e.g. `my-new-skill`)

## Steps

1. Create the directory: `mkdir -p arf/skills/<slug>`.
2. Create `arf/skills/<slug>/SKILL.md` (see
   [`arf/skills/check-skill/SKILL.md`](../../skills/check-skill/SKILL.md) for an example) with YAML
   frontmatter containing `name` (matching the slug) and `description` (stating both capability and
   trigger context).
3. Add `**Version**: 1` in the skill body, immediately after the `#` title.
4. Fill in the body sections: `## Goal`, `## Inputs`, `## Context`, `## Steps`, `## Done When`,
   `## Forbidden`.
5. Symlink for Claude Code: `ln -s ../../arf/skills/<slug> .claude/skills/<slug>`.
6. Symlink for Codex: `ln -s ../../arf/skills/<slug> .codex/skills/<slug>`.
7. Stage both: `git add .claude/skills/<slug> .codex/skills/<slug>`.
8. Format: `uv run flowmark --inplace --nobackup arf/skills/<slug>/SKILL.md`.

## Verification

Invoke the [`check-skill`](../../skills/check-skill/SKILL.md) skill against the new slug. Expected:
zero errors and zero warnings. Confirm symlinks resolve:

```bash
readlink .claude/skills/<slug>
readlink .codex/skills/<slug>
```

Both must print `../../arf/skills/<slug>`.

## Pitfalls

* Missing one or both discovery symlinks — the skill becomes invisible to that tool
* Missing `name` or `description` in YAML frontmatter
* `description` does not state *when* to trigger the skill
* Missing `**Version**: 1` line below the title
* Absolute symlink target instead of `../../arf/skills/<slug>`

## See Also

* `../reference/skills.md`
* `../../specifications/agent_skills_specification.md`
