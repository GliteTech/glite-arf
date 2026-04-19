from pathlib import Path

import pytest

from arf.scripts.verificators import verify_metrics as verify_mod
from arf.scripts.verificators.common.types import VerificationResult
from arf.tests.fixtures.metadata_builders import build_metric
from arf.tests.fixtures.paths import configure_repo_paths

METRIC_KEY: str = "f1_all"


def _setup(*, monkeypatch: pytest.MonkeyPatch, repo_root: Path) -> None:
    configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=repo_root,
        verificator_modules=[verify_mod],
    )


def _codes(result: VerificationResult) -> list[str]:
    return [d.code.text for d in result.diagnostics]


def _run(*, key: str = METRIC_KEY) -> VerificationResult:
    return verify_mod.verify_metric(metric_key=key)


class TestValidHigherIsBetterTrue:
    def test_valid_metric_true(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_metric(
            repo_root=tmp_path,
            metric_key=METRIC_KEY,
            overrides={"higher_is_better": True},
        )
        result: VerificationResult = _run()
        assert len(result.diagnostics) == 0, f"Unexpected diagnostics: {_codes(result=result)}"
        assert result.passed is True


class TestValidHigherIsBetterFalse:
    def test_valid_metric_false(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_metric(
            repo_root=tmp_path,
            metric_key=METRIC_KEY,
            overrides={"higher_is_better": False},
        )
        result: VerificationResult = _run()
        assert len(result.diagnostics) == 0, f"Unexpected diagnostics: {_codes(result=result)}"
        assert result.passed is True


class TestE002HigherIsBetterMissing:
    def test_missing_higher_is_better(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        # higher_is_better=None tells build_metric to omit the field so we
        # can exercise the required-field-missing code path.
        build_metric(
            repo_root=tmp_path,
            metric_key=METRIC_KEY,
            higher_is_better=None,
        )
        result: VerificationResult = _run()
        assert "MT-E002" in _codes(result=result)


class TestE009HigherIsBetterNotBool:
    def test_string_value(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_metric(
            repo_root=tmp_path,
            metric_key=METRIC_KEY,
            overrides={"higher_is_better": "yes"},
        )
        result: VerificationResult = _run()
        assert "MT-E009" in _codes(result=result)

    def test_int_value(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        # Python's isinstance(True, int) is True, so implementation must use
        # an explicit isinstance(x, bool) check, not int.
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_metric(
            repo_root=tmp_path,
            metric_key=METRIC_KEY,
            overrides={"higher_is_better": 1},
        )
        result: VerificationResult = _run()
        assert "MT-E009" in _codes(result=result)
