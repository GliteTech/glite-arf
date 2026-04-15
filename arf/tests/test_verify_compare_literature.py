from pathlib import Path

import pytest

import arf.scripts.verificators.verify_compare_literature as verify_cl_module
from arf.scripts.verificators.common import paths
from arf.scripts.verificators.common.types import VerificationResult
from arf.tests.fixtures.paths import configure_repo_paths
from arf.tests.fixtures.task_builder import build_task_folder
from arf.tests.fixtures.writers import write_frontmatter_md, write_text

TASK_ID: str = "t0001_test"

VALID_BODY: str = (
    "# Comparison with Published Results\n"
    "\n"
    "## Summary\n"
    "\n"
    "Our MFS baseline implementation achieves **65.5 F1** on the Raganato ALL "
    "concatenation, exactly matching the published MFS result from Raganato2017. "
    "Per-dataset results match within **0.1 F1** for all five evaluation sets, "
    "confirming faithful reproduction of the baseline method.\n"
    "\n"
    "## Comparison Table\n"
    "\n"
    "| Method / Paper | Metric | Published Value | Our Value | Delta | Notes |\n"
    "|----------------|--------|-----------------|-----------|-------|-------|\n"
    "| MFS (Raganato2017) | F1 ALL | 65.5 | 65.5 | +0.0 | Exact match |\n"
    "| MFS (Raganato2017) | F1 SE2 | 66.8 | 66.8 | +0.0 | Exact match |\n"
    "| IMS (Raganato2017) | F1 ALL | 71.3 | 71.1 | -0.2 | Minor diff |\n"
    "\n"
    "## Methodology Differences\n"
    "\n"
    "* Both use WordNet 3.0 synsets\n"
    "* Both derive MFS counts from SemCor 3.0\n"
    "\n"
    "## Analysis\n"
    "\n"
    "The reproduction is highly faithful. Five of six comparisons yield exact "
    "matches. The only deviation is minor and within expected variance. "
    "This confirms our evaluation pipeline is correctly aligned with the "
    "Raganato framework and can serve as a reliable baseline for "
    "subsequent experiments in this project.\n"
    "\n"
    "## Limitations\n"
    "\n"
    "* Only the MFS baseline was compared\n"
    "* Per-POS breakdowns were not compared\n"
)

VALID_FRONTMATTER: dict[str, str | int] = {
    "spec_version": "1",
    "task_id": TASK_ID,
    "date_compared": "2026-04-01",
}


def _setup(*, monkeypatch: pytest.MonkeyPatch, repo_root: Path) -> None:
    configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=repo_root,
        verificator_modules=[verify_cl_module],
    )


def _codes(result: VerificationResult) -> list[str]:
    return [d.code.text for d in result.diagnostics]


def _verify(
    *,
    task_id: str = TASK_ID,
) -> VerificationResult | None:
    return verify_cl_module.verify_compare_literature(task_id=task_id)


# ---------------------------------------------------------------------------
# Optional file — missing returns None
# ---------------------------------------------------------------------------


def test_missing_file_returns_none(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    result: VerificationResult | None = _verify()
    assert result is None


# ---------------------------------------------------------------------------
# Valid compare_literature passes
# ---------------------------------------------------------------------------


def test_valid_compare_literature_passes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    write_frontmatter_md(
        path=paths.compare_literature_path(task_id=TASK_ID),
        frontmatter=VALID_FRONTMATTER,
        body=VALID_BODY,
    )
    result: VerificationResult | None = _verify()
    assert result is not None
    assert len(result.diagnostics) == 0, f"Unexpected diagnostics: {_codes(result)}"
    assert result.passed is True


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


def test_cl_e001_no_frontmatter(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    write_text(
        path=paths.compare_literature_path(task_id=TASK_ID),
        content=VALID_BODY,
    )
    result: VerificationResult | None = _verify()
    assert result is not None
    assert "CL-E001" in _codes(result=result)


@pytest.mark.parametrize(
    "missing_field",
    ["spec_version", "task_id", "date_compared"],
)
def test_cl_e002_missing_frontmatter_field(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    missing_field: str,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    frontmatter: dict[str, str | int] = dict(VALID_FRONTMATTER)
    del frontmatter[missing_field]
    write_frontmatter_md(
        path=paths.compare_literature_path(task_id=TASK_ID),
        frontmatter=frontmatter,
        body=VALID_BODY,
    )
    result: VerificationResult | None = _verify()
    assert result is not None
    assert "CL-E002" in _codes(result=result)


@pytest.mark.parametrize(
    "missing_section",
    [
        "Summary",
        "Comparison Table",
        "Methodology Differences",
        "Analysis",
        "Limitations",
    ],
)
def test_cl_e003_missing_section(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    missing_section: str,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    # Remove the section from the body
    lines: list[str] = VALID_BODY.splitlines(keepends=True)
    filtered: list[str] = []
    skip: bool = False
    for line in lines:
        if line.strip() == f"## {missing_section}":
            skip = True
            continue
        if skip and line.startswith("## "):
            skip = False
        if not skip:
            filtered.append(line)
    write_frontmatter_md(
        path=paths.compare_literature_path(task_id=TASK_ID),
        frontmatter=VALID_FRONTMATTER,
        body="".join(filtered),
    )
    result: VerificationResult | None = _verify()
    assert result is not None
    assert "CL-E003" in _codes(result=result)


def test_cl_e004_no_table_in_comparison(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    body_no_table: str = (
        "# Comparison\n\n"
        "## Summary\n\n"
        "Our results match Raganato2017 baseline at **65.5 F1**. "
        "The reproduction is faithful and confirms the pipeline works. "
        "Multiple comparison points were examined across datasets.\n\n"
        "## Comparison Table\n\n"
        "No table data available at this time.\n\n"
        "## Methodology Differences\n\n"
        "* Both use WordNet 3.0\n\n"
        "## Analysis\n\n"
        "Results are consistent with published values. "
        "The analysis confirms correctness of implementation.\n\n"
        "## Limitations\n\n"
        "* Only MFS compared\n"
    )
    write_frontmatter_md(
        path=paths.compare_literature_path(task_id=TASK_ID),
        frontmatter=VALID_FRONTMATTER,
        body=body_no_table,
    )
    result: VerificationResult | None = _verify()
    assert result is not None
    assert "CL-E004" in _codes(result=result)


def test_cl_e005_fewer_than_2_data_rows(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    body_one_row: str = (
        "# Comparison\n\n"
        "## Summary\n\n"
        "Our results match Raganato2017 baseline at **65.5 F1**. "
        "The reproduction is faithful and confirms the pipeline works. "
        "Multiple comparison points were examined across datasets.\n\n"
        "## Comparison Table\n\n"
        "| Method / Paper | Metric | Published Value | Our Value "
        "| Delta | Notes |\n"
        "|----------------|--------|-----------------|-----------|"
        "-------|-------|\n"
        "| MFS (Raganato2017) | F1 ALL | 65.5 | 65.5 | +0.0 "
        "| Exact match |\n\n"
        "## Methodology Differences\n\n"
        "* Both use WordNet 3.0\n\n"
        "## Analysis\n\n"
        "Results are consistent with published values. "
        "The analysis confirms correctness of implementation.\n\n"
        "## Limitations\n\n"
        "* Only MFS compared\n"
    )
    write_frontmatter_md(
        path=paths.compare_literature_path(task_id=TASK_ID),
        frontmatter=VALID_FRONTMATTER,
        body=body_one_row,
    )
    result: VerificationResult | None = _verify()
    assert result is not None
    assert "CL-E005" in _codes(result=result)


# ---------------------------------------------------------------------------
# Warnings
# ---------------------------------------------------------------------------


def test_cl_w001_low_word_count(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    short_body: str = (
        "# Comparison\n\n"
        "## Summary\n\nShort Raganato2017.\n\n"
        "## Comparison Table\n\n"
        "| Method / Paper | Metric | Published Value | Our Value "
        "| Delta | Notes |\n"
        "|----------------|--------|-----------------|-----------|"
        "-------|-------|\n"
        "| A (Raganato2017) | F1 | 65.5 | 65.5 | +0.0 | OK |\n"
        "| B (Smith2020) | F1 | 70.0 | 69.8 | -0.2 | OK |\n\n"
        "## Methodology Differences\n\n* Same.\n\n"
        "## Analysis\n\nOK.\n\n"
        "## Limitations\n\n* None.\n"
    )
    write_frontmatter_md(
        path=paths.compare_literature_path(task_id=TASK_ID),
        frontmatter=VALID_FRONTMATTER,
        body=short_body,
    )
    result: VerificationResult | None = _verify()
    assert result is not None
    assert "CL-W001" in _codes(result=result)


def test_cl_w002_table_rows_missing_numeric_values(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    body_no_nums: str = (
        "# Comparison\n\n"
        "## Summary\n\n"
        "Our results match Raganato2017 baseline well. "
        "The reproduction is faithful and confirms the pipeline works. "
        "Multiple comparison points were examined across datasets.\n\n"
        "## Comparison Table\n\n"
        "| Method / Paper | Metric | Published Value | Our Value "
        "| Delta | Notes |\n"
        "|----------------|--------|-----------------|-----------|"
        "-------|-------|\n"
        "| MFS (Raganato2017) | F1 | N/A | N/A | N/A | Not available |\n"
        "| IMS (Raganato2017) | F1 | N/A | N/A | N/A | Not available |\n\n"
        "## Methodology Differences\n\n"
        "* Both use WordNet 3.0\n\n"
        "## Analysis\n\n"
        "Results are consistent with published values. "
        "The analysis confirms correctness of implementation.\n\n"
        "## Limitations\n\n"
        "* Only MFS compared\n"
    )
    write_frontmatter_md(
        path=paths.compare_literature_path(task_id=TASK_ID),
        frontmatter=VALID_FRONTMATTER,
        body=body_no_nums,
    )
    result: VerificationResult | None = _verify()
    assert result is not None
    assert "CL-W002" in _codes(result=result)


def test_cl_w003_no_citation_keys(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    body_no_cites: str = (
        "# comparison with published results\n\n"
        "## Summary\n\n"
        "our baseline implementation achieves good results on the benchmark "
        "concatenation, matching the published baseline result exactly. "
        "per-dataset results match within tolerance for all five evaluation "
        "sets, confirming faithful reproduction of the baseline method.\n\n"
        "## Comparison Table\n\n"
        "| method | metric | published value | our value | delta | notes |\n"
        "|--------|--------|-----------------|-----------|-------|-------|\n"
        "| baseline | f1 | 65.5 | 65.5 | +0.0 | exact match |\n"
        "| advanced | f1 | 71.3 | 71.1 | -0.2 | minor diff |\n\n"
        "## Methodology Differences\n\n"
        "* both use the same sense inventory\n"
        "* both derive counts from the same corpus\n\n"
        "## Analysis\n\n"
        "the reproduction is highly faithful. five of six comparisons "
        "yield exact matches. the only deviation is minor.\n\n"
        "## Limitations\n\n"
        "* only the baseline was compared\n"
        "* per-category breakdowns were not compared\n"
    )
    write_frontmatter_md(
        path=paths.compare_literature_path(task_id=TASK_ID),
        frontmatter=VALID_FRONTMATTER,
        body=body_no_cites,
    )
    result: VerificationResult | None = _verify()
    assert result is not None
    assert "CL-W003" in _codes(result=result)
