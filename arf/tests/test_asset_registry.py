"""Tests for the asset type discovery registry.

The registry scans ``meta/asset_types/*/`` for self-contained asset type
packages and exposes their verificator, aggregator, and formatter module
paths for the generic dispatchers.
"""

from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _create_asset_type(
    *,
    meta_dir: Path,
    slug: str,
    has_spec: bool = True,
    has_verificator: bool = False,
    has_aggregator: bool = False,
    has_formatter: bool = False,
) -> Path:
    """Seed a minimal asset type package under a fake meta/asset_types/ dir."""
    asset_dir: Path = meta_dir / "asset_types" / slug
    asset_dir.mkdir(parents=True, exist_ok=True)
    if has_spec:
        (asset_dir / "specification.md").write_text(
            f"# {slug} spec\n\n**Version**: 1\n",
            encoding="utf-8",
        )
    if has_verificator:
        (asset_dir / "verificator.py").write_text(
            "# stub verificator\n",
            encoding="utf-8",
        )
    if has_aggregator:
        (asset_dir / "aggregator.py").write_text(
            "# stub aggregator\n",
            encoding="utf-8",
        )
    if has_formatter:
        (asset_dir / "format_overview.py").write_text(
            "# stub formatter\n",
            encoding="utf-8",
        )
    return asset_dir


# ---------------------------------------------------------------------------
# discover_asset_types
# ---------------------------------------------------------------------------


def test_discovers_asset_type_with_spec(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import arf.scripts.common.asset_registry as registry_module

    meta_dir: Path = tmp_path / "meta"
    monkeypatch.setattr(
        target=registry_module,
        name="META_DIR",
        value=meta_dir,
    )
    registry_module._clear_cache()

    _create_asset_type(
        meta_dir=meta_dir,
        slug="paper",
        has_verificator=True,
        has_aggregator=True,
    )

    result = registry_module.discover_asset_types()

    assert "paper" in result
    info = result["paper"]
    assert info.slug == "paper"
    assert info.has_verificator is True
    assert info.has_aggregator is True
    assert info.has_formatter is False


def test_ignores_dir_without_specification_md(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import arf.scripts.common.asset_registry as registry_module

    meta_dir: Path = tmp_path / "meta"
    monkeypatch.setattr(
        target=registry_module,
        name="META_DIR",
        value=meta_dir,
    )
    registry_module._clear_cache()

    _create_asset_type(
        meta_dir=meta_dir,
        slug="orphan",
        has_spec=False,
        has_verificator=True,
    )

    result = registry_module.discover_asset_types()
    assert "orphan" not in result


def test_returns_empty_when_no_asset_types_exist(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import arf.scripts.common.asset_registry as registry_module

    meta_dir: Path = tmp_path / "meta"
    (meta_dir / "asset_types").mkdir(parents=True)
    monkeypatch.setattr(
        target=registry_module,
        name="META_DIR",
        value=meta_dir,
    )
    registry_module._clear_cache()

    result = registry_module.discover_asset_types()
    assert len(result) == 0


def test_discovers_multiple_asset_types(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import arf.scripts.common.asset_registry as registry_module

    meta_dir: Path = tmp_path / "meta"
    monkeypatch.setattr(
        target=registry_module,
        name="META_DIR",
        value=meta_dir,
    )
    registry_module._clear_cache()

    _create_asset_type(meta_dir=meta_dir, slug="paper", has_verificator=True)
    _create_asset_type(meta_dir=meta_dir, slug="dataset", has_aggregator=True)
    _create_asset_type(meta_dir=meta_dir, slug="benchmark")

    result = registry_module.discover_asset_types()
    assert set(result.keys()) == {"paper", "dataset", "benchmark"}


# ---------------------------------------------------------------------------
# get_verificator_module / get_aggregator_module / get_formatter_module
# ---------------------------------------------------------------------------


def test_get_verificator_module_returns_path_when_exists(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import arf.scripts.common.asset_registry as registry_module

    meta_dir: Path = tmp_path / "meta"
    monkeypatch.setattr(
        target=registry_module,
        name="META_DIR",
        value=meta_dir,
    )
    registry_module._clear_cache()

    _create_asset_type(meta_dir=meta_dir, slug="paper", has_verificator=True)

    result: str | None = registry_module.get_verificator_module(slug="paper")
    assert result == "meta.asset_types.paper.verificator"


def test_get_verificator_module_returns_none_when_missing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import arf.scripts.common.asset_registry as registry_module

    meta_dir: Path = tmp_path / "meta"
    monkeypatch.setattr(
        target=registry_module,
        name="META_DIR",
        value=meta_dir,
    )
    registry_module._clear_cache()

    _create_asset_type(meta_dir=meta_dir, slug="paper", has_verificator=False)

    result: str | None = registry_module.get_verificator_module(slug="paper")
    assert result is None


def test_get_aggregator_module_returns_path_when_exists(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import arf.scripts.common.asset_registry as registry_module

    meta_dir: Path = tmp_path / "meta"
    monkeypatch.setattr(
        target=registry_module,
        name="META_DIR",
        value=meta_dir,
    )
    registry_module._clear_cache()

    _create_asset_type(meta_dir=meta_dir, slug="dataset", has_aggregator=True)

    result: str | None = registry_module.get_aggregator_module(slug="dataset")
    assert result == "meta.asset_types.dataset.aggregator"


def test_get_formatter_module_returns_path_when_exists(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import arf.scripts.common.asset_registry as registry_module

    meta_dir: Path = tmp_path / "meta"
    monkeypatch.setattr(
        target=registry_module,
        name="META_DIR",
        value=meta_dir,
    )
    registry_module._clear_cache()

    _create_asset_type(meta_dir=meta_dir, slug="model", has_formatter=True)

    result: str | None = registry_module.get_formatter_module(slug="model")
    assert result == "meta.asset_types.model.format_overview"


def test_get_module_returns_none_for_unknown_slug(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import arf.scripts.common.asset_registry as registry_module

    meta_dir: Path = tmp_path / "meta"
    (meta_dir / "asset_types").mkdir(parents=True)
    monkeypatch.setattr(
        target=registry_module,
        name="META_DIR",
        value=meta_dir,
    )
    registry_module._clear_cache()

    assert registry_module.get_verificator_module(slug="nonexistent") is None
    assert registry_module.get_aggregator_module(slug="nonexistent") is None
    assert registry_module.get_formatter_module(slug="nonexistent") is None


# ---------------------------------------------------------------------------
# build_verificator_module_map (used by verify_task_complete dispatch)
# ---------------------------------------------------------------------------


def test_build_verificator_module_map_returns_only_types_with_verificators(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import arf.scripts.common.asset_registry as registry_module

    meta_dir: Path = tmp_path / "meta"
    monkeypatch.setattr(
        target=registry_module,
        name="META_DIR",
        value=meta_dir,
    )
    registry_module._clear_cache()

    _create_asset_type(meta_dir=meta_dir, slug="paper", has_verificator=True)
    _create_asset_type(meta_dir=meta_dir, slug="dataset", has_verificator=False)
    _create_asset_type(meta_dir=meta_dir, slug="model", has_verificator=True)

    result: dict[str, str] = registry_module.build_verificator_module_map()

    assert result == {
        "paper": "meta.asset_types.paper.verificator",
        "model": "meta.asset_types.model.verificator",
    }
    assert "dataset" not in result


# ---------------------------------------------------------------------------
# Cache behavior
# ---------------------------------------------------------------------------


def test_cache_is_invalidated_by_clear_cache(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import arf.scripts.common.asset_registry as registry_module

    meta_dir: Path = tmp_path / "meta"
    monkeypatch.setattr(
        target=registry_module,
        name="META_DIR",
        value=meta_dir,
    )
    registry_module._clear_cache()

    _create_asset_type(meta_dir=meta_dir, slug="paper")
    first = registry_module.discover_asset_types()
    assert "paper" in first

    _create_asset_type(meta_dir=meta_dir, slug="dataset")
    same_as_first = registry_module.discover_asset_types()
    assert "dataset" not in same_as_first, "cache should still return old result"

    registry_module._clear_cache()
    after_clear = registry_module.discover_asset_types()
    assert "dataset" in after_clear, "cache cleared, dataset should now appear"
