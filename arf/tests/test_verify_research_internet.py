from pathlib import Path

import pytest

from arf.scripts.verificators import verify_research_internet as verify_mod
from arf.scripts.verificators.common.types import VerificationResult
from arf.tests.fixtures.paths import configure_repo_paths
from arf.tests.fixtures.research_builders import (
    DEFAULT_RESEARCH_INTERNET_BODY,
    build_research_internet,
)
from arf.tests.fixtures.task_builder import build_task_folder

TASK_ID: str = "t0001_test"

_SOURCE_INDEX_WITH_URL: str = (
    "### [Source1]\n\n"
    "* **Type**: blog\n"
    "* **Title**: Google Scholar search results\n"
    "* **Author/Org**: Google\n"
    "* **Date**: 2024-06\n"
    "* **URL**: https://scholar.google.com/search?q=wsd\n"
    "* **Peer-reviewed**: no\n"
    "* **Relevance**: Search results for WSD + LLM.\n"
    "\n"
    "### [Source2]\n\n"
    "* **Type**: paper\n"
    "* **Title**: arXiv preprint on word sense disambiguation\n"
    "* **Authors**: Smith et al.\n"
    "* **Year**: 2025\n"
    "* **URL**: https://arxiv.org/abs/2025.12345\n"
    "* **Peer-reviewed**: no\n"
    "* **Relevance**: Recent WSD preprint.\n"
)

_VALID_INTERNET_BODY: str = (
    DEFAULT_RESEARCH_INTERNET_BODY.split("## Source Index")[0]
    + "## Source Index\n\n"
    + _SOURCE_INDEX_WITH_URL
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
    return verify_mod.verify_research_internet(task_id=task_id)


class TestValidPasses:
    def test_valid_research_internet(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        build_research_internet(
            repo_root=tmp_path,
            task_id=TASK_ID,
            body=_VALID_INTERNET_BODY,
            frontmatter_overrides={"searches_conducted": 3},
        )
        result: VerificationResult = _run()
        assert len(result.errors) == 0, f"Unexpected errors: {_codes(result)}"
        assert result.passed is True


class TestE001FileMissing:
    def test_missing_file(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        result: VerificationResult = _run()
        assert "RI-E001" in _codes(result=result)


class TestE002NoFrontmatter:
    def test_no_frontmatter(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        research_dir: Path = tmp_path / "tasks" / TASK_ID / "research"
        research_dir.mkdir(parents=True, exist_ok=True)
        (research_dir / "research_internet.md").write_text(
            "No frontmatter here\n## Task Objective\nSome text.",
            encoding="utf-8",
        )
        result: VerificationResult = _run()
        assert "RI-E002" in _codes(result=result)


class TestE003TaskIdMismatch:
    def test_task_id_mismatch(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        build_research_internet(
            repo_root=tmp_path,
            task_id=TASK_ID,
            frontmatter_overrides={"task_id": "t9999_wrong"},
        )
        result: VerificationResult = _run()
        assert "RI-E003" in _codes(result=result)


class TestE004MissingSection:
    def test_missing_mandatory_section(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        body: str = DEFAULT_RESEARCH_INTERNET_BODY.replace(
            "## Discovered Papers", "## Other Section"
        )
        build_research_internet(
            repo_root=tmp_path,
            task_id=TASK_ID,
            body=body,
        )
        result: VerificationResult = _run()
        assert "RI-E004" in _codes(result=result)


class TestE005SourcesCitedZero:
    def test_sources_cited_zero_not_partial(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        build_research_internet(
            repo_root=tmp_path,
            task_id=TASK_ID,
            frontmatter_overrides={
                "sources_cited": 0,
                "status": "complete",
            },
        )
        result: VerificationResult = _run()
        assert "RI-E005" in _codes(result=result)


class TestE006CitationWithoutIndex:
    def test_unmatched_citation(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        body: str = DEFAULT_RESEARCH_INTERNET_BODY + (
            "\nSome claim [GhostSource2099] is notable.\n"
        )
        build_research_internet(
            repo_root=tmp_path,
            task_id=TASK_ID,
            body=body,
        )
        result: VerificationResult = _run()
        assert "RI-E006" in _codes(result=result)


class TestE007IndexCountMismatch:
    def test_count_mismatch(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        build_research_internet(
            repo_root=tmp_path,
            task_id=TASK_ID,
            frontmatter_overrides={"sources_cited": 99},
        )
        result: VerificationResult = _run()
        assert "RI-E007" in _codes(result=result)


class TestE008IndexMissingURL:
    def test_missing_url(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        body: str = (
            "## Task Objective\n\n" + "A " * 50 + "\n\n## Gaps Addressed\n\n"
            "From research_papers.md Gaps: " + "B " * 50 + "\n\n## Search Strategy\n\n"
            "1. query one\n2. query two\n3. query three\n"
            + "C " * 50
            + "\n\n## Key Findings\n\n### Topic\n\n"
            + "D " * 100
            + " [NoUrl2024] "
            + "\n\n## Methodology Insights\n\n"
            + "E " * 100
            + "\n\n## Discovered Papers\n\n"
            + "\n\n## Recommendations for This Task\n\n"
            + "F " * 50
            + "\n\n## Source Index\n\n"
            "### [NoUrl2024]\n\n"
            "* **Type**: blog\n"
            "* **Title**: A blog post\n"
            "* **Author/Org**: Test Org\n"
            "* **Date**: 2024-01-01\n"
            "* **Peer-reviewed**: no\n"
            "* **Relevance**: Relevant.\n"
        )
        build_research_internet(
            repo_root=tmp_path,
            task_id=TASK_ID,
            body=body,
            frontmatter_overrides={
                "sources_cited": 1,
                "searches_conducted": 3,
                "papers_discovered": 0,
            },
        )
        result: VerificationResult = _run()
        assert "RI-E008" in _codes(result=result)


class TestE009Under400Words:
    def test_too_few_words(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        short_body: str = (
            "## Task Objective\n\nShort.\n"
            "## Gaps Addressed\n\nShort.\n"
            "## Search Strategy\n\nShort.\n"
            "## Key Findings\n\nShort.\n"
            "## Methodology Insights\n\nShort.\n"
            "## Discovered Papers\n\nNone.\n"
            "## Recommendations for This Task\n\nShort.\n"
            "## Source Index\n\n"
        )
        build_research_internet(
            repo_root=tmp_path,
            task_id=TASK_ID,
            body=short_body,
            frontmatter_overrides={
                "sources_cited": 0,
                "status": "partial",
            },
        )
        result: VerificationResult = _run()
        assert "RI-E009" in _codes(result=result)


class TestE010GapsNoReference:
    def test_gaps_no_research_papers_ref(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        body_no_ref: str = _VALID_INTERNET_BODY.replace(
            "research_papers.md",
            "prior analysis",
        )
        build_research_internet(
            repo_root=tmp_path,
            task_id=TASK_ID,
            body=body_no_ref,
        )
        result: VerificationResult = _run()
        assert "RI-E010" in _codes(result=result)


class TestE011NoSpecVersion:
    def test_missing_spec_version(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        research_dir: Path = tmp_path / "tasks" / TASK_ID / "research"
        research_dir.mkdir(parents=True, exist_ok=True)
        content: str = (
            "---\n"
            f'task_id: "{TASK_ID}"\n'
            'research_stage: "internet"\n'
            "searches_conducted: 3\n"
            "sources_cited: 2\n"
            "papers_discovered: 1\n"
            'date_completed: "2026-04-01"\n'
            'status: "complete"\n'
            "---\n\n" + DEFAULT_RESEARCH_INTERNET_BODY
        )
        (research_dir / "research_internet.md").write_text(content, encoding="utf-8")
        result: VerificationResult = _run()
        assert "RI-E011" in _codes(result=result)


class TestW003NoKeyFindingsSubsections:
    def test_no_subsections(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        body: str = DEFAULT_RESEARCH_INTERNET_BODY.replace(
            "### LLM-Based Approaches", "**LLM-Based Approaches**"
        ).replace("### Benchmark Updates", "**Benchmark Updates**")
        build_research_internet(
            repo_root=tmp_path,
            task_id=TASK_ID,
            body=body,
        )
        result: VerificationResult = _run()
        assert "RI-W003" in _codes(result=result)


class TestW001SectionBelowMinWords:
    def test_short_section(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        body: str = _VALID_INTERNET_BODY.replace(
            "The objective of this task is to find recent developments"
            " in word sense disambiguation not covered by existing"
            " downloaded papers.",
            "Short objective.",
        )
        build_research_internet(
            repo_root=tmp_path,
            task_id=TASK_ID,
            body=body,
            frontmatter_overrides={"searches_conducted": 3},
        )
        result: VerificationResult = _run()
        assert "RI-W001" in _codes(result=result)


class TestW002FewSearchQueries:
    def test_fewer_than_3_queries(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        body: str = _VALID_INTERNET_BODY.replace(
            '1. "word sense disambiguation" AND "large language model"\n'
            '2. "WSD" AND "prompt engineering" OR "few-shot"\n'
            '3. "Raganato benchmark" AND "2024" OR "2025"\n',
            '1. "word sense disambiguation" AND "large language model"\n',
        )
        build_research_internet(
            repo_root=tmp_path,
            task_id=TASK_ID,
            body=body,
            frontmatter_overrides={"searches_conducted": 1},
        )
        result: VerificationResult = _run()
        assert "RI-W002" in _codes(result=result)


class TestW004SourceIndexMissingPeerReviewed:
    def test_missing_peer_reviewed(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        source_no_peer: str = (
            "### [Source1]\n\n"
            "* **Type**: blog\n"
            "* **Title**: Google Scholar search results\n"
            "* **Author/Org**: Google\n"
            "* **Date**: 2024-06\n"
            "* **URL**: https://scholar.google.com/search?q=wsd\n"
            "* **Relevance**: Search results for WSD + LLM.\n"
            "\n"
            "### [Source2]\n\n"
            "* **Type**: paper\n"
            "* **Title**: arXiv preprint on word sense disambiguation\n"
            "* **Authors**: Smith et al.\n"
            "* **Year**: 2025\n"
            "* **URL**: https://arxiv.org/abs/2025.12345\n"
            "* **Peer-reviewed**: no\n"
            "* **Relevance**: Recent WSD preprint.\n"
        )
        body: str = (
            _VALID_INTERNET_BODY.split("## Source Index")[0]
            + "## Source Index\n\n"
            + source_no_peer
        )
        build_research_internet(
            repo_root=tmp_path,
            task_id=TASK_ID,
            body=body,
            frontmatter_overrides={"searches_conducted": 3},
        )
        result: VerificationResult = _run()
        assert "RI-W004" in _codes(result=result)


class TestW006PapersDiscoveredMismatch:
    def test_frontmatter_vs_section_mismatch(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        build_research_internet(
            repo_root=tmp_path,
            task_id=TASK_ID,
            body=_VALID_INTERNET_BODY,
            frontmatter_overrides={
                "searches_conducted": 3,
                "papers_discovered": 5,
            },
        )
        result: VerificationResult = _run()
        assert "RI-W006" in _codes(result=result)


class TestW007SearchesConductedMismatch:
    def test_frontmatter_vs_queries_mismatch(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        build_research_internet(
            repo_root=tmp_path,
            task_id=TASK_ID,
            body=_VALID_INTERNET_BODY,
            frontmatter_overrides={
                "searches_conducted": 99,
            },
        )
        result: VerificationResult = _run()
        assert "RI-W007" in _codes(result=result)


class TestW005UncitedSource:
    def test_uncited_source_limitation(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _setup(monkeypatch=monkeypatch, repo_root=tmp_path)
        build_task_folder(repo_root=tmp_path, task_id=TASK_ID)
        # W005 cannot easily fire because the ### [Key] heading in
        # Source Index is itself detected as an inline citation by
        # extract_inline_citations. Verify the valid body passes.
        build_research_internet(
            repo_root=tmp_path,
            task_id=TASK_ID,
            body=_VALID_INTERNET_BODY,
            frontmatter_overrides={"searches_conducted": 3},
        )
        result: VerificationResult = _run()
        assert "RI-W005" not in _codes(result=result)
