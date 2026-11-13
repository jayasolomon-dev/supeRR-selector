# SUPERR SELECTOR — PIPELINE QUALITY REVIEW REPORT
**Document Reference:** `reports/pipeline_quality_review.md`  
**Author:** Senior Cricket Data Auditor & Data Engineering Specialist  
**Project:** SUPERR SELECTOR (Cricket Pressure-Performance Analytics)  
**Date:** November 2026  
**Status:** Audit Complete — Pending Stakeholder Sign-Off  

---

## Executive Summary

Following the execution of **Master Task 03 (Data Filtering & Feature Pipeline)**, this independent quality review was commissioned under **Master Task 03.1** to investigate reported discrepancies and edge cases in the data preparation and match-state reconstruction pipeline.

This audit audited five critical dimensions:
1. **Match Count Reconciliation:** Reconciled the previous Dataset Audit (883 total, 16 zero-delivery matches, 867 with deliveries) against the Feature Pipeline Report (883 total, 17 abandoned, 866 with deliveries).
2. **Required Run Rate (RRR) Cap Behavior:** Evaluated the mathematical and algorithmic behavior of the RRR formula in `src/data_pipeline.py` against reported case-study values of 42.0, 48.0, and 132.0.
3. **Current Run Rate (CRR) Zero-Denominator Edge Case:** Investigated deliveries where `legal_balls_before == 0` and `score_before > 0` (114 instances) and assessed how zero legal balls are distinguished from zero runs.
4. **Delivery Runs & Extras Validation:** Verified whether `ball_total_runs = runs + extras1_runs + extras_2_runs` holds across all 200,999 raw deliveries, and evaluated the representation of wides, oversteps, byes, leg-byes, penalty runs, and "other" extras.
5. **Referential Integrity & Safety Verification:** Audited join integrity, temporal leakage prevention, and confirmed that zero raw CSV files were altered.

---

## Check 1 — Match Count Discrepancy & Zero-Delivery Analysis

### 1.1 The Reported Discrepancy
* **Dataset Audit Report (`reports/dataset_audit.md`):**
  * 883 total matches in `matches.csv`
  * 16 matches with 0 deliveries in `ball_by_ball.csv`
  * 867 matches with valid deliveries in `ball_by_ball.csv`
* **Feature Pipeline Report (`reports/feature_pipeline_report.md`):**
  * 883 total matches
  * 17 matches reported under "Abandoned (0 balls)"
  * 866 matches with deliveries (222 IPL + 644 T20I)

### 1.2 Root Cause Analysis
To determine the root cause, an empirical cross-join was executed between `data/raw/matches.csv` and `data/raw/ball_by_ball.csv`:
1. In `matches.csv`, there are **883 matches** (227 IPL, 656 T20I).
2. Matches with **zero deliveries** in `ball_by_ball.csv`: Exactly **16 matches** (4 IPL, 12 T20I).
3. Matches with `result == 'Match Abandoned'` in `matches.csv`: Exactly **19 matches** (5 IPL, 14 T20I).
4. The discrepancy of 1 match originates from **Match ID 20226** (IPL 2023, Match 45: Lucknow Super Giants vs Chennai Super Kings on 2023-05-03 at Lucknow):
   - In `matches.csv`, its official result is `Match Abandoned`.
   - However, **118 deliveries (19.2 overs) were actually bowled** (LSG scored 125/7 before torrential rain ended play).
   - The previous pipeline report conflated **total abandoned IPL matches (5)** with **zero-delivery IPL matches (4)**.
   - It summed $5 \text{ (IPL abandoned)} + 12 \text{ (T20I zero deliveries)} = 17$, labeled the metric "Abandoned (0 balls)", and incorrectly subtracted 17 from 883, yielding 866.
   - In addition, two T20I matches (Match 15410: IND vs SA, 22 balls; Match 21406: PAK vs NZ, 118 balls) were abandoned after play started.

### 1.3 Audit Evidence: All 16 Matches with Zero Deliveries
The following 16 matches in `matches.csv` have zero balls recorded in `ball_by_ball.csv` (called off before toss/first ball without play):

| Match ID | Comp ID | Competition Name | Match Date | Home Team | Away Team | Official Result | Deliveries Bowled |
|:---:|:---:|:---|:---:|:---|:---|:---:|:---:|
| **31281** | 2193 | IPL 2024 | 2024-05-13 | Gujarat Titans | Kolkata Knight Riders | Match Abandoned | 0 |
| **31284** | 2193 | IPL 2024 | 2024-05-16 | Sunrisers Hyderabad | Gujarat Titans | Match Abandoned | 0 |
| **31288** | 2193 | IPL 2024 | 2024-05-19 | Rajasthan Royals | Kolkata Knight Riders | Match Abandoned | 0 |
| **40761** | 2725 | IPL 2025 | 2025-05-17 | Royal Challengers Bengaluru | Kolkata Knight Riders | Match Abandoned | 0 |
| **32610** | 2354 | Pakistan in England T20I Series 2024 | 2024-05-22 | England | Pakistan | Match Abandoned | 0 |
| **32612** | 2354 | Pakistan in England T20I Series 2024 | 2024-05-28 | England | Pakistan | Match Abandoned | 0 |
| **32622** | 2398 | Netherlands Tri-Nation T20I Series 2024 | 2024-05-20 | Ireland | Scotland | Match Abandoned | 0 |
| **38797** | 2442 | Pakistan in South Africa T20I Series 2024 | 2024-12-14 | South Africa | Pakistan | Match Abandoned | 0 |
| **36564** | 2548 | Australia in England T20I Series 2024 | 2024-09-15 | England | Australia | Match Abandoned | 0 |
| **36210** | 2628 | South Africa in England T20I Series 2025 | 2025-09-14 | England | South Africa | Match Abandoned | 0 |
| **41502** | 2873 | West Indies in Ireland T20I Series 2025 | 2025-06-12 | Ireland | West Indies | Match Abandoned | 0 |
| **41503** | 2873 | West Indies in Ireland T20I Series 2025 | 2025-06-14 | Ireland | West Indies | Match Abandoned | 0 |
| **42030** | 2921 | South Africa in India T20I Series 2025 | 2025-12-17 | India | South Africa | Match Abandoned | 0 |
| **46008** | 3174 | England in Ireland T20I series 2025 | 2025-09-19 | Ireland | England | Match Abandoned | 0 |
| **48513** | 3317 | Pakistan in Sri Lanka T20I Series 2026 | 2026-01-10 | Sri Lanka | Pakistan | Match Abandoned | 0 |
| **50189** | 3433 | New Zealand in Bangladesh T20I Series 2026 | 2026-04-29 | Bangladesh | New Zealand | Match Abandoned | 0 |

### 1.4 Audit Evidence: The 3 Abandoned Matches WITH Deliveries
These matches were officially abandoned due to weather after play had begun:

| Match ID | Comp ID | Competition Name | Match Date | Home Team | Away Team | Official Result | Deliveries Bowled |
|:---:|:---:|:---|:---:|:---|:---|:---:|:---:|
| **15410** | 1439 | South Africa in India T20I Series 2022 | 2022-06-19 | India | South Africa | Match Abandoned | 22 (3.3 ov) |
| **20226** | 1715 | IPL 2023 | 2023-05-03 | Lucknow Super Giants | Chennai Super Kings | Match Abandoned | 118 (19.2 ov) |
| **21406** | 1799 | New Zealand in Pakistan T20I Series 2023 | 2023-04-20 | Pakistan | New Zealand | Match Abandoned | 118 (18.5 ov) |

### 1.5 Reconciliation Verdict
* **Total Matches:** 883
* **Zero-Delivery Matches:** Exactly 16 (4 IPL, 12 T20I)
* **Matches with Deliveries:** Exactly 867 (223 IPL, 644 T20I)
* **Conclusion:** The discrepancy was purely a **reporting error** in the pipeline markdown table where Match 20226 was misclassified under "0 balls". The actual data files, filtering logic, and delivery tables in `data/processed/` contain all 867 matches with complete integrity.

---

## Check 2 — RRR Cap & Case-Study Verification

### 2.1 The Issue
The feature pipeline report claimed that Required Run Rate (RRR) is capped at 36.0 runs per over. However, reported chase case studies exhibited RRR values of **42.0**, **48.0**, and **132.0**.

### 2.2 Code Inspection (`src/data_pipeline.py`)
Lines 237–241 of `src/data_pipeline.py` implement RRR as follows:
```python
safe_balls_rem = np.where(legal_balls_remaining_before > 0, legal_balls_remaining_before, 1)
rrr_calc = (df["required_runs_before"] / safe_balls_rem) * 6.0
df["required_run_rate_before"] = np.where(
    df["legal_balls_remaining_before"] > 0,
    rrr_calc,
    np.where(df["required_runs_before"] > 0, 36.0, 0.0)
)
```

### 2.3 Mathematical Proof of Case Studies
* **Case Study 1 (RRR = 42.0):**
  - Situation: 14 runs required from 2 legal balls remaining.
  - Formula: $\text{RRR} = \frac{14}{2} \times 6.0 = 7.0 \times 6.0 = 42.0$ runs/over.
* **Case Study 2 (RRR = 48.0):**
  - Situation: 8 runs required from 1 legal ball remaining.
  - Formula: $\text{RRR} = \frac{8}{1} \times 6.0 = 8.0 \times 6.0 = 48.0$ runs/over.
* **Case Study 3 (RRR = 132.0):**
  - Situation: 22 runs required from 1 legal ball remaining.
  - Formula: $\text{RRR} = \frac{22}{1} \times 6.0 = 22.0 \times 6.0 = 132.0$ runs/over.

### 2.4 Audit Finding
1. **The Code Rule:** The constant `36.0` was **NOT** used as a universal ceiling (`clip` or `min(rrr, 36.0)`). It was used **strictly as a zero-denominator fallback** when `legal_balls_remaining_before == 0` and `required_runs_before > 0`.
2. **The Documentation Inconsistency:** The written report stated "RRR capped at 36.0", which misled readers into expecting $\min(\text{RRR}, 36.0)$.
3. **Recommendation for Modeling:**
   - For pure cricket tracking, the raw mathematical required run rate ($\frac{\text{Runs}}{\text{Balls}} \times 6$) accurately reflects mathematical impossibility (> 36 runs/over without extras).
   - For machine learning and pressure index models, unconstrained RRR of 132.0 creates extreme outlier skew. A true ceiling cap (e.g. `np.clip(rrr, 0.0, 36.0)` or `48.0`) is recommended during pressure feature engineering (Task 04).

---

## Check 3 — CRR Zero-Denominator Edge Case

### 3.1 The Issue
Investigation of deliveries where:
- `legal_balls_before == 0`
- `score_before > 0`

### 3.2 Empirical Occurrence in Processed Dataset
Across the 194,014 processed deliveries, exactly **114 deliveries** have `legal_balls_before == 0` and `score_before > 0`.
Every single one of these 114 instances occurs when an innings commences with an illegal delivery (e.g. Ball 1 is a Wide or an Overstep/No-Ball) or multiple consecutive wides before the first legal ball is completed:
- Example: Bowler bowls a wide on delivery 1. Innings score becomes 1/0, but 0 legal balls have been completed.
- On delivery 2, `score_before = 1`, but `legal_balls_before = 0`.

### 3.3 Code Inspection & The Conflation Problem
In `src/data_pipeline.py` (lines 232–235):
```python
df["current_run_rate_before"] = np.where(
    df["legal_balls_before"] > 0,
    (df["score_before"] / df["legal_balls_before"]) * 6.0,
    0.0
)
```
When `legal_balls_before == 0`, the code returns `0.0`.
This creates a **semantic conflation**:
1. Case A: Team has faced 4 legal balls and scored 0 runs $\implies$ genuine CRR of $0.00$.
2. Case B: Team has scored 2 runs off wides with 0 legal balls bowled $\implies \frac{2}{0} \implies$ mathematically undefined ($\infty$).

### 3.4 Recommended Representation
* In cricket scoring convention, CRR is **Undefined / Not Applicable** until at least 1 legal ball has been bowled.
* For analytical clarity:
  - In pandas/data exports, represent CRR before the first legal ball as `NaN` (or `None`).
  - When numerical arrays are required for models, either document `0.0` as an explicit zero-ball sentinel, or provide a flag `has_legal_balls_before`.

---

## Check 4 — Delivery Runs & Extras Validation

### 4.1 Verification of `ball_total_runs`
We audited all 200,999 raw deliveries in `data/raw/ball_by_ball.csv` to verify whether:
$$\text{ball\_total\_runs} = \text{runs} + \text{extras1\_runs} + \text{extras\_2\_runs}$$
holds true.

**Result: 100% Mathematically Valid.**
The total runs per ball ranges strictly from 0 to 7:
- **0 runs:** 68,027 deliveries
- **1 run:** 82,209 deliveries
- **2 runs:** 13,196 deliveries
- **3 runs:** 751 deliveries
- **4 runs:** 23,564 deliveries
- **5 runs:** 438 deliveries (includes 270 wides for 5, and 1 penalty of 5)
- **6 runs:** 12,741 deliveries
- **7 runs:** 73 deliveries (no-balls where a six was hit, or no-ball + overthrows)

### 4.2 Breakdown by `extras_type`

| `extras_type` | Delivery Count | `runs` (Bat Runs) | `extras1_runs` | `extras_2_runs` | Total Run Formula Verified |
|:---|:---:|:---:|:---:|:---:|:---:|
| **None (Ordinary)** | 189,167 | 0, 1, 2, 3, 4, 6 | 0 (189,166), 1 (1 row) | 0 (189,166), 1 (1 row) | $\text{runs} + 0 + 0$ |
| **wide** | 7,714 | 0 (100%) | 1, 2, 3, 4, 5 | 0 (100%) | $0 + \text{ext1} + 0$ |
| **legbyes** | 2,748 | 0 (2,747), 1 (1 row) | 1, 2, 3, 4, 5 | 0 (100%) | $0 + \text{ext1} + 0$ |
| **Overstep** | 576 | 0, 1, 2, 3, 4, 6 | 1 (100%) | 0 (555), 1 (12), 4 (9) | $\text{runs} + 1 + \text{ext2}$ |
| **byes** | 529 | 0 (100%) | 1, 2, 3, 4, 5 | 0 (100%) | $0 + \text{ext1} + 0$ |
| **other** | 264 | 0, 1, 2, 3, 4, 6 | 1 (100%) | 0 (250), 1 (7), 4 (7) | $\text{runs} + 1 + \text{ext2}$ |
| **Penalty** | 1 | 0 | 5 (100%) | 0 | $0 + 5 + 0 = 5$ |

### 4.3 Crucial Discovery: `extras_type == 'other'` are No-Balls
An in-depth investigation into the 264 deliveries with `extras_type == 'other'` revealed:
1. Every over containing an `other` extra has **7 or more deliveries** (the ball is re-bowled).
2. `extras1_runs` is always **exactly 1** (the 1-run penalty).
3. Batters can score runs off the bat (`runs` has 1, 2, 3, 4, 6).
4. The only dismissal recorded across all 264 deliveries is **Run Out** (3 dismissals: Matches 14102, 24658, 30882).
5. In 14 cases, `extras_2_runs` contains additional byes/leg-byes off the delivery.

**Conclusion:** `other` denotes non-overstep No-Balls (e.g. above waist-height full tosses, bouncer violations, fielding restriction breaches).  
**Pipeline Gap Identified:** In `src/data_pipeline.py`, `is_noball` was defined only as `clean_extras == "overstep"`, which meant the 264 `other` deliveries were classified as legal deliveries. They should be classified as no-balls (`clean_extras.isin(["overstep", "other"])`) in future updates.

### 4.4 Scorer Entry Anomalies (3 Isolated Rows)
Three minor clerical data-entry anomalies were identified in the raw records:
1. **Index 113765 (Match 37099, Inn 1, Ov 14.1):** Striker Nimesh Vimukthi vs Qais Ahmad. `extras_type = 'legbyes'`, but `runs = 1`, `extras1_runs = 0`. Total = 1.
2. **Index 36854 (Match 17555, Inn 1, Ov 5.4):** Striker Dawid Malan vs Haris Rauf. `extras_type = NaN`, `runs = 0`, `extras_2_runs = 1`. Total = 1.
3. **Index 107489 (Match 36097, Inn 2, Ov 8.6):** Striker Rassie van der Dussen vs Romario Shepherd. `extras_type = NaN`, `runs = 0`, `extras1_runs = 1`. Total = 1.

Because `ball_total_runs` uses `runs + ext1 + ext2`, the total match score remains 100% accurate despite the mislabeling.

---

## Check 5 — Final Integrity Verification & Audit Reconciliation

| Verification Item | Specification / Requirement | Audit Result | Status |
|:---|:---|:---|:---:|
| **Total Raw Matches** | 883 matches in `matches.csv` | Exactly 883 matches accounted for | **PASS** |
| **IPL Matches** | 227 total (223 with balls, 4 with 0 balls) | Reconciled 227 (223 + 4) | **PASS** |
| **T20I Matches** | 656 total (644 with balls, 12 with 0 balls) | Reconciled 656 (644 + 12) | **PASS** |
| **Matches with Deliveries** | $883 - 16 = 867$ matches | Exactly 867 matches in processed datasets | **PASS** |
| **Referential Integrity** | Every delivery joins to a valid match | 194,014 / 194,014 deliveries (100%) join cleanly | **PASS** |
| **Future Data Leakage** | Pre-delivery states do not leak ball outcome | Grouped cumulative sum minus current ball verified: 0 leakages | **PASS** |
| **Raw Data Immutability** | No original CSV modified or overwritten | All 6 raw CSVs in `data/raw/` untouched | **PASS** |

---

## Summary of Recommendations for Master Task 04

Before building the Pressure Scoring Engine, the following adjustments are recommended:
1. **Document Match Count Reconciliation:** Update report documentation to cite 867 active matches and explain Match 20226's partial play.
2. **Include `'other'` in No-Ball Definitions:** In `src/data_pipeline.py`, update `is_noball = clean_extras.isin(["overstep", "other"])` so that the 264 height/fielding no-balls are not counted as legal deliveries.
3. **Formalize RRR Pressure Ceiling:** Explicitly apply `np.clip(rrr, 0.0, 36.0)` when computing the pressure index to avoid distortion from single-ball outliers.
4. **Distinguish CRR at 0 Legal Balls:** Distinguish 0 legal balls from 0 runs by setting `current_run_rate_before = np.nan` when `legal_balls_before == 0`.

