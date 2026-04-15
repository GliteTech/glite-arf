from pathlib import Path

import pytest

from arf.scripts.verificators import verify_categories as verify_mod
from arf.scripts.verificators.common.types import VerificationResult
from arf.tests.fixtures.metadata_builders import build_category
from arf.tests.fixtures.paths import configure_repo_paths
from arf.tests.fixtures.writers import write_json, write_text

CATEGORY_SLUG: str = "test-category"


def _setup(*, monkeypatch: pytest.MonkeyPatch, repo_root: Path) -> None:
    configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=repo_root,
        verificator_modules=[verify_mod],
    )


def _codes(result: VerificationResult) -> list[str]:
    return [d.code.text for d in result.diagnostics]


def _run(*, slug: str = CATEGORY_SLUG) -> VerificationResult:
    return verify_mod.verify_category(category_slug=slug)


class TestValidPasses:
    def test_valid_category(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_category(repo_root=tmp_path, category_slug=CATEGORY_SLUG)
        result: VerificationResult = _run()
        assert len(result.diagnostics) == 0, f"Unexpected diagnostics: {_codes(result)}"
        assert result.passed is True


class TestE001FileMissing:
    def test_missing_file(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        result: VerificationResult = _run()
        assert "CA-E001" in _codes(result=result)

    def test_invalid_json(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        cat_dir: Path = tmp_path / "meta" / "categories" / CATEGORY_SLUG
        cat_dir.mkdir(parents=True, exist_ok=True)
        write_text(
            path=cat_dir / "description.json",
            content="not valid json",
        )
        result: VerificationResult = _run()
        assert "CA-E001" in _codes(result=result)


class TestE002MissingField:
    @pytest.mark.parametrize(
        "field",
        [
            "spec_version",
            "name",
            "short_description",
            "detailed_description",
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
            "name": "Test Category",
            "short_description": "A test category.",
            "detailed_description": (
                "This is a detailed description of the test category that provides enough context."
            ),
        }
        del data[field]
        cat_dir: Path = tmp_path / "meta" / "categories" / CATEGORY_SLUG
        cat_dir.mkdir(parents=True, exist_ok=True)
        write_json(
            path=cat_dir / "description.json",
            data=data,
        )
        result: VerificationResult = _run()
        assert "CA-E002" in _codes(result=result)


class TestE003SpecVersionNotInt:
    def test_string_spec_version(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_category(
            repo_root=tmp_path,
            category_slug=CATEGORY_SLUG,
            overrides={"spec_version": "1"},
        )
        result: VerificationResult = _run()
        assert "CA-E003" in _codes(result=result)


class TestE004InvalidSlug:
    @pytest.mark.parametrize(
        "slug",
        [
            "Uppercase-Bad",
            "under_score",
            "3starts-with-digit",
        ],
    )
    def test_invalid_slug_format(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        slug: str,
    ) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_category(repo_root=tmp_path, category_slug=slug)
        result: VerificationResult = _run(slug=slug)
        assert "CA-E004" in _codes(result=result)


class TestW001ShortDescriptionTooLong:
    def test_long_short_description(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_category(
            repo_root=tmp_path,
            category_slug=CATEGORY_SLUG,
            short_description="A" * 201,
        )
        result: VerificationResult = _run()
        assert "CA-W001" in _codes(result=result)


class TestW002DetailedDescriptionTooShort:
    def test_short_detailed_description(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_category(
            repo_root=tmp_path,
            category_slug=CATEGORY_SLUG,
            detailed_description="Too short.",
        )
        result: VerificationResult = _run()
        assert "CA-W002" in _codes(result=result)


class TestW003DetailedDescriptionTooLong:
    def test_long_detailed_description(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_category(
            repo_root=tmp_path,
            category_slug=CATEGORY_SLUG,
            detailed_description="A" * 1001,
        )
        result: VerificationResult = _run()
        assert "CA-W003" in _codes(result=result)


class TestW004NameTooLong:
    def test_long_name(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_category(
            repo_root=tmp_path,
            category_slug=CATEGORY_SLUG,
            name="A" * 51,
        )
        result: VerificationResult = _run()
        assert "CA-W004" in _codes(result=result)
