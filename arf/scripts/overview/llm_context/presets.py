"""Preset definitions for overview LLM context archives."""

from arf.scripts.overview.llm_context.models import (
    PresetContentDetail,
    PresetDefinition,
    PresetOptions,
)


def _detail(*, content_type: str, coverage: str) -> PresetContentDetail:
    return PresetContentDetail(
        content_type=content_type,
        coverage=coverage,
    )


def build_presets() -> list[PresetDefinition]:
    return [
        PresetDefinition(
            preset_id="project-overview",
            title="Project Overview",
            file_name="project-overview.xml",
            description=("Compact starter context for general project chats."),
            use_case=(
                "General orientation, quick status questions, and lightweight strategy chats."
            ),
            included_content=[
                "project description",
                "completed task summaries",
                "planned tasks",
                "question and short-answer coverage",
            ],
            short_name="overview",
            featured_rank=1,
            content_details=[
                _detail(
                    content_type="Project description",
                    coverage="Full `project/description.md`.",
                ),
                _detail(
                    content_type="Completed tasks",
                    coverage="All completed tasks with `results_summary` excerpts and short"
                    " descriptions.",
                ),
                _detail(
                    content_type="Planned tasks",
                    coverage="All planned or active tasks with status, date, dependencies, and"
                    " short descriptions.",
                ),
                _detail(
                    content_type="Questions and answers",
                    coverage="All questions with short-answer coverage only.",
                ),
            ],
            options=PresetOptions(
                include_completed_task_details=False,
                include_planned_task_long_descriptions=False,
                include_research_documents=False,
                include_suggestions=False,
                suggestion_limit=None,
                include_papers=False,
                paper_limit=None,
                include_datasets=False,
                include_libraries=False,
                include_metrics=False,
                include_full_answers=False,
            ),
        ),
        PresetDefinition(
            preset_id="full",
            title="Full Project Context",
            file_name="full.xml",
            description=(
                "Largest preset with detailed completed-task reports and the full project knowledge"
                " base."
            ),
            use_case=("Deep project review, comprehensive planning, and long-context synthesis."),
            included_content=[
                "project description",
                "completed task summaries",
                "planned tasks with long descriptions",
                "full answer coverage",
                "paper summaries",
                "datasets",
                "libraries",
                "metrics",
                "results_detailed.md for each completed task",
            ],
            short_name="full",
            featured_rank=2,
            content_details=[
                _detail(
                    content_type="Project description",
                    coverage="Full `project/description.md`.",
                ),
                _detail(
                    content_type="Completed tasks",
                    coverage="All completed tasks with `results_summary` excerpts and short"
                    " descriptions.",
                ),
                _detail(
                    content_type="Detailed results",
                    coverage="Every available completed-task `results/results_detailed.md` file in"
                    " full.",
                ),
                _detail(
                    content_type="Planned tasks",
                    coverage="All planned or active tasks with status, date, dependencies, short"
                    " descriptions, and full long descriptions.",
                ),
                _detail(
                    content_type="Questions and answers",
                    coverage="All questions with full-answer bodies when available.",
                ),
                _detail(
                    content_type="Papers",
                    coverage="All papers with metadata and summary excerpts from paper summaries,"
                    " full summaries, or abstracts.",
                ),
                _detail(
                    content_type="Datasets",
                    coverage="All datasets with access, size, source task, and description"
                    " excerpts.",
                ),
                _detail(
                    content_type="Libraries",
                    coverage="All libraries with module paths, source task, and description"
                    " excerpts.",
                ),
                _detail(
                    content_type="Metrics",
                    coverage="All registered metrics with units, value types, and description"
                    " excerpts.",
                ),
            ],
            options=PresetOptions(
                include_completed_task_details=True,
                include_planned_task_long_descriptions=True,
                include_research_documents=False,
                include_suggestions=False,
                suggestion_limit=None,
                include_papers=True,
                paper_limit=None,
                include_datasets=True,
                include_libraries=True,
                include_metrics=True,
                include_full_answers=True,
            ),
        ),
        PresetDefinition(
            preset_id="research-history",
            title="Research History",
            file_name="research-history.xml",
            description=(
                "Research-stage documents across completed tasks, plus core project context."
            ),
            use_case=(
                "Literature review continuity, methodology discussion, and prior-investigation"
                " lookup."
            ),
            included_content=[
                "project description",
                "completed task summaries",
                "planned tasks",
                "question and short-answer coverage",
                "all task research documents",
            ],
            short_name="research",
            content_details=[
                _detail(
                    content_type="Project description",
                    coverage="Full `project/description.md`.",
                ),
                _detail(
                    content_type="Completed tasks",
                    coverage="All completed tasks with `results_summary` excerpts and short"
                    " descriptions.",
                ),
                _detail(
                    content_type="Planned tasks",
                    coverage="All planned or active tasks with status, date, dependencies, and"
                    " short descriptions.",
                ),
                _detail(
                    content_type="Questions and answers",
                    coverage="All questions with short-answer coverage only.",
                ),
                _detail(
                    content_type="Research documents",
                    coverage="All available completed-task `research_papers.md`,"
                    " `research_internet.md`, and `research_code.md` files in full.",
                ),
            ],
            options=PresetOptions(
                include_completed_task_details=False,
                include_planned_task_long_descriptions=False,
                include_research_documents=True,
                include_suggestions=False,
                suggestion_limit=None,
                include_papers=False,
                paper_limit=None,
                include_datasets=False,
                include_libraries=False,
                include_metrics=False,
                include_full_answers=False,
            ),
        ),
        PresetDefinition(
            preset_id="results-deep-dive",
            title="Results Deep Dive",
            file_name="results-deep-dive.xml",
            description=("Completed-task result summaries plus all detailed results reports."),
            use_case=("Performance analysis, experiment comparison, and result interpretation."),
            included_content=[
                "project description",
                "completed task summaries",
                "planned tasks",
                "question and short-answer coverage",
                "results_detailed.md for each completed task",
            ],
            short_name="results",
            featured_rank=4,
            content_details=[
                _detail(
                    content_type="Project description",
                    coverage="Full `project/description.md`.",
                ),
                _detail(
                    content_type="Completed tasks",
                    coverage="All completed tasks with `results_summary` excerpts and short"
                    " descriptions.",
                ),
                _detail(
                    content_type="Detailed results",
                    coverage="Every available completed-task `results/results_detailed.md` file in"
                    " full.",
                ),
                _detail(
                    content_type="Planned tasks",
                    coverage="All planned or active tasks with status, date, dependencies, and"
                    " short descriptions.",
                ),
                _detail(
                    content_type="Questions and answers",
                    coverage="All questions with short-answer coverage only.",
                ),
            ],
            options=PresetOptions(
                include_completed_task_details=True,
                include_planned_task_long_descriptions=False,
                include_research_documents=False,
                include_suggestions=False,
                suggestion_limit=None,
                include_papers=False,
                paper_limit=None,
                include_datasets=False,
                include_libraries=False,
                include_metrics=False,
                include_full_answers=False,
            ),
        ),
        PresetDefinition(
            preset_id="roadmap",
            title="Roadmap",
            file_name="roadmap.xml",
            description=(
                "Project planning preset centered on upcoming tasks and open suggestions."
            ),
            use_case=(
                "Deciding what to do next, prioritizing experiments, and planning follow-up work."
            ),
            included_content=[
                "project description",
                "completed task summaries",
                "planned tasks with long descriptions",
                "question and short-answer coverage",
                "open suggestions",
            ],
            short_name="roadmap",
            featured_rank=3,
            content_details=[
                _detail(
                    content_type="Project description",
                    coverage="Full `project/description.md`.",
                ),
                _detail(
                    content_type="Completed tasks",
                    coverage="All completed tasks with `results_summary` excerpts and short"
                    " descriptions.",
                ),
                _detail(
                    content_type="Planned tasks",
                    coverage="All planned or active tasks with status, date, dependencies, short"
                    " descriptions, and full long descriptions.",
                ),
                _detail(
                    content_type="Questions and answers",
                    coverage="All questions with short-answer coverage only.",
                ),
                _detail(
                    content_type="Suggestions",
                    coverage="All open suggestions with priority, kind, source task, and"
                    " description excerpts.",
                ),
            ],
            options=PresetOptions(
                include_completed_task_details=False,
                include_planned_task_long_descriptions=True,
                include_research_documents=False,
                include_suggestions=True,
                suggestion_limit=None,
                include_papers=False,
                paper_limit=None,
                include_datasets=False,
                include_libraries=False,
                include_metrics=False,
                include_full_answers=False,
            ),
        ),
        PresetDefinition(
            preset_id="literature-and-assets",
            title="Literature and Assets",
            file_name="literature-and-assets.xml",
            description=(
                "Paper summaries and reusable project assets without the heaviest task reports."
            ),
            use_case=("Method discussion, resource selection, and related-work chats."),
            included_content=[
                "project description",
                "completed task summaries",
                "planned tasks",
                "question and short-answer coverage",
                "paper summaries",
                "datasets",
                "libraries",
                "metrics",
            ],
            short_name="assets",
            featured_rank=5,
            content_details=[
                _detail(
                    content_type="Project description",
                    coverage="Full `project/description.md`.",
                ),
                _detail(
                    content_type="Completed tasks",
                    coverage="All completed tasks with `results_summary` excerpts and short"
                    " descriptions.",
                ),
                _detail(
                    content_type="Planned tasks",
                    coverage="All planned or active tasks with status, date, dependencies, and"
                    " short descriptions.",
                ),
                _detail(
                    content_type="Questions and answers",
                    coverage="All questions with short-answer coverage only.",
                ),
                _detail(
                    content_type="Papers",
                    coverage="All papers with metadata and summary excerpts from paper summaries,"
                    " full summaries, or abstracts.",
                ),
                _detail(
                    content_type="Datasets",
                    coverage="All datasets with access, size, source task, and description"
                    " excerpts.",
                ),
                _detail(
                    content_type="Libraries",
                    coverage="All libraries with module paths, source task, and description"
                    " excerpts.",
                ),
                _detail(
                    content_type="Metrics",
                    coverage="All registered metrics with units, value types, and description"
                    " excerpts.",
                ),
            ],
            options=PresetOptions(
                include_completed_task_details=False,
                include_planned_task_long_descriptions=False,
                include_research_documents=False,
                include_suggestions=False,
                suggestion_limit=None,
                include_papers=True,
                paper_limit=None,
                include_datasets=True,
                include_libraries=True,
                include_metrics=True,
                include_full_answers=False,
            ),
        ),
        PresetDefinition(
            preset_id="qa",
            title="Questions and Answers",
            file_name="qa.xml",
            description=(
                "Question-centric preset with the full answer corpus and compact project state."
            ),
            use_case=("Answer review, follow-up questioning, and project knowledge-base chats."),
            included_content=[
                "project description",
                "completed task summaries",
                "planned tasks",
                "full answer coverage",
            ],
            short_name="qa",
            content_details=[
                _detail(
                    content_type="Project description",
                    coverage="Full `project/description.md`.",
                ),
                _detail(
                    content_type="Completed tasks",
                    coverage="All completed tasks with `results_summary` excerpts and short"
                    " descriptions.",
                ),
                _detail(
                    content_type="Planned tasks",
                    coverage="All planned or active tasks with status, date, dependencies, and"
                    " short descriptions.",
                ),
                _detail(
                    content_type="Questions and answers",
                    coverage="All questions with full-answer bodies when available.",
                ),
            ],
            options=PresetOptions(
                include_completed_task_details=False,
                include_planned_task_long_descriptions=False,
                include_research_documents=False,
                include_suggestions=False,
                suggestion_limit=None,
                include_papers=False,
                paper_limit=None,
                include_datasets=False,
                include_libraries=False,
                include_metrics=False,
                include_full_answers=True,
            ),
        ),
        PresetDefinition(
            preset_id="project-memory",
            title="Project Memory",
            file_name="project-memory.xml",
            description=(
                "Mid-size preset intended as a reusable working memory for ongoing chats."
            ),
            use_case=("Keeping a durable project memory in medium-size chat sessions."),
            included_content=[
                "project description",
                "completed task summaries",
                "planned tasks",
                "question and short-answer coverage",
                "recent paper summaries",
                "datasets",
                "libraries",
                "metrics",
                "top open suggestions",
            ],
            short_name="memory",
            content_details=[
                _detail(
                    content_type="Project description",
                    coverage="Full `project/description.md`.",
                ),
                _detail(
                    content_type="Completed tasks",
                    coverage="All completed tasks with `results_summary` excerpts and short"
                    " descriptions.",
                ),
                _detail(
                    content_type="Planned tasks",
                    coverage="All planned or active tasks with status, date, dependencies, and"
                    " short descriptions.",
                ),
                _detail(
                    content_type="Questions and answers",
                    coverage="All questions with short-answer coverage only.",
                ),
                _detail(
                    content_type="Papers",
                    coverage="The 20 most recent papers with metadata and summary excerpts.",
                ),
                _detail(
                    content_type="Datasets",
                    coverage="All datasets with access, size, source task, and description"
                    " excerpts.",
                ),
                _detail(
                    content_type="Libraries",
                    coverage="All libraries with module paths, source task, and description"
                    " excerpts.",
                ),
                _detail(
                    content_type="Metrics",
                    coverage="All registered metrics with units, value types, and description"
                    " excerpts.",
                ),
                _detail(
                    content_type="Suggestions",
                    coverage="The top 20 open suggestions ordered by priority and date.",
                ),
            ],
            options=PresetOptions(
                include_completed_task_details=False,
                include_planned_task_long_descriptions=False,
                include_research_documents=False,
                include_suggestions=True,
                suggestion_limit=20,
                include_papers=True,
                paper_limit=20,
                include_datasets=True,
                include_libraries=True,
                include_metrics=True,
                include_full_answers=False,
            ),
        ),
    ]
