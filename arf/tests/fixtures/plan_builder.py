from pathlib import Path

from arf.scripts.verificators.common import paths
from arf.tests.fixtures.writers import write_frontmatter_md

SPEC_VERSION_PLAN: str = "2"
DEFAULT_DATE_COMPLETED: str = "2026-04-01"
STATUS_COMPLETE: str = "complete"

SECTION_OBJECTIVE: str = "Objective"
SECTION_REQUIREMENT_CHECKLIST: str = "Task Requirement Checklist"
SECTION_APPROACH: str = "Approach"
SECTION_COST_ESTIMATION: str = "Cost Estimation"
SECTION_STEP_BY_STEP: str = "Step by Step"
SECTION_REMOTE_MACHINES: str = "Remote Machines"
SECTION_ASSETS_NEEDED: str = "Assets Needed"
SECTION_EXPECTED_ASSETS: str = "Expected Assets"
SECTION_TIME_ESTIMATION: str = "Time Estimation"
SECTION_RISKS_FALLBACKS: str = "Risks & Fallbacks"
SECTION_VERIFICATION_CRITERIA: str = "Verification Criteria"

DEFAULT_SECTIONS: dict[str, str] = {
    SECTION_OBJECTIVE: (
        "Implement and evaluate a baseline word sense disambiguation"
        " model using the Raganato unified evaluation framework to"
        " establish reference performance numbers."
    ),
    SECTION_REQUIREMENT_CHECKLIST: (
        "* REQ-1: Train a baseline WSD model on SemCor training data\n"
        "* REQ-2: Evaluate on all five Raganato benchmark datasets\n"
        "* REQ-3: Report per-POS F1 breakdown for each dataset\n"
        "* REQ-4: Document model architecture and hyperparameters"
    ),
    SECTION_APPROACH: (
        "Train a bi-encoder model that maps context embeddings and"
        " sense definition embeddings into a shared space. Use"
        " cosine similarity for sense ranking at inference time."
        " Evaluate using the standard Raganato scorer."
    ),
    SECTION_COST_ESTIMATION: (
        "Estimated total cost: $5.00.\n"
        "* Compute: $0.00 (local machine)\n"
        "* API calls: $5.00 (OpenAI embeddings for comparison)"
    ),
    SECTION_STEP_BY_STEP: (
        "1. [CRITICAL] Load and validate SemCor training data using"
        " the existing data loader from t0012\n"
        "2. Prepare sense definitions from WordNet 3.0 for all"
        " target senses in the training set\n"
        "3. Train the bi-encoder model with contrastive loss\n"
        "4. [CRITICAL] Evaluate on all five Raganato datasets and"
        " compute per-POS F1 scores\n"
        "5. Generate results summary and comparison charts"
    ),
    SECTION_REMOTE_MACHINES: (
        "No remote machines required. All computation runs on the local development machine."
    ),
    SECTION_ASSETS_NEEDED: ("* SemCor training data from t0008\n* WSD data loader from t0012"),
    SECTION_EXPECTED_ASSETS: (
        "* One trained model asset (bi-encoder baseline)\n"
        "* One predictions asset (evaluation predictions)\n"
        "* Results charts in results/images/"
    ),
    SECTION_TIME_ESTIMATION: ("Estimated time: 2-3 hours including training and evaluation."),
    SECTION_RISKS_FALLBACKS: (
        "| Risk | Likelihood | Impact | Mitigation |\n"
        "|------|-----------|--------|------------|\n"
        "| Training divergence | Low | High |"
        " Use learning rate warmup and gradient clipping |\n"
        "| Memory overflow | Medium | Medium |"
        " Reduce batch size or use gradient accumulation |"
    ),
    SECTION_VERIFICATION_CRITERIA: (
        "* Model produces predictions for all instances in each"
        " evaluation dataset\n"
        "* F1 scores are computed for each dataset and each POS\n"
        "* Results summary contains all required sections\n"
        "* All output files pass verificator checks"
    ),
}

MANDATORY_SECTION_ORDER: list[str] = [
    SECTION_OBJECTIVE,
    SECTION_REQUIREMENT_CHECKLIST,
    SECTION_APPROACH,
    SECTION_COST_ESTIMATION,
    SECTION_STEP_BY_STEP,
    SECTION_REMOTE_MACHINES,
    SECTION_ASSETS_NEEDED,
    SECTION_EXPECTED_ASSETS,
    SECTION_TIME_ESTIMATION,
    SECTION_RISKS_FALLBACKS,
    SECTION_VERIFICATION_CRITERIA,
]


def build_plan(
    *,
    repo_root: Path,
    task_id: str,
    sections: dict[str, str] | None = None,
    omit_sections: list[str] | None = None,
    frontmatter_overrides: dict[str, str | int] | None = None,
) -> Path:
    frontmatter: dict[str, str | int] = {
        "spec_version": SPEC_VERSION_PLAN,
        "task_id": task_id,
        "date_completed": DEFAULT_DATE_COMPLETED,
        "status": STATUS_COMPLETE,
    }
    if frontmatter_overrides is not None:
        frontmatter.update(frontmatter_overrides)

    merged_sections: dict[str, str] = dict(DEFAULT_SECTIONS)
    if sections is not None:
        merged_sections.update(sections)

    omit_set: set[str] = set(omit_sections) if omit_sections is not None else set()

    body_parts: list[str] = ["# Plan\n"]
    for section_name in MANDATORY_SECTION_ORDER:
        if section_name in omit_set:
            continue
        content: str = merged_sections.get(section_name, "")
        body_parts.append(f"## {section_name}\n")
        body_parts.append(f"{content}\n")

    body: str = "\n".join(body_parts)

    plan_file_path: Path = paths.plan_path(task_id=task_id)
    write_frontmatter_md(
        path=plan_file_path,
        frontmatter=frontmatter,
        body=body,
    )
    return plan_file_path
