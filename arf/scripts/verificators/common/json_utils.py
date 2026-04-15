import json
from pathlib import Path
from typing import Any


def load_json_file(*, file_path: Path) -> dict[str, Any] | None:
    try:
        raw: str = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    try:
        data: object = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    return data


def check_required_fields(
    *,
    data: dict[str, Any],
    required_fields: list[str],
) -> list[str]:
    missing: list[str] = []
    for field_name in required_fields:
        if field_name not in data:
            missing.append(field_name)
    return missing
