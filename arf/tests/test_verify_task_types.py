from pathlib import Path

import pytest

from arf.scripts.verificators import verify_task_types as verify_mod
from arf.scripts.verificators.common.types import VerificationResult
from arf.tests.fixtures.metadata_builders import build_task_type
from arf.tests.fixtures.paths import configure_repo_paths
from arf.tests.fixtures.writers import write_json, write_text

TASK_TYPE_SLUG: str = "data-analysis"


def _setup(*, monkeypatch: pytest.MonkeyPatch, repo_root: Path) -> None:
    configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=repo_root,
        verificator_modules=[verify_mod],
    )


def _codes(result: VerificationResult) -> list[str]:
    return [d.code.text for d in result.diagnostics]


def _run(*, slug: str = TASK_TYPE_SLUG) -> VerificationResult:
    return verify_mod.verify_task_type(task_type_slug=slug)


class TestValidPasses:
    def test_valid_task_type(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_type(
            repo_root=tmp_path,
            task_type_slug=TASK_TYPE_SLUG,
            optional_steps=["research-papers", "planning"],
        )
        result: VerificationResult = _run()
        assert len(result.diagnostics) == 0, f"Unexpected diagnostics: {_codes(result)}"
        assert result.passed is True


class TestE001DescriptionMissing:
    def test_missing_description(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        result: VerificationResult = _run()
        assert "TY-E001" in _codes(result=result)

    def test_invalid_json(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        tt_dir: Path = tmp_path / "meta" / "task_types" / TASK_TYPE_SLUG
        tt_dir.mkdir(parents=True, exist_ok=True)
        write_text(
            path=tt_dir / "description.json",
            content="not json",
        )
        result: VerificationResult = _run()
        assert "TY-E001" in _codes(result=result)


class TestE002MissingField:
    @pytest.mark.parametrize(
        "field",
        [
            "spec_version",
            "name",
            "short_description",
            "detailed_description",
            "optional_steps",
            "has_external_costs",
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
            "spec_version": 2,
            "name": "Data Analysis",
            "short_description": "Analyze data.",
            "detailed_description": (
                "This is a detailed description of the data analysis"
                " task type that provides enough context."
            ),
            "optional_steps": [],
            "has_external_costs": False,
        }
        del data[field]
        tt_dir: Path = tmp_path / "meta" / "task_types" / TASK_TYPE_SLUG
        tt_dir.mkdir(parents=True, exist_ok=True)
        write_json(
            path=tt_dir / "description.json",
            data=data,
        )
        write_text(
            path=tt_dir / "instruction.md",
            content=(
                "# Data Analysis\n\n"
                "## Planning Guidelines\n\nFollow plan.\n\n"
                "## Implementation Guidelines\n\nImplement it.\n"
            ),
        )
        result: VerificationResult = _run()
        assert "TY-E002" in _codes(result=result)


class TestE008HasExternalCostsNotBool:
    @pytest.mark.parametrize(
        "bad_value",
        [
            "true",
            1,
            0,
            None,
            ["true"],
        ],
    )
    def test_non_bool_value_flagged(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        bad_value: object,
    ) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_type(
            repo_root=tmp_path,
            task_type_slug=TASK_TYPE_SLUG,
            overrides={"has_external_costs": bad_value},
        )
        result: VerificationResult = _run()
        assert "TY-E008" in _codes(result=result), (
            f"TY-E008 must fire for has_external_costs={bad_value!r}; "
            f"got codes: {_codes(result=result)}"
        )

    def test_bool_value_passes(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_type(
            repo_root=tmp_path,
            task_type_slug=TASK_TYPE_SLUG,
            overrides={"has_external_costs": False},
        )
        result: VerificationResult = _run()
        assert "TY-E008" not in _codes(result=result)


class TestE003SpecVersionNotInt:
    def test_string_spec_version(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_type(
            repo_root=tmp_path,
            task_type_slug=TASK_TYPE_SLUG,
            overrides={"spec_version": "1"},
        )
        result: VerificationResult = _run()
        assert "TY-E003" in _codes(result=result)


class TestE004InvalidSlug:
    @pytest.mark.parametrize(
        "slug",
        [
            "Uppercase-Bad",
            "under_score",
            "3starts-with-digit",
        ],
    )
    def test_invalid_slug(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        slug: str,
    ) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_type(repo_root=tmp_path, task_type_slug=slug)
        result: VerificationResult = _run(slug=slug)
        assert "TY-E004" in _codes(result=result)


class TestE005InstructionMissing:
    def test_no_instruction_md(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_type(
            repo_root=tmp_path,
            task_type_slug=TASK_TYPE_SLUG,
        )
        instruction_path: Path = (
            tmp_path / "meta" / "task_types" / TASK_TYPE_SLUG / "instruction.md"
        )
        instruction_path.unlink()
        result: VerificationResult = _run()
        assert "TY-E005" in _codes(result=result)


class TestE006InstructionMissingGuidelines:
    def test_missing_guidelines_heading(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_type(
            repo_root=tmp_path,
            task_type_slug=TASK_TYPE_SLUG,
        )
        instruction_path: Path = (
            tmp_path / "meta" / "task_types" / TASK_TYPE_SLUG / "instruction.md"
        )
        instruction_path.write_text(
            "# Instructions\n\n## Some Other Section\n\nContent.\n" + "X " * 100,
            encoding="utf-8",
        )
        result: VerificationResult = _run()
        assert "TY-E006" in _codes(result=result)


class TestE007InvalidOptionalStep:
    def test_invalid_step_value(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_type(
            repo_root=tmp_path,
            task_type_slug=TASK_TYPE_SLUG,
            optional_steps=["research-papers", "invalid-step-name"],
        )
        result: VerificationResult = _run()
        assert "TY-E007" in _codes(result=result)


class TestW001ShortDescriptionTooLong:
    def test_long_short_description(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_type(
            repo_root=tmp_path,
            task_type_slug=TASK_TYPE_SLUG,
            short_description="A" * 201,
        )
        result: VerificationResult = _run()
        assert "TY-W001" in _codes(result=result)


class TestW002DetailedDescriptionTooShort:
    def test_short_detailed_description(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_type(
            repo_root=tmp_path,
            task_type_slug=TASK_TYPE_SLUG,
            detailed_description="Too short.",
        )
        result: VerificationResult = _run()
        assert "TY-W002" in _codes(result=result)


class TestW003DetailedDescriptionTooLong:
    def test_long_detailed_description(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_type(
            repo_root=tmp_path,
            task_type_slug=TASK_TYPE_SLUG,
            detailed_description="A" * 1001,
        )
        result: VerificationResult = _run()
        assert "TY-W003" in _codes(result=result)


class TestW004NameTooLong:
    def test_long_name(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_type(
            repo_root=tmp_path,
            task_type_slug=TASK_TYPE_SLUG,
            name="A" * 51,
        )
        result: VerificationResult = _run()
        assert "TY-W004" in _codes(result=result)


class TestW005InstructionTooShort:
    def test_short_instruction(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_type(
            repo_root=tmp_path,
            task_type_slug=TASK_TYPE_SLUG,
        )
        instruction_path: Path = (
            tmp_path / "meta" / "task_types" / TASK_TYPE_SLUG / "instruction.md"
        )
        instruction_path.write_text(
            "# X\n\n## Planning Guidelines\n\nShort.\n\n## Implementation Guidelines\n\nShort.\n",
            encoding="utf-8",
        )
        result: VerificationResult = _run()
        assert "TY-W005" in _codes(result=result)
