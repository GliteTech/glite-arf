from pathlib import Path

import pytest

import meta.asset_types.paper.verificator as verify_paper_asset_module
import meta.asset_types.paper.verify_details as verify_paper_details_module
import meta.asset_types.paper.verify_summary as verify_paper_summary_module
from arf.scripts.verificators.common.types import VerificationResult
from arf.tests.fixtures.asset_builders.paper import (
    DEFAULT_CITATION_KEY,
    DEFAULT_PAPER_ID,
    DEFAULT_TASK_ID,
    build_paper_asset,
)
from arf.tests.fixtures.metadata_builders import build_category
from arf.tests.fixtures.paths import configure_repo_paths
from arf.tests.fixtures.task_builder import build_complete_task
from arf.tests.fixtures.writers import write_json, write_text

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_VERIFICATOR_MODULES = [
    verify_paper_asset_module,
    verify_paper_details_module,
    verify_paper_summary_module,
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _diagnostic_codes(result: VerificationResult) -> list[str]:
    return [d.code.text for d in result.diagnostics]


def _error_codes(result: VerificationResult) -> list[str]:
    return [d.code.text for d in result.errors]


def _warning_codes(result: VerificationResult) -> list[str]:
    return [d.code.text for d in result.warnings]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def repo(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> Path:
    configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=tmp_path,
        verificator_modules=_VERIFICATOR_MODULES,
    )
    build_complete_task(repo_root=tmp_path, task_id=DEFAULT_TASK_ID)
    return tmp_path


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_valid_paper_passes(repo: Path) -> None:
    build_paper_asset(repo_root=repo)
    result: VerificationResult = verify_paper_asset_module.verify_paper_asset(
        paper_id=DEFAULT_PAPER_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert result.passed is True, _diagnostic_codes(result)


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


def test_e001_details_json_missing(repo: Path) -> None:
    build_paper_asset(repo_root=repo)
    from arf.scripts.verificators.common.paths import paper_details_path

    paper_details_path(
        paper_id=DEFAULT_PAPER_ID,
        task_id=DEFAULT_TASK_ID,
    ).unlink()
    result: VerificationResult = verify_paper_asset_module.verify_paper_asset(
        paper_id=DEFAULT_PAPER_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "PA-E001" in _error_codes(result)


def test_e002_summary_missing(repo: Path) -> None:
    build_paper_asset(repo_root=repo, include_summary=False)
    result: VerificationResult = verify_paper_asset_module.verify_paper_asset(
        paper_id=DEFAULT_PAPER_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "PA-E002" in _error_codes(result)


def test_e003_files_dir_empty_when_success(repo: Path) -> None:
    build_paper_asset(repo_root=repo, include_files_dir=False)
    result: VerificationResult = verify_paper_asset_module.verify_paper_asset(
        paper_id=DEFAULT_PAPER_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "PA-E003" in _error_codes(result)


def test_e004_paper_id_mismatch(repo: Path) -> None:
    build_paper_asset(
        repo_root=repo,
        details_overrides={"paper_id": "wrong_id"},
    )
    result: VerificationResult = verify_paper_asset_module.verify_paper_asset(
        paper_id=DEFAULT_PAPER_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "PA-E004" in _error_codes(result)


def test_e005_required_field_missing(repo: Path) -> None:
    build_paper_asset(repo_root=repo)
    from arf.scripts.verificators.common.paths import paper_details_path

    details_path: Path = paper_details_path(
        paper_id=DEFAULT_PAPER_ID,
        task_id=DEFAULT_TASK_ID,
    )
    import json

    data: dict[str, object] = json.loads(
        details_path.read_text(encoding="utf-8"),
    )
    del data["title"]
    write_json(path=details_path, data=data)
    result: VerificationResult = verify_paper_asset_module.verify_paper_asset(
        paper_id=DEFAULT_PAPER_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "PA-E005" in _error_codes(result)


def test_e006_citation_key_mismatch_in_summary(repo: Path) -> None:
    build_paper_asset(repo_root=repo)
    from arf.scripts.verificators.common.paths import paper_summary_path

    summary_path: Path = paper_summary_path(
        paper_id=DEFAULT_PAPER_ID,
        task_id=DEFAULT_TASK_ID,
    )
    content: str = summary_path.read_text(encoding="utf-8")
    content = content.replace(
        f'citation_key: "{DEFAULT_CITATION_KEY}"',
        'citation_key: "WrongKey2099"',
    )
    write_text(path=summary_path, content=content)
    result: VerificationResult = verify_paper_asset_module.verify_paper_asset(
        paper_id=DEFAULT_PAPER_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "PA-E006" in _error_codes(result)


def test_e007_paper_id_mismatch_in_summary(repo: Path) -> None:
    build_paper_asset(repo_root=repo)
    from arf.scripts.verificators.common.paths import paper_summary_path

    summary_path: Path = paper_summary_path(
        paper_id=DEFAULT_PAPER_ID,
        task_id=DEFAULT_TASK_ID,
    )
    content: str = summary_path.read_text(encoding="utf-8")
    content = content.replace(
        f'paper_id: "{DEFAULT_PAPER_ID}"',
        'paper_id: "wrong_paper_id"',
    )
    write_text(path=summary_path, content=content)
    result: VerificationResult = verify_paper_asset_module.verify_paper_asset(
        paper_id=DEFAULT_PAPER_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "PA-E007" in _error_codes(result)


def test_e008_listed_file_does_not_exist(repo: Path) -> None:
    build_paper_asset(
        repo_root=repo,
        details_overrides={
            "files": ["files/nonexistent.pdf"],
        },
    )
    result: VerificationResult = verify_paper_asset_module.verify_paper_asset(
        paper_id=DEFAULT_PAPER_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "PA-E008" in _error_codes(result)


def test_e009_summary_missing_section(repo: Path) -> None:
    build_paper_asset(
        repo_root=repo,
        summary_body="# Title\n\n## Metadata\n\nSome text.\n",
    )
    result: VerificationResult = verify_paper_asset_module.verify_paper_asset(
        paper_id=DEFAULT_PAPER_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "PA-E009" in _error_codes(result)


def test_e010_invalid_venue_type(repo: Path) -> None:
    build_paper_asset(
        repo_root=repo,
        venue_type="magazine",
    )
    result: VerificationResult = verify_paper_asset_module.verify_paper_asset(
        paper_id=DEFAULT_PAPER_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "PA-E010" in _error_codes(result)


def test_e011_folder_name_has_slash() -> None:
    from meta.asset_types.paper.verify_details import (
        _check_folder_name_no_slash,
    )

    diagnostics = _check_folder_name_no_slash(
        paper_id="10.1234/test/2026",
        file_path=Path("/fake"),
    )
    codes: list[str] = [d.code.text for d in diagnostics]
    assert "PA-E011" in codes


def test_e012_summary_missing_frontmatter(repo: Path) -> None:
    build_paper_asset(repo_root=repo)
    from arf.scripts.verificators.common.paths import paper_summary_path

    summary_path: Path = paper_summary_path(
        paper_id=DEFAULT_PAPER_ID,
        task_id=DEFAULT_TASK_ID,
    )
    write_text(
        path=summary_path,
        content="# No Frontmatter\n\nJust text.\n",
    )
    result: VerificationResult = verify_paper_asset_module.verify_paper_asset(
        paper_id=DEFAULT_PAPER_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "PA-E012" in _error_codes(result)


def test_e013_no_spec_version(repo: Path) -> None:
    build_paper_asset(repo_root=repo)
    import json

    from arf.scripts.verificators.common.paths import paper_details_path

    details_path: Path = paper_details_path(
        paper_id=DEFAULT_PAPER_ID,
        task_id=DEFAULT_TASK_ID,
    )
    data: dict[str, object] = json.loads(
        details_path.read_text(encoding="utf-8"),
    )
    del data["spec_version"]
    write_json(path=details_path, data=data)
    result: VerificationResult = verify_paper_asset_module.verify_paper_asset(
        paper_id=DEFAULT_PAPER_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "PA-E013" in _error_codes(result)


def test_e014_failed_status_no_reason(repo: Path) -> None:
    build_paper_asset(
        repo_root=repo,
        download_status="failed",
        download_failure_reason=None,
    )
    result: VerificationResult = verify_paper_asset_module.verify_paper_asset(
        paper_id=DEFAULT_PAPER_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "PA-E014" in _error_codes(result)


def test_e015_invalid_download_status(repo: Path) -> None:
    build_paper_asset(
        repo_root=repo,
        download_status="pending",
    )
    result: VerificationResult = verify_paper_asset_module.verify_paper_asset(
        paper_id=DEFAULT_PAPER_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "PA-E015" in _error_codes(result)


# ---------------------------------------------------------------------------
# Warnings
# ---------------------------------------------------------------------------


def test_w001_summary_under_500_words(repo: Path) -> None:
    build_paper_asset(
        repo_root=repo,
        summary_body=(
            "# Title\n\n"
            "## Metadata\n\nShort.\n\n"
            "## Abstract\n\nShort.\n\n"
            "## Overview\n\nShort.\n\n"
            "## Architecture, Models and Methods\n\nShort.\n\n"
            "## Results\n\n"
            "* R1\n* R2\n* R3\n* R4\n* R5\n\n"
            "## Innovations\n\nShort.\n\n"
            "## Datasets\n\nShort.\n\n"
            "## Main Ideas\n\n"
            "* Idea one\n* Idea two\n* Idea three\n\n"
            "## Summary\n\n"
            "P1.\n\nP2.\n\nP3.\n\nP4.\n"
        ),
    )
    result: VerificationResult = verify_paper_asset_module.verify_paper_asset(
        paper_id=DEFAULT_PAPER_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "PA-W001" in _warning_codes(result)


def test_w002_results_fewer_than_5_bullets(repo: Path) -> None:
    build_paper_asset(
        repo_root=repo,
        summary_body=(
            "# Title\n\n"
            "## Metadata\n\nMeta.\n\n"
            "## Abstract\n\nAbstract text.\n\n"
            "## Overview\n\n" + ("Word " * 120) + "\n\n"
            "## Architecture, Models and Methods\n\n" + ("Word " * 160) + "\n\n"
            "## Results\n\n"
            "* Only one bullet\n\n"
            "## Innovations\n\nInnovation text.\n\n"
            "## Datasets\n\nDataset text.\n\n"
            "## Main Ideas\n\n"
            "* Idea one\n* Idea two\n* Idea three\n\n"
            "## Summary\n\n"
            "P1.\n\nP2.\n\nP3.\n\nP4.\n"
        ),
    )
    result: VerificationResult = verify_paper_asset_module.verify_paper_asset(
        paper_id=DEFAULT_PAPER_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "PA-W002" in _warning_codes(result)


def test_w003_main_ideas_fewer_than_3(repo: Path) -> None:
    build_paper_asset(
        repo_root=repo,
        summary_body=(
            "# Title\n\n"
            "## Metadata\n\nMeta.\n\n"
            "## Abstract\n\nAbstract text.\n\n"
            "## Overview\n\n" + ("Word " * 120) + "\n\n"
            "## Architecture, Models and Methods\n\n" + ("Word " * 160) + "\n\n"
            "## Results\n\n"
            "* R1\n* R2\n* R3\n* R4\n* R5\n\n"
            "## Innovations\n\nInnovation text.\n\n"
            "## Datasets\n\nDataset text.\n\n"
            "## Main Ideas\n\n"
            "* Only one idea\n\n"
            "## Summary\n\n"
            "P1.\n\nP2.\n\nP3.\n\nP4.\n"
        ),
    )
    result: VerificationResult = verify_paper_asset_module.verify_paper_asset(
        paper_id=DEFAULT_PAPER_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "PA-W003" in _warning_codes(result)


def test_w004_summary_not_4_paragraphs(repo: Path) -> None:
    build_paper_asset(
        repo_root=repo,
        summary_body=(
            "# Title\n\n"
            "## Metadata\n\nMeta.\n\n"
            "## Abstract\n\nAbstract text.\n\n"
            "## Overview\n\n" + ("Word " * 120) + "\n\n"
            "## Architecture, Models and Methods\n\n" + ("Word " * 160) + "\n\n"
            "## Results\n\n"
            "* R1\n* R2\n* R3\n* R4\n* R5\n\n"
            "## Innovations\n\nInnovation text.\n\n"
            "## Datasets\n\nDataset text.\n\n"
            "## Main Ideas\n\n"
            "* Idea one\n* Idea two\n* Idea three\n\n"
            "## Summary\n\n"
            "Just one paragraph here.\n"
        ),
    )
    result: VerificationResult = verify_paper_asset_module.verify_paper_asset(
        paper_id=DEFAULT_PAPER_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "PA-W004" in _warning_codes(result)


def test_w005_nonexistent_category(repo: Path) -> None:
    build_paper_asset(
        repo_root=repo,
        categories=["nonexistent-category"],
    )
    result: VerificationResult = verify_paper_asset_module.verify_paper_asset(
        paper_id=DEFAULT_PAPER_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "PA-W005" in _warning_codes(result)


def test_w005_existing_category_no_warning(repo: Path) -> None:
    build_category(repo_root=repo, category_slug="real-category")
    build_paper_asset(
        repo_root=repo,
        categories=["real-category"],
    )
    result: VerificationResult = verify_paper_asset_module.verify_paper_asset(
        paper_id=DEFAULT_PAPER_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "PA-W005" not in _warning_codes(result)


def test_w006_null_doi_without_no_doi_prefix(repo: Path) -> None:
    build_paper_asset(
        repo_root=repo,
        doi=None,
    )
    result: VerificationResult = verify_paper_asset_module.verify_paper_asset(
        paper_id=DEFAULT_PAPER_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "PA-W006" in _warning_codes(result)


def test_w007_no_author_country(repo: Path) -> None:
    build_paper_asset(
        repo_root=repo,
        details_overrides={
            "authors": [
                {
                    "name": "No Country Author",
                    "country": None,
                    "institution": "Test Uni",
                    "orcid": None,
                },
            ],
        },
    )
    result: VerificationResult = verify_paper_asset_module.verify_paper_asset(
        paper_id=DEFAULT_PAPER_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "PA-W007" in _warning_codes(result)


def test_w008_abstract_under_50_words(repo: Path) -> None:
    build_paper_asset(
        repo_root=repo,
        abstract="Very short abstract.",
    )
    result: VerificationResult = verify_paper_asset_module.verify_paper_asset(
        paper_id=DEFAULT_PAPER_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "PA-W008" in _warning_codes(result)


def test_w009_null_date_published(repo: Path) -> None:
    build_paper_asset(
        repo_root=repo,
        date_published=None,
    )
    result: VerificationResult = verify_paper_asset_module.verify_paper_asset(
        paper_id=DEFAULT_PAPER_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "PA-W009" in _warning_codes(result)


def test_w010_invalid_country_code(repo: Path) -> None:
    build_paper_asset(
        repo_root=repo,
        details_overrides={
            "authors": [
                {
                    "name": "Bad Country Author",
                    "country": "usa",
                    "institution": "Test Uni",
                    "orcid": None,
                },
            ],
        },
    )
    result: VerificationResult = verify_paper_asset_module.verify_paper_asset(
        paper_id=DEFAULT_PAPER_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "PA-W010" in _warning_codes(result)


def test_w011_invalid_date_published_format(repo: Path) -> None:
    build_paper_asset(
        repo_root=repo,
        date_published="January 2026",
    )
    result: VerificationResult = verify_paper_asset_module.verify_paper_asset(
        paper_id=DEFAULT_PAPER_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "PA-W011" in _warning_codes(result)
