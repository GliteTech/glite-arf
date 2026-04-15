# Implementation Bugs Report

## Summary

* Total failures triaged: 16
* Test bugs (fixed): 3
* Implementation bugs (spec codes not implemented): 13

## Test Bugs Fixed

### MT-E008: Dataset not in assets (test\_verify\_metrics\_definition.py)

The test did not create any dataset directories under `tasks/*/assets/dataset/`, so
`_collect_all_dataset_ids()` returned an empty set and the guard `if len(all_dataset_ids) > 0:`
skipped the check entirely. Fixed by creating a dummy dataset directory so the guard passes and the
check runs.

### TR-W013 and TR-W014: Examples section checks (test\_verify\_task\_results.py)

Both tests used `task_types=["run-experiment"]` but the verificator's `EXPERIMENT_TASK_TYPES`
frozenset contains `"experiment-run"`, not `"run-experiment"`. Fixed by changing the test to use
`"experiment-run"`.

## Implementation Bugs

### Group 1: verify\_machines\_destroyed.py -- 7 missing codes

The verificator at `arf/scripts/verificators/verify_machines_destroyed.py` only implements RM-E001
(no `destroyed_at`), RM-E002 (instance still active via API), and RM-E003 (invalid
machine\_log.json). It defines a `_CODE_API_UNREACHABLE` for RM-W001 but never emits it (the code
path that could produce it checks `api_status in _ACTIVE_STATUSES` which does not match
`"unreachable"`). The remaining codes are entirely absent from the implementation.

#### RM-E004: Missing required field in machine entry

* **Spec**: `arf/specifications/remote_machines_specification.md`, Verification Rules table
* **Spec says**: "A required field is missing from a machine entry"
* **Verificator**: `arf/scripts/verificators/verify_machines_destroyed.py`
* **Status**: Code RM-E004 is NOT implemented. The verificator iterates `machine_log_entries` but
  only checks `instance_id` and `destroyed_at` fields. It never validates that other required fields
  (provider, offer\_id, ssh\_host, cuda\_version, etc.) are present.

#### RM-E005: instance\_id mismatch with remote\_machines\_used.json

* **Spec**: `arf/specifications/remote_machines_specification.md`, Verification Rules table
* **Spec says**: "`instance_id` in `machine_log.json` does not match `machine_id` in
  `remote_machines_used.json`"
* **Verificator**: `arf/scripts/verificators/verify_machines_destroyed.py`
* **Status**: Code RM-E005 is NOT implemented. The verificator reads both files but never
  cross-references instance IDs between `machine_log.json` and `remote_machines_used.json`.

#### RM-E006: total\_cost\_usd mismatch

* **Spec**: `arf/specifications/remote_machines_specification.md`, Verification Rules table
* **Spec says**: "`total_cost_usd` in `machine_log.json` does not match `cost_usd` in
  `remote_machines_used.json`"
* **Verificator**: `arf/scripts/verificators/verify_machines_destroyed.py`
* **Status**: Code RM-E006 is NOT implemented. The verificator never compares cost values between
  `machine_log.json` and `remote_machines_used.json`.

#### RM-W001: Vast.ai API unreachable

* **Spec**: `arf/specifications/remote_machines_specification.md`, Verification Rules table
* **Spec says**: "Vast.ai API unreachable (cannot confirm destruction, but `destroyed_at` is
  present)"
* **Verificator**: `arf/scripts/verificators/verify_machines_destroyed.py`
* **Status**: Code RM-W001 is defined as `_CODE_API_UNREACHABLE` but is never emitted. When
  `_check_instance_via_api` returns `None` (unreachable) or `"unreachable"`, no diagnostic is
  produced. The `_check_instance_via_api` stub returns `"unreachable"` as a string, but the
  verificator only acts on values in `_ACTIVE_STATUSES` ("running", "loading").

#### RM-W002: Cost exceeds plan estimate by >50%

* **Spec**: `arf/specifications/remote_machines_specification.md`, Verification Rules table
* **Spec says**: "Actual cost exceeds plan estimate by more than 50%"
* **Verificator**: `arf/scripts/verificators/verify_machines_destroyed.py`
* **Status**: Code RM-W002 is NOT implemented. No `DiagnosticCode` is defined for it, and no
  cost-vs-estimate comparison logic exists.

#### RM-W003: Machine running more than 12 hours

* **Spec**: `arf/specifications/remote_machines_specification.md`, Verification Rules table
* **Spec says**: "Machine was running for more than 12 hours"
* **Verificator**: `arf/scripts/verificators/verify_machines_destroyed.py`
* **Status**: Code RM-W003 is NOT implemented. No `DiagnosticCode` is defined for it, and no
  duration check exists.

#### RM-W004: selection\_rationale empty or under 20 characters

* **Spec**: `arf/specifications/remote_machines_specification.md`, Verification Rules table
* **Spec says**: "`selection_rationale` is empty or under 20 characters"
* **Verificator**: `arf/scripts/verificators/verify_machines_destroyed.py`
* **Status**: Code RM-W004 is NOT implemented. No `DiagnosticCode` is defined for it, and no
  rationale length check exists.

### Group 2: verify\_task\_results.py -- 6 missing metrics.json checks

The verificator at `arf/scripts/verificators/verify_task_results.py` defines `DiagnosticCode`
constants for TR-E003, TR-E008, TR-E010, and TR-W006 but the `verify_task_results()` function never
calls any metrics.json validation logic. The function calls `_check_results_summary`,
`_check_results_detailed`, `_check_costs`, `_check_remote_machines`, and `_check_images_dir` -- but
there is no `_check_metrics` function.

#### TR-E003: metrics.json does not exist or is not valid JSON

* **Spec**: `arf/specifications/task_results_specification.md`, Verification Rules table
* **Spec says**: "`metrics.json` does not exist or is not valid JSON"
* **Verificator**: `arf/scripts/verificators/verify_task_results.py`
* **Status**: Code TR-E003 is defined (line 152) but no check function reads or validates
  `metrics.json`. The `verify_task_results()` function has no call to any metrics checker.

#### TR-E008: metrics.json top-level value is not a JSON object

* **Spec**: `arf/specifications/task_results_specification.md`, Verification Rules table
* **Spec says**: "`metrics.json` top-level value is not a JSON object"
* **Verificator**: `arf/scripts/verificators/verify_task_results.py`
* **Status**: Code TR-E008 is defined (line 177) but never emitted. No metrics.json validation
  exists.

#### TR-E010: metrics.json uses an invalid metric payload shape

* **Spec**: `arf/specifications/task_results_specification.md`, Verification Rules table
* **Spec says**: "`metrics.json` uses an invalid metric payload shape"
* **Verificator**: `arf/scripts/verificators/verify_task_results.py`
* **Status**: Code TR-E010 is defined (line 187) but never emitted. No metrics.json shape validation
  exists (empty variants array, variant missing variant\_id).

#### TR-W006: metrics.json key not snake\_case

* **Spec**: `arf/specifications/task_results_specification.md`, Verification Rules table
* **Spec says**: "A `metrics.json` metric or dimension key is not `snake_case`"
* **Verificator**: `arf/scripts/verificators/verify_task_results.py`
* **Status**: Code TR-W006 is defined (line 265) but never emitted. The `SNAKE_CASE_PATTERN`
  constant is defined but no function applies it to metrics.json keys.
