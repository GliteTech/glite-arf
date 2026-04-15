from pathlib import Path

from arf.scripts.verificators.common import paths
from arf.tests.fixtures.writers import write_json

SPEC_VERSION_CORRECTION: str = "3"
DEFAULT_CORRECTION_ID: str = "C-0001-01"
DEFAULT_TARGET_TASK: str = "t0001_test"
DEFAULT_TARGET_KIND: str = "paper"
DEFAULT_TARGET_ID: str = "test-paper"
DEFAULT_ACTION: str = "update"
DEFAULT_RATIONALE: str = "Test correction."


def build_correction(
    *,
    repo_root: Path,
    correcting_task: str,
    file_name: str,
    correction_id: str = DEFAULT_CORRECTION_ID,
    target_task: str = DEFAULT_TARGET_TASK,
    target_kind: str = DEFAULT_TARGET_KIND,
    target_id: str = DEFAULT_TARGET_ID,
    action: str = DEFAULT_ACTION,
    changes: dict[str, object] | None = None,
    file_changes: dict[str, object] | None = None,
    rationale: str = DEFAULT_RATIONALE,
    spec_version: str = SPEC_VERSION_CORRECTION,
) -> Path:
    kinds_without_files: set[str] = {"suggestion"}
    data: dict[str, object] = {
        "spec_version": spec_version,
        "correction_id": correction_id,
        "correcting_task": correcting_task,
        "target_task": target_task,
        "target_kind": target_kind,
        "target_id": target_id,
        "action": action,
        "changes": changes if changes is not None else {},
        "rationale": rationale,
    }
    if target_kind not in kinds_without_files:
        data["file_changes"] = file_changes if file_changes is not None else {}

    corrections_dir: Path = paths.corrections_dir(
        task_id=correcting_task,
    )
    correction_path: Path = corrections_dir / f"{file_name}.json"
    write_json(path=correction_path, data=data)
    return correction_path
