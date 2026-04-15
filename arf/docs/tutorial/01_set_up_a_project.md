# 1. Set Up a Project

First of five tutorials. By the end you will have an ARF project with one completed task, a
refreshed dashboard, and a results page on GitHub.

## What You'll Build

A tiny project called **MyResearch** that studies image augmentation. This part lays the skeleton:
GitHub repo, environment, description, budget. No tasks yet.

## Step 1: Fork the ARF Repository

ARF lives in a single GitHub repository. Fork it on github.com — click **Fork**, name the new repo
`myproject`, then clone your fork locally:

```bash
git clone git@github.com:<you>/myproject.git ~/myproject
cd ~/myproject
```

The fork already contains everything you need: the `arf/` directory (skills, verificators,
aggregators, specifications), `doctor.py` (the environment validator), [`meta/`](../../../meta/)
with default asset types, categories, metrics, and task types, and the top-level tooling files
(`pyproject.toml`, `uv.lock`, `ruff.toml`, etc.). No template, no copy-paste — just fork and go.

## Step 2: Run doctor.py

[`doctor.py`](../../../doctor.py) is the canonical setup tool. Run it with any Python — no
dependencies needed:

```bash
python3 doctor.py
```

It checks Python version, `uv`, `git`, `direnv`, the virtual environment, installed dependencies,
`.env` API keys, Git LFS, and pre-commit hooks. Each failed check prints the exact command or action
needed. **Follow its instructions**, fix the failure, and re-run. Repeat until every check is green.

## Step 3: Run create-project-description

The [`create-project-description`](../../skills/create-project-description/SKILL.md) skill walks you
through writing `project/description.md` and `project/budget.json` interactively. ARF skills work in
both Claude Code and Codex:

```text
/create-project-description   # Claude Code
$create-project-description   # Codex
```

The skill asks about the project goal, scope, research questions, success criteria, key references,
and budget. Answer in your own words. It maps your answers to the required sections of
[`project_description_specification.md`](../../specifications/project_description_specification.md)
and [`project_budget_specification.md`](../../specifications/project_budget_specification.md), runs
the verificators, and commits the result.

For this tutorial, tell the skill: a small project that studies image augmentation on CIFAR-10 with
ResNet-18, $100 budget, OpenAI and Anthropic APIs available.

When the skill finishes, `project/description.md` and `project/budget.json` exist, pass
verification, and are already committed.

## Next

Skeleton ready. The project ships with default [asset types](../reference/asset_types.md),
categories, metrics, and task types under `meta/` — these are project-specific and you should adjust
them before running any real tasks. Continue to [2. Customize meta/](02_customize_meta.md).
