import json
from pathlib import Path

import pytest

import meta.asset_types.dataset.verificator as verify_dataset_asset_module
import meta.asset_types.dataset.verify_description as verify_dataset_description_module
import meta.asset_types.dataset.verify_details as verify_dataset_details_module
from arf.scripts.verificators.common.types import VerificationResult
from arf.tests.fixtures.asset_builders.dataset import (
    DEFAULT_DATASET_ID,
    DEFAULT_TASK_ID,
    build_dataset_asset,
)
from arf.tests.fixtures.paths import configure_repo_paths
from arf.tests.fixtures.task_builder import build_complete_task
from arf.tests.fixtures.writers import write_json, write_text

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_VERIFICATOR_MODULES = [
    verify_dataset_asset_module,
    verify_dataset_details_module,
    verify_dataset_description_module,
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


def test_valid_dataset_passes(repo: Path) -> None:
    build_dataset_asset(repo_root=repo)
    result: VerificationResult = verify_dataset_asset_module.verify_dataset_asset(
        dataset_id=DEFAULT_DATASET_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert result.passed is True, _diagnostic_codes(result)


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


def test_e001_details_json_missing(repo: Path) -> None:
    build_dataset_asset(repo_root=repo)
    from arf.scripts.verificators.common.paths import dataset_details_path

    dataset_details_path(
        dataset_id=DEFAULT_DATASET_ID,
        task_id=DEFAULT_TASK_ID,
    ).unlink()
    result: VerificationResult = verify_dataset_asset_module.verify_dataset_asset(
        dataset_id=DEFAULT_DATASET_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "DA-E001" in _error_codes(result)


def test_e002_description_missing(repo: Path) -> None:
    build_dataset_asset(
        repo_root=repo,
        include_description=False,
    )
    result: VerificationResult = verify_dataset_asset_module.verify_dataset_asset(
        dataset_id=DEFAULT_DATASET_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "DA-E002" in _error_codes(result)


def test_e003_files_dir_empty(repo: Path) -> None:
    build_dataset_asset(
        repo_root=repo,
        include_files_dir=False,
    )
    result: VerificationResult = verify_dataset_asset_module.verify_dataset_asset(
        dataset_id=DEFAULT_DATASET_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "DA-E003" in _error_codes(result)


def test_e004_dataset_id_mismatch(repo: Path) -> None:
    build_dataset_asset(
        repo_root=repo,
        details_overrides={"dataset_id": "wrong-id"},
    )
    result: VerificationResult = verify_dataset_asset_module.verify_dataset_asset(
        dataset_id=DEFAULT_DATASET_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "DA-E004" in _error_codes(result)


def test_e005_required_field_missing(repo: Path) -> None:
    build_dataset_asset(repo_root=repo)
    from arf.scripts.verificators.common.paths import dataset_details_path

    details_path: Path = dataset_details_path(
        dataset_id=DEFAULT_DATASET_ID,
        task_id=DEFAULT_TASK_ID,
    )
    data: dict[str, object] = json.loads(
        details_path.read_text(encoding="utf-8"),
    )
    del data["name"]
    write_json(path=details_path, data=data)
    result: VerificationResult = verify_dataset_asset_module.verify_dataset_asset(
        dataset_id=DEFAULT_DATASET_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "DA-E005" in _error_codes(result)


def test_e007_frontmatter_id_mismatch(repo: Path) -> None:
    build_dataset_asset(repo_root=repo)
    from arf.scripts.verificators.common.paths import dataset_description_path

    desc_path: Path = dataset_description_path(
        dataset_id=DEFAULT_DATASET_ID,
        task_id=DEFAULT_TASK_ID,
    )
    content: str = desc_path.read_text(encoding="utf-8")
    content = content.replace(
        f'dataset_id: "{DEFAULT_DATASET_ID}"',
        'dataset_id: "wrong-id"',
    )
    write_text(path=desc_path, content=content)
    result: VerificationResult = verify_dataset_asset_module.verify_dataset_asset(
        dataset_id=DEFAULT_DATASET_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "DA-E007" in _error_codes(result)


def test_e008_listed_file_does_not_exist(repo: Path) -> None:
    build_dataset_asset(
        repo_root=repo,
        details_overrides={
            "files": [
                {
                    "path": "files/nonexistent.csv",
                    "description": "Missing",
                    "format": "csv",
                },
            ],
        },
    )
    result: VerificationResult = verify_dataset_asset_module.verify_dataset_asset(
        dataset_id=DEFAULT_DATASET_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "DA-E008" in _error_codes(result)


def test_e009_description_missing_section(repo: Path) -> None:
    build_dataset_asset(
        repo_root=repo,
        description_body="# Title\n\n## Metadata\n\nSome text.\n",
    )
    result: VerificationResult = verify_dataset_asset_module.verify_dataset_asset(
        dataset_id=DEFAULT_DATASET_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "DA-E009" in _error_codes(result)


def test_e010_invalid_access_kind(repo: Path) -> None:
    build_dataset_asset(
        repo_root=repo,
        access_kind="secret",
    )
    result: VerificationResult = verify_dataset_asset_module.verify_dataset_asset(
        dataset_id=DEFAULT_DATASET_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "DA-E010" in _error_codes(result)


def test_e011_folder_name_invalid(repo: Path) -> None:
    bad_id: str = "BAD_NAME"
    build_dataset_asset(
        repo_root=repo,
        dataset_id=bad_id,
    )
    result: VerificationResult = verify_dataset_asset_module.verify_dataset_asset(
        dataset_id=bad_id,
        task_id=DEFAULT_TASK_ID,
    )
    assert "DA-E011" in _error_codes(result)


def test_e012_description_missing_frontmatter(repo: Path) -> None:
    build_dataset_asset(repo_root=repo)
    from arf.scripts.verificators.common.paths import dataset_description_path

    desc_path: Path = dataset_description_path(
        dataset_id=DEFAULT_DATASET_ID,
        task_id=DEFAULT_TASK_ID,
    )
    write_text(
        path=desc_path,
        content="# No Frontmatter\n\nJust text.\n",
    )
    result: VerificationResult = verify_dataset_asset_module.verify_dataset_asset(
        dataset_id=DEFAULT_DATASET_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "DA-E012" in _error_codes(result)


def test_e013_no_spec_version(repo: Path) -> None:
    build_dataset_asset(repo_root=repo)
    from arf.scripts.verificators.common.paths import dataset_details_path

    details_path: Path = dataset_details_path(
        dataset_id=DEFAULT_DATASET_ID,
        task_id=DEFAULT_TASK_ID,
    )
    data: dict[str, object] = json.loads(
        details_path.read_text(encoding="utf-8"),
    )
    del data["spec_version"]
    write_json(path=details_path, data=data)
    result: VerificationResult = verify_dataset_asset_module.verify_dataset_asset(
        dataset_id=DEFAULT_DATASET_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "DA-E013" in _error_codes(result)


def test_e016_invalid_file_entry(repo: Path) -> None:
    build_dataset_asset(
        repo_root=repo,
        details_overrides={
            "files": ["not-an-object"],
        },
    )
    result: VerificationResult = verify_dataset_asset_module.verify_dataset_asset(
        dataset_id=DEFAULT_DATASET_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "DA-E016" in _error_codes(result)


# ---------------------------------------------------------------------------
# Warnings
# ---------------------------------------------------------------------------


def test_w001_description_under_400_words(repo: Path) -> None:
    build_dataset_asset(
        repo_root=repo,
        description_body=(
            "# Title\n\n"
            "## Metadata\n\nMeta.\n\n"
            "## Overview\n\n" + ("Word " * 90) + "\n\n"
            "## Content & Annotation\n\nShort.\n\n"
            "## Statistics\n\nShort.\n\n"
            "## Usage Notes\n\nShort.\n\n"
            "## Main Ideas\n\n"
            "* Idea one\n* Idea two\n* Idea three\n\n"
            "## Summary\n\n"
            "P1.\n\nP2.\n"
        ),
    )
    result: VerificationResult = verify_dataset_asset_module.verify_dataset_asset(
        dataset_id=DEFAULT_DATASET_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "DA-W001" in _warning_codes(result)


def test_w003_main_ideas_fewer_than_3(repo: Path) -> None:
    build_dataset_asset(
        repo_root=repo,
        description_body=(
            "# Title\n\n"
            "## Metadata\n\nMeta.\n\n"
            "## Overview\n\n" + ("Word " * 90) + "\n\n"
            "## Content & Annotation\n\n" + ("Word " * 80) + "\n\n"
            "## Statistics\n\n" + ("Word " * 40) + "\n\n"
            "## Usage Notes\n\n" + ("Word " * 40) + "\n\n"
            "## Main Ideas\n\n"
            "* Only one idea\n\n"
            "## Summary\n\n"
            "P1.\n\nP2.\n"
        ),
    )
    result: VerificationResult = verify_dataset_asset_module.verify_dataset_asset(
        dataset_id=DEFAULT_DATASET_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "DA-W003" in _warning_codes(result)


def test_w004_summary_not_2_or_3_paragraphs(repo: Path) -> None:
    build_dataset_asset(
        repo_root=repo,
        description_body=(
            "# Title\n\n"
            "## Metadata\n\nMeta.\n\n"
            "## Overview\n\n" + ("Word " * 90) + "\n\n"
            "## Content & Annotation\n\n" + ("Word " * 80) + "\n\n"
            "## Statistics\n\n" + ("Word " * 40) + "\n\n"
            "## Usage Notes\n\n" + ("Word " * 40) + "\n\n"
            "## Main Ideas\n\n"
            "* Idea one\n* Idea two\n* Idea three\n\n"
            "## Summary\n\n"
            "Just one paragraph.\n"
        ),
    )
    result: VerificationResult = verify_dataset_asset_module.verify_dataset_asset(
        dataset_id=DEFAULT_DATASET_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "DA-W004" in _warning_codes(result)


def test_w005_nonexistent_category(repo: Path) -> None:
    build_dataset_asset(
        repo_root=repo,
        categories=["nonexistent-category"],
    )
    result: VerificationResult = verify_dataset_asset_module.verify_dataset_asset(
        dataset_id=DEFAULT_DATASET_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "DA-W005" in _warning_codes(result)


def test_w007_no_author_country(repo: Path) -> None:
    build_dataset_asset(
        repo_root=repo,
        details_overrides={
            "authors": [
                {
                    "name": "No Country Author",
                    "country": None,
                    "institution": "Test Uni",
                },
            ],
        },
    )
    result: VerificationResult = verify_dataset_asset_module.verify_dataset_asset(
        dataset_id=DEFAULT_DATASET_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "DA-W007" in _warning_codes(result)


def test_w008_short_description_under_10_words(repo: Path) -> None:
    build_dataset_asset(
        repo_root=repo,
        short_description="Too short.",
    )
    result: VerificationResult = verify_dataset_asset_module.verify_dataset_asset(
        dataset_id=DEFAULT_DATASET_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "DA-W008" in _warning_codes(result)


def test_w009_null_date_published(repo: Path) -> None:
    build_dataset_asset(
        repo_root=repo,
        date_published=None,
    )
    result: VerificationResult = verify_dataset_asset_module.verify_dataset_asset(
        dataset_id=DEFAULT_DATASET_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "DA-W009" in _warning_codes(result)


def test_w010_invalid_country_code(repo: Path) -> None:
    build_dataset_asset(
        repo_root=repo,
        details_overrides={
            "authors": [
                {
                    "name": "Bad Country Author",
                    "country": "usa",
                    "institution": "Test Uni",
                },
            ],
        },
    )
    result: VerificationResult = verify_dataset_asset_module.verify_dataset_asset(
        dataset_id=DEFAULT_DATASET_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "DA-W010" in _warning_codes(result)


def test_w011_invalid_date_published_format(repo: Path) -> None:
    build_dataset_asset(
        repo_root=repo,
        date_published="January 2026",
    )
    result: VerificationResult = verify_dataset_asset_module.verify_dataset_asset(
        dataset_id=DEFAULT_DATASET_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "DA-W011" in _warning_codes(result)


def test_w012_empty_size_description(repo: Path) -> None:
    build_dataset_asset(
        repo_root=repo,
        size_description="",
    )
    result: VerificationResult = verify_dataset_asset_module.verify_dataset_asset(
        dataset_id=DEFAULT_DATASET_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "DA-W012" in _warning_codes(result)


def test_w013_overview_under_80_words(repo: Path) -> None:
    build_dataset_asset(
        repo_root=repo,
        description_body=(
            "# Title\n\n"
            "## Metadata\n\nMeta.\n\n"
            "## Overview\n\nShort overview.\n\n"
            "## Content & Annotation\n\n" + ("Word " * 80) + "\n\n"
            "## Statistics\n\n" + ("Word " * 40) + "\n\n"
            "## Usage Notes\n\n" + ("Word " * 40) + "\n\n"
            "## Main Ideas\n\n"
            "* Idea one\n* Idea two\n* Idea three\n\n"
            "## Summary\n\n"
            "P1.\n\nP2.\n"
        ),
    )
    result: VerificationResult = verify_dataset_asset_module.verify_dataset_asset(
        dataset_id=DEFAULT_DATASET_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "DA-W013" in _warning_codes(result)
