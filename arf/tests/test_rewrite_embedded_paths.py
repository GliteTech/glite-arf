from arf.scripts.overview.common import rewrite_embedded_paths

# ---------------------------------------------------------------------------
# Basic path rewriting for task results embedded in overview pages
# ---------------------------------------------------------------------------


def test_rewrites_relative_image_path() -> None:
    content: str = "![chart](images/cost_vs_f1.png)"
    result: str = rewrite_embedded_paths(
        content=content,
        source_dir="tasks/t0061/results",
        target_rel="../../../",
    )
    assert "](../../../tasks/t0061/results/images/cost_vs_f1.png)" in result


def test_rewrites_dotslash_path() -> None:
    content: str = "![chart](./images/chart.png)"
    result: str = rewrite_embedded_paths(
        content=content,
        source_dir="tasks/t0061/results",
        target_rel="../../../",
    )
    assert "](../../../tasks/t0061/results/images/chart.png)" in result


def test_rewrites_parent_relative_path() -> None:
    content: str = "[link](../assets/paper/doi/summary.md)"
    result: str = rewrite_embedded_paths(
        content=content,
        source_dir="tasks/t0061/results",
        target_rel="../../../",
    )
    assert "](../../../tasks/t0061/assets/paper/doi/summary.md)" in result


def test_preserves_absolute_urls() -> None:
    content: str = "[site](https://example.com/path)"
    result: str = rewrite_embedded_paths(
        content=content,
        source_dir="tasks/t0061/results",
        target_rel="../../../",
    )
    assert "(https://example.com/path)" in result


def test_preserves_anchor_links() -> None:
    content: str = "[section](#methodology)"
    result: str = rewrite_embedded_paths(
        content=content,
        source_dir="tasks/t0061/results",
        target_rel="../../../",
    )
    assert "(#methodology)" in result


def test_preserves_absolute_paths() -> None:
    content: str = "[file](/absolute/path.md)"
    result: str = rewrite_embedded_paths(
        content=content,
        source_dir="tasks/t0061/results",
        target_rel="../../../",
    )
    assert "(/absolute/path.md)" in result


# ---------------------------------------------------------------------------
# News-specific: paths relative from news/ directory
# ---------------------------------------------------------------------------


def test_news_parent_relative() -> None:
    content: str = "![chart](../tasks/t0061/results/images/cost.png)"
    result: str = rewrite_embedded_paths(
        content=content,
        source_dir="news",
        target_rel="../../",
    )
    assert "](../../tasks/t0061/results/images/cost.png)" in result


def test_news_overview_link() -> None:
    content: str = "[metric](../overview/metrics-results/f1_all.md)"
    result: str = rewrite_embedded_paths(
        content=content,
        source_dir="news",
        target_rel="../../",
    )
    assert "](../../overview/metrics-results/f1_all.md)" in result


# ---------------------------------------------------------------------------
# Multiple links in one line
# ---------------------------------------------------------------------------


def test_multiple_links_on_one_line() -> None:
    content: str = (
        "| [BEM](../overview/tasks/t0065.md) | [**79.4**](../overview/metrics-results/f1_all.md) |"
    )
    result: str = rewrite_embedded_paths(
        content=content,
        source_dir="news",
        target_rel="../../",
    )
    assert "](../../overview/tasks/t0065.md)" in result
    assert "](../../overview/metrics-results/f1_all.md)" in result


# ---------------------------------------------------------------------------
# Plain text without links is unchanged
# ---------------------------------------------------------------------------


def test_plain_text_unchanged() -> None:
    content: str = "This is plain text with no links."
    result: str = rewrite_embedded_paths(
        content=content,
        source_dir="tasks/t0061/results",
        target_rel="../../../",
    )
    assert result == content
