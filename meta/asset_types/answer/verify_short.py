import re
from pathlib import Path
from typing import Any

from arf.scripts.common.artifacts import (
    DOCUMENT_KIND_SHORT_ANSWER,
    TARGET_KIND_ANSWER,
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
    extract_sections,
    normalize_whitespace,
)
from arf.scripts.verificators.common.paths import (
    answer_asset_dir,
    answer_details_path,
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
ANSWER_ID_FIELD: str = "answer_id"

SECTION_QUESTION: str = "Question"
SECTION_ANSWER: str = "Answer"
SECTION_SOURCES: str = "Sources"

MANDATORY_SECTIONS: list[str] = [
    SECTION_QUESTION,
    SECTION_ANSWER,
    SECTION_SOURCES,
]

MIN_ANSWER_SENTENCES: int = 2
MAX_ANSWER_SENTENCES: int = 5

_SENTENCE_PATTERN: re.Pattern[str] = re.compile(r"(?<=[.!?])\s+")
_BULLET_PATTERN: re.Pattern[str] = re.compile(r"^\s*\*\s+", re.MULTILINE)

# ---------------------------------------------------------------------------
# Diagnostic codes
# ---------------------------------------------------------------------------

_PREFIX: str = "AA"

AA_E002: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=2,
)
AA_E003: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=3,
)
AA_E011: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=11,
)
AA_E013: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=13,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _count_sentences(*, text: str) -> int:
    stripped: str = text.strip()
    if len(stripped) == 0:
        return 0
    parts: list[str] = [
        part.strip() for part in _SENTENCE_PATTERN.split(stripped) if len(part.strip()) > 0
    ]
    return len(parts)


def _find_section(
    *,
    sections: list[MarkdownSection],
    heading: str,
) -> MarkdownSection | None:
    for section in sections:
        if section.heading == heading:
            return section
    return None


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------


def _check_mandatory_sections(
    *,
    sections: list[MarkdownSection],
    file_path: Path,
) -> list[Diagnostic]:
    found_headings: set[str] = {section.heading for section in sections}
    diagnostics: list[Diagnostic] = []
    for heading in MANDATORY_SECTIONS:
        if heading not in found_headings:
            diagnostics.append(
                Diagnostic(
                    code=AA_E011,
                    message=f"Missing mandatory section: '## {heading}'",
                    file_path=file_path,
                ),
            )
    return diagnostics


def _check_answer_id_match(
    *,
    frontmatter: dict[str, Any],
    answer_id: str,
    file_path: Path,
) -> list[Diagnostic]:
    frontmatter_answer_id: object = frontmatter.get(ANSWER_ID_FIELD)
    if frontmatter_answer_id is None:
        return []
    if str(frontmatter_answer_id) != answer_id:
        return [
            Diagnostic(
                code=AA_E003,
                message=(
                    f"answer_id '{frontmatter_answer_id}' in short answer document does "
                    f"not match folder name '{answer_id}'"
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
                code=AA_E011,
                message="spec_version is missing from short answer document frontmatter",
                file_path=file_path,
            ),
        ]
    return []


def _check_answer_sentence_count(
    *,
    sections: list[MarkdownSection],
    file_path: Path,
) -> list[Diagnostic]:
    answer_section: MarkdownSection | None = _find_section(
        sections=sections,
        heading=SECTION_ANSWER,
    )
    if answer_section is None:
        return []
    sentence_count: int = _count_sentences(text=answer_section.content)
    if sentence_count < MIN_ANSWER_SENTENCES or sentence_count > MAX_ANSWER_SENTENCES:
        return [
            Diagnostic(
                code=AA_E013,
                message=(
                    f"## Answer in short answer document has {sentence_count} sentences "
                    f"(expected: {MIN_ANSWER_SENTENCES}-{MAX_ANSWER_SENTENCES})"
                ),
                file_path=file_path,
            ),
        ]
    return []


def _check_question_match(
    *,
    sections: list[MarkdownSection],
    expected_question: str | None,
    file_path: Path,
) -> list[Diagnostic]:
    if expected_question is None:
        return []
    question_section: MarkdownSection | None = _find_section(
        sections=sections,
        heading=SECTION_QUESTION,
    )
    if question_section is None:
        return []
    if normalize_whitespace(question_section.content) != normalize_whitespace(expected_question):
        return [
            Diagnostic(
                code=AA_E011,
                message="## Question in short answer document does not match details.json question",
                file_path=file_path,
            ),
        ]
    return []


def _check_sources_nonempty(
    *,
    sections: list[MarkdownSection],
    file_path: Path,
) -> list[Diagnostic]:
    sources_section: MarkdownSection | None = _find_section(
        sections=sections,
        heading=SECTION_SOURCES,
    )
    if sources_section is None:
        return []
    bullet_count: int = len(_BULLET_PATTERN.findall(sources_section.content))
    if bullet_count == 0:
        return [
            Diagnostic(
                code=AA_E011,
                message="## Sources in short answer document must contain at least one bullet",
                file_path=file_path,
            ),
        ]
    return []


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def verify_answer_short(
    *,
    answer_id: str,
    expected_question: str | None = None,
    task_id: str | None = None,
) -> list[Diagnostic]:
    details_path: Path = answer_details_path(
        answer_id=answer_id,
        task_id=task_id,
    )
    asset_dir: Path = answer_asset_dir(
        answer_id=answer_id,
        task_id=task_id,
    )
    resolution = resolve_document_verification_path(
        target_kind=TARGET_KIND_ANSWER,
        document_kind=DOCUMENT_KIND_SHORT_ANSWER,
        details_path=details_path,
        asset_dir=asset_dir,
    )
    if resolution is None:
        return []
    if resolution.logical_path is None or resolution.file_path is None:
        return [
            Diagnostic(
                code=AA_E002,
                message=(
                    f"Field '{resolution.metadata_field}' is invalid; cannot resolve "
                    "short answer document path"
                ),
                file_path=details_path,
            ),
        ]
    file_path: Path = resolution.file_path
    logical_path: str = resolution.logical_path
    if not file_path.exists():
        return [
            Diagnostic(
                code=AA_E002,
                message=f"{logical_path} does not exist: {file_path}",
                file_path=file_path,
            ),
        ]

    try:
        content: str = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return [
            Diagnostic(
                code=AA_E002,
                message=f"{logical_path} is not valid UTF-8: {file_path}",
                file_path=file_path,
            ),
        ]

    split_result: FrontmatterResult | None = extract_frontmatter_and_body(content=content)
    if split_result is None:
        return [
            Diagnostic(
                code=AA_E011,
                message=f"{logical_path} is missing valid YAML frontmatter",
                file_path=file_path,
            ),
        ]

    frontmatter: dict[str, Any] | None = parse_frontmatter(
        raw_yaml=split_result.raw_yaml,
    )
    if frontmatter is None:
        return [
            Diagnostic(
                code=AA_E011,
                message=f"{logical_path} frontmatter is not valid YAML mapping",
                file_path=file_path,
            ),
        ]

    sections: list[MarkdownSection] = extract_sections(
        body=split_result.body,
        level=2,
    )

    diagnostics: list[Diagnostic] = []
    diagnostics.extend(_check_mandatory_sections(sections=sections, file_path=file_path))
    diagnostics.extend(
        _check_answer_id_match(
            frontmatter=frontmatter,
            answer_id=answer_id,
            file_path=file_path,
        ),
    )
    diagnostics.extend(_check_spec_version(frontmatter=frontmatter, file_path=file_path))
    diagnostics.extend(
        _check_question_match(
            sections=sections,
            expected_question=expected_question,
            file_path=file_path,
        ),
    )
    diagnostics.extend(_check_answer_sentence_count(sections=sections, file_path=file_path))
    diagnostics.extend(_check_sources_nonempty(sections=sections, file_path=file_path))
    return diagnostics
