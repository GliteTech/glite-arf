"""Shared constants and helpers for overview materialization."""

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from re import Match, Pattern
from re import compile as compile_regex
from re import match as match_regex
from shutil import rmtree
from textwrap import fill, wrap
from typing import Any

from arf.scripts.overview import paths as overview_paths
from arf.scripts.overview.paths import TaskID
from arf.scripts.verificators.common.paths import REPO_ROOT

MARKDOWN_WIDTH: int = 94
OVERVIEW_DIR: Path = overview_paths.OVERVIEW_DIR
README_FILE_NAME: str = overview_paths.README_FILE_NAME
MARKDOWN_FILE_SUFFIX: str = overview_paths.MARKDOWN_FILE_SUFFIX
RESULTS_DETAILED_FILE_NAME: str = overview_paths.RESULTS_DETAILED_FILE_NAME
BY_CATEGORY_VIEW: str = "by-category"
BY_DATE_ADDED_VIEW: str = "by-date-added"
BY_STATUS_VIEW: str = "by-status"
UNKNOWN_DATE: str = "unknown"

TASKS_SEGMENT: str = "tasks"
ASSETS_ANSWER_SEGMENT: str = "assets/answer"
ASSETS_PAPER_SEGMENT: str = "assets/paper"
META_CATEGORIES_SEGMENT: str = "meta/categories"
RESULTS_SEGMENT: str = "results"
EMPTY_MARKDOWN_VALUE: str = "\u2014"
CODE_FENCE: str = "```"
HEADING_PREFIX: str = "#"
TOP_LEVEL_H1_PREFIX: str = "# "
SECOND_LEVEL_H1_PREFIX: str = "## "
HTML_OPEN: str = "<"
HTML_CLOSE: str = ">"
TABLE_PREFIX: str = "|"
BLOCKQUOTE_PREFIX: str = ">"
SUMMARY_OPEN: str = "<summary>"
SUMMARY_CLOSE: str = "</summary>"
SPACE: str = " "
FULL_ANSWER_FILE_NAME: str = "full_answer.md"
SUMMARY_FILE_NAME: str = "summary.md"

SUGGESTION_PRIORITY_HIGH: str = "high"
SUGGESTION_PRIORITY_MEDIUM: str = "medium"
SUGGESTION_PRIORITY_LOW: str = "low"

KIND_EMOJI: dict[str, str] = {
    "experiment": "\U0001f9ea",
    "dataset": "\U0001f4c2",
    "library": "\U0001f4da",
    "technique": "\U0001f527",
    "evaluation": "\U0001f4ca",
}

type AnswerID = str
type PaperID = str
type RepoRelativePath = str
type RelativePrefix = str


@dataclass(frozen=True, slots=True)
class DateGroup[T_Item]:
    date: str
    items: list[T_Item]


overview_section_dir = overview_paths.overview_section_dir
overview_section_readme = overview_paths.overview_section_readme
overview_legacy_markdown_path = overview_paths.overview_legacy_markdown_path
overview_section_view_dir = overview_paths.overview_section_view_dir
overview_section_view_readme = overview_paths.overview_section_view_readme
overview_repo_task_path = overview_paths.overview_repo_task_path
results_detailed_path = overview_paths.results_detailed_path


def normalize_date_value(*, value: str | None) -> str:
    if value is None:
        return UNKNOWN_DATE
    stripped: str = value.strip()
    if len(stripped) < 10:
        return UNKNOWN_DATE
    return stripped[:10]


def group_items_by_date[T_Item](
    *,
    items: list[T_Item],
    get_date: Callable[[T_Item], str | None],
    sort_key: Callable[[T_Item], Any],
) -> list[DateGroup[T_Item]]:
    grouped: dict[str, list[T_Item]] = {}
    for item in items:
        date_key: str = normalize_date_value(value=get_date(item))
        if date_key not in grouped:
            grouped[date_key] = []
        grouped[date_key].append(item)

    ordered_dates: list[str] = sorted(
        [date for date in grouped if date != UNKNOWN_DATE],
        reverse=True,
    )
    if UNKNOWN_DATE in grouped:
        ordered_dates.append(UNKNOWN_DATE)

    result: list[DateGroup[T_Item]] = []
    for date_key in ordered_dates:
        result.append(
            DateGroup(
                date=date_key,
                items=sorted(grouped[date_key], key=sort_key),
            ),
        )
    return result


def remove_dir_if_exists(*, dir_path: Path) -> None:
    if dir_path.exists():
        rmtree(dir_path)
        print(f"  Removed {_display_path(path=dir_path)}")


def remove_file_if_exists(*, file_path: Path) -> None:
    if file_path.exists():
        file_path.unlink()
        print(f"  Removed {_display_path(path=file_path)}")


def _display_path(*, path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


# ---------------------------------------------------------------------------
# Link helpers
# ---------------------------------------------------------------------------


OVERVIEW_TASK_PAGES_PATH: str = "overview/tasks/task_pages"


def task_link(*, task_id: TaskID, rel: RelativePrefix) -> str:
    return f"[`{task_id}`]({rel}{OVERVIEW_TASK_PAGES_PATH}/{task_id}.md)"


def task_name_link(*, task_id: TaskID, name: str, rel: RelativePrefix) -> str:
    return f"[{name}]({rel}{OVERVIEW_TASK_PAGES_PATH}/{task_id}.md)"


def task_index_link(*, task_id: TaskID, task_index: int, rel: RelativePrefix) -> str:
    return f"[{task_index}]({rel}{OVERVIEW_TASK_PAGES_PATH}/{task_id}.md)"


def asset_name_link(
    *,
    name: str,
    description_path: str | None,
    rel: RelativePrefix,
) -> str:
    if description_path is None:
        return name
    return f"[{name}]({rel}{description_path})"


def answer_asset_link(
    *,
    answer_id: AnswerID,
    task_id: TaskID,
    rel: RelativePrefix,
) -> str:
    return f"[`{answer_id}`]({rel}{TASKS_SEGMENT}/{task_id}/{ASSETS_ANSWER_SEGMENT}/{answer_id}/)"


def paper_asset_link(
    *,
    paper_id: PaperID,
    task_id: TaskID,
    rel: RelativePrefix,
) -> str:
    return f"[`{paper_id}`]({rel}{TASKS_SEGMENT}/{task_id}/{ASSETS_PAPER_SEGMENT}/{paper_id}/)"


def category_links(*, categories: list[str], rel: str) -> str:
    if len(categories) == 0:
        return EMPTY_MARKDOWN_VALUE
    parts: list[str] = [f"[`{cat}`]({rel}{META_CATEGORIES_SEGMENT}/{cat}/)" for cat in categories]
    return ", ".join(parts)


def repo_file_link(
    *,
    label: str,
    repo_relative_path: RepoRelativePath,
    rel: RelativePrefix,
) -> str:
    return f"[`{label}`]({rel}{repo_relative_path})"


# ---------------------------------------------------------------------------
# Markdown formatting
# ---------------------------------------------------------------------------


_LIST_RE: Pattern[str] = compile_regex(r"^(\s*)([*-] |\d+\. )(.*)$")


def _is_fence(*, line: str) -> bool:
    return line.lstrip().startswith(CODE_FENCE)


def _is_heading(*, line: str) -> bool:
    return line.startswith(HEADING_PREFIX)


def _is_html_tag(*, line: str) -> bool:
    stripped: str = line.strip()
    return stripped.startswith(HTML_OPEN) and stripped.endswith(HTML_CLOSE)


def _is_table_row(*, line: str) -> bool:
    return line.lstrip().startswith(TABLE_PREFIX)


def _is_blockquote(*, line: str) -> bool:
    return line.lstrip().startswith(BLOCKQUOTE_PREFIX)


def _is_list_item(*, line: str) -> bool:
    return _LIST_RE.match(line) is not None


def _is_structural(*, line: str) -> bool:
    return (
        len(line.strip()) == 0
        or _is_heading(line=line)
        or _is_html_tag(line=line)
        or _is_table_row(line=line)
        or _is_blockquote(line=line)
        or _is_list_item(line=line)
        or _is_fence(line=line)
    )


def _wrap_text(
    *,
    text: str,
    initial_indent: str,
    subsequent_indent: str,
) -> list[str]:
    return fill(
        text=text,
        width=MARKDOWN_WIDTH,
        initial_indent=initial_indent,
        subsequent_indent=subsequent_indent,
        break_long_words=False,
        break_on_hyphens=False,
    ).splitlines()


def _wrap_summary_line(*, line: str) -> list[str]:
    stripped: str = line.strip()
    prefix: str = SUMMARY_OPEN
    suffix: str = SUMMARY_CLOSE
    if not stripped.startswith(prefix) or not stripped.endswith(suffix):
        return [line]

    inner: str = stripped[len(prefix) : -len(suffix)].strip()
    if len(line) <= MARKDOWN_WIDTH:
        return [line]

    if len(inner) == 0:
        return [line]

    inner_width: int = MARKDOWN_WIDTH - len(prefix) - len(suffix)
    wrapped_inner: list[str] = wrap(
        text=inner,
        width=inner_width,
        break_long_words=False,
        break_on_hyphens=False,
    )
    if len(wrapped_inner) == 0:
        return [line]

    while len(wrapped_inner) > 1 and len(wrapped_inner[-1]) < 50:
        previous_words: list[str] = wrapped_inner[-2].split()
        if len(previous_words) <= 1:
            break
        moved_word: str = previous_words.pop()
        candidate_last: str = f"{moved_word}{SPACE}{wrapped_inner[-1]}".strip()
        if len(candidate_last) > inner_width or len(" ".join(previous_words)) < 70:
            break
        wrapped_inner[-2] = " ".join(previous_words)
        wrapped_inner[-1] = candidate_last

    lines: list[str] = [f"{prefix}{wrapped_inner[0]}"]
    for middle in wrapped_inner[1:-1]:
        lines.append(middle)
    lines[-1] = f"{lines[-1]}{suffix}" if len(wrapped_inner) == 1 else lines[-1]
    if len(wrapped_inner) > 1:
        lines.append(f"{wrapped_inner[-1]}{suffix}")
    return lines


def normalize_markdown(
    *,
    content: str,
    demote_headings_after_first_h1: bool = False,
) -> str:
    lines: list[str] = content.splitlines()
    out: list[str] = []
    in_code: bool = False
    seen_top_h1: bool = False
    i: int = 0

    while i < len(lines):
        line: str = lines[i]
        if demote_headings_after_first_h1 and line.startswith(HEADING_PREFIX):
            if line.startswith(TOP_LEVEL_H1_PREFIX):
                if seen_top_h1:
                    line = f"{SECOND_LEVEL_H1_PREFIX}{line[2:]}"
                else:
                    seen_top_h1 = True
            elif seen_top_h1 and match_regex(pattern=r"^#{2,6} ", string=line) is not None:
                hashes, title = line.split(sep=SPACE, maxsplit=1)
                line = f"{hashes}#{SPACE}{title}"
        if _is_fence(line=line):
            in_code = not in_code
            out.append(line)
            i += 1
            continue

        if in_code:
            out.append(line)
            i += 1
            continue

        if line.strip().startswith(SUMMARY_OPEN) and line.strip().endswith(SUMMARY_CLOSE):
            out.extend(_wrap_summary_line(line=line))
            i += 1
            continue

        if (
            len(line.strip()) == 0
            or _is_heading(line=line)
            or _is_html_tag(line=line)
            or _is_table_row(line=line)
            or _is_blockquote(line=line)
        ):
            if len(line.strip()) == 0 and len(out) > 0 and len(out[-1].strip()) == 0:
                i += 1
                continue
            out.append(line)
            i += 1
            continue

        list_match: Match[str] | None = _LIST_RE.match(line)
        if list_match is not None:
            indent, marker, rest = list_match.groups()
            parts: list[str] = [rest.strip()] if len(rest.strip()) > 0 else []
            i += 1
            while i < len(lines):
                next_line: str = lines[i]
                if _is_structural(line=next_line):
                    break
                parts.append(next_line.strip())
                i += 1
            text: str = " ".join(part for part in parts if len(part) > 0)
            if len(text) == 0:
                out.append(f"{indent}{marker}".rstrip())
                continue
            out.extend(
                _wrap_text(
                    text=text,
                    initial_indent=f"{indent}{marker}",
                    subsequent_indent=" " * (len(indent) + len(marker)),
                ),
            )
            continue

        paragraph_indent: str = line[: len(line) - len(line.lstrip(SPACE))]
        paragraph_parts: list[str] = [line.strip()]
        i += 1
        while i < len(lines):
            paragraph_line: str = lines[i]
            if _is_structural(line=paragraph_line):
                break
            paragraph_parts.append(paragraph_line.strip())
            i += 1
        out.extend(
            _wrap_text(
                text=" ".join(paragraph_parts),
                initial_indent=paragraph_indent,
                subsequent_indent=paragraph_indent,
            ),
        )

    while len(out) > 0 and len(out[-1].strip()) == 0:
        out.pop()

    return "\n".join(out)


# ---------------------------------------------------------------------------
# File writing
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Embedded content path rewriting
# ---------------------------------------------------------------------------

# Matches ](some_relative_path) in markdown links/images — but NOT ](http or ](#
_MD_LINK_TARGET: Pattern[str] = compile_regex(
    r"(\]\()(?!https?://|#|/)((?:\.\.?/)?[^\)]+)",
)


def rewrite_embedded_paths(
    *,
    content: str,
    source_dir: str,
    target_rel: str,
) -> str:
    """Rewrite relative paths in embedded markdown content.

    When a file from ``source_dir`` (repo-relative, e.g. ``tasks/t0061/results``)
    is embedded in an overview page that uses ``target_rel`` (e.g. ``../../../``)
    to reach the repo root, this function rewrites relative paths so they resolve
    correctly from the overview page location.

    For example, ``images/chart.png`` in a file at ``tasks/t0061/results/`` becomes
    ``../../../tasks/t0061/results/images/chart.png`` when ``target_rel`` is
    ``../../../``.
    """

    def _replacer(m: Match[str]) -> str:
        prefix: str = m.group(1)  # ](
        path: str = m.group(2)
        if path.startswith("../") or path.startswith("./"):
            # Already relative — resolve against source_dir
            resolved: str = str(
                (Path(source_dir) / path).as_posix(),
            )
            # Normalize ../ components
            parts: list[str] = []
            for part in resolved.split("/"):
                if part == "..":
                    if len(parts) > 0:
                        parts.pop()
                elif part != ".":
                    parts.append(part)
            return f"{prefix}{target_rel}{'/'.join(parts)}"
        if "/" in path or path.endswith((".png", ".jpg", ".md", ".json", ".pdf")):
            # Looks like a relative file path from source_dir
            return f"{prefix}{target_rel}{source_dir}/{path}"
        return m.group(0)

    return _MD_LINK_TARGET.sub(_replacer, content)


# ---------------------------------------------------------------------------
# File writing
# ---------------------------------------------------------------------------


def write_file(*, file_path: Path, content: str) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    normalized: str = content.rstrip("\n") + "\n"
    file_path.write_text(
        data=normalized,
        encoding="utf-8",
    )
    print(f"  Wrote {_display_path(path=file_path)}")
