from datetime import date as date_type
from datetime import datetime
from pathlib import Path

from arf.scripts.verificators.common import paths
from arf.tests.fixtures.writers import write_json, write_text

SPEC_VERSION_NEWS: str = "2"
DEFAULT_DATE: str = "2026-04-05"
DEFAULT_HUMAN_DATE: str = "April 5, 2026"
DEFAULT_TASK_ID: str = "t0065_multi_sentence_context_bem"
DEFAULT_TASK_NAME: str = "Multi-sentence context for BEM"
DEFAULT_KEY_FINDING: str = "Adding one surrounding sentence gives +0.4 F1"
DEFAULT_REASON: str = "Inference-only context limited by train-test mismatch"


def iso_to_human_date(*, iso_date: str) -> str:
    parsed: date_type = datetime.strptime(iso_date, "%Y-%m-%d").date()
    day: int = parsed.day
    return parsed.strftime(f"%B {day}, %Y")


def build_task_completed(
    *,
    task_id: str = DEFAULT_TASK_ID,
    name: str = DEFAULT_TASK_NAME,
    cost_usd: float = 0.22,
    key_finding: str = DEFAULT_KEY_FINDING,
    overrides: dict[str, object] | None = None,
) -> dict[str, object]:
    data: dict[str, object] = {
        "task_id": task_id,
        "name": name,
        "cost_usd": cost_usd,
        "key_finding": key_finding,
    }
    if overrides is not None:
        data.update(overrides)
    return data


def build_task_created(
    *,
    task_id: str = "t0082_retrain_bem_preceding_context",
    name: str = "Retrain BEM with preceding-sentence context",
    reason: str = DEFAULT_REASON,
    overrides: dict[str, object] | None = None,
) -> dict[str, object]:
    data: dict[str, object] = {
        "task_id": task_id,
        "name": name,
        "reason": reason,
    }
    if overrides is not None:
        data.update(overrides)
    return data


def build_task_cancelled(
    *,
    task_id: str = "t0067_multi_sentence_context_consec",
    reason: str = "Superseded by retrain-from-scratch task t0084",
    overrides: dict[str, object] | None = None,
) -> dict[str, object]:
    data: dict[str, object] = {
        "task_id": task_id,
        "reason": reason,
    }
    if overrides is not None:
        data.update(overrides)
    return data


def build_best_result(
    *,
    system: str = "SANDWiCH",
    f1: float = 87.4,
    result_type: str = "fine-tuned",
    overrides: dict[str, object] | None = None,
) -> dict[str, object]:
    data: dict[str, object] = {
        "system": system,
        "f1": f1,
        "type": result_type,
    }
    if overrides is not None:
        data.update(overrides)
    return data


def build_news_json_data(
    *,
    date: str = DEFAULT_DATE,
    spec_version: str = SPEC_VERSION_NEWS,
    tasks_completed: list[dict[str, object]] | None = None,
    tasks_created: list[dict[str, object]] | None = None,
    tasks_cancelled: list[dict[str, object]] | None = None,
    total_cost_usd: float = 153.66,
    assets_added: int = 9,
    papers_added: int = 7,
    infrastructure_changes: list[str] | None = None,
    current_best_results: list[dict[str, object]] | None = None,
    key_findings: list[str] | None = None,
    overrides: dict[str, object] | None = None,
) -> dict[str, object]:
    data: dict[str, object] = {
        "spec_version": spec_version,
        "date": date,
        "tasks_completed": (
            tasks_completed if tasks_completed is not None else [build_task_completed()]
        ),
        "tasks_created": (tasks_created if tasks_created is not None else [build_task_created()]),
        "tasks_cancelled": (tasks_cancelled if tasks_cancelled is not None else []),
        "total_cost_usd": total_cost_usd,
        "assets_added": assets_added,
        "papers_added": papers_added,
        "infrastructure_changes": (
            infrastructure_changes
            if infrastructure_changes is not None
            else ["Added verificator test coverage"]
        ),
        "current_best_results": (
            current_best_results if current_best_results is not None else [build_best_result()]
        ),
        "key_findings": (
            key_findings
            if key_findings is not None
            else ["Prompt design doesn't matter; reasoning effort does"]
        ),
    }
    if overrides is not None:
        data.update(overrides)
    return data


def build_news_md_content(
    *,
    date: str = DEFAULT_DATE,
    include_findings: bool = True,
    include_where_we_stand: bool = True,
    include_costs: bool = True,
    include_papers: bool = True,
    include_answers: bool = True,
    include_images: bool = True,
    include_links: bool = True,
    start_with_h1: bool = False,
    wrong_date_heading: str | None = None,
) -> str:
    human_date: str = (
        wrong_date_heading if wrong_date_heading is not None else iso_to_human_date(iso_date=date)
    )
    lines: list[str] = []
    if start_with_h1:
        lines.append(f"# {human_date}")
    else:
        lines.append(f"## {human_date}")
    lines.append("")
    lines.append("**7 tasks completed. ~$154 spent.**")
    lines.append("")
    if include_findings:
        lines.append("## Three things we learned")
        lines.append("")
        lines.append("### 1. Prompt design doesn't matter. Reasoning effort does.")
        lines.append("")
        if include_links:
            lines.append("Under [controlled conditions](../overview/tasks/task_pages/t0061.md):")
        else:
            lines.append("Under controlled conditions:")
        lines.append("")
        lines.append("* Best variant: **83.4 F1**")
        lines.append("")
        if include_images:
            lines.append("![Cost vs Quality](../tasks/t0061/results/images/cost_vs_f1.png)")
            lines.append("")
    if include_where_we_stand:
        lines.append("## Where we stand")
        lines.append("")
        if include_links:
            lines.append("| System | [F1](../overview/metrics-results/f1_all.md) |")
        else:
            lines.append("| System | F1 |")
        lines.append("|--------|-----|")
        if include_links:
            lines.append(
                "| [SANDWiCH](../overview/models/README.md)"
                " | [**87.4**](../overview/metrics-results/f1_all.md) |"
            )
        else:
            lines.append("| SANDWiCH | 87.4 |")
        lines.append("")
        lines.append("Gap to SOTA: **4 F1 points**. Next bet: retrain-with-context.")
        lines.append("")
    if include_costs:
        lines.append("## Costs")
        lines.append("")
        lines.append("| What | Cost |")
        lines.append("|------|------|")
        if include_links:
            lines.append("| [OpenAI](../overview/tasks/task_pages/t0061.md) | $125 |")
        else:
            lines.append("| OpenAI | $125 |")
        lines.append("| **Day total** | **~$154** |")
        lines.append("")
    if include_papers:
        lines.append("## Key papers added")
        lines.append("")
        if include_links:
            lines.append(
                "**[Paper Title](../tasks/t0024/assets/paper/doi/summary.md)**"
                " (Author, 2021). Why it matters."
            )
        else:
            lines.append("**Paper Title** (Author, 2021). Why it matters.")
        lines.append("")
    if include_answers:
        lines.append("## Key questions answered")
        lines.append("")
        if include_links:
            lines.append(
                "**[What is the ceiling?](../tasks/t0063/assets/answer/id/full_answer.md)**"
                " Summary answer."
            )
        else:
            lines.append("**What is the ceiling?** Summary answer.")
        lines.append("")
    return "\n".join(lines)


def build_news_files(
    *,
    repo_root: Path,
    date: str = DEFAULT_DATE,
    json_data: dict[str, object] | None = None,
    md_content: str | None = None,
) -> None:
    json_path: Path = paths.news_json_path(date=date)
    md_path: Path = paths.news_md_path(date=date)
    write_json(
        path=json_path,
        data=json_data if json_data is not None else build_news_json_data(date=date),
    )
    write_text(
        path=md_path,
        content=(md_content if md_content is not None else build_news_md_content(date=date)),
    )
