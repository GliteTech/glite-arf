"""Find existing paper assets similar to a given paper.

Scans all paper assets across task folders, compares them against the
provided paper metadata (title, authors, DOI, year), and reports
matches above a configurable similarity threshold.

Matching heuristics:
  - DOI exact match (after normalization) → definitive duplicate
  - Title similarity via SequenceMatcher (normalized)
  - Author set overlap (order-independent, last-name based)
  - Year proximity (exact or ±1)
"""

import argparse
import re
import sys
import unicodedata
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path

from pydantic import ValidationError

from arf.scripts.utils.doi_to_slug import doi_to_slug
from arf.scripts.verificators.common.paths import (
    TASKS_DIR,
    paper_base_dir,
    paper_details_path,
)
from meta.asset_types.paper.aggregator import PaperDetailsModel

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_THRESHOLD: float = 0.5

# Weights for combined score (when no DOI match)
TITLE_WEIGHT: float = 0.60
AUTHOR_WEIGHT: float = 0.30
YEAR_WEIGHT: float = 0.10

# Punctuation and whitespace normalization
_NON_ALNUM_PATTERN: re.Pattern[str] = re.compile(r"[^a-z0-9\s]")
_WHITESPACE_PATTERN: re.Pattern[str] = re.compile(r"\s+")

# Common name prefixes/particles to strip for last-name extraction
_NAME_PARTICLES: set[str] = {
    "de",
    "del",
    "della",
    "di",
    "van",
    "von",
    "le",
    "la",
    "el",
    "al",
    "bin",
    "ibn",
    "abu",
    "dos",
    "das",
    "do",
    "da",
}


# ---------------------------------------------------------------------------
# Internal data types
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class PaperMatch:
    paper_id: str
    title: str
    year: int
    authors: list[str]
    task_id: str | None
    doi: str | None
    overall_score: float
    doi_match: bool
    title_score: float
    author_score: float
    year_score: float


@dataclass(frozen=True, slots=True)
class _ExistingPaper:
    paper_id: str
    title: str
    year: int
    author_names: list[str]
    doi: str | None
    task_id: str | None


# ---------------------------------------------------------------------------
# Normalization helpers
# ---------------------------------------------------------------------------


def _normalize_title(*, title: str) -> str:
    """Lowercase, strip accents, remove punctuation, collapse whitespace."""
    lowered: str = title.lower().strip()
    # Decompose Unicode and strip combining marks (accents)
    nfkd: str = unicodedata.normalize("NFKD", lowered)
    stripped: str = "".join(ch for ch in nfkd if not unicodedata.combining(ch))
    no_punct: str = _NON_ALNUM_PATTERN.sub(" ", stripped)
    collapsed: str = _WHITESPACE_PATTERN.sub(" ", no_punct).strip()
    return collapsed


def _normalize_doi(*, doi: str) -> str:
    """Normalize a DOI to its slug form for comparison."""
    try:
        return doi_to_slug(doi=doi).lower()
    except ValueError:
        return doi.strip().lower().replace("/", "_")


def _extract_last_name(*, full_name: str) -> str:
    """Extract and normalize the last name from a full name.

    Handles "First Last", "Last, First", and name particles.
    """
    name: str = full_name.strip()
    if len(name) == 0:
        return ""

    # Handle "Last, First" format
    if "," in name:
        last: str = name.split(",")[0].strip()
    else:
        parts: list[str] = name.split()
        # Walk backwards past particles to find the real last name
        last = parts[-1]
        idx: int = len(parts) - 1
        while idx > 0 and parts[idx].lower() in _NAME_PARTICLES:
            idx -= 1
            last = parts[idx]

    # Normalize: lowercase, strip accents
    lowered: str = last.lower()
    nfkd: str = unicodedata.normalize("NFKD", lowered)
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch))


# ---------------------------------------------------------------------------
# Similarity functions
# ---------------------------------------------------------------------------


def _title_similarity(*, query: str, candidate: str) -> float:
    """Normalized title similarity using SequenceMatcher."""
    norm_query: str = _normalize_title(title=query)
    norm_candidate: str = _normalize_title(title=candidate)
    if norm_query == norm_candidate:
        return 1.0
    if len(norm_query) == 0 or len(norm_candidate) == 0:
        return 0.0
    return SequenceMatcher(
        a=norm_query,
        b=norm_candidate,
    ).ratio()


def _author_similarity(
    *,
    query_authors: list[str],
    candidate_authors: list[str],
) -> float:
    """Order-independent author similarity based on last-name overlap.

    Uses the overlap coefficient: |intersection| / min(|A|, |B|).
    This handles cases where one list is a subset of the other
    (e.g., a shorter author list that omits some contributors).
    """
    if len(query_authors) == 0 or len(candidate_authors) == 0:
        return 0.0

    query_last_names: set[str] = {_extract_last_name(full_name=name) for name in query_authors}
    candidate_last_names: set[str] = {
        _extract_last_name(full_name=name) for name in candidate_authors
    }

    # Remove empty strings from failed extractions
    query_last_names.discard("")
    candidate_last_names.discard("")

    if len(query_last_names) == 0 or len(candidate_last_names) == 0:
        return 0.0

    intersection_size: int = len(
        query_last_names & candidate_last_names,
    )
    min_size: int = min(len(query_last_names), len(candidate_last_names))

    return intersection_size / min_size


def _year_similarity(*, query_year: int, candidate_year: int) -> float:
    """Year proximity: 1.0 for exact, 0.5 for ±1, 0.0 otherwise."""
    diff: int = abs(query_year - candidate_year)
    if diff == 0:
        return 1.0
    if diff == 1:
        return 0.5
    return 0.0


def _doi_matches(*, query_doi: str, candidate_doi: str) -> bool:
    """Check if two DOIs refer to the same paper after normalization."""
    return _normalize_doi(doi=query_doi) == _normalize_doi(doi=candidate_doi)


# ---------------------------------------------------------------------------
# Discovery and loading
# ---------------------------------------------------------------------------


def _discover_existing_papers() -> list[_ExistingPaper]:
    """Scan all task folders and top-level assets for paper details."""
    seen: set[str] = set()
    papers: list[_ExistingPaper] = []

    # Scan tasks/*/assets/paper/
    if TASKS_DIR.exists():
        for task_dir in sorted(TASKS_DIR.iterdir()):
            if not task_dir.is_dir() or task_dir.name.startswith("."):
                continue
            base: Path = paper_base_dir(task_id=task_dir.name)
            if not base.exists():
                continue
            for paper_dir in sorted(base.iterdir()):
                if (
                    paper_dir.is_dir()
                    and not paper_dir.name.startswith(".")
                    and paper_dir.name not in seen
                ):
                    seen.add(paper_dir.name)
                    loaded: _ExistingPaper | None = _load_paper(
                        paper_id=paper_dir.name,
                        task_id=task_dir.name,
                    )
                    if loaded is not None:
                        papers.append(loaded)

    # Scan top-level assets/paper/
    top_level: Path = paper_base_dir(task_id=None)
    if top_level.exists():
        for paper_dir in sorted(top_level.iterdir()):
            if (
                paper_dir.is_dir()
                and not paper_dir.name.startswith(".")
                and paper_dir.name not in seen
            ):
                seen.add(paper_dir.name)
                loaded = _load_paper(
                    paper_id=paper_dir.name,
                    task_id=None,
                )
                if loaded is not None:
                    papers.append(loaded)

    return papers


def _load_paper(
    *,
    paper_id: str,
    task_id: str | None,
) -> _ExistingPaper | None:
    file_path: Path = paper_details_path(
        paper_id=paper_id,
        task_id=task_id,
    )
    if not file_path.exists():
        return None
    try:
        raw: str = file_path.read_text(encoding="utf-8")
        details: PaperDetailsModel = PaperDetailsModel.model_validate_json(
            raw,
        )
        return _ExistingPaper(
            paper_id=details.paper_id,
            title=details.title,
            year=details.year,
            author_names=[a.name for a in details.authors],
            doi=details.doi,
            task_id=task_id,
        )
    except (OSError, UnicodeDecodeError, ValidationError):
        return None


# ---------------------------------------------------------------------------
# Core matching logic
# ---------------------------------------------------------------------------


def find_similar_papers(
    *,
    title: str,
    authors: list[str] | None = None,
    doi: str | None = None,
    year: int | None = None,
    threshold: float = DEFAULT_THRESHOLD,
) -> list[PaperMatch]:
    """Find existing papers that are similar to the given metadata.

    Returns matches sorted by overall_score descending, filtered to
    those at or above the threshold.
    """
    existing: list[_ExistingPaper] = _discover_existing_papers()
    query_authors: list[str] = authors if authors is not None else []
    matches: list[PaperMatch] = []

    for paper in existing:
        # Check DOI first — definitive match
        is_doi_match: bool = False
        if doi is not None and paper.doi is not None:
            is_doi_match = _doi_matches(
                query_doi=doi,
                candidate_doi=paper.doi,
            )

        title_score: float = _title_similarity(
            query=title,
            candidate=paper.title,
        )
        author_score: float = _author_similarity(
            query_authors=query_authors,
            candidate_authors=paper.author_names,
        )
        year_score: float = 0.0
        if year is not None:
            year_score = _year_similarity(
                query_year=year,
                candidate_year=paper.year,
            )

        # DOI match is definitive
        if is_doi_match:
            overall: float = 1.0
        else:
            overall = (
                TITLE_WEIGHT * title_score + AUTHOR_WEIGHT * author_score + YEAR_WEIGHT * year_score
            )

        if overall >= threshold:
            matches.append(
                PaperMatch(
                    paper_id=paper.paper_id,
                    title=paper.title,
                    year=paper.year,
                    authors=paper.author_names,
                    task_id=paper.task_id,
                    doi=paper.doi,
                    overall_score=overall,
                    doi_match=is_doi_match,
                    title_score=title_score,
                    author_score=author_score,
                    year_score=year_score,
                ),
            )

    matches.sort(key=lambda m: m.overall_score, reverse=True)
    return matches


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------


def _format_match(*, match: PaperMatch, rank: int) -> str:
    lines: list[str] = []
    label: str = "DOI MATCH" if match.doi_match else "SIMILAR"
    lines.append(
        f"  [{rank}] {label} (score: {match.overall_score:.2f}) — {match.paper_id}",
    )
    lines.append(f"      Title:   {match.title}")
    lines.append(f"      Authors: {', '.join(match.authors)}")
    lines.append(f"      Year:    {match.year}")
    if match.doi is not None:
        lines.append(f"      DOI:     {match.doi}")
    if match.task_id is not None:
        lines.append(f"      Task:    {match.task_id}")
    lines.append(
        f"      Scores:  title={match.title_score:.2f}"
        f"  authors={match.author_score:.2f}"
        f"  year={match.year_score:.2f}",
    )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description=(
            "Find existing paper assets similar to a given paper. "
            "Reports matches above a similarity threshold."
        ),
    )
    parser.add_argument(
        "--title",
        required=True,
        help="Paper title to search for",
    )
    parser.add_argument(
        "--authors",
        nargs="*",
        default=None,
        help='Author names (e.g., --authors "John Smith" "Jane Doe")',
    )
    parser.add_argument(
        "--doi",
        default=None,
        help="DOI of the paper (e.g., 10.18653/v1/E17-1010)",
    )
    parser.add_argument(
        "--year",
        type=int,
        default=None,
        help="Publication year",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_THRESHOLD,
        help=f"Minimum similarity score to report (default: {DEFAULT_THRESHOLD})",
    )
    args: argparse.Namespace = parser.parse_args()

    matches: list[PaperMatch] = find_similar_papers(
        title=args.title,
        authors=args.authors,
        doi=args.doi,
        year=args.year,
        threshold=args.threshold,
    )

    if len(matches) == 0:
        print("No similar papers found.")
        sys.exit(0)

    print(f"Found {len(matches)} similar paper(s):\n")
    for rank, match in enumerate(matches, start=1):
        print(_format_match(match=match, rank=rank))
        print()

    sys.exit(0)


if __name__ == "__main__":
    main()
