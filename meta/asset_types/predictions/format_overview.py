"""Predictions overview formatting with by-date-added and by-category views."""

from pathlib import Path

from arf.scripts.overview.common import (
    BY_CATEGORY_VIEW,
    BY_DATE_ADDED_VIEW,
    EMPTY_MARKDOWN_VALUE,
    README_FILE_NAME,
    DateGroup,
    category_links,
    group_items_by_date,
    normalize_markdown,
    overview_legacy_markdown_path,
    overview_section_readme,
    overview_section_view_dir,
    overview_section_view_readme,
    remove_dir_if_exists,
    remove_file_if_exists,
    repo_file_link,
    task_link,
    write_file,
)
from meta.asset_types.predictions.aggregator import PredictionsInfoFull

SECTION_NAME: str = "predictions"
PREDICTIONS_README: Path = overview_section_readme(section_name=SECTION_NAME)
PREDICTIONS_BY_DATE_DIR: Path = overview_section_view_dir(
    section_name=SECTION_NAME,
    view_name=BY_DATE_ADDED_VIEW,
)
PREDICTIONS_BY_DATE_README: Path = overview_section_view_readme(
    section_name=SECTION_NAME,
    view_name=BY_DATE_ADDED_VIEW,
)
PREDICTIONS_BY_CATEGORY_DIR: Path = overview_section_view_dir(
    section_name=SECTION_NAME,
    view_name=BY_CATEGORY_VIEW,
)

_SECTION_REL: str = "../../"
_DATE_REL: str = "../../../"
_CATEGORY_REL: str = "../../../"


def _format_predictions_detail(*, predictions: PredictionsInfoFull, rel: str) -> str:
    model_str: str = (
        predictions.model_id if predictions.model_id is not None else EMPTY_MARKDOWN_VALUE
    )
    instance_str: str = (
        str(predictions.instance_count)
        if predictions.instance_count is not None
        else EMPTY_MARKDOWN_VALUE
    )
    datasets_str: str = ", ".join(f"`{dataset_id}`" for dataset_id in predictions.dataset_ids)

    lines: list[str] = [
        "<details>",
        f"<summary>\U0001f4ca <strong>{predictions.name}</strong>"
        f" (<code>{predictions.predictions_id}</code>) \u2014 {instance_str} instances"
        f" ({predictions.prediction_format})</summary>",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| **ID** | `{predictions.predictions_id}` |",
        f"| **Model ID** | {model_str} |",
        f"| **Model** | {predictions.model_description} |",
        f"| **Datasets** | {datasets_str} |",
        f"| **Format** | {predictions.prediction_format} |",
        f"| **Instances** | {instance_str} |",
        f"| **Date created** | {predictions.date_created} |",
        f"| **Categories** | {category_links(categories=predictions.categories, rel=rel)} |",
        f"| **Created by** | {task_link(task_id=predictions.created_by_task, rel=rel)} |",
        (
            "| **Documentation** | "
            f"{_format_description_link(description_path=predictions.description_path, rel=rel)} |"
        ),
        "",
    ]

    if predictions.metrics_at_creation is not None and len(predictions.metrics_at_creation) > 0:
        lines.append("**Metrics at creation:**")
        lines.append("")
        for metric_name, metric_value in predictions.metrics_at_creation.items():
            lines.append(f"* **{metric_name}**: {metric_value}")
        lines.append("")

    if predictions.full_description is not None and len(predictions.full_description.strip()) > 0:
        lines.append(predictions.full_description.strip())
        lines.append("")
    elif len(predictions.short_description) > 0:
        lines.append(predictions.short_description)
        lines.append("")

    lines.append("</details>")
    return "\n".join(lines)


def _format_description_link(*, description_path: str | None, rel: str) -> str:
    if description_path is None:
        return EMPTY_MARKDOWN_VALUE
    return repo_file_link(
        label="description.md",
        repo_relative_path=description_path,
        rel=rel,
    )


def _format_predictions_page(
    *,
    title: str,
    predictions_list: list[PredictionsInfoFull],
    rel: str,
    show_date_index: bool,
    show_category_index: bool,
    back_link: str | None,
) -> str:
    if len(predictions_list) == 0:
        return f"# {title}\n\nNo predictions found."

    lines: list[str] = [f"# {title}", "", f"{len(predictions_list)} predictions asset(s)."]

    if back_link is not None:
        lines.append("")
        lines.append(f"[Back to all predictions]({back_link})")

    browse_parts: list[str] = []
    if show_category_index:
        all_categories: set[str] = set()
        for p in predictions_list:
            all_categories.update(p.categories)
        if len(all_categories) > 0:
            category_links_md: list[str] = [
                f"[`{c}`]({BY_CATEGORY_VIEW}/{c}.md)" for c in sorted(all_categories)
            ]
            browse_parts.append(f"By category: {', '.join(category_links_md)}")
    if show_date_index:
        browse_parts.append(f"[By date added]({BY_DATE_ADDED_VIEW}/{README_FILE_NAME})")
    if len(browse_parts) > 0:
        lines.append("")
        lines.append(f"**Browse by view**: {'; '.join(browse_parts)}")

    lines.append("")
    lines.append("---")
    lines.append("")

    for predictions in sorted(
        predictions_list,
        key=lambda item: (item.name.lower(), item.predictions_id),
    ):
        lines.append(_format_predictions_detail(predictions=predictions, rel=rel))
        lines.append("")

    return "\n".join(lines)


def _format_predictions_by_date_page(*, predictions_list: list[PredictionsInfoFull]) -> str:
    if len(predictions_list) == 0:
        return "# Predictions by Date Added\n\nNo predictions found."

    date_groups: list[DateGroup[PredictionsInfoFull]] = group_items_by_date(
        items=predictions_list,
        get_date=lambda item: item.date_created,
        sort_key=lambda item: (item.name.lower(), item.predictions_id),
    )

    lines: list[str] = [
        "# Predictions by Date Added",
        "",
        f"{len(predictions_list)} predictions asset(s) grouped by creation date.",
        "",
        "[Back to all predictions](../README.md)",
        "",
        "---",
    ]

    for date_group in date_groups:
        lines.append("")
        lines.append(f"## {date_group.date} ({len(date_group.items)})")
        lines.append("")
        for predictions in date_group.items:
            lines.append(_format_predictions_detail(predictions=predictions, rel=_DATE_REL))
            lines.append("")

    return "\n".join(lines)


def materialize_predictions(*, predictions: list[PredictionsInfoFull]) -> None:
    remove_dir_if_exists(dir_path=PREDICTIONS_BY_DATE_DIR)
    remove_dir_if_exists(dir_path=PREDICTIONS_BY_CATEGORY_DIR)

    write_file(
        file_path=PREDICTIONS_README,
        content=normalize_markdown(
            content=_format_predictions_page(
                title=f"Predictions ({len(predictions)})",
                predictions_list=predictions,
                rel=_SECTION_REL,
                show_date_index=True,
                show_category_index=True,
                back_link=None,
            ),
        ),
    )
    write_file(
        file_path=PREDICTIONS_BY_DATE_README,
        content=normalize_markdown(
            content=_format_predictions_by_date_page(predictions_list=predictions),
        ),
    )

    categories: dict[str, list[PredictionsInfoFull]] = {}
    for p in predictions:
        for cat in p.categories:
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(p)

    for cat, cat_predictions in sorted(categories.items()):
        write_file(
            file_path=PREDICTIONS_BY_CATEGORY_DIR / f"{cat}.md",
            content=normalize_markdown(
                content=_format_predictions_page(
                    title=f"Predictions: `{cat}`",
                    predictions_list=cat_predictions,
                    rel=_CATEGORY_REL,
                    show_date_index=False,
                    show_category_index=False,
                    back_link="../README.md",
                ),
            ),
        )

    remove_file_if_exists(
        file_path=overview_legacy_markdown_path(section_name=SECTION_NAME),
    )
