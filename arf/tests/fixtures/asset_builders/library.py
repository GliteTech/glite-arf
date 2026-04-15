from pathlib import Path

from arf.scripts.verificators.common import paths as common_paths
from arf.scripts.verificators.common.paths import (
    library_asset_dir,
    library_description_path,
    library_details_path,
)
from arf.tests.fixtures.writers import (
    write_frontmatter_md,
    write_json,
    write_text,
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
DEPENDENCIES_FIELD: str = "dependencies"
TEST_PATHS_FIELD: str = "test_paths"
CATEGORIES_FIELD: str = "categories"
CREATED_BY_TASK_FIELD: str = "created_by_task"
DATE_CREATED_FIELD: str = "date_created"

DEFAULT_SPEC_VERSION: str = "2"
DEFAULT_LIBRARY_ID: str = "test_library"
DEFAULT_TASK_ID: str = "t0001_test"
DEFAULT_NAME: str = "Test Library"
DEFAULT_VERSION: str = "0.1.0"
DEFAULT_SHORT_DESCRIPTION: str = (
    "A test library providing data loading and scoring utilities "
    "for word sense disambiguation evaluation across standard "
    "benchmarks."
)
DEFAULT_DESCRIPTION_PATH: str = "description.md"
DEFAULT_MODULE_PATH: str = "code/test_library.py"
DEFAULT_TEST_PATH: str = "code/test_test_library.py"
DEFAULT_DATE_CREATED: str = "2026-01-20"

DEFAULT_ENTRY_POINT_NAME: str = "load_data"
DEFAULT_ENTRY_POINT_KIND: str = "function"
DEFAULT_ENTRY_POINT_MODULE: str = "code.test_library"
DEFAULT_ENTRY_POINT_DESCRIPTION: str = "Load WSD evaluation data from JSONL files"

_OVERVIEW_TEXT: str = (
    "This library provides a unified interface for loading word sense "
    "disambiguation datasets and scoring model predictions. It supports "
    "the Raganato evaluation format and can compute micro-averaged F1 "
    "scores broken down by part of speech. The library is designed for "
    "use within the project task framework."
)

_API_REFERENCE_TEXT: str = (
    "The main entry point is the `load_data` function which reads JSONL "
    "files and returns structured instances. Each instance contains the "
    "target word, its context, candidate senses from WordNet 3.0, and "
    "the gold-standard sense key. The `score_predictions` function "
    "accepts a list of predictions and gold labels and returns micro-F1 "
    "with optional per-POS breakdown. Both functions use keyword arguments "
    "for all parameters."
)

_DESCRIPTION_BODY: str = (
    "# Test Library\n\n"
    "## Metadata\n\n"
    "* **Name**: Test Library\n"
    "* **Version**: 0.1.0\n"
    "* **Module**: `code/test_library.py`\n\n"
    "## Overview\n\n"
    f"{_OVERVIEW_TEXT}\n\n"
    "## API Reference\n\n"
    f"{_API_REFERENCE_TEXT}\n\n"
    "## Usage Examples\n\n"
    "```python\n"
    "from tasks.t0001_test.code.test_library import load_data\n"
    "instances = load_data(path=Path('data.jsonl'))\n"
    "```\n\n"
    "## Dependencies\n\n"
    "No external dependencies beyond the standard library.\n\n"
    "## Testing\n\n"
    "Run tests with `uv run pytest tasks/t0001_test/code/test_test_library.py`.\n\n"
    "## Main Ideas\n\n"
    "* Provides a single entry point for loading WSD data\n"
    "* Supports per-POS F1 score breakdown\n"
    "* Compatible with the Raganato evaluation format\n\n"
    "## Summary\n\n"
    "This library encapsulates data loading and scoring logic for word "
    "sense disambiguation evaluation. It reads JSONL-formatted datasets "
    "and computes micro-averaged F1 scores with optional part-of-speech "
    "breakdowns. The library is designed for integration with the project "
    "task framework and follows all project coding conventions.\n"
)

_MODULE_CONTENT: str = (
    '"""Test library module for WSD data loading."""\n'
    "\n"
    "from pathlib import Path\n"
    "\n"
    "\n"
    "def load_data(*, path: Path) -> list[dict[str, str]]:\n"
    '    return [{"token": "test", "sense": "test%1:04:00::"}]\n'
)


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------


def build_library_asset(
    *,
    repo_root: Path,
    library_id: str = DEFAULT_LIBRARY_ID,
    task_id: str = DEFAULT_TASK_ID,
    spec_version: str = DEFAULT_SPEC_VERSION,
    name: str = DEFAULT_NAME,
    version: str = DEFAULT_VERSION,
    short_description: str = DEFAULT_SHORT_DESCRIPTION,
    description_path: str = DEFAULT_DESCRIPTION_PATH,
    module_paths: list[str] | None = None,
    entry_points: list[dict[str, str]] | None = None,
    dependencies: list[str] | None = None,
    test_paths: list[str] | None = None,
    categories: list[str] | None = None,
    date_created: str = DEFAULT_DATE_CREATED,
    include_description: bool = True,
    include_module_files: bool = True,
    details_overrides: dict[str, object] | None = None,
    description_body: str | None = None,
) -> Path:
    asset_dir: Path = library_asset_dir(
        library_id=library_id,
        task_id=task_id,
    )
    asset_dir.mkdir(parents=True, exist_ok=True)

    resolved_module_paths: list[str] = (
        module_paths if module_paths is not None else [DEFAULT_MODULE_PATH]
    )
    resolved_entry_points: list[dict[str, str]] = (
        entry_points
        if entry_points is not None
        else [
            {
                "name": DEFAULT_ENTRY_POINT_NAME,
                "kind": DEFAULT_ENTRY_POINT_KIND,
                "module": DEFAULT_ENTRY_POINT_MODULE,
                "description": DEFAULT_ENTRY_POINT_DESCRIPTION,
            },
        ]
    )
    resolved_dependencies: list[str] = dependencies if dependencies is not None else []
    resolved_test_paths: list[str] = test_paths if test_paths is not None else [DEFAULT_TEST_PATH]
    resolved_categories: list[str] = categories if categories is not None else []

    details: dict[str, object] = {
        SPEC_VERSION_FIELD: spec_version,
        LIBRARY_ID_FIELD: library_id,
        NAME_FIELD: name,
        VERSION_FIELD: version,
        SHORT_DESCRIPTION_FIELD: short_description,
        DESCRIPTION_PATH_FIELD: description_path,
        MODULE_PATHS_FIELD: resolved_module_paths,
        ENTRY_POINTS_FIELD: resolved_entry_points,
        DEPENDENCIES_FIELD: resolved_dependencies,
        TEST_PATHS_FIELD: resolved_test_paths,
        CATEGORIES_FIELD: resolved_categories,
        CREATED_BY_TASK_FIELD: task_id,
        DATE_CREATED_FIELD: date_created,
    }

    if details_overrides is not None:
        details.update(details_overrides)

    write_json(
        path=library_details_path(
            library_id=library_id,
            task_id=task_id,
        ),
        data=details,
    )

    if include_description:
        frontmatter: dict[str, str | int] = {
            SPEC_VERSION_FIELD: spec_version,
            LIBRARY_ID_FIELD: library_id,
            "documented_by_task": task_id,
            "date_documented": date_created,
        }
        write_frontmatter_md(
            path=library_description_path(
                library_id=library_id,
                task_id=task_id,
            ),
            frontmatter=frontmatter,
            body=(description_body if description_body is not None else _DESCRIPTION_BODY),
        )

    if include_module_files:
        task_root: Path = common_paths.TASKS_DIR / task_id
        for module_path in resolved_module_paths:
            full_path: Path = task_root / module_path
            if not full_path.exists():
                write_text(path=full_path, content=_MODULE_CONTENT)
        for tp in resolved_test_paths:
            test_full: Path = task_root / tp
            if not test_full.exists():
                write_text(
                    path=test_full,
                    content=(
                        '"""Tests for test_library."""\n'
                        "\n"
                        "def test_placeholder() -> None:\n"
                        "    assert True\n"
                    ),
                )

    return asset_dir
