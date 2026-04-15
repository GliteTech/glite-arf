from pathlib import Path

import pytest

from arf.scripts.verificators import verify_project_budget as verify_mod
from arf.scripts.verificators.common.types import VerificationResult
from arf.tests.fixtures.paths import configure_repo_paths
from arf.tests.fixtures.writers import write_json, write_text

VALID_BUDGET: dict[str, object] = {
    "total_budget": 2000.0,
    "currency": "USD",
    "per_task_default_limit": 100.0,
    "available_services": ["openai_api", "anthropic_api"],
    "alerts": {
        "warn_at_percent": 80,
        "stop_at_percent": 100,
    },
}


def _setup(*, monkeypatch: pytest.MonkeyPatch, repo_root: Path) -> None:
    configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=repo_root,
        verificator_modules=[verify_mod],
    )


def _codes(result: VerificationResult) -> list[str]:
    return [d.code.text for d in result.diagnostics]


def _run(*, repo_root: Path | None = None) -> VerificationResult:
    if repo_root is not None:
        return verify_mod.verify_project_budget(
            file_path=repo_root / "project" / "budget.json",
        )
    return verify_mod.verify_project_budget()


def _write_budget(*, repo_root: Path, data: dict[str, object]) -> None:
    write_json(
        path=repo_root / "project" / "budget.json",
        data=data,
    )


class TestValidPasses:
    def test_valid_budget(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        _write_budget(repo_root=tmp_path, data=VALID_BUDGET)
        result: VerificationResult = _run(repo_root=tmp_path)
        assert len(result.diagnostics) == 0, f"Unexpected diagnostics: {_codes(result)}"
        assert result.passed is True


class TestE001FileMissing:
    def test_missing_file(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        result: VerificationResult = _run(repo_root=tmp_path)
        assert "PB-E001" in _codes(result=result)


class TestE002NotReadableJSON:
    def test_invalid_json(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        write_text(
            path=tmp_path / "project" / "budget.json",
            content="not valid json {",
        )
        result: VerificationResult = _run(repo_root=tmp_path)
        assert "PB-E002" in _codes(result=result)


class TestE003NotObject:
    def test_top_level_array(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        write_text(
            path=tmp_path / "project" / "budget.json",
            content="[1, 2, 3]",
        )
        result: VerificationResult = _run(repo_root=tmp_path)
        assert "PB-E003" in _codes(result=result)


class TestE004MissingOrInvalidField:
    def test_missing_total_budget(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        data: dict[str, object] = dict(VALID_BUDGET)
        del data["total_budget"]
        _write_budget(repo_root=tmp_path, data=data)
        result: VerificationResult = _run(repo_root=tmp_path)
        assert "PB-E004" in _codes(result=result)

    def test_invalid_currency(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        data: dict[str, object] = dict(VALID_BUDGET)
        data["currency"] = "us"
        _write_budget(repo_root=tmp_path, data=data)
        result: VerificationResult = _run(repo_root=tmp_path)
        assert "PB-E004" in _codes(result=result)

    def test_missing_alerts(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        data: dict[str, object] = dict(VALID_BUDGET)
        del data["alerts"]
        _write_budget(repo_root=tmp_path, data=data)
        result: VerificationResult = _run(repo_root=tmp_path)
        assert "PB-E004" in _codes(result=result)


class TestW001PerTaskExceedsBudget:
    def test_per_task_exceeds_total(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        data: dict[str, object] = dict(VALID_BUDGET)
        data["per_task_default_limit"] = 5000.0
        _write_budget(repo_root=tmp_path, data=data)
        result: VerificationResult = _run(repo_root=tmp_path)
        assert "PB-W001" in _codes(result=result)


class TestW002EmptyServices:
    def test_empty_services_list(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        data: dict[str, object] = dict(VALID_BUDGET)
        data["available_services"] = []
        _write_budget(repo_root=tmp_path, data=data)
        result: VerificationResult = _run(repo_root=tmp_path)
        assert "PB-W002" in _codes(result=result)
