# Results Summary: Simulator Library Survey for DSGC Compartmental Modelling

## Summary

Produced a single answer asset recommending **NEURON 8.2.7** (paired with **NetPyNE 1.1.1** for
parameter sweeps) as the project's primary compartmental simulator and **Arbor 0.12.0** as backup,
after surveying five candidate libraries (NEURON, NetPyNE, Brian2, MOOSE, Arbor) on five axes
(cable-model fidelity, Python ergonomics, speed and parallelism, DSGC/RGC example availability,
long-term maintenance). Brian2 and MOOSE were rejected with grounded evidence. The full answer
embeds a 5-row × 5-column comparison table backed by 20 indexed internet sources.

## Metrics

* **Libraries evaluated**: 5 (NEURON, NetPyNE, Brian2, MOOSE, Arbor)
* **Evaluation axes**: 5 (cable-model fidelity, Python ergonomics, speed and parallelism, DSGC/RGC
  examples, long-term maintenance)
* **Sources cited**: 20 URLs, including 4 newly discovered papers
* **Answer assets produced**: 1 (`dsgc-compartmental-simulator-choice`)
* **Task requirements satisfied**: 17 of 17 (REQ-1 through REQ-17)
* **External cost incurred**: $0.00 (no paid APIs, no remote compute)
* **Registered metrics measured**: 0 (none apply — this task selects a simulator rather than running
  one; `metrics.json` is `{}`)

## Verification

* `verify_task_dependencies.py` — PASSED (0 errors, 0 warnings)
* `verify_research_internet.py` — PASSED (0 errors, 0 warnings)
* `verify_plan.py` — PASSED (0 errors, 0 warnings)
* `verify_answer_asset.py` — PASSED (0 errors, 0 warnings)
