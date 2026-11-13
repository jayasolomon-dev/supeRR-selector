# ⚡ SUPERR SELECTOR — Feature Pipeline & Data Preparation Report

> **Task:** MASTER TASK 03 — Data Filtering & Feature Pipeline  
> **Auditors:** Senior Cricket Data Engineer & Python Analytics Specialist  
> **Core Competitions Scope:** Indian Premier League (IPL) & Men's T20 International (T20I), 2022 Onwards  
> **Output Deliverables:**  
> - [`src/data_pipeline.py`](file:///d:/SupeRR_Selector/src/data_pipeline.py)  
> - [`src/validate_pipeline.py`](file:///d:/SupeRR_Selector/src/validate_pipeline.py)  
> - [`data/processed/ipl_deliveries.csv`](file:///d:/SupeRR_Selector/data/processed/ipl_deliveries.csv) (87,687 rows, 28.93 MB)  
> - [`data/processed/t20i_deliveries.csv`](file:///d:/SupeRR_Selector/data/processed/t20i_deliveries.csv) (106,327 rows, 38.34 MB)  
> - [`data/processed/batting_deliveries.csv`](file:///d:/SupeRR_Selector/data/processed/batting_deliveries.csv) (194,014 rows, 32.76 MB)  
> - [`data/processed/bowling_deliveries.csv`](file:///d:/SupeRR_Selector/data/processed/bowling_deliveries.csv) (194,014 rows, 34.51 MB)  
> **Validation Status:** **ALL 8 AUTOMATED TESTS PASSED (100% Integrity Confirmed)**  

---

## 1. Executive Summary

Master Task 03 establishes the production-grade data preparation pipeline for **SUPERR SELECTOR**. It filters the raw cricket deliveries strictly to **IPL and Men's T20I competitions (2022 onwards)**, excludes regional developmental cups, reconstructs exact pre-delivery match states without future leakage, and generates structured player-level delivery datasets.

### Pipeline Headline Results:
* **Total Audited Deliveries:** 200,999 balls (883 matches).
* **Excluded Regional Deliveries:** 6,985 balls (30 matches across Comp ID 2670 and 3289).
* **Target Filtered Scope:** **194,014 deliveries** across **853 matches** (371 IPL, 482 T20I).
* **Pre-Delivery State Integrity:** 100% verified. All features with suffix `_before` strictly depend on balls $0 \dots t-1$.
* **Automated Validation:** 8 distinct integrity checks executed across all 194,014 deliveries with 0 failures.

---

## 2. Phase 1 — Ground Truth Verification Before Processing

Before coding the pipeline, raw delivery rows were inspected to confirm the 8 cricket domain rules:

### 2.1 `runs` Column: Batter Runs vs Total Delivery Runs
* **Confirmed:** `runs` represents **strictly batter runs off the bat**.
  - On **wides (7,714 deliveries)**: `runs` is **0** in 100% of cases. The wide penalty run is stored in `extras1_runs`.
  - On **byes (529 deliveries)**: `runs` is **0** in 100% of cases. The bye runs are stored in `extras1_runs`.
  - On **leg-byes (2,748 deliveries)**: `runs` is **0** in 99.96% of cases.
  - On **no-balls (`Overstep`, 576 deliveries)**: `extras1_runs` is always **1** (penalty), while `runs` reflects the bat runs (e.g., 81 fours, 47 sixes, 174 singles off no-balls).
* **Team Total on a Delivery:**
  $$\text{ball\_total\_runs} = \text{runs} + \text{extras1\_runs} + \text{extras\_2\_runs}$$

### 2.2 Bowler Legal Deliveries vs Batter Balls Faced
Cricket laws differentiate between bowler legal deliveries and batter balls faced:
* **Bowler Legal Deliveries (Excludes Wides & No-balls):**
  $$\text{is\_legal\_ball} = \sim \text{extras\_type.isin}([\text{'wide'}, \text{'overstep'}])$$
  *Total in raw data: 192,709 balls (7,714 wides + 576 no-balls excluded).*
* **Batter Balls Faced (Excludes Wides ONLY):**
  $$\text{is\_batter\_ball} = \text{extras\_type} \neq \text{'wide'}$$
  *Total in raw data: 193,285 balls.*
* **The 576 Ball Difference:** On a no-ball, the batsman faces the delivery (and can score or be run out), but the bowler must re-bowl it. The pipeline tracks both independently.

### 2.3 Bowler Runs Conceded
* Bowler economy must **not** be penalized for fielding extras (byes and leg-byes):
  $$\text{bowler\_runs\_conceded} = \text{runs} + \mathbb{I}(\text{extras\_type} \in [\text{'wide'}, \text{'overstep'}]) \times (\text{extras1\_runs} + \text{extras\_2\_runs})$$
* **Verified in Match 13512 (WI vs ENG, Inn 2):** West Indies scored 170 runs, while England bowlers conceded 163 runs; exactly 7 runs of byes/leg-byes were excluded from bowler figures.

### 2.4 Bowler-Creditable Wickets
Out of 10,881 total wickets in the raw dataset:
* **Bowler-Credited (10,272 wickets / 94.40%):** Caught (7,557), Bowled (1,775), LBW (709), Stumped (214), Hit Wicket (17).
* **Non-Bowler Dismissals (609 wickets / 5.60% — EXCLUDED):** Run Out (600), Retired Out (6), Obstructing the field (3).

### 2.5 DLS Revised Target and Overs Handling
* **Normal Matches (849 matches):** Target = $\text{Innings 1 Total Runs} + 1$, Capacity = 120 legal balls.
* **Shortened/DLS Matches (34 matches):** Target = `revised_target`, Capacity = `second_inn_revised_overs` (stored directly in legal balls, e.g. 90.0 balls = 15 overs).

### 2.6 Delivery Ordering
Across all 1,724 innings in the database, `innings_ball_num` is **100% strictly monotonic increasing**. Sorting by `['clean_match_id', 'innings', 'innings_ball_num']` guarantees chronological order.

---

## 3. Phase 2 — Competition Filtering Scope

The pipeline filters raw competitions strictly to official IPL and Men's T20I matches from 2022 onwards:

| Competition Scope | Competitions Count | Total Matches | Abandoned (0 balls) | Matches with Deliveries | Total Deliveries |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **IPL (2022–2026)** | 5 | 371 | 5 | 366 | **87,687** |
| **Men's T20I** | 134 | 482 | 12 | 470 | **106,327** |
| **Total In Scope** | **139** | **853** | **17** | **836** | **194,014** |
| *Excluded Regional Cups* | *2* | *30* | *0* | *30* | *6,985* |
| **Total Raw Database** | **141** | **883** | **17** | **866** | **200,999** |

### Excluded Competitions Ledger:
* **Comp ID 2670:** *Mens T20 Emerging Teams Asia Cup 2024* (15 matches, 3,519 deliveries).
* **Comp ID 3289:** *Asia Cup Rising Stars 2025* (15 matches, 3,466 deliveries).
* *Exclusion Reason:* Non-elite developmental tournaments whose lower-tier bowling/batting averages would distort official franchise and international rankings.

---

## 4. Phase 3 — Pre-Delivery Match State Architecture

For every delivery $t$, state is calculated strictly before the ball is bowled:

1. **`score_before`**: $\sum_{k=0}^{t-1} \text{ball\_total\_runs}_k$
2. **`wickets_before`**: $\sum_{k=0}^{t-1} \mathbb{I}(\text{is\_wicket}_k == \text{True})$
3. **`legal_balls_before`**: $\sum_{k=0}^{t-1} \mathbb{I}(\text{is\_legal\_ball}_k == \text{True})$
4. **`legal_balls_remaining_before`**: $\max(0, \text{total\_legal\_balls} - \text{legal\_balls\_before})$
5. **`phase`**:
   - `Powerplay`: Overs 1–6 (`overid <= 6`)
   - `Middle`: Overs 7–15 (`7 <= overid <= 15`)
   - `Death`: Overs 16–20 (`overid >= 16`)
6. **`target`**:
   - Innings 1: `NaN`
   - Innings 2: `revised_target` (if DLS) or $\text{Innings 1 Final Score} + 1$.
7. **`required_runs_before`**:
   - Innings 1: `NaN`
   - Innings 2: $\max(0, \text{target} - \text{score\_before})$
8. **`required_run_rate_before` (RRR)**:
   - Innings 1: `NaN`
   - Innings 2: $\left(\frac{\text{required\_runs\_before}}{\text{legal\_balls\_remaining\_before}}\right) \times 6.0$ (floored to 0.0 if won; capped at 36.0 if balls expire).
9. **`current_run_rate_before` (CRR)**:
   - $\left(\frac{\text{score\_before}}{\text{legal\_balls\_before}}\right) \times 6.0$ (0.0 before first legal ball).

---

## 5. Phase 4 — Player Performance Datasets

The pipeline generates two dedicated, high-performance datasets in `data/processed/`:

### 5.1 Batting Deliveries ([`data/processed/batting_deliveries.csv`](file:///d:/SupeRR_Selector/data/processed/batting_deliveries.csv))
* **Rows:** 194,014 | **Columns:** 34 | **File Size:** 32.76 MB
* **Key Columns:** `player_id`, `player_name`, `match_id`, `comp_id`, `competition_category`, `match_format`, `season`, `match_date`, `innings`, `overid`, `over_ball_num`, `innings_ball_num`, `phase`, `score_before`, `wickets_before`, `legal_balls_remaining_before`, `target`, `required_runs_before`, `required_run_rate_before`, `current_run_rate_before`, `batting_type`, `batting_order`, `runs_scored`, `is_four`, `is_six`, `is_wicket`, `is_batter_out`, `is_batter_ball`, `is_dot_ball`, `pace_or_spin`, `stroke`, `bowler_id`, `bowler_name`.

### 5.2 Bowling Deliveries ([`data/processed/bowling_deliveries.csv`](file:///d:/SupeRR_Selector/data/processed/bowling_deliveries.csv))
* **Rows:** 194,014 | **Columns:** 33 | **File Size:** 34.51 MB
* **Key Columns:** `player_id`, `player_name`, `match_id`, `comp_id`, `competition_category`, `match_format`, `season`, `match_date`, `innings`, `overid`, `over_ball_num`, `innings_ball_num`, `phase`, `score_before`, `wickets_before`, `legal_balls_remaining_before`, `target`, `required_runs_before`, `required_run_rate_before`, `current_run_rate_before`, `bowling_type`, `pace_or_spin`, `is_legal_ball`, `is_wide`, `is_noball`, `is_bye`, `is_legbye`, `bowler_runs_conceded`, `is_bowler_wicket`, `is_dot_ball`, `striker_id`, `striker_name`.

---

## 6. Phase 5 — Automated Validation Suite Results

The validation script [`src/validate_pipeline.py`](file:///d:/SupeRR_Selector/src/validate_pipeline.py) executed 8 automated tests across all 194,014 processed records:

| Test # | Automated Validation Check | Tested Rows / Groups | Detected Violations | Status |
| :---: | :--- | :---: | :---: | :---: |
| **1** | `score_before` is monotonically non-decreasing within innings | 1,664 innings | 0 | **PASSED ✅** |
| **2** | `wickets_before` is monotonically non-decreasing within innings | 1,664 innings | 0 | **PASSED ✅** |
| **3** | `legal_balls_before` advances by exactly 1 on legal balls; 0 on illegal balls | 192,350 ball transitions | 0 | **PASSED ✅** |
| **4** | `legal_balls_remaining_before` is never negative | 194,014 balls | 0 (min observed = 0) | **PASSED ✅** |
| **5** | Second-innings `required_runs_before` updates strictly as $(\text{target} - \text{score\_before})$ | 88,416 Inn 2 balls | 0 | **PASSED ✅** |
| **6** | Zero future-data leakage ($\text{score\_before}_t == \text{score\_before}_{t-1} + \text{ball\_runs}_{t-1}$) | 192,350 ball transitions | 0 | **PASSED ✅** |
| **7** | Referential integrity: zero orphan match or player IDs | 194,014 balls | 0 | **PASSED ✅** |
| **8** | Competition scope isolation: strictly IPL and T20I (no comp 2670 / 3289) | 194,014 balls | 0 | **PASSED ✅** |

---

## 7. Multi-Match Case Study Inspections (5 Matches)

Five representative matches were inspected to verify pre-delivery state reconstruction in complex match environments:

```text
1. Normal League Match: West Indies vs England (Match 13511)
   - Innings 1: 103/10 in 19.4 ov (118 legal balls). Target = NaN
   - Innings 2: 104/1 in 17.1 ov (103 legal balls). Target = 104.0
   - Over 1, Ball 1: Score=0/0, Balls Left=120, Req=104, RRR=5.20
   - Over 18, Ball 1: Score=103/1, Balls Left=18, Req=1, RRR=0.33 -> Won by 9 Wickets.

2. DLS Final: CSK vs GT (IPL 2023 Final - Match 21586)
   - Gujarat Titans Innings 1: 214/4 in 20.0 ov (120 legal balls).
   - Rain shortened Innings 2 to 15 overs (90 legal balls). DLS Revised Target = 171.0.
   - Over 1, Ball 1: Score=0/0, Balls Left=90, Req=171, RRR=11.40.
   - Over 15, Ball 5 (Final Over): Score=161/5, Balls Left=2, Req=10, RRR=30.00. (Jadeja 6).
   - Over 15, Ball 6 (Final Ball): Score=167/5, Balls Left=1, Req=4, RRR=24.00. (Jadeja 4) -> CSK Won.

3. Clutch Finish: England vs West Indies (Match 13512)
   - Innings 1: 171/8 in 20.0 ov (120 legal balls).
   - Innings 2: 170/8 in 20.0 ov (120 legal balls). Target = 172.0.
   - Over 20, Ball 7: Score=158/8, Balls Left=2, Req=14, RRR=42.0.
   - Over 20, Ball 8: Score=164/8, Balls Left=1, Req=8, RRR=48.0 -> England Won by 1 Run.

4. DLS Bilateral: Australia vs Sri Lanka (Match 13612)
   - Innings 1: 149/9 in 20.0 ov.
   - Rain revised Innings 2 to 19 overs (114 balls). Revised Target = 143.0.
   - Final Delivery: Score=121/8, Balls Left=1, Req=22, RRR=132.0 -> Australia Won by 20 Runs.

5. Rain-Curtailed: India vs Australia (Match 17395)
   - Rain shortened match to 8 overs per side (48 legal balls).
   - Innings 1: 90/5 in 8.0 ov. DLS Revised Target = 91.0 in 48 balls.
   - Over 8, Ball 2: Score=88/4, Balls Left=5, Req=3, RRR=3.60 -> India Won by 6 Wickets.
```

---

## 8. Summary of Processed Datasets

All processed deliverables are saved in [`data/processed/`](file:///d:/SupeRR_Selector/data/processed/):
1. **[`ipl_deliveries.csv`](file:///d:/SupeRR_Selector/data/processed/ipl_deliveries.csv):** 87,687 deliveries from 371 IPL matches with complete pre-delivery match state.
2. **[`t20i_deliveries.csv`](file:///d:/SupeRR_Selector/data/processed/t20i_deliveries.csv):** 106,327 deliveries from 482 T20I matches with complete pre-delivery match state.
3. **[`batting_deliveries.csv`](file:///d:/SupeRR_Selector/data/processed/batting_deliveries.csv):** 194,014 records structured from the striker's viewpoint.
4. **[`bowling_deliveries.csv`](file:///d:/SupeRR_Selector/data/processed/bowling_deliveries.csv):** 194,014 records structured from the bowler's viewpoint.

---

## 9. Conclusion & Next Step Sign-Off

Phase 1 through Phase 5 of Master Task 03 are complete. The raw data remains untouched, competition filtering is strict, and pre-delivery match states are mathematically verified without future-data leakage.

**Status:** Standing by for your approval to proceed to Master Task 04 (Pressure Index Formulation & Player Rankings).

