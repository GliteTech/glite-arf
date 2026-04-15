"""Step verification registry.

Maps canonical step IDs to their verification requirements. Each step
defines what files must exist in its step folder, what external output
files it produces, and what markdown sections are required.

Usage:
    from arf.scripts.verificators.step_registry import (
        get_step_spec,
        STEP_REGISTRY,
    )
"""

from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Requirement dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class MarkdownFileRequirement:
    relative_path: str
    required_sections: list[str] = field(default_factory=list)
    min_total_words: int = 0


@dataclass(frozen=True, slots=True)
class FileRequirement:
    relative_path: str
    is_external: bool = False
    markdown: MarkdownFileRequirement | None = None


@dataclass(frozen=True, slots=True)
class StepVerificationSpec:
    step_id: str
    step_order: int
    display_name: str
    is_required: bool
    required_files: list[FileRequirement] = field(default_factory=list)
    optional_files: list[FileRequirement] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Shared markdown section lists
# ---------------------------------------------------------------------------

SECTIONS_STEP_LOG: list[str] = [
    "Summary",
    "Actions Taken",
    "Outputs",
    "Issues",
]

SECTIONS_RESEARCH_PAPERS: list[str] = [
    "Task Objective",
    "Category Selection Rationale",
    "Key Findings",
    "Methodology Insights",
    "Gaps and Limitations",
    "Recommendations for This Task",
    "Paper Index",
]

SECTIONS_RESEARCH_INTERNET: list[str] = [
    "Task Objective",
    "Gaps Addressed",
    "Search Strategy",
    "Key Findings",
    "Methodology Insights",
    "Discovered Papers",
    "Recommendations for This Task",
    "Source Index",
]

SECTIONS_RESEARCH_CODE: list[str] = [
    "Task Objective",
    "Library Landscape",
    "Key Findings",
    "Reusable Code and Assets",
    "Lessons Learned",
    "Recommendations for This Task",
    "Task Index",
]

SECTIONS_PLAN: list[str] = [
    "Objective",
    "Approach",
    "Cost Estimation",
    "Step by Step",
    "Remote Machines",
    "Assets Needed",
    "Expected Assets",
    "Time Estimation",
    "Risks & Fallbacks",
    "Verification Criteria",
]

SECTIONS_RESULTS_SUMMARY: list[str] = [
    "Summary",
    "Metrics",
    "Verification",
]

SECTIONS_RESULTS_DETAILED: list[str] = [
    "Summary",
    "Methodology",
    "Verification",
]


# ---------------------------------------------------------------------------
# Helper to build a standard step_log.md requirement
# ---------------------------------------------------------------------------


def _step_log(*, min_words: int = 50) -> FileRequirement:
    return FileRequirement(
        relative_path="step_log.md",
        markdown=MarkdownFileRequirement(
            relative_path="step_log.md",
            required_sections=SECTIONS_STEP_LOG,
            min_total_words=min_words,
        ),
    )


# ---------------------------------------------------------------------------
# Canonical step definitions
# ---------------------------------------------------------------------------


def _build_registry() -> dict[str, StepVerificationSpec]:
    specs: list[StepVerificationSpec] = [
        # --- Preflight Phase ---
        StepVerificationSpec(
            step_id="create-branch",
            step_order=1,
            display_name="Create branch",
            is_required=True,
            required_files=[
                FileRequirement(relative_path="branch_info.txt"),
            ],
        ),
        StepVerificationSpec(
            step_id="check-deps",
            step_order=2,
            display_name="Check dependencies",
            is_required=True,
            required_files=[
                FileRequirement(relative_path="deps_report.json"),
            ],
        ),
        StepVerificationSpec(
            step_id="init-folders",
            step_order=3,
            display_name="Initialize folders",
            is_required=True,
            required_files=[
                FileRequirement(relative_path="folders_created.txt"),
            ],
        ),
        # --- Research Phase ---
        StepVerificationSpec(
            step_id="research-papers",
            step_order=4,
            display_name="Research existing papers",
            is_required=False,
            required_files=[
                _step_log(min_words=100),
                FileRequirement(
                    relative_path="research/research_papers.md",
                    is_external=True,
                    markdown=MarkdownFileRequirement(
                        relative_path="research/research_papers.md",
                        required_sections=SECTIONS_RESEARCH_PAPERS,
                        min_total_words=400,
                    ),
                ),
            ],
        ),
        StepVerificationSpec(
            step_id="research-internet",
            step_order=5,
            display_name="Internet research",
            is_required=False,
            required_files=[
                _step_log(min_words=100),
                FileRequirement(
                    relative_path="research/research_internet.md",
                    is_external=True,
                    markdown=MarkdownFileRequirement(
                        relative_path="research/research_internet.md",
                        required_sections=SECTIONS_RESEARCH_INTERNET,
                        min_total_words=400,
                    ),
                ),
            ],
        ),
        StepVerificationSpec(
            step_id="research-code",
            step_order=6,
            display_name="Research previous tasks",
            is_required=False,
            required_files=[
                _step_log(min_words=50),
                FileRequirement(
                    relative_path="research/research_code.md",
                    is_external=True,
                    markdown=MarkdownFileRequirement(
                        relative_path="research/research_code.md",
                        required_sections=SECTIONS_RESEARCH_CODE,
                        min_total_words=300,
                    ),
                ),
            ],
        ),
        # --- Planning Phase ---
        StepVerificationSpec(
            step_id="planning",
            step_order=7,
            display_name="Planning",
            is_required=False,
            required_files=[
                _step_log(min_words=50),
                FileRequirement(
                    relative_path="plan/plan.md",
                    is_external=True,
                    markdown=MarkdownFileRequirement(
                        relative_path="plan/plan.md",
                        required_sections=SECTIONS_PLAN,
                        min_total_words=200,
                    ),
                ),
            ],
        ),
        # --- Execution Phase ---
        StepVerificationSpec(
            step_id="setup-machines",
            step_order=8,
            display_name="Set up machines",
            is_required=False,
            required_files=[
                _step_log(min_words=30),
            ],
        ),
        StepVerificationSpec(
            step_id="implementation",
            step_order=9,
            display_name="Implementation",
            is_required=True,
            required_files=[
                _step_log(min_words=100),
            ],
        ),
        StepVerificationSpec(
            step_id="teardown",
            step_order=10,
            display_name="Tear down machines",
            is_required=False,
            required_files=[
                _step_log(min_words=30),
            ],
        ),
        # --- Analysis Phase ---
        StepVerificationSpec(
            step_id="creative-thinking",
            step_order=11,
            display_name="Creative thinking",
            is_required=False,
            required_files=[
                _step_log(min_words=100),
            ],
        ),
        StepVerificationSpec(
            step_id="results",
            step_order=12,
            display_name="Results summarization",
            is_required=True,
            required_files=[
                _step_log(min_words=50),
                FileRequirement(
                    relative_path="results/results_summary.md",
                    is_external=True,
                    markdown=MarkdownFileRequirement(
                        relative_path="results/results_summary.md",
                        required_sections=SECTIONS_RESULTS_SUMMARY,
                        min_total_words=100,
                    ),
                ),
                FileRequirement(
                    relative_path="results/results_detailed.md",
                    is_external=True,
                    markdown=MarkdownFileRequirement(
                        relative_path="results/results_detailed.md",
                        required_sections=SECTIONS_RESULTS_DETAILED,
                        min_total_words=200,
                    ),
                ),
                FileRequirement(
                    relative_path="results/metrics.json",
                    is_external=True,
                ),
            ],
        ),
        StepVerificationSpec(
            step_id="compare-literature",
            step_order=13,
            display_name="Compare to literature",
            is_required=False,
            required_files=[
                _step_log(min_words=100),
            ],
        ),
        # --- Reporting Phase ---
        StepVerificationSpec(
            step_id="suggestions",
            step_order=14,
            display_name="Formulate suggestions",
            is_required=True,
            required_files=[
                _step_log(min_words=50),
                FileRequirement(
                    relative_path="results/suggestions.json",
                    is_external=True,
                ),
            ],
        ),
        StepVerificationSpec(
            step_id="reporting",
            step_order=15,
            display_name="Post-task reporting",
            is_required=True,
            required_files=[
                _step_log(min_words=50),
                FileRequirement(
                    relative_path="logs/sessions/capture_report.json",
                    is_external=True,
                ),
            ],
        ),
    ]

    registry: dict[str, StepVerificationSpec] = {}
    for spec in specs:
        registry[spec.step_id] = spec
    return registry


STEP_REGISTRY: dict[str, StepVerificationSpec] = _build_registry()


# ---------------------------------------------------------------------------
# Lookup helpers
# ---------------------------------------------------------------------------


def get_step_spec(*, step_id: str) -> StepVerificationSpec | None:
    return STEP_REGISTRY.get(step_id)


def build_default_spec(
    *,
    step_id: str,
    step_order: int,
) -> StepVerificationSpec:
    """Build a minimal spec for a custom (non-canonical) step."""
    return StepVerificationSpec(
        step_id=step_id,
        step_order=step_order,
        display_name=step_id.replace("-", " ").title(),
        is_required=False,
        required_files=[
            _step_log(min_words=30),
        ],
    )


def get_canonical_step_ids() -> list[str]:
    sorted_specs: list[StepVerificationSpec] = sorted(
        STEP_REGISTRY.values(),
        key=lambda s: s.step_order,
    )
    return [spec.step_id for spec in sorted_specs]
