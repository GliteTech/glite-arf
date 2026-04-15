# How to Add an Aggregator

## Goal

Create a new aggregator that collects one asset type across tasks, applies corrections, and outputs
a combined view.

## Prerequisites

* The asset type already has a specification and verificator
* Read
  [`arf/scripts/aggregators/aggregate_papers.py`](../../scripts/aggregators/aggregate_papers.py) as
  a reference
* Familiarity with [`arf/scripts/common/corrections.py`](../../scripts/common/corrections.py)

## Steps

1. Copy the template:
   `cp arf/scripts/aggregators/aggregate_papers.py arf/scripts/aggregators/aggregate_<slug>s.py`.
2. Walk `tasks/*/assets/<slug>/*/` and load each asset's `details.json` and canonical document.
3. Use Pydantic `BaseModel` at the I/O boundary, frozen dataclasses for internal logic.
4. Apply corrections via `arf/scripts/common/corrections.py` so deleted or replaced assets are
   honored.
5. Add the standard CLI flags via `argparse`:
   * `--format {json,md}`
   * `--detail {short,full}`
   * `--ids <task_id> [<task_id> ...]`
   * `--categories <cat> [<cat> ...]`
6. Implement both JSON and Markdown outputs. JSON uses Pydantic `model_dump_json()`; Markdown uses a
   deterministic template.
7. Register the aggregator in `arf/docs/reference/aggregators.md`.
8. Run `uv run ruff check --fix . && uv run ruff format . && uv run mypy .`.

## Verification

```bash
uv run python -m arf.scripts.aggregators.aggregate_<slug>s --format json
uv run python -m arf.scripts.aggregators.aggregate_<slug>s --format md --ids <task_id>
```

Expected: non-empty output matching the assets on disk minus anything removed by corrections.

## Pitfalls

* Forgetting to apply correction overlays — deleted assets reappear
* Mixing Pydantic models and dataclasses without a clear boundary
* Omitting `--ids` or `--categories` filters
* Non-deterministic ordering — sort results explicitly
* Instantiating `TypeAdapter` inside the hot loop instead of at module level

## See Also

* `../reference/aggregators.md`
* `../explanation/corrections_model.md`
