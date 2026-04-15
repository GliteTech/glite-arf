import json
from pathlib import Path

import pytest

import arf.scripts.overview.format_news as format_news_module
from arf.scripts.overview.format_news import (
    NewsDayInfo,
    _format_day_page,
    _format_index_page,
    _rewrite_relative_paths,
    discover_news_dates,
    load_all_news,
    materialize_news,
)
from arf.tests.fixtures.paths import configure_repo_paths


def _setup(*, monkeypatch: pytest.MonkeyPatch, repo_root: Path) -> None:
    configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=repo_root,
        verificator_modules=[format_news_module],
    )
    news_dir: Path = repo_root / "news"
    overview_news_dir: Path = repo_root / "overview" / "news"
    monkeypatch.setattr(format_news_module, "NEWS_DIR", news_dir)
    monkeypatch.setattr(format_news_module, "NEWS_OVERVIEW_DIR", overview_news_dir)
    monkeypatch.setattr(
        format_news_module,
        "NEWS_INDEX_README",
        overview_news_dir / "README.md",
    )


def _write_news_pair(
    *,
    news_dir: Path,
    date: str,
    tasks_completed: int = 3,
    tasks_created: int = 1,
    total_cost_usd: float = 100.0,
) -> None:
    news_dir.mkdir(parents=True, exist_ok=True)
    md_path: Path = news_dir / f"{date}.md"
    json_path: Path = news_dir / f"{date}.json"
    md_path.write_text(
        f"## Test Day {date}\n\n**{tasks_completed} tasks completed.**\n\n"
        f"## Where we stand\n\n| S | F1 |\n\n## Costs\n\n| x | $1 |\n",
        encoding="utf-8",
    )
    json_data: dict[str, object] = {
        "spec_version": "2",
        "date": date,
        "tasks_completed": [
            {"task_id": f"t{i:04d}_test", "name": "Test", "cost_usd": 0, "key_finding": "x"}
            for i in range(tasks_completed)
        ],
        "tasks_created": [
            {"task_id": f"t{i:04d}_new", "name": "New", "reason": "x"} for i in range(tasks_created)
        ],
        "tasks_cancelled": [],
        "total_cost_usd": total_cost_usd,
        "assets_added": 0,
        "papers_added": 0,
        "infrastructure_changes": [],
        "current_best_results": [],
        "key_findings": ["Finding one"],
    }
    json_path.write_text(
        json.dumps(json_data, indent=2),
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# discover_news_dates
# ---------------------------------------------------------------------------


def test_discover_no_news_dir(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    dates: list[str] = discover_news_dates()
    assert len(dates) == 0


def test_discover_empty_news_dir(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    (tmp_path / "news").mkdir(exist_ok=True)
    dates = discover_news_dates()
    assert len(dates) == 0


def test_discover_finds_dates_sorted(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    news_dir: Path = tmp_path / "news"
    _write_news_pair(news_dir=news_dir, date="2026-04-05")
    _write_news_pair(news_dir=news_dir, date="2026-04-03")
    _write_news_pair(news_dir=news_dir, date="2026-04-07")
    dates: list[str] = discover_news_dates()
    assert dates == ["2026-04-03", "2026-04-05", "2026-04-07"]


def test_discover_ignores_non_date_files(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    news_dir: Path = tmp_path / "news"
    news_dir.mkdir(exist_ok=True)
    (news_dir / "not-a-date.md").write_text("hello", encoding="utf-8")
    (news_dir / "README.md").write_text("hello", encoding="utf-8")
    _write_news_pair(news_dir=news_dir, date="2026-04-05")
    dates: list[str] = discover_news_dates()
    assert dates == ["2026-04-05"]


# ---------------------------------------------------------------------------
# load_all_news
# ---------------------------------------------------------------------------


def test_load_parses_json(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    news_dir: Path = tmp_path / "news"
    _write_news_pair(
        news_dir=news_dir,
        date="2026-04-05",
        tasks_completed=7,
        tasks_created=3,
        total_cost_usd=154.0,
    )
    days: list[NewsDayInfo] = load_all_news()
    assert len(days) == 1
    day: NewsDayInfo = days[0]
    assert day.date == "2026-04-05"
    assert day.tasks_completed_count == 7
    assert day.tasks_created_count == 3
    assert day.total_cost_usd == 154.0


def test_load_handles_missing_json(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    news_dir: Path = tmp_path / "news"
    news_dir.mkdir(exist_ok=True)
    (news_dir / "2026-04-05.md").write_text("## Test\n", encoding="utf-8")
    days: list[NewsDayInfo] = load_all_news()
    assert len(days) == 1
    assert days[0].total_cost_usd is None
    assert days[0].tasks_completed_count == 0


# ---------------------------------------------------------------------------
# _format_index_page
# ---------------------------------------------------------------------------


def test_index_page_empty() -> None:
    content: str = _format_index_page(days=[])
    assert "No news files found" in content
    assert "Daily News" in content


def test_index_page_newest_first() -> None:
    days: list[NewsDayInfo] = [
        NewsDayInfo(
            date="2026-04-03",
            md_path=Path("x"),
            json_path=Path("x"),
            total_cost_usd=10.0,
            tasks_completed_count=1,
            tasks_created_count=0,
        ),
        NewsDayInfo(
            date="2026-04-05",
            md_path=Path("x"),
            json_path=Path("x"),
            total_cost_usd=200.0,
            tasks_completed_count=5,
            tasks_created_count=3,
        ),
    ]
    content: str = _format_index_page(days=days)
    pos_05: int = content.index("2026-04-05")
    pos_03: int = content.index("2026-04-03")
    assert pos_05 < pos_03, "Newest date should appear first"
    assert "$200" in content
    assert "$10" in content


def test_index_page_links_to_day_pages() -> None:
    days: list[NewsDayInfo] = [
        NewsDayInfo(
            date="2026-04-05",
            md_path=Path("x"),
            json_path=Path("x"),
            total_cost_usd=None,
            tasks_completed_count=0,
            tasks_created_count=0,
        ),
    ]
    content: str = _format_index_page(days=days)
    assert "[Apr 5, 2026](2026-04-05.md)" in content


def test_index_page_links_to_dashboard() -> None:
    content: str = _format_index_page(days=[])
    assert "[Back to dashboard](../README.md)" in content


# ---------------------------------------------------------------------------
# _format_day_page
# ---------------------------------------------------------------------------


def test_day_page_contains_content(
    tmp_path: Path,
) -> None:
    md_path: Path = tmp_path / "test.md"
    md_path.write_text("## April 5, 2026\n\nHello world.\n", encoding="utf-8")
    day: NewsDayInfo = NewsDayInfo(
        date="2026-04-05",
        md_path=md_path,
        json_path=tmp_path / "test.json",
        total_cost_usd=100.0,
        tasks_completed_count=3,
        tasks_created_count=1,
    )
    content: str = _format_day_page(
        day=day,
        prev_date=None,
        next_date=None,
    )
    assert "Hello world" in content
    assert "[Index](README.md)" in content


def test_day_page_prev_next_links(
    tmp_path: Path,
) -> None:
    md_path: Path = tmp_path / "test.md"
    md_path.write_text("## Test\n", encoding="utf-8")
    day: NewsDayInfo = NewsDayInfo(
        date="2026-04-05",
        md_path=md_path,
        json_path=tmp_path / "test.json",
        total_cost_usd=None,
        tasks_completed_count=0,
        tasks_created_count=0,
    )
    content: str = _format_day_page(
        day=day,
        prev_date="2026-04-04",
        next_date="2026-04-06",
    )
    assert "[← Apr 4, 2026](2026-04-04.md)" in content
    assert "[Apr 6, 2026 →](2026-04-06.md)" in content


def test_day_page_no_prev(
    tmp_path: Path,
) -> None:
    md_path: Path = tmp_path / "test.md"
    md_path.write_text("## Test\n", encoding="utf-8")
    day: NewsDayInfo = NewsDayInfo(
        date="2026-04-05",
        md_path=md_path,
        json_path=tmp_path / "test.json",
        total_cost_usd=None,
        tasks_completed_count=0,
        tasks_created_count=0,
    )
    content: str = _format_day_page(
        day=day,
        prev_date=None,
        next_date="2026-04-06",
    )
    assert "← " not in content
    assert "[Apr 6, 2026 →]" in content


# ---------------------------------------------------------------------------
# _rewrite_relative_paths
# ---------------------------------------------------------------------------


def test_rewrite_image_paths() -> None:
    content: str = "![chart](../tasks/t0061/results/images/cost.png)"
    result: str = _rewrite_relative_paths(content=content)
    assert "](../../tasks/t0061/results/images/cost.png)" in result


def test_rewrite_link_paths() -> None:
    content: str = "[details](../overview/tasks/task_pages/t0061.md)"
    result: str = _rewrite_relative_paths(content=content)
    assert "../../overview/tasks/task_pages/t0061.md" in result


def test_rewrite_preserves_absolute_urls() -> None:
    content: str = "[site](https://example.com/path)"
    result: str = _rewrite_relative_paths(content=content)
    assert "https://example.com/path" in result


def test_rewrite_bare_filename_gets_source_prefix() -> None:
    content: str = "[readme](README.md)"
    result: str = _rewrite_relative_paths(content=content)
    assert "(../../news/README.md)" in result


def test_day_page_rewrites_image_paths(
    tmp_path: Path,
) -> None:
    md_path: Path = tmp_path / "test.md"
    md_path.write_text(
        "## Test\n\n![chart](../tasks/t0061/results/images/cost.png)\n",
        encoding="utf-8",
    )
    day: NewsDayInfo = NewsDayInfo(
        date="2026-04-05",
        md_path=md_path,
        json_path=tmp_path / "test.json",
        total_cost_usd=None,
        tasks_completed_count=0,
        tasks_created_count=0,
    )
    content: str = _format_day_page(
        day=day,
        prev_date=None,
        next_date=None,
    )
    assert "../../tasks/t0061/results/images/cost.png" in content
    assert "](../tasks/" not in content


# ---------------------------------------------------------------------------
# materialize_news (integration)
# ---------------------------------------------------------------------------


def test_materialize_creates_files(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    news_dir: Path = tmp_path / "news"
    _write_news_pair(news_dir=news_dir, date="2026-04-05")
    _write_news_pair(news_dir=news_dir, date="2026-04-06")
    overview_news: Path = tmp_path / "overview" / "news"

    days: list[NewsDayInfo] = materialize_news()

    assert len(days) == 2
    assert (overview_news / "README.md").exists()
    assert (overview_news / "2026-04-05.md").exists()
    assert (overview_news / "2026-04-06.md").exists()


def test_materialize_empty(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    overview_news: Path = tmp_path / "overview" / "news"

    days: list[NewsDayInfo] = materialize_news()

    assert len(days) == 0
    assert (overview_news / "README.md").exists()
    index_content: str = (overview_news / "README.md").read_text(encoding="utf-8")
    assert "No news files found" in index_content
