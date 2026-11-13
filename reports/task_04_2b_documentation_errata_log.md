# SUPERR SELECTOR — TASK 04.2B DOCUMENTATION ERRATA LOG

**Document Reference:** `reports/task_04_2b_documentation_errata_log.md`  
**Task Reference:** Task 05.0 Documentation Preflight & Errata Log  
**Author:** Senior Cricket Data Scientist & Quantitative Lead  
**Project:** Rajasthan Royals SupeRR Selector Season 2 Hackathon  
**Target Document Corrected:** `reports/task_04_2b_independent_validation_report.md` (and its artifact copy)  
**Date:** November 12, 2026  
**Status:** **APPROVED & RECONCILED (Option A Adopted)**  

---

## 1. Context and Objective

During Task 04.2B.1 (`reports/task_04_2b_1_methodology_reconciliation_report.md`), an independent quantitative audit reconciled the completed Task 04.2B validation report against the formally approved Task 04.1 Revision 2.1 methodology and the production implementation in `src/features/pressure_engine.py`.

The audit confirmed that:
- Production code and derived datasets are **100% compliant** with the approved Revision 2.1 methodology.
- The three identified discrepancies were **documentation/drafting errata** within the report prose of `task_04_2b_independent_validation_report.md`.
- Under the approved **Option A decision**, these three documentation errata are formally corrected in `reports/task_04_2b_independent_validation_report.md` without modifying any production code or derived datasets.

---

## 2. Errata Record & Reconciliation Log

### Erratum 1: Pressure Category Threshold Boundaries

- **Sections Affected:** Section 5.4 (Line 149) and Section 10.2 Table (Lines 280–281).
- **Original Wording:**
  - Section 5.4: `Category thresholds: Low [0, 40), Moderate [40, 70), High [70, 85), Extreme [85, 100].`
  - Section 10.2 Table:
    ```markdown
    | **Moderate** | $[40, 70)$ | 52.99% | 75.05% | 54.84% | 74.89% |
    | **High**     | $[70, 85)$ |  7.34% |  6.72% |  8.64% |  6.63% |
    ```
- **Corrected Wording:**
  - Section 5.4: `Category thresholds: Low [0, 40), Moderate [40, 65), High [65, 85), Extreme [85, 100].`
  - Section 10.2 Table:
    ```markdown
    | **Moderate** | $[40, 65)$ | 52.99% | 75.05% | 54.84% | 74.89% |
    | **High**     | $[65, 85)$ |  7.34% |  6.72% |  8.64% |  6.63% |
    ```
- **Reason for Correction:** In `src/features/pressure_engine.py` (lines 48, 361–364) and the approved methodology (`reports/pressure_engine_methodology.md:228–232`), Moderate is strictly $[40.0, 65.0)$ and High is strictly $[65.0, 85.0)$. The percentages reported in the Section 10.2 table were already computed using the approved $[40, 65)$ and $[65, 85)$ boundaries. The appearance of "70" was a drafting typo in the markdown text.

---

### Erratum 2: Expected Wickets ($W_{\text{exp}}$) Baseline Reference

- **Sections Affected:** Section 15 (Line 405).
- **Original Wording:**
  - `1. **Powerplay Expected Wickets ($W_{\text{exp}}$) Heuristic:** In Innings 1, the wicket-in-hand component utilizes the baseline $W_{\text{exp}} = 4.5$ expected wickets lost. In overs 1–6, actual wickets lost rarely exceed 2, creating an inherent resource buffer. This is intentional: teams preserving top-order wickets in the Powerplay naturally face lower context pressure, while early wickets trigger immediate resource distress.`
- **Corrected Wording:**
  - `1. **Expected Wickets ($W_{\text{exp}}$) Progression:** In Innings 1, the wicket resource component strictly follows the approved dynamic power curve $W_{\text{exp}} = 6.0 \times (t/120)^{0.80}$. Under this formula, expected wickets evaluate to $2.28$ at the end of the Powerplay (Over 6.0 / ball 36), $3.45$ at Over 10.0, and reach $\approx 4.51$ at Over 14.0 (the empirical milestone referenced in methodology Section 2.4). Because actual Powerplay wickets lost average $\approx 1.61$, top orders preserving wickets face lower context pressure, while early collapses immediately elevate resource distress.`
- **Reason for Correction:** The production code (`src/features/pressure_engine.py:84, 137`) evaluates $W_{\text{exp}} = 6.0 \times (t/120)^{0.80}$ dynamically on every ball. In a standard 120-ball innings, $W_{\text{exp}}$ evaluates to $2.28$ at the end of the Powerplay, not 4.5. The figure 4.5 corresponds to Over 14.0 ($W_{\text{exp}} \approx 4.51$) in the Section 2.4 empirical validation table of `pressure_engine_methodology.md`. The original report text conflated the Over 14.0 milestone with the Powerplay.

---

### Erratum 3: Weight Sensitivity Rank Correlation & Max Delta Qualification

- **Sections Affected:** Section 1 (Executive Summary, Line 27), Section 11.2 (Lines 325–327), and Section 16 Risk Table (Line 416).
- **Original Wording:**
  - Section 1: `Sensitivity audits under $\pm 5\%$ relative weight perturbations on 10,000 deliveries demonstrated near-perfect rank stability (Spearman $\rho \ge 0.999$, average score shift $< 0.45$ points).`
  - Section 11.2 Note: `*\*Note on Case 4 Max $\Delta$: Occurs on boundary-edge terminal deliveries where runway denominator is near zero; the mean shift across all 10,000 deliveries is only 0.348 points, and the rank correlation $\rho = 0.99868$ confirms virtually invariant ordering.*`
  - Section 16: `| **Weight Sensitivity Risk** | **VERY LOW** | $\pm 5\%$ weight perturbations yielded Spearman rank correlations $\rho \ge 0.999$, proving that player pressure groupings are robust. |`
- **Corrected Wording:**
  - Section 1: `Sensitivity audits under $\pm 5\%$ relative weight perturbations on 10,000 deliveries demonstrated near-perfect rank stability. Across the raw diagnostic sample, Case 4 yielded Spearman $\rho = 0.99868$ due to a single post-target terminal delivery artifact in Match 48610 (where the un-overridden test dot product produced a Max $\Delta = 96.159$). On the clean competitive cohort ($\sim\text{is\_target\_met\_delivery}$), Case 4 Spearman correlation is $\rho = 0.99994$ with Max $\Delta = 0.882$ and average score shift $< 0.35$ points.`
  - Section 11.2 Note: `*\*Note on Case 4 Max $\Delta$: The raw maximum shift of $96.159$ occurred on a single post-conclusion delivery in Match 48610 (Over 14.4, is_target_met_delivery = True), where production correctly collapsed the score to 0.00 but the diagnostic test script recomputed an un-overridden raw component dot product. When evaluated on the clean competitive standard cohort, Case 4 exhibits a Max $\Delta = 0.882$, Mean $\Delta = 0.331$, and Spearman $\rho = 0.99994$.*`
  - Section 16: `| **Weight Sensitivity Risk** | **VERY LOW** | $\pm 5\%$ weight perturbations yielded Spearman rank correlations $\rho \ge 0.99868$ on raw sample and $\rho \ge 0.9999$ on clean competitive cohort, proving that player pressure groupings are robust. |`
- **Reason for Correction:** Forensic inspection revealed that in `src/validate_pressure_engine_04_2b.py`, the diagnostic test harness recomputed perturbed scores using `np.dot(c_matrix, w_pert)` without applying the terminal override `if is_target_met_delivery: score = 0.0`. A single post-target ball in Match 48610 (Ball 14.4) had stored `bowling_pressure_score = 0.00`, but its raw component dot product evaluated to $96.159$, producing $\Delta = 96.159$ and pulling the raw Spearman $\rho$ to $0.99868$. Stating $\rho \ge 0.999$ in the executive prose without qualification was mathematically inaccurate for the uncurated sample, though completely true on the clean competitive cohort ($\rho = 0.99994$, Max $\Delta = 0.882$).

---

## 3. Summary of Status

All three documentation errata have been formally corrected in `reports/task_04_2b_independent_validation_report.md` and its artifact copy. Zero code changes were made to `src/features/pressure_engine.py`, and zero data changes were made to `data/derived/*.csv`. The codebase and reports are now in 100% mutual alignment.

