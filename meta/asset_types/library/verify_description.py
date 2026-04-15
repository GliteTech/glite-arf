import re
from pathlib import Path
from typing import Any

from arf.scripts.common.artifacts import (
    DOCUMENT_KIND_DESCRIPTION,
    TARGET_KIND_LIBRARY,
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
    library_asset_dir,
    library_details_path,
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
LIBRARY_ID_FIELD: str = "library_id"

SECTION_METADATA: str = "Metadata"
SECTION_OVERVIEW: str = "Overview"
SECTION_API_REFERENCE: str = "API Reference"
SECTION_USAGE_EXAMPLES: str = "Usage Examples"
SECTION_DEPENDENCIES: str = "Dependencies"
SECTION_TESTING: str = "Testing"
SECTION_MAIN_IDEAS: str = "Main Ideas"
SECTION_SUMMARY: str = "Summary"

MANDATORY_SECTIONS: list[str] = [
    SECTION_METADATA,
    SECTION_OVERVIEW,
    SECTION_API_REFERENCE,
    SECTION_USAGE_EXAMPLES,
    SECTION_DEPENDENCIES,
    SECTION_TESTING,
    SECTION_MAIN_IDEAS,
    SECTION_SUMMARY,
]

MIN_TOTAL_WORDS: int = 400
MIN_MAIN_IDEAS_BULLETS: int = 3
MIN_SUMMARY_PARAGRAPHS: int = 2
MAX_SUMMARY_PARAGRAPHS: int = 3
MIN_OVERVIEW_WORDS: int = 80
MIN_API_REFERENCE_WORDS: int = 100

_BULLET_PATTERN: re.Pattern[str] = re.compile(r"^\s*\*\s+", re.MULTILINE)
_PARAGRAPH_PATTERN: re.Pattern[str] = re.compile(r"\n\n+")

# ---------------------------------------------------------------------------
# Diagnostic codes
# ---------------------------------------------------------------------------

_PREFIX: str = "LA"

LA_E002: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=2,
)
LA_E007: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=7,
)
LA_E009: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=9,
)
LA_E012: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=12,
)
LA_E013: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=13,
)
LA_W001: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=1,
)
LA_W003: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=3,
)
LA_W004: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=4,
)
LA_W013: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=13,
)
LA_W016: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=16,
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
                    code=LA_E009,
                    message=f"Missing mandatory section: '## {required}'",
                    file_path=file_path,
                ),
            )
    return diagnostics


def _check_library_id_match(
    *,
    frontmatter: dict[str, Any],
    library_id: str,
    file_path: Path,
) -> list[Diagnostic]:
    fm_id: object = frontmatter.get(LIBRARY_ID_FIELD)
    if fm_id is None:
        return []
    if str(fm_id) != library_id:
        return [
            Diagnostic(
                code=LA_E007,
                message=(
                    f"library_id '{fm_id}' in description document does not match "
                    f"folder name '{library_id}'"
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
                code=LA_E013,
                message="spec_version is missing from description document frontmatter",
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
                code=LA_W001,
                message=(f"Total word count is {total} (minimum: {MIN_TOTAL_WORDS})"),
                file_path=file_path,
            ),
        ]
    return []


def _check_main_ideas_bullets(
    *,
    sections: list[MarkdownSection],
    file_path: Path,
) -> list[Diagnostic]:
    for section in sections:
        if section.heading == SECTION_MAIN_IDEAS:
            bullet_count: int = len(
                _BULLET_PATTERN.findall(section.content),
            )
            if bullet_count < MIN_MAIN_IDEAS_BULLETS:
                return [
                    Diagnostic(
                        code=LA_W003,
                        message=(
                            f"Main Ideas section has {bullet_count} "
                            f"bullet points "
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
            paragraph_count: int = _count_paragraphs(
                text=section.content,
            )
            if paragraph_count < MIN_SUMMARY_PARAGRAPHS or paragraph_count > MAX_SUMMARY_PARAGRAPHS:
                return [
                    Diagnostic(
                        code=LA_W004,
                        message=(
                            f"Summary section has {paragraph_count} "
                            f"paragraphs (expected: "
                            f"{MIN_SUMMARY_PARAGRAPHS}-"
                            f"{MAX_SUMMARY_PARAGRAPHS})"
                        ),
                        file_path=file_path,
                    ),
                ]
            return []
    return []


def _check_overview_word_count(
    *,
    sections: list[MarkdownSection],
    file_path: Path,
) -> list[Diagnostic]:
    for section in sections:
        if section.heading == SECTION_OVERVIEW:
            word_count: int = count_words(text=section.content)
            if word_count < MIN_OVERVIEW_WORDS:
                return [
                    Diagnostic(
                        code=LA_W013,
                        message=(
                            f"Overview section has {word_count} words "
                            f"(minimum: {MIN_OVERVIEW_WORDS})"
                        ),
                        file_path=file_path,
                    ),
                ]
            return []
    return []


def _check_api_reference_word_count(
    *,
    sections: list[MarkdownSection],
    file_path: Path,
) -> list[Diagnostic]:
    for section in sections:
        if section.heading == SECTION_API_REFERENCE:
            word_count: int = count_words(text=section.content)
            if word_count < MIN_API_REFERENCE_WORDS:
                return [
                    Diagnostic(
                        code=LA_W016,
                        message=(
                            f"API Reference section has {word_count} words "
                            f"(minimum: {MIN_API_REFERENCE_WORDS})"
                        ),
                        file_path=file_path,
                    ),
                ]
            return []
    return []


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def verify_library_description(
    *,
    library_id: str,
    task_id: str | None = None,
) -> list[Diagnostic]:
    details_path: Path = library_details_path(
        library_id=library_id,
        task_id=task_id,
    )
    asset_dir: Path = library_asset_dir(
        library_id=library_id,
        task_id=task_id,
    )
    resolution = resolve_document_verification_path(
        target_kind=TARGET_KIND_LIBRARY,
        document_kind=DOCUMENT_KIND_DESCRIPTION,
        details_path=details_path,
        asset_dir=asset_dir,
    )
    if resolution is None:
        return []
    if resolution.logical_path is None or resolution.file_path is None:
        return [
            Diagnostic(
                code=LA_E002,
                message=(
                    f"Field '{resolution.metadata_field}' is invalid; cannot resolve "
                    "description document path"
                ),
                file_path=details_path,
            ),
        ]
    file_path: Path = resolution.file_path
    logical_path: str = resolution.logical_path

    if not file_path.exists():
        return [
            Diagnostic(
                code=LA_E002,
                message=f"{logical_path} does not exist: {file_path}",
                file_path=file_path,
            ),
        ]

    try:
        content: str = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return [
            Diagnostic(
                code=LA_E002,
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
                code=LA_E012,
                message=f"{logical_path} is missing YAML frontmatter",
                file_path=file_path,
            ),
        ]

    raw_yaml: str = split_result.raw_yaml
    body: str = split_result.body
    frontmatter: dict[str, Any] | None = parse_frontmatter(
        raw_yaml=raw_yaml,
    )
    if frontmatter is None:
        return [
            Diagnostic(
                code=LA_E012,
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
        _check_library_id_match(
            frontmatter=frontmatter,
            library_id=library_id,
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
    diagnostics.extend(
        _check_overview_word_count(
            sections=sections,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_api_reference_word_count(
            sections=sections,
            file_path=file_path,
        ),
    )

    return diagnostics
