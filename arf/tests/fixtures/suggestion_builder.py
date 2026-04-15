from pathlib import Path

from arf.scripts.verificators.common import paths
from arf.tests.fixtures.writers import write_json

SPEC_VERSION_SUGGESTIONS: str = "2"
DEFAULT_SUGGESTION_ID: str = "S-0001-01"
DEFAULT_TITLE: str = "Test suggestion"
DEFAULT_DESCRIPTION: str = (
    "A test suggestion for evaluating new approaches to word sense disambiguation."
)
DEFAULT_KIND: str = "experiment"
DEFAULT_PRIORITY: str = "medium"
DEFAULT_SOURCE_TASK: str = "t0001_test"
DEFAULT_STATUS: str = "active"
DEFAULT_CATEGORY: str = "test-category"


def build_suggestion(
    *,
    suggestion_id: str = DEFAULT_SUGGESTION_ID,
    title: str = DEFAULT_TITLE,
    description: str = DEFAULT_DESCRIPTION,
    kind: str = DEFAULT_KIND,
    priority: str = DEFAULT_PRIORITY,
    source_task: str = DEFAULT_SOURCE_TASK,
    source_paper: str | None = None,
    categories: list[str] | None = None,
    status: str = DEFAULT_STATUS,
    overrides: dict[str, object] | None = None,
) -> dict[str, object]:
    data: dict[str, object] = {
        "id": suggestion_id,
        "title": title,
        "description": description,
        "kind": kind,
        "priority": priority,
        "source_task": source_task,
        "source_paper": source_paper,
        "categories": (categories if categories is not None else [DEFAULT_CATEGORY]),
        "status": status,
    }
    if overrides is not None:
        data.update(overrides)
    return data


def build_suggestions_file(
    *,
    repo_root: Path,
    task_id: str,
    suggestions: list[dict[str, object]] | None = None,
    spec_version: str = SPEC_VERSION_SUGGESTIONS,
) -> Path:
    items: list[dict[str, object]] = suggestions if suggestions is not None else []
    data: dict[str, object] = {
        "spec_version": spec_version,
        "suggestions": items,
    }
    suggestions_path: Path = paths.suggestions_path(task_id=task_id)
    write_json(path=suggestions_path, data=data)
    return suggestions_path
