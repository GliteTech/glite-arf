import json
from pathlib import Path

import pytest

import meta.asset_types.model.verificator as verify_model_asset_module
import meta.asset_types.model.verify_description as verify_model_description_module
import meta.asset_types.model.verify_details as verify_model_details_module
from arf.scripts.verificators.common.types import VerificationResult
from arf.tests.fixtures.asset_builders.model import (
    DEFAULT_MODEL_ID,
    DEFAULT_TASK_ID,
    build_model_asset,
)
from arf.tests.fixtures.paths import configure_repo_paths
from arf.tests.fixtures.task_builder import build_complete_task
from arf.tests.fixtures.writers import write_json, write_text

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_VERIFICATOR_MODULES = [
    verify_model_asset_module,
    verify_model_details_module,
    verify_model_description_module,
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


def test_valid_model_passes(repo: Path) -> None:
    build_model_asset(repo_root=repo)
    result: VerificationResult = verify_model_asset_module.verify_model_asset(
        model_id=DEFAULT_MODEL_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert result.passed is True, _diagnostic_codes(result)


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


def test_e001_details_json_missing(repo: Path) -> None:
    build_model_asset(repo_root=repo)
    from arf.scripts.verificators.common.paths import model_details_path

    model_details_path(
        model_id=DEFAULT_MODEL_ID,
        task_id=DEFAULT_TASK_ID,
    ).unlink()
    result: VerificationResult = verify_model_asset_module.verify_model_asset(
        model_id=DEFAULT_MODEL_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "MA-E001" in _error_codes(result)


def test_e002_description_missing(repo: Path) -> None:
    build_model_asset(
        repo_root=repo,
        include_description=False,
    )
    result: VerificationResult = verify_model_asset_module.verify_model_asset(
        model_id=DEFAULT_MODEL_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "MA-E002" in _error_codes(result)


def test_e003_files_dir_empty(repo: Path) -> None:
    build_model_asset(
        repo_root=repo,
        include_files_dir=False,
    )
    result: VerificationResult = verify_model_asset_module.verify_model_asset(
        model_id=DEFAULT_MODEL_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "MA-E003" in _error_codes(result)


def test_e004_model_id_mismatch(repo: Path) -> None:
    build_model_asset(
        repo_root=repo,
        details_overrides={"model_id": "wrong-id"},
    )
    result: VerificationResult = verify_model_asset_module.verify_model_asset(
        model_id=DEFAULT_MODEL_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "MA-E004" in _error_codes(result)


def test_e005_required_field_missing(repo: Path) -> None:
    build_model_asset(repo_root=repo)
    from arf.scripts.verificators.common.paths import model_details_path

    details_path: Path = model_details_path(
        model_id=DEFAULT_MODEL_ID,
        task_id=DEFAULT_TASK_ID,
    )
    data: dict[str, object] = json.loads(
        details_path.read_text(encoding="utf-8"),
    )
    del data["name"]
    write_json(path=details_path, data=data)
    result: VerificationResult = verify_model_asset_module.verify_model_asset(
        model_id=DEFAULT_MODEL_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "MA-E005" in _error_codes(result)


def test_e007_frontmatter_id_mismatch(repo: Path) -> None:
    build_model_asset(repo_root=repo)
    from arf.scripts.verificators.common.paths import model_description_path

    desc_path: Path = model_description_path(
        model_id=DEFAULT_MODEL_ID,
        task_id=DEFAULT_TASK_ID,
    )
    content: str = desc_path.read_text(encoding="utf-8")
    content = content.replace(
        f'model_id: "{DEFAULT_MODEL_ID}"',
        'model_id: "wrong-model-id"',
    )
    write_text(path=desc_path, content=content)
    result: VerificationResult = verify_model_asset_module.verify_model_asset(
        model_id=DEFAULT_MODEL_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "MA-E007" in _error_codes(result)


def test_e008_listed_file_does_not_exist(repo: Path) -> None:
    build_model_asset(
        repo_root=repo,
        details_overrides={
            "files": [
                {
                    "path": "files/nonexistent.pt",
                    "description": "Missing",
                    "format": "pt",
                },
            ],
        },
    )
    result: VerificationResult = verify_model_asset_module.verify_model_asset(
        model_id=DEFAULT_MODEL_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "MA-E008" in _error_codes(result)


def test_e009_description_missing_section(repo: Path) -> None:
    build_model_asset(
        repo_root=repo,
        description_body="# Title\n\n## Metadata\n\nSome text.\n",
    )
    result: VerificationResult = verify_model_asset_module.verify_model_asset(
        model_id=DEFAULT_MODEL_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "MA-E009" in _error_codes(result)


def test_e010_invalid_framework(repo: Path) -> None:
    build_model_asset(
        repo_root=repo,
        framework="caffe",
    )
    result: VerificationResult = verify_model_asset_module.verify_model_asset(
        model_id=DEFAULT_MODEL_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "MA-E010" in _error_codes(result)


def test_e011_folder_name_invalid(repo: Path) -> None:
    bad_id: str = "BAD_MODEL"
    build_model_asset(
        repo_root=repo,
        model_id=bad_id,
    )
    result: VerificationResult = verify_model_asset_module.verify_model_asset(
        model_id=bad_id,
        task_id=DEFAULT_TASK_ID,
    )
    assert "MA-E011" in _error_codes(result)


def test_e012_description_missing_frontmatter(repo: Path) -> None:
    build_model_asset(repo_root=repo)
    from arf.scripts.verificators.common.paths import model_description_path

    desc_path: Path = model_description_path(
        model_id=DEFAULT_MODEL_ID,
        task_id=DEFAULT_TASK_ID,
    )
    write_text(
        path=desc_path,
        content="# No Frontmatter\n\nJust text.\n",
    )
    result: VerificationResult = verify_model_asset_module.verify_model_asset(
        model_id=DEFAULT_MODEL_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "MA-E012" in _error_codes(result)


def test_e013_no_spec_version(repo: Path) -> None:
    build_model_asset(repo_root=repo)
    from arf.scripts.verificators.common.paths import model_details_path

    details_path: Path = model_details_path(
        model_id=DEFAULT_MODEL_ID,
        task_id=DEFAULT_TASK_ID,
    )
    data: dict[str, object] = json.loads(
        details_path.read_text(encoding="utf-8"),
    )
    del data["spec_version"]
    write_json(path=details_path, data=data)
    result: VerificationResult = verify_model_asset_module.verify_model_asset(
        model_id=DEFAULT_MODEL_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "MA-E013" in _error_codes(result)


def test_e016_invalid_file_entry(repo: Path) -> None:
    build_model_asset(
        repo_root=repo,
        details_overrides={
            "files": ["not-an-object"],
        },
    )
    result: VerificationResult = verify_model_asset_module.verify_model_asset(
        model_id=DEFAULT_MODEL_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "MA-E016" in _error_codes(result)


# ---------------------------------------------------------------------------
# Warnings
# ---------------------------------------------------------------------------


def test_w001_description_under_400_words(repo: Path) -> None:
    build_model_asset(
        repo_root=repo,
        description_body=(
            "# Title\n\n"
            "## Metadata\n\nMeta.\n\n"
            "## Overview\n\n" + ("Word " * 90) + "\n\n"
            "## Architecture\n\nShort.\n\n"
            "## Training\n\nShort.\n\n"
            "## Evaluation\n\nShort.\n\n"
            "## Usage Notes\n\nShort.\n\n"
            "## Main Ideas\n\n"
            "* Idea one\n* Idea two\n* Idea three\n\n"
            "## Summary\n\n"
            "P1.\n\nP2.\n"
        ),
    )
    result: VerificationResult = verify_model_asset_module.verify_model_asset(
        model_id=DEFAULT_MODEL_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "MA-W001" in _warning_codes(result)


def test_w003_main_ideas_fewer_than_3(repo: Path) -> None:
    build_model_asset(
        repo_root=repo,
        description_body=(
            "# Title\n\n"
            "## Metadata\n\nMeta.\n\n"
            "## Overview\n\n" + ("Word " * 90) + "\n\n"
            "## Architecture\n\n" + ("Word " * 60) + "\n\n"
            "## Training\n\n" + ("Word " * 60) + "\n\n"
            "## Evaluation\n\n" + ("Word " * 40) + "\n\n"
            "## Usage Notes\n\n" + ("Word " * 20) + "\n\n"
            "## Main Ideas\n\n"
            "* Only one idea\n\n"
            "## Summary\n\n"
            "P1.\n\nP2.\n"
        ),
    )
    result: VerificationResult = verify_model_asset_module.verify_model_asset(
        model_id=DEFAULT_MODEL_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "MA-W003" in _warning_codes(result)


def test_w004_summary_not_2_or_3_paragraphs(repo: Path) -> None:
    build_model_asset(
        repo_root=repo,
        description_body=(
            "# Title\n\n"
            "## Metadata\n\nMeta.\n\n"
            "## Overview\n\n" + ("Word " * 90) + "\n\n"
            "## Architecture\n\n" + ("Word " * 60) + "\n\n"
            "## Training\n\n" + ("Word " * 60) + "\n\n"
            "## Evaluation\n\n" + ("Word " * 40) + "\n\n"
            "## Usage Notes\n\n" + ("Word " * 20) + "\n\n"
            "## Main Ideas\n\n"
            "* Idea one\n* Idea two\n* Idea three\n\n"
            "## Summary\n\n"
            "Just one paragraph.\n"
        ),
    )
    result: VerificationResult = verify_model_asset_module.verify_model_asset(
        model_id=DEFAULT_MODEL_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "MA-W004" in _warning_codes(result)


def test_w005_nonexistent_category(repo: Path) -> None:
    build_model_asset(
        repo_root=repo,
        categories=["nonexistent-category"],
    )
    result: VerificationResult = verify_model_asset_module.verify_model_asset(
        model_id=DEFAULT_MODEL_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "MA-W005" in _warning_codes(result)


def test_w008_short_description_under_10_words(repo: Path) -> None:
    build_model_asset(
        repo_root=repo,
        short_description="Too short.",
    )
    result: VerificationResult = verify_model_asset_module.verify_model_asset(
        model_id=DEFAULT_MODEL_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "MA-W008" in _warning_codes(result)


def test_w013_overview_under_80_words(repo: Path) -> None:
    build_model_asset(
        repo_root=repo,
        description_body=(
            "# Title\n\n"
            "## Metadata\n\nMeta.\n\n"
            "## Overview\n\nShort overview.\n\n"
            "## Architecture\n\n" + ("Word " * 60) + "\n\n"
            "## Training\n\n" + ("Word " * 60) + "\n\n"
            "## Evaluation\n\n" + ("Word " * 40) + "\n\n"
            "## Usage Notes\n\n" + ("Word " * 20) + "\n\n"
            "## Main Ideas\n\n"
            "* Idea one\n* Idea two\n* Idea three\n\n"
            "## Summary\n\n"
            "P1.\n\nP2.\n"
        ),
    )
    result: VerificationResult = verify_model_asset_module.verify_model_asset(
        model_id=DEFAULT_MODEL_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "MA-W013" in _warning_codes(result)


def test_w014_empty_training_dataset_ids(repo: Path) -> None:
    build_model_asset(
        repo_root=repo,
        training_dataset_ids=[],
    )
    result: VerificationResult = verify_model_asset_module.verify_model_asset(
        model_id=DEFAULT_MODEL_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "MA-W014" in _warning_codes(result)


def test_w015_empty_hyperparameters(repo: Path) -> None:
    build_model_asset(
        repo_root=repo,
        details_overrides={"hyperparameters": None},
    )
    result: VerificationResult = verify_model_asset_module.verify_model_asset(
        model_id=DEFAULT_MODEL_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "MA-W015" in _warning_codes(result)


def test_w016_empty_training_metrics(repo: Path) -> None:
    build_model_asset(
        repo_root=repo,
        details_overrides={"training_metrics": None},
    )
    result: VerificationResult = verify_model_asset_module.verify_model_asset(
        model_id=DEFAULT_MODEL_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "MA-W016" in _warning_codes(result)
