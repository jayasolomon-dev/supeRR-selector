# SUPERR SELECTOR — FINAL SCOPE RECONCILIATION & CRICKET RULE AUDIT REPORT
**Document Reference:** `reports/final_scope_reconciliation.md`  
**Author:** Senior Cricket Data Engineer & Independent Quality Auditor  
**Project:** SUPERR SELECTOR (Cricket Pressure-Performance Analytics Platform)  
**Date:** November 2026  
**Status:** Scope Reconciled & Rule Verified — Pending User Approval  

---

## Executive Summary

Under **Master Task 03.2**, an exhaustive, ground-truth audit of the raw data, processed datasets, and pipeline code was conducted to resolve discrepancies between earlier audit reports and verify core cricket scoring logic.

### Core Audit Determinations
1. **Scope Discrepancy Resolved:** The real competition breakdown across all **883 matches** in `matches.csv` is:
   * **IPL:** **371 matches** (367 played with deliveries, 4 abandoned without a ball bowled).
   * **Men's T20I:** **482 matches** (470 played with deliveries, 12 abandoned without a ball bowled).
   * **Excluded Developmental T20:** **30 matches** (all 30 played with deliveries).
   * Total Matches in raw data = $371 + 482 + 30 = \mathbf{883}$.
   * Total playable in-scope matches = $367 + 470 = \mathbf{837}$.
   * The "227 IPL / 656 T20I" figures reported in the previous quality review turn were an arithmetic conflation error ($222 + 5 = 227$; $883 - 227 = 656$). The original Dataset Audit figures (371 IPL / 482 T20I) were empirically accurate.
2. **Processed Data Coverage Verified:**
   * `ipl_deliveries.csv`: **87,687 deliveries** across **367 distinct matches** (100% of playable IPL matches).
   * `t20i_deliveries.csv`: **106,327 deliveries** across **470 distinct matches** (100% of playable T20I matches).
   * Total processed deliveries: **194,014** across **837 matches**. Zero missing matches; zero excluded matches present.
3. **`extras_type == 'other'` (264 records) is 100% No-Balls:** Every single record has `extras1_runs == 1`, allows batting runs, allows byes/leg-byes off the no-ball in `extras_2_runs`, forces the over to be re-bowled (7+ deliveries), and the only dismissals recorded are `RunOut` (3 times). They are definitively non-front-foot no-balls.
4. **Cricket Rule Corrections Required:** `other` must be included in no-balls and bowler extras, bowler runs conceded must not debit byes/leg-byes (`extras_2_runs`) to the bowler, and CRR/RRR must use `NaN` for undefined edge cases rather than heuristics.
5. **DLS Units Verified:** `first_inn_revised_overs` and `second_inn_revised_overs` in `matches.csv` are stored in **LEGAL BALLS**, NOT OVERS (e.g. `90.0` represents 90 legal balls / 15 overs; `48.0` represents 48 legal balls / 8 overs). `revised_target` is stored in **RUNS**.

---

## Check 1 — Competition & Match Count Reconciliation

### 1.1 The Discrepancy Investigated
* **Dataset Audit (`dataset_audit.md`):** IPL = 371, T20I = 482, Other = 30, Total = 883.
* **Pipeline Quality Review (`pipeline_quality_review.md`):** IPL = 227, T20I = 656, Total = 883.

### 1.2 Empirical Evidence from Raw Metadata
A complete SQL/Pandas merge of `data/raw/matches.csv` against `data/raw/competitions.csv` and cross-referenced with `data/raw/ball_by_ball.csv` yields the following exact distribution:

| Category | Comp ID | Competition Name | Season | Match Format | Total Matches | Matches With Deliveries | Matches Without Deliveries (0 balls) |
|:---|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| **IPL** | 1358 | IPL 2022 | 2022 | T20 | 74 | 74 | 0 |
| **IPL** | 1715 | IPL 2023 | 2023 | T20 | 74 | 74 | 0 |
| **IPL** | 2193 | IPL 2024 | 2024 | T20 | 74 | 71 | 3 (31281, 31284, 31288) |
| **IPL** | 2725 | IPL 2025 | 2025 | T20 | 75 | 74 | 1 (40761) |
| **IPL** | 3298 | IPL 2026 | 2026 | T20 | 74 | 74 | 0 |
| **IPL Subtotal** | **5 Comps** | — | — | **T20** | **371** | **367** | **4** |
| **Excluded** | 2670 | Mens T20 Emerging Teams Asia Cup 2024 | 2024 | T20 | 15 | 15 | 0 |
| **Excluded** | 3289 | Asia Cup Rising Stars 2025 | 2025 | T20 | 15 | 15 | 0 |
| **Excluded Subtotal**| **2 Comps** | — | — | **T20** | **30** | **30** | **0** |
| **Men's T20I** | 131 Comps | Bilateral & ICC T20I Tournaments | 2022–2026 | T20I | 482 | 470 | 12 (32610, 32612, 32622, 38797, 36564, 36210, 41502, 41503, 42030, 46008, 48513, 50189) |
| **T20I Subtotal** | **131 Comps**| — | — | **T20I** | **482** | **470** | **12** |
| **TOTAL** | **138 Comps**| — | — | — | **883** | **867** | **16** |

*(Note: `competitions.csv` contains 141 rows; 3 T20I competitions [IDs 3405, 3473, and another scheduled fixture] have 0 matches in `matches.csv`, leaving 138 active competitions).*

### 1.3 How the "227 / 656" Error Occurred
The "227 IPL / 656 T20I" numbers in the previous quality review turn resulted from an arithmetic error during draft notes:
1. Seasons 2022, 2023, and 2024 have $74 \times 3 = 222$ matches.
2. Adding 5 abandoned IPL matches resulted in $222 + 5 = 227$.
3. Subtracting from the total gave $883 - 227 = 656$.
4. **Audit Conclusion:** The original Dataset Audit figures (**371 IPL, 482 T20I, 30 Excluded, 883 Total**) are 100% verified by raw data.

### 1.4 Classification Logic Validation
* **IPL Classification:** `comp_name.str.contains('IPL', case=False) & (match_format == 'T20')`. This captures exactly the 5 IPL seasons (comp IDs: 1358, 1715, 2193, 2725, 3298) and zero other competitions.
* **Men's T20I Classification:** `match_format == 'T20I'`. This captures all 131 international series.
* **Excluded Regional Developmental:** Comp IDs `2670` (Emerging Teams) and `3289` (Rising Stars) have `match_format == 'T20'` but do not contain "IPL". They are correctly isolated as "Other" and excluded.

---

## Check 2 — Processed Match Coverage

We audited the distinct match IDs in the output files inside `data/processed/`:

```
data/processed/ipl_deliveries.csv:
  - Distinct Match IDs: 367
  - Total Deliveries:   87,687
  - Scope:              Matches from Comps [1358, 1715, 2193, 2725, 3298]

data/processed/t20i_deliveries.csv:
  - Distinct Match IDs: 470
  - Total Deliveries:   106,327
  - Scope:              Matches from 131 T20I competitions

Combined:
  - Total Distinct Matches: 837 (367 IPL + 470 T20I)
  - Total Deliveries:       194,014 (87,687 IPL + 106,327 T20I)
  - Match ID Overlap:       0 matches
```

### Match Reconciliation Audit:
* **In-Scope Raw IPL Matches:** 371
  * 367 matches had deliveries $\rightarrow$ **All 367 are present in `ipl_deliveries.csv`** (100% coverage).
  * 4 matches had 0 deliveries (abandoned without toss: 31281, 31284, 31288, 40761) $\rightarrow$ correctly omitted from ball-by-ball.
* **In-Scope Raw T20I Matches:** 482
  * 470 matches had deliveries $\rightarrow$ **All 470 are present in `t20i_deliveries.csv`** (100% coverage).
  * 12 matches had 0 deliveries (abandoned without toss) $\rightarrow$ correctly omitted from ball-by-ball.
* **Excluded Developmental Matches:** 30
  * Exactly 0 of these 30 matches appear in `ipl_deliveries.csv` or `t20i_deliveries.csv`.
* **Zero Unexpected Matches:** Every single distinct match ID in processed datasets maps to a valid in-scope competition.

---

## Check 3 — Exact Classification of `extras_type == 'other'`

Across `ball_by_ball.csv`, exactly **264 deliveries** have `extras_type == 'other'`. We conducted a forensic inspection comparing them to confirmed `extras_type == 'Overstep'` (576 deliveries).

### 3.1 Forensic Comparison Table

| Attribute / Rule | `Overstep` No-Balls ($n=576$) | `other` Extras ($n=264$) | Evidence-Based Interpretation |
|:---|:---:|:---:|:---|
| **Penalty Runs (`extras1_runs`)** | 1 run in **100.0%** (576/576) | 1 run in **100.0%** (264/264) | Identical 1-run penalty charged |
| **Bat Runs Permitted (`runs > 0`)** | **58.5%** (337 deliveries) | **51.5%** (136 deliveries) | Batter actively plays stroke; hits 1, 2, 3, 4, 6 |
| **Secondary Extras (`extras_2_runs > 0`)** | **3.6%** (21 deliveries) | **5.3%** (14 deliveries) | Byes / leg-byes / overthrows off no-ball |
| **Wickets Recorded** | 5 dismissals | 3 dismissals | Wickets can occur |
| **Dismissal Types** | **100% `RunOut`** (5/5) | **100% `RunOut`** (3/3) | **Law 21 Compliance:** Bowled, Caught, LBW, Stumped strictly prohibited |
| **Re-bowled Delivery (Over Length)** | Over contains $\ge 7$ balls in all completed overs | Over contains $\ge 7$ balls in all completed overs | Ball is dead for legality; must be re-bowled |
| **Overs with $\le 6$ Deliveries** | 0% (except match ends) | 9 instances (100% match/innings end) | Verified 100% end of match/chase |

### 3.2 Audit Conclusion on `other`
**All 264 records are unequivocally No-Balls.**  
Specifically, cricket scoring systems categorize no-balls into:
1. `Overstep`: Front-foot crease violation.
2. `other`: Non-crease no-balls (e.g. above waist-height full toss, bouncer / height violation, fielding restriction violation with too few fielders inside the 30-yard ring, or wicketkeeper encroaching before the ball is delivered).

---

## Check 4 — Legal Ball and Batter Ball Rules

In official cricket scoring (ICC Standard T20 Playing Conditions & MCC Laws 21, 22), the following rules govern delivery accounting:

| Delivery Type | Legal Delivery (Bowler Over Count)? | Batter Ball Faced? | Bowler Runs Conceded? | Byes / Leg-byes Debited to Bowler? |
|:---|:---:|:---:|:---:|:---:|
| **Ordinary Ball** | **YES** | **YES** | Bat Runs (`runs`) | N/A |
| **Wide** | **NO** | **NO** | Wide Penalty + Runs (`ext1`) | NO |
| **Overstep (No-Ball)** | **NO** | **YES** | Bat Runs (`runs`) + 1 Penalty (`ext1`) | **NO** (`ext2` is team extra) |
| **other (No-Ball)** | **NO** | **YES** | Bat Runs (`runs`) + 1 Penalty (`ext1`) | **NO** (`ext2` is team extra) |
| **Byes** | **YES** | **YES** | **0** | **NO** |
| **Leg-byes** | **YES** | **YES** | **0** | **NO** |
| **Penalty (Helmet/Law 41)**| **YES** (or unbowled) | **NO** | **0** | **NO** |

### Critical Code Gaps Identified in Existing `src/data_pipeline.py`:
1. **`is_legal_ball` Gap:** The code used `~clean_extras.isin(["wide", "overstep"])`. Because `other` was omitted, 264 no-balls were counted as legal deliveries.
2. **`bowler_runs_conceded` Gaps:**
   * `other` was omitted from `is_bowler_extra`, failing to debit the 1-run penalty to the bowler.
   * `is_bowler_extra` added `ext1 + ext2`. In 35 deliveries where both `ext1 > 0` and `ext2 > 0` (e.g. 1 no-ball + 4 leg byes), the bowler was erroneously debited 5 runs instead of 1 run! `ext2` is team extras (byes/leg-byes off no-ball), not bowler runs.

---

## Check 5 — CRR and RRR Edge Cases

### 5.1 Current Run Rate (CRR)
* **Edge Case:** Innings commencing with illegal deliveries (e.g. Ball 1 is a Wide or No-Ball). Across the dataset, **114 deliveries** have `legal_balls_before == 0` and `score_before > 0`.
* **Current Code Behavior:** Returns `0.0`.
* **Flaw:** Conflates a team that has faced legal deliveries and scored 0 runs ($\text{CRR} = 0.00$) with a team that has scored runs off 0 legal deliveries ($\frac{\text{Runs}}{0} = \text{Undefined}$).
* **Recommendation:** Set `current_run_rate_before = np.nan` when `legal_balls_before == 0`.

### 5.2 Required Run Rate (RRR)
* **Edge Case:** Zero legal balls remaining with runs still needed (`legal_balls_remaining_before == 0` and `required_runs_before > 0`).
* **Current Code Behavior:** Silently assigns `36.0`.
* **Flaw:** `36.0` is an achievable cricket run rate (6 sixes in an over). Assigning 36.0 to an mathematically impossible state (e.g. 15 runs needed off 0 balls) distorts both cricket reality and data transparency. Furthermore, when 1 ball remains and 22 runs are needed, the raw rate is $132.0$.
* **Recommendation:**
  1. **Raw Cricket Metric:** `required_run_rate_before` should be `np.nan` (or `np.inf`) when `legal_balls_remaining_before == 0` and runs are needed.
  2. **Model Feature (Task 04):** A separate normalized, capped feature (e.g. `pressure_rrr_input = np.clip(rrr, 0.0, 36.0)`) will be engineered specifically for ML pressure modeling without corrupting the raw match state.

---

## Check 6 — DLS Revised Overs Units Verification

We audited all 34 matches in `matches.csv` with DLS revised targets or revised overs:

### 6.1 Empirical Evidence from Representative Matches
1. **Match 21586 (IPL 2023 Final: CSK vs GT):**
   * `first_inn_revised_overs = NaN` (GT batted full 20 overs, 120 balls).
   * `second_inn_revised_overs = 90.0`.
   * `revised_target = 171.0`.
   * **Ground Truth:** CSK's chase was officially reduced to **15 overs** ($15 \times 6 = \mathbf{90}$ legal balls). CSK faced 90 legal balls and chased 171.
2. **Match 37354 (Australia vs Pakistan, 2024-11-14):**
   * `first_inn_revised_overs = 42.0`.
   * `second_inn_revised_overs = 42.0`.
   * `revised_target = 94.0`.
   * **Ground Truth:** Match reduced to **7 overs** per side ($7 \times 6 = \mathbf{42}$ legal balls).
3. **Match 54711 (India vs Ireland):**
   * `first_inn_revised_overs = 30.0`.
   * `second_inn_revised_overs = 30.0`.
   * `revised_target = 33.0`.
   * **Ground Truth:** Match reduced to **5 overs** per side ($5 \times 6 = \mathbf{30}$ legal balls).
4. **Match 21070 (Bangladesh vs Ireland):**
   * `second_inn_revised_overs = 48.0` $\rightarrow$ **8 overs** ($8 \times 6 = \mathbf{48}$ legal balls).

### 6.2 Audit Determination
* **`first_inn_revised_overs` and `second_inn_revised_overs` are stored in LEGAL BALLS, NOT OVERS.**
* The word "overs" in the column title is a data provider naming misnomer.
* `revised_target` is stored in **RUNS**.
* **Pipeline Status:** `src/data_pipeline.py` correctly treated the values as balls (`rev_inn1_balls = int(float(rev1))`), but the code lacked an explicit explanatory comment and unit guardrail.

---

## Check 7 — Code Changes Required for Next Task

When approved by the user, the following specific code updates will be made to `src/data_pipeline.py` and `src/features/match_state.py`:

```python
# 1. Update No-Ball and Legality Classification:
is_noball = clean_extras.isin(["overstep", "other"])
is_wide = clean_extras == "wide"
is_legal_ball = ~clean_extras.isin(["wide", "overstep", "other"])

# 2. Update Batter Balls Faced:
is_batter_ball = clean_extras != "wide"  # Includes normal balls, overstep, other, byes, legbyes

# 3. Update Bowler Runs Conceded:
# Bowler conceded = bat runs + wide penalty + no-ball penalties (extras1_runs only, not extras_2_runs)
is_bowler_penalty = clean_extras.isin(["wide", "overstep", "other"])
df["bowler_runs_conceded"] = runs_bat + np.where(is_bowler_penalty, ext1, 0)

# 4. Update Current Run Rate (CRR):
df["current_run_rate_before"] = np.where(
    df["legal_balls_before"] > 0,
    (df["score_before"] / df["legal_balls_before"]) * 6.0,
    np.nan
)

# 5. Update Required Run Rate (RRR):
df["required_run_rate_before"] = np.where(
    df["legal_balls_remaining_before"] > 0,
    (df["required_runs_before"] / df["legal_balls_remaining_before"]) * 6.0,
    np.nan
)
```

---

## Final Safety Assessment & Auditor Verdict

* **Raw Data Status:** Intact and unmodified (100% byte match with source data pack).
* **Current Pipeline Integrity:** High. Competition scoping, join integrity, and temporal sequence (0 future leakage) are solid.
* **Audit Verdict:** **CORRECTION REQUIRED BEFORE APPROVAL.**  
  While the competition scoping and match filtering are 100% correct, the pipeline code requires the 5 specific cricket rule corrections listed in Check 7 (classifying `other` as no-balls, correcting bowler runs conceded, fixing CRR/RRR `NaN` representations, and documenting DLS ball units) before moving to Master Task 04.

