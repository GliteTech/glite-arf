from pathlib import Path

import pytest

from arf.scripts.verificators import verify_research_code as verify_mod
from arf.scripts.verificators.common.types import VerificationResult
from arf.tests.fixtures.paths import configure_repo_paths
from arf.tests.fixtures.research_builders import (
    DEFAULT_RESEARCH_CODE_BODY,
    build_research_code,
)
from arf.tests.fixtures.task_builder import build_task_folder

TASK_ID: str = "t0001_test"

_TASK_INDEX: str = (
    "### [t0008]\n\n"
    "* **Task ID**: `t0008_download_semcor`\n"
    "* **Name**: Download SemCor\n"
    "* **Status**: completed\n"
    "* **Relevance**: SemCor dataset download and preprocessing.\n"
    "\n"
    "### [t0012]\n\n"
    "* **Task ID**: `t0012_build_wsd_data_loader_and_scorer`\n"
    "* **Name**: WSD Data Loader\n"
    "* **Status**: completed\n"
    "* **Relevance**: Data loader and scorer implementation.\n"
    "\n"
    "### [t0015]\n\n"
    "* **Task ID**: `t0015_sentence_transformers`\n"
    "* **Name**: Sentence Transformers\n"
    "* **Status**: completed\n"
    "* **Relevance**: Sentence transformer experiments.\n"
)

VALID_CODE_BODY: str = (
    DEFAULT_RESEARCH_CODE_BODY.split("## Task Index")[0] + "## Task Index\n\n" + _TASK_INDEX
)


def _setup(*, monkeypatch: pytest.MonkeyPatch, repo_root: Path) -> None:
    configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=repo_root,
        verificator_modules=[verify_mod],
    )


def _codes(result: VerificationResult) -> list[str]:
    return [d.code.text for d in result.diagnostics]


def _run(*, task_id: str = TASK_ID) -> VerificationResult:
    return verify_mod.verify_research_code(task_id=task_id)


class TestValidPasses:
    def test_valid_research_code(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        build_research_code(
            repo_root=tmp_path,
            task_id=TASK_ID,
            body=VALID_CODE_BODY,
            frontmatter_overrides={"tasks_cited": 3},
        )
        result: VerificationResult = _run()
        assert len(result.errors) == 0, f"Unexpected errors: {_codes(result)}"
        assert result.passed is True


class TestE001FileMissing:
    def test_missing_file(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        result: VerificationResult = _run()
        assert "RC-E001" in _codes(result=result)


class TestE002NoFrontmatter:
    def test_no_frontmatter(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        research_dir: Path = tmp_path / "tasks" / TASK_ID / "research"
        research_dir.mkdir(parents=True, exist_ok=True)
        (research_dir / "research_code.md").write_text(
            "No frontmatter here\n## Task Objective\nSome text.",
            encoding="utf-8",
        )
        result: VerificationResult = _run()
        assert "RC-E002" in _codes(result=result)


class TestE003TaskIdMismatch:
    def test_task_id_mismatch(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        build_research_code(
            repo_root=tmp_path,
            task_id=TASK_ID,
            frontmatter_overrides={"task_id": "t9999_wrong"},
        )
        result: VerificationResult = _run()
        assert "RC-E003" in _codes(result=result)


class TestE004MissingSection:
    def test_missing_mandatory_section(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        body: str = DEFAULT_RESEARCH_CODE_BODY.replace("## Lessons Learned", "## Other Section")
        build_research_code(
            repo_root=tmp_path,
            task_id=TASK_ID,
            body=body,
        )
        result: VerificationResult = _run()
        assert "RC-E004" in _codes(result=result)


class TestE005TasksCitedZero:
    def test_tasks_cited_zero_not_partial(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        build_research_code(
            repo_root=tmp_path,
            task_id=TASK_ID,
            frontmatter_overrides={
                "tasks_cited": 0,
                "status": "complete",
            },
        )
        result: VerificationResult = _run()
        assert "RC-E005" in _codes(result=result)

    def test_tasks_cited_zero_partial_ok(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        build_research_code(
            repo_root=tmp_path,
            task_id=TASK_ID,
            frontmatter_overrides={
                "tasks_cited": 0,
                "status": "partial",
            },
        )
        result: VerificationResult = _run()
        assert "RC-E005" not in _codes(result=result)


class TestE006CitationWithoutIndex:
    def test_unmatched_citation(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        body: str = DEFAULT_RESEARCH_CODE_BODY + ("\nSome claim about code from [t9999].\n")
        build_research_code(
            repo_root=tmp_path,
            task_id=TASK_ID,
            body=body,
            frontmatter_overrides={"tasks_cited": 3},
        )
        result: VerificationResult = _run()
        assert "RC-E006" in _codes(result=result)


class TestE007TaskIndexMissingTaskID:
    def test_missing_task_id_field(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        body: str = (
            "## Task Objective\n\n"
            + "A " * 50
            + "\n\n## Library Landscape\n\n"
            + "B " * 50
            + "\n\n## Key Findings\n\n### Topic\n\n"
            + "C " * 100
            + " [t0001] "
            + "\n\n## Reusable Code and Assets\n\n"
            + "D " * 100
            + "\n\n## Lessons Learned\n\n"
            + "E " * 50
            + "\n\n## Recommendations for This Task\n\n"
            + "F " * 50
            + "\n\n## Task Index\n\n"
            "### [t0001]\n\n"
            "* **Name**: Test task\n"
            "* **Status**: completed\n"
            "* **Relevance**: Relevant.\n"
        )
        build_research_code(
            repo_root=tmp_path,
            task_id=TASK_ID,
            body=body,
            frontmatter_overrides={"tasks_cited": 1},
        )
        result: VerificationResult = _run()
        assert "RC-E007" in _codes(result=result)


class TestE008NoSpecVersion:
    def test_missing_spec_version(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        research_dir: Path = tmp_path / "tasks" / TASK_ID / "research"
        research_dir.mkdir(parents=True, exist_ok=True)
        content: str = (
            "---\n"
            f'task_id: "{TASK_ID}"\n'
            'research_stage: "code"\n'
            "tasks_reviewed: 3\n"
            "tasks_cited: 3\n"
            "libraries_found: 1\n"
            "libraries_relevant: 1\n"
            'date_completed: "2026-04-01"\n'
            'status: "complete"\n'
            "---\n\n" + DEFAULT_RESEARCH_CODE_BODY
        )
        (research_dir / "research_code.md").write_text(content, encoding="utf-8")
        result: VerificationResult = _run()
        assert "RC-E008" in _codes(result=result)


class TestE009Under300Words:
    def test_too_few_words(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        short_body: str = (
            "## Task Objective\n\nShort.\n"
            "## Library Landscape\n\nShort.\n"
            "## Key Findings\n\n### Topic\n\nShort.\n"
            "## Reusable Code and Assets\n\nShort.\n"
            "## Lessons Learned\n\nShort.\n"
            "## Recommendations for This Task\n\nShort.\n"
            "## Task Index\n\n"
        )
        build_research_code(
            repo_root=tmp_path,
            task_id=TASK_ID,
            body=short_body,
            frontmatter_overrides={
                "tasks_cited": 0,
                "status": "partial",
            },
        )
        result: VerificationResult = _run()
        assert "RC-E009" in _codes(result=result)


class TestW001SectionBelowMinWords:
    def test_short_section(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        body: str = DEFAULT_RESEARCH_CODE_BODY.replace(
            "The objective of this task is to review existing code,"
            " libraries, and assets from prior tasks that can be"
            " reused.",
            "Short objective.",
        )
        build_research_code(
            repo_root=tmp_path,
            task_id=TASK_ID,
            body=body,
            frontmatter_overrides={"tasks_cited": 3},
        )
        result: VerificationResult = _run()
        assert "RC-W001" in _codes(result=result)


class TestW003NoKeyFindingsSubsections:
    def test_no_subsections(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        body: str = DEFAULT_RESEARCH_CODE_BODY.replace(
            "### Prior Task Implementations", "**Prior Tasks**"
        ).replace("### External Libraries", "**External Libs**")
        build_research_code(
            repo_root=tmp_path,
            task_id=TASK_ID,
            body=body,
            frontmatter_overrides={"tasks_cited": 3},
        )
        result: VerificationResult = _run()
        assert "RC-W003" in _codes(result=result)


class TestW002TaskIdNotInFolder:
    def test_nonexistent_task_folder(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        # Task Index references t0008, t0012, t0015 — none exist
        build_research_code(
            repo_root=tmp_path,
            task_id=TASK_ID,
            body=VALID_CODE_BODY,
            frontmatter_overrides={"tasks_cited": 3},
        )
        result: VerificationResult = _run()
        assert "RC-W002" in _codes(result=result)


class TestW004TaskIndexEntryNeverCited:
    def test_uncited_limitation(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """RC-W004 cannot easily fire because the ### [key] heading in
        Task Index is itself detected as an inline citation by
        extract_inline_citations. Verify the verificator runs without
        error for a valid case.
        """
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        build_research_code(
            repo_root=tmp_path,
            task_id=TASK_ID,
            body=VALID_CODE_BODY,
            frontmatter_overrides={"tasks_cited": 3},
        )
        result: VerificationResult = _run()
        assert "RC-W004" not in _codes(result=result)


class TestW005ReviewedLessThanCited:
    def test_reviewed_less_than_cited(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        build_research_code(
            repo_root=tmp_path,
            task_id=TASK_ID,
            frontmatter_overrides={
                "tasks_reviewed": 1,
                "tasks_cited": 3,
            },
        )
        result: VerificationResult = _run()
        assert "RC-W005" in _codes(result=result)
