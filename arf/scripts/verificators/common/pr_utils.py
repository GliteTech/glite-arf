import json
import subprocess
from pathlib import Path
from typing import Any

GH_CMD: str = "gh"
PR_NUMBER_FIELD: str = "number"


def get_pr_json(
    *,
    repo_root: Path,
    pr_number: int,
    fields: str,
) -> dict[str, Any] | None:
    try:
        result: subprocess.CompletedProcess[str] = subprocess.run(
            [GH_CMD, "pr", "view", str(pr_number), "--json", fields],
            capture_output=True,
            text=True,
            cwd=repo_root,
        )
        if result.returncode != 0:
            return None
        data: object = json.loads(result.stdout)
        if isinstance(data, dict):
            return data
        return None
    except (OSError, json.JSONDecodeError):
        return None


def find_open_pr(*, repo_root: Path, branch: str) -> int | None:
    try:
        result: subprocess.CompletedProcess[str] = subprocess.run(
            [
                GH_CMD,
                "pr",
                "list",
                "--head",
                branch,
                "--state",
                "open",
                "--json",
                PR_NUMBER_FIELD,
            ],
            capture_output=True,
            text=True,
            cwd=repo_root,
        )
        if result.returncode != 0:
            return None
        prs: object = json.loads(result.stdout)
        if isinstance(prs, list) and len(prs) > 0:
            first: object = prs[0]
            if isinstance(first, dict):
                num: object = first.get(PR_NUMBER_FIELD)
                if isinstance(num, int):
                    return num
        return None
    except (OSError, json.JSONDecodeError):
        return None
