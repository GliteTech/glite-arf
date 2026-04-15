# Answer Question Instructions

## Planning Guidelines

* Define the exact question or list of questions before planning the work. The question text must be
  stable enough to become the canonical text in `assets/answer/`.
* Plan for one answer asset per question. If the task covers multiple questions, list every planned
  `answer_id` explicitly.
* Decide which evidence channels are needed: existing papers, internet sources, prior project
  assets, new code experiments, or a combination.
* The plan must name the expected source types and the stopping criterion for the research.
  Question-answering tasks expand indefinitely if "enough evidence" is not defined.
* The plan must identify what would count as insufficient evidence and how uncertainty will be
  reported in the final answer.

## Implementation Guidelines

* Treat the question as the core deliverable, not as background context. Every action during
  implementation should improve the evidence base for the answer.
* Create one answer asset per question under `assets/answer/<answer_id>/`. Set `short_answer_path`
  and `full_answer_path` in `details.json` to the canonical answer document paths.
* Write the canonical short answer document only after the evidence is stable. It must answer the
  question directly in 2-5 sentences and identify the evidence basis.
* **Answer style**: Write in a direct, authoritative tone. State the conclusion first, then the
  supporting reason. If the question is yes/no, begin the answer with "Yes", "No", or "I don't
  know". No evasive language, hedging, filler, or diplomatic softening.
* **No inline citations in short answers**: The `## Answer` section in the canonical short answer
  document and the `## Short Answer` section in the canonical full answer document must never
  contain bracketed references like `[AuthorYear]` or `[tNNNN]`. All citations belong in
  `## Sources`.
* Write the canonical full answer document as a mini-paper: explain the research process, summarize
  evidence by source type, synthesize the conclusion, and state limitations clearly.
* **Reference links**: The `## Sources` section in the canonical full answer document must include
  markdown reference link definitions so that inline citations in the body sections render as
  clickable links on GitHub. See the answer asset specification for the exact format.
* If code experiments are needed, create reproducible scripts in `code/` and reference them
  explicitly in the `## Evidence from Code or Experiments` section.
* When evidence conflicts, state the conflict instead of forcing a false certainty. Confidence
  should reflect the strength of the evidence, not the agent's preference.

## Common Pitfalls

* **Answering vaguely**: The short answer must actually answer the question, not merely restate the
  question or summarize background context. Be direct and decisive — no "maybe", "perhaps", or "it
  depends" unless factually required.
* **Using inline citations in short answers**: `[AuthorYear]` and `[tNNNN]` brackets must not appear
  in the `## Answer` or `## Short Answer` sections. Citations belong exclusively in `## Sources`.
* **Losing source traceability**: Every answer must name the concrete supporting paper IDs, URLs,
  and task IDs. Unsourced conclusions are not acceptable.
* **Skipping negative evidence**: If an experiment failed or a source contradicted the emerging
  answer, include that in the full answer. Omitting it weakens the audit trail.
* **Bundling multiple questions into one asset**: Keep one question per answer asset so aggregators
  and overview pages remain clear.

## Verification Additions

* Confirm every answer asset passes `verify_answer_asset.py`.
* Confirm the canonical short answer document contains an `## Answer` section with 2-5 sentences.
* Confirm the canonical full answer document lists all cited paper IDs, task IDs, and URLs in
  `## Sources`.
* Confirm the evidence sections used by the task are substantive and match `details.json`
  `answer_methods`.

## Related Skills

* `/research-papers` — review already-downloaded papers relevant to the question
* `/research-internet` — search for documentation and external sources
* `/research-code` — review prior task findings, code, and assets
* `/planning` — define the evidence plan and output answer assets
* `/implementation` — run experiments, create answer assets, and verify them
