from pathlib import Path

import pytest

from arf.scripts.verificators import verify_metrics as verify_mod
from arf.scripts.verificators.common.types import VerificationResult
from arf.tests.fixtures.metadata_builders import build_metric
from arf.tests.fixtures.paths import configure_repo_paths
from arf.tests.fixtures.writers import write_json, write_text

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


class TestValidPasses:
    def test_valid_metric(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_metric(repo_root=tmp_path, metric_key=METRIC_KEY)
        result: VerificationResult = _run()
        assert len(result.diagnostics) == 0, f"Unexpected diagnostics: {_codes(result)}"
        assert result.passed is True


class TestE001FileMissing:
    def test_missing_file(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        result: VerificationResult = _run()
        assert "MT-E001" in _codes(result=result)

    def test_invalid_json(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        metric_dir: Path = tmp_path / "meta" / "metrics" / METRIC_KEY
        metric_dir.mkdir(parents=True, exist_ok=True)
        write_text(
            path=metric_dir / "description.json",
            content="not valid json",
        )
        result: VerificationResult = _run()
        assert "MT-E001" in _codes(result=result)


class TestE002MissingField:
    @pytest.mark.parametrize(
        "field",
        [
            "spec_version",
            "name",
            "description",
            "unit",
            "value_type",
        ],
    )
    def test_missing_required_field(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        field: str,
    ) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        data: dict[str, object] = {
            "spec_version": 1,
            "name": "F1 All",
            "description": "F1 score on the ALL concatenation benchmark.",
            "unit": "f1",
            "value_type": "float",
        }
        del data[field]
        metric_dir: Path = tmp_path / "meta" / "metrics" / METRIC_KEY
        metric_dir.mkdir(parents=True, exist_ok=True)
        write_json(
            path=metric_dir / "description.json",
            data=data,
        )
        result: VerificationResult = _run()
        assert "MT-E002" in _codes(result=result)


class TestE003SpecVersionNotInt:
    def test_string_spec_version(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_metric(
            repo_root=tmp_path,
            metric_key=METRIC_KEY,
            overrides={"spec_version": "1"},
        )
        result: VerificationResult = _run()
        assert "MT-E003" in _codes(result=result)


class TestE004InvalidUnit:
    def test_invalid_unit_value(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_metric(
            repo_root=tmp_path,
            metric_key=METRIC_KEY,
            unit="invalid_unit",
        )
        result: VerificationResult = _run()
        assert "MT-E004" in _codes(result=result)


class TestE005InvalidValueType:
    def test_invalid_value_type(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_metric(
            repo_root=tmp_path,
            metric_key=METRIC_KEY,
            value_type="complex",
        )
        result: VerificationResult = _run()
        assert "MT-E005" in _codes(result=result)


class TestE006KeyNotSnakeCase:
    @pytest.mark.parametrize(
        "key",
        [
            "F1-All",
            "f1-all",
            "F1All",
        ],
    )
    def test_invalid_key_format(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        key: str,
    ) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_metric(repo_root=tmp_path, metric_key=key)
        result: VerificationResult = _run(key=key)
        assert "MT-E006" in _codes(result=result)


class TestE007DatasetsNotList:
    def test_datasets_not_list(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_metric(
            repo_root=tmp_path,
            metric_key=METRIC_KEY,
            overrides={"datasets": "not-a-list"},
        )
        result: VerificationResult = _run()
        assert "MT-E007" in _codes(result=result)

    def test_datasets_item_not_string(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_metric(
            repo_root=tmp_path,
            metric_key=METRIC_KEY,
            overrides={"datasets": [123]},
        )
        result: VerificationResult = _run()
        assert "MT-E007" in _codes(result=result)


class TestW001ShortDescription:
    def test_short_description(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_metric(
            repo_root=tmp_path,
            metric_key=METRIC_KEY,
            description="Short.",
        )
        result: VerificationResult = _run()
        assert "MT-W001" in _codes(result=result)


class TestE008DatasetNotInAssets:
    def test_nonexistent_dataset(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        # Create a real dataset so _collect_all_dataset_ids() returns a
        # non-empty set (the guard skips the check when no datasets exist).
        existing_dataset_dir: Path = (
            tmp_path / "tasks" / "t0099_dummy" / "assets" / "dataset" / "existing-dataset"
        )
        existing_dataset_dir.mkdir(parents=True, exist_ok=True)
        build_metric(
            repo_root=tmp_path,
            metric_key=METRIC_KEY,
            overrides={"datasets": ["nonexistent-dataset"]},
        )
        result: VerificationResult = _run()
        assert "MT-E008" in _codes(result=result)


class TestW002LongName:
    def test_long_name(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_metric(
            repo_root=tmp_path,
            metric_key=METRIC_KEY,
            name="A" * 81,
        )
        result: VerificationResult = _run()
        assert "MT-W002" in _codes(result=result)
