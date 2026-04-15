import json
from pathlib import Path
from typing import Any

import pytest

import arf.scripts.utils.skip_step as skip_step_module
import arf.scripts.verificators.verify_logs as verify_logs_module
from arf.scripts.verificators.common import paths
from arf.scripts.verificators.common.frontmatter import (
    FrontmatterResult,
    extract_frontmatter_and_body,
)
from arf.scripts.verificators.common.markdown_sections import (
    MarkdownSection,
    count_words,
    extract_sections,
)

type TaskID = str

TASKS_SUBDIR: str = "tasks"
TASK_ID: TaskID = "t0099_test_skip"


def _write_json(*, path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(obj=data, indent=2) + "\n",
        encoding="utf-8",
    )


def _configure_repo_paths(
    *,
    monkeypatch: pytest.MonkeyPatch,
    repo_root: Path,
) -> Path:
    tasks_dir: Path = repo_root / TASKS_SUBDIR
    tasks_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(target=paths, name="TASKS_DIR", value=tasks_dir)
    monkeypatch.setattr(
        target=skip_step_module,
        name="TASKS_DIR",
        value=tasks_dir,
    )
    return tasks_dir


def _build_tracker(*, steps: list[dict[str, object]]) -> dict[str, object]:
    return {"task_id": TASK_ID, "steps": steps}


def _make_step(
    *,
    step: int,
    name: str,
    status: str = "not_started",
) -> dict[str, object]:
    return {
        "step": step,
        "name": name,
        "description": f"Test step {name}",
        "status": status,
        "started_at": None,
        "completed_at": None,
        "log_file": None,
    }


def _setup(
    *,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    steps: list[dict[str, object]] | None = None,
) -> Path:
    tasks_dir: Path = _configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=tmp_path,
    )
    task_dir: Path = tasks_dir / TASK_ID
    task_dir.mkdir(parents=True, exist_ok=True)

    if steps is None:
        steps = [
            _make_step(step=4, name="research-papers"),
            _make_step(step=5, name="research-internet"),
            _make_step(step=6, name="research-code"),
            _make_step(step=7, name="planning"),
        ]

    tracker: dict[str, object] = _build_tracker(steps=steps)
    _write_json(
        path=task_dir / "step_tracker.json",
        data=tracker,
    )
    return task_dir


def test_skip_single_step(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    task_dir: Path = _setup(
        monkeypatch=monkeypatch,
        tmp_path=tmp_path,
    )

    results: list[skip_step_module.SkipResult] = skip_step_module.skip_steps(
        task_id=TASK_ID,
        requests=[
            skip_step_module.SkipRequest(
                step_id="research-papers",
                reason="No relevant papers in corpus.",
            ),
        ],
    )

    assert len(results) == 1
    assert results[0].step_id == "research-papers"
    assert results[0].step_number == 4

    log_file: Path = task_dir / "logs" / "steps" / "004_research-papers" / "step_log.md"
    assert log_file.exists() is True

    content: str = log_file.read_text(encoding="utf-8")
    assert 'status: "skipped"' in content
    assert f'task_id: "{TASK_ID}"' in content
    assert "step_number: 4" in content
    assert "No relevant papers in corpus." in content
    assert "## Summary" in content
    assert "## Actions Taken" in content
    assert "## Outputs" in content
    assert "## Issues" in content


def test_skip_multiple_steps(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    task_dir: Path = _setup(
        monkeypatch=monkeypatch,
        tmp_path=tmp_path,
    )

    results: list[skip_step_module.SkipResult] = skip_step_module.skip_steps(
        task_id=TASK_ID,
        requests=[
            skip_step_module.SkipRequest(
                step_id="research-papers",
                reason="No papers needed.",
            ),
            skip_step_module.SkipRequest(
                step_id="research-code",
                reason="No prior code.",
            ),
        ],
    )

    assert len(results) == 2

    for r in results:
        log_dir: Path = task_dir / "logs" / "steps" / f"{r.step_number:03d}_{r.step_id}"
        assert (log_dir / "step_log.md").exists() is True


def test_skip_updates_step_tracker(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    task_dir: Path = _setup(
        monkeypatch=monkeypatch,
        tmp_path=tmp_path,
    )

    skip_step_module.skip_steps(
        task_id=TASK_ID,
        requests=[
            skip_step_module.SkipRequest(
                step_id="research-internet",
                reason="Not needed.",
            ),
        ],
    )

    tracker: dict[str, object] = json.loads(
        (task_dir / "step_tracker.json").read_text(encoding="utf-8"),
    )
    steps: list[dict[str, object]] = tracker["steps"]  # type: ignore[assignment]
    internet_step: dict[str, object] | None = None
    for s in steps:
        if s.get("name") == "research-internet":
            internet_step = s
            break

    assert internet_step is not None
    assert internet_step["status"] == "skipped"
    assert internet_step["log_file"] == "logs/steps/005_research-internet/"


def test_skip_nonexistent_step_exits(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _setup(monkeypatch=monkeypatch, tmp_path=tmp_path)

    with pytest.raises(SystemExit) as exc_info:
        skip_step_module.skip_steps(
            task_id=TASK_ID,
            requests=[
                skip_step_module.SkipRequest(
                    step_id="nonexistent-step",
                    reason="Does not exist.",
                ),
            ],
        )

    assert exc_info.value.code == 1


def test_skip_already_completed_step_exits(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _setup(
        monkeypatch=monkeypatch,
        tmp_path=tmp_path,
        steps=[
            _make_step(step=4, name="research-papers", status="completed"),
        ],
    )

    with pytest.raises(SystemExit) as exc_info:
        skip_step_module.skip_steps(
            task_id=TASK_ID,
            requests=[
                skip_step_module.SkipRequest(
                    step_id="research-papers",
                    reason="Want to skip.",
                ),
            ],
        )

    assert exc_info.value.code == 1


def test_skip_missing_tracker_exits(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tasks_dir: Path = _configure_repo_paths(
        monkeypatch=monkeypatch,
        repo_root=tmp_path,
    )
    task_dir: Path = tasks_dir / TASK_ID
    task_dir.mkdir(parents=True, exist_ok=True)
    # No step_tracker.json created

    with pytest.raises(SystemExit) as exc_info:
        skip_step_module.skip_steps(
            task_id=TASK_ID,
            requests=[
                skip_step_module.SkipRequest(
                    step_id="research-papers",
                    reason="No tracker.",
                ),
            ],
        )

    assert exc_info.value.code == 1


def test_step_log_has_correct_frontmatter_fields(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    task_dir: Path = _setup(
        monkeypatch=monkeypatch,
        tmp_path=tmp_path,
    )

    skip_step_module.skip_steps(
        task_id=TASK_ID,
        requests=[
            skip_step_module.SkipRequest(
                step_id="planning",
                reason="Task type does not require planning.",
            ),
        ],
    )

    log_file: Path = task_dir / "logs" / "steps" / "007_planning" / "step_log.md"
    content: str = log_file.read_text(encoding="utf-8")

    assert 'spec_version: "3"' in content
    assert f'task_id: "{TASK_ID}"' in content
    assert "step_number: 7" in content
    assert 'step_name: "planning"' in content
    assert 'status: "skipped"' in content
    assert "started_at:" in content
    assert "completed_at:" in content


def test_skip_step_summary_meets_min_word_count_with_short_reason(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    task_dir: Path = _setup(
        monkeypatch=monkeypatch,
        tmp_path=tmp_path,
    )

    skip_step_module.skip_steps(
        task_id=TASK_ID,
        requests=[
            skip_step_module.SkipRequest(
                step_id="planning",
                reason="N/A.",
            ),
        ],
    )

    log_file: Path = task_dir / "logs" / "steps" / "007_planning" / "step_log.md"
    content: str = log_file.read_text(encoding="utf-8")

    fm_result: FrontmatterResult | None = extract_frontmatter_and_body(content=content)
    assert fm_result is not None, "step_log.md must have frontmatter + body"
    sections: list[MarkdownSection] = extract_sections(body=fm_result.body, level=2)
    summary_sections: list[MarkdownSection] = [s for s in sections if s.heading == "Summary"]
    assert len(summary_sections) == 1
    summary_word_count: int = count_words(text=summary_sections[0].content)
    assert summary_word_count >= verify_logs_module.MIN_SUMMARY_WORDS, (
        f"Summary has {summary_word_count} words "
        f"(minimum: {verify_logs_module.MIN_SUMMARY_WORDS}). "
        f"Summary body:\n{summary_sections[0].content}"
    )


def test_unskipped_steps_remain_not_started(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    task_dir: Path = _setup(
        monkeypatch=monkeypatch,
        tmp_path=tmp_path,
    )

    skip_step_module.skip_steps(
        task_id=TASK_ID,
        requests=[
            skip_step_module.SkipRequest(
                step_id="research-papers",
                reason="Not needed.",
            ),
        ],
    )

    tracker: dict[str, object] = json.loads(
        (task_dir / "step_tracker.json").read_text(encoding="utf-8"),
    )
    steps: list[dict[str, object]] = tracker["steps"]  # type: ignore[assignment]
    for s in steps:
        if s.get("name") != "research-papers":
            assert s["status"] == "not_started", f"step {s['name']} should remain not_started"


def test_reskip_is_idempotent_noop(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    task_dir: Path = _setup(
        monkeypatch=monkeypatch,
        tmp_path=tmp_path,
    )

    request: skip_step_module.SkipRequest = skip_step_module.SkipRequest(
        step_id="research-papers",
        reason="Not needed.",
    )

    first_results: list[skip_step_module.SkipResult] = skip_step_module.skip_steps(
        task_id=TASK_ID,
        requests=[request],
    )
    assert len(first_results) == 1

    tracker_path: Path = task_dir / "step_tracker.json"
    tracker_before: dict[str, object] = json.loads(
        tracker_path.read_text(encoding="utf-8"),
    )
    steps_before: list[dict[str, object]] = tracker_before["steps"]  # type: ignore[assignment]
    step_before: dict[str, object] | None = None
    for s in steps_before:
        if s.get("name") == "research-papers":
            step_before = s
            break
    assert step_before is not None
    assert step_before.get("status") == "skipped"

    log_file: Path = task_dir / "logs" / "steps" / "004_research-papers" / "step_log.md"
    assert log_file.exists() is True
    content_before: str = log_file.read_text(encoding="utf-8")

    second_results: list[skip_step_module.SkipResult] = skip_step_module.skip_steps(
        task_id=TASK_ID,
        requests=[request],
    )

    assert len(second_results) == 1
    assert second_results[0].step_id == "research-papers"
    assert second_results[0].step_number == 4

    tracker_after: dict[str, object] = json.loads(
        tracker_path.read_text(encoding="utf-8"),
    )
    steps_after: list[dict[str, object]] = tracker_after["steps"]  # type: ignore[assignment]
    step_after: dict[str, object] | None = None
    for s in steps_after:
        if s.get("name") == "research-papers":
            step_after = s
            break
    assert step_after is not None
    assert step_after == step_before

    content_after: str = log_file.read_text(encoding="utf-8")
    assert content_after == content_before
