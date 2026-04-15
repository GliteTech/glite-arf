"""Model overview formatting with by-date-added and by-category views."""

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
from meta.asset_types.model.aggregator import ModelInfoFull

SECTION_NAME: str = "models"
MODELS_README: Path = overview_section_readme(section_name=SECTION_NAME)
MODELS_BY_DATE_DIR: Path = overview_section_view_dir(
    section_name=SECTION_NAME,
    view_name=BY_DATE_ADDED_VIEW,
)
MODELS_BY_DATE_README: Path = overview_section_view_readme(
    section_name=SECTION_NAME,
    view_name=BY_DATE_ADDED_VIEW,
)
MODELS_BY_CATEGORY_DIR: Path = overview_section_view_dir(
    section_name=SECTION_NAME,
    view_name=BY_CATEGORY_VIEW,
)

_SECTION_REL: str = "../../"
_DATE_REL: str = "../../../"
_CATEGORY_REL: str = "../../../"


def _format_model_detail(*, model: ModelInfoFull, rel: str) -> str:
    base_model_str: str = model.base_model if model.base_model is not None else EMPTY_MARKDOWN_VALUE
    datasets_str: str = ", ".join(f"`{dataset_id}`" for dataset_id in model.training_dataset_ids)
    if len(model.training_dataset_ids) == 0:
        datasets_str = EMPTY_MARKDOWN_VALUE

    lines: list[str] = [
        "<details>",
        f"<summary>\U0001f9e0 <strong>{model.name}</strong> (<code>{model.model_id}</code>)"
        f" \u2014 {model.framework} / {base_model_str}</summary>",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| **ID** | `{model.model_id}` |",
        f"| **Version** | {model.version} |",
        f"| **Framework** | {model.framework} |",
        f"| **Base model** | {base_model_str} |",
        f"| **Architecture** | {model.architecture} |",
        f"| **Date created** | {model.date_created} |",
        f"| **Training task** | {task_link(task_id=model.training_task_id, rel=rel)} |",
        f"| **Training datasets** | {datasets_str} |",
        f"| **Categories** | {category_links(categories=model.categories, rel=rel)} |",
        f"| **Created by** | {task_link(task_id=model.created_by_task, rel=rel)} |",
        (
            "| **Documentation** | "
            f"{_format_description_link(description_path=model.description_path, rel=rel)} |"
        ),
        "",
    ]

    if model.full_description is not None and len(model.full_description.strip()) > 0:
        lines.append(model.full_description.strip())
        lines.append("")
    elif len(model.short_description) > 0:
        lines.append(model.short_description)
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


def _format_models_page(
    *,
    title: str,
    models: list[ModelInfoFull],
    rel: str,
    show_date_index: bool,
    show_category_index: bool,
    back_link: str | None,
) -> str:
    if len(models) == 0:
        return f"# {title}\n\nNo models found."

    lines: list[str] = [f"# {title}", "", f"{len(models)} model(s)."]

    if back_link is not None:
        lines.append("")
        lines.append(f"[Back to all models]({back_link})")

    browse_parts: list[str] = []
    if show_category_index:
        all_categories: set[str] = set()
        for m in models:
            all_categories.update(m.categories)
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

    for model in sorted(models, key=lambda item: (item.name.lower(), item.model_id)):
        lines.append(_format_model_detail(model=model, rel=rel))
        lines.append("")

    return "\n".join(lines)


def _format_models_by_date_page(*, models: list[ModelInfoFull]) -> str:
    if len(models) == 0:
        return "# Models by Date Added\n\nNo models found."

    date_groups: list[DateGroup[ModelInfoFull]] = group_items_by_date(
        items=models,
        get_date=lambda item: item.date_created,
        sort_key=lambda item: (item.name.lower(), item.model_id),
    )

    lines: list[str] = [
        "# Models by Date Added",
        "",
        f"{len(models)} model(s) grouped by creation date.",
        "",
        "[Back to all models](../README.md)",
        "",
        "---",
    ]

    for date_group in date_groups:
        lines.append("")
        lines.append(f"## {date_group.date} ({len(date_group.items)})")
        lines.append("")
        for model in date_group.items:
            lines.append(_format_model_detail(model=model, rel=_DATE_REL))
            lines.append("")

    return "\n".join(lines)


def materialize_models(*, models: list[ModelInfoFull]) -> None:
    remove_dir_if_exists(dir_path=MODELS_BY_DATE_DIR)
    remove_dir_if_exists(dir_path=MODELS_BY_CATEGORY_DIR)

    write_file(
        file_path=MODELS_README,
        content=normalize_markdown(
            content=_format_models_page(
                title=f"Models ({len(models)})",
                models=models,
                rel=_SECTION_REL,
                show_date_index=True,
                show_category_index=True,
                back_link=None,
            ),
        ),
    )
    write_file(
        file_path=MODELS_BY_DATE_README,
        content=normalize_markdown(
            content=_format_models_by_date_page(models=models),
        ),
    )

    categories: dict[str, list[ModelInfoFull]] = {}
    for m in models:
        for cat in m.categories:
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(m)

    for cat, cat_models in sorted(categories.items()):
        write_file(
            file_path=MODELS_BY_CATEGORY_DIR / f"{cat}.md",
            content=normalize_markdown(
                content=_format_models_page(
                    title=f"Models: `{cat}`",
                    models=cat_models,
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
