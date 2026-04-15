"""Discovery registry for asset type packages under ``meta/asset_types/``.

Each asset type is a self-contained directory::

    meta/asset_types/<slug>/
    ├── specification.md      # required — the type exists iff this file exists
    ├── verificator.py        # optional — validates asset structure
    ├── aggregator.py         # optional — collects assets across tasks
    ├── format_overview.py    # optional — materializes overview output
    └── ...

The registry scans once per process (cached), returns
:class:`AssetTypeInfo` records, and exposes module-path helpers for the
generic dispatchers in ``verify_task_complete``, ``materialize``, etc.
"""

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT: Path = Path(__file__).resolve().parents[3]
META_DIR: Path = REPO_ROOT / "meta"

ASSET_TYPES_SUBDIR: str = "asset_types"
SPEC_FILE_NAME: str = "specification.md"
VERIFICATOR_FILE_NAME: str = "verificator.py"
AGGREGATOR_FILE_NAME: str = "aggregator.py"
FORMATTER_FILE_NAME: str = "format_overview.py"

MODULE_BASE_PREFIX: str = "meta.asset_types"


@dataclass(frozen=True, slots=True)
class AssetTypeInfo:
    """Metadata about a discovered asset type package."""

    slug: str
    spec_path: Path
    has_verificator: bool
    has_aggregator: bool
    has_formatter: bool
    module_base: str


# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------

_cache: dict[str, AssetTypeInfo] | None = None


def _clear_cache() -> None:
    """Invalidate the cached registry. Used by tests."""
    global _cache  # noqa: PLW0603
    _cache = None


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


def discover_asset_types() -> dict[str, AssetTypeInfo]:
    """Scan ``meta/asset_types/*/`` and return a dict keyed by slug.

    A directory is recognized as an asset type if and only if it
    contains a ``specification.md`` file. All other files
    (``verificator.py``, ``aggregator.py``, ``format_overview.py``)
    are optional capabilities detected by presence.

    Results are cached for the lifetime of the process. Call
    :func:`_clear_cache` to force a re-scan (primarily for tests).
    """
    global _cache  # noqa: PLW0603
    if _cache is not None:
        return _cache

    asset_types_dir: Path = META_DIR / ASSET_TYPES_SUBDIR
    result: dict[str, AssetTypeInfo] = {}

    if asset_types_dir.is_dir() is False:
        _cache = result
        return result

    for entry in sorted(asset_types_dir.iterdir()):
        if entry.is_dir() is False:
            continue
        spec_path: Path = entry / SPEC_FILE_NAME
        if spec_path.is_file() is False:
            continue

        slug: str = entry.name
        result[slug] = AssetTypeInfo(
            slug=slug,
            spec_path=spec_path,
            has_verificator=(entry / VERIFICATOR_FILE_NAME).is_file(),
            has_aggregator=(entry / AGGREGATOR_FILE_NAME).is_file(),
            has_formatter=(entry / FORMATTER_FILE_NAME).is_file(),
            module_base=f"{MODULE_BASE_PREFIX}.{slug}",
        )

    _cache = result
    return result


# ---------------------------------------------------------------------------
# Module-path helpers
# ---------------------------------------------------------------------------


def get_verificator_module(*, slug: str) -> str | None:
    """Return the dotted module path for a type's verificator, or None."""
    info: AssetTypeInfo | None = discover_asset_types().get(slug)
    if info is None or info.has_verificator is False:
        return None
    return f"{info.module_base}.verificator"


def get_aggregator_module(*, slug: str) -> str | None:
    """Return the dotted module path for a type's aggregator, or None."""
    info: AssetTypeInfo | None = discover_asset_types().get(slug)
    if info is None or info.has_aggregator is False:
        return None
    return f"{info.module_base}.aggregator"


def get_formatter_module(*, slug: str) -> str | None:
    """Return the dotted module path for a type's formatter, or None."""
    info: AssetTypeInfo | None = discover_asset_types().get(slug)
    if info is None or info.has_formatter is False:
        return None
    return f"{info.module_base}.format_overview"


# ---------------------------------------------------------------------------
# Dispatch-map builder (used by verify_task_complete)
# ---------------------------------------------------------------------------


def build_verificator_module_map() -> dict[str, str]:
    """Build the ``{slug: module_path}`` dict for asset verificator dispatch.

    Returns only asset types that have a ``verificator.py``. This is the
    dynamic replacement for the hardcoded
    ``ASSET_TYPE_VERIFICATOR_MODULES`` dict in ``constants.py``.
    """
    return {
        slug: f"{info.module_base}.verificator"
        for slug, info in discover_asset_types().items()
        if info.has_verificator is True
    }
