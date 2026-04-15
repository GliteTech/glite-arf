from pathlib import Path

import pytest

from arf.scripts.verificators import verify_project_description as verify_mod
from arf.scripts.verificators.common.types import VerificationResult
from arf.tests.fixtures.paths import configure_repo_paths
from arf.tests.fixtures.writers import write_text

VALID_DESCRIPTION: str = (
    "# Test Project\n\n"
    "## Goal\n\n"
    "Research and reproduce state-of-the-art methods for word sense"
    " disambiguation, compare fine-tuned models against LLM-based"
    " approaches across quality, cost, and speed dimensions.\n\n"
    "## Scope\n\n"
    "### In Scope\n\n"
    "* English all-words WSD using WordNet\n"
    "* Reproducing published SOTA methods\n"
    "* Standard evaluation benchmarks\n\n"
    "### Out of Scope\n\n"
    "* Non-English languages\n"
    "* Production deployment\n\n"
    "## Research Questions\n\n"
    "1. What is the current SOTA for English WSD?\n"
    "2. Can LLM-generated data improve WSD performance?\n"
    "3. How do fine-tuned models compare to LLMs?\n\n"
    "## Success Criteria\n\n"
    "* Reproduce at least 3 published SOTA methods\n"
    "* Achieve or exceed current SOTA F1\n"
    "* Produce a cost/speed vs quality chart\n\n"
    "## Key References\n\n"
    "* Raganato2017 evaluation framework\n"
    "* SemCor training corpus\n"
    "* WordNet 3.0 sense inventory\n\n"
    "## Current Phase\n\n"
    "The project is in the early infrastructure phase with 39 papers"
    " collected and first experiments planned.\n"
)


def _setup(*, monkeypatch: pytest.MonkeyPatch, repo_root: Path) -> None:
    configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=repo_root,
        verificator_modules=[verify_mod],
    )


def _codes(result: VerificationResult) -> list[str]:
    return [d.code.text for d in result.diagnostics]


def _run(*, repo_root: Path) -> VerificationResult:
    return verify_mod.verify_project_description(
        file_path=repo_root / "project" / "description.md",
    )


class TestValidPasses:
    def test_valid_project_description(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        write_text(
            path=tmp_path / "project" / "description.md",
            content=VALID_DESCRIPTION,
        )
        result: VerificationResult = _run(repo_root=tmp_path)
        assert len(result.errors) == 0, f"Unexpected errors: {_codes(result)}"
        assert result.passed is True


class TestE001FileMissing:
    def test_missing_file(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        result: VerificationResult = _run(repo_root=tmp_path)
        assert "PD-E001" in _codes(result=result)


class TestE002MissingSection:
    @pytest.mark.parametrize(
        "section",
        [
            "Goal",
            "Scope",
            "Research Questions",
            "Success Criteria",
            "Key References",
            "Current Phase",
        ],
    )
    def test_missing_mandatory_section(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        section: str,
    ) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        content: str = VALID_DESCRIPTION.replace(f"## {section}", "## Removed Section")
        write_text(
            path=tmp_path / "project" / "description.md",
            content=content,
        )
        result: VerificationResult = _run(repo_root=tmp_path)
        assert "PD-E002" in _codes(result=result)


class TestE003HeadingIssues:
    def test_no_h1_heading(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        content: str = VALID_DESCRIPTION.replace("# Test Project", "## Test Project")
        write_text(
            path=tmp_path / "project" / "description.md",
            content=content,
        )
        result: VerificationResult = _run(repo_root=tmp_path)
        assert "PD-E003" in _codes(result=result)

    def test_multiple_h1_headings(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        content: str = VALID_DESCRIPTION + "\n# Another Title\n"
        write_text(
            path=tmp_path / "project" / "description.md",
            content=content,
        )
        result: VerificationResult = _run(repo_root=tmp_path)
        assert "PD-E003" in _codes(result=result)


class TestE004ScopeMissingSubsection:
    def test_missing_in_scope(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        content: str = VALID_DESCRIPTION.replace("### In Scope", "### Included")
        write_text(
            path=tmp_path / "project" / "description.md",
            content=content,
        )
        result: VerificationResult = _run(repo_root=tmp_path)
        assert "PD-E004" in _codes(result=result)

    def test_missing_out_of_scope(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        content: str = VALID_DESCRIPTION.replace("### Out of Scope", "### Excluded")
        write_text(
            path=tmp_path / "project" / "description.md",
            content=content,
        )
        result: VerificationResult = _run(repo_root=tmp_path)
        assert "PD-E004" in _codes(result=result)


class TestW001GoalUnder30Words:
    def test_short_goal(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        content: str = VALID_DESCRIPTION.replace(
            "Research and reproduce state-of-the-art methods for word"
            " sense disambiguation, compare fine-tuned models against"
            " LLM-based approaches across quality, cost, and speed"
            " dimensions.",
            "Do WSD research.",
        )
        write_text(
            path=tmp_path / "project" / "description.md",
            content=content,
        )
        result: VerificationResult = _run(repo_root=tmp_path)
        assert "PD-W001" in _codes(result=result)


class TestW002FewResearchQuestions:
    def test_fewer_than_3_questions(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        content: str = VALID_DESCRIPTION.replace(
            "1. What is the current SOTA for English WSD?\n"
            "2. Can LLM-generated data improve WSD performance?\n"
            "3. How do fine-tuned models compare to LLMs?\n",
            "1. What is the SOTA?\n",
        )
        write_text(
            path=tmp_path / "project" / "description.md",
            content=content,
        )
        result: VerificationResult = _run(repo_root=tmp_path)
        assert "PD-W002" in _codes(result=result)


class TestW003TooManyResearchQuestions:
    def test_more_than_7_questions(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        questions: str = "".join(f"{i}. Research question number {i}?\n" for i in range(1, 9))
        content: str = VALID_DESCRIPTION.replace(
            "1. What is the current SOTA for English WSD?\n"
            "2. Can LLM-generated data improve WSD performance?\n"
            "3. How do fine-tuned models compare to LLMs?\n",
            questions,
        )
        write_text(
            path=tmp_path / "project" / "description.md",
            content=content,
        )
        result: VerificationResult = _run(repo_root=tmp_path)
        assert "PD-W003" in _codes(result=result)


class TestW004FewSuccessCriteria:
    def test_fewer_than_3_criteria(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        content: str = VALID_DESCRIPTION.replace(
            "* Reproduce at least 3 published SOTA methods\n"
            "* Achieve or exceed current SOTA F1\n"
            "* Produce a cost/speed vs quality chart\n",
            "* Do something good\n",
        )
        write_text(
            path=tmp_path / "project" / "description.md",
            content=content,
        )
        result: VerificationResult = _run(repo_root=tmp_path)
        assert "PD-W004" in _codes(result=result)


class TestW005FewKeyReferences:
    def test_fewer_than_3_references(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        content: str = VALID_DESCRIPTION.replace(
            "* Raganato2017 evaluation framework\n"
            "* SemCor training corpus\n"
            "* WordNet 3.0 sense inventory\n",
            "* One reference\n",
        )
        write_text(
            path=tmp_path / "project" / "description.md",
            content=content,
        )
        result: VerificationResult = _run(repo_root=tmp_path)
        assert "PD-W005" in _codes(result=result)


class TestW006ShortCurrentPhase:
    def test_short_current_phase(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        content: str = VALID_DESCRIPTION.replace(
            "The project is in the early infrastructure phase with 39"
            " papers collected and first experiments planned.",
            "Early phase.",
        )
        write_text(
            path=tmp_path / "project" / "description.md",
            content=content,
        )
        result: VerificationResult = _run(repo_root=tmp_path)
        assert "PD-W006" in _codes(result=result)
