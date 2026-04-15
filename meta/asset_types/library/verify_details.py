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
    TASKS_DIR,
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
NAME_FIELD: str = "name"
VERSION_FIELD: str = "version"
SHORT_DESCRIPTION_FIELD: str = "short_description"
DESCRIPTION_PATH_FIELD: str = "description_path"
MODULE_PATHS_FIELD: str = "module_paths"
ENTRY_POINTS_FIELD: str = "entry_points"
ENTRY_POINT_NAME_FIELD: str = "name"
ENTRY_POINT_KIND_FIELD: str = "kind"
ENTRY_POINT_MODULE_FIELD: str = "module"
ENTRY_POINT_DESCRIPTION_FIELD: str = "description"
DEPENDENCIES_FIELD: str = "dependencies"
TEST_PATHS_FIELD: str = "test_paths"
CATEGORIES_FIELD: str = "categories"
CREATED_BY_TASK_FIELD: str = "created_by_task"
DATE_CREATED_FIELD: str = "date_created"
LEGACY_SPEC_VERSION: str = "1"

REQUIRED_FIELDS: list[str] = [
    SPEC_VERSION_FIELD,
    LIBRARY_ID_FIELD,
    NAME_FIELD,
    VERSION_FIELD,
    SHORT_DESCRIPTION_FIELD,
    MODULE_PATHS_FIELD,
    ENTRY_POINTS_FIELD,
    DEPENDENCIES_FIELD,
    CATEGORIES_FIELD,
    CREATED_BY_TASK_FIELD,
    DATE_CREATED_FIELD,
]

ENTRY_POINT_REQUIRED_KEYS: list[str] = [
    ENTRY_POINT_NAME_FIELD,
    ENTRY_POINT_KIND_FIELD,
    ENTRY_POINT_MODULE_FIELD,
    ENTRY_POINT_DESCRIPTION_FIELD,
]

ALLOWED_ENTRY_POINT_KINDS: list[str] = [
    "function",
    "class",
    "script",
]

MIN_SHORT_DESCRIPTION_WORDS: int = 10

_LIBRARY_ID_PATTERN: re.Pattern[str] = re.compile(
    r"^[a-z][a-z0-9]*(_[a-z0-9]+)*$",
)

# ---------------------------------------------------------------------------
# Diagnostic codes
# ---------------------------------------------------------------------------

_PREFIX: str = "LA"

LA_E001: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=1,
)
LA_E004: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=4,
)
LA_E005: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=5,
)
LA_E006: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=6,
)
LA_E008: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=8,
)
LA_E010: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=10,
)
LA_E011: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=11,
)
LA_E013: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=13,
)
LA_E016: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.ERROR,
    number=16,
)
LA_W005: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=5,
)
LA_W008: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=8,
)
LA_W014: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=14,
)
LA_W015: DiagnosticCode = DiagnosticCode(
    prefix=_PREFIX,
    severity=Severity.WARNING,
    number=15,
)


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------


def _check_library_id_format(
    *,
    library_id: str,
    file_path: Path,
) -> list[Diagnostic]:
    if _LIBRARY_ID_PATTERN.match(library_id) is None:
        return [
            Diagnostic(
                code=LA_E011,
                message=(
                    f"Folder name '{library_id}' does not match "
                    "library ID format (lowercase letters, digits, "
                    "underscores; must start with a letter)"
                ),
                file_path=file_path,
            ),
        ]
    return []


def _check_library_id_match(
    *,
    data: dict[str, Any],
    library_id: str,
    file_path: Path,
) -> list[Diagnostic]:
    json_id: object = data.get(LIBRARY_ID_FIELD)
    if json_id is None:
        return []
    if str(json_id) != library_id:
        return [
            Diagnostic(
                code=LA_E004,
                message=(f"library_id '{json_id}' does not match folder name '{library_id}'"),
                file_path=file_path,
            ),
        ]
    return []


def _check_required_fields_lib(
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
                code=LA_E005,
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
                code=LA_E013,
                message="spec_version is missing from details.json",
                file_path=file_path,
            ),
        ]
    return []


def _check_description_path_field(
    *,
    data: dict[str, Any],
    library_id: str,
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
                code=LA_E005,
                message=f"Required string field missing: '{DESCRIPTION_PATH_FIELD}'",
                file_path=file_path,
            ),
        ]
    if value is not None and (not isinstance(value, str) or len(value.strip()) == 0):
        return [
            Diagnostic(
                code=LA_E005,
                message=f"Field '{DESCRIPTION_PATH_FIELD}' must be a non-empty string",
                file_path=file_path,
            ),
        ]
    if isinstance(value, str):
        declared_path: Path = (
            library_details_path(
                library_id=library_id,
                task_id=task_id,
            ).parent
            / value
        )
        if not declared_path.exists():
            return [
                Diagnostic(
                    code=LA_E008,
                    message=f"Declared description path does not exist: '{value}'",
                    file_path=file_path,
                ),
            ]
    return []


def _check_module_paths_nonempty(
    *,
    data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    module_paths: object = data.get(MODULE_PATHS_FIELD)
    if isinstance(module_paths, list) and len(module_paths) == 0:
        return [
            Diagnostic(
                code=LA_E006,
                message="module_paths is empty (library must have at least one module)",
                file_path=file_path,
            ),
        ]
    return []


def _check_module_paths_exist(
    *,
    data: dict[str, Any],
    task_id: str | None,
    file_path: Path,
) -> list[Diagnostic]:
    module_paths: object = data.get(MODULE_PATHS_FIELD)
    if not isinstance(module_paths, list):
        return []
    if task_id is None:
        return []
    task_root: Path = TASKS_DIR / task_id
    diagnostics: list[Diagnostic] = []
    for path_value in module_paths:
        if not isinstance(path_value, str):
            continue
        full_path: Path = task_root / path_value
        if not full_path.exists():
            diagnostics.append(
                Diagnostic(
                    code=LA_E008,
                    message=(
                        f"Module path does not exist: '{path_value}' (resolved to {full_path})"
                    ),
                    file_path=file_path,
                ),
            )
    return diagnostics


def _check_entry_points_structure(
    *,
    data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    entry_points: object = data.get(ENTRY_POINTS_FIELD)
    if not isinstance(entry_points, list):
        return []
    diagnostics: list[Diagnostic] = []
    for i, entry in enumerate(entry_points):
        if not isinstance(entry, dict):
            diagnostics.append(
                Diagnostic(
                    code=LA_E016,
                    message=f"entry_points[{i}] is not an object",
                    file_path=file_path,
                ),
            )
            continue
        for key in ENTRY_POINT_REQUIRED_KEYS:
            value: object = entry.get(key)
            if value is None or not isinstance(value, str):
                diagnostics.append(
                    Diagnostic(
                        code=LA_E016,
                        message=(f"entry_points[{i}] is missing required string field '{key}'"),
                        file_path=file_path,
                    ),
                )
    return diagnostics


def _check_entry_point_kinds(
    *,
    data: dict[str, Any],
    file_path: Path,
) -> list[Diagnostic]:
    entry_points: object = data.get(ENTRY_POINTS_FIELD)
    if not isinstance(entry_points, list):
        return []
    diagnostics: list[Diagnostic] = []
    for i, entry in enumerate(entry_points):
        if not isinstance(entry, dict):
            continue
        kind: object = entry.get(ENTRY_POINT_KIND_FIELD)
        if isinstance(kind, str) and kind not in ALLOWED_ENTRY_POINT_KINDS:
            diagnostics.append(
                Diagnostic(
                    code=LA_E010,
                    message=(
                        f"entry_points[{i}].kind '{kind}' is not one of: "
                        f"{', '.join(ALLOWED_ENTRY_POINT_KINDS)}"
                    ),
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
        category_dir: Path = CATEGORIES_DIR / category
        if not category_dir.exists():
            diagnostics.append(
                Diagnostic(
                    code=LA_W005,
                    message=(f"Category '{category}' does not exist in meta/categories/"),
                    file_path=file_path,
                ),
            )
    return diagnostics


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
                code=LA_W008,
                message=(
                    f"short_description has {word_count} words "
                    f"(minimum: {MIN_SHORT_DESCRIPTION_WORDS})"
                ),
                file_path=file_path,
            ),
        ]
    return []


def _check_test_paths(
    *,
    data: dict[str, Any],
    task_id: str | None,
    file_path: Path,
) -> list[Diagnostic]:
    test_paths: object = data.get(TEST_PATHS_FIELD)
    if test_paths is None:
        return [
            Diagnostic(
                code=LA_W014,
                message="No test_paths provided (testing is recommended)",
                file_path=file_path,
            ),
        ]
    if not isinstance(test_paths, list):
        return []
    if len(test_paths) == 0:
        return [
            Diagnostic(
                code=LA_W014,
                message="test_paths is empty (testing is recommended)",
                file_path=file_path,
            ),
        ]
    if task_id is None:
        return []
    task_root: Path = TASKS_DIR / task_id
    diagnostics: list[Diagnostic] = []
    for path_value in test_paths:
        if not isinstance(path_value, str):
            continue
        full_path: Path = task_root / path_value
        if not full_path.exists():
            diagnostics.append(
                Diagnostic(
                    code=LA_W015,
                    message=(f"Test path does not exist: '{path_value}' (resolved to {full_path})"),
                    file_path=file_path,
                ),
            )
    return diagnostics


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def verify_library_details(
    *,
    library_id: str,
    task_id: str | None = None,
) -> list[Diagnostic]:
    file_path: Path = library_details_path(
        library_id=library_id,
        task_id=task_id,
    )

    if not file_path.exists():
        return [
            Diagnostic(
                code=LA_E001,
                message=f"details.json does not exist: {file_path}",
                file_path=file_path,
            ),
        ]

    data: dict[str, Any] | None = load_json_file(file_path=file_path)
    if data is None:
        return [
            Diagnostic(
                code=LA_E001,
                message=f"details.json is not valid JSON: {file_path}",
                file_path=file_path,
            ),
        ]

    diagnostics: list[Diagnostic] = []

    diagnostics.extend(
        _check_library_id_format(
            library_id=library_id,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_required_fields_lib(
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
            library_id=library_id,
            task_id=task_id,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_library_id_match(
            data=data,
            library_id=library_id,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_module_paths_nonempty(
            data=data,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_module_paths_exist(
            data=data,
            task_id=task_id,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_entry_points_structure(
            data=data,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_entry_point_kinds(
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
        _check_short_description_length(
            data=data,
            file_path=file_path,
        ),
    )
    diagnostics.extend(
        _check_test_paths(
            data=data,
            task_id=task_id,
            file_path=file_path,
        ),
    )

    return diagnostics
