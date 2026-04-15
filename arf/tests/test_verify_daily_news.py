from pathlib import Path
from unittest.mock import patch

import pytest

import arf.scripts.verificators.verify_daily_news as verify_daily_news_module
from arf.scripts.verificators.common import paths
from arf.scripts.verificators.common.types import VerificationResult
from arf.tests.fixtures.daily_news_builder import (
    DEFAULT_DATE,
    build_best_result,
    build_news_files,
    build_news_json_data,
    build_news_md_content,
    build_task_completed,
)
from arf.tests.fixtures.paths import configure_repo_paths
from arf.tests.fixtures.writers import write_json, write_text


def _setup(*, monkeypatch: pytest.MonkeyPatch, repo_root: Path) -> None:
    configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=repo_root,
        verificator_modules=[verify_daily_news_module],
    )


def _codes(result: VerificationResult) -> list[str]:
    return [d.code.text for d in result.diagnostics]


def _verify(*, date: str = DEFAULT_DATE) -> VerificationResult:
    return verify_daily_news_module.verify_daily_news(date=date)


# ---------------------------------------------------------------------------
# Valid cases
# ---------------------------------------------------------------------------


def test_valid_news_files_pass(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_news_files(repo_root=tmp_path)
    result: VerificationResult = _verify()
    assert len(result.errors) == 0, f"Unexpected errors: {_codes(result)}"
    assert result.passed is True


def test_valid_minimal_news_pass(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    json_data: dict[str, object] = build_news_json_data(
        tasks_completed=[],
        tasks_created=[],
        tasks_cancelled=[],
        total_cost_usd=0.0,
        assets_added=0,
        papers_added=0,
        infrastructure_changes=[],
        current_best_results=[],
        key_findings=[],
    )
    build_news_files(repo_root=tmp_path, json_data=json_data)
    result: VerificationResult = _verify()
    # Minimal files may trigger warnings but no errors
    assert result.passed is True


# ---------------------------------------------------------------------------
# JSON errors
# ---------------------------------------------------------------------------


def test_dn_e001_missing_json(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    write_text(
        path=paths.news_md_path(date=DEFAULT_DATE),
        content=build_news_md_content(),
    )
    result: VerificationResult = _verify()
    assert "DN-E001" in _codes(result=result)


def test_dn_e001_invalid_json(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    write_text(
        path=paths.news_json_path(date=DEFAULT_DATE),
        content="NOT VALID JSON {{{",
    )
    write_text(
        path=paths.news_md_path(date=DEFAULT_DATE),
        content=build_news_md_content(),
    )
    result: VerificationResult = _verify()
    assert "DN-E001" in _codes(result=result)


def test_dn_e002_not_object(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    write_text(
        path=paths.news_json_path(date=DEFAULT_DATE),
        content="[1, 2, 3]",
    )
    write_text(
        path=paths.news_md_path(date=DEFAULT_DATE),
        content=build_news_md_content(),
    )
    result: VerificationResult = _verify()
    assert "DN-E002" in _codes(result=result)


def test_dn_e003_missing_spec_version(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    json_data: dict[str, object] = build_news_json_data()
    del json_data["spec_version"]
    build_news_files(repo_root=tmp_path, json_data=json_data)
    result: VerificationResult = _verify()
    assert "DN-E003" in _codes(result=result)


def test_dn_e004_missing_date(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    json_data: dict[str, object] = build_news_json_data()
    del json_data["date"]
    build_news_files(repo_root=tmp_path, json_data=json_data)
    result: VerificationResult = _verify()
    assert "DN-E004" in _codes(result=result)


def test_dn_e005_date_mismatch(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    json_data: dict[str, object] = build_news_json_data(
        overrides={"date": "2026-01-01"},
    )
    build_news_files(repo_root=tmp_path, json_data=json_data)
    result: VerificationResult = _verify()
    assert "DN-E005" in _codes(result=result)


def test_dn_e005_invalid_date_format(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    json_data: dict[str, object] = build_news_json_data(
        overrides={"date": "not-a-date"},
    )
    build_news_files(repo_root=tmp_path, json_data=json_data)
    result: VerificationResult = _verify()
    assert "DN-E005" in _codes(result=result)


def test_dn_e006_missing_required_field(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    json_data: dict[str, object] = build_news_json_data()
    del json_data["tasks_completed"]
    build_news_files(repo_root=tmp_path, json_data=json_data)
    result: VerificationResult = _verify()
    assert "DN-E006" in _codes(result=result)


def test_dn_e007_wrong_type(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    json_data: dict[str, object] = build_news_json_data(
        overrides={"tasks_completed": "not a list"},
    )
    build_news_files(repo_root=tmp_path, json_data=json_data)
    result: VerificationResult = _verify()
    assert "DN-E007" in _codes(result=result)


def test_dn_e008_task_completed_missing_subfield(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    bad_item: dict[str, object] = build_task_completed()
    del bad_item["key_finding"]
    json_data: dict[str, object] = build_news_json_data(
        tasks_completed=[bad_item],
    )
    build_news_files(repo_root=tmp_path, json_data=json_data)
    result: VerificationResult = _verify()
    assert "DN-E008" in _codes(result=result)


def test_dn_e009_task_created_missing_subfield(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    bad_item: dict[str, object] = {"task_id": "t0001_test", "name": "Test"}
    json_data: dict[str, object] = build_news_json_data(
        tasks_created=[bad_item],
    )
    build_news_files(repo_root=tmp_path, json_data=json_data)
    result: VerificationResult = _verify()
    assert "DN-E009" in _codes(result=result)


def test_dn_e010_task_cancelled_missing_subfield(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    bad_item: dict[str, object] = {"task_id": "t0001_test"}
    json_data: dict[str, object] = build_news_json_data(
        tasks_cancelled=[bad_item],
    )
    build_news_files(repo_root=tmp_path, json_data=json_data)
    result: VerificationResult = _verify()
    assert "DN-E010" in _codes(result=result)


def test_dn_e016_total_cost_not_number(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    json_data: dict[str, object] = build_news_json_data(
        overrides={"total_cost_usd": "not a number"},
    )
    build_news_files(repo_root=tmp_path, json_data=json_data)
    result: VerificationResult = _verify()
    assert "DN-E016" in _codes(result=result)


def test_dn_e017_best_result_missing_subfield(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    bad_item: dict[str, object] = build_best_result()
    del bad_item["f1"]
    json_data: dict[str, object] = build_news_json_data(
        current_best_results=[bad_item],
    )
    build_news_files(repo_root=tmp_path, json_data=json_data)
    result: VerificationResult = _verify()
    assert "DN-E017" in _codes(result=result)


# ---------------------------------------------------------------------------
# Markdown errors
# ---------------------------------------------------------------------------


def test_dn_e011_missing_md(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    write_json(
        path=paths.news_json_path(date=DEFAULT_DATE),
        data=build_news_json_data(),
    )
    result: VerificationResult = _verify()
    assert "DN-E011" in _codes(result=result)


def test_dn_e012_md_starts_with_h1(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    md_content: str = build_news_md_content(start_with_h1=True)
    build_news_files(repo_root=tmp_path, md_content=md_content)
    result: VerificationResult = _verify()
    assert "DN-E012" in _codes(result=result)


def test_dn_e013_md_wrong_date_heading(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    md_content: str = build_news_md_content(wrong_date_heading="January 1, 2026")
    build_news_files(repo_root=tmp_path, md_content=md_content)
    result: VerificationResult = _verify()
    assert "DN-E013" in _codes(result=result)


def test_dn_e013_md_unrecognized_date_format(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    md_content: str = build_news_md_content(wrong_date_heading="not a date")
    build_news_files(repo_root=tmp_path, md_content=md_content)
    result: VerificationResult = _verify()
    assert "DN-E013" in _codes(result=result)


def test_dn_e014_md_missing_where_we_stand(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    md_content: str = build_news_md_content(include_where_we_stand=False)
    build_news_files(repo_root=tmp_path, md_content=md_content)
    result: VerificationResult = _verify()
    assert "DN-E014" in _codes(result=result)


def test_dn_e015_md_missing_costs(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    md_content: str = build_news_md_content(include_costs=False)
    build_news_files(repo_root=tmp_path, md_content=md_content)
    result: VerificationResult = _verify()
    assert "DN-E015" in _codes(result=result)


# ---------------------------------------------------------------------------
# Warnings
# ---------------------------------------------------------------------------


def test_dn_w001_no_findings_heading(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    md_content: str = build_news_md_content(include_findings=False)
    build_news_files(repo_root=tmp_path, md_content=md_content)
    result: VerificationResult = _verify()
    assert "DN-W001" in _codes(result=result)


def test_dn_w002_empty_key_findings(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    json_data: dict[str, object] = build_news_json_data(key_findings=[])
    build_news_files(repo_root=tmp_path, json_data=json_data)
    result: VerificationResult = _verify()
    assert "DN-W002" in _codes(result=result)


def test_dn_w003_zero_cost(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    json_data: dict[str, object] = build_news_json_data(total_cost_usd=0.0)
    build_news_files(repo_root=tmp_path, json_data=json_data)
    result: VerificationResult = _verify()
    assert "DN-W003" in _codes(result=result)


def test_dn_w004_md_too_short(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    md_content: str = (
        "## April 5, 2026\n\nShort.\n\n## Where we stand\n\n| x |\n\n## Costs\n\n| x |\n"
    )
    build_news_files(repo_root=tmp_path, md_content=md_content)
    result: VerificationResult = _verify()
    assert "DN-W004" in _codes(result=result)


def test_dn_w005_md_too_long(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    padding: str = "x " * 8000
    md_content: str = (
        f"## April 5, 2026\n\n{padding}\n\n"
        "## Three things we learned\n\nStuff.\n\n"
        "## Where we stand\n\n| x |\n\n## Costs\n\n| x |\n"
    )
    build_news_files(repo_root=tmp_path, md_content=md_content)
    result: VerificationResult = _verify()
    assert "DN-W005" in _codes(result=result)


def test_dn_w006_no_images(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    md_content: str = build_news_md_content(include_images=False)
    build_news_files(repo_root=tmp_path, md_content=md_content)
    result: VerificationResult = _verify()
    assert "DN-W006" in _codes(result=result)


def test_dn_w007_few_links(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    md_content: str = build_news_md_content(include_links=False)
    build_news_files(repo_root=tmp_path, md_content=md_content)
    result: VerificationResult = _verify()
    assert "DN-W007" in _codes(result=result)


def test_dn_w008_no_papers_section(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    md_content: str = build_news_md_content(include_papers=False)
    build_news_files(repo_root=tmp_path, md_content=md_content)
    result: VerificationResult = _verify()
    assert "DN-W008" in _codes(result=result)


def test_dn_w009_no_answers_section(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    md_content: str = build_news_md_content(include_answers=False)
    build_news_files(repo_root=tmp_path, md_content=md_content)
    result: VerificationResult = _verify()
    assert "DN-W009" in _codes(result=result)


# ---------------------------------------------------------------------------
# Git checks
# ---------------------------------------------------------------------------


def _mock_run_git_uncommitted(*, args: list[str]) -> str | None:
    if args[0] == "status":
        return "?? news/2026-04-05.json"
    return ""


def _mock_run_git_committed_not_pushed(*, args: list[str]) -> str | None:
    if args[0] == "status":
        return ""
    if args[0] == "rev-parse":
        if len(args) > 1 and args[1] == "--abbrev-ref":
            if len(args) > 2 and args[2] == "HEAD":
                return "main"
            return "origin/main"
        if len(args) > 1 and args[1] == "HEAD":
            return "local_sha"
        return "remote_sha"
    if args[0] == "cat-file":
        return None
    return ""


def _mock_run_git_all_pushed(*, args: list[str]) -> str | None:
    if args[0] == "status":
        return ""
    if args[0] == "rev-parse":
        return "same_sha"
    return ""


def test_dn_e018_not_committed(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_news_files(repo_root=tmp_path)
    with patch.object(
        verify_daily_news_module,
        "_run_git",
        side_effect=_mock_run_git_uncommitted,
    ):
        result: VerificationResult = _verify()
    assert "DN-E018" in _codes(result=result)


def test_dn_e019_not_pushed(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_news_files(repo_root=tmp_path)
    with patch.object(
        verify_daily_news_module,
        "_run_git",
        side_effect=_mock_run_git_committed_not_pushed,
    ):
        result: VerificationResult = _verify()
    assert "DN-E019" in _codes(result=result)


def test_valid_committed_and_pushed(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_news_files(repo_root=tmp_path)
    with patch.object(
        verify_daily_news_module,
        "_run_git",
        side_effect=_mock_run_git_all_pushed,
    ):
        result: VerificationResult = _verify()
    assert "DN-E018" not in _codes(result=result)
    assert "DN-E019" not in _codes(result=result)
