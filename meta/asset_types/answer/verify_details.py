import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from arf.scripts.verificators.common.json_utils import (
    check_required_fields,
    load_json_file,
)
from arf.scripts.verificators.common.markdown_sections import count_words
from arf.scripts.verificators.common.paths import (
    CATEGORIES_DIR,
    TASKS_DIR,
    answer_asset_dir,
    answer_details_path,
    paper_base_dir,
)
from arf.scripts.verificators.common.types import (
    Diagnostic,
    DiagnosticCode,
    Severity,
)

type AnswerID = str
type PaperID = str
type TaskID = str

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SPEC_VERSION_FIELD: str = "spec_version"
ANSWER_ID_FIELD: str = "answer_id"
QUESTION_FIELD: str = "question"
SHORT_TITLE_FIELD: str = "short_title"
CATEGORIES_FIELD: str = "categories"
SHORT_ANSWER_PATH_FIELD: str = "short_answer_path"
FULL_ANSWER_PATH_FIELD: str = "full_answer_path"
ANSWER_METHODS_FIELD: str = "answer_methods"
SOURCE_PAPER_IDS_FIELD: str = "source_paper_ids"
SOURCE_URLS_FIELD: str = "source_urls"
SOURCE_TASK_IDS_FIELD: str = "source_task_ids"
CONFIDENCE_FIELD: str = "confidence"
CREATED_BY_TASK_FIELD: str = "created_by_task"
DATE_CREATED_FIELD: str = "date_created"
LEGACY_SPEC_VERSION: str = "1"

REQUIRED_FIELDS: list[str] = [
    SPEC_VERSION_FIELD,
    ANSWER_ID_FIELD,
    QUESTION_FIELD,
    SHORT_TITLE_FIELD,
    CATEGORIES_FIELD,
    ANSWER_METHODS_FIELD,
    SOURCE_PAPER_IDS_FIELD,
    SOURCE_URLS_FIELD,
    SOURCE_TASK_IDS_FIELD,
    CONFIDENCE_FIELD,
    CREATED_BY_TASK_FIELD,
    DATE_CREATED_FIELD,
]

ALLOWED_ANSWER_METHODS: set[str] = {"papers", "internet", "code-experiment"}
ALLOWED_CONFIDENCE_VALUES: set[str] = {"high", "medium", "low"}

MIN_QUESTION_WORDS: int = 5
MIN_SHORT_TITLE_WORDS: int = 2

_ANSWER_ID_PATTERN: re.Pattern[str] = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
_DATE_ISO_PATTERN: re.Pattern[str] = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# ---------------------------------------------------------------------------
# Diagnostic codes
# ---------------------------------------------------------------------------

_PREFIX: str = "AA"

AA_E001: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=1,
)
AA_E003: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=3,
)
AA_E004: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=4,
)
AA_E005: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=5,
)
AA_E006: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=6,
)
AA_E007: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=7,
)
AA_E008: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=8,
)
AA_E009: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=9,
)
AA_E010: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=10,
)
AA_E013: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=13,
)
AA_E014: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=14,
)

AA_W001: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=1,
)
AA_W002: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=2,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _paper_id_exists(*, paper_id: PaperID) -> bool:
    if len(paper_id) == 0:
        return False
    if TASKS_DIR.exists():
        for task_dir in TASKS_DIR.iterdir():
            if not task_dir.is_dir() or task_dir.name.startswith("."):
                continue
            if (paper_base_dir(task_id=task_dir.name) / paper_id).exists():
                return True
    return (paper_base_dir(task_id=None) / paper_id).exists()


def _is_valid_http_url(*, url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and len(parsed.netloc) > 0


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------


def _check_answer_id_format(
    *,
    answer_id: AnswerID,
    file_path: Path,
) -> list[Diagnostic]:
    if _ANSWER_ID_PATTERN.match(answer_id) is None:
        return [
            Diagnostic(
                code=AA_E004,
                message=(
                    f"Folder name '{answer_id}' does not match answer ID format "
                    "(lowercase letters, digits, hyphens)"
                ),
                file_path=file_path,
            ),
        ]
    return []


def _check_answer_id_match(
    *,
    data: dict[str, Any],
    answer_id: AnswerID,
    file_path: Path,
) -> list[Diagnostic]:
    json_id: object = data.get(ANSWER_ID_FIELD)
    if json_id is None:
        return []
    if str(json_id) != answer_id:
        return [
            Diagnostic(
                code=AA_E003,
                message=f"answer_id '{json_id}' does not match folder name '{answer_id}'",
                file_path=file_path,
            ),
        ]
    return []


def _check_required_fields_answer(
    *,
    data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    missing: list[str] = check_required_fields(
        data=data,
        required_fields=REQUIRED_FIELDS,
    )
    diagnostics: list[Diagnostic] = []
    for field_name in missing:
        diagnostics.append(
            Diagnostic(
                code=AA_E005,
                message=f"Required field missing: '{field_name}'",
                file_path=file_path,
            ),
        )
    return diagnostics


def _check_spec_version(
    *,
    data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    version: object = data.get(SPEC_VERSION_FIELD)
    if version is None:
        return [
            Diagnostic(
                code=AA_E013,
                message="spec_version is missing from details.json",
                file_path=file_path,
            ),
        ]
    return []


def _check_document_path_fields(
    *,
    data: dict[str, Any],
    answer_id: AnswerID,
    task_id: TaskID | None,
    file_path: Path,
) -> list[Diagnostic]:
    version: object = data.get(SPEC_VERSION_FIELD)
    asset_dir: Path = answer_asset_dir(answer_id=answer_id, task_id=task_id)
    diagnostics: list[Diagnostic] = []
    for field_name in [SHORT_ANSWER_PATH_FIELD, FULL_ANSWER_PATH_FIELD]:
        value: object = data.get(field_name)
        if (
            isinstance(version, str)
            and version != LEGACY_SPEC_VERSION
            and (not isinstance(value, str) or len(value.strip()) == 0)
        ):
            diagnostics.append(
                Diagnostic(
                    code=AA_E005,
                    message=f"Required string field missing: '{field_name}'",
                    file_path=file_path,
                ),
            )
            continue
        if value is None:
            continue
        if not isinstance(value, str) or len(value.strip()) == 0:
            diagnostics.append(
                Diagnostic(
                    code=AA_E005,
                    message=f"Field '{field_name}' must be a non-empty string",
                    file_path=file_path,
                ),
            )
            continue
        declared_path: Path = asset_dir / value
        if not declared_path.exists():
            diagnostics.append(
                Diagnostic(
                    code=AA_E005,
                    message=f"Declared document path does not exist: '{value}'",
                    file_path=file_path,
                ),
            )
    return diagnostics


def _check_question_length(
    *,
    data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    question: object = data.get(QUESTION_FIELD)
    if not isinstance(question, str):
        return []
    word_count: int = count_words(text=question)
    if word_count < MIN_QUESTION_WORDS:
        return [
            Diagnostic(
                code=AA_W002,
                message=(
                    f"Question has {word_count} words (minimum recommended: {MIN_QUESTION_WORDS})"
                ),
                file_path=file_path,
            ),
        ]
    return []


def _check_short_title_length(
    *,
    data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    short_title: object = data.get(SHORT_TITLE_FIELD)
    if not isinstance(short_title, str):
        return []
    word_count: int = count_words(text=short_title)
    if word_count < MIN_SHORT_TITLE_WORDS:
        return [
            Diagnostic(
                code=AA_W002,
                message=(
                    f"short_title has {word_count} word(s) (minimum recommended: "
                    f"{MIN_SHORT_TITLE_WORDS})"
                ),
                file_path=file_path,
            ),
        ]
    return []


def _check_answer_methods(
    *,
    data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    methods: object = data.get(ANSWER_METHODS_FIELD)
    if not isinstance(methods, list):
        return []
    diagnostics: list[Diagnostic] = []
    for method in methods:
        if not isinstance(method, str) or method not in ALLOWED_ANSWER_METHODS:
            diagnostics.append(
                Diagnostic(
                    code=AA_E006,
                    message=(
                        f"answer_methods contains invalid value '{method}'; allowed: "
                        f"{', '.join(sorted(ALLOWED_ANSWER_METHODS))}"
                    ),
                    file_path=file_path,
                ),
            )
    return diagnostics


def _check_confidence(
    *,
    data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    confidence: object = data.get(CONFIDENCE_FIELD)
    if not isinstance(confidence, str):
        return []
    if confidence not in ALLOWED_CONFIDENCE_VALUES:
        return [
            Diagnostic(
                code=AA_E007,
                message=(
                    f"confidence '{confidence}' is not one of: "
                    f"{', '.join(sorted(ALLOWED_CONFIDENCE_VALUES))}"
                ),
                file_path=file_path,
            ),
        ]
    return []


def _check_source_tasks(
    *,
    data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    source_task_ids: object = data.get(SOURCE_TASK_IDS_FIELD)
    if not isinstance(source_task_ids, list):
        return []
    diagnostics: list[Diagnostic] = []
    for task_id in source_task_ids:
        if not isinstance(task_id, str):
            diagnostics.append(
                Diagnostic(
                    code=AA_E008,
                    message="source_task_ids contains a non-string value",
                    file_path=file_path,
                ),
            )
            continue
        if not (TASKS_DIR / task_id).exists():
            diagnostics.append(
                Diagnostic(
                    code=AA_E008,
                    message=f"Referenced task does not exist: '{task_id}'",
                    file_path=file_path,
                ),
            )
    return diagnostics


def _check_source_papers(
    *,
    data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    source_paper_ids: object = data.get(SOURCE_PAPER_IDS_FIELD)
    if not isinstance(source_paper_ids, list):
        return []
    diagnostics: list[Diagnostic] = []
    for paper_id in source_paper_ids:
        if not isinstance(paper_id, str):
            diagnostics.append(
                Diagnostic(
                    code=AA_E009,
                    message="source_paper_ids contains a non-string value",
                    file_path=file_path,
                ),
            )
            continue
        if not _paper_id_exists(paper_id=paper_id):
            diagnostics.append(
                Diagnostic(
                    code=AA_E009,
                    message=f"Referenced paper does not exist: '{paper_id}'",
                    file_path=file_path,
                ),
            )
    return diagnostics


def _check_source_urls(
    *,
    data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    source_urls: object = data.get(SOURCE_URLS_FIELD)
    if not isinstance(source_urls, list):
        return []
    diagnostics: list[Diagnostic] = []
    for url in source_urls:
        if not isinstance(url, str) or not _is_valid_http_url(url=url):
            diagnostics.append(
                Diagnostic(
                    code=AA_E010,
                    message=f"Referenced URL is not valid HTTP or HTTPS: '{url}'",
                    file_path=file_path,
                ),
            )
    return diagnostics


def _check_categories_exist(
    *,
    data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    categories: object = data.get(CATEGORIES_FIELD)
    if not isinstance(categories, list):
        return []
    diagnostics: list[Diagnostic] = []
    for category in categories:
        if not isinstance(category, str):
            continue
        if not (CATEGORIES_DIR / category).exists():
            diagnostics.append(
                Diagnostic(
                    code=AA_W001,
                    message=f"Category '{category}' does not exist in meta/categories/",
                    file_path=file_path,
                ),
            )
    return diagnostics


def _check_evidence_presence(
    *,
    data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    source_paper_ids: object = data.get(SOURCE_PAPER_IDS_FIELD)
    source_urls: object = data.get(SOURCE_URLS_FIELD)
    source_task_ids: object = data.get(SOURCE_TASK_IDS_FIELD)
    paper_count: int = len(source_paper_ids) if isinstance(source_paper_ids, list) else 0
    url_count: int = len(source_urls) if isinstance(source_urls, list) else 0
    task_count: int = len(source_task_ids) if isinstance(source_task_ids, list) else 0
    if paper_count + url_count + task_count == 0:
        return [
            Diagnostic(
                code=AA_E014,
                message=(
                    "At least one evidence reference is required across "
                    "source_paper_ids, source_urls, and source_task_ids"
                ),
                file_path=file_path,
            ),
        ]
    return []


def _check_created_by_task(
    *,
    data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    task_id: object = data.get(CREATED_BY_TASK_FIELD)
    if not isinstance(task_id, str):
        return []
    if not (TASKS_DIR / task_id).exists():
        return [
            Diagnostic(
                code=AA_E008,
                message=f"created_by_task does not exist: '{task_id}'",
                file_path=file_path,
            ),
        ]
    return []


def _check_date_created(
    *,
    data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    date_created: object = data.get(DATE_CREATED_FIELD)
    if not isinstance(date_created, str):
        return []
    if _DATE_ISO_PATTERN.match(date_created) is None:
        return [
            Diagnostic(
                code=AA_E005,
                message=(f"date_created '{date_created}' is not a valid ISO date (YYYY-MM-DD)"),
                file_path=file_path,
            ),
        ]
    return []


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def verify_answer_details(
    *,
    answer_id: AnswerID,
    task_id: TaskID | None = None,
) -> list[Diagnostic]:
    file_path: Path = answer_details_path(
        answer_id=answer_id,
        task_id=task_id,
    )
    data: dict[str, Any] | None = load_json_file(file_path=file_path)
    if data is None:
        return [
            Diagnostic(
                code=AA_E001,
                message=f"details.json does not exist or is not valid JSON: {file_path}",
                file_path=file_path,
            ),
        ]

    diagnostics: list[Diagnostic] = []
    diagnostics.extend(_check_answer_id_format(answer_id=answer_id, file_path=file_path))
    diagnostics.extend(
        _check_answer_id_match(
            data=data,
            answer_id=answer_id,
            file_path=file_path,
        ),
    )
    diagnostics.extend(_check_required_fields_answer(data=data, file_path=file_path))
    diagnostics.extend(_check_spec_version(data=data, file_path=file_path))
    diagnostics.extend(
        _check_document_path_fields(
            data=data,
            answer_id=answer_id,
            task_id=task_id,
            file_path=file_path,
        ),
    )
    diagnostics.extend(_check_question_length(data=data, file_path=file_path))
    diagnostics.extend(_check_short_title_length(data=data, file_path=file_path))
    diagnostics.extend(_check_answer_methods(data=data, file_path=file_path))
    diagnostics.extend(_check_confidence(data=data, file_path=file_path))
    diagnostics.extend(_check_source_tasks(data=data, file_path=file_path))
    diagnostics.extend(_check_source_papers(data=data, file_path=file_path))
    diagnostics.extend(_check_source_urls(data=data, file_path=file_path))
    diagnostics.extend(_check_categories_exist(data=data, file_path=file_path))
    diagnostics.extend(_check_evidence_presence(data=data, file_path=file_path))
    diagnostics.extend(_check_created_by_task(data=data, file_path=file_path))
    diagnostics.extend(_check_date_created(data=data, file_path=file_path))
    return diagnostics
