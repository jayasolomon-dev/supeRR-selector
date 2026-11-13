# SUPERR SELECTOR — FINAL PIPELINE FORENSIC REVIEW REPORT
**Document Reference:** `reports/final_pipeline_forensic_review.md`  
**Author:** Senior Cricket Data Engineer & Independent Forensic Auditor  
**Project:** SUPERR SELECTOR (Cricket Pressure-Performance Analytics Platform)  
**Date:** November 2026  
**Auditing Mode:** STRICT READ-ONLY FORENSIC AUDIT  
**Status:** Forensic Verification Complete — Final Auditor Sign-Off  

---

## Executive Summary

Under **Master Task 03.3.1**, an independent forensic investigation was conducted in strict read-only mode to audit:
1. The reported DLS target discrepancy regarding **Match ID 37354** (why prior documentation cited a target of 94, whereas the latest validation printout reported `Target = nan`).
2. A full reconciliation of all **34 DLS/revised matches** in `data/raw/matches.csv`.
3. In-memory synthetic edge-case verification of Required Run Rate (RRR) and `impossible_chase_state` (Cases A, B, C, D and edge cases).
4. An architectural review of `src/validate_pipeline.py` regarding assertion counts, test numbering, and potential false-positive test risks.

---

## Check 1 — Match 37354 & Complete 34-Match DLS Reconciliation

### 1.1 Match 37354 Forensic Investigation
* **The Question:** Why did `reports/final_scope_reconciliation.md` state `revised_target = 94`, while the validation log for Test 14 in `reports/pipeline_correction_report.md` printed `Target = nan`?
* **Evidence from `data/raw/matches.csv`:**
  - Row for Match 37354:
    ```
    match_id: 37354
    comp_id: 2387 (Pakistan in Australia T20I Series 2024, Match 1 at Brisbane, 2024-11-14)
    first_inn_revised_overs: 42.0 (7 overs per side)
    second_inn_revised_overs: 42.0 (7 overs per side)
    revised_target: 94.0
    result: Australia Won by 29 runs
    ```
  - **Ground Truth:** `revised_target = 94.0` is the actual, official raw value stored in `matches.csv`.
* **Evidence from `data/processed/t20i_deliveries.csv`:**
  - In `t20i_deliveries.csv`, Match 37354 has 86 total deliveries (44 in Innings 1, 42 in Innings 2).
  - In Innings 1: `target` is `NaN` across all 44 deliveries.
  - In Innings 2: `target` is **`94.0` across all 42 deliveries**.
  - Delivery 1: `score_before = 0`, `target = 94.0`, `required_runs_before = 94.0`, `required_run_rate_before = 13.43`.
  - Delivery 2: `score_before = 4`, `target = 94.0`, `required_runs_before = 90.0`, `required_run_rate_before = 13.17`.
  - Delivery 42: `score_before = 64`, `target = 94.0`, `required_runs_before = 30.0`.
* **Root Cause of the Discrepancy:**
  - In `src/validate_pipeline.py` (line 195), the test case definition for Match 37354 was configured as:
    ```python
    {"mid": 37354, "inn": 1, "exp_balls": 42, "exp_target": np.nan, "desc": "AUS vs PAK (2024, 7 overs = 42 balls)"}
    ```
  - The test deliberately probed **Innings 1** (`"inn": 1`). In cricket, the first batting team has no target to chase, so `target` is by design `NaN` for all Innings 1 deliveries.
  - The validation test passed because it asserted Innings 1 target (`NaN`), but the console printout gave the impression that the match had no target.
  - **Verdict:** The target of 94 in Innings 2 is **100% correctly stored, propagated, and intact** in `data/processed/t20i_deliveries.csv`. The apparent discrepancy was purely an artifact of testing Innings 1 in the validation script.

---

### 1.2 Reconciliation Table of All 34 DLS / Revised Matches in `matches.csv`

Every single match in `data/raw/matches.csv` with revised overs or targets was audited against `data/processed/`:

| Match ID | Competition Name | Official Result | Raw Revised Overs (Inn1 / Inn2) | Raw Revised Target | Processed Inn2 Balls | Processed Inn2 Target | Forensic Reconciliation Status |
|:---:|:---|:---|:---:|:---:|:---:|:---:|:---|
| **13612** | Sri Lanka in Australia T20I Series 2022 | Australia Won by 20 runs (D/L method) | - / 114 | 143.0 | 114 | 143.0 | ✅ Exact Match (DLS Target Applied) |
| **15410** | South Africa in India T20I Series 2022 | Match Abandoned | 114 / - | - | N/A | N/A | ✅ Inn 2 unplayed (Rain stopped play in Inn 1) |
| **15546** | Bangladesh in West Indies T20I Series 2022 | No Result | 84 / - | - | N/A | N/A | ✅ Inn 2 unplayed (Rain stopped play in Inn 1) |
| **16753** | Afghanistan in Ireland T20I Series 2022 | Afghanistan Won by 27 Runs | 66 / - | - | 66 | 133.0 | ✅ Exact Match (Dynamically Inn 1 total 132 + 1) |
| **16754** | Afghanistan in Ireland T20I Series 2022 | Ireland Won by 7 Wickets(D/L Method) | - / 42 | 56.0 | 42 | 56.0 | ✅ Exact Match (DLS Target Applied) |
| **17395** | Australia in India T20I Series 2022 | India Won by 6 Wickets | 48 / 48 | 91.0 | 48 | 91.0 | ✅ Exact Match (DLS Target Applied) |
| **17765** | England in Australia T20I Series 2022 | No Result | 72 / 72 | 130.0 | 72 | 130.0 | ✅ Exact Match (DLS Target Applied) |
| **21586** | IPL 2023 | Chennai Super Kings Won by 5 wickets (DLS method) | - / 90 | 171.0 | 90 | 171.0 | ✅ Exact Match (DLS Target Applied) |
| **19959** | West Indies in South Africa T20I Series 2023 | West Indies won by 3 wickets | 66 / - | - | 66 | 132.0 | ✅ Exact Match (Dynamically Inn 1 total 131 + 1) |
| **21070** | Ireland in Bangladesh T20I Series 2023 | Bangladesh Won by 22 Runs (DLS method) | - / 48 | 104.0 | 48 | 104.0 | ✅ Exact Match (DLS Target Applied) |
| **21071** | Ireland in Bangladesh T20I Series 2023 | Bangladesh Won by 77 Runs | 102 / 102 | 203.0 | 102 | 203.0 | ✅ Exact Match (DLS Target Applied) |
| **28046** | India in South Africa T20I Series 2023 | South Africa won by 5 wickets (DLS) | - / 90 | 152.0 | 90 | 152.0 | ✅ Exact Match (DLS Target Applied) |
| **29984** | Australia in New Zealand T20I Series 2024 | Australia Won by 27 Runs (DLS method) | - / 60 | 126.0 | 60 | 126.0 | ✅ Exact Match (DLS Target Applied) |
| **31707** | New Zealand in Pakistan T20I Series 2024 | No Result | 30 / - | - | N/A | N/A | ✅ Inn 2 unplayed (Rain stopped play in Inn 1) |
| **37354** | Pakistan in Australia T20I Series 2024 | Australia Won by 29 runs | 42 / 42 | 94.0 | 42 | 94.0 | ✅ Exact Match (DLS Target Applied) |
| **36098** | South Africa in West Indies T20I Series 2024 | West Indies Won by 8 wickets (DLS) | 78 / 78 | 116.0 | 78 | 116.0 | ✅ Exact Match (DLS Target Applied) |
| **34428** | India in Sri Lanka T20I Series 2024 | India Won by 7 wickets(D/L Method) | - / 48 | 78.0 | 48 | 78.0 | ✅ Exact Match (DLS Target Applied) |
| **36208** | South Africa in England T20I Series 2025 | South Africa Won by 14 runs(DLS method) | 54 / 30 | 69.0 | 30 | 69.0 | ✅ Exact Match (DLS Target Applied) |
| **40727** | IPL 2025 | Punjab Kings Won by 5 wickets | 84 / 84 | 96.0 | 84 | 96.0 | ✅ Exact Match (DLS Target Applied) |
| **40749** | IPL 2025 | Gujarat Titans Won by 3 wickets (DLS Method) | - / 114 | 147.0 | 114 | 147.0 | ✅ Exact Match (DLS Target Applied) |
| **39809** | Pakistan in New Zealand T20I Series 2025 | New Zealand Won by 5 wickets | 90 / 90 | 136.0 | 90 | 136.0 | ✅ Exact Match (DLS Target Applied) |
| **39983** | Ireland in Zimbabwe T20I Series 2025 | No Result | 54 / - | - | N/A | N/A | ✅ Inn 2 unplayed (Rain stopped play in Inn 1) |
| **39985** | Ireland in Zimbabwe T20I Series 2025 | No Result | 108 / - | - | N/A | N/A | ✅ Inn 2 unplayed (Rain stopped play in Inn 1) |
| **41851** | West Indies in South Africa T20I Series 2026 | West Indies Won by 6 runs(DLS Method) | 60 / 60 | 125.0 | 60 | 125.0 | ✅ Exact Match (DLS Target Applied) |
| **41975** | India in Australia T20I Series 2025 | No Result | 108 / - | - | N/A | N/A | ✅ Inn 2 unplayed (Rain stopped play in Inn 1) |
| **46311** | Australia in New Zealand T20I Series 2025 | No Result | 54 / 54 | - | N/A | N/A | ✅ Inn 2 unplayed (Rain stopped play in Inn 1) |
| **46749** | England in New Zealand T20I Series 2025 | No Result | 84 / - | - | N/A | N/A | ✅ Inn 2 unplayed (Rain stopped play in Inn 1) |
| **50137** | IPL 2026 | Rajasthan Royals Won by 27 runs | 66 / 66 | 151.0 | 66 | 151.0 | ✅ Exact Match (DLS Target Applied) |
| **50371** | IPL 2026 | Lucknow Super Giants Won by 9 runs (DLS method) | 114 / 114 | 213.0 | 114 | 213.0 | ✅ Exact Match (DLS Target Applied) |
| **48610** | England in Sri Lanka T20I Series 2026 | England Won by 11 runs (DLS method) | 102 / 90 | 115.0 | 90 | 115.0 | ✅ Exact Match (DLS Target Applied) |
| **48611** | England in Sri Lanka T20I Series 2026 | England Won by 6 wickets(DLS Method) | - / 102 | 168.0 | 102 | 168.0 | ✅ Exact Match (DLS Target Applied) |
| **50190** | New Zealand in Bangladesh T20I Series 2026 | New Zealand Won by 6 wickets (DLS Method) | 90 / 90 | 103.0 | 90 | 103.0 | ✅ Exact Match (DLS Target Applied) |
| **50408** | West Indies in India T20I Series 2026 | No Result | 54 / 54 | - | N/A | N/A | ✅ Inn 2 unplayed (Rain stopped play in Inn 1) |
| **54711** | India in Japan T20I Match 2026 | India Won by 2 runs | 30 / 30 | 33.0 | 30 | 33.0 | ✅ Exact Match (DLS Target Applied) |

**Forensic Finding:** Zero mismatches exist. In all 23 matches where `revised_target` is provided in `matches.csv` and Innings 2 was played, the processed dataset matches `revised_target` with 100% mathematical fidelity.

---

## Check 2 — Synthetic RRR & Impossible Chase Stress Testing

### 2.1 The Issue
In historical cricket datasets, innings end as soon as the scheduled balls are bowled (or all wickets are lost). Therefore, **zero real deliveries in `data/processed/` are bowled when `legal_balls_remaining_before == 0`** (`legal_balls_remaining_before` min value is 1).

To verify the mathematical correctness of edge cases, an independent in-memory synthetic testing harness was executed without modifying production code.

### 2.2 Synthetic Test Results Matrix

| Test Case | Scenario / Parameters | Expected RRR | Actual RRR | Expected Impossible Chase Flag | Actual Impossible Chase Flag | Test Status |
|:---|:---|:---:|:---:|:---:|:---:|:---:|
| **Case A** | Innings 2, Balls Remaining = 0, Required Runs = 10 | `NaN` | `NaN` | `True` | `True` | **PASS ✅** |
| **Case B** | Innings 2, Balls Remaining = 0, Required Runs = 0 | `NaN` | `NaN` | `False` | `False` | **PASS ✅** |
| **Case C** | Innings 2, Balls Remaining = 1, Required Runs = 22 | `132.0` | `132.0` | `False` | `False` | **PASS ✅** |
| **Case D** | Innings 1, Balls Remaining = 60, Score = 60 | `NaN` | `NaN` | `False` | `False` | **PASS ✅** |
| **Edge 1: Missing Balls** | Innings 2, Balls Remaining = `NaN`, Req Runs = 10 | `NaN` | `NaN` | `False` | `False` | **PASS ✅** |
| **Edge 2: Overshot Target** | Innings 2, Target = 100, Score = 105 (Req Runs = 0) | `0.00` | `0.00` | `False` | `False` | **PASS ✅** |
| **Edge 3: Negative Balls** | Innings 2, Balls Remaining = -1, Req Runs = 10 | `NaN` | `NaN` | `False` | `False` | **PASS ✅** |

### 2.3 Mathematical Proofs
1. **Case A (Impossible Chase):** $\frac{10}{0}$ is undefined ($\infty$). RRR returns `NaN`. `impossible_chase_state` evaluates to `(Inn == 2) & (Balls == 0) & (ReqRuns > 0) = True`.
2. **Case B (Target Already Met with 0 balls):** $\frac{0}{0}$ is undefined. RRR returns `NaN`. `impossible_chase_state` evaluates to `False` (because $0 > 0$ is `False`).
3. **Case C (Last Ball Steep Chase):** $\text{RRR} = \frac{22}{1} \times 6.0 = 132.0$. Unclipped raw cricket rate is strictly preserved. `impossible_chase_state = False`.
4. **Case D (Innings 1):** Target setting phase has no RRR or chase state. Both evaluate to `NaN` and `False`.

---

## Check 3 — Validation Suite Architectural Audit

An inspection of `src/validate_pipeline.py` revealed several critical observations regarding assertion counts and false-positive test risks:

### 3.1 Test Numbering & Assertion Counts
- **Discrepancy:** The suite header states *"15-POINT COMPREHENSIVE PIPELINE VALIDATION SUITE"*, but the console summary reported *"16/16 TESTS PASSED"*.
- **Cause:** A dedicated test for dual extras was inserted and named `[TEST 6B]`. This created 16 distinct test keys in `test_results`:
  - `test_01` to `test_06` (6 tests)
  - `test_06b` (1 test)
  - `test_07` to `test_15` (9 tests)
  - Total executed test keys = $6 + 1 + 9 = \mathbf{16}$.
- **Independent Assertions:** Each test key executes between 1 and 194,014 vectorized boolean assertions (e.g. Test 10 validates 194,014 rows; Test 15 validates recurrence across 1,660 innings). The suite executes over 500,000 element-wise assertions.

### 3.2 False-Positive Test Risks Identified
The audit identified two tests with potential false-positive risks when run exclusively on historical dataset deliveries:
1. **Test 8 (`test_08_rrr_nan_when_zero_balls_remain`):**
   - The test filtered for deliveries where `legal_balls_remaining_before == 0`.
   - Because no bowler delivers a ball when 0 legal balls remain in a 20-over match, the filtered slice returned 0 rows.
   - In pandas, calling `.isna().all()` on an empty Series returns `True`.
   - **Risk:** The test passed vacuously on historical data without actually encountering a 0-ball delivery row.
2. **Test 9 (`test_09_impossible_chase_state_flag`):**
   - The test evaluated `imp_mask = inn2_mask & (balls_rem == 0) & (req_runs > 0)`.
   - Across all 194,014 historical rows, `imp_mask` was `False` for all rows.
   - `actual_imp` was also `False` for all rows.
   - Thus, `(actual_imp == imp_mask).all()` evaluated to `True`.
   - **Risk:** While the boolean logic is 100% mathematically correct (as proven by our synthetic tests in Check 2), testing it on historical data alone did not assert a `True` condition.
3. **Test 14 (`test_14_dls_units_verified`):**
   - Probed `Match 37354` using `inn: 1`.
   - Because target is always `NaN` in Innings 1, it validated that Innings 1 target is `NaN`, while the actual revised target (94.0 in Innings 2) was not asserted in the test harness.

---

## 4. Auditor Recommendations for Test Harness Hardening

While the production code and processed data are 100% correct, the validation suite should be updated prior to final submission:
1. **Renumber Tests:** Officially renumber the suite to 16 distinct integer tests (Tests 1 through 16).
2. **Incorporate Synthetic Edge Tests:** Add an explicit in-memory synthetic fixture to `src/validate_pipeline.py` that directly runs Cases A, B, C, and D so that zero-denominator and impossible chase conditions are asserted on non-empty vectors.
3. **Target Innings 2 for Match 37354:** In Test 14, change `{"mid": 37354, "inn": 1, "exp_target": np.nan}` to `{"mid": 37354, "inn": 2, "exp_target": 94.0}`.

---

## 5. Final Forensic Verdict

> [!IMPORTANT]
> **AUDITOR VERDICT: PIPELINE IS 100% SOUND & SAFE TO APPROVE FOR MASTER TASK 04.**  
> 1. **DLS Target Integrity:** Match 37354 correctly carries `target = 94.0` on every delivery in Innings 2. All 34 DLS matches reconcile with 100% accuracy.  
> 2. **RRR & Edge Case Integrity:** Synthetic testing confirmed that Case A, Case B, Case C, Case D, and negative/missing edge cases behave with exact mathematical precision.  
> 3. **Raw Data Safety:** All 6 raw CSV files in `data/raw/` remain untouched.  
> 4. **Readiness:** The pipeline data in `data/processed/` is completely verified and ready for Master Task 04 (Pressure Engine & Modeling).

