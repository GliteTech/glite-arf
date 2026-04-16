"""Capture raw agent session transcripts for a task.

Usage:
    uv run python -m arf.scripts.utils.capture_task_sessions --task-id <task_id>
    uv run python -m arf.scripts.utils.capture_task_sessions --skill <skill-slug>
    uv run python -m arf.scripts.utils.capture_task_sessions --current

Task mode (``--task-id``) captures into ``tasks/<task_id>/logs/sessions/``:

    1. Scans supported CLI session roots recursively.
    2. Matches JSONL transcript files via PID mapping (Claude Code), thread ID (Codex),
       and content-based task ID matching (fallback).
    3. Copies all matching transcripts into tasks/<task_id>/logs/sessions/.
    4. Writes logs/sessions/capture_report.json with the scan summary.

Skill mode (``--skill <slug>``) and current-session mode (``--current``) are
read-only discovery modes used by meta-skills such as ``self-analyze``. They
print the resolved JSONL paths to stdout and exit 0 without copying files.

Session capture is best-effort. Missing transcript roots or zero matches are reported in the JSON
report, but they are not fatal errors for the script itself.
"""

import argparse
import gzip
import json
import os
import shutil
import sys
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import assert_never

from arf.scripts.verificators.common.paths import (
    REPO_ROOT,
    session_capture_report_path,
    session_logs_dir,
    task_dir,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SPEC_VERSION: str = "1"
MATCH_KIND_PID: str = "pid_mapping"
MATCH_KIND_THREAD_ID: str = "codex_thread_id"
MATCH_KIND_CONTENT: str = "task_id_content"
JSONL_GLOB: str = "*.jsonl"
GITKEEP_FILE_NAME: str = ".gitkeep"
CODEX_SOURCE_KIND: str = "codex"
CLAUDE_CODE_SOURCE_KIND: str = "claude_code"
TASK_SCAN_CHUNK_BYTES: int = 64 * 1024
CAPTURE_REPORT_FILE_NAME: str = "capture_report.json"
SESSION_COMPRESS_THRESHOLD_BYTES: int = 4 * 1024 * 1024  # 4 MB
SESSION_LOGS_RELATIVE_PREFIX: str = "logs/sessions"
DATETIME_FORMAT: str = "%Y-%m-%dT%H:%M:%SZ"

# Claude Code session directory names
CLAUDE_SESSIONS_DIR_NAME: str = "sessions"
CLAUDE_PROJECTS_DIR_NAME: str = "projects"
SUBAGENTS_DIR_NAME: str = "subagents"

# Codex session directory name under ``~/.codex/``
CODEX_SESSIONS_DIR_NAME: str = "sessions"

# Worktree path suffix for matching cwd to task.
# The worktree utility creates worktrees in ``<repo>-worktrees/<task_id>``.
WORKTREE_PARENT_SUFFIX: str = "-worktrees"

# Environment variable for Codex thread ID
CODEX_THREAD_ID_ENV_VAR: str = "CODEX_THREAD_ID"


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class SessionSourceRoot:
    source_kind: str
    root_path: Path


@dataclass(frozen=True, slots=True)
class SessionRootScan:
    source_kind: str
    root_path: str
    exists: bool
    candidate_file_count: int
    matched_file_count: int


@dataclass(frozen=True, slots=True)
class CapturedSession:
    source_kind: str
    source_path: str
    copied_path: str
    matched_by: str


@dataclass(frozen=True, slots=True)
class SessionCaptureReport:
    spec_version: str
    task_id: str
    captured_at: str
    checked_roots: list[SessionRootScan]
    copied_sessions: list[CapturedSession]
    errors: list[str]


@dataclass(frozen=True, slots=True)
class SessionCaptureOutcome:
    report_path: Path
    sessions_dir: Path
    report: SessionCaptureReport


@dataclass(frozen=True, slots=True)
class PreciseMatch:
    file_path: Path
    match_kind: str


# ---------------------------------------------------------------------------
# Discovery API target types
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class TaskTarget:
    """Discovery target: a specific ``tNNNN_*`` task."""

    task_id: str


@dataclass(frozen=True, slots=True)
class SkillSlugTarget:
    """Discovery target: the most recent session that invoked a named skill.

    ``slug`` is the skill directory name under ``arf/skills/``. The discovery
    function content-matches each candidate transcript against both the bare
    slug and the ``arf/skills/<slug>/SKILL.md`` path, taking the first hit.
    """

    slug: str


@dataclass(frozen=True, slots=True)
class CurrentSessionTarget:
    """Discovery target: the currently running session.

    If ``CODEX_THREAD_ID`` is set, uses that to locate the Codex transcript.
    Otherwise, falls back to the most recent ``~/.claude/projects/<encoded>``
    JSONL by mtime (plus its co-located subagent transcripts).
    """


type SessionDiscoveryTarget = TaskTarget | SkillSlugTarget | CurrentSessionTarget


@dataclass(frozen=True, slots=True)
class SessionDiscoveryResult:
    """Result of a ``discover_session_files`` call.

    * ``target_description`` — short label such as ``"task:t0003_foo"``,
      ``"skill:human-brainstorm"``, or ``"current"``.
    * ``matched_files`` — absolute JSONL paths, deduplicated but preserving
      first-seen order.
    * ``checked_roots`` — every root the discovery walked, whether it existed,
      and how many files were considered.
    * ``resolution_note`` — human-readable one-liner explaining which matching
      strategy produced the result.
    """

    target_description: str
    matched_files: list[Path]
    checked_roots: list[SessionRootScan]
    resolution_note: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _default_source_roots(*, home_dir: Path) -> list[SessionSourceRoot]:
    return [
        SessionSourceRoot(
            source_kind=CODEX_SOURCE_KIND,
            root_path=home_dir / ".codex" / "sessions",
        ),
        SessionSourceRoot(
            source_kind=CLAUDE_CODE_SOURCE_KIND,
            root_path=home_dir / ".claude" / "projects",
        ),
    ]


def _iter_candidate_files(*, source_root: SessionSourceRoot) -> list[Path]:
    if source_root.root_path.is_dir() is False:
        return []
    return sorted(
        path for path in source_root.root_path.rglob(JSONL_GLOB) if path.is_file() is True
    )


def _file_mentions_task_id(
    *,
    file_path: Path,
    task_id: str,
) -> bool:
    task_id_bytes: bytes = task_id.encode("utf-8")
    overlap_size: int = max(len(task_id_bytes) - 1, 0)
    trailing_bytes: bytes = b""

    with file_path.open("rb") as handle:
        while True:
            chunk: bytes = handle.read(TASK_SCAN_CHUNK_BYTES)
            if len(chunk) == 0:
                return False

            haystack: bytes = trailing_bytes + chunk
            if task_id_bytes in haystack:
                return True

            trailing_bytes = haystack[-overlap_size:] if overlap_size > 0 else b""


def _build_destination_name(
    *,
    source_root: SessionSourceRoot,
    source_path: Path,
) -> str:
    relative_path: Path = source_path.relative_to(source_root.root_path)
    relative_slug: str = "__".join(relative_path.parts)
    return f"{source_root.source_kind}__{relative_slug}"


def _reset_sessions_dir(*, destination_dir: Path) -> list[str]:
    destination_dir.mkdir(parents=True, exist_ok=True)
    errors: list[str] = []

    for entry in sorted(destination_dir.iterdir()):
        if entry.name == GITKEEP_FILE_NAME:
            continue
        try:
            if entry.is_dir() is True:
                shutil.rmtree(entry)
            else:
                entry.unlink()
        except OSError as exc:
            errors.append(f"Failed to remove stale session log '{entry}': {exc}")

    return errors


def _cwd_to_encoded_path(*, cwd: str) -> str:
    # Claude Code encodes project paths by replacing / with -
    return cwd.replace("/", "-")


def cwd_to_encoded_path(*, cwd: str) -> str:
    """Public wrapper around the Claude Code project-path encoding rule.

    Converts an absolute filesystem path (e.g.
    ``/Users/me/glite-arf``) into the encoded directory name under
    ``~/.claude/projects/`` by replacing every ``/`` with ``-``.

    Public so that callers outside this module (notably the ``self-analyze``
    skill, via the CLI) do not need to re-derive the encoding rule.
    """
    return _cwd_to_encoded_path(cwd=cwd)


def _path_has_worktree_evidence(*, file_path: Path, task_id: str) -> bool:
    """Check whether a file path has worktree-level evidence of belonging to a task.

    Returns True if any directory component in the path contains a worktree
    indicator (``-worktrees``) AND the task ID or its numeric prefix. This
    distinguishes worktree sessions from repo-root sessions that merely mention
    the task ID in their content.
    """
    task_prefix: str = task_id.split("_")[0] if "_" in task_id else task_id
    path_str: str = str(file_path)
    if WORKTREE_PARENT_SUFFIX not in path_str:
        return False
    return task_id in path_str or task_prefix in path_str


def _cwd_value_references_task_worktree(
    *,
    cwd_value: str,
    task_id: str,
    task_prefix: str,
) -> bool:
    if WORKTREE_PARENT_SUFFIX not in cwd_value:
        return False
    return task_id in cwd_value or task_prefix in cwd_value


def _payload_has_worktree_cwd(
    *,
    data: object,
    task_id: str,
    task_prefix: str,
) -> bool:
    if isinstance(data, dict):
        for key, value in data.items():
            if (
                key == "cwd"
                and isinstance(value, str)
                and _cwd_value_references_task_worktree(
                    cwd_value=value,
                    task_id=task_id,
                    task_prefix=task_prefix,
                )
            ):
                return True
            if _payload_has_worktree_cwd(
                data=value,
                task_id=task_id,
                task_prefix=task_prefix,
            ):
                return True
    elif isinstance(data, list):
        for item in data:
            if _payload_has_worktree_cwd(
                data=item,
                task_id=task_id,
                task_prefix=task_prefix,
            ):
                return True
    return False


def _jsonl_content_has_worktree_cwd(
    *,
    file_path: Path,
    task_id: str,
) -> bool:
    """Check whether a JSONL session file has a ``cwd`` field pointing at a
    worktree directory for this task.

    Applies to any newline-delimited JSON session transcript (Codex or Claude
    Code). Each line may record ``cwd`` at the top level (e.g. Codex
    ``session_meta`` events, Claude Code messages), nested inside a
    ``payload.arguments`` object (Codex tool calls), or anywhere else in the
    JSON tree. This helper scans the file line-by-line and returns True as
    soon as any decoded object contains a ``cwd`` string that references the
    task worktree (contains ``-worktrees`` and the task ID or its numeric
    prefix).

    Lines that do not contain both the worktree suffix and the task marker are
    skipped without JSON parsing, keeping the scan cheap on large files.
    """
    task_prefix: str = task_id.split("_")[0] if "_" in task_id else task_id

    try:
        with file_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if WORKTREE_PARENT_SUFFIX not in line:
                    continue
                if task_id not in line and task_prefix not in line:
                    continue
                try:
                    data: object = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if _payload_has_worktree_cwd(
                    data=data,
                    task_id=task_id,
                    task_prefix=task_prefix,
                ):
                    return True
    except OSError:
        return False
    return False


def _cwd_matches_task(*, cwd: str, task_id: str, repo_root: Path | None = None) -> bool:
    """Check whether a session cwd corresponds to work on *task_id*.

    A cwd matches if it is a worktree directory whose parent ends with
    ``-worktrees`` and whose name contains the task ID or its numeric
    prefix.  Repo-root sessions are intentionally excluded — they are
    ambiguous and could belong to any task.
    """
    cwd_path: Path = Path(cwd)

    # Repo root is intentionally NOT matched — sessions run from the repo root
    # are ambiguous and could belong to any task. Only worktree matches are
    # precise enough.

    # Worktree match: parent directory ends with ``-worktrees`` and the
    # directory name relates to the task.
    parent_name: str = cwd_path.parent.name
    if parent_name.endswith(WORKTREE_PARENT_SUFFIX):
        task_prefix: str = task_id.split("_")[0] if "_" in task_id else task_id
        dir_name: str = cwd_path.name
        if task_prefix in dir_name or task_id in dir_name:
            return True

    return False


def _compress_if_large(
    *,
    path: Path,
    threshold_bytes: int = SESSION_COMPRESS_THRESHOLD_BYTES,
) -> Path:
    """Gzip-compress a file if it exceeds the size threshold.

    Returns the (possibly renamed) path. If compressed, the original
    file is removed and the ``.gz`` path is returned.
    """
    try:
        size: int = path.stat().st_size
    except OSError:
        return path
    if size <= threshold_bytes:
        return path

    gz_path: Path = path.with_suffix(path.suffix + ".gz")
    with open(file=path, mode="rb") as f_in, gzip.open(filename=gz_path, mode="wb") as f_out:
        while True:
            chunk: bytes = f_in.read(65536)
            if len(chunk) == 0:
                break
            f_out.write(chunk)
    path.unlink()
    return gz_path


def _collect_session_files_for_id(
    *,
    projects_dir: Path,
    encoded_path: str,
    session_id: str,
) -> list[Path]:
    """Collect the main JSONL and all subagent JSONLs for a session."""
    project_dir: Path = projects_dir / encoded_path
    files: list[Path] = []

    main_jsonl: Path = project_dir / f"{session_id}.jsonl"
    if main_jsonl.is_file() is True:
        files.append(main_jsonl)

    subagents_dir: Path = project_dir / session_id / SUBAGENTS_DIR_NAME
    if subagents_dir.is_dir() is True:
        for subagent_file in sorted(subagents_dir.rglob(JSONL_GLOB)):
            if subagent_file.is_file() is True:
                files.append(subagent_file)

    return files


def _find_claude_sessions_by_pid(
    *,
    task_id: str,
    home_dir: Path,
) -> list[PreciseMatch]:
    """Find Claude Code session files by scanning PID mapping files.

    Reads JSON files from ``~/.claude/sessions/``. Each file has the format::

        {"pid": N, "sessionId": "...", "cwd": "..."}

    For every PID file whose ``cwd`` matches the task worktree path pattern or the
    main repo path, collects the corresponding JSONL transcript and subagent files
    from ``~/.claude/projects/<encoded-path>/<sessionId>.jsonl``.
    """
    sessions_dir: Path = home_dir / ".claude" / CLAUDE_SESSIONS_DIR_NAME
    projects_dir: Path = home_dir / ".claude" / CLAUDE_PROJECTS_DIR_NAME

    if sessions_dir.is_dir() is False or projects_dir.is_dir() is False:
        return []

    matches: list[PreciseMatch] = []

    for pid_file in sorted(sessions_dir.iterdir()):
        if pid_file.suffix != ".json" or pid_file.is_file() is False:
            continue

        try:
            raw: object = json.loads(pid_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue

        if not isinstance(raw, dict):
            continue

        cwd: object = raw.get("cwd")
        session_id: object = raw.get("sessionId")
        if not isinstance(cwd, str) or not isinstance(session_id, str):
            continue

        if _cwd_matches_task(cwd=cwd, task_id=task_id, repo_root=REPO_ROOT) is False:
            continue

        encoded_path: str = _cwd_to_encoded_path(cwd=cwd)
        session_files: list[Path] = _collect_session_files_for_id(
            projects_dir=projects_dir,
            encoded_path=encoded_path,
            session_id=session_id,
        )
        for file_path in session_files:
            matches.append(
                PreciseMatch(
                    file_path=file_path,
                    match_kind=MATCH_KIND_PID,
                ),
            )

    return matches


def _find_codex_session_by_thread_id(
    *,
    codex_sessions_root: Path,
) -> list[PreciseMatch]:
    thread_id: str | None = os.environ.get(CODEX_THREAD_ID_ENV_VAR)
    if thread_id is None or len(thread_id) == 0:
        return []

    if codex_sessions_root.is_dir() is False:
        return []

    matches: list[PreciseMatch] = []
    for jsonl_file in sorted(codex_sessions_root.rglob(JSONL_GLOB)):
        if jsonl_file.is_file() is False:
            continue
        if thread_id in jsonl_file.name:
            matches.append(
                PreciseMatch(
                    file_path=jsonl_file,
                    match_kind=MATCH_KIND_THREAD_ID,
                ),
            )

    return matches


# ---------------------------------------------------------------------------
# Discovery API: read-only, no copying
# ---------------------------------------------------------------------------


def _file_contains_any_token(
    *,
    file_path: Path,
    tokens: list[bytes],
) -> bool:
    """Stream-scan ``file_path`` for any of the given byte tokens.

    Generalization of ``_file_mentions_task_id`` for the discovery API.
    """
    if len(tokens) == 0:
        return False
    overlap_size: int = max(max(len(t) for t in tokens) - 1, 0)
    trailing_bytes: bytes = b""
    with file_path.open("rb") as handle:
        while True:
            chunk: bytes = handle.read(TASK_SCAN_CHUNK_BYTES)
            if len(chunk) == 0:
                return False
            haystack: bytes = trailing_bytes + chunk
            for token in tokens:
                if token in haystack:
                    return True
            trailing_bytes = haystack[-overlap_size:] if overlap_size > 0 else b""


def _claude_projects_dir_for_repo(*, home_dir: Path) -> Path:
    encoded: str = cwd_to_encoded_path(cwd=str(REPO_ROOT))
    return home_dir / ".claude" / CLAUDE_PROJECTS_DIR_NAME / encoded


def _collect_claude_subagent_files(*, jsonl_file: Path) -> list[Path]:
    session_id: str = jsonl_file.stem
    subagents_dir: Path = jsonl_file.parent / session_id / SUBAGENTS_DIR_NAME
    if subagents_dir.is_dir() is False:
        return []
    return sorted(f for f in subagents_dir.rglob(JSONL_GLOB) if f.is_file() is True)


def _discover_task_target(
    *,
    task_id: str,
    home_dir: Path,
) -> SessionDiscoveryResult:
    """Reuse the existing task-matching logic, without copying files."""
    source_roots: list[SessionSourceRoot] = _default_source_roots(home_dir=home_dir)
    matched: list[Path] = []
    seen: set[Path] = set()
    checked_roots: list[SessionRootScan] = []

    # Phase 1: precise PID / thread-id matching
    for source_root in source_roots:
        if source_root.root_path.is_dir() is False:
            continue
        try:
            if source_root.source_kind == CLAUDE_CODE_SOURCE_KIND:
                for m in _find_claude_sessions_by_pid(
                    task_id=task_id,
                    home_dir=home_dir,
                ):
                    resolved: Path = m.file_path.resolve()
                    if resolved not in seen:
                        matched.append(m.file_path)
                        seen.add(resolved)
            elif source_root.source_kind == CODEX_SOURCE_KIND:
                for m in _find_codex_session_by_thread_id(
                    codex_sessions_root=source_root.root_path,
                ):
                    resolved = m.file_path.resolve()
                    if resolved not in seen:
                        matched.append(m.file_path)
                        seen.add(resolved)
        except OSError:
            continue

    # Phase 2: content fallback
    for source_root in source_roots:
        candidate_files: list[Path] = _iter_candidate_files(source_root=source_root)
        matched_count: int = 0
        for candidate in candidate_files:
            try:
                resolved = candidate.resolve()
            except OSError:
                continue
            if resolved in seen:
                matched_count += 1
                continue
            try:
                if _file_mentions_task_id(file_path=candidate, task_id=task_id) is False:
                    continue
            except OSError:
                continue
            if source_root.source_kind == CLAUDE_CODE_SOURCE_KIND:
                has_path_evidence: bool = _path_has_worktree_evidence(
                    file_path=candidate,
                    task_id=task_id,
                )
                if (
                    has_path_evidence is False
                    and _jsonl_content_has_worktree_cwd(
                        file_path=candidate,
                        task_id=task_id,
                    )
                    is False
                ):
                    continue
            if (
                source_root.source_kind == CODEX_SOURCE_KIND
                and _jsonl_content_has_worktree_cwd(
                    file_path=candidate,
                    task_id=task_id,
                )
                is False
            ):
                continue
            matched.append(candidate)
            seen.add(resolved)
            matched_count += 1

        checked_roots.append(
            SessionRootScan(
                source_kind=source_root.source_kind,
                root_path=str(source_root.root_path),
                exists=source_root.root_path.is_dir(),
                candidate_file_count=len(candidate_files),
                matched_file_count=matched_count,
            ),
        )

    note: str = (
        f"Resolved {len(matched)} transcript(s) for task '{task_id}' "
        "via PID/thread-id precise match + content-match fallback."
    )
    return SessionDiscoveryResult(
        target_description=f"task:{task_id}",
        matched_files=matched,
        checked_roots=checked_roots,
        resolution_note=note,
    )


def _discover_skill_target(
    *,
    slug: str,
    home_dir: Path,
) -> SessionDiscoveryResult:
    """Content-match the skill slug against recent Claude / Codex transcripts."""
    claude_project_dir: Path = _claude_projects_dir_for_repo(home_dir=home_dir)
    codex_root: Path = home_dir / ".codex" / CODEX_SESSIONS_DIR_NAME

    tokens: list[bytes] = [
        slug.encode("utf-8"),
        f"arf/skills/{slug}/SKILL.md".encode(),
    ]

    def _candidates(root: Path) -> list[Path]:
        if root.is_dir() is False:
            return []
        return sorted(
            (f for f in root.rglob(JSONL_GLOB) if f.is_file() is True),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

    matched: list[Path] = []
    seen: set[Path] = set()
    checked_roots: list[SessionRootScan] = []

    # Claude Code transcripts scoped to this repo's encoded project dir
    claude_candidates: list[Path] = _candidates(claude_project_dir)
    claude_matched: int = 0
    for candidate in claude_candidates:
        try:
            if _file_contains_any_token(file_path=candidate, tokens=tokens) is False:
                continue
        except OSError:
            continue
        resolved: Path = candidate.resolve()
        if resolved in seen:
            continue
        matched.append(candidate)
        seen.add(resolved)
        claude_matched += 1
        for subagent in _collect_claude_subagent_files(jsonl_file=candidate):
            sub_resolved: Path = subagent.resolve()
            if sub_resolved not in seen:
                matched.append(subagent)
                seen.add(sub_resolved)
        break  # stop at first match (newest by mtime)

    checked_roots.append(
        SessionRootScan(
            source_kind=CLAUDE_CODE_SOURCE_KIND,
            root_path=str(claude_project_dir),
            exists=claude_project_dir.is_dir(),
            candidate_file_count=len(claude_candidates),
            matched_file_count=claude_matched,
        ),
    )

    # Codex transcripts (global, not scoped to cwd)
    codex_candidates: list[Path] = _candidates(codex_root)
    codex_matched: int = 0
    for candidate in codex_candidates:
        try:
            if _file_contains_any_token(file_path=candidate, tokens=tokens) is False:
                continue
        except OSError:
            continue
        resolved = candidate.resolve()
        if resolved in seen:
            continue
        matched.append(candidate)
        seen.add(resolved)
        codex_matched += 1
        break

    checked_roots.append(
        SessionRootScan(
            source_kind=CODEX_SOURCE_KIND,
            root_path=str(codex_root),
            exists=codex_root.is_dir(),
            candidate_file_count=len(codex_candidates),
            matched_file_count=codex_matched,
        ),
    )

    note: str = (
        f"Resolved {len(matched)} transcript(s) for skill '{slug}' "
        "via content match on the slug and SKILL.md path."
    )
    return SessionDiscoveryResult(
        target_description=f"skill:{slug}",
        matched_files=matched,
        checked_roots=checked_roots,
        resolution_note=note,
    )


def _discover_current_target(*, home_dir: Path) -> SessionDiscoveryResult:
    """Resolve the currently running session via CODEX_THREAD_ID or newest mtime."""
    matched: list[Path] = []
    seen: set[Path] = set()
    checked_roots: list[SessionRootScan] = []
    note: str

    codex_root: Path = home_dir / ".codex" / CODEX_SESSIONS_DIR_NAME
    thread_id: str | None = os.environ.get(CODEX_THREAD_ID_ENV_VAR)

    if thread_id is not None and len(thread_id) > 0:
        codex_matches: list[PreciseMatch] = _find_codex_session_by_thread_id(
            codex_sessions_root=codex_root,
        )
        matched_count: int = 0
        for m in codex_matches:
            resolved: Path = m.file_path.resolve()
            if resolved not in seen:
                matched.append(m.file_path)
                seen.add(resolved)
                matched_count += 1
        checked_roots.append(
            SessionRootScan(
                source_kind=CODEX_SOURCE_KIND,
                root_path=str(codex_root),
                exists=codex_root.is_dir(),
                candidate_file_count=matched_count,
                matched_file_count=matched_count,
            ),
        )
        if len(matched) > 0:
            note = (
                f"Resolved {len(matched)} Codex transcript(s) via "
                f"{CODEX_THREAD_ID_ENV_VAR}='{thread_id}'."
            )
            return SessionDiscoveryResult(
                target_description="current",
                matched_files=matched,
                checked_roots=checked_roots,
                resolution_note=note,
            )

    # Fall back to most recent Claude Code session for this repo
    claude_project_dir: Path = _claude_projects_dir_for_repo(home_dir=home_dir)
    candidates: list[Path] = []
    if claude_project_dir.is_dir() is True:
        candidates = sorted(
            (f for f in claude_project_dir.rglob(JSONL_GLOB) if f.is_file() is True),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
    claude_matched: int = 0
    if len(candidates) > 0:
        newest: Path = candidates[0]
        matched.append(newest)
        seen.add(newest.resolve())
        claude_matched += 1
        for subagent in _collect_claude_subagent_files(jsonl_file=newest):
            sub_resolved: Path = subagent.resolve()
            if sub_resolved not in seen:
                matched.append(subagent)
                seen.add(sub_resolved)
    checked_roots.append(
        SessionRootScan(
            source_kind=CLAUDE_CODE_SOURCE_KIND,
            root_path=str(claude_project_dir),
            exists=claude_project_dir.is_dir(),
            candidate_file_count=len(candidates),
            matched_file_count=claude_matched,
        ),
    )

    if len(matched) == 0:
        note = "No current session found: no CODEX_THREAD_ID and no Claude sessions for this repo."
    else:
        note = (
            f"Resolved {len(matched)} Claude transcript(s) as the "
            "newest session for this repo (no CODEX_THREAD_ID set)."
        )

    return SessionDiscoveryResult(
        target_description="current",
        matched_files=matched,
        checked_roots=checked_roots,
        resolution_note=note,
    )


def discover_session_files(
    *,
    target: SessionDiscoveryTarget,
    home_dir: Path | None = None,
) -> SessionDiscoveryResult:
    """Public discovery API: resolve agent session transcripts to a path list.

    Does not copy files, does not mutate any task folder. Callers read the
    ``matched_files`` list and open the jsonl transcripts themselves.
    Intended for meta-skills such as ``self-analyze`` that review past
    sessions without modifying them.
    """
    resolved_home_dir: Path = home_dir if home_dir is not None else Path.home()
    if isinstance(target, TaskTarget):
        return _discover_task_target(
            task_id=target.task_id,
            home_dir=resolved_home_dir,
        )
    if isinstance(target, SkillSlugTarget):
        return _discover_skill_target(
            slug=target.slug,
            home_dir=resolved_home_dir,
        )
    if isinstance(target, CurrentSessionTarget):
        return _discover_current_target(home_dir=resolved_home_dir)
    assert_never(target)


def capture_task_sessions(
    *,
    task_id: str,
    source_roots: list[SessionSourceRoot] | None = None,
    home_dir: Path | None = None,
) -> SessionCaptureOutcome:
    task_root: Path = task_dir(task_id=task_id)
    if task_root.is_dir() is False:
        raise FileNotFoundError(f"Task directory does not exist: {task_root}")

    resolved_home_dir: Path = home_dir if home_dir is not None else Path.home()
    resolved_source_roots: list[SessionSourceRoot] = (
        source_roots
        if source_roots is not None
        else _default_source_roots(home_dir=resolved_home_dir)
    )
    destination_dir: Path = session_logs_dir(task_id=task_id)
    report_path: Path = session_capture_report_path(task_id=task_id)
    errors: list[str] = _reset_sessions_dir(destination_dir=destination_dir)

    # ------------------------------------------------------------------
    # Phase 1: Precise matching (PID for Claude Code, thread ID for Codex)
    # ------------------------------------------------------------------
    precise_matched_paths: set[Path] = set()
    precise_matches: list[PreciseMatch] = []

    for source_root in resolved_source_roots:
        if source_root.root_path.is_dir() is False:
            continue

        if source_root.source_kind == CLAUDE_CODE_SOURCE_KIND:
            try:
                claude_matches: list[PreciseMatch] = _find_claude_sessions_by_pid(
                    task_id=task_id,
                    home_dir=resolved_home_dir,
                )
                precise_matches.extend(claude_matches)
            except OSError as exc:
                errors.append(f"PID-based Claude Code session scan failed: {exc}")

        elif source_root.source_kind == CODEX_SOURCE_KIND:
            try:
                codex_matches: list[PreciseMatch] = _find_codex_session_by_thread_id(
                    codex_sessions_root=source_root.root_path,
                )
                precise_matches.extend(codex_matches)
            except OSError as exc:
                errors.append(f"Thread-ID-based Codex session scan failed: {exc}")

    for match in precise_matches:
        precise_matched_paths.add(match.file_path.resolve())

    # ------------------------------------------------------------------
    # Phase 2: Content-based matching (fallback), skipping already matched
    # ------------------------------------------------------------------
    checked_roots: list[SessionRootScan] = []
    copied_sessions: list[CapturedSession] = []

    # First, copy all precise matches
    for match in precise_matches:
        # Determine which source root this file belongs to
        source_root_for_match: SessionSourceRoot | None = None
        for source_root in resolved_source_roots:
            if source_root.root_path.is_dir() is False:
                continue
            try:
                match.file_path.relative_to(source_root.root_path)
                source_root_for_match = source_root
                break
            except ValueError:
                continue

        if source_root_for_match is None:
            errors.append(f"Could not determine source root for precise match: {match.file_path}")
            continue

        destination_name: str = _build_destination_name(
            source_root=source_root_for_match,
            source_path=match.file_path,
        )
        copied_path: Path = destination_dir / destination_name
        try:
            shutil.copy2(src=match.file_path, dst=copied_path)
        except OSError as exc:
            errors.append(
                f"Failed to copy session log '{match.file_path}' to '{copied_path}': {exc}"
            )
            continue

        copied_path = _compress_if_large(path=copied_path)
        copied_sessions.append(
            CapturedSession(
                source_kind=source_root_for_match.source_kind,
                source_path=str(match.file_path),
                copied_path=f"{SESSION_LOGS_RELATIVE_PREFIX}/{copied_path.name}",
                matched_by=match.match_kind,
            ),
        )

    # Then, content-based scan for each source root
    for source_root in resolved_source_roots:
        if source_root.root_path.is_dir() is False:
            checked_roots.append(
                SessionRootScan(
                    source_kind=source_root.source_kind,
                    root_path=str(source_root.root_path),
                    exists=False,
                    candidate_file_count=0,
                    matched_file_count=0,
                ),
            )
            continue

        candidate_files: list[Path] = []
        matched_files: list[Path] = []
        try:
            candidate_files = _iter_candidate_files(source_root=source_root)
        except OSError as exc:
            errors.append(f"Failed to enumerate session root '{source_root.root_path}': {exc}")

        for candidate_file in candidate_files:
            # Skip files already captured by precise matching
            if candidate_file.resolve() in precise_matched_paths:
                matched_files.append(candidate_file)
                continue

            try:
                if _file_mentions_task_id(file_path=candidate_file, task_id=task_id) is False:
                    continue
            except OSError as exc:
                errors.append(f"Failed to scan session log '{candidate_file}': {exc}")
                continue

            # Content mentions the task ID. Apply source-specific precision
            # filters to avoid capturing repo-root sessions that merely
            # discuss the task.
            #
            # Claude Code sessions live under per-cwd directories. The
            # preferred signal is the on-disk path containing a worktree
            # indicator. When that signal is absent — e.g. the orchestrator
            # session for ``/execute-task`` runs from the main repo cwd so
            # its file path has no worktree marker — we fall back to scanning
            # the JSONL body for a ``cwd`` field that references a worktree
            # directory for this task. Subagents launched into the worktree
            # record such ``cwd`` values in their tool call payloads and
            # message envelopes.
            #
            # Codex sessions live under a flat date-based directory and have
            # no path-level signal, so we always require JSONL-body ``cwd``
            # evidence for them.
            if source_root.source_kind == CLAUDE_CODE_SOURCE_KIND:
                has_path_evidence: bool = _path_has_worktree_evidence(
                    file_path=candidate_file,
                    task_id=task_id,
                )
                if (
                    has_path_evidence is False
                    and _jsonl_content_has_worktree_cwd(
                        file_path=candidate_file,
                        task_id=task_id,
                    )
                    is False
                ):
                    continue
            if (
                source_root.source_kind == CODEX_SOURCE_KIND
                and _jsonl_content_has_worktree_cwd(
                    file_path=candidate_file,
                    task_id=task_id,
                )
                is False
            ):
                continue

            matched_files.append(candidate_file)

            # Copy content-matched file (not already precise-matched)
            destination_name = _build_destination_name(
                source_root=source_root,
                source_path=candidate_file,
            )
            copied_path = destination_dir / destination_name
            try:
                shutil.copy2(src=candidate_file, dst=copied_path)
            except OSError as exc:
                errors.append(
                    f"Failed to copy session log '{candidate_file}' to '{copied_path}': {exc}"
                )
                continue

            copied_path = _compress_if_large(path=copied_path)
            copied_sessions.append(
                CapturedSession(
                    source_kind=source_root.source_kind,
                    source_path=str(candidate_file),
                    copied_path=f"{SESSION_LOGS_RELATIVE_PREFIX}/{copied_path.name}",
                    matched_by=MATCH_KIND_CONTENT,
                ),
            )

        checked_roots.append(
            SessionRootScan(
                source_kind=source_root.source_kind,
                root_path=str(source_root.root_path),
                exists=True,
                candidate_file_count=len(candidate_files),
                matched_file_count=len(matched_files),
            ),
        )

    report: SessionCaptureReport = SessionCaptureReport(
        spec_version=SPEC_VERSION,
        task_id=task_id,
        captured_at=datetime.now(tz=UTC).strftime(DATETIME_FORMAT),
        checked_roots=checked_roots,
        copied_sessions=copied_sessions,
        errors=errors,
    )
    report_path.write_text(
        json.dumps(asdict(report), indent=2) + "\n",
        encoding="utf-8",
    )
    return SessionCaptureOutcome(
        report_path=report_path,
        sessions_dir=destination_dir,
        report=report,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _print_discovery_result(*, result: SessionDiscoveryResult) -> None:
    sys.stdout.write(f"Target: {result.target_description}\n")
    sys.stdout.write(f"{result.resolution_note}\n")
    if len(result.checked_roots) > 0:
        sys.stdout.write("Scanned roots:\n")
        for root in result.checked_roots:
            exists_marker: str = "ok" if root.exists is True else "missing"
            sys.stdout.write(
                f"  - [{exists_marker}] {root.source_kind}: {root.root_path} "
                f"(candidates={root.candidate_file_count}, "
                f"matched={root.matched_file_count})\n",
            )
    if len(result.matched_files) == 0:
        sys.stdout.write("No transcript files matched.\n")
        return
    sys.stdout.write("Matched transcripts:\n")
    for path in result.matched_files:
        sys.stdout.write(f"  {path}\n")


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Capture or discover raw CLI session transcripts",
    )
    target_group = parser.add_mutually_exclusive_group(required=True)
    target_group.add_argument(
        "--task-id",
        help=(
            "Task ID (e.g. t0003_download_training_corpus). "
            "Captures matching transcripts into tasks/<task_id>/logs/sessions/."
        ),
    )
    target_group.add_argument(
        "--skill",
        help=(
            "Skill slug (e.g. human-brainstorm). Prints the path(s) of the "
            "most recent matching transcript(s); does not copy files."
        ),
    )
    target_group.add_argument(
        "--current",
        action="store_true",
        help=(
            "Resolve the currently running session via CODEX_THREAD_ID or "
            "newest Claude transcript mtime. Read-only; does not copy."
        ),
    )
    args: argparse.Namespace = parser.parse_args()

    if args.task_id is not None:
        try:
            outcome: SessionCaptureOutcome = capture_task_sessions(task_id=args.task_id)
        except OSError as exc:
            sys.stderr.write(f"Session capture failed: {exc}\n")
            sys.exit(1)
        copied_count: int = len(outcome.report.copied_sessions)
        sys.stdout.write(
            f"Captured {copied_count} session transcript(s) into {outcome.sessions_dir}.\n",
        )
        sys.stdout.write(f"Wrote capture report to {outcome.report_path}.\n")
        sys.exit(0)

    target: SessionDiscoveryTarget = (
        SkillSlugTarget(slug=args.skill) if args.skill is not None else CurrentSessionTarget()
    )

    try:
        result: SessionDiscoveryResult = discover_session_files(target=target)
    except OSError as exc:
        sys.stderr.write(f"Session discovery failed: {exc}\n")
        sys.exit(1)

    _print_discovery_result(result=result)
    sys.exit(0)


if __name__ == "__main__":
    main()
