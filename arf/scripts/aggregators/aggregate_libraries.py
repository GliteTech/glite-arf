"""Shim exposing the library-asset aggregator at its documented module path.

The real implementation lives at ``meta.asset_types.library.aggregator`` so it
stays co-located with the library asset specification. This shim lets callers
invoke the aggregator as documented in ``arf/docs/reference/aggregators.md``:

    uv run python -m arf.scripts.aggregators.aggregate_libraries
"""

from meta.asset_types.library.aggregator import main

__all__ = ["main"]


if __name__ == "__main__":
    main()
