import re
from pathlib import Path
from typing import Any

from arf.scripts.common.artifacts import (
    DOCUMENT_KIND_SUMMARY,
    TARGET_KIND_PAPER,
)
from arf.scripts.verificators.common.canonical_documents import (
    resolve_document_verification_path,
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
    paper_asset_dir,
    paper_details_path,
)
from arf.scripts.verificators.common.types import (
    Diagnostic,
    DiagnosticCode,
    Severity,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SPEC_VERSION_FIELD: str = "spec_version"
PAPER_ID_FIELD: str = "paper_id"
CITATION_KEY_FIELD: str = "citation_key"

SECTION_METADATA: str = "Metadata"
SECTION_ABSTRACT: str = "Abstract"
SECTION_OVERVIEW: str = "Overview"
SECTION_METHODS: str = "Architecture, Models and Methods"
SECTION_RESULTS: str = "Results"
SECTION_INNOVATIONS: str = "Innovations"
SECTION_DATASETS: str = "Datasets"
SECTION_MAIN_IDEAS: str = "Main Ideas"
SECTION_SUMMARY: str = "Summary"

MANDATORY_SECTIONS: list[str] = [
    SECTION_METADATA,
    SECTION_ABSTRACT,
    SECTION_OVERVIEW,
    SECTION_METHODS,
    SECTION_RESULTS,
    SECTION_INNOVATIONS,
    SECTION_DATASETS,
    SECTION_MAIN_IDEAS,
    SECTION_SUMMARY,
]

MIN_TOTAL_WORDS: int = 500
MIN_RESULTS_BULLETS: int = 5
MIN_MAIN_IDEAS_BULLETS: int = 3
EXPECTED_SUMMARY_PARAGRAPHS: int = 4

_BULLET_PATTERN: re.Pattern[str] = re.compile(r"^\s*\*\s+", re.MULTILINE)
_PARAGRAPH_PATTERN: re.Pattern[str] = re.compile(r"\n\n+")

# ---------------------------------------------------------------------------
# Diagnostic codes
# ---------------------------------------------------------------------------

_PREFIX: str = "PA"

PA_E002: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=2,
)
PA_E006: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=6,
)
PA_E007: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=7,
)
PA_E009: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=9,
)
PA_E012: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=12,
)
PA_E013: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=13,
)
PA_W001: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=1,
)
PA_W002: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=2,
)
PA_W003: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=3,
)
PA_W004: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=4,
)


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------


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
                    code=PA_E009,
                    message=f"Missing mandatory section: '## {required}'",
                    file_path=file_path,
                ),
            )
    return diagnostics


def _check_citation_key_match(
    *,
    frontmatter: dict[str, Any],
    expected_citation_key: str | None,
    file_path: Path,
) -> list[Diagnostic]:
    if expected_citation_key is None:
        return []
    fm_key: object = frontmatter.get(CITATION_KEY_FIELD)
    if fm_key is None:
        return []
    if str(fm_key) != expected_citation_key:
        return [
            Diagnostic(
                code=PA_E006,
                message=(
                    f"citation_key '{fm_key}' in summary document does not match "
                    f"details.json citation_key '{expected_citation_key}'"
                ),
                file_path=file_path,
            ),
        ]
    return []


def _check_paper_id_match(
    *,
    frontmatter: dict[str, Any],
    paper_id: str,
    file_path: Path,
) -> list[Diagnostic]:
    fm_paper_id: object = frontmatter.get(PAPER_ID_FIELD)
    if fm_paper_id is None:
        return []
    if str(fm_paper_id) != paper_id:
        return [
            Diagnostic(
                code=PA_E007,
                message=(
                    f"paper_id '{fm_paper_id}' in summary document does not match "
                    f"folder name '{paper_id}'"
                ),
                file_path=file_path,
            ),
        ]
    return []


def _check_spec_version(
    *,
    frontmatter: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    version: object = frontmatter.get(SPEC_VERSION_FIELD)
    if version is None:
        return [
            Diagnostic(
                code=PA_E013,
                message="spec_version is missing from summary document frontmatter",
                file_path=file_path,
            ),
        ]
    return []


def _check_total_word_count(
    *,
    body: str,
    file_path: Path,
) -> list[Diagnostic]:
    total: int = count_words(text=body)
    if total < MIN_TOTAL_WORDS:
        return [
            Diagnostic(
                code=PA_W001,
                message=f"Total word count is {total} (minimum: {MIN_TOTAL_WORDS})",
                file_path=file_path,
            ),
        ]
    return []


def _check_results_bullets(
    *,
    sections: list[MarkdownSection],
    file_path: Path,
) -> list[Diagnostic]:
    for section in sections:
        if section.heading == SECTION_RESULTS:
            bullet_count: int = len(_BULLET_PATTERN.findall(section.content))
            if bullet_count < MIN_RESULTS_BULLETS:
                return [
                    Diagnostic(
                        code=PA_W002,
                        message=(
                            f"Results section has {bullet_count} bullet points "
                            f"(minimum: {MIN_RESULTS_BULLETS})"
                        ),
                        file_path=file_path,
                    ),
                ]
            return []
    return []


def _check_main_ideas_bullets(
    *,
    sections: list[MarkdownSection],
    file_path: Path,
) -> list[Diagnostic]:
    for section in sections:
        if section.heading == SECTION_MAIN_IDEAS:
            bullet_count: int = len(_BULLET_PATTERN.findall(section.content))
            if bullet_count < MIN_MAIN_IDEAS_BULLETS:
                return [
                    Diagnostic(
                        code=PA_W003,
                        message=(
                            f"Main Ideas section has {bullet_count} bullet points "
                            f"(minimum: {MIN_MAIN_IDEAS_BULLETS})"
                        ),
                        file_path=file_path,
                    ),
                ]
            return []
    return []


def _count_paragraphs(*, text: str) -> int:
    stripped: str = text.strip()
    if len(stripped) == 0:
        return 0
    paragraphs: list[str] = [
        p.strip() for p in _PARAGRAPH_PATTERN.split(stripped) if len(p.strip()) > 0
    ]
    return len(paragraphs)


def _check_summary_paragraphs(
    *,
    sections: list[MarkdownSection],
    file_path: Path,
) -> list[Diagnostic]:
    for section in sections:
        if section.heading == SECTION_SUMMARY:
            paragraph_count: int = _count_paragraphs(text=section.content)
            if paragraph_count != EXPECTED_SUMMARY_PARAGRAPHS:
                return [
                    Diagnostic(
                        code=PA_W004,
                        message=(
                            f"Summary section has {paragraph_count} paragraphs "
                            f"(expected: {EXPECTED_SUMMARY_PARAGRAPHS})"
                        ),
                        file_path=file_path,
                    ),
                ]
            return []
    return []


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def verify_paper_summary(
    *,
    paper_id: str,
    expected_citation_key: str | None = None,
    task_id: str | None = None,
) -> list[Diagnostic]:
    details_path: Path = paper_details_path(
        paper_id=paper_id,
        task_id=task_id,
    )
    asset_dir: Path = paper_asset_dir(
        paper_id=paper_id,
        task_id=task_id,
    )
    resolution = resolve_document_verification_path(
        target_kind=TARGET_KIND_PAPER,
        document_kind=DOCUMENT_KIND_SUMMARY,
        details_path=details_path,
        asset_dir=asset_dir,
    )
    if resolution is None:
        return []
    if resolution.logical_path is None or resolution.file_path is None:
        return [
            Diagnostic(
                code=PA_E002,
                message=(
                    f"Field '{resolution.metadata_field}' is invalid; cannot resolve "
                    "summary document path"
                ),
                file_path=details_path,
            ),
        ]
    file_path: Path = resolution.file_path
    logical_path: str = resolution.logical_path

    if not file_path.exists():
        return [
            Diagnostic(
                code=PA_E002,
                message=f"{logical_path} does not exist: {file_path}",
                file_path=file_path,
            ),
        ]

    try:
        content: str = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return [
            Diagnostic(
                code=PA_E002,
                message=f"{logical_path} is not valid UTF-8: {file_path}",
                file_path=file_path,
            ),
        ]

    split_result: FrontmatterResult | None = extract_frontmatter_and_body(
        content=content,
    )
    if split_result is None:
        return [
            Diagnostic(
                code=PA_E012,
                message=f"{logical_path} is missing YAML frontmatter",
                file_path=file_path,
            ),
        ]

    raw_yaml: str = split_result.raw_yaml
    body: str = split_result.body
    frontmatter: dict[str, Any] | None = parse_frontmatter(raw_yaml=raw_yaml)
    if frontmatter is None:
        return [
            Diagnostic(
                code=PA_E012,
                message=f"{logical_path} YAML frontmatter is not parseable",
                file_path=file_path,
            ),
        ]

    sections: list[MarkdownSection] = extract_sections(
        body=body,
        level=2,
    )

    diagnostics: list[Diagnostic] = []

    diagnostics.extend(
        _check_spec_version(
            frontmatter=frontmatter,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_paper_id_match(
            frontmatter=frontmatter,
            paper_id=paper_id,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_citation_key_match(
            frontmatter=frontmatter,
            expected_citation_key=expected_citation_key,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_mandatory_sections(
            sections=sections,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_total_word_count(
            body=body,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_results_bullets(
            sections=sections,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_main_ideas_bullets(
            sections=sections,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_summary_paragraphs(
            sections=sections,
            file_path=file_path,
        ),
    )

    return diagnostics
