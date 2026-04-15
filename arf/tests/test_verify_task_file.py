from pathlib import Path

import pytest

import arf.scripts.common.task_description as task_description_module
import arf.scripts.verificators.verify_task_dependencies as verify_deps_module
import arf.scripts.verificators.verify_task_file as verify_task_file_module
from arf.scripts.verificators.common import paths
from arf.scripts.verificators.common.types import VerificationResult
from arf.tests.fixtures.metadata_builders import build_task_type
from arf.tests.fixtures.paths import configure_repo_paths
from arf.tests.fixtures.suggestion_builder import (
    build_suggestion,
    build_suggestions_file,
)
from arf.tests.fixtures.task_builder import (
    build_step_tracker,
    build_task_folder,
    build_task_json,
)
from arf.tests.fixtures.writers import write_json, write_text

TASK_ID: str = "t0001_test"
TASK_INDEX: int = 1


def _setup(*, monkeypatch: pytest.MonkeyPatch, repo_root: Path) -> None:
    configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=repo_root,
        verificator_modules=[
            verify_task_file_module,
            verify_deps_module,
            task_description_module,
        ],
    )


def _codes(result: VerificationResult) -> list[str]:
    return [d.code.text for d in result.diagnostics]


def _verify(*, task_id: str = TASK_ID) -> VerificationResult:
    return verify_task_file_module.verify_task_file(task_id=task_id)


# ---------------------------------------------------------------------------
# Valid task.json passes
# ---------------------------------------------------------------------------


def test_valid_task_json_passes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        expected_assets={"paper": 1},
    )
    build_step_tracker(repo_root=tmp_path, task_id=TASK_ID)
    result: VerificationResult = _verify()
    assert len(result.diagnostics) == 0, f"Unexpected diagnostics: {_codes(result)}"
    assert result.passed is True


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


def test_tf_e001_missing_file(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    result: VerificationResult = _verify()
    assert "TF-E001" in _codes(result=result)


def test_tf_e001_invalid_json(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    task_json: Path = paths.task_json_path(task_id=TASK_ID)
    write_text(path=task_json, content="NOT JSON {{{")
    result: VerificationResult = _verify()
    assert "TF-E001" in _codes(result=result)


def test_tf_e002_task_id_mismatch(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        overrides={"task_id": "t0099_wrong"},
    )
    result: VerificationResult = _verify()
    assert "TF-E002" in _codes(result=result)


def test_tf_e003_missing_required_field(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    task_json: Path = paths.task_json_path(task_id=TASK_ID)
    write_json(
        path=task_json,
        data={
            "spec_version": 4,
            "task_id": TASK_ID,
            "long_description_file": "task_description.md",
        },
    )
    write_text(
        path=paths.task_dir(task_id=TASK_ID) / "task_description.md",
        content="# Description\n",
    )
    result: VerificationResult = _verify()
    assert "TF-E003" in _codes(result=result)


def test_tf_e004_invalid_status(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        status="invalid_status",
    )
    result: VerificationResult = _verify()
    assert "TF-E004" in _codes(result=result)


def test_tf_e005_bad_task_id_format(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    bad_id: str = "bad-task-id"
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=bad_id)
    build_task_json(
        repo_root=tmp_path,
        task_id=bad_id,
        task_index=1,
        overrides={"task_id": bad_id},
    )
    result: VerificationResult = verify_task_file_module.verify_task_file(
        task_id=bad_id,
    )
    assert "TF-E005" in _codes(result=result)


def test_tf_e006_nonexistent_dependency(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        status="in_progress",
        dependencies=["t9999_nonexistent"],
        start_time="2026-04-01T00:00:00Z",
    )
    result: VerificationResult = _verify()
    assert "TD-E001" in _codes(result=result)


def test_tf_e007_bad_timestamp(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        start_time="not-a-timestamp",
    )
    result: VerificationResult = _verify()
    assert "TF-E007" in _codes(result=result)


def test_tf_e007_non_string_timestamp(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        overrides={"start_time": 12345},
    )
    result: VerificationResult = _verify()
    assert "TF-E007" in _codes(result=result)


def test_tf_e008_bad_source_suggestion_format(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        source_suggestion="BAD-FORMAT",
    )
    result: VerificationResult = _verify()
    assert "TF-E008" in _codes(result=result)


def test_tf_e008_non_string_source_suggestion(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        overrides={"source_suggestion": 123},
    )
    result: VerificationResult = _verify()
    assert "TF-E008" in _codes(result=result)


def test_tf_e009_source_suggestion_not_found(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        source_suggestion="S-9999-01",
    )
    result: VerificationResult = _verify()
    assert "TF-E009" in _codes(result=result)


def test_tf_e009_source_suggestion_found(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    source_task: str = "t0002_source"
    build_task_folder(repo_root=tmp_path, task_id=source_task)
    build_suggestions_file(
        repo_root=tmp_path,
        task_id=source_task,
        suggestions=[
            build_suggestion(
                suggestion_id="S-0002-01",
                source_task=source_task,
            ),
        ],
    )
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        source_suggestion="S-0002-01",
    )
    result: VerificationResult = _verify()
    assert "TF-E009" not in _codes(result=result)


def test_tf_e010_task_index_not_integer(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        overrides={"task_index": "one"},
    )
    result: VerificationResult = _verify()
    assert "TF-E010" in _codes(result=result)


def test_tf_e010_task_index_mismatch(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=99,
    )
    result: VerificationResult = _verify()
    assert "TF-E010" in _codes(result=result)


def test_tf_e011_task_types_not_list(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        overrides={"task_types": "not-a-list"},
    )
    result: VerificationResult = _verify()
    assert "TF-E011" in _codes(result=result)


def test_tf_e012_task_type_not_in_meta(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        task_types=["nonexistent-type"],
    )
    result: VerificationResult = _verify()
    assert "TF-E012" in _codes(result=result)


def test_tf_e012_task_type_exists(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_type(repo_root=tmp_path, task_type_slug="download-dataset")
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        task_types=["download-dataset"],
    )
    result: VerificationResult = _verify()
    assert "TF-E012" not in _codes(result=result)


def test_tf_e013_bad_spec_version_type(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        overrides={"spec_version": "four"},
    )
    result: VerificationResult = _verify()
    assert "TF-E013" in _codes(result=result)


def test_tf_e013_unsupported_spec_version(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        overrides={"spec_version": 99},
    )
    result: VerificationResult = _verify()
    assert "TF-E013" in _codes(result=result)


def test_tf_e014_v4_both_long_description_fields(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    task_json: Path = paths.task_json_path(task_id=TASK_ID)
    data: dict[str, object] = {
        "spec_version": 4,
        "task_id": TASK_ID,
        "task_index": TASK_INDEX,
        "name": "Test",
        "short_description": "A test.",
        "long_description": "Inline text",
        "long_description_file": "task_description.md",
        "status": "not_started",
        "dependencies": [],
        "start_time": None,
        "end_time": None,
        "expected_assets": {},
        "task_types": [],
        "source_suggestion": None,
    }
    write_json(path=task_json, data=data)
    write_text(
        path=paths.task_dir(task_id=TASK_ID) / "task_description.md",
        content="# Desc\n",
    )
    result: VerificationResult = _verify()
    assert "TF-E014" in _codes(result=result)


def test_tf_e014_v4_neither_long_description_field(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    task_json: Path = paths.task_json_path(task_id=TASK_ID)
    data: dict[str, object] = {
        "spec_version": 4,
        "task_id": TASK_ID,
        "task_index": TASK_INDEX,
        "name": "Test",
        "short_description": "A test.",
        "status": "not_started",
        "dependencies": [],
        "start_time": None,
        "end_time": None,
        "expected_assets": {},
        "task_types": [],
        "source_suggestion": None,
    }
    write_json(path=task_json, data=data)
    result: VerificationResult = _verify()
    assert "TF-E014" in _codes(result=result)


def test_tf_e015_bad_long_description_file_name(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        long_description_file="subdir/file.md",
        long_description=None,
    )
    result: VerificationResult = _verify()
    assert "TF-E015" in _codes(result=result)


def test_tf_e016_missing_long_description_file(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    task_json: Path = paths.task_json_path(task_id=TASK_ID)
    data: dict[str, object] = {
        "spec_version": 4,
        "task_id": TASK_ID,
        "task_index": TASK_INDEX,
        "name": "Test",
        "short_description": "A test.",
        "long_description_file": "nonexistent.md",
        "status": "not_started",
        "dependencies": [],
        "start_time": None,
        "end_time": None,
        "expected_assets": {},
        "task_types": [],
        "source_suggestion": None,
    }
    write_json(path=task_json, data=data)
    result: VerificationResult = _verify()
    assert "TF-E016" in _codes(result=result)


# ---------------------------------------------------------------------------
# Warnings
# ---------------------------------------------------------------------------


def test_tf_w001_short_description_too_long(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        short_description="x" * 201,
    )
    result: VerificationResult = _verify()
    assert "TF-W001" in _codes(result=result)


def test_tf_w002_name_too_long(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        name="N" * 81,
    )
    result: VerificationResult = _verify()
    assert "TF-W002" in _codes(result=result)


def test_tf_w003_in_progress_null_start_time(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        status="in_progress",
        start_time=None,
        end_time=None,
    )
    result: VerificationResult = _verify()
    assert "TF-W003" in _codes(result=result)


def test_tf_w004_completed_null_end_time(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        status="completed",
        end_time=None,
    )
    result: VerificationResult = _verify()
    assert "TF-W004" in _codes(result=result)


def test_tf_w005_empty_expected_assets(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        expected_assets={},
    )
    result: VerificationResult = _verify()
    assert "TF-W005" in _codes(result=result)


def test_tf_w006_expected_asset_key_not_in_meta(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """TF-W006: expected_assets key doesn't match any meta/asset_types/ folder."""
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    # Create the meta/asset_types/ structure with known types
    asset_types_dir: Path = tmp_path / "meta" / "asset_types"
    (asset_types_dir / "paper").mkdir(parents=True)
    (asset_types_dir / "predictions").mkdir(parents=True)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        expected_assets={"prediction": 1},  # Wrong: should be "predictions"
    )
    result: VerificationResult = _verify()
    assert "TF-W006" in _codes(result=result)


def test_tf_w006_valid_expected_asset_key(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """No TF-W006 when expected_assets keys match meta/asset_types/ folders."""
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    asset_types_dir: Path = tmp_path / "meta" / "asset_types"
    (asset_types_dir / "paper").mkdir(parents=True)
    (asset_types_dir / "predictions").mkdir(parents=True)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        expected_assets={"predictions": 1, "paper": 2},
    )
    result: VerificationResult = _verify()
    assert "TF-W006" not in _codes(result=result)


def test_tf_w006_dependency_not_completed(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """TF-W006: dependency task does not have status completed.

    verify_task_file delegates to check_all_dependencies which produces
    TD-E003 for non-completed dependencies.
    """
    dep_id: str = "t0002_dep"
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=dep_id)
    build_task_json(
        repo_root=tmp_path,
        task_id=dep_id,
        task_index=2,
        status="in_progress",
        start_time="2026-04-01T00:00:00Z",
    )
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_task_json(
        repo_root=tmp_path,
        task_id=TASK_ID,
        task_index=TASK_INDEX,
        status="in_progress",
        dependencies=[dep_id],
        start_time="2026-04-01T00:00:00Z",
    )
    result: VerificationResult = _verify()
    assert "TD-E003" in _codes(result=result)
