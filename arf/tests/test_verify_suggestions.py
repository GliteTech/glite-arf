from pathlib import Path

import pytest

import arf.scripts.verificators.verify_suggestions as verify_suggestions_module
from arf.scripts.verificators.common import paths
from arf.scripts.verificators.common.types import VerificationResult
from arf.tests.fixtures.metadata_builders import build_category
from arf.tests.fixtures.paths import configure_repo_paths
from arf.tests.fixtures.suggestion_builder import (
    build_suggestion,
    build_suggestions_file,
)
from arf.tests.fixtures.task_builder import build_task_folder
from arf.tests.fixtures.writers import write_json, write_text

TASK_ID: str = "t0001_test"


def _setup(*, monkeypatch: pytest.MonkeyPatch, repo_root: Path) -> None:
    configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=repo_root,
        verificator_modules=[verify_suggestions_module],
    )


def _codes(result: VerificationResult) -> list[str]:
    return [d.code.text for d in result.diagnostics]


def _verify(*, task_id: str = TASK_ID) -> VerificationResult:
    return verify_suggestions_module.verify_suggestions(task_id=task_id)


# ---------------------------------------------------------------------------
# Valid suggestions pass
# ---------------------------------------------------------------------------


def test_valid_suggestions_pass(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_category(repo_root=tmp_path, category_slug="test-category")
    build_suggestions_file(
        repo_root=tmp_path,
        task_id=TASK_ID,
        suggestions=[build_suggestion(source_task=TASK_ID)],
    )
    result: VerificationResult = _verify()
    assert len(result.diagnostics) == 0, f"Unexpected diagnostics: {_codes(result)}"
    assert result.passed is True


def test_valid_empty_suggestions_pass(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_suggestions_file(
        repo_root=tmp_path,
        task_id=TASK_ID,
        suggestions=[],
    )
    result: VerificationResult = _verify()
    assert result.passed is True


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


def test_sg_e001_missing_file(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    result: VerificationResult = _verify()
    assert "SG-E001" in _codes(result=result)


def test_sg_e001_invalid_json(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    write_text(
        path=paths.suggestions_path(task_id=TASK_ID),
        content="NOT VALID JSON",
    )
    result: VerificationResult = _verify()
    assert "SG-E001" in _codes(result=result)


def test_sg_e002_not_object(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    suggestions_file: Path = paths.suggestions_path(task_id=TASK_ID)
    write_json(path=suggestions_file, data=[1, 2, 3])
    result: VerificationResult = _verify()
    assert "SG-E002" in _codes(result=result)


def test_sg_e003_missing_spec_version(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    suggestions_file: Path = paths.suggestions_path(task_id=TASK_ID)
    write_json(path=suggestions_file, data={"suggestions": []})
    result: VerificationResult = _verify()
    assert "SG-E003" in _codes(result=result)


def test_sg_e004_missing_suggestions_field(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    suggestions_file: Path = paths.suggestions_path(task_id=TASK_ID)
    write_json(path=suggestions_file, data={"spec_version": "2"})
    result: VerificationResult = _verify()
    assert "SG-E004" in _codes(result=result)


def test_sg_e004_suggestions_not_array(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    suggestions_file: Path = paths.suggestions_path(task_id=TASK_ID)
    write_json(
        path=suggestions_file,
        data={"spec_version": "2", "suggestions": "not-a-list"},
    )
    result: VerificationResult = _verify()
    assert "SG-E004" in _codes(result=result)


def test_sg_e005_element_not_object(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    suggestions_file: Path = paths.suggestions_path(task_id=TASK_ID)
    write_json(
        path=suggestions_file,
        data={"spec_version": "2", "suggestions": ["not-an-object"]},
    )
    result: VerificationResult = _verify()
    assert "SG-E005" in _codes(result=result)


def test_sg_e006_missing_required_field(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    suggestions_file: Path = paths.suggestions_path(task_id=TASK_ID)
    incomplete_suggestion: dict[str, object] = {"id": "S-0001-01"}
    write_json(
        path=suggestions_file,
        data={"spec_version": "2", "suggestions": [incomplete_suggestion]},
    )
    result: VerificationResult = _verify()
    assert "SG-E006" in _codes(result=result)


def test_sg_e007_bad_id_format(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_suggestions_file(
        repo_root=tmp_path,
        task_id=TASK_ID,
        suggestions=[
            build_suggestion(
                suggestion_id="BAD-ID",
                source_task=TASK_ID,
            ),
        ],
    )
    result: VerificationResult = _verify()
    assert "SG-E007" in _codes(result=result)


def test_sg_e008_invalid_kind(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_suggestions_file(
        repo_root=tmp_path,
        task_id=TASK_ID,
        suggestions=[
            build_suggestion(
                kind="invalid_kind",
                source_task=TASK_ID,
            ),
        ],
    )
    result: VerificationResult = _verify()
    assert "SG-E008" in _codes(result=result)


def test_sg_e009_invalid_priority(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_suggestions_file(
        repo_root=tmp_path,
        task_id=TASK_ID,
        suggestions=[
            build_suggestion(
                priority="urgent",
                source_task=TASK_ID,
            ),
        ],
    )
    result: VerificationResult = _verify()
    assert "SG-E009" in _codes(result=result)


def test_sg_e010_source_task_mismatch(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_suggestions_file(
        repo_root=tmp_path,
        task_id=TASK_ID,
        suggestions=[
            build_suggestion(source_task="t0099_wrong_task"),
        ],
    )
    result: VerificationResult = _verify()
    assert "SG-E010" in _codes(result=result)


def test_sg_e011_duplicate_ids(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_suggestions_file(
        repo_root=tmp_path,
        task_id=TASK_ID,
        suggestions=[
            build_suggestion(
                suggestion_id="S-0001-01",
                source_task=TASK_ID,
            ),
            build_suggestion(
                suggestion_id="S-0001-01",
                source_task=TASK_ID,
            ),
        ],
    )
    result: VerificationResult = _verify()
    assert "SG-E011" in _codes(result=result)


def test_sg_e012_categories_not_list(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_suggestions_file(
        repo_root=tmp_path,
        task_id=TASK_ID,
        suggestions=[
            build_suggestion(
                source_task=TASK_ID,
                overrides={"categories": "not-a-list"},
            ),
        ],
    )
    result: VerificationResult = _verify()
    assert "SG-E012" in _codes(result=result)


def test_sg_e013_invalid_status(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_suggestions_file(
        repo_root=tmp_path,
        task_id=TASK_ID,
        suggestions=[
            build_suggestion(
                status="invalid_status",
                source_task=TASK_ID,
            ),
        ],
    )
    result: VerificationResult = _verify()
    assert "SG-E013" in _codes(result=result)


# ---------------------------------------------------------------------------
# Warnings
# ---------------------------------------------------------------------------


def test_sg_w001_title_too_long(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_suggestions_file(
        repo_root=tmp_path,
        task_id=TASK_ID,
        suggestions=[
            build_suggestion(
                title="T" * 121,
                source_task=TASK_ID,
            ),
        ],
    )
    result: VerificationResult = _verify()
    assert "SG-W001" in _codes(result=result)


def test_sg_w002_description_too_short(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_suggestions_file(
        repo_root=tmp_path,
        task_id=TASK_ID,
        suggestions=[
            build_suggestion(
                description="Short",
                source_task=TASK_ID,
            ),
        ],
    )
    result: VerificationResult = _verify()
    assert "SG-W002" in _codes(result=result)


def test_sg_w003_description_too_long(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_suggestions_file(
        repo_root=tmp_path,
        task_id=TASK_ID,
        suggestions=[
            build_suggestion(
                description="D" * 1001,
                source_task=TASK_ID,
            ),
        ],
    )
    result: VerificationResult = _verify()
    assert "SG-W003" in _codes(result=result)


def test_sg_w004_empty_title(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_suggestions_file(
        repo_root=tmp_path,
        task_id=TASK_ID,
        suggestions=[
            build_suggestion(
                title="   ",
                source_task=TASK_ID,
            ),
        ],
    )
    result: VerificationResult = _verify()
    assert "SG-W004" in _codes(result=result)


def test_sg_w005_empty_description(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_suggestions_file(
        repo_root=tmp_path,
        task_id=TASK_ID,
        suggestions=[
            build_suggestion(
                description="   ",
                source_task=TASK_ID,
            ),
        ],
    )
    result: VerificationResult = _verify()
    assert "SG-W005" in _codes(result=result)


def test_sg_w006_nonexistent_category(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
    build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
    build_suggestions_file(
        repo_root=tmp_path,
        task_id=TASK_ID,
        suggestions=[
            build_suggestion(
                source_task=TASK_ID,
                categories=["nonexistent-category"],
            ),
        ],
    )
    result: VerificationResult = _verify()
    assert "SG-W006" in _codes(result=result)
