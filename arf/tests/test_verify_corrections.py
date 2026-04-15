"""Tests for the verify_corrections verificator (CR-codes).

Tests verify correction file format, required fields, action semantics,
and reference integrity as defined in corrections_specification.md.
"""

from pathlib import Path

import pytest

import arf.scripts.common.artifacts as artifacts_module
import arf.scripts.common.corrections as corrections_module
import arf.scripts.verificators.verify_corrections as verify_cr_module
from arf.scripts.verificators.common import paths
from arf.scripts.verificators.common.types import VerificationResult
from arf.tests.fixtures.paths import configure_repo_paths
from arf.tests.fixtures.suggestion_builder import (
    build_suggestion,
    build_suggestions_file,
)
from arf.tests.fixtures.task_builder import (
    build_task_folder,
    build_task_json,
)
from arf.tests.fixtures.writers import write_json, write_text

CORRECTING_TASK: str = "t0002_fixup"
CORRECTING_INDEX: int = 2
TARGET_TASK: str = "t0001_original"
TARGET_INDEX: int = 1
SUGGESTION_ID: str = "S-0001-01"


def _setup(*, monkeypatch: pytest.MonkeyPatch, repo_root: Path) -> None:
    configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=repo_root,
        verificator_modules=[
            verify_cr_module,
            artifacts_module,
            corrections_module,
        ],
    )


def _codes(result: VerificationResult) -> list[str]:
    return [d.code.text for d in result.diagnostics]


def _verify(*, task_id: str = CORRECTING_TASK) -> VerificationResult:
    return verify_cr_module.verify_corrections(task_id=task_id)


def _build_target_with_suggestion(*, repo_root: Path) -> None:
    build_task_folder(repo_root=repo_root, task_id=TARGET_TASK)
    build_task_json(
        repo_root=repo_root,
        task_id=TARGET_TASK,
        task_index=TARGET_INDEX,
        status="completed",
    )
    build_suggestions_file(
        repo_root=repo_root,
        task_id=TARGET_TASK,
        suggestions=[
            build_suggestion(
                suggestion_id=SUGGESTION_ID,
                source_task=TARGET_TASK,
            ),
        ],
    )


def _write_correction(
    *,
    task_id: str = CORRECTING_TASK,
    file_name: str = "suggestion_S-0001-01.json",
    data: dict[str, object],
) -> Path:
    correction_dir: Path = paths.corrections_dir(task_id=task_id)
    correction_path: Path = correction_dir / file_name
    write_json(path=correction_path, data=data)
    return correction_path


def _valid_correction() -> dict[str, object]:
    return {
        "spec_version": "3",
        "correction_id": "C-0002-01",
        "correcting_task": CORRECTING_TASK,
        "target_task": TARGET_TASK,
        "target_kind": "suggestion",
        "target_id": SUGGESTION_ID,
        "action": "update",
        "changes": {"priority": "high"},
        "rationale": "New evidence supports higher priority.",
    }


# ---------------------------------------------------------------------------
# Valid correction passes
# ---------------------------------------------------------------------------


def test_valid_correction_passes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_target_with_suggestion(repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=CORRECTING_TASK)
    build_task_json(
        repo_root=tmp_path,
        task_id=CORRECTING_TASK,
        task_index=CORRECTING_INDEX,
    )
    _write_correction(data=_valid_correction())
    result: VerificationResult = _verify()
    assert len(result.diagnostics) == 0, f"Unexpected diagnostics: {_codes(result)}"
    assert result.passed is True


# ---------------------------------------------------------------------------
# No corrections passes (empty corrections/ dir)
# ---------------------------------------------------------------------------


def test_no_corrections_passes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=CORRECTING_TASK)
    build_task_json(
        repo_root=tmp_path,
        task_id=CORRECTING_TASK,
        task_index=CORRECTING_INDEX,
    )
    result: VerificationResult = _verify()
    assert len(result.diagnostics) == 0, f"Unexpected diagnostics: {_codes(result)}"
    assert result.passed is True


# ---------------------------------------------------------------------------
# CR-E001: Invalid JSON
# ---------------------------------------------------------------------------


def test_cr_e001_invalid_json(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=CORRECTING_TASK)
    correction_path: Path = paths.corrections_dir(task_id=CORRECTING_TASK) / "bad.json"
    write_text(path=correction_path, content="NOT VALID JSON {{{")
    result: VerificationResult = _verify()
    assert "CR-E001" in _codes(result=result)


# ---------------------------------------------------------------------------
# CR-E002: Top-level not an object
# ---------------------------------------------------------------------------


def test_cr_e002_not_an_object(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=CORRECTING_TASK)
    correction_path: Path = paths.corrections_dir(task_id=CORRECTING_TASK) / "array.json"
    write_json(path=correction_path, data=[1, 2, 3])
    result: VerificationResult = _verify()
    assert "CR-E002" in _codes(result=result)


# ---------------------------------------------------------------------------
# CR-E003: Missing required field
# ---------------------------------------------------------------------------


def test_cr_e003_missing_required_fields(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_target_with_suggestion(repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=CORRECTING_TASK)
    # Only spec_version, missing everything else
    _write_correction(data={"spec_version": "3"})
    result: VerificationResult = _verify()
    assert "CR-E003" in _codes(result=result)


# ---------------------------------------------------------------------------
# CR-E005: Invalid correction_id format
# ---------------------------------------------------------------------------


def test_cr_e005_bad_correction_id(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_target_with_suggestion(repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=CORRECTING_TASK)
    data: dict[str, object] = _valid_correction()
    data["correction_id"] = "BADFORMAT"
    _write_correction(data=data)
    result: VerificationResult = _verify()
    assert "CR-E005" in _codes(result=result)


def test_cr_e005_wrong_task_index_in_id(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_target_with_suggestion(repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=CORRECTING_TASK)
    data: dict[str, object] = _valid_correction()
    # correction_id uses 9999 but correcting_task is t0002
    data["correction_id"] = "C-9999-01"
    _write_correction(data=data)
    result: VerificationResult = _verify()
    assert "CR-E005" in _codes(result=result)


# ---------------------------------------------------------------------------
# CR-E006: correcting_task mismatch
# ---------------------------------------------------------------------------


def test_cr_e006_correcting_task_mismatch(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_target_with_suggestion(repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=CORRECTING_TASK)
    data: dict[str, object] = _valid_correction()
    data["correcting_task"] = "t9999_wrong"
    _write_correction(data=data)
    result: VerificationResult = _verify()
    assert "CR-E006" in _codes(result=result)


# ---------------------------------------------------------------------------
# CR-E007: target_task does not exist
# ---------------------------------------------------------------------------


def test_cr_e007_target_task_missing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=CORRECTING_TASK)
    data: dict[str, object] = _valid_correction()
    data["target_task"] = "t9999_nonexistent"
    _write_correction(data=data)
    result: VerificationResult = _verify()
    assert "CR-E007" in _codes(result=result)


# ---------------------------------------------------------------------------
# CR-E008: Invalid target_kind
# ---------------------------------------------------------------------------


def test_cr_e008_invalid_target_kind(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_target_with_suggestion(repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=CORRECTING_TASK)
    data: dict[str, object] = _valid_correction()
    data["target_kind"] = "invalid_kind"
    _write_correction(data=data)
    result: VerificationResult = _verify()
    assert "CR-E008" in _codes(result=result)


# ---------------------------------------------------------------------------
# CR-E009: Invalid action
# ---------------------------------------------------------------------------


def test_cr_e009_invalid_action(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_target_with_suggestion(repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=CORRECTING_TASK)
    data: dict[str, object] = _valid_correction()
    data["action"] = "destroy"
    _write_correction(data=data)
    result: VerificationResult = _verify()
    assert "CR-E009" in _codes(result=result)


# ---------------------------------------------------------------------------
# CR-E010: Delete action with non-null changes
# ---------------------------------------------------------------------------


def test_cr_e010_delete_with_changes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_target_with_suggestion(repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=CORRECTING_TASK)
    data: dict[str, object] = _valid_correction()
    data["action"] = "delete"
    data["changes"] = {"priority": "low"}
    _write_correction(data=data)
    result: VerificationResult = _verify()
    assert "CR-E010" in _codes(result=result)


# ---------------------------------------------------------------------------
# CR-E012: Empty rationale
# ---------------------------------------------------------------------------


def test_cr_e012_empty_rationale(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_target_with_suggestion(repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=CORRECTING_TASK)
    data: dict[str, object] = _valid_correction()
    data["rationale"] = "   "
    _write_correction(data=data)
    result: VerificationResult = _verify()
    assert "CR-E012" in _codes(result=result)


# ---------------------------------------------------------------------------
# CR-W002: Filename does not match convention
# ---------------------------------------------------------------------------


def test_cr_w002_filename_mismatch(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_target_with_suggestion(repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=CORRECTING_TASK)
    _write_correction(
        data=_valid_correction(),
        file_name="wrong_filename.json",
    )
    result: VerificationResult = _verify()
    assert "CR-W002" in _codes(result=result)


# ---------------------------------------------------------------------------
# CR-W003: Rationale too short
# ---------------------------------------------------------------------------


def test_cr_w003_short_rationale(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    _build_target_with_suggestion(repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=CORRECTING_TASK)
    data: dict[str, object] = _valid_correction()
    data["rationale"] = "Short."
    _write_correction(data=data)
    result: VerificationResult = _verify()
    assert "CR-W003" in _codes(result=result)
