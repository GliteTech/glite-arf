from pathlib import Path
from typing import Any

from arf.scripts.verificators.common.paths import TASKS_DIR

type TaskID = str

FIELD_SPEC_VERSION: str = "spec_version"
FIELD_LONG_DESCRIPTION: str = "long_description"
FIELD_LONG_DESCRIPTION_FILE: str = "long_description_file"

LEGACY_TASK_SPEC_VERSION: int = 3
CURRENT_TASK_SPEC_VERSION: int = 4
SUPPORTED_TASK_SPEC_VERSIONS: set[int] = {
    LEGACY_TASK_SPEC_VERSION,
    CURRENT_TASK_SPEC_VERSION,
}
RECOMMENDED_TASK_DESCRIPTION_FILE_NAME: str = "task_description.md"
TASK_DESCRIPTION_FILE_SUFFIX: str = ".md"


def infer_task_spec_version(*, data: dict[str, Any]) -> int | None:
    raw_spec_version: object = data.get(FIELD_SPEC_VERSION)
    if raw_spec_version is None:
        return LEGACY_TASK_SPEC_VERSION
    if not isinstance(raw_spec_version, int) or isinstance(raw_spec_version, bool):
        return None
    if raw_spec_version not in SUPPORTED_TASK_SPEC_VERSIONS:
        return None
    return raw_spec_version


def is_valid_task_description_file_name(*, file_name: str) -> bool:
    stripped: str = file_name.strip()
    if len(stripped) == 0:
        return False

    file_path: Path = Path(stripped)
    if file_path.is_absolute():
        return False
    if file_path.name != stripped:
        return False
    return file_path.suffix.lower() == TASK_DESCRIPTION_FILE_SUFFIX


def load_task_long_description(
    *,
    task_id: TaskID,
    data: dict[str, Any],
) -> str | None:
    spec_version: int | None = infer_task_spec_version(data=data)
    if spec_version is None:
        return None

    inline_value: object = data.get(FIELD_LONG_DESCRIPTION)
    file_value: object = data.get(FIELD_LONG_DESCRIPTION_FILE)

    if spec_version == LEGACY_TASK_SPEC_VERSION:
        if not isinstance(inline_value, str):
            return None
        if file_value is not None:
            return None
        return inline_value

    has_inline: bool = isinstance(inline_value, str)
    has_file: bool = isinstance(file_value, str)
    if has_inline == has_file:
        return None

    if has_inline:
        assert isinstance(inline_value, str)
        return inline_value

    assert isinstance(file_value, str)
    if not is_valid_task_description_file_name(file_name=file_value):
        return None

    description_path: Path = task_description_file_path(
        task_id=task_id,
        file_name=file_value,
    )
    try:
        return description_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def task_description_file_path(*, task_id: TaskID, file_name: str) -> Path:
    return TASKS_DIR / task_id / file_name
