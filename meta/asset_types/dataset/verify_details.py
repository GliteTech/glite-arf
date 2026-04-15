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
    dataset_asset_dir,
    dataset_details_path,
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
DATASET_ID_FIELD: str = "dataset_id"
NAME_FIELD: str = "name"
VERSION_FIELD: str = "version"
SHORT_DESCRIPTION_FIELD: str = "short_description"
DESCRIPTION_PATH_FIELD: str = "description_path"
SOURCE_PAPER_ID_FIELD: str = "source_paper_id"
URL_FIELD: str = "url"
YEAR_FIELD: str = "year"
AUTHORS_FIELD: str = "authors"
INSTITUTIONS_FIELD: str = "institutions"
LICENSE_FIELD: str = "license"
ACCESS_KIND_FIELD: str = "access_kind"
SIZE_DESCRIPTION_FIELD: str = "size_description"
FILES_FIELD: str = "files"
PATH_FIELD: str = "path"
CATEGORIES_FIELD: str = "categories"
DATE_PUBLISHED_FIELD: str = "date_published"
COUNTRY_FIELD: str = "country"
LEGACY_SPEC_VERSION: str = "1"

REQUIRED_FIELDS: list[str] = [
    SPEC_VERSION_FIELD,
    DATASET_ID_FIELD,
    NAME_FIELD,
    VERSION_FIELD,
    SHORT_DESCRIPTION_FIELD,
    SOURCE_PAPER_ID_FIELD,
    URL_FIELD,
    YEAR_FIELD,
    AUTHORS_FIELD,
    INSTITUTIONS_FIELD,
    LICENSE_FIELD,
    ACCESS_KIND_FIELD,
    SIZE_DESCRIPTION_FIELD,
    FILES_FIELD,
    CATEGORIES_FIELD,
]

ALLOWED_ACCESS_KINDS: list[str] = [
    "public",
    "restricted",
    "proprietary",
]

DATASET_FILE_REQUIRED_KEYS: list[str] = [
    PATH_FIELD,
    "description",
    "format",
]

MIN_SHORT_DESCRIPTION_WORDS: int = 10

_DATASET_ID_PATTERN: re.Pattern[str] = re.compile(
    r"^[a-z0-9]+([.\-][a-z0-9]+)*$",
)
_COUNTRY_CODE_PATTERN: re.Pattern[str] = re.compile(r"^[A-Z]{2}$")
_DATE_ISO_PATTERN: re.Pattern[str] = re.compile(
    r"^\d{4}(-\d{2}(-\d{2})?)?$",
)

# ---------------------------------------------------------------------------
# Diagnostic codes
# ---------------------------------------------------------------------------

_PREFIX: str = "DA"

DA_E001: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=1,
)
DA_E004: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=4,
)
DA_E005: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=5,
)
DA_E008: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=8,
)
DA_E010: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=10,
)
DA_E011: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=11,
)
DA_E013: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=13,
)
DA_E016: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=16,
)
DA_W005: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=5,
)
DA_W007: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=7,
)
DA_W008: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=8,
)
DA_W009: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=9,
)
DA_W010: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=10,
)
DA_W011: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=11,
)
DA_W012: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=12,
)


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------


def _check_dataset_id_match(
    *,
    data: dict[str, Any],
    dataset_id: str,
    file_path: Path,
) -> list[Diagnostic]:
    json_id: object = data.get(DATASET_ID_FIELD)
    if json_id is None:
        return []
    if str(json_id) != dataset_id:
        return [
            Diagnostic(
                code=DA_E004,
                message=(f"dataset_id '{json_id}' does not match folder name '{dataset_id}'"),
                file_path=file_path,
            ),
        ]
    return []


def _check_required_fields_ds(
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
                code=DA_E005,
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
                code=DA_E013,
                message="spec_version is missing from details.json",
                file_path=file_path,
            ),
        ]
    return []


def _check_description_path_field(
    *,
    data: dict[str, Any],
    dataset_id: str,
    task_id: str | None,
    file_path: Path,
) -> list[Diagnostic]:
    version: object = data.get(SPEC_VERSION_FIELD)
    value: object = data.get(DESCRIPTION_PATH_FIELD)
    if (
        isinstance(version, str)
        and version != LEGACY_SPEC_VERSION
        and (not isinstance(value, str) or len(value.strip()) == 0)
    ):
        return [
            Diagnostic(
                code=DA_E005,
                message=f"Required string field missing: '{DESCRIPTION_PATH_FIELD}'",
                file_path=file_path,
            ),
        ]
    if value is None:
        return []
    if not isinstance(value, str) or len(value.strip()) == 0:
        return [
            Diagnostic(
                code=DA_E005,
                message=f"Field '{DESCRIPTION_PATH_FIELD}' must be a non-empty string",
                file_path=file_path,
            ),
        ]
    declared_path: Path = (
        dataset_asset_dir(
            dataset_id=dataset_id,
            task_id=task_id,
        )
        / value
    )
    if not declared_path.exists():
        return [
            Diagnostic(
                code=DA_E008,
                message=f"Declared description path does not exist: '{value}'",
                file_path=file_path,
            ),
        ]
    return []


def _check_files_structure(
    *,
    data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    files: object = data.get(FILES_FIELD)
    if not isinstance(files, list):
        return []
    diagnostics: list[Diagnostic] = []
    for i, entry in enumerate(files):
        if not isinstance(entry, dict):
            diagnostics.append(
                Diagnostic(
                    code=DA_E016,
                    message=f"files[{i}] is not an object",
                    file_path=file_path,
                ),
            )
            continue
        for key in DATASET_FILE_REQUIRED_KEYS:
            value: object = entry.get(key)
            if value is None or not isinstance(value, str):
                diagnostics.append(
                    Diagnostic(
                        code=DA_E016,
                        message=(f"files[{i}] is missing required string field '{key}'"),
                        file_path=file_path,
                    ),
                )
    return diagnostics


def _check_files_exist(
    *,
    data: dict[str, Any],
    dataset_id: str,
    task_id: str | None,
    file_path: Path,
) -> list[Diagnostic]:
    files: object = data.get(FILES_FIELD)
    if not isinstance(files, list):
        return []
    asset_dir: Path = dataset_asset_dir(
        dataset_id=dataset_id,
        task_id=task_id,
    )
    diagnostics: list[Diagnostic] = []
    for entry in files:
        if not isinstance(entry, dict):
            continue
        path_value: object = entry.get(PATH_FIELD)
        if not isinstance(path_value, str):
            continue
        full_path: Path = asset_dir / path_value
        if not full_path.exists():
            diagnostics.append(
                Diagnostic(
                    code=DA_E008,
                    message=f"Listed file does not exist: '{path_value}'",
                    file_path=file_path,
                ),
            )
    return diagnostics


def _check_access_kind(
    *,
    data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    access_kind: object = data.get(ACCESS_KIND_FIELD)
    if access_kind is None:
        return []
    if str(access_kind) not in ALLOWED_ACCESS_KINDS:
        return [
            Diagnostic(
                code=DA_E010,
                message=(
                    f"access_kind '{access_kind}' is not one of: {', '.join(ALLOWED_ACCESS_KINDS)}"
                ),
                file_path=file_path,
            ),
        ]
    return []


def _check_dataset_id_format(
    *,
    dataset_id: str,
    file_path: Path,
) -> list[Diagnostic]:
    if _DATASET_ID_PATTERN.match(dataset_id) is None:
        return [
            Diagnostic(
                code=DA_E011,
                message=(
                    f"Folder name '{dataset_id}' does not match "
                    "dataset ID format (lowercase alphanumeric, "
                    "hyphens, dots)"
                ),
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
                    code=DA_W005,
                    message=(f"Category '{category}' does not exist in meta/categories/"),
                    file_path=file_path,
                ),
            )
    return diagnostics


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
                code=DA_W007,
                message="No author has a non-null country field",
                file_path=file_path,
            ),
        ]
    return []


def _check_short_description_length(
    *,
    data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    desc: object = data.get(SHORT_DESCRIPTION_FIELD)
    if not isinstance(desc, str):
        return []
    word_count: int = count_words(text=desc)
    if word_count < MIN_SHORT_DESCRIPTION_WORDS:
        return [
            Diagnostic(
                code=DA_W008,
                message=(
                    f"short_description has {word_count} words "
                    f"(minimum: {MIN_SHORT_DESCRIPTION_WORDS})"
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
                code=DA_W009,
                message="date_published is null (only year is known)",
                file_path=file_path,
            ),
        ]
    if isinstance(date_published, str) and _DATE_ISO_PATTERN.match(date_published) is None:
        return [
            Diagnostic(
                code=DA_W011,
                message=(
                    f"date_published '{date_published}' does not match "
                    "ISO 8601 format (YYYY, YYYY-MM, or YYYY-MM-DD)"
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
                author_name: str = str(
                    author.get(NAME_FIELD, "unknown"),
                )
                diagnostics.append(
                    Diagnostic(
                        code=DA_W010,
                        message=(
                            f"Author '{author_name}' has invalid "
                            f"country code '{country}' (expected "
                            "ISO 3166-1 alpha-2, e.g., US, IT)"
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
                inst_name: str = str(
                    institution.get(NAME_FIELD, "unknown"),
                )
                diagnostics.append(
                    Diagnostic(
                        code=DA_W010,
                        message=(
                            f"Institution '{inst_name}' has null "
                            "country (country is required for "
                            "institutions)"
                        ),
                        file_path=file_path,
                    ),
                )
                continue
            if not isinstance(country, str) or _COUNTRY_CODE_PATTERN.match(country) is None:
                inst_name = str(
                    institution.get(NAME_FIELD, "unknown"),
                )
                diagnostics.append(
                    Diagnostic(
                        code=DA_W010,
                        message=(
                            f"Institution '{inst_name}' has invalid "
                            f"country code '{country}' (expected "
                            "ISO 3166-1 alpha-2, e.g., US, IT)"
                        ),
                        file_path=file_path,
                    ),
                )
    return diagnostics


def _check_size_description(
    *,
    data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    size_desc: object = data.get(SIZE_DESCRIPTION_FIELD)
    if isinstance(size_desc, str) and len(size_desc.strip()) == 0:
        return [
            Diagnostic(
                code=DA_W012,
                message="size_description is empty",
                file_path=file_path,
            ),
        ]
    return []


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def verify_dataset_details(
    *,
    dataset_id: str,
    task_id: str | None = None,
) -> list[Diagnostic]:
    file_path: Path = dataset_details_path(
        dataset_id=dataset_id,
        task_id=task_id,
    )

    if not file_path.exists():
        return [
            Diagnostic(
                code=DA_E001,
                message=f"details.json does not exist: {file_path}",
                file_path=file_path,
            ),
        ]

    data: dict[str, Any] | None = load_json_file(file_path=file_path)
    if data is None:
        return [
            Diagnostic(
                code=DA_E001,
                message=f"details.json is not valid JSON: {file_path}",
                file_path=file_path,
            ),
        ]

    diagnostics: list[Diagnostic] = []

    diagnostics.extend(
        _check_dataset_id_format(
            dataset_id=dataset_id,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_required_fields_ds(
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
        _check_description_path_field(
            data=data,
            dataset_id=dataset_id,
            task_id=task_id,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_dataset_id_match(
            data=data,
            dataset_id=dataset_id,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_files_structure(
            data=data,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_files_exist(
            data=data,
            dataset_id=dataset_id,
            task_id=task_id,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_access_kind(
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
        _check_author_countries(
            data=data,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_short_description_length(
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
        _check_country_codes(
            data=data,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_size_description(
            data=data,
            file_path=file_path,
        ),
    )

    return diagnostics
