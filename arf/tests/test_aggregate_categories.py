"""Tests for arf.scripts.aggregators.aggregate_categories."""

from pathlib import Path

import pytest

import arf.scripts.aggregators.aggregate_categories as agg_mod
from arf.scripts.aggregators.aggregate_categories import (
    CategoryInfo,
    aggregate_categories,
)
from arf.tests.fixtures.metadata_builders import build_category
from arf.tests.fixtures.paths import configure_repo_paths

CATEGORY_WSD: str = "wsd-evaluation"
CATEGORY_NLP: str = "nlp-general"
CATEGORY_INFRA: str = "infrastructure"


@pytest.fixture()
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=tmp_path,
        aggregator_modules=[agg_mod],
    )
    return tmp_path


# ---------------------------------------------------------------------------
# Empty state
# ---------------------------------------------------------------------------


def test_empty_returns_no_categories(repo: Path) -> None:
    result: list[CategoryInfo] = aggregate_categories()
    assert len(result) == 0


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


def test_discovers_multiple_categories(repo: Path) -> None:
    build_category(
        repo_root=repo,
        category_slug=CATEGORY_WSD,
        name="WSD Evaluation",
    )
    build_category(
        repo_root=repo,
        category_slug=CATEGORY_NLP,
        name="NLP General",
    )

    result: list[CategoryInfo] = aggregate_categories()
    slugs: list[str] = [c.category_id for c in result]

    assert CATEGORY_WSD in slugs
    assert CATEGORY_NLP in slugs
    assert len(result) == 2


def test_category_fields_populated(repo: Path) -> None:
    build_category(
        repo_root=repo,
        category_slug=CATEGORY_WSD,
        name="WSD Evaluation",
        short_description="Evaluating WSD systems.",
    )

    result: list[CategoryInfo] = aggregate_categories()
    assert len(result) == 1

    cat: CategoryInfo = result[0]
    assert cat.category_id == CATEGORY_WSD
    assert cat.name == "WSD Evaluation"
    assert cat.short_description == "Evaluating WSD systems."


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_malformed_description_json_skipped(repo: Path) -> None:
    build_category(repo_root=repo, category_slug=CATEGORY_WSD)

    # Create a malformed category
    bad_dir: Path = repo / "meta" / "categories" / "bad-cat"
    bad_dir.mkdir(parents=True, exist_ok=True)
    (bad_dir / "description.json").write_text("{invalid", encoding="utf-8")

    result: list[CategoryInfo] = aggregate_categories()
    slugs: list[str] = [c.category_id for c in result]
    assert CATEGORY_WSD in slugs
    assert "bad-cat" not in slugs


def test_sorted_alphabetically(repo: Path) -> None:
    build_category(repo_root=repo, category_slug=CATEGORY_NLP)
    build_category(repo_root=repo, category_slug=CATEGORY_INFRA)
    build_category(repo_root=repo, category_slug=CATEGORY_WSD)

    result: list[CategoryInfo] = aggregate_categories()
    slugs: list[str] = [c.category_id for c in result]
    assert slugs == sorted(slugs)
