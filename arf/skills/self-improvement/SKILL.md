---
name: "self-improvement"
description: "Plan and execute a framework change across every related ARF file — specifications, verificators, aggregators, skills, scripts, hooks, tests, materializers, and docs — in a dedicated infrastructure branch and worktree, with style checks and the full test suite. Use whenever anything under `arf/` or generic parts of `meta/` needs to change."
---
# Self-Improvement

**Version**: 2

## Goal

Plan and execute a change to the Glite ARF framework so every related specification, verificator,
aggregator, script, test, skill, hook, materializer, reference doc, and style guide stays
consistent, and ship it through an isolated infrastructure branch and pull request.

## Inputs

* `$ARGUMENTS` — free-text description of the framework change the user wants. It may point at a
  specification, a verificator, an aggregator, a skill, a script, a hook, a doc, the materializer,
  or any combination of those. If `$ARGUMENTS` is empty, stop and ask the user what to change before
  doing anything else.

## Context

Read before starting:

* `arf/README.md` — framework principles, glossary, and the fundamental rules the skill enforces
  (task isolation, immutability of completed tasks, structure enforced by scripts, no duplication,
  comprehensive logging, subagent isolation).
* `CLAUDE.md` — repository rules, especially rule 0 ("framework / infrastructure / specification /
  skill / verificator / aggregator / materializer changes in `arf/`, generic `meta/`, and generic
  boilerplate are not task work").
* `arf/specifications/agent_skills_specification.md` — the skill format contract this skill is
  itself held to.
* `arf/styleguide/agent_instructions_styleguide.md` — rules for writing skills, rules, and
  specifications.
* `arf/styleguide/markdown_styleguide.md` — Flowmark-aligned markdown rules enforced by
  `check-markdown-style`.
* `arf/styleguide/python_styleguide.md` — Python rules enforced by `check-python-style`.
* `arf/docs/reference/aggregators.md` — canonical list of aggregators and their flags.
* `arf/docs/reference/` — other reference docs (verificators, specifications, skills, glossary,
  utilities, asset types) whenever the change touches one of those areas.
* `arf/scripts/utils/worktree.py` — provides the `raw-path <slug>` CLI used in Step 3 to compute the
  sibling-worktree path for the `infra/` branch. Use the CLI; never hardcode the
  `../<repo-name>-worktrees/` literal in this skill.
* Every concrete framework file the requested change will edit: read it before proposing a diff, and
  name it in the impact map (Step 2).

## Steps

### Step 1: Confirm the change is framework-level

1. Classify `$ARGUMENTS`. Framework-level targets live only in:
   * `arf/` — specifications, scripts, skills, tests, styleguide, docs.
   * Generic boilerplate under `meta/` (asset type definitions, task type definitions, category
     scaffolding, metric definitions that apply to any project).
   * Top-level tooling files the framework owns: `pyproject.toml`, `uv.lock`, `ruff.toml`,
     `mypy.ini`, `.gitignore`, `.pre-commit-config.yaml`, `.claude/settings.json`.
2. Reject anything project-specific. Specific datasets, specific experiments, specific papers,
   specific research findings, domain vocabulary belong in `project/` or under `tasks/tXXXX_*`,
   never in `arf/` or generic `meta/`. Redirect the user to the task workflow (`execute-task`,
   `create-task`) instead.
3. If any part of the request mixes framework and project concerns, split it: keep only the
   framework-generic part and tell the user to file the project-specific part as a task.

### Step 2: Map the impact surface

List every framework area that might need updating for this change. Do not skip an area — mark it
explicitly "not affected — because ..." when it does not apply.

* **Specifications** — `arf/specifications/*.md`. Does any contract change? If yes, bump its
  `**Version**: N` integer and update every `spec_version` field in schemas the spec defines.
* **Verificators** — `arf/scripts/verificators/*.py`. Does any rule, error code, or warning code
  change, or does a new one need to exist?
* **Aggregators** — `arf/scripts/aggregators/*.py` and `arf/docs/reference/aggregators.md`. Does any
  aggregator need a new flag, a new field, a new filter, or a new entry?
* **Skills** — `arf/skills/*/SKILL.md`. Does any skill step, forbidden rule, context pointer, or
  version need updating? Does a new skill need to exist?
* **Scripts and utilities** — `arf/scripts/utils/*.py`, `arf/scripts/common/*.py`. Does shared code
  need changes or new helpers?
* **Hooks** — `arf/scripts/hooks/*.py` and `.claude/settings.json`. Does a hook need to be added,
  removed, or re-wired?
* **Materializers** — `arf/scripts/overview/materialize.py` and every `format_*.py` next to it. Does
  overview output depend on the changed contract?
* **LLM context archives** — `arf/scripts/overview/llm_context/` outputs. Will they need a rebuild?
* **Tests** — `arf/tests/test_*.py`. Every verificator, aggregator, and framework script must have a
  test. New behavior needs a new test; changed behavior needs an updated one.
* **Style guides** — `arf/styleguide/*.md`. Are any rules added, changed, or clarified?
* **Reference and how-to docs** — `arf/docs/reference/`, `arf/docs/howto/`, `arf/docs/explanation/`,
  `arf/docs/tutorial/`. Update the docs that describe the changed area.
* **Top-level tooling** — `pyproject.toml`, `uv.lock`, `ruff.toml`, `mypy.ini`, `.gitignore`. Does
  the change add a dependency or a lint rule?
* **Generic `meta/`** — `meta/asset_types/`, `meta/task_types/`, and any scaffolding directories.
  Does a generic template need updating?

Write this impact map as the first message in the PR description so it is reviewable.

### Step 3: Create the infrastructure branch and worktree

1. Start from a clean `main`:

   ```bash
   git checkout main
   git pull --ff-only
   git status
   ```

2. Pick a short slug and construct the infrastructure branch name with the `infra/` prefix. The
   branch name must never start with `task/` and must not match any existing branch.

3. Resolve the sibling-worktree path via the canonical CLI — never hardcode the literal. The
   `raw-path` subcommand derives the path from the current repository's name, so the skill stays
   project-agnostic across forks:

   ```bash
   SLUG=<short-slug>
   WT_SLUG="infra_${SLUG}"
   BRANCH="infra/${SLUG}"
   WT_PATH=$(uv run python -m arf.scripts.utils.worktree raw-path "$WT_SLUG")
   git worktree add -b "$BRANCH" "$WT_PATH" main
   ```

4. Enter the worktree and run `uv sync` so it has the same environment as the main checkout:

   ```bash
   cd "$WT_PATH"
   uv sync
   ```

5. Do the rest of the work inside the worktree. Never edit files in the main checkout for this
   change.

### Step 4: Write tests first for any new script behavior

For any new script, new function, or new public behavior in an existing script:

1. Delegate test authoring to a dedicated subagent. Give that subagent only the specification and
   the style guide — do not give it the current implementation or a draft of it. Otherwise the tests
   describe the implementation instead of the contract.
2. The subagent places tests under `arf/tests/test_*.py` following the existing fixture and builder
   conventions.
3. Run the new tests once and confirm they fail for the right reason (the feature does not exist
   yet). Only then proceed to implementation.

Edits that only touch markdown, a specification, a skill, a reference doc, or a style guide do not
need new Python tests, but must still respect any existing test that asserts on their contents.

### Step 5: Implement the change in one consistent pass

1. Edit every file identified in the impact map in Step 2.
2. Keep edits that share a contract in the same PR. A specification change without its matching
   verificator, aggregator, test, and doc update is forbidden.
3. Bump versions where required: `**Version**: N` in specifications and skills, `spec_version`
   fields in the data formats the spec defines.
4. Follow the three style guides while editing:
   * `arf/styleguide/markdown_styleguide.md` for every `.md` file.
   * `arf/styleguide/agent_instructions_styleguide.md` for skills, rules, and specifications.
   * `arf/styleguide/python_styleguide.md` for every `.py` file.
5. Commit each logically distinct change as its own commit with a descriptive message.

### Step 6: Run the three style checkers in parallel, one per file

For every file that was added or modified, run the matching checker. Launch the checkers as
independent parallel subagents — one subagent per file per applicable checker — so results do not
contaminate each other.

* Every edited `.md` file → invoke `/check-markdown-style` with that file as the argument.
* Every edited `.py` file → invoke `/check-python-style` with that file as the argument.
* Every added or edited skill directory → invoke `/check-skill` with that skill slug.

Fix every reported violation at the source. Never silence a checker.

### Step 7: Run the framework test suite

From inside the worktree:

```bash
uv run python -u arf/scripts/utils/run_with_logs.py uv run pytest arf/tests -q
```

Fix every failure at its root cause. Never weaken an assertion to make a test pass.

### Step 8: Run affected verificators on fixtures

If the change modifies any verificator or any specification it enforces, run that verificator
against the relevant fixture data in `arf/tests/fixtures/` and confirm the expected error and
warning codes fire. Add fixtures for any new code path.

### Step 9: Rebuild the overview when materializers or their inputs changed

If the change touches `arf/scripts/overview/` or any contract that an `overview/` output consumes,
rebuild the overview from inside the worktree:

```bash
uv run python -u arf/scripts/overview/materialize.py
```

Commit the regenerated files in the same branch. If no materializer input changed, record "overview
rebuild: not needed — no materializer inputs changed" in the final report.

### Step 10: Open the PR, merge, sync `main`, and remove the worktree

1. Push the infrastructure branch.

2. Open a PR. The PR description must contain:
   * The impact map from Step 2.
   * The version bumps from Step 5.
   * The style check, test, and verificator results from Steps 6-8.
   * The overview rebuild status from Step 9.

3. After the PR is green, merge it into `main` via the normal merge path. Resolve any conflicts; do
   not force-merge.

4. Switch the main checkout back to `main`, pull with fast-forward, and confirm the merge landed:

   ```bash
   git checkout main
   git pull --ff-only
   git status
   git log --oneline -5
   ```

5. Remove the worktree and delete the branch locally. The worktree path is re-resolved via the same
   `raw-path` helper used in Step 3, so the skill never needs to know the repo name:

   ```bash
   WT_PATH=$(uv run python -m arf.scripts.utils.worktree raw-path "infra_${SLUG}")
   git worktree remove "$WT_PATH"
   git branch -d "infra/${SLUG}"
   ```

### Step 11: Final verification on `main`

1. Re-run `uv run pytest arf/tests -q` on `main`.
2. Re-run `/check-skill` on any skill that changed.
3. Confirm `arf/todo.md` has an empty diff for the whole PR.
4. Confirm no `tasks/tXXXX_*` folder was created for this change.

## Output Format

Report back to the user in the chat with these sections, as markdown:

* `## Change Summary` — one paragraph describing what changed and why.
* `## Impact Map` — the table of framework areas from Step 2, with each row marked "updated" or "not
  affected — because ...".
* `## Files Touched` — grouped by framework area, with file paths.
* `## Version Bumps` — every specification and skill whose `**Version**: N` integer changed, and
  every `spec_version` value updated in data formats.
* `## Tests` — new and changed test files, plus the `pytest` result.
* `## Style Checks` — result of every `/check-markdown-style`, `/check-python-style`, and
  `/check-skill` run, one line per file.
* `## Verificator Runs` — any verificator sanity run and its outcome.
* `## Overview Rebuild` — either "rebuilt" with the commit hash, or "not needed — no materializer
  inputs changed".
* `## PR` — branch name, PR URL, merge status.
* `## Final Verification` — `pytest` result on `main`, confirmation the worktree was removed, and
  confirmation `arf/todo.md` was untouched.

## Done When

* Step 2 impact map exists and every framework area is either "updated" or explicitly "not affected
  — because ...".
* Tests for any new script behavior were written by a separate subagent before the implementation
  and initially failed for the right reason.
* Every edited `.md`, `.py`, and skill directory passed its matching checker without fixing
  violations by silencing the checker.
* `uv run pytest arf/tests -q` is green both inside the worktree and on `main` after merge.
* Any affected verificator was exercised against fixtures and produced the expected codes.
* `arf/scripts/overview/materialize.py` was re-run whenever a materializer input changed, and the
  regenerated files were committed in the same PR.
* The change shipped on an `infra/<slug>` branch in a sibling git worktree (path resolved via
  `arf.scripts.utils.worktree raw-path`, never hardcoded) and was merged into `main` via a
  reviewable PR.
* `arf/todo.md` was **not** touched.
* No `tasks/tXXXX_*` folder was created for this change.
* The sibling worktree was removed and the local `infra/<slug>` branch was deleted after merge.

## Forbidden

* NEVER edit `arf/todo.md`. The user updates it by hand.
* NEVER create a `tasks/tXXXX_*` folder or a `task/*` branch for framework work. Framework work is
  not task work.
* NEVER introduce project-specific content (specific datasets, specific experiments, specific domain
  vocabulary, specific research findings) into `arf/` or the generic parts of `meta/`. The framework
  must stay project-agnostic so it can be reused across research projects. This explicitly includes
  hardcoding the worktree path — always call `arf.scripts.utils.worktree raw-path` instead of
  writing `../<something>-worktrees/...` literally.
* NEVER implement new script behavior before writing its tests in a separate subagent that does not
  see the implementation.
* NEVER skip running `check-markdown-style`, `check-python-style`, or `check-skill` on files they
  apply to, and never silence a checker instead of fixing the violation.
* NEVER merge without a green `uv run pytest arf/tests -q` from inside the worktree.
* NEVER edit a specification without also updating the verificators, aggregators, skills, tests, and
  reference docs that depend on that specification in the same PR.
* NEVER reuse an existing branch name or work directly on `main` for an infrastructure change.
* NEVER bypass pre-commit, verification, or hook failures with `--no-verify` or equivalent.
* NEVER rebuild the overview on a task branch. Overview rebuilds triggered by framework changes land
  on the same `infra/<slug>` branch that made the change.
