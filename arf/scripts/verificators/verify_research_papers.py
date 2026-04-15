"""Verificator for research_papers.md files.

Usage:
    uv run python -m arf.scripts.verificators.verify_research_papers <task_id>

Exit codes:
    0 — no errors (warnings may be present)
    1 — one or more errors found
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Any

from arf.scripts.verificators.common.citation_utils import (
    SourceIndexEntry,
    extract_inline_citations,
    parse_source_index,
)
from arf.scripts.verificators.common.constants import (
    FRONTMATTER_FIELD_STATUS,
    FRONTMATTER_FIELD_TASK_ID,
    STATUS_PARTIAL,
)
from arf.scripts.verificators.common.frontmatter import (
    FrontmatterResult,
    extract_frontmatter_and_body,
    parse_frontmatter,
)
from arf.scripts.verificators.common.markdown_sections import (
    MarkdownSection,
    count_words,
    extract_sections,
)
from arf.scripts.verificators.common.paths import (
    CATEGORIES_DIR,
    TASKS_DIR,
    paper_base_dir,
    research_papers_path,
)
from arf.scripts.verificators.common.reporting import (
    exit_code_for_result,
    print_verification_result,
)
from arf.scripts.verificators.common.types import (
    Diagnostic,
    DiagnosticCode,
    Severity,
    VerificationResult,
)

# ---------------------------------------------------------------------------
# Research-papers-specific constants
# ---------------------------------------------------------------------------

FRONTMATTER_FIELD_SPEC_VERSION: str = "spec_version"
FRONTMATTER_FIELD_PAPERS_CITED: str = "papers_cited"
FRONTMATTER_FIELD_PAPERS_REVIEWED: str = "papers_reviewed"
FRONTMATTER_FIELD_CATEGORIES_CONSULTED: str = "categories_consulted"

PAPER_INDEX_FIELD_DOI: str = "doi"
PAPER_INDEX_FIELD_CATEGORIES: str = "categories"

SECTION_TASK_OBJECTIVE: str = "Task Objective"
SECTION_CATEGORY_SELECTION: str = "Category Selection Rationale"
SECTION_KEY_FINDINGS: str = "Key Findings"
SECTION_METHODOLOGY_INSIGHTS: str = "Methodology Insights"
SECTION_GAPS_LIMITATIONS: str = "Gaps and Limitations"
SECTION_RECOMMENDATIONS: str = "Recommendations for This Task"
SECTION_PAPER_INDEX: str = "Paper Index"

MANDATORY_SECTIONS: list[str] = [
    SECTION_TASK_OBJECTIVE,
    SECTION_CATEGORY_SELECTION,
    SECTION_KEY_FINDINGS,
    SECTION_METHODOLOGY_INSIGHTS,
    SECTION_GAPS_LIMITATIONS,
    SECTION_RECOMMENDATIONS,
    SECTION_PAPER_INDEX,
]

MIN_WORDS_PER_SECTION: dict[str, int] = {
    SECTION_TASK_OBJECTIVE: 30,
    SECTION_CATEGORY_SELECTION: 50,
    SECTION_KEY_FINDINGS: 200,
    SECTION_METHODOLOGY_INSIGHTS: 100,
    SECTION_GAPS_LIMITATIONS: 50,
    SECTION_RECOMMENDATIONS: 50,
    SECTION_PAPER_INDEX: 0,
}

MIN_TOTAL_WORDS: int = 300

# ---------------------------------------------------------------------------
# Diagnostic codes
# ---------------------------------------------------------------------------

_PREFIX: str = "RP"

RP_E001: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=1,
)
RP_E002: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=2,
)
RP_E003: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=3,
)
RP_E004: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=4,
)
RP_E005: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=5,
)
RP_E006: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=6,
)
RP_W007: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=7,
)
RP_E008: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=8,
)
RP_E009: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=9,
)

RP_W001: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=1,
)
RP_W002: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=2,
)
RP_W003: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=3,
)
RP_W004: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=4,
)
RP_W005: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=5,
)
RP_E010: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=10,
)

RP_W006: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=6,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_BACKTICK_STRIP: re.Pattern[str] = re.compile(r"^`+|`+$")


def _strip_backticks(value: str) -> str:
    return _BACKTICK_STRIP.sub(repl="", string=value).strip()


def _doi_to_paper_id(doi: str) -> str:
    return doi.replace("/", "_")


def _paper_asset_exists(*, paper_id: str) -> bool:
    top_level: Path = paper_base_dir(task_id=None)
    if (top_level / paper_id).is_dir():
        return True
    if TASKS_DIR.exists():
        for task_dir in TASKS_DIR.iterdir():
            if not task_dir.is_dir() or task_dir.name.startswith("."):
                continue
            candidate: Path = paper_base_dir(task_id=task_dir.name) / paper_id
            if candidate.is_dir():
                return True
    return False


def _category_exists(*, slug: str) -> bool:
    return (CATEGORIES_DIR / slug).is_dir()


def _extract_category_slugs_from_field(value: str) -> list[str]:
    parts: list[str] = value.split(",")
    slugs: list[str] = []
    for part in parts:
        cleaned: str = _strip_backticks(value=part.strip())
        if len(cleaned) > 0:
            slugs.append(cleaned)
    return slugs


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------


def _check_spec_version(
    *,
    frontmatter: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    if FRONTMATTER_FIELD_SPEC_VERSION not in frontmatter:
        return [
            Diagnostic(
                code=RP_E010,
                message="Frontmatter is missing the 'spec_version' field",
                file_path=file_path,
            ),
        ]
    return []


def _check_task_id_match(
    *,
    frontmatter: dict[str, Any],
    task_id: str,
    file_path: Path,
) -> list[Diagnostic]:
    fm_task_id: object = frontmatter.get(FRONTMATTER_FIELD_TASK_ID)
    if fm_task_id is None:
        return [
            Diagnostic(
                code=RP_E003,
                message="Frontmatter is missing the 'task_id' field",
                file_path=file_path,
            ),
        ]
    if str(fm_task_id) != task_id:
        return [
            Diagnostic(
                code=RP_E003,
                message=(
                    f"Frontmatter task_id '{fm_task_id}' does not match task folder '{task_id}'"
                ),
                file_path=file_path,
            ),
        ]
    return []


def _check_mandatory_sections(
    *,
    sections: list[MarkdownSection],
    file_path: Path,
) -> list[Diagnostic]:
    found_headings: set[str] = {s.heading for s in sections}
    diagnostics: list[Diagnostic] = []
    for required in MANDATORY_SECTIONS:
        if required not in found_headings:
            diagnostics.append(
                Diagnostic(
                    code=RP_E004,
                    message=f"Missing mandatory section: '## {required}'",
                    file_path=file_path,
                ),
            )
    return diagnostics


def _check_papers_cited(
    *,
    frontmatter: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    papers_cited: object = frontmatter.get(FRONTMATTER_FIELD_PAPERS_CITED)
    status: object = frontmatter.get(FRONTMATTER_FIELD_STATUS)
    if isinstance(papers_cited, int) and papers_cited < 1 and str(status) != STATUS_PARTIAL:
        return [
            Diagnostic(
                code=RP_E005,
                message="papers_cited is 0 but status is not 'partial'",
                file_path=file_path,
            ),
        ]
    return []


def _check_inline_citations(
    *,
    body: str,
    paper_entries: list[SourceIndexEntry],
    file_path: Path,
) -> list[Diagnostic]:
    inline_keys: set[str] = extract_inline_citations(text=body)
    index_keys: set[str] = {entry.key for entry in paper_entries}
    diagnostics: list[Diagnostic] = []
    for key in sorted(inline_keys - index_keys):
        diagnostics.append(
            Diagnostic(
                code=RP_E006,
                message=f"Inline citation [{key}] has no matching Paper Index entry",
                file_path=file_path,
            ),
        )
    return diagnostics


def _check_paper_count(
    *,
    frontmatter: dict[str, Any],
    paper_entries: list[SourceIndexEntry],
    file_path: Path,
) -> list[Diagnostic]:
    papers_cited: object = frontmatter.get(FRONTMATTER_FIELD_PAPERS_CITED)
    if not isinstance(papers_cited, int):
        return [
            Diagnostic(
                code=RP_W007,
                message="Frontmatter is missing or has non-integer 'papers_cited'",
                file_path=file_path,
            ),
        ]
    actual_count: int = len(paper_entries)
    if actual_count != papers_cited:
        return [
            Diagnostic(
                code=RP_W007,
                message=(
                    f"Paper Index has {actual_count} entries "
                    f"but frontmatter says papers_cited={papers_cited}"
                ),
                file_path=file_path,
            ),
        ]
    return []


def _check_paper_doi(
    *,
    paper_entries: list[SourceIndexEntry],
    file_path: Path,
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for entry in paper_entries:
        if PAPER_INDEX_FIELD_DOI not in entry.fields:
            diagnostics.append(
                Diagnostic(
                    code=RP_E008,
                    message=(f"Paper Index entry [{entry.key}] is missing the DOI field"),
                    file_path=file_path,
                ),
            )
    return diagnostics


def _check_total_word_count(
    *,
    body: str,
    file_path: Path,
) -> list[Diagnostic]:
    total: int = count_words(text=body)
    if total < MIN_TOTAL_WORDS:
        return [
            Diagnostic(
                code=RP_E009,
                message=(f"Total content has {total} words (minimum: {MIN_TOTAL_WORDS})"),
                file_path=file_path,
            ),
        ]
    return []


def _check_section_word_counts(
    *,
    sections: list[MarkdownSection],
    file_path: Path,
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for section in sections:
        min_words: int | None = MIN_WORDS_PER_SECTION.get(section.heading)
        if min_words is None or min_words == 0:
            continue
        actual: int = count_words(text=section.content)
        if actual < min_words:
            diagnostics.append(
                Diagnostic(
                    code=RP_W001,
                    message=(
                        f"Section '{section.heading}' has {actual} words (minimum: {min_words})"
                    ),
                    file_path=file_path,
                ),
            )
    return diagnostics


def _check_doi_paper_asset(
    *,
    paper_entries: list[SourceIndexEntry],
    file_path: Path,
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for entry in paper_entries:
        raw_doi: str | None = entry.fields.get(PAPER_INDEX_FIELD_DOI)
        if raw_doi is None:
            continue
        doi: str = _strip_backticks(value=raw_doi)
        if len(doi) == 0:
            continue
        paper_id: str = _doi_to_paper_id(doi=doi)
        if not _paper_asset_exists(paper_id=paper_id):
            diagnostics.append(
                Diagnostic(
                    code=RP_W002,
                    message=(
                        f"Paper Index entry [{entry.key}] has DOI '{doi}' "
                        f"but no paper asset folder '{paper_id}' was found"
                    ),
                    file_path=file_path,
                ),
            )
    return diagnostics


def _check_categories_exist(
    *,
    frontmatter: dict[str, Any],
    paper_entries: list[SourceIndexEntry],
    file_path: Path,
) -> list[Diagnostic]:
    slugs_to_check: set[str] = set()

    categories_consulted: object = frontmatter.get(
        FRONTMATTER_FIELD_CATEGORIES_CONSULTED,
    )
    if isinstance(categories_consulted, list):
        for item in categories_consulted:
            slugs_to_check.add(str(item))

    for entry in paper_entries:
        raw_categories: str | None = entry.fields.get(PAPER_INDEX_FIELD_CATEGORIES)
        if raw_categories is not None:
            slugs_to_check.update(
                _extract_category_slugs_from_field(value=raw_categories),
            )

    diagnostics: list[Diagnostic] = []
    for slug in sorted(slugs_to_check):
        if not _category_exists(slug=slug):
            diagnostics.append(
                Diagnostic(
                    code=RP_W003,
                    message=(f"Category '{slug}' does not exist in {CATEGORIES_DIR}"),
                    file_path=file_path,
                ),
            )
    return diagnostics


def _check_papers_reviewed_vs_cited(
    *,
    frontmatter: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    papers_reviewed: object = frontmatter.get(FRONTMATTER_FIELD_PAPERS_REVIEWED)
    papers_cited: object = frontmatter.get(FRONTMATTER_FIELD_PAPERS_CITED)
    if (
        isinstance(papers_reviewed, int)
        and isinstance(papers_cited, int)
        and papers_reviewed < papers_cited
    ):
        return [
            Diagnostic(
                code=RP_W004,
                message=(
                    f"papers_reviewed ({papers_reviewed}) < papers_cited "
                    f"({papers_cited}) — likely a frontmatter error"
                ),
                file_path=file_path,
            ),
        ]
    return []


def _check_key_findings_subsections(
    *,
    sections: list[MarkdownSection],
    file_path: Path,
) -> list[Diagnostic]:
    for section in sections:
        if section.heading == SECTION_KEY_FINDINGS:
            if re.search(r"^### ", section.content, re.MULTILINE) is None:
                return [
                    Diagnostic(
                        code=RP_W005,
                        message=("'## Key Findings' section contains no ### subsections"),
                        file_path=file_path,
                    ),
                ]
            return []
    return []


def _check_uncited_papers(
    *,
    body: str,
    paper_entries: list[SourceIndexEntry],
    file_path: Path,
) -> list[Diagnostic]:
    inline_keys: set[str] = extract_inline_citations(text=body)
    diagnostics: list[Diagnostic] = []
    for entry in paper_entries:
        if entry.key not in inline_keys:
            diagnostics.append(
                Diagnostic(
                    code=RP_W006,
                    message=(f"Paper Index entry [{entry.key}] is never cited in body text"),
                    file_path=file_path,
                ),
            )
    return diagnostics


# ---------------------------------------------------------------------------
# Main verification function
# ---------------------------------------------------------------------------


def verify_research_papers(
    *,
    task_id: str,
) -> VerificationResult:
    file_path: Path = research_papers_path(task_id=task_id)
    diagnostics: list[Diagnostic] = []

    # E001: File existence
    if not file_path.exists():
        diagnostics.append(
            Diagnostic(
                code=RP_E001,
                message=f"File does not exist: {file_path}",
                file_path=file_path,
            ),
        )
        return VerificationResult(
            file_path=file_path,
            diagnostics=diagnostics,
        )

    try:
        content: str = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        diagnostics.append(
            Diagnostic(
                code=RP_E002,
                message=f"File is not valid UTF-8: {exc}",
                file_path=file_path,
            ),
        )
        return VerificationResult(
            file_path=file_path,
            diagnostics=diagnostics,
        )

    # E002: Frontmatter parsing
    split_result: FrontmatterResult | None = extract_frontmatter_and_body(
        content=content,
    )
    if split_result is None:
        diagnostics.append(
            Diagnostic(
                code=RP_E002,
                message="YAML frontmatter is missing or has invalid delimiters",
                file_path=file_path,
            ),
        )
        return VerificationResult(
            file_path=file_path,
            diagnostics=diagnostics,
        )

    raw_yaml: str = split_result.raw_yaml
    body: str = split_result.body
    frontmatter: dict[str, Any] | None = parse_frontmatter(raw_yaml=raw_yaml)
    if frontmatter is None:
        diagnostics.append(
            Diagnostic(
                code=RP_E002,
                message="YAML frontmatter is not parseable",
                file_path=file_path,
            ),
        )
        return VerificationResult(
            file_path=file_path,
            diagnostics=diagnostics,
        )

    # Extract sections and Paper Index (used by many checks)
    sections: list[MarkdownSection] = extract_sections(
        body=body,
        level=2,
    )
    paper_index_content: str = ""
    for section in sections:
        if section.heading == SECTION_PAPER_INDEX:
            paper_index_content = section.content
            break
    paper_entries: list[SourceIndexEntry] = parse_source_index(
        section_content=paper_index_content,
    )

    # E010: spec_version
    diagnostics.extend(
        _check_spec_version(
            frontmatter=frontmatter,
            file_path=file_path,
        ),
    )

    # E003: task_id match
    diagnostics.extend(
        _check_task_id_match(
            frontmatter=frontmatter,
            task_id=task_id,
            file_path=file_path,
        ),
    )

    # E004: Mandatory sections
    diagnostics.extend(
        _check_mandatory_sections(
            sections=sections,
            file_path=file_path,
        ),
    )

    # E005: papers_cited < 1 with non-partial status
    diagnostics.extend(
        _check_papers_cited(
            frontmatter=frontmatter,
            file_path=file_path,
        ),
    )

    # E006: Inline citations without Paper Index match
    diagnostics.extend(
        _check_inline_citations(
            body=body,
            paper_entries=paper_entries,
            file_path=file_path,
        ),
    )

    # E007: Paper Index count mismatch
    diagnostics.extend(
        _check_paper_count(
            frontmatter=frontmatter,
            paper_entries=paper_entries,
            file_path=file_path,
        ),
    )

    # E008: Paper Index entries missing DOI
    diagnostics.extend(
        _check_paper_doi(
            paper_entries=paper_entries,
            file_path=file_path,
        ),
    )

    # E009: Total word count
    diagnostics.extend(
        _check_total_word_count(
            body=body,
            file_path=file_path,
        ),
    )

    # W001: Section word counts
    diagnostics.extend(
        _check_section_word_counts(
            sections=sections,
            file_path=file_path,
        ),
    )

    # W002: DOI-to-paper-asset mapping
    diagnostics.extend(
        _check_doi_paper_asset(
            paper_entries=paper_entries,
            file_path=file_path,
        ),
    )

    # W003: Category existence
    diagnostics.extend(
        _check_categories_exist(
            frontmatter=frontmatter,
            paper_entries=paper_entries,
            file_path=file_path,
        ),
    )

    # W004: papers_reviewed < papers_cited
    diagnostics.extend(
        _check_papers_reviewed_vs_cited(
            frontmatter=frontmatter,
            file_path=file_path,
        ),
    )

    # W005: Key Findings subsections
    diagnostics.extend(
        _check_key_findings_subsections(
            sections=sections,
            file_path=file_path,
        ),
    )

    # W006: Uncited Paper Index entries
    diagnostics.extend(
        _check_uncited_papers(
            body=body,
            paper_entries=paper_entries,
            file_path=file_path,
        ),
    )

    return VerificationResult(
        file_path=file_path,
        diagnostics=diagnostics,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Verify research_papers.md for a given task",
    )
    parser.add_argument(
        "task_id",
        help="Task ID (e.g. 0008-baseline-sentiment-classifier)",
    )
    args: argparse.Namespace = parser.parse_args()

    result: VerificationResult = verify_research_papers(
        task_id=args.task_id,
    )
    print_verification_result(result=result)
    sys.exit(exit_code_for_result(result=result))


if __name__ == "__main__":
    main()
