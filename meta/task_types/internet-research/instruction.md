# Internet Research Instructions

## Planning Guidelines

* Define the research question precisely before starting any searches. A well-scoped
  question prevents rabbit holes and unfocused browsing.
* List 3-5 specific search queries you plan to use, covering different angles of the
  question (synonyms, related terms, specific tools).
* Identify which types of sources are most relevant: official docs, academic papers,
  blog posts, GitHub repos, forum threads.
* Set a time budget. Internet research expands to fill available time without a clear
  stopping criterion.

## Implementation Guidelines

* Start with broad searches to understand the landscape, then narrow to specific
  subtopics identified in the initial pass.
* Record every source URL immediately when you find useful information. Reconstructing
  sources after the fact is unreliable and wastes time.
* For each source, note: URL, date accessed, author/organization, and a one-sentence
  summary of what it contributes to the research question.
* Cross-reference claims across multiple independent sources. A single blog post is not
  sufficient evidence for factual claims.
* Write findings into `research/research_internet.md` incrementally as you discover
  them, not in a single pass at the end.
* Structure the output document by subtopic, not by source. Group related findings
  together even if they came from different searches.
* Include direct quotes with attribution for key claims. Paraphrasing without citation
  is not acceptable.

## Common Pitfalls

* **Not documenting sources**: Every claim must have a URL. Unsourced claims are
  indistinguishable from hallucinations and will be flagged during review.
* **Search tunnel vision**: Using only one search query or one type of source misses
  important perspectives. Vary your queries and check official docs, forums, and
  independent benchmarks.
* **Not verifying claims**: Blog posts and forum answers may be outdated or wrong.
  Cross-check version numbers, API availability, and benchmark results against official
  documentation.
* **Summarizing without synthesizing**: Listing what each source says is not research.
  Synthesize findings into actionable conclusions that answer the original research
  question.
* **Ignoring recency**: Check publication dates. A 2020 comparison of tools may be
  irrelevant if major releases happened since then.

## Verification Additions

* Confirm `research/research_internet.md` exists and exceeds 500 words.
* Every factual claim has an inline citation with a URL.
* The document contains a clear answer or conclusion addressing the original research
  question, not just a collection of notes.
* At least 3 independent sources are cited.

## Related Skills

* `/research-internet` — primary skill for conducting internet research
