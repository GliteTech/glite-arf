from pathlib import Path
from typing import Any

from arf.scripts.common.artifacts import (
    DOCUMENT_KIND_FULL_ANSWER,
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
    count_words,
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
CONFIDENCE_FIELD: str = "confidence"

SECTION_QUESTION: str = "Question"
SECTION_SHORT_ANSWER: str = "Short Answer"
SECTION_RESEARCH_PROCESS: str = "Research Process"
SECTION_EVIDENCE_PAPERS: str = "Evidence from Papers"
SECTION_EVIDENCE_INTERNET: str = "Evidence from Internet Sources"
SECTION_EVIDENCE_CODE: str = "Evidence from Code or Experiments"
SECTION_SYNTHESIS: str = "Synthesis"
SECTION_LIMITATIONS: str = "Limitations"
SECTION_SOURCES: str = "Sources"

MANDATORY_SECTIONS: list[str] = [
    SECTION_QUESTION,
    SECTION_SHORT_ANSWER,
    SECTION_RESEARCH_PROCESS,
    SECTION_EVIDENCE_PAPERS,
    SECTION_EVIDENCE_INTERNET,
    SECTION_EVIDENCE_CODE,
    SECTION_SYNTHESIS,
    SECTION_LIMITATIONS,
    SECTION_SOURCES,
]

MIN_TOTAL_WORDS: int = 300
MIN_RESEARCH_PROCESS_WORDS: int = 40
MIN_SYNTHESIS_WORDS: int = 40
MIN_LIMITATIONS_WORDS: int = 20
MIN_EVIDENCE_WORDS: int = 30
NOT_USED_TEXT: str = "not used"

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
AA_E012: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=12,
)
AA_W003: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=3,
)
AA_W004: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=4,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _find_section(
    *,
    sections: list[MarkdownSection],
    heading: str,
) -> MarkdownSection | None:
    for section in sections:
        if section.heading == heading:
            return section
    return None


def _is_substantive(*, section: MarkdownSection | None) -> bool:
    if section is None:
        return False
    content: str = section.content.strip().lower()
    if len(content) == 0:
        return False
    return NOT_USED_TEXT not in content or count_words(text=content) > 8


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
                    code=AA_E012,
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
                    f"answer_id '{frontmatter_answer_id}' in full answer document does not "
                    f"match folder name '{answer_id}'"
                ),
                file_path=file_path,
            ),
        ]
    return []


def _check_required_frontmatter(
    *,
    frontmatter: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    if frontmatter.get(SPEC_VERSION_FIELD) is None:
        diagnostics.append(
            Diagnostic(
                code=AA_E012,
                message="spec_version is missing from full answer document frontmatter",
                file_path=file_path,
            ),
        )
    if frontmatter.get(CONFIDENCE_FIELD) is None:
        diagnostics.append(
            Diagnostic(
                code=AA_E012,
                message="confidence is missing from full answer document frontmatter",
                file_path=file_path,
            ),
        )
    return diagnostics


def _check_confidence_match(
    *,
    frontmatter: dict[str, Any],
    expected_confidence: str | None,
    file_path: Path,
) -> list[Diagnostic]:
    if expected_confidence is None:
        return []
    confidence: object = frontmatter.get(CONFIDENCE_FIELD)
    if confidence is None:
        return []
    if str(confidence) != expected_confidence:
        return [
            Diagnostic(
                code=AA_E012,
                message="confidence in full answer document does not match details.json confidence",
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
                code=AA_E012,
                message="## Question in full answer document does not match details.json question",
                file_path=file_path,
            ),
        ]
    return []


def _check_total_word_count(
    *,
    body: str,
    file_path: Path,
) -> list[Diagnostic]:
    total_words: int = count_words(text=body)
    if total_words < MIN_TOTAL_WORDS:
        return [
            Diagnostic(
                code=AA_W004,
                message=(
                    f"Full answer document has {total_words} words (minimum: {MIN_TOTAL_WORDS})"
                ),
                file_path=file_path,
            ),
        ]
    return []


def _check_section_word_count(
    *,
    sections: list[MarkdownSection],
    heading: str,
    minimum_words: int,
    code: DiagnosticCode,
    file_path: Path,
) -> list[Diagnostic]:
    section: MarkdownSection | None = _find_section(sections=sections, heading=heading)
    if section is None:
        return []
    word_count: int = count_words(text=section.content)
    if word_count < minimum_words:
        return [
            Diagnostic(
                code=code,
                message=(
                    f"## {heading} has {word_count} words (minimum recommended: {minimum_words})"
                ),
                file_path=file_path,
            ),
        ]
    return []


def _check_evidence_depth(
    *,
    sections: list[MarkdownSection],
    file_path: Path,
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for heading in [
        SECTION_EVIDENCE_PAPERS,
        SECTION_EVIDENCE_INTERNET,
        SECTION_EVIDENCE_CODE,
    ]:
        section: MarkdownSection | None = _find_section(sections=sections, heading=heading)
        if section is None:
            continue
        if _is_substantive(section=section):
            word_count: int = count_words(text=section.content)
            if word_count < MIN_EVIDENCE_WORDS:
                diagnostics.append(
                    Diagnostic(
                        code=AA_W003,
                        message=(
                            f"## {heading} is present but shallow ({word_count} words; "
                            f"minimum recommended: {MIN_EVIDENCE_WORDS})"
                        ),
                        file_path=file_path,
                    ),
                )
    return diagnostics


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def verify_answer_full(
    *,
    answer_id: str,
    expected_confidence: str | None = None,
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
        document_kind=DOCUMENT_KIND_FULL_ANSWER,
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
                    "full answer document path"
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
                code=AA_E012,
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
                code=AA_E012,
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
    diagnostics.extend(_check_required_frontmatter(frontmatter=frontmatter, file_path=file_path))
    diagnostics.extend(
        _check_confidence_match(
            frontmatter=frontmatter,
            expected_confidence=expected_confidence,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_question_match(
            sections=sections,
            expected_question=expected_question,
            file_path=file_path,
        ),
    )
    diagnostics.extend(_check_total_word_count(body=split_result.body, file_path=file_path))
    diagnostics.extend(
        _check_section_word_count(
            sections=sections,
            heading=SECTION_RESEARCH_PROCESS,
            minimum_words=MIN_RESEARCH_PROCESS_WORDS,
            code=AA_W003,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_section_word_count(
            sections=sections,
            heading=SECTION_SYNTHESIS,
            minimum_words=MIN_SYNTHESIS_WORDS,
            code=AA_W003,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_section_word_count(
            sections=sections,
            heading=SECTION_LIMITATIONS,
            minimum_words=MIN_LIMITATIONS_WORDS,
            code=AA_W003,
            file_path=file_path,
        ),
    )
    diagnostics.extend(_check_evidence_depth(sections=sections, file_path=file_path))
    return diagnostics
