"""Shim exposing the predictions-asset aggregator at its documented module path.

The real implementation lives at ``meta.asset_types.predictions.aggregator`` so
it stays co-located with the predictions asset specification. This shim lets
callers invoke the aggregator as documented in
``arf/docs/reference/aggregators.md``:

    uv run python -m arf.scripts.aggregators.aggregate_predictions
"""

from meta.asset_types.predictions.aggregator import main

__all__ = ["main"]


if __name__ == "__main__":
    main()
