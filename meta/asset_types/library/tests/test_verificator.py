import json
from pathlib import Path

import pytest

import arf.tests.fixtures.asset_builders.library as library_builder_module
import meta.asset_types.library.verificator as verify_library_asset_module
import meta.asset_types.library.verify_description as verify_library_description_module
import meta.asset_types.library.verify_details as verify_library_details_module
from arf.scripts.verificators.common.types import VerificationResult
from arf.tests.fixtures.asset_builders.library import (
    DEFAULT_LIBRARY_ID,
    DEFAULT_TASK_ID,
    build_library_asset,
)
from arf.tests.fixtures.paths import configure_repo_paths
from arf.tests.fixtures.task_builder import build_complete_task
from arf.tests.fixtures.writers import write_json, write_text

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_VERIFICATOR_MODULES = [
    verify_library_asset_module,
    verify_library_details_module,
    verify_library_description_module,
    library_builder_module,
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


def test_valid_library_passes(repo: Path) -> None:
    build_library_asset(repo_root=repo)
    result: VerificationResult = verify_library_asset_module.verify_library_asset(
        library_id=DEFAULT_LIBRARY_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert result.passed is True, _diagnostic_codes(result)


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


def test_e001_details_json_missing(repo: Path) -> None:
    build_library_asset(repo_root=repo)
    from arf.scripts.verificators.common.paths import library_details_path

    library_details_path(
        library_id=DEFAULT_LIBRARY_ID,
        task_id=DEFAULT_TASK_ID,
    ).unlink()
    result: VerificationResult = verify_library_asset_module.verify_library_asset(
        library_id=DEFAULT_LIBRARY_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "LA-E001" in _error_codes(result)


def test_e002_description_missing(repo: Path) -> None:
    build_library_asset(
        repo_root=repo,
        include_description=False,
    )
    result: VerificationResult = verify_library_asset_module.verify_library_asset(
        library_id=DEFAULT_LIBRARY_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "LA-E002" in _error_codes(result)


def test_e004_library_id_mismatch(repo: Path) -> None:
    build_library_asset(
        repo_root=repo,
        details_overrides={"library_id": "wrong_id"},
    )
    result: VerificationResult = verify_library_asset_module.verify_library_asset(
        library_id=DEFAULT_LIBRARY_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "LA-E004" in _error_codes(result)


def test_e005_required_field_missing(repo: Path) -> None:
    build_library_asset(repo_root=repo)
    from arf.scripts.verificators.common.paths import library_details_path

    details_path: Path = library_details_path(
        library_id=DEFAULT_LIBRARY_ID,
        task_id=DEFAULT_TASK_ID,
    )
    data: dict[str, object] = json.loads(
        details_path.read_text(encoding="utf-8"),
    )
    del data["name"]
    write_json(path=details_path, data=data)
    result: VerificationResult = verify_library_asset_module.verify_library_asset(
        library_id=DEFAULT_LIBRARY_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "LA-E005" in _error_codes(result)


def test_e006_empty_module_paths(repo: Path) -> None:
    build_library_asset(
        repo_root=repo,
        module_paths=[],
    )
    result: VerificationResult = verify_library_asset_module.verify_library_asset(
        library_id=DEFAULT_LIBRARY_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "LA-E006" in _error_codes(result)


def test_e008_module_file_does_not_exist(repo: Path) -> None:
    build_library_asset(
        repo_root=repo,
        module_paths=["code/nonexistent_module.py"],
        include_module_files=False,
    )
    result: VerificationResult = verify_library_asset_module.verify_library_asset(
        library_id=DEFAULT_LIBRARY_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "LA-E008" in _error_codes(result)


def test_e009_description_missing_section(repo: Path) -> None:
    build_library_asset(
        repo_root=repo,
        description_body="# Title\n\n## Metadata\n\nSome text.\n",
    )
    result: VerificationResult = verify_library_asset_module.verify_library_asset(
        library_id=DEFAULT_LIBRARY_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "LA-E009" in _error_codes(result)


def test_e010_invalid_entry_point_kind(repo: Path) -> None:
    build_library_asset(
        repo_root=repo,
        entry_points=[
            {
                "name": "load",
                "kind": "invalid_kind",
                "module": "code.test_library",
                "description": "Test entry point",
            },
        ],
    )
    result: VerificationResult = verify_library_asset_module.verify_library_asset(
        library_id=DEFAULT_LIBRARY_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "LA-E010" in _error_codes(result)


def test_e011_folder_name_invalid(repo: Path) -> None:
    bad_id: str = "BAD-LIBRARY"
    build_library_asset(
        repo_root=repo,
        library_id=bad_id,
        include_module_files=False,
    )
    result: VerificationResult = verify_library_asset_module.verify_library_asset(
        library_id=bad_id,
        task_id=DEFAULT_TASK_ID,
    )
    assert "LA-E011" in _error_codes(result)


def test_e012_description_missing_frontmatter(repo: Path) -> None:
    build_library_asset(repo_root=repo)
    from arf.scripts.verificators.common.paths import library_description_path

    desc_path: Path = library_description_path(
        library_id=DEFAULT_LIBRARY_ID,
        task_id=DEFAULT_TASK_ID,
    )
    write_text(
        path=desc_path,
        content="# No Frontmatter\n\nJust text.\n",
    )
    result: VerificationResult = verify_library_asset_module.verify_library_asset(
        library_id=DEFAULT_LIBRARY_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "LA-E012" in _error_codes(result)


def test_e013_no_spec_version(repo: Path) -> None:
    build_library_asset(repo_root=repo)
    from arf.scripts.verificators.common.paths import library_details_path

    details_path: Path = library_details_path(
        library_id=DEFAULT_LIBRARY_ID,
        task_id=DEFAULT_TASK_ID,
    )
    data: dict[str, object] = json.loads(
        details_path.read_text(encoding="utf-8"),
    )
    del data["spec_version"]
    write_json(path=details_path, data=data)
    result: VerificationResult = verify_library_asset_module.verify_library_asset(
        library_id=DEFAULT_LIBRARY_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "LA-E013" in _error_codes(result)


def test_e016_entry_point_missing_required_field(repo: Path) -> None:
    build_library_asset(
        repo_root=repo,
        entry_points=[
            {
                "name": "load",
                "kind": "function",
                # missing "module" and "description"
            },
        ],
    )
    result: VerificationResult = verify_library_asset_module.verify_library_asset(
        library_id=DEFAULT_LIBRARY_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "LA-E016" in _error_codes(result)


# ---------------------------------------------------------------------------
# Warnings
# ---------------------------------------------------------------------------


def test_w001_description_under_400_words(repo: Path) -> None:
    build_library_asset(
        repo_root=repo,
        description_body=(
            "# Title\n\n"
            "## Metadata\n\nMeta.\n\n"
            "## Overview\n\n" + ("Word " * 90) + "\n\n"
            "## API Reference\n\n" + ("Word " * 110) + "\n\n"
            "## Usage Examples\n\nShort.\n\n"
            "## Dependencies\n\nNone.\n\n"
            "## Testing\n\nShort.\n\n"
            "## Main Ideas\n\n"
            "* Idea one\n* Idea two\n* Idea three\n\n"
            "## Summary\n\n"
            "P1.\n\nP2.\n"
        ),
    )
    result: VerificationResult = verify_library_asset_module.verify_library_asset(
        library_id=DEFAULT_LIBRARY_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "LA-W001" in _warning_codes(result)


def test_w003_main_ideas_fewer_than_3(repo: Path) -> None:
    build_library_asset(
        repo_root=repo,
        description_body=(
            "# Title\n\n"
            "## Metadata\n\nMeta.\n\n"
            "## Overview\n\n" + ("Word " * 90) + "\n\n"
            "## API Reference\n\n" + ("Word " * 110) + "\n\n"
            "## Usage Examples\n\n" + ("Word " * 30) + "\n\n"
            "## Dependencies\n\n" + ("Word " * 20) + "\n\n"
            "## Testing\n\n" + ("Word " * 20) + "\n\n"
            "## Main Ideas\n\n"
            "* Only one idea\n\n"
            "## Summary\n\n"
            "P1.\n\nP2.\n"
        ),
    )
    result: VerificationResult = verify_library_asset_module.verify_library_asset(
        library_id=DEFAULT_LIBRARY_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "LA-W003" in _warning_codes(result)


def test_w004_summary_not_2_or_3_paragraphs(repo: Path) -> None:
    build_library_asset(
        repo_root=repo,
        description_body=(
            "# Title\n\n"
            "## Metadata\n\nMeta.\n\n"
            "## Overview\n\n" + ("Word " * 90) + "\n\n"
            "## API Reference\n\n" + ("Word " * 110) + "\n\n"
            "## Usage Examples\n\n" + ("Word " * 30) + "\n\n"
            "## Dependencies\n\n" + ("Word " * 20) + "\n\n"
            "## Testing\n\n" + ("Word " * 20) + "\n\n"
            "## Main Ideas\n\n"
            "* Idea one\n* Idea two\n* Idea three\n\n"
            "## Summary\n\n"
            "Just one paragraph.\n"
        ),
    )
    result: VerificationResult = verify_library_asset_module.verify_library_asset(
        library_id=DEFAULT_LIBRARY_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "LA-W004" in _warning_codes(result)


def test_w005_nonexistent_category(repo: Path) -> None:
    build_library_asset(
        repo_root=repo,
        categories=["nonexistent-category"],
    )
    result: VerificationResult = verify_library_asset_module.verify_library_asset(
        library_id=DEFAULT_LIBRARY_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "LA-W005" in _warning_codes(result)


def test_w008_short_description_under_10_words(repo: Path) -> None:
    build_library_asset(
        repo_root=repo,
        short_description="Too short.",
    )
    result: VerificationResult = verify_library_asset_module.verify_library_asset(
        library_id=DEFAULT_LIBRARY_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "LA-W008" in _warning_codes(result)


def test_w013_overview_under_80_words(repo: Path) -> None:
    build_library_asset(
        repo_root=repo,
        description_body=(
            "# Title\n\n"
            "## Metadata\n\nMeta.\n\n"
            "## Overview\n\nShort overview.\n\n"
            "## API Reference\n\n" + ("Word " * 110) + "\n\n"
            "## Usage Examples\n\n" + ("Word " * 30) + "\n\n"
            "## Dependencies\n\n" + ("Word " * 20) + "\n\n"
            "## Testing\n\n" + ("Word " * 20) + "\n\n"
            "## Main Ideas\n\n"
            "* Idea one\n* Idea two\n* Idea three\n\n"
            "## Summary\n\n"
            "P1.\n\nP2.\n"
        ),
    )
    result: VerificationResult = verify_library_asset_module.verify_library_asset(
        library_id=DEFAULT_LIBRARY_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "LA-W013" in _warning_codes(result)


def test_w014_no_test_paths(repo: Path) -> None:
    build_library_asset(
        repo_root=repo,
        test_paths=[],
    )
    result: VerificationResult = verify_library_asset_module.verify_library_asset(
        library_id=DEFAULT_LIBRARY_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "LA-W014" in _warning_codes(result)


def test_w015_test_path_does_not_exist(repo: Path) -> None:
    build_library_asset(repo_root=repo)
    # Overwrite details.json with a test_path that doesn't exist
    from arf.scripts.verificators.common.paths import library_details_path

    details_path: Path = library_details_path(
        library_id=DEFAULT_LIBRARY_ID,
        task_id=DEFAULT_TASK_ID,
    )
    data: dict[str, object] = json.loads(
        details_path.read_text(encoding="utf-8"),
    )
    data["test_paths"] = ["code/nonexistent_test.py"]
    write_json(path=details_path, data=data)
    result: VerificationResult = verify_library_asset_module.verify_library_asset(
        library_id=DEFAULT_LIBRARY_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "LA-W015" in _warning_codes(result)


def test_w016_api_reference_under_100_words(repo: Path) -> None:
    build_library_asset(
        repo_root=repo,
        description_body=(
            "# Title\n\n"
            "## Metadata\n\nMeta.\n\n"
            "## Overview\n\n" + ("Word " * 90) + "\n\n"
            "## API Reference\n\nShort API ref.\n\n"
            "## Usage Examples\n\n" + ("Word " * 30) + "\n\n"
            "## Dependencies\n\n" + ("Word " * 20) + "\n\n"
            "## Testing\n\n" + ("Word " * 20) + "\n\n"
            "## Main Ideas\n\n"
            "* Idea one\n* Idea two\n* Idea three\n\n"
            "## Summary\n\n"
            "P1.\n\nP2.\n"
        ),
    )
    result: VerificationResult = verify_library_asset_module.verify_library_asset(
        library_id=DEFAULT_LIBRARY_ID,
        task_id=DEFAULT_TASK_ID,
    )
    assert "LA-W016" in _warning_codes(result)
