# Literature Survey Instructions

## Planning Guidelines

* Define the search scope: topic keywords, year range, venues to prioritize.
* Set a target number of papers to find (minimum and maximum).
* Plan the search strategy: which databases to query (Semantic Scholar, Google Scholar, ACL
  Anthology, arXiv), which keyword combinations to use.
* Check existing paper assets by running `aggregate_papers.py` to avoid downloading papers already
  in the project.

## Implementation Guidelines

* Use the `/research-internet` skill to discover papers systematically.
* Use the `/add-paper` skill for each paper to create properly structured paper assets with
  `details.json` and the canonical summary document.
* Use the `/download_paper` skill to obtain PDF files when available.
* Organize discovered papers by theme or category. Assign appropriate categories from
  `meta/categories/` to each paper.
* Produce a synthesis document in `results/results_summary.md` that organizes findings by theme,
  identifies gaps in the literature, and highlights consensus vs. disagreement across papers.
* **NEVER fabricate citations.** Every paper referenced must have a corresponding paper asset with
  verifiable metadata. If a paper cannot be found or verified, do not include it.
* For each paper, read the full text before writing the summary. Abstract-only summaries are
  acceptable only when download fails (mark this explicitly).

## Common Pitfalls

* **Citation fabrication**: This is the most critical risk. Never invent paper titles, authors, or
  DOIs. Every claim must trace to a real, downloaded paper.
* **Shallow coverage**: Searching only one database or one keyword combination misses relevant work.
  Use at least 3 different search queries.
* **Missing synthesis**: A list of paper summaries is not a survey. The results must include a
  synthesis that identifies themes, trends, and gaps.
* **Duplicate papers**: Check the aggregated paper list before adding each paper. The same paper may
  appear under different titles or URLs.

## Verification Additions

* Confirm each paper asset passes the paper verificator with no errors.
* Confirm `results/results_summary.md` contains a synthesis section that goes beyond listing
  individual papers.
* Confirm no paper is duplicated against the existing aggregated paper list.
* Confirm every citation in the synthesis traces to an actual paper asset.

## Related Skills

* `/research-internet` — systematic web search for papers
* `/research-papers` — review papers already in the project
* `/add-paper` — create structured paper assets
* `/download_paper` — download PDF files for discovered papers
