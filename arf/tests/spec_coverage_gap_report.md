# Spec Coverage Gap Report

## Summary

* Total spec codes: 265 (excluding ~12 prose-only corrections rules and removed TR-E009/TR-W009)
* Covered by tests: 222
* Newly added tests: 16 (TR-E003, TR-E008, TR-E010, TR-E019, TR-W006, TR-W011, TR-W013, TR-W014,
  MT-E008, RM-E004, RM-E005, RM-E006, RM-W001, RM-W002, RM-W003, RM-W004)
* Still NOT covered (no verificator module exists): 27
* Coverage after additions: 89.8%

* * *

## Missing Tests (by specification)

### task_file_specification.md (TF)

All 22 codes covered. Note: TF-E006 tests assert `TD-E001` (delegated code), and TF-W006 tests
assert `TD-E003` (delegated code). Both are semantically covered.

### task_folder_specification.md (FD)

All 22 codes covered.

### task_git_specification.md (TG)

No dedicated verificator module for TG codes exists. The git checks are embedded in
`verify_pr_premerge.py` as private helper functions (`_check_branch_name`, `_check_pr_target`,
`_check_file_isolation`, etc.) that produce PM-prefixed codes. The TG codes from the spec are not
emitted by any verificator. **Cannot add tests without a TG-code-emitting verificator.**

* TG-E001: Branch name does not match task/<task_id> pattern -- NO VERIFICATOR
* TG-E002: Task branch modifies files outside allowed set -- NO VERIFICATOR
* TG-E003: No commits on the task branch -- NO VERIFICATOR
* TG-E004: Completed step has no associated commit -- NO VERIFICATOR
* TG-E005: PR does not target main -- NO VERIFICATOR
* TG-W001: Commit message missing task ID and step ID -- NO VERIFICATOR
* TG-W002: Commit message first line exceeds 72 characters -- NO VERIFICATOR
* TG-W003: PR title wrong format -- NO VERIFICATOR
* TG-W004: PR body missing required section -- NO VERIFICATOR

### task_steps_specification.md (TS)

No dedicated verificator module for TS codes exists. `verify_step.py` produces SV codes for
individual step folder validation. The TS codes (step_tracker-level validation of step IDs,
ordering, and required steps) are not emitted by any verificator. **Cannot add tests without a
TS-code-emitting verificator.**

* TS-E001: Step ID not a valid slug format -- NO VERIFICATOR
* TS-E002: Required step missing from step_tracker.json -- NO VERIFICATOR
* TS-E003: Step order numbers not sequential -- NO VERIFICATOR
* TS-W001: Step ID not in canonical list -- NO VERIFICATOR
* TS-W002: Steps out of canonical order -- NO VERIFICATOR

### task_results_specification.md (TR)

All 8 previously missing codes now have tests added to `test_verify_task_results.py`:

* TR-E003: metrics.json missing or invalid -- ADDED (replaced empty `pass` stubs)
* TR-E008: metrics.json top-level not object -- ADDED
* TR-E010: metrics.json invalid payload shape -- ADDED (2 tests)
* TR-E019: results_detailed.md spec_version not recognized -- ADDED
* TR-W006: metrics.json key not snake_case -- ADDED
* TR-W011: Task Requirement Coverage lacks status labels -- ADDED
* TR-W013: Examples section missing for experiment-type task -- ADDED
* TR-W014: Examples section fewer than 10 bullet points -- ADDED

### task_type_specification.md (TY)

All 12 codes covered.

### logs_specification.md (LG)

All 16 codes covered.

### plan_specification.md (PL)

All 15 codes covered.

### suggestions_specification.md (SG)

All 19 codes covered.

### corrections_specification.md (CO/CR)

Prose rules only (no formal codes in spec). Test file uses CR-E/CR-W codes. Not auditable against
pseudo-test codes since spec defines no formal codes.

### metrics_specification.md (MT)

* MT-E008: Dataset ID in datasets does not exist -- ADDED to `test_verify_metrics_definition.py`

### research_papers_specification.md (RP)

All 16 codes covered. Note: RP-W006 test verifies the limitation that the code cannot easily fire
(heading detected as citation), so it asserts `passed is True` rather than asserting the warning
code.

### research_internet_specification.md (RI)

All 18 codes covered. Note: RI-W005 has the same limitation as RP-W006.

### research_code_specification.md (RC)

All 14 codes covered. Note: RC-W004 has the same limitation.

### step_tracker_specification.md (ST)

No dedicated verificator module for ST codes exists. Step tracker validation happens indirectly in
`verify_logs.py`, `verify_task_folder.py`, and `verify_task_complete.py`, but these produce LG/FD/TC
codes, not ST codes. **Cannot add tests without a ST-code-emitting verificator.**

* ST-E001: step_tracker.json missing or invalid JSON -- NO VERIFICATOR
* ST-E002: task_id does not match folder name -- NO VERIFICATOR
* ST-E003: steps missing or not a list -- NO VERIFICATOR
* ST-E004: Step missing required fields -- NO VERIFICATOR
* ST-E005: Step numbers not sequential -- NO VERIFICATOR
* ST-E006: Status not an allowed value -- NO VERIFICATOR
* ST-W001: Completed step has null log_file -- NO VERIFICATOR
* ST-W002: log_file path does not exist -- NO VERIFICATOR
* ST-W003: started_at null for non-pending step -- NO VERIFICATOR
* ST-W004: completed_at null for terminal step -- NO VERIFICATOR

### category_specification.md (CA)

All 8 codes covered.

### compare_literature_specification.md (CL)

All 8 codes covered.

### remote_machines_specification.md (RM)

All 7 previously missing codes now have tests added to `test_verify_machines_destroyed.py`:

* RM-E004: Machine entry missing required field -- ADDED
* RM-E005: instance_id mismatch with remote_machines_used.json -- ADDED
* RM-E006: total_cost_usd mismatch with remote_machines_used.json -- ADDED
* RM-W001: Vast.ai API unreachable -- ADDED
* RM-W002: Actual cost exceeds plan estimate by >50% -- ADDED
* RM-W003: Machine running for more than 12 hours -- ADDED
* RM-W004: selection_rationale empty or under 20 characters -- ADDED

### agent_skills_specification.md (SK)

No `verify_skill.py` or similar verificator module exists. No test file tests SK codes. **Cannot add
tests without a SK-code-emitting verificator.**

* SK-E001: SKILL.md missing or empty -- NO VERIFICATOR
* SK-E002: YAML frontmatter missing -- NO VERIFICATOR
* SK-E003: name missing from frontmatter -- NO VERIFICATOR
* SK-E004: description missing from frontmatter -- NO VERIFICATOR
* SK-E005: Frontmatter name does not match directory slug -- NO VERIFICATOR
* SK-E006: Required body section missing -- NO VERIFICATOR
* SK-E007: .claude/skills symlink missing -- NO VERIFICATOR
* SK-E008: .codex/skills symlink missing -- NO VERIFICATOR
* SK-E009: Symlink resolves to directory without SKILL.md -- NO VERIFICATOR
* SK-W001: Description too vague -- NO VERIFICATOR
* SK-W002: Output Format missing for file-producing skill -- NO VERIFICATOR
* SK-W003: Unnecessary tool-specific metadata -- NO VERIFICATOR

### project_budget_specification.md (PB)

All 6 codes covered.

### project_description_specification.md (PD)

All 10 codes covered.

### paper asset specification (PA)

All 26 codes covered.

### library asset specification (LA)

All 21 codes covered.

### dataset asset specification (DA)

All 23 codes covered.

### answer asset specification (AA)

All 18 codes covered.

### model asset specification (MA)

All 22 codes covered.

### predictions asset specification (PR)

All 22 codes covered.

* * *

## Covered Codes (for reference)

TF-E001, TF-E002, TF-E003, TF-E004, TF-E005, TF-E006, TF-E007, TF-E008, TF-E009, TF-E010, TF-E011,
TF-E012, TF-E013, TF-E014, TF-E015, TF-E016, TF-W001, TF-W002, TF-W003, TF-W004, TF-W005, TF-W006,
FD-E001, FD-E002, FD-E003, FD-E004, FD-E005, FD-E006, FD-E007, FD-E008, FD-E009, FD-E010, FD-E011,
FD-E012, FD-E013, FD-E014, FD-E015, FD-E016, FD-W001, FD-W002, FD-W003, FD-W004, FD-W005, FD-W006,
LG-E001, LG-E002, LG-E003, LG-E004, LG-E005, LG-E006, LG-E007, LG-E008, LG-W001, LG-W002, LG-W003,
LG-W004, LG-W005, LG-W006, LG-W007, LG-W008, PL-E001, PL-E002, PL-E003, PL-E004, PL-E005, PL-E006,
PL-E007, PL-W001, PL-W002, PL-W003, PL-W004, PL-W005, PL-W006, PL-W007, PL-W008, SG-E001, SG-E002,
SG-E003, SG-E004, SG-E005, SG-E006, SG-E007, SG-E008, SG-E009, SG-E010, SG-E011, SG-E012, SG-E013,
SG-W001, SG-W002, SG-W003, SG-W004, SG-W005, SG-W006, MT-E001, MT-E002, MT-E003, MT-E004, MT-E005,
MT-E006, MT-E007, MT-W001, MT-W002, RP-E001, RP-E002, RP-E003, RP-E004, RP-E005, RP-E006, RP-E007,
RP-E008, RP-E009, RP-E010, RP-W001, RP-W002, RP-W003, RP-W004, RP-W005, RP-W006, RI-E001, RI-E002,
RI-E003, RI-E004, RI-E005, RI-E006, RI-E007, RI-E008, RI-E009, RI-E010, RI-E011, RI-W001, RI-W002,
RI-W003, RI-W004, RI-W005, RI-W006, RI-W007, RC-E001, RC-E002, RC-E003, RC-E004, RC-E005, RC-E006,
RC-E007, RC-E008, RC-E009, RC-W001, RC-W002, RC-W003, RC-W004, RC-W005, CA-E001, CA-E002, CA-E003,
CA-E004, CA-W001, CA-W002, CA-W003, CA-W004, CL-E001, CL-E002, CL-E003, CL-E004, CL-E005, CL-W001,
CL-W002, CL-W003, RM-E001, RM-E002, RM-E003, PB-E001, PB-E002, PB-E003, PB-E004, PB-W001, PB-W002,
PD-E001, PD-E002, PD-E003, PD-E004, PD-W001, PD-W002, PD-W003, PD-W004, PD-W005, PD-W006, PA-E001,
PA-E002, PA-E003, PA-E004, PA-E005, PA-E006, PA-E007, PA-E008, PA-E009, PA-E010, PA-E011, PA-E012,
PA-E013, PA-E014, PA-E015, PA-W001, PA-W002, PA-W003, PA-W004, PA-W005, PA-W006, PA-W007, PA-W008,
PA-W009, PA-W010, PA-W011, LA-E001, LA-E002, LA-E004, LA-E005, LA-E006, LA-E008, LA-E009, LA-E010,
LA-E011, LA-E012, LA-E013, LA-E016, LA-W001, LA-W003, LA-W004, LA-W005, LA-W008, LA-W013, LA-W014,
LA-W015, LA-W016, DA-E001, DA-E002, DA-E003, DA-E004, DA-E005, DA-E007, DA-E008, DA-E009, DA-E010,
DA-E011, DA-E012, DA-E013, DA-E016, DA-W001, DA-W003, DA-W004, DA-W005, DA-W007, DA-W008, DA-W009,
DA-W010, DA-W011, DA-W012, DA-W013, AA-E001, AA-E002, AA-E003, AA-E004, AA-E005, AA-E006, AA-E007,
AA-E008, AA-E009, AA-E010, AA-E011, AA-E012, AA-E013, AA-E014, AA-W001, AA-W002, AA-W003, AA-W004,
MA-E001, MA-E002, MA-E003, MA-E004, MA-E005, MA-E007, MA-E008, MA-E009, MA-E010, MA-E011, MA-E012,
MA-E013, MA-E016, MA-W001, MA-W003, MA-W004, MA-W005, MA-W008, MA-W013, MA-W014, MA-W015, MA-W016,
PR-E001, PR-E002, PR-E003, PR-E004, PR-E005, PR-E007, PR-E008, PR-E009, PR-E010, PR-E011, PR-E012,
PR-E013, PR-E016, PR-W001, PR-W003, PR-W004, PR-W005, PR-W008, PR-W013, PR-W014, PR-W015, PR-W016,
PR-W017, TY-E001, TY-E002, TY-E003, TY-E004, TY-E005, TY-E006, TY-E007, TY-W001, TY-W002, TY-W003,
TY-W004, TY-W005

* * *

## Aggregator Test Coverage

The following aggregator test files exist:

* `test_aggregate_answers.py`
* `test_aggregate_categories.py`
* `test_aggregate_costs.py`
* `test_aggregate_datasets.py`
* `test_aggregate_libraries.py`
* `test_aggregate_metrics.py`
* `test_aggregate_models.py`
* `test_aggregate_papers.py`
* `test_aggregate_predictions.py`
* `test_aggregate_suggestions.py`
* `test_aggregate_task_types.py`
* `test_aggregate_tasks.py`
* `test_aggregator_input_tolerance.py`

No obvious aggregator test files appear to be missing.
