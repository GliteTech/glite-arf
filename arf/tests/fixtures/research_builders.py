from pathlib import Path

from arf.scripts.verificators.common import paths
from arf.tests.fixtures.writers import write_text

SPEC_VERSION_RESEARCH: str = "1"
DEFAULT_DATE_COMPLETED: str = "2026-04-01"
STATUS_COMPLETE: str = "complete"
STAGE_PAPERS: str = "papers"
STAGE_INTERNET: str = "internet"
STAGE_CODE: str = "code"
DEFAULT_CATEGORY: str = "test-category"


def _serialize_frontmatter(
    data: dict[str, str | int | list[str]],
) -> str:
    lines: list[str] = ["---"]
    for key, value in data.items():
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f'  - "{item}"')
        elif isinstance(value, int):
            lines.append(f"{key}: {value}")
        else:
            lines.append(f'{key}: "{value}"')
    lines.append("---")
    return "\n".join(lines)


DEFAULT_RESEARCH_PAPERS_BODY: str = (
    "# Research Papers\n"
    "\n"
    "## Task Objective\n"
    "\n"
    "The objective of this task is to investigate methods for word sense"
    " disambiguation and evaluate their effectiveness on standard"
    " benchmarks.\n"
    "\n"
    "## Category Selection Rationale\n"
    "\n"
    "The test-category was selected because it contains papers directly"
    " relevant to the task objective. Papers in this category cover"
    " supervised methods, evaluation frameworks, and baseline approaches"
    " that inform our experimental design.\n"
    "\n"
    "## Key Findings\n"
    "\n"
    "### Supervised Approaches\n"
    "\n"
    "Recent supervised approaches to word sense disambiguation have"
    " achieved strong results on standard benchmarks. Bi-encoder models"
    " map target words and sense definitions into a shared embedding"
    " space, enabling efficient nearest-neighbor lookup at inference"
    " time [TestPaper2024]. Cross-encoder models jointly encode the"
    " context and each candidate definition, achieving higher accuracy"
    " at the cost of increased inference time [AnotherPaper2023].\n"
    "\n"
    "### Evaluation Frameworks\n"
    "\n"
    "The Raganato unified evaluation framework remains the standard"
    " benchmark for English all-words WSD. It combines five datasets"
    " (Senseval-2, Senseval-3, SemEval-2007, SemEval-2013, and"
    " SemEval-2015) with a consistent scoring methodology"
    " [Raganato2017]. Performance varies significantly across parts"
    " of speech, with verbs consistently proving the most difficult"
    " category for all systems tested.\n"
    "\n"
    "### Knowledge-Based Methods\n"
    "\n"
    "Knowledge-based approaches leverage the structure of WordNet and"
    " other lexical resources to perform disambiguation without"
    " requiring labeled training data. Graph-based methods such as"
    " UKB propagate activation through the WordNet graph to identify"
    " the most relevant sense for each target word in context"
    " [KnowledgePaper2022].\n"
    "\n"
    "## Methodology Insights\n"
    "\n"
    "The most effective approaches combine contextual embeddings from"
    " pretrained language models with sense definitions from WordNet."
    " Training on SemCor remains the standard approach, though recent"
    " work has explored augmenting training data with LLM-generated"
    " examples. Evaluation should always include per-POS breakdowns"
    " to identify specific weaknesses.\n"
    "\n"
    "## Gaps and Limitations\n"
    "\n"
    "Current research has limited coverage of cost-quality tradeoffs"
    " and real-time inference requirements. Few papers systematically"
    " compare model sizes against disambiguation accuracy.\n"
    "\n"
    "## Recommendations for This Task\n"
    "\n"
    "Start with a bi-encoder baseline trained on SemCor and evaluate"
    " on the full Raganato benchmark. Include per-POS analysis in all"
    " evaluation reports to identify verb-specific weaknesses.\n"
    "\n"
    "## Paper Index\n"
    "\n"
    "### [TestPaper2024]\n"
    "\n"
    "* **Title**: A Test Paper About WSD Methods\n"
    "* **Authors**: Test Author\n"
    "* **Year**: 2024\n"
    "* **DOI**: `10.1234/test/2024`\n"
    "* **Asset**: `assets/paper/10.1234_test_2024/`\n"
    "* **Categories**: `test-category`\n"
    "* **Relevance**: Directly relevant bi-encoder approach.\n"
    "\n"
    "### [AnotherPaper2023]\n"
    "\n"
    "* **Title**: Cross-Encoder Approaches to WSD\n"
    "* **Authors**: Another Author\n"
    "* **Year**: 2023\n"
    "* **DOI**: `10.1234/another/2023`\n"
    "* **Asset**: `assets/paper/10.1234_another_2023/`\n"
    "* **Categories**: `test-category`\n"
    "* **Relevance**: Cross-encoder comparison baseline.\n"
    "\n"
    "### [Raganato2017]\n"
    "\n"
    "* **Title**: Unified WSD Evaluation Framework\n"
    "* **Authors**: Raganato, A. et al.\n"
    "* **Year**: 2017\n"
    "* **DOI**: `10.18653/v1/E17-1010`\n"
    "* **Asset**: `assets/paper/10.18653_v1_E17-1010/`\n"
    "* **Categories**: `test-category`\n"
    "* **Relevance**: Standard evaluation benchmark.\n"
    "\n"
    "### [KnowledgePaper2022]\n"
    "\n"
    "* **Title**: Graph-Based WSD with WordNet\n"
    "* **Authors**: Knowledge Author\n"
    "* **Year**: 2022\n"
    "* **DOI**: `10.1234/knowledge/2022`\n"
    "* **Asset**: `assets/paper/10.1234_knowledge_2022/`\n"
    "* **Categories**: `test-category`\n"
    "* **Relevance**: Knowledge-based baseline approach.\n"
)

DEFAULT_RESEARCH_INTERNET_BODY: str = (
    "# Research Internet\n"
    "\n"
    "## Task Objective\n"
    "\n"
    "The objective of this task is to find recent developments in word"
    " sense disambiguation not covered by existing downloaded papers."
    " This includes LLM-based approaches, recent benchmark results,"
    " and community best practices for evaluation.\n"
    "\n"
    "## Gaps Addressed\n"
    "\n"
    "Based on gaps identified in `research_papers.md`, this internet"
    " research addresses insufficient coverage of recent preprints and"
    " blog posts about LLM-based WSD approaches. The paper research"
    " identified limited coverage of cost-quality tradeoffs and real-time"
    " inference requirements as key gaps.\n"
    "\n"
    "* Cost-quality tradeoff analysis: Partially resolved\n"
    "* LLM prompting strategies for WSD: Resolved\n"
    "* Recent benchmark leaderboard results: Resolved\n"
    "\n"
    "## Search Strategy\n"
    "\n"
    "Searches were conducted on Google Scholar, Semantic Scholar, and"
    " arXiv using the following queries:\n"
    "\n"
    '1. "word sense disambiguation" AND "large language model"\n'
    '2. "WSD" AND "prompt engineering" OR "few-shot"\n'
    '3. "Raganato benchmark" AND "2024" OR "2025"\n'
    "\n"
    "Date filters were applied to focus on publications from 2024"
    " and 2025. Inclusion criteria: English-language publications"
    " addressing WSD methods, evaluation, or datasets.\n"
    "\n"
    "## Key Findings\n"
    "\n"
    "### LLM-Based Approaches\n"
    "\n"
    "Several recent blog posts and preprints describe using GPT-4 and"
    " Claude for zero-shot WSD. Results suggest that large language"
    " models can achieve competitive performance on common senses but"
    " struggle with rare senses and domain-specific terminology."
    " Chain-of-thought prompting improves accuracy by encouraging the"
    " model to reason explicitly about sense distinctions before"
    " selecting an answer. Cost analysis indicates that LLM-based"
    " approaches are significantly more expensive per instance than"
    " fine-tuned models, with GPT-4 costing approximately $0.01 per"
    " disambiguation compared to sub-millisecond inference with"
    " dedicated models.\n"
    "\n"
    "### Benchmark Updates\n"
    "\n"
    "The Raganato benchmark remains the standard evaluation framework."
    " No new major evaluation datasets have been released in 2025."
    " Several teams have reported results on the benchmark using"
    " instruction-tuned models with varying degrees of success."
    " The current top results hover around 85-89 F1 on the ALL"
    " concatenation.\n"
    "\n"
    "## Methodology Insights\n"
    "\n"
    "Internet research confirms that combining fine-tuned encoders"
    " with LLM-generated training data is a promising direction."
    " Several practitioners report success with curriculum learning"
    " strategies that prioritize difficult senses during training."
    " Evaluation should include cost-per-instance metrics alongside"
    " traditional accuracy measures.\n"
    "\n"
    "## Discovered Papers\n"
    "\n"
    '* **Title**: "LLM-WSD: Zero-Shot Word Sense Disambiguation'
    ' with Instruction-Tuned Models"\n'
    "  * **Authors**: Preprint Author et al.\n"
    "  * **Year**: 2025\n"
    "  * **URL**: https://arxiv.org/abs/2025.12345\n"
    "  * **Suggested categories**: `test-category`\n"
    "  * **Why download**: Directly relevant to LLM-based WSD.\n"
    "\n"
    "## Recommendations for This Task\n"
    "\n"
    "Include LLM-based baselines in the experimental comparison and"
    " track cost-per-instance alongside F1 scores. Consider using"
    " chain-of-thought prompting for the LLM experiments.\n"
    "\n"
    "## Source Index\n"
    "\n"
    "### [Source1]\n"
    "\n"
    "* **Type**: blog\n"
    "* **Title**: LLM-Based WSD: A Practical Guide\n"
    "* **Author/Org**: AI Research Blog\n"
    "* **Date**: 2025-01\n"
    "* **URL**: https://example.com/llm-wsd-guide\n"
    "* **Peer-reviewed**: no\n"
    "* **Relevance**: Practical guidance on LLM-based WSD.\n"
    "\n"
    "### [Source2]\n"
    "\n"
    "* **Type**: paper\n"
    "* **Title**: Zero-Shot WSD with Instruction-Tuned Models\n"
    "* **Authors**: Preprint Author et al.\n"
    "* **Year**: 2025\n"
    "* **URL**: https://arxiv.org/abs/2025.12345\n"
    "* **Peer-reviewed**: no\n"
    "* **Relevance**: Recent preprint on zero-shot WSD.\n"
)

DEFAULT_RESEARCH_CODE_BODY: str = (
    "# Research Code\n"
    "\n"
    "## Task Objective\n"
    "\n"
    "The objective of this task is to review existing code, libraries,"
    " and assets from prior tasks that can be reused for the current"
    " word sense disambiguation implementation work.\n"
    "\n"
    "## Library Landscape\n"
    "\n"
    "The Python ecosystem provides several relevant libraries for WSD"
    " including NLTK, spaCy, and the Hugging Face transformers library.\n"
    "\n"
    "## Key Findings\n"
    "\n"
    "### Prior Task Implementations\n"
    "\n"
    "Previous tasks have implemented a data loader for the Raganato"
    " XML format [t0012] that handles tokenization, lemmatization,"
    " and sense key mapping. This loader supports all five evaluation"
    " datasets and produces a standardized DataFrame output. The"
    " scorer module from the same task computes micro-F1 scores with"
    " per-POS breakdowns.\n"
    "\n"
    "### External Libraries\n"
    "\n"
    "The transformers library from Hugging Face provides pretrained"
    " encoder models suitable for WSD. The sentence-transformers"
    " library offers bi-encoder architectures that can be adapted"
    " for sense embedding comparison [t0015]. NLTK provides WordNet"
    " access and basic sense inventory utilities.\n"
    "\n"
    "## Reusable Code and Assets\n"
    "\n"
    "The WSD data loader from t0012 should be imported directly rather"
    " than reimplemented. The scorer module provides standardized"
    " evaluation that matches the Raganato Java scorer output. Both"
    " modules are well-tested and documented. The sentence-transformers"
    " library offers useful building blocks for sense embedding"
    " comparison.\n"
    "\n"
    "## Lessons Learned\n"
    "\n"
    "Prior tasks found that XML parsing of the Raganato format requires"
    " careful handling of multi-word expressions and entity references."
    " The evaluation scorer must match the Raganato Java scorer output"
    " exactly for results to be comparable with published literature.\n"
    "\n"
    "## Recommendations for This Task\n"
    "\n"
    "Reuse the data loader and scorer from [t0012] for all evaluation"
    " runs. Use the transformers library for encoder models and"
    " sentence-transformers from [t0015] for bi-encoder baselines."
    " Ensure that all evaluation scripts produce per-POS breakdowns"
    " in addition to the overall F1 metric.\n"
    "\n"
    "## Task Index\n"
    "\n"
    "### [t0012]\n"
    "\n"
    "* **Task ID**: t0012_build_wsd_data_loader_and_scorer\n"
    "* **Name**: Build WSD Data Loader and Scorer\n"
    "* **Status**: completed\n"
    "* **Relevance**: Provides reusable data loader and scorer.\n"
    "\n"
    "### [t0015]\n"
    "\n"
    "* **Task ID**: t0015_sentence_transformer_experiments\n"
    "* **Name**: Sentence Transformer Experiments\n"
    "* **Status**: completed\n"
    "* **Relevance**: Bi-encoder architecture for sense embeddings.\n"
)


def build_research_papers(
    *,
    repo_root: Path,
    task_id: str,
    body: str | None = None,
    frontmatter_overrides: dict[str, str | int | list[str]] | None = None,
) -> Path:
    frontmatter: dict[str, str | int | list[str]] = {
        "spec_version": SPEC_VERSION_RESEARCH,
        "task_id": task_id,
        "research_stage": STAGE_PAPERS,
        "papers_reviewed": 5,
        "papers_cited": 4,
        "categories_consulted": [DEFAULT_CATEGORY],
        "date_completed": DEFAULT_DATE_COMPLETED,
        "status": STATUS_COMPLETE,
    }
    if frontmatter_overrides is not None:
        frontmatter.update(frontmatter_overrides)

    content: str = (
        _serialize_frontmatter(data=frontmatter)
        + "\n\n"
        + (body if body is not None else DEFAULT_RESEARCH_PAPERS_BODY)
    )
    research_path: Path = paths.research_papers_path(task_id=task_id)
    write_text(path=research_path, content=content)
    return research_path


def build_research_internet(
    *,
    repo_root: Path,
    task_id: str,
    body: str | None = None,
    frontmatter_overrides: dict[str, str | int | list[str]] | None = None,
) -> Path:
    frontmatter: dict[str, str | int | list[str]] = {
        "spec_version": SPEC_VERSION_RESEARCH,
        "task_id": task_id,
        "research_stage": STAGE_INTERNET,
        "searches_conducted": 3,
        "sources_cited": 2,
        "papers_discovered": 1,
        "date_completed": DEFAULT_DATE_COMPLETED,
        "status": STATUS_COMPLETE,
    }
    if frontmatter_overrides is not None:
        frontmatter.update(frontmatter_overrides)

    content: str = (
        _serialize_frontmatter(data=frontmatter)
        + "\n\n"
        + (body if body is not None else DEFAULT_RESEARCH_INTERNET_BODY)
    )
    research_path: Path = paths.research_internet_path(task_id=task_id)
    write_text(path=research_path, content=content)
    return research_path


def build_research_code(
    *,
    repo_root: Path,
    task_id: str,
    body: str | None = None,
    frontmatter_overrides: dict[str, str | int | list[str]] | None = None,
) -> Path:
    frontmatter: dict[str, str | int | list[str]] = {
        "spec_version": SPEC_VERSION_RESEARCH,
        "task_id": task_id,
        "research_stage": STAGE_CODE,
        "tasks_reviewed": 3,
        "tasks_cited": 2,
        "libraries_found": 1,
        "libraries_relevant": 1,
        "date_completed": DEFAULT_DATE_COMPLETED,
        "status": STATUS_COMPLETE,
    }
    if frontmatter_overrides is not None:
        frontmatter.update(frontmatter_overrides)

    content: str = (
        _serialize_frontmatter(data=frontmatter)
        + "\n\n"
        + (body if body is not None else DEFAULT_RESEARCH_CODE_BODY)
    )
    research_path: Path = paths.research_code_path(task_id=task_id)
    write_text(path=research_path, content=content)
    return research_path
