from pathlib import Path

from arf.scripts.verificators.common import paths
from arf.tests.fixtures.writers import write_json, write_text

DEFAULT_PROJECT_DESCRIPTION: str = (
    "# Test Research Project\n"
    "\n"
    "## Goal\n"
    "\n"
    "Research and evaluate methods for the test domain, comparing"
    " fine-tuned models against LLM-based approaches across quality,"
    " cost, and speed dimensions.\n"
    "\n"
    "## Scope\n"
    "\n"
    "### In Scope\n"
    "\n"
    "* Reproducing and comparing published methods\n"
    "* Standard evaluation on established benchmarks\n"
    "* LLM-based approaches via prompting and fine-tuning\n"
    "* Cost, speed, and quality analysis across all approaches\n"
    "\n"
    "### Out of Scope\n"
    "\n"
    "* Non-English languages and multilingual evaluation\n"
    "* Production deployment and serving infrastructure\n"
    "\n"
    "## Research Questions\n"
    "\n"
    "1. What is the current state of the art and can we reproduce"
    " the top results?\n"
    "2. Can LLM-generated training data improve performance over"
    " human-annotated corpora?\n"
    "3. How do fine-tuned small models compare to large LLMs on"
    " quality, cost, and speed?\n"
    "\n"
    "## Success Criteria\n"
    "\n"
    "* Reproduce at least 3 published methods within 2 points of"
    " reported results\n"
    "* Achieve or exceed current state-of-the-art performance\n"
    "* Produce a cost/speed vs. quality Pareto chart comparing at"
    " least 5 approaches\n"
    "\n"
    "## Key References\n"
    "\n"
    "* Raganato2017 -- Unified evaluation framework and benchmark\n"
    "* SemCor -- Primary human-annotated training corpus\n"
    "* SANDWiCH (2025) -- Current near-SOTA bi-encoder approach\n"
    "\n"
    "## Current Phase\n"
    "\n"
    "The project is in the early infrastructure phase. Initial papers"
    " have been collected and the first baseline experiments are"
    " being planned.\n"
)

DEFAULT_BUDGET_PAYLOAD: dict[str, object] = {
    "total_budget": 2000.0,
    "currency": "USD",
    "per_task_default_limit": 100.0,
    "available_services": ["openai", "anthropic"],
    "alerts": {
        "warn_at_percent": 80,
        "stop_at_percent": 95,
    },
}


def build_project_description(
    *,
    repo_root: Path,
    content: str | None = None,
) -> Path:
    desc_path: Path = paths.PROJECT_DESCRIPTION_PATH
    write_text(
        path=desc_path,
        content=(content if content is not None else DEFAULT_PROJECT_DESCRIPTION),
    )
    return desc_path


def build_project_budget(
    *,
    repo_root: Path,
    payload: dict[str, object] | None = None,
) -> Path:
    budget_path: Path = paths.PROJECT_BUDGET_PATH
    write_json(
        path=budget_path,
        data=(payload if payload is not None else dict(DEFAULT_BUDGET_PAYLOAD)),
    )
    return budget_path
