---
spec_version: "2"
task_id: "t0003_simulator_library_survey"
date_completed: "2026-04-19"
status: "complete"
---
# Plan: Simulator library survey for DSGC compartmental modelling

## Objective

Synthesize the already-collected internet research into one answer asset under `assets/answer/` that
recommends a primary simulator plus one backup for the project's direction-selective ganglion cell
(DSGC) compartmental modelling work, and that includes a complete five-axis comparison table
covering NEURON, NetPyNE, Brian2, MOOSE, and Arbor. "Done" means a single answer asset exists in
`tasks/t0003_simulator_library_survey/assets/answer/<answer_id>/`, contains the required short and
full answer documents, passes `verify_answer_asset.py` with zero errors, states the primary and
backup simulator in one or two sentences in its `## Answer` block, and embeds the five-axis
comparison table (cable-model fidelity, Python ergonomics, speed/parallelism, DSGC/RGC examples
available, long-term maintenance) with one row per candidate library.

## Task Requirement Checklist

The operative task text quoted verbatim from
`tasks/t0003_simulator_library_survey/task_description.md`:

> # Simulator library survey for DSGC compartmental modelling

> ## Motivation

> `project/description.md` mentions NEURON as the canonical simulator but the researcher wants to
> evaluate several libraries before committing. A bad simulator choice locks the project into poor
> cable-model fidelity, slow parameter sweeps, or brittle tooling for months. A short survey up
> front prevents this.
>
> ## Scope

> Evaluate the following candidate libraries:
>
> * NEURON (plus NEURON+Python bindings)
> * NetPyNE (higher-level NEURON wrapper)
> * Brian2 with cable-model extensions
> * MOOSE
> * Arbor
>
> For each library, collect:
>
> 1. **Cable-model fidelity** — does it solve the full compartmental cable equation, support
>    voltage-gated conductances in arbitrary compartments, and handle reconstructed morphologies
>    (SWC, HOC, NeuroML)?
> 2. **Python ergonomics** — pure Python vs wrapped C++/MOD files, packaging on `uv`, quality of
>    current documentation and examples.
> 3. **Speed and parallelism** — single-cell simulation speed and support for running large
>    parameter sweeps.
> 4. **DSGC examples available** — whether any published DSGC or broader RGC compartmental model has
>    been released in that library.
> 5. **Long-term maintenance** — last release, community activity, active maintainers.
>
> ## Approach

> 1. Run `/research-internet` to gather documentation, benchmarks, and user reports for each
>    library.
> 2. Build a comparison table covering the five axes above.
> 3. Produce a single answer asset that recommends a **primary** simulator plus one **backup**, with
>    explicit rationale.
>
> ## Expected Outputs

> * One answer asset under `assets/answer/` summarising the library comparison and stating the
>   primary plus backup recommendation.
>
> ## Compute and Budget

> No external cost. Local LLM CLI and internet search only.
>
> ## Dependencies

> None. Runs in parallel with t0002 and t0004.
>
> ## Verification Criteria

> * The answer asset passes `verify_answer_asset.py`.
> * The `## Answer` section states the primary and backup simulator in one or two sentences.
> * The full answer includes the five-axis comparison table for every candidate library.

Concrete requirements extracted from the quoted text:

* **REQ-1**: Evaluate NEURON (including Python bindings) on all five axes. Satisfied by the NEURON
  row of the comparison table built in Step 3 and the NEURON paragraphs in `full_answer.md` produced
  by Step 4. Evidence: the NEURON row exists and cites `research_internet.md` findings.
* **REQ-2**: Evaluate NetPyNE on all five axes. Satisfied by the NetPyNE row of the comparison table
  built in Step 3 and NetPyNE paragraphs in `full_answer.md` produced by Step 4.
* **REQ-3**: Evaluate Brian2 with cable-model extensions on all five axes. Satisfied by the Brian2
  row of the comparison table (Step 3) and the Brian2 paragraphs in `full_answer.md` (Step 4).
* **REQ-4**: Evaluate MOOSE on all five axes. Satisfied by the MOOSE row of the comparison table
  (Step 3) and the MOOSE paragraphs in `full_answer.md` (Step 4).
* **REQ-5**: Evaluate Arbor on all five axes. Satisfied by the Arbor row of the comparison table
  (Step 3) and the Arbor paragraphs in `full_answer.md` (Step 4).
* **REQ-6**: For each library, report cable-model fidelity (full compartmental cable equation,
  voltage-gated conductances in arbitrary compartments, SWC/HOC/NeuroML morphology support).
  Satisfied by the "Cable-model fidelity" column in the Step 3 table and the "Cable-model fidelity"
  sub-section of Step 4's full answer.
* **REQ-7**: For each library, report Python ergonomics (pure Python vs wrapped C++/MOD, pip/`uv`
  packaging, documentation quality). Satisfied by the "Python ergonomics" column in the Step 3 table
  and Step 4 sub-section.
* **REQ-8**: For each library, report speed and parallelism (single-cell speed, parameter sweep
  support). Satisfied by the "Speed & parallelism" column in the Step 3 table and Step 4
  sub-section.
* **REQ-9**: For each library, report whether any published DSGC or broader RGC compartmental model
  has been released in that library. Satisfied by the "DSGC/RGC examples" column in the Step 3 table
  and Step 4 sub-section.
* **REQ-10**: For each library, report long-term maintenance (last release, community activity,
  active maintainers). Satisfied by the "Long-term maintenance" column in the Step 3 table and Step
  4 sub-section.
* **REQ-11**: Produce a single markdown five-axis comparison table with one row per library and one
  column per axis. Satisfied by Step 3 and embedded verbatim in `full_answer.md` by Step 4.
* **REQ-12**: Produce exactly one answer asset under `assets/answer/` (count must match `task.json`
  `expected_assets.answer = 1`). Satisfied by Step 2 creating the folder and Step 5 writing
  `details.json`.
* **REQ-13**: Recommend a primary simulator and a backup simulator with explicit rationale.
  Satisfied by Step 4's `## Answer` and `## Synthesis` sections, which both state the primary and
  backup plus the rationale drawn from the five-axis comparison.
* **REQ-14**: The answer asset passes `verify_answer_asset.py` with zero errors. Satisfied by Step 6
  running the verificator and fixing anything it flags.
* **REQ-15**: The `## Answer` section states the primary and backup simulator in one or two
  sentences. Satisfied by Step 4 enforcing the sentence count while drafting the short answer.
* **REQ-16**: The full answer document includes the five-axis comparison table for every candidate
  library. Satisfied by Step 4 embedding the Step 3 table verbatim into `full_answer.md` under the
  `## Synthesis` section.
* **REQ-17**: Respect the "no external cost" constraint from the task. Satisfied by keeping
  implementation to local markdown authoring plus CLI verification — no paid APIs, no remote
  compute.

## Approach

The work is answer-asset authoring built on top of the research already in
`tasks/t0003_simulator_library_survey/research/research_internet.md`. The research file has already
resolved all five evaluation axes for all five libraries (see its "Gaps Addressed" and "Key
Findings" sections), so this plan does not need to conduct fresh searches. The plan's job is to
translate that research into the canonical answer-asset format defined by
`meta/asset_types/answer/specification.md`.

Key research findings that drive the recommendation (quoted compactly from `research_internet.md` so
the implementation agent need not re-read that file):

* NEURON ships pip wheels (Python 3.9-3.13 via 8.2.7; Python 3.14 via 9.0.1), has the largest
  published-model ecosystem, is the only simulator with a public DSGC model (ModelDB 189347,
  Poleg-Polsky & Diamond 2016 — aligns with project DSGC scope), and shows strong 2025 release
  cadence (8.2.7 May 2025, 9.0.0 Sep 2025, 9.0.1 Nov 2025). CoreNEURON gives 30-52x GPU speedups on
  large networks.
* Arbor is measured 7-12x faster than NEURON on single morphologically-detailed cells and 5-8x
  faster on MPI-parallel networks; pip wheel via `pip install arbor`; v0.12.0 released 17 Apr 2025;
  uses a stricter NMODL dialect (`modcc`) so MOD-file ports from NEURON cost several days of
  translation.
* NetPyNE wraps NEURON and provides the most ergonomic parameter-sweep layer across all five
  candidates (`Batch` class with Optuna and inspyred backends); v1.1.1 released 14 Sep 2025;
  requires NEURON to be pip-installed first.
* Brian2's own authors describe multicompartment support as "not yet as mature" as NEURON
  [Stimberg2019], and multicompartment code generation is restricted to the C++ standalone target
  [Brian2-MC-Docs]. No public DSGC model in Brian2.
* MOOSE shows the weakest maintenance signal (22 GitHub stars, single-lab maintenance, latest tag
  chamcham 3.1.x with no year visible on the release page surfaced), no public DSGC model, and no
  built-in batch/sweep layer.

**Recommendation embedded in the plan**: primary = NEURON 8.2.7 (with NetPyNE 1.1.1 for the
optimisation/sweep stage); backup = Arbor 0.12.0. Reject Brian2 and MOOSE. This matches the
"Recommendations for This Task" section of `research_internet.md` verbatim.

**Alternatives considered and rejected**:

* *Alternative 1 — pick Arbor as primary because it is 7-12x faster.* Rejected because the only
  public DSGC reference implementation (ModelDB 189347) is in NEURON, and Arbor's stricter NMODL
  dialect adds several days of MOD-file translation before any Arbor speedup is realisable. With the
  project's modest expected sweep size (~200 parameter combinations on a single cell), NEURON
  + NetPyNE Batch + 8 MPI ranks on one workstation is expected to finish in under 8 hours —
    CoreNEURON+GPU or Arbor is overkill at this scale.
* *Alternative 2 — produce one answer asset per library (five assets total) instead of one
  consolidated answer.* Rejected because `task.json` `expected_assets.answer = 1` and the task
  description explicitly says "one answer asset". Splitting would violate both REQ-12 and the
  `expected_assets` contract.
* *Alternative 3 — build a CSV/JSON machine-readable comparison instead of a markdown table.*
  Rejected because the answer-asset specification prescribes markdown documents (`short_answer.md`
  and `full_answer.md`) as the canonical artefacts, and the task's verification criterion explicitly
  asks for the comparison table to appear in the full answer document.

**Task type**: `internet-research` (already declared in `task.json.task_types`). The Planning
Guidelines from `meta/task_types/internet-research/instruction.md` emphasise writing one concluding
answer to the research question and citing every factual claim with a URL — both requirements are
met by routing every table-cell fact through a reference link to one of the 20 citations already
indexed in `research_internet.md`. Because the research stage is complete, this plan's
implementation work is the "produce the concluding answer" phase that the task-type guidelines
describe.

**Registered metrics applicability**: The four registered metrics (`direction_selectivity_index`,
`tuning_curve_hwhm_deg`, `tuning_curve_reliability`, `tuning_curve_rmse`) all measure output of a
running DSGC simulation. This task does not run a simulation — it selects which simulator to use —
so **no registered metric applies** and `results/metrics.json` will contain an empty measurement
set. This omission is deliberate, not accidental.

## Cost Estimation

Total: **$0.00 USD**.

* **Paid APIs**: $0.00 — no paid LLM inference. Claude CLI is used locally; no OpenAI, Anthropic
  API, or other external paid service is invoked.
* **Remote compute**: $0.00 — no GPU, no cloud instance, no Vast.ai. All work is markdown authoring
  plus Python verificator runs on the local workstation.
* **Data transfer**: $0.00 — the research is already on disk in `research/research_internet.md`; no
  additional downloads are triggered.

`project/budget.json` reports `total_budget = 0.0 USD` and `per_task_default_limit = 0.0 USD` with
`available_services = []`. The estimate sits exactly at the per-task limit ($0.00 ≤ $0.00), so the
task is within budget.

## Step by Step

The implementation agent must execute the steps in order. Every command line call must be wrapped in
`uv run python -u -m arf.scripts.utils.run_with_logs --task-id t0003_simulator_library_survey -- <command>`
on Windows bash with `export PATH="/c/Users/md1avn/.local/bin:/c/Program Files/GitHub CLI:$PATH"`
prepended. File paths are relative to the worktree root
`C:/Users/md1avn/Documents/GitHub/neuron-channels-worktrees/t0003_simulator_library_survey/`.

### Milestone A — Preparation

1. **Re-read the research evidence.** Open
   `tasks/t0003_simulator_library_survey/research/research_internet.md` and identify the exact
   citation keys used per axis per library. The file's `## Source Index` lists the 20 canonical
   citation keys: `Awile2022`, `Stimberg2019`, `Plastic-Arbor-2026`, `Schachter2010`,
   `ModelDB-189347`, `NEURON-Changelog`, `NEURON-Py313-Issue`, `Arbor-Releases`,
   `Arbor-Install-Doc`, `Arbor-RTD-2025`, `Arbor-NMODL-Doc`, `NetPyNE-Doc`, `NetPyNE-GH`,
   `Brian2-MC-Docs`, `Brian2-GH`, `MOOSE-GH`, `MOOSE-Releases`, `MOOSE-Rdes-Doc`, `jzlab-DSG-GH`,
   `Berens-RGC-GH`. Produce no output file from this step — it is a read-only warm-up. Expected
   observable: the agent can name, without re-opening the file, which library each citation key
   supports. Satisfies REQ-1 through REQ-10 (as information grounding).

2. **Create the answer asset folder skeleton.** The canonical answer ID is
   `dsgc-compartmental-simulator-choice` (lowercase, hyphenated, derived from the task's core
   question "which compartmental simulator should we use for DSGC modelling?"). Create the folder
   `tasks/t0003_simulator_library_survey/assets/answer/dsgc-compartmental-simulator-choice/`. Inside
   it, create three placeholder files: `details.json`, `short_answer.md`, `full_answer.md` — they
   will be filled in later steps. Expected observable: `ls` on the folder returns exactly those
   three filenames. Satisfies REQ-12.

### Milestone B — Comparison Table

3. **Draft the five-axis comparison table.** Create the table below as an intermediate working
   artefact; it will be embedded verbatim into `full_answer.md` in Step 4. The columns are exactly
   the five axes from the task description (in the order the task lists them); the rows are the five
   libraries (in the order the task lists them). Each cell is one or two information-dense sentences
   with an inline citation using the keys from Step 1. The table must be a single-line-per-row
   markdown table (per `arf/styleguide/markdown_styleguide.md` — "Never split a table cell across
   multiple lines"); rows may exceed 100 characters because table rows are exempt from the
   line-length limit.

   Required table content per row (paraphrased from `research_internet.md`; implementation agent
   rewrites faithfully into the table format):

   * **NEURON** — Cable-model fidelity: full cable equation, voltage-gated channels in any
     compartment via MOD files, loads SWC/HOC/NeuroML [NEURON-Changelog, Awile2022]. Python
     ergonomics: pip wheel `neuron` supporting Python 3.9-3.13 in 8.2.7 and Python 3.14 in 9.0.1;
     MOD files still require `nrnivmodl`; `uv pip install neuron` works
     [Awile2022, NEURON-Py313-Issue]. Speed & parallelism: single-cell baseline; CoreNEURON gives
     30-52x on GPU for large networks [Awile2022]. DSGC/RGC examples: **yes** — ModelDB 189347
     Poleg-Polsky & Diamond 2016 is in NEURON [ModelDB-189347]. Long-term maintenance: 8.2.7 (May
     2025), 9.0.0 (Sep 2025), 9.0.1 (Nov 2025); BlueBrain+Yale/Duke co-maintained, CI modernised
     [NEURON-Changelog, Awile2022].

   * **NetPyNE** — Cable-model fidelity: identical to NEURON because it wraps NEURON's solver
     [NetPyNE-Doc]. Python ergonomics: pure-Python model description on top of NEURON; pip wheel
     `netpyne` v1.1.1 but NEURON must be installed first [NetPyNE-Doc, NetPyNE-GH]. Speed &
     parallelism: inherits NEURON MPI; **adds `Batch` class with Optuna and inspyred backends — the
     most ergonomic sweep layer among all five candidates** [NetPyNE-Doc]. DSGC/RGC examples: no
     native DSGC model but inherits ModelDB access through its NEURON base. Long- term maintenance:
     v1.1.1 released 14 Sep 2025, 169 GitHub stars, active forum [NetPyNE-GH].

   * **Brian2** — Cable-model fidelity: `SpatialNeuron` discretises the cable equation and reads SWC
     morphologies, but the Brian2 authors themselves state multicompartment is "not yet as mature as
     NEURON and GENESIS" [Stimberg2019]; multicompartment code generation is restricted to the C++
     standalone target (no GPU/Cython path) [Brian2-MC-Docs]. Python ergonomics: fully pure-Python
     via equation strings, pip wheel `brian2` 2.10.x [Brian2-GH]. Speed & parallelism: fastest on
     point-neuron CUBA networks but behind NEURON/Arbor on multicompartment [Stimberg2019]. DSGC/RGC
     examples: **no** — no public DSGC Brian2 model found by 16 search queries. Long-term
     maintenance: 1.2k GitHub stars, 176 open issues, 29 open PRs, **no GitHub release tags**
     (unusual) [Brian2-GH].

   * **MOOSE** — Cable-model fidelity: `rdesigneur` loads SWC morphologies and distributes HH
     channels via `chanDistrib` directives, supports multiscale (electrical + biochemical) coupling
     [MOOSE-Rdes-Doc]. Python ergonomics: partial PyPI distribution — pip is not the primary path
     [MOOSE-GH]. Speed & parallelism: no built-in batch driver, sweeps are Python loops around
     `buildModel()` [MOOSE-Rdes-Doc]. DSGC/RGC examples: **no** — no public DSGC MOOSE model found.
     Long-term maintenance: **weakest signal** — 22 GitHub stars, single lab (BhallaLab at NCBS)
     maintains, latest visible tag is chamcham 3.1.x with no year on the release page surfaced
     [MOOSE-GH, MOOSE-Releases].

   * **Arbor** — Cable-model fidelity: full cable equation, NMODL-defined channels via `modcc`
     compiler (stricter dialect than NEURON — `PARAMETER` vs `ASSIGNED` distinction matters and not
     every NEURON MOD file ports without edits) [Arbor-NMODL-Doc]. Python ergonomics: pip wheel
     `arbor` for Python 3.7+, v0.12.0 released 17 Apr 2025 [Arbor-Install-Doc, Arbor-Releases].
     Speed & parallelism: **7-12x faster than NEURON on single morphologically-detailed cells**
     [Plastic-Arbor-2026]; 5-8x faster than NEURON on MPI-parallel networks, doubling under
     HPC-tuned distribution [Arbor-RTD-2025]. DSGC/RGC examples: **no** — no public Arbor DSGC
     model. Long-term maintenance: active cadence v0.10.0 (Aug 2024), v0.11.0 (Apr 2024 backport),
     v0.12.0 (Apr 2025) [Arbor-Releases].

   Expected observable: a single markdown table drafted in the implementation agent's scratch
   context with exactly 5 rows (one per library) and 5 data columns (one per axis), plus the leading
   library-name column. Satisfies REQ-1, REQ-2, REQ-3, REQ-4, REQ-5, REQ-6, REQ-7, REQ-8, REQ-9,
   REQ-10, REQ-11.

### Milestone C — Answer Documents

4. **Write `full_answer.md`.** Create
   `tasks/t0003_simulator_library_survey/assets/answer/dsgc-compartmental-simulator-choice/full_answer.md`
   conforming to the "Full Answer Document" section of `meta/asset_types/answer/specification.md`.
   Structure:

   * YAML frontmatter with `spec_version: "2"`, `answer_id: "dsgc-compartmental-simulator-choice"`,
     `answered_by_task: "t0003_simulator_library_survey"`, `date_answered: "2026-04-19"`,
     `confidence: "high"`.
   * `## Question` — "Which compartmental simulator should the direction-selective ganglion cell
     (DSGC) project use as its primary simulator, and which should it keep as a backup?" (must match
     the `question` field in `details.json` verbatim — the verificator normalizes whitespace before
     comparing).
   * `## Short Answer` — 2-5 sentences. Must state: primary = NEURON 8.2.7 (with NetPyNE 1.1.1 for
     parameter sweeps); backup = Arbor 0.12.0; Brian2 and MOOSE rejected. No inline citations in
     this section — references live only in `## Sources`.
   * `## Research Process` — describe that 16 Google searches + 9 WebFetch deep reads produced 20
     indexed sources in `research_internet.md`, then this task consolidated them into a five-axis
     comparison. Note that the `research-papers` stage was deliberately skipped for this task (it is
     tooling comparison, not biology literature).
   * `## Evidence from Papers` — summarise the peer-reviewed paper evidence: `Stimberg2019` (Brian2
     authors acknowledge multicompartment immaturity), `Awile2022` (NEURON modernisation and
     CoreNEURON 30-52x speedups), `Plastic-Arbor-2026` (Arbor 7-12x single-cell speedup over
     NEURON), `Schachter2010` (secondary DSGC NEURON model — already in t0002 corpus).
   * `## Evidence from Internet Sources` — summarise the documentation and repository evidence per
     library (release dates, pip wheel availability, GitHub activity). Cite every claim via the
     citation keys from Step 1.
   * `## Evidence from Code or Experiments` — state explicitly: "The `code-experiment` method was
     not used for this task; no new simulations or benchmarks were run — all speed numbers and
     feature claims come from peer-reviewed papers and the libraries' own documentation."
   * `## Synthesis` — embed the Step 3 comparison table verbatim, then explain the recommendation
     rationale: NEURON wins on ecosystem and DSGC-specific code availability (ModelDB 189347),
     NetPyNE adds the sweep-ergonomics layer the project needs, Arbor wins on raw speed so it is the
     correct backup, Brian2 rejected because its own authors flag multicompartment as immature,
     MOOSE rejected on maintenance signal and absent DSGC asset. Mention the NMODL portability
     caveat (several days of MOD-file translation before Arbor fallback yields speedups).
   * `## Limitations` — MOOSE release dates were hard to extract from the surfaced release page; no
     hands-on benchmark was run on the project's actual workstation; all speed claims are
     transferred from third-party benchmarks on different morphologies; the chosen primary (NEURON
     8.2.7) may need re-validation if the project adopts NEURON 9.0's C++ MOD-file migration; no
     public Brian2/Arbor/MOOSE DSGC code exists to stress-test those candidates on the project's
     actual use case.
   * `## Sources` — bullet list of every citation key used, with markdown reference link definitions
     at the end pointing to the URLs recorded in `research_internet.md` `## Source Index`. Include
     at least: `Awile2022`, `Stimberg2019`, `Plastic-Arbor-2026`, `ModelDB-189347`,
     `NEURON-Changelog`, `Arbor-Releases`, `Arbor-Install-Doc`, `Arbor-RTD-2025`, `Arbor-NMODL-Doc`,
     `NetPyNE-Doc`, `NetPyNE-GH`, `Brian2-MC-Docs`, `Brian2-GH`, `MOOSE-GH`, `MOOSE-Releases`,
     `MOOSE-Rdes-Doc`.

   Expected observable: `full_answer.md` exists, starts with valid YAML frontmatter, contains all
   nine mandatory headings in the specified order, embeds the comparison table under `## Synthesis`,
   and is above 800 words total. Satisfies REQ-6, REQ-7, REQ-8, REQ-9, REQ-10, REQ-11, REQ-13,
   REQ-15, REQ-16.

5. **Write `short_answer.md` and `details.json`.**

   * Create
     `tasks/t0003_simulator_library_survey/assets/answer/dsgc-compartmental-simulator-choice/short_answer.md`
     with YAML frontmatter (`spec_version: "2"`, `answer_id`, `answered_by_task`,
     `date_answered: "2026-04-19"`) and three mandatory headings in order: `## Question`,
     `## Answer` (2-5 sentences, no inline citations, same primary/backup verdict as
     `full_answer.md`), `## Sources` (bullet list of the same citation keys used in
     `full_answer.md`). The `## Answer` text must state the primary and backup simulator in one or
     two sentences (REQ-15).

   * Create
     `tasks/t0003_simulator_library_survey/assets/answer/dsgc-compartmental-simulator-choice/details.json`
     with the exact keys required by `meta/asset_types/answer/specification.md` Version 2:
     `spec_version="2"`, `answer_id="dsgc-compartmental-simulator-choice"`,
     `question="Which compartmental simulator should the direction-selective ganglion cell (DSGC) project use as its primary simulator, and which should it keep as a backup?"`,
     `short_title="DSGC compartmental simulator choice"`, `short_answer_path="short_answer.md"`,
     `full_answer_path="full_answer.md"`,
     `categories=["compartmental-modeling", "retinal-ganglion-cell"]` (both slugs exist in
     `meta/categories/`), `answer_methods=["internet", "papers"]`, `source_paper_ids=[]` (no papers
     are yet in this task's own `assets/paper/`; the papers cited live in `research_internet.md`
     only), `source_urls` = the full list of URLs from the `## Source Index` in
     `research_internet.md` (approximately 17 URLs — one per non-paper source plus the paper URLs,
     all formatted as valid `https://` URLs), `source_task_ids=[]`, `confidence="high"`,
     `created_by_task="t0003_simulator_library_survey"`, `date_created="2026-04-19"`. Because
     `source_paper_ids` is empty, evidence coverage is preserved via `source_urls` — the answer-spec
     requirement is "at least one evidence reference must be present across `source_paper_ids`,
     `source_urls`, and `source_task_ids`", which is satisfied by the URL list.

   Expected observable: all three files (`details.json`, `short_answer.md`, `full_answer.md`) exist,
   `details.json` is valid JSON, both markdown files start with YAML frontmatter. Satisfies REQ-12,
   REQ-13, REQ-15, REQ-17.

### Milestone D — Formatting and Verification

6. **Normalize markdown with flowmark.** For each of `short_answer.md` and `full_answer.md`, copy
   the file to `$HOME/tmp_flowmark/`, run
   `PYTHONUTF8=1 uv run flowmark --inplace --nobackup "$HOME/tmp_flowmark/<file>.md"` from inside
   the worktree, then copy the file back to its original location in
   `assets/answer/dsgc-compartmental-simulator-choice/`. Do this for both files. Expected
   observable: `git diff` on the two markdown files shows only whitespace/wrapping changes, not
   content changes.

7. **Run linters.** Run `uv run ruff check --fix . && uv run ruff format . && uv run mypy .` wrapped
   in `run_with_logs` with the task ID. Expected observable: exit code 0 from all three commands
   (this task adds no Python code, but the repo-level lint invariant must still hold).

8. **Run the answer-asset verificator.** Execute
   `uv run python -u -m arf.scripts.verificators.verify_answer_asset --task-id t0003_simulator_library_survey`
   wrapped in `run_with_logs`. Expected observable: zero errors (warnings are acceptable if
   documented). If any error is reported, return to Step 4 or Step 5 and fix the offending field.
   Satisfies REQ-14.

9. **Run the plan verificator (sanity check for this plan itself).** Execute
   `uv run python -u -m arf.scripts.verificators.verify_plan t0003_simulator_library_survey`.
   Expected observable: zero errors. (This plan should already pass, but a paranoia check after any
   late edits is cheap.)

Note on **registered metrics**: none of the four project metrics (`direction_selectivity_index`,
`tuning_curve_hwhm_deg`, `tuning_curve_reliability`, `tuning_curve_rmse`) apply — this task does not
run simulations that produce tuning curves. `results/metrics.json` will therefore contain an empty
measurement set (the orchestrator owns that file; no implementation step writes to it).

Note on **validation gates**: no step in this plan runs inference, trains a model, calls a paid API,
or processes more than 100 items. The largest data object produced is the ~20-row citation reference
list in `full_answer.md`. Validation gates for expensive operations are therefore not applicable.

## Remote Machines

None required. All implementation is local markdown authoring plus local Python verificator runs on
the researcher's workstation. The research inputs already exist on disk in
`research/research_internet.md`. No GPU, no cloud VM, no Vast.ai instance is needed.

## Assets Needed

* `tasks/t0003_simulator_library_survey/research/research_internet.md` — produced in-task by the
  already-completed research-internet stage. Source of every factual claim, citation key, and URL in
  the answer asset.

* `tasks/t0003_simulator_library_survey/task_description.md` — source of the verbatim task text
  quoted in the `## Task Requirement Checklist` section above.

* `meta/asset_types/answer/specification.md` — authoritative format for the output answer asset.

* `meta/categories/compartmental-modeling/` and `meta/categories/retinal-ganglion-cell/` — the two
  category slugs referenced in `details.json.categories`.

No dependency tasks (`task.json.dependencies = []`), no external downloads, no paper assets are
required to live inside this task folder (paper evidence lives only as citations from
`research_internet.md`'s `## Source Index`, which is a legitimate internet-research pattern per
`meta/task_types/internet-research/instruction.md`).

## Expected Assets

Exactly one answer asset, matching `task.json.expected_assets = {"answer": 1}`:

* **Type**: `answer`
* **Asset ID**: `dsgc-compartmental-simulator-choice`
* **Location**:
  `tasks/t0003_simulator_library_survey/assets/answer/dsgc-compartmental-simulator-choice/`
* **Contents**: `details.json`, `short_answer.md`, `full_answer.md`
* **Description**: Recommends NEURON 8.2.7 (with NetPyNE 1.1.1 for sweeps) as the project's primary
  compartmental simulator and Arbor 0.12.0 as its backup, rejecting Brian2 and MOOSE. Includes a
  five-axis comparison table covering cable-model fidelity, Python ergonomics, speed and
  parallelism, DSGC/RGC example availability, and long-term maintenance for all five candidate
  libraries. Evidence comes from 20 indexed sources in `research_internet.md` including three
  peer-reviewed papers (`Stimberg2019`, `Awile2022`, `Plastic-Arbor-2026`) and the ModelDB 189347
  DSGC code repository.

## Time Estimation

Total wall-clock: **1.5 to 2 hours** of implementation work.

* Research (already done, does not re-run): 0 hours.
* Step 1 (warm-up re-read of research): 10 minutes.
* Step 2 (folder skeleton): 2 minutes.
* Step 3 (draft comparison table): 30 minutes.
* Step 4 (write `full_answer.md`): 40 minutes.
* Step 5 (write `short_answer.md` and `details.json`): 15 minutes.
* Step 6 (flowmark normalisation): 5 minutes.
* Step 7 (ruff + mypy): 2 minutes.
* Step 8 (verify answer asset): 2 minutes, plus up to 20 minutes of fix-iteration if the verificator
  flags any fields.
* Step 9 (verify plan): 2 minutes.

No remote compute time; no validation runs; no asset creation beyond the three markdown+JSON files.

## Risks & Fallbacks

Applying the pre-mortem technique: imagine the answer asset has already failed verification — why?

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| `verify_answer_asset.py` rejects `details.json` because `answer_methods` list contains an unknown value | Medium | Blocks REQ-14 | Step 5 uses only the values allowed by `meta/asset_types/answer/specification.md`: `"internet"` and `"papers"`. Consult the spec before writing `details.json`. If the verificator still rejects, read the error code table in the spec and map the reported code to the offending field. |
| `short_answer.md` `## Answer` section exceeds 5 sentences and triggers `AA-E013` | Medium | Blocks REQ-14 and REQ-15 | When drafting, count sentence terminators before saving. Keep the answer to 2-4 sentences: "Use NEURON 8.2.7 as primary, with NetPyNE 1.1.1 for parameter sweeps. Use Arbor 0.12.0 as backup. Brian2 and MOOSE are rejected." If Flowmark's reflow introduces ambiguity, re-count sentences after Step 6 before Step 8. |
| A cited citation key in `full_answer.md` has no matching reference-link definition in `## Sources`, rendering as bare text on GitHub | Medium | Cosmetic, may weaken evidence audit | Before running verificators, grep the rendered citation keys (e.g., `\[Awile2022\]`, `\[Stimberg2019\]`) and confirm each has a matching `[Awile2022]: <url>` definition at the end of `## Sources`. The `## Source Index` section of `research_internet.md` supplies the canonical URLs. |
| `source_urls` in `details.json` contains a URL that is not valid HTTP(S) and triggers `AA-E010` | Low | Blocks REQ-14 | Copy URLs verbatim from `research_internet.md` `## Source Index` — every URL there is already HTTP(S). Do not hand-edit URLs. |
| `research_internet.md` contains a number or claim that turns out to be wrong (e.g., a wrong release date), and the answer asset propagates the error | Low | Degraded recommendation quality | Before embedding in `full_answer.md`, spot-check two release dates (NEURON 9.0.1 should be 17 Nov 2025; Arbor 0.12.0 should be 17 Apr 2025) by opening the cited URL. If either dates is wrong in the research file, log a correction via the corrections mechanism in a later task — do not modify `research/research_internet.md` in this task. |
| The chosen answer ID slug `dsgc-compartmental-simulator-choice` collides with an existing answer asset in the project | Very low | Would require rename | Before creating the folder, run `uv run python -u -m arf.scripts.aggregators.aggregate_answers --format ids` and confirm the slug is not in the returned list. If it is, choose `dsgc-simulator-primary-and-backup` instead. |
| The researcher reading the final answer disagrees with the NEURON-as-primary recommendation and wants NetPyNE listed as primary instead | Low | Would require rework | The recommendation rationale is grounded in four concrete facts documented in `full_answer.md`: (a) only DSGC public model is in NEURON, (b) NetPyNE *is* NEURON plus a sweep layer, (c) NEURON ships active 2025 releases, (d) Arbor's NMODL cost makes it unsuitable as primary. If the researcher disagrees, rewrite `## Short Answer` and `## Synthesis` to promote NetPyNE as primary (it is technically still NEURON underneath) but preserve Arbor as backup. This is a content edit, not a structural change, so the verificator will still pass. |

## Verification Criteria

* **Answer asset folder structure is correct.** Command:
  `ls tasks/t0003_simulator_library_survey/assets/answer/dsgc-compartmental-simulator-choice/`.
  Expected output: exactly three entries — `details.json`, `short_answer.md`, `full_answer.md` (no
  extra files, no sub-folders).

* **Exactly one answer asset exists in the task.** Command:
  `uv run python -u -m arf.scripts.aggregators.aggregate_answers --format ids` (filtered to this
  task, or verify by `ls tasks/t0003_simulator_library_survey/assets/answer/ | wc -l`). Expected
  output: 1 asset ID for this task, matching `task.json.expected_assets.answer = 1`. Confirms
  REQ-12.

* **Answer-asset verificator passes with zero errors.** Command:
  `uv run python -u -m arf.scripts.verificators.verify_answer_asset --task-id t0003_simulator_library_survey`.
  Expected output: exit code 0, zero errors, warnings acceptable. Confirms REQ-14.

* **The `## Answer` heading in `short_answer.md` and `full_answer.md` `## Short Answer` section
  both name the primary and backup simulator.** Command:
  `grep -E "NEURON|Arbor" tasks/t0003_simulator_library_survey/assets/answer/dsgc-compartmental-simulator-choice/short_answer.md`
  and the equivalent grep on `full_answer.md`. Expected output: at least one match for each of
  "NEURON" and "Arbor" in both files, within the answer sections. Confirms REQ-13 and REQ-15.

* **The comparison table embedded in `full_answer.md` has exactly five rows for the five
  libraries.** Command:
  `grep -c "^\| \*\*\(NEURON\|NetPyNE\|Brian2\|MOOSE\|Arbor\)\*\*" tasks/t0003_simulator_library_survey/assets/answer/dsgc-compartmental-simulator-choice/full_answer.md`.
  Expected output: `5`. Confirms REQ-11 and REQ-16.

* **All five evaluation axes appear as column headers in the comparison table.** Command:
  `grep -E "Cable.*model|Python ergonomics|Speed.*parallelism|DSGC.*RGC|Long.*term" tasks/t0003_simulator_library_survey/assets/answer/dsgc-compartmental-simulator-choice/full_answer.md`.
  Expected output: at least 5 lines matched (one per axis header). Confirms REQ-6, REQ-7, REQ-8,
  REQ-9, REQ-10.

* **Requirement coverage check.** Open `full_answer.md` and visually confirm that every one of
  REQ-1 through REQ-17 has been satisfied by the produced content. Command:
  `grep -E "REQ-[0-9]+" tasks/t0003_simulator_library_survey/plan/plan.md | wc -l`. Expected
  output: at least 17 (each REQ-ID appears at least once in the plan; this is a plan-level
  integrity check, not a content check on the answer asset). Confirms the traceability from
  `task.json` → plan → answer asset is intact.

* **Plan verificator passes.** Command:
  `uv run python -u -m arf.scripts.verificators.verify_plan t0003_simulator_library_survey`.
  Expected output: exit code 0, zero errors.
