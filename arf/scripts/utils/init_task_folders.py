"""Create the mandatory task folder structure with .gitkeep files.

Creates all required directories and adds .gitkeep to every empty directory.
Reads expected_assets from task.json to determine asset subdirectories.

Usage:
    uv run python -m arf.scripts.utils.init_task_folders <task_id>

Exit codes:
    0 — all directories created
    1 — error (task.json not found, etc.)
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

from arf.scripts.verificators.common.paths import TASKS_DIR

REQUIRED_DIRS: list[str] = [
    "plan",
    "research",
    "results",
    "results/images",
    "corrections",
    "intervention",
    "code",
    "logs/commands",
    "logs/searches",
    "logs/sessions",
    "logs/steps",
]

FIELD_EXPECTED_ASSETS: str = "expected_assets"
GITKEEP: str = ".gitkeep"
INIT_PY: str = "__init__.py"


@dataclass(frozen=True, slots=True)
class InitTaskFoldersResult:
    directories_created: list[str] = field(default_factory=list)
    init_py_created: list[str] = field(default_factory=list)


def _load_expected_asset_types(*, task_dir: Path) -> list[str]:
    task_json: Path = task_dir / "task.json"
    if not task_json.exists():
        return []
    try:
        data: object = json.loads(task_json.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(data, dict):
        return []
    expected: object = data.get(FIELD_EXPECTED_ASSETS)
    if not isinstance(expected, dict):
        return []
    return [k for k in expected if isinstance(k, str)]


def init_task_folders(*, task_id: str) -> InitTaskFoldersResult:
    task_dir: Path = TASKS_DIR / task_id
    if not task_dir.exists():
        print(
            f"Error: task directory does not exist: {task_dir}",
            file=sys.stderr,
        )
        sys.exit(1)

    dirs_to_create: list[str] = list(REQUIRED_DIRS)

    asset_types: list[str] = _load_expected_asset_types(task_dir=task_dir)
    for asset_type in asset_types:
        dirs_to_create.append(f"assets/{asset_type}")

    if len(asset_types) == 0:
        dirs_to_create.append("assets")

    created: list[str] = []
    for rel_dir in dirs_to_create:
        dir_path: Path = task_dir / rel_dir
        dir_path.mkdir(parents=True, exist_ok=True)
        created.append(rel_dir)

        gitkeep_path: Path = dir_path / GITKEEP
        if not gitkeep_path.exists():
            children: list[Path] = [p for p in dir_path.iterdir() if p.name != GITKEEP]
            if len(children) == 0:
                gitkeep_path.touch()

    # Create __init__.py in task root and code/ for Python import support
    init_py_created: list[str] = []
    for init_dir in [task_dir, task_dir / "code"]:
        init_path: Path = init_dir / INIT_PY
        if init_dir.is_dir() and not init_path.exists():
            init_path.touch()
            init_py_created.append(
                str(init_path.relative_to(task_dir)),
            )

    return InitTaskFoldersResult(
        directories_created=created,
        init_py_created=init_py_created,
    )


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Create mandatory task folder structure with .gitkeep files.",
    )
    parser.add_argument("task_id", help="Task ID (e.g., t0061_ablation_study)")
    parser.add_argument(
        "--step-log-dir",
        type=Path,
        default=None,
        help="Step log directory; writes folders_created.txt there if provided",
    )
    args: argparse.Namespace = parser.parse_args()

    result: InitTaskFoldersResult = init_task_folders(task_id=args.task_id)
    for d in result.directories_created:
        print(d)
    print(f"\nCreated {len(result.directories_created)} directories with .gitkeep files.")
    for ip in result.init_py_created:
        print(f"Created {ip}")

    task_id: str = args.task_id
    step_log_dir: Path | None = args.step_log_dir
    if step_log_dir is not None:
        step_log_dir = step_log_dir.resolve()
        task_dir_fragment: str = f"tasks/{task_id}/"
        if task_dir_fragment not in str(step_log_dir):
            print(
                f"Error: --step-log-dir must be inside tasks/{task_id}/. Got: {step_log_dir}",
                file=sys.stderr,
            )
            sys.exit(1)
        step_log_dir.mkdir(parents=True, exist_ok=True)
        output_path: Path = step_log_dir / "folders_created.txt"
        output_path.write_text(
            "\n".join(result.directories_created) + "\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
