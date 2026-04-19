"""Tests for the ``slug`` alias in aggregate_task_types JSON output.

Spec: JSON output of ``aggregate_task_types`` must include a ``slug`` field
on every task type, equal to ``task_type_id``. Makes output forward-compatible
with consumers that expect ``slug`` (which is how the underlying directory
name is referred to in the rest of ARF).
"""

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT: Path = Path(__file__).resolve().parents[2]

SHIM_MODULE: str = "arf.scripts.aggregators.aggregate_task_types"
TASK_TYPES_KEY: str = "task_types"
TASK_TYPE_ID_KEY: str = "task_type_id"
SLUG_KEY: str = "slug"
SLUG_PATTERN: re.Pattern[str] = re.compile(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def _run_aggregator() -> dict[str, Any]:
    result: subprocess.CompletedProcess[str] = subprocess.run(
        args=[
            sys.executable,
            "-u",
            "-m",
            SHIM_MODULE,
            "--format",
            "json",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, (
        f"Running {SHIM_MODULE} failed with code {result.returncode}; stderr={result.stderr!r}"
    )
    payload: object = json.loads(result.stdout)
    assert isinstance(payload, dict), (
        f"{SHIM_MODULE} JSON output must be an object; got {type(payload).__name__}"
    )
    return payload


def test_every_entry_has_both_task_type_id_and_slug() -> None:
    payload: dict[str, Any] = _run_aggregator()
    assert TASK_TYPES_KEY in payload, (
        f"Output missing {TASK_TYPES_KEY!r} key; got {list(payload.keys())}"
    )
    entries: list[dict[str, Any]] = payload[TASK_TYPES_KEY]
    assert len(entries) > 0, (
        "Expected at least one task type registered in meta/task_types/ "
        "for this test to be meaningful; found none."
    )
    for entry in entries:
        assert TASK_TYPE_ID_KEY in entry, f"Task type entry missing {TASK_TYPE_ID_KEY!r}: {entry}"
        assert SLUG_KEY in entry, f"Task type entry missing {SLUG_KEY!r}: {entry}"


def test_task_type_id_equals_slug() -> None:
    payload: dict[str, Any] = _run_aggregator()
    entries: list[dict[str, Any]] = payload[TASK_TYPES_KEY]
    for entry in entries:
        assert entry[TASK_TYPE_ID_KEY] == entry[SLUG_KEY], (
            f"task_type_id ({entry[TASK_TYPE_ID_KEY]!r}) and slug "
            f"({entry[SLUG_KEY]!r}) must match for entry {entry}"
        )


def test_slug_matches_validation_pattern() -> None:
    payload: dict[str, Any] = _run_aggregator()
    entries: list[dict[str, Any]] = payload[TASK_TYPES_KEY]
    for entry in entries:
        slug: str = entry[SLUG_KEY]
        assert isinstance(slug, str), (
            f"slug must be a string; got {type(slug).__name__} for {entry}"
        )
        assert SLUG_PATTERN.match(string=slug) is not None, (
            f"slug {slug!r} does not match pattern {SLUG_PATTERN.pattern!r}"
        )
