# How to Add an Asset Type

## Goal

Register a new asset type as a self-contained package under `meta/asset_types/<slug>/`. The
framework discovers it automatically — no edits to `arf/` needed.

## Prerequisites

* A unique snake_case slug (e.g. `benchmark`, `experiment_log`)
* Read [`meta/asset_types/paper/`](../../../meta/asset_types/paper/) as a working example of a
  complete asset type package

## Steps

1. Create the directory:

   ```bash
   mkdir -p meta/asset_types/<slug>/tests
   touch meta/asset_types/<slug>/__init__.py
   touch meta/asset_types/<slug>/tests/__init__.py
   ```

2. Write `meta/asset_types/<slug>/specification.md`, copying the paper spec structure. Include
   `**Version**: 1` near the top.

3. Define the folder layout under `tasks/<task_id>/assets/<slug>/<asset_id>/`.

4. Define the `details.json` schema as a table: every field, type, required/optional, description.
   Always include `spec_version`, `added_by_task`, `date_added`.

5. Define the canonical document (e.g. `summary.md`, `description.md`) with required YAML
   frontmatter and mandatory sections. Record its path in a `<name>_path` field in `details.json`.

6. **Add a verificator** (optional but recommended). Create `meta/asset_types/<slug>/verificator.py`
   following the pattern in
   [`meta/asset_types/paper/verificator.py`](../../../meta/asset_types/paper/verificator.py). Use a
   2-3 letter diagnostic prefix. The framework discovers and runs it automatically via
   `verify_task_complete`.

7. Add all error and warning codes to the new spec's "Verification Rules" section.

8. **Add an aggregator** (optional). Create `meta/asset_types/<slug>/aggregator.py` following the
   pattern in
   [`meta/asset_types/paper/aggregator.py`](../../../meta/asset_types/paper/aggregator.py).

9. **Add a formatter** (optional). Create `meta/asset_types/<slug>/format_overview.py` for the
   materialized overview output.

10. Add tests in `meta/asset_types/<slug>/tests/test_verificator.py` and `test_aggregator.py`.
    Pytest discovers them automatically from `meta/`.

11. Add an entry in `arf/docs/reference/asset_types.md`.

12. Run `uv run flowmark --inplace --nobackup meta/asset_types/<slug>/specification.md`.

## What the framework discovers automatically

The asset registry (`arf/scripts/common/asset_registry.py`) scans `meta/asset_types/*/` for
directories containing `specification.md`. For each discovered type:

* If `verificator.py` exists → `verify_task_complete` runs it on matching assets.
* If `aggregator.py` exists → it can be called via
  `uv run python -m meta.asset_types.<slug>.aggregator`.
* If `format_overview.py` exists → `materialize.py` calls it for overview output.

No edits to `arf/` are needed. No constants to add. No dispatch dicts to update.

## Verification

Create one example asset under a scratch task and run:

```bash
uv run python -m meta.asset_types.<slug>.verificator <task_id> <asset_id>
```

Expected: zero errors. Then run
`uv run ruff check --fix . && uv run ruff format . && uv run mypy .`.

## Pitfalls

* Skipping the canonical document path field in `details.json`
* Diagnostic prefix collides with an existing verificator
* Forgetting to update `arf/docs/reference/asset_types.md`
* Omitting `spec_version` from `details.json`
* Missing `__init__.py` in the asset type directory or its tests/ subdirectory

## See Also

* `../reference/asset_types.md`
* `arf/scripts/common/asset_registry.py` — the discovery module
