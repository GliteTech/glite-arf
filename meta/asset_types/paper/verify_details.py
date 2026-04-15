import re
from pathlib import Path
from typing import Any

from arf.scripts.verificators.common.json_utils import (
    check_required_fields,
    load_json_file,
)
from arf.scripts.verificators.common.markdown_sections import count_words
from arf.scripts.verificators.common.paths import (
    CATEGORIES_DIR,
    paper_asset_dir,
    paper_details_path,
    paper_files_dir,
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
DOI_FIELD: str = "doi"
TITLE_FIELD: str = "title"
URL_FIELD: str = "url"
YEAR_FIELD: str = "year"
AUTHORS_FIELD: str = "authors"
INSTITUTIONS_FIELD: str = "institutions"
JOURNAL_FIELD: str = "journal"
VENUE_TYPE_FIELD: str = "venue_type"
CATEGORIES_FIELD: str = "categories"
ABSTRACT_FIELD: str = "abstract"
CITATION_KEY_FIELD: str = "citation_key"
SUMMARY_PATH_FIELD: str = "summary_path"
FILES_FIELD: str = "files"
DOWNLOAD_STATUS_FIELD: str = "download_status"
DOWNLOAD_FAILURE_REASON_FIELD: str = "download_failure_reason"
ADDED_BY_TASK_FIELD: str = "added_by_task"
DATE_ADDED_FIELD: str = "date_added"
DATE_PUBLISHED_FIELD: str = "date_published"
COUNTRY_FIELD: str = "country"
NAME_FIELD: str = "name"
LEGACY_SPEC_VERSION: str = "2"

ALLOWED_DOWNLOAD_STATUSES: list[str] = [
    "success",
    "failed",
]

REQUIRED_FIELDS: list[str] = [
    SPEC_VERSION_FIELD,
    PAPER_ID_FIELD,
    DOI_FIELD,
    TITLE_FIELD,
    URL_FIELD,
    YEAR_FIELD,
    AUTHORS_FIELD,
    INSTITUTIONS_FIELD,
    JOURNAL_FIELD,
    VENUE_TYPE_FIELD,
    CATEGORIES_FIELD,
    ABSTRACT_FIELD,
    CITATION_KEY_FIELD,
    FILES_FIELD,
    DOWNLOAD_STATUS_FIELD,
    DOWNLOAD_FAILURE_REASON_FIELD,
    ADDED_BY_TASK_FIELD,
    DATE_ADDED_FIELD,
]

ALLOWED_VENUE_TYPES: list[str] = [
    "journal",
    "conference",
    "workshop",
    "preprint",
    "book",
    "thesis",
    "technical_report",
    "other",
]

NO_DOI_PREFIX: str = "no-doi_"

MIN_ABSTRACT_WORDS: int = 50

_SLASH_PATTERN: re.Pattern[str] = re.compile(r"/")
_COUNTRY_CODE_PATTERN: re.Pattern[str] = re.compile(r"^[A-Z]{2}$")
_DATE_ISO_PATTERN: re.Pattern[str] = re.compile(r"^\d{4}(-\d{2}(-\d{2})?)?$")

# ---------------------------------------------------------------------------
# Diagnostic codes
# ---------------------------------------------------------------------------

_PREFIX: str = "PA"

PA_E001: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=1,
)
PA_E004: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=4,
)
PA_E005: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=5,
)
PA_E008: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=8,
)
PA_E010: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=10,
)
PA_E011: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=11,
)
PA_E013: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=13,
)
PA_E014: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=14,
)
PA_W005: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=5,
)
PA_W006: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=6,
)
PA_W007: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=7,
)
PA_W008: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=8,
)
PA_W009: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=9,
)
PA_E015: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=15,
)
PA_W010: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=10,
)
PA_W011: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=11,
)


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------


def _check_paper_id_match(
    *,
    data: dict[str, Any],
    paper_id: str,
    file_path: Path,
) -> list[Diagnostic]:
    json_paper_id: object = data.get(PAPER_ID_FIELD)
    if json_paper_id is None:
        return []  # Already reported by required-fields check.
    if str(json_paper_id) != paper_id:
        return [
            Diagnostic(
                code=PA_E004,
                message=(f"paper_id '{json_paper_id}' does not match folder name '{paper_id}'"),
                file_path=file_path,
            ),
        ]
    return []


def _check_required_fields(
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
                code=PA_E005,
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
                code=PA_E013,
                message="spec_version is missing from details.json",
                file_path=file_path,
            ),
        ]
    return []


def _check_summary_path_field(
    *,
    data: dict[str, Any],
    paper_id: str,
    task_id: str | None,
    file_path: Path,
) -> list[Diagnostic]:
    version: object = data.get(SPEC_VERSION_FIELD)
    value: object = data.get(SUMMARY_PATH_FIELD)
    if (
        isinstance(version, str)
        and version != LEGACY_SPEC_VERSION
        and (not isinstance(value, str) or len(value.strip()) == 0)
    ):
        return [
            Diagnostic(
                code=PA_E005,
                message=f"Required string field missing: '{SUMMARY_PATH_FIELD}'",
                file_path=file_path,
            ),
        ]
    if value is None:
        return []
    if not isinstance(value, str) or len(value.strip()) == 0:
        return [
            Diagnostic(
                code=PA_E005,
                message=f"Field '{SUMMARY_PATH_FIELD}' must be a non-empty string",
                file_path=file_path,
            ),
        ]
    declared_path: Path = (
        paper_asset_dir(
            paper_id=paper_id,
            task_id=task_id,
        )
        / value
    )
    if not declared_path.exists():
        return [
            Diagnostic(
                code=PA_E008,
                message=f"Declared summary path does not exist: '{value}'",
                file_path=file_path,
            ),
        ]
    return []


def _check_files_exist(
    *,
    data: dict[str, Any],
    paper_id: str,
    task_id: str | None,
    file_path: Path,
) -> list[Diagnostic]:
    files: object = data.get(FILES_FIELD)
    if not isinstance(files, list):
        return []
    files_dir: Path = paper_files_dir(paper_id=paper_id, task_id=task_id)
    diagnostics: list[Diagnostic] = []
    for entry in files:
        if not isinstance(entry, str):
            continue
        full_path: Path = files_dir.parent / entry
        if not full_path.exists():
            diagnostics.append(
                Diagnostic(
                    code=PA_E008,
                    message=f"Listed file does not exist: '{entry}'",
                    file_path=file_path,
                ),
            )
    return diagnostics


def _check_venue_type(
    *,
    data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    venue_type: object = data.get(VENUE_TYPE_FIELD)
    if venue_type is None:
        return []  # Already reported by required-fields check.
    if str(venue_type) not in ALLOWED_VENUE_TYPES:
        return [
            Diagnostic(
                code=PA_E010,
                message=(
                    f"venue_type '{venue_type}' is not one of: {', '.join(ALLOWED_VENUE_TYPES)}"
                ),
                file_path=file_path,
            ),
        ]
    return []


def _check_folder_name_no_slash(
    *,
    paper_id: str,
    file_path: Path,
) -> list[Diagnostic]:
    if _SLASH_PATTERN.search(paper_id) is not None:
        return [
            Diagnostic(
                code=PA_E011,
                message=f"Folder name contains '/' characters: '{paper_id}'",
                file_path=file_path,
            ),
        ]
    return []


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
        category_dir: Path = CATEGORIES_DIR / category
        if not category_dir.exists():
            diagnostics.append(
                Diagnostic(
                    code=PA_W005,
                    message=f"Category '{category}' does not exist in meta/categories/",
                    file_path=file_path,
                ),
            )
    return diagnostics


def _check_doi_folder_consistency(
    *,
    data: dict[str, Any],
    paper_id: str,
    file_path: Path,
) -> list[Diagnostic]:
    doi: object = data.get(DOI_FIELD)
    if doi is None and not paper_id.startswith(NO_DOI_PREFIX):
        return [
            Diagnostic(
                code=PA_W006,
                message=(
                    f"doi is null but folder name '{paper_id}' "
                    f"does not start with '{NO_DOI_PREFIX}'"
                ),
                file_path=file_path,
            ),
        ]
    return []


def _check_author_countries(
    *,
    data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    authors: object = data.get(AUTHORS_FIELD)
    if not isinstance(authors, list) or len(authors) == 0:
        return []
    has_country: bool = False
    for author in authors:
        if isinstance(author, dict) and author.get(COUNTRY_FIELD) is not None:
            has_country = True
            break
    if not has_country:
        return [
            Diagnostic(
                code=PA_W007,
                message="No author has a non-null country field",
                file_path=file_path,
            ),
        ]
    return []


def _check_abstract_length(
    *,
    data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    abstract: object = data.get(ABSTRACT_FIELD)
    if not isinstance(abstract, str):
        return []
    word_count: int = count_words(text=abstract)
    if word_count < MIN_ABSTRACT_WORDS:
        return [
            Diagnostic(
                code=PA_W008,
                message=(f"abstract has {word_count} words (minimum: {MIN_ABSTRACT_WORDS})"),
                file_path=file_path,
            ),
        ]
    return []


def _check_download_failure_reason(
    *,
    data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    status: object = data.get(DOWNLOAD_STATUS_FIELD)
    if str(status) != "failed":
        return []
    reason: object = data.get(DOWNLOAD_FAILURE_REASON_FIELD)
    if reason is None or (isinstance(reason, str) and len(reason.strip()) == 0):
        return [
            Diagnostic(
                code=PA_E014,
                message=(
                    "download_status is 'failed' but download_failure_reason is null or empty"
                ),
                file_path=file_path,
            ),
        ]
    return []


def _check_date_published(
    *,
    data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    date_published: object = data.get(DATE_PUBLISHED_FIELD)
    if date_published is None:
        return [
            Diagnostic(
                code=PA_W009,
                message="date_published is null (only year is known)",
                file_path=file_path,
            ),
        ]
    if isinstance(date_published, str) and _DATE_ISO_PATTERN.match(date_published) is None:
        return [
            Diagnostic(
                code=PA_W011,
                message=(
                    f"date_published '{date_published}' does not match "
                    "ISO 8601 format (YYYY, YYYY-MM, or YYYY-MM-DD)"
                ),
                file_path=file_path,
            ),
        ]
    return []


def _check_download_status_value(
    *,
    data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    status: object = data.get(DOWNLOAD_STATUS_FIELD)
    if status is None:
        return []  # Already reported by required-fields check.
    if str(status) not in ALLOWED_DOWNLOAD_STATUSES:
        return [
            Diagnostic(
                code=PA_E015,
                message=(
                    f"download_status '{status}' is not one of: "
                    f"{', '.join(ALLOWED_DOWNLOAD_STATUSES)}"
                ),
                file_path=file_path,
            ),
        ]
    return []


def _check_country_codes(
    *,
    data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    authors: object = data.get(AUTHORS_FIELD)
    if isinstance(authors, list):
        for author in authors:
            if not isinstance(author, dict):
                continue
            country: object = author.get(COUNTRY_FIELD)
            if country is None:
                continue
            if not isinstance(country, str) or _COUNTRY_CODE_PATTERN.match(country) is None:
                author_name: str = str(author.get(NAME_FIELD, "unknown"))
                diagnostics.append(
                    Diagnostic(
                        code=PA_W010,
                        message=(
                            f"Author '{author_name}' has invalid country code "
                            f"'{country}' (expected ISO 3166-1 alpha-2, e.g., US, IT)"
                        ),
                        file_path=file_path,
                    ),
                )
    institutions: object = data.get(INSTITUTIONS_FIELD)
    if isinstance(institutions, list):
        for institution in institutions:
            if not isinstance(institution, dict):
                continue
            country = institution.get(COUNTRY_FIELD)
            if country is None:
                inst_name: str = str(institution.get(NAME_FIELD, "unknown"))
                diagnostics.append(
                    Diagnostic(
                        code=PA_W010,
                        message=(
                            f"Institution '{inst_name}' has null country "
                            "(country is required for institutions)"
                        ),
                        file_path=file_path,
                    ),
                )
                continue
            if not isinstance(country, str) or _COUNTRY_CODE_PATTERN.match(country) is None:
                inst_name = str(institution.get(NAME_FIELD, "unknown"))
                diagnostics.append(
                    Diagnostic(
                        code=PA_W010,
                        message=(
                            f"Institution '{inst_name}' has invalid country code "
                            f"'{country}' (expected ISO 3166-1 alpha-2, e.g., US, IT)"
                        ),
                        file_path=file_path,
                    ),
                )
    return diagnostics


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def verify_paper_details(
    *,
    paper_id: str,
    task_id: str | None = None,
) -> list[Diagnostic]:
    file_path: Path = paper_details_path(paper_id=paper_id, task_id=task_id)

    if not file_path.exists():
        return [
            Diagnostic(
                code=PA_E001,
                message=f"details.json does not exist: {file_path}",
                file_path=file_path,
            ),
        ]

    data: dict[str, Any] | None = load_json_file(file_path=file_path)
    if data is None:
        return [
            Diagnostic(
                code=PA_E001,
                message=f"details.json is not valid JSON: {file_path}",
                file_path=file_path,
            ),
        ]

    diagnostics: list[Diagnostic] = []

    diagnostics.extend(
        _check_folder_name_no_slash(
            paper_id=paper_id,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_required_fields(
            data=data,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_spec_version(
            data=data,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_summary_path_field(
            data=data,
            paper_id=paper_id,
            task_id=task_id,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_paper_id_match(
            data=data,
            paper_id=paper_id,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_files_exist(
            data=data,
            paper_id=paper_id,
            task_id=task_id,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_venue_type(
            data=data,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_categories_exist(
            data=data,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_doi_folder_consistency(
            data=data,
            paper_id=paper_id,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_author_countries(
            data=data,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_abstract_length(
            data=data,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_date_published(
            data=data,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_download_failure_reason(
            data=data,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_download_status_value(
            data=data,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_country_codes(
            data=data,
            file_path=file_path,
        ),
    )

    return diagnostics
