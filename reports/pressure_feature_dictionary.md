# SUPERR SELECTOR — PRESSURE FEATURE DICTIONARY & SCHEMA SPECIFICATION (REVISED)
**Document Reference:** `reports/pressure_feature_dictionary.md`  
**Task Reference:** Master Task 04.1 (Pressure Engine: Methodology Design & Feature Specification)  
**Author:** Senior Cricket Data Scientist & Machine Learning Architect  
**Project:** SUPERR SELECTOR (Rajasthan Royals SupeRR Selector Season 2 Hackathon)  
**Date:** November 2026 (Revision 2.0)  
**Status:** Complete Feature Specification — Ready for Engine Implementation in Task 04.2  

---

## 1. Schema Overview & Data Engineering Principles

This document defines every feature to be generated and stored in the delivery-level pressure dataset (`data/processed/pressure_deliveries.csv`), as well as the player-centric subsets (`batting_pressure_deliveries.csv` and `bowling_pressure_deliveries.csv`).

### Foundational Principles
1. **Ex-Ante Purity:** Every feature is derived strictly from information available **prior to the bowler initiating the delivery run-up**.
2. **Situational Difficulty vs. Player Performance:** These features quantify the **objective match-situation difficulty** faced by the batting and bowling units. They do not evaluate individual player talent, execution, or biometric stress. Player performance under pressure is evaluated separately in Master Task 05.
3. **Bowling Pressure as Team-Context Pressure:** Bowling pressure measures the **team-context defensive pressure** (runway margin, proximity to defeat, boundary vulnerability, opponent depth), not individual psychological anxiety.
4. **Explainability & Sub-Component Decomposition:** All sub-components are retained as distinct columns to allow additive white-box decomposition (supporting transparent inspection and feature attribution).
5. **Exact Schema Reconciliation:** The output schema contains **exactly 48 standardized columns** across 6 functional groups. All input fields are verified against `data/processed/ipl_deliveries.csv` and `data/processed/t20i_deliveries.csv`.

---

## 2. Feature Groups Summary (48 Columns Total)

| Group | Functional Category | Column Count | Description & Scope |
|:---:|:---|:---:|:---|
| **Group 1** | Delivery Identifiers & Metadata | **16** | Match IDs, teams, players, overs, ball sequence, tournament tier. |
| **Group 2** | Ground-Truth Pre-Delivery State | **10** | Pre-delivery scores, wickets, balls, target, RRR, CRR, chase state. |
| **Group 3** | Contextual Baselines & Transforms | **5** | Format par, Bayesian CRR, bounded RRR, resource depletion, runway. |
| **Group 4** | Component Sub-Scores (Decomposition) | **9** | Additive explainability components for Innings 1 and 2 (Bat & Bowl). |
| **Group 5** | Core Pressure Indices & Categories | **4** | Continuous master scores $[0, 100]$ and 4-tier categorical bins. |
| **Group 6** | Quality, Audit & Edge-Case Flags | **4** | DLS flag, early ball flag, extreme RRR flag, terminal target met flag. |
| **TOTAL** | **Standardized Pressure Delivery Schema** | **48** | **Comprehensive, verified delivery-level schema.** |

*(Note on reconciliation: Revision 1.0 previously stated 42 columns in prose while listing 46 in tables, omitting the two Innings 1 components `bat_comp_phase_urgency` and `bowl_comp_death_defense`. Revision 2.0 adds both components and corrects the total to exactly 48 verified columns).*

---

## 3. Comprehensive Feature Dictionary

### Group 1: Delivery Identifiers & Relational Metadata (16 Columns)

| # | Column Name | Data Type | Range / Allowed Values | Provenance / Source | Description & Cricket Relevance |
|:---:|:---|:---:|:---:|:---:|:---|
| 1 | `match_id` | `int64` | Positive integers | `matches.csv` | Unique identifier of the cricket match. Foreign key to match metadata. |
| 2 | `competition_category` | `string` | `['IPL', 'T20I']` | `competitions.csv` | Tournament category. Assigns format par scoring baseline. |
| 3 | `comp_id` | `int64` | `[1358, 1374, ...]` | `competitions.csv` | Unique identifier for tournament season edition. |
| 4 | `season` | `string` | `['2022', '2023', '2024', '2025', '2026']` | `matches.csv` | Season year of competition. |
| 5 | `match_date` | `string` | `YYYY-MM-DD` | `matches.csv` | Scheduled calendar date of the match. |
| 6 | `innings` | `int64` | `[1, 2, 3, 4]` | `ball_by_ball.csv` | Chronological innings sequence: `1` = First innings (target setting), `2` = Second innings (run chase), `3` = Super Over first batting innings, `4` = Super Over second batting innings. (Note: Innings 3 & 4 represent historical Super Over tie-breakers; standard 20-over reliability indexing in Task 05 excludes them via `is_super_over == False`). |
| 7 | `overid` | `int64` | `1` to `20` | `ball_by_ball.csv` | Over index within the innings (1-indexed). |
| 8 | `over_ball_num` | `int64` | `1` to `12+` | `ball_by_ball.csv` | Chronological delivery number within over (includes extras). |
| 9 | `innings_ball_num` | `int64` | `1` to `140+` | `ball_by_ball.csv` | Absolute chronological ball number within the innings. |
| 10 | `phase` | `string` | `['Powerplay', 'Middle', 'Death']` | `features/match_state.py` | Tactical phase: Powerplay (ov 1-6), Middle (ov 7-15), Death (ov 16-20). |
| 11 | `batting_team_id` | `int64` | Positive integers | `ball_by_ball.csv` | Unique team identifier of the batting team. |
| 12 | `bowling_team_id` | `int64` | Positive integers | `ball_by_ball.csv` | Unique team identifier of the bowling team. |
| 13 | `striker_id` | `int64` | Positive integers | `ball_by_ball.csv` | Unique player identifier of the batter facing delivery. |
| 14 | `striker_name` | `string` | Text string | `ball_by_ball.csv` | Standardized display name of the striker. |
| 15 | `bowler_id` | `int64` | Positive integers | `ball_by_ball.csv` | Unique player identifier of the bowler. |
| 16 | `bowler_name` | `string` | Text string | `ball_by_ball.csv` | Standardized display name of the bowler. |

---

### Group 2: Ground-Truth Pre-Delivery Match State (10 Columns)

*All features in this group represent cumulative match history up to delivery $t-1$.*

| # | Column Name | Data Type | Range / Allowed Values | Formula / Source | Description & Anti-Leakage Verification |
|:---:|:---|:---:|:---:|:---:|:---|
| 17 | `score_before` | `int64` | $0$ to $300+$ | $\sum_{i=1}^{t-1} \text{runs}_i$ | Total runs scored by batting side prior to this delivery. |
| 18 | `wickets_before` | `int64` | $0$ to $9$ | $\sum_{i=1}^{t-1} \text{wicket\_ball}_i$ | Wickets lost by batting side prior to this delivery. |
| 19 | `legal_balls_before` | `int64` | $0$ to $120$ | $\sum_{i=1}^{t-1} \text{legal\_ball}_i$ | Number of legal deliveries bowled prior to this delivery. |
| 20 | `total_legal_balls` | `int64` | $30$ to $120$ | Match capacity | Scheduled legal balls in innings (120 full, $<120$ for DLS). |
| 21 | `legal_balls_remaining_before` | `int64` | $0$ to $120$ | $\text{total} - \text{legal\_balls\_before}$ | Legal deliveries remaining in innings prior to this delivery. |
| 22 | `target` | `float64` | $30.0$ to $300.0$, or `NaN` | Match context | Target to win in Innings 2. Strictly `NaN` in Innings 1. |
| 23 | `required_runs_before` | `float64` | Reals, or `NaN` | $\text{target} - \text{score\_before}$ | Runs needed to win prior to this delivery. `NaN` in Innings 1. |
| 24 | `current_run_rate_before` | `float64` | $\ge 0.0$, or `NaN` | $\frac{\text{score\_before}}{\text{legal\_balls\_before}} \times 6.0$ | Current scoring rate. Strictly `NaN` when legal balls is 0. |
| 25 | `required_run_rate_before` | `float64` | Reals, or `NaN` | $\frac{\text{req\_runs}}{\text{balls\_rem}} \times 6.0$ | Required run rate in Innings 2. Strictly `NaN` in Innings 1. |
| 26 | `impossible_chase_state` | `bool` | `[True, False]` | Production function | `True` only if Innings 2, balls remaining is 0, and runs needed $>0$. |

---

### Group 3: Contextual Baselines & Transformed Features (5 Columns)

| # | Column Name | Data Type | Range / Allowed Values | Mathematical Formula | Purpose & Normalization Logic |
|:---:|:---|:---:|:---:|:---|:---|
| 27 | `par_run_rate_comp` | `float64` | `9.35` (IPL), `8.59` (T20I) | Empirical median run rate | Format baseline par rate. Prevents cross-competition bias. |
| 28 | `crr_shrinkage_before` | `float64` | $\ge 0.0$ | $\frac{\text{score\_before} + \text{PAR} \times 2.0}{\frac{\text{legal\_balls\_before}}{6.0} + 2.0}$ | Bayesian-smoothed CRR. Stabilizes variance in first 12 balls. |
| 29 | `rrr_bounded` | `float64` | $[0.0, 100.0]$, or `NaN` | $\frac{100.0}{1.0 + \exp(-0.35 \cdot (\text{RRR} - \text{PAR}))}$ | Proposed sigmoidal RRR feature. Saturates gracefully when RRR spikes. |
| 30 | `resource_percentage_depleted` | `float64` | $[0.0, 100.0]$ | $100.0 \times \left(1.0 - \left(1.0 - \frac{w}{10}\right) \cdot \left(\frac{\text{rem}}{\text{total}}\right)^{0.65}\right)$ | Overall resource depletion index across wickets and overs. |
| 31 | `runs_to_defend_per_ball` | `float64` | $\ge 0.0$, or `NaN` | $\frac{\text{required\_runs\_before}}{\max(\text{legal\_balls\_remaining\_before}, 1)}$ | Runway metric for bowling team in Innings 2. Drives bowling pressure. |

---

### Group 4: Component Sub-Scores (Explainability Vectors) (9 Columns)

*Every sub-component is normalized to $[0.0, 100.0]$ (except multiplier) for white-box auditability.*

| # | Column Name | Data Type | Range | Innings | Perspective | Mathematical Definition |
|:---:|:---|:---:|:---:|:---:|:---:|:---|
| 32 | `bat_comp_pace_urgency` | `float64` | $[0.0, 100.0]$ | 1 & 2 | Batting | Innings 1: Pace deficit $(\text{PAR} - \text{CRR}_{\text{adj}})$. Innings 2: Sigmoidal RRR ($S_{\text{RRR}}$). |
| 33 | `bat_comp_resource_stress` | `float64` | $[0.0, 100.0]$ | 1 & 2 | Batting | Innings 1: Wicket deficit vs expected. Innings 2: Wicket loss curve $(\frac{w}{10})^{1.35}$. |
| 34 | `bat_comp_phase_urgency` | `float64` | $[0.0, 100.0]$ | 1 | Batting | Innings 1: Overs fraction escalation $35.0 + 50.0 \times (t / \text{total})^{1.5}$. |
| 35 | `bat_comp_crunch_mult` | `float64` | $[0.75, 1.30]$ | 2 | Batting | Ball crunch interaction multiplier scaling RRR tension late in chase. |
| 36 | `bowl_comp_containment` | `float64` | $[0.0, 100.0]$ | 1 | Bowling | Bowling team containment stress $(\text{CRR}_{\text{adj}} - \text{PAR})$. |
| 37 | `bowl_comp_death_defense` | `float64` | $[0.0, 100.0]$ | 1 | Bowling | Inherent execution demand during Innings 1 death overs (overs 16–20). |
| 38 | `bowl_comp_runway` | `float64` | $[0.0, 100.0]$ | 2 | Bowling | Defensive runway danger based on runs to defend per ball remaining. |
| 39 | `bowl_comp_boundary_threat` | `float64` | $[0.0, 100.0]$ | 2 | Bowling | Boundary cushion vulnerability: $100 - 15 \times \frac{\text{req}-1}{4}$. |
| 40 | `bowl_comp_depth_stress` | `float64` | $[0.0, 100.0]$ | 1 & 2 | Bowling | Threat posed by remaining batting depth of the opposing team. |

---

### Group 5: Core Pressure Indices & Categorical Tiers (4 Columns)

| # | Column Name | Data Type | Range / Allowed Values | Calculation Logic | Analytical Application |
|:---:|:---|:---:|:---:|:---|:---|
| 41 | `batting_pressure_score` | `float64` | $[0.00, 100.00]$ | Weighted composite | Master batting situational pressure index. |
| 42 | `bowling_pressure_score` | `float64` | $[0.00, 100.00]$ | Weighted composite | Master bowling team-context defensive pressure index. |
| 43 | `batting_pressure_cat` | `string` | `['Low', 'Moderate', 'High', 'Extreme']` | Binned $[0, 40), [40, 65), [65, 85), [85, 100]$ | Proposed 4-tier batting pressure category. |
| 44 | `bowling_pressure_cat` | `string` | `['Low', 'Moderate', 'High', 'Extreme']` | Binned $[0, 40), [40, 65), [65, 85), [85, 100]$ | Proposed 4-tier bowling defensive pressure category. |

---

### Group 6: Quality, Audit & Edge-Case Flags (4 Columns)

| # | Column Name | Data Type | Allowed Values | Flag Trigger Condition | Quality Assurance Purpose |
|:---:|:---|:---:|:---|:---|:---|
| 45 | `is_dls_shortened` | `bool` | `[True, False]` | `total_legal_balls < 120` | Identifies rain-interrupted matches where capacity is $<20$ overs. |
| 46 | `is_early_delivery` | `bool` | `[True, False]` | `legal_balls_before < 12` | Flags deliveries subject to Bayesian CRR shrinkage. |
| 47 | `is_extreme_rrr_bounded` | `bool` | `[True, False]` | `required_run_rate_before >= 24.0` | Flags deliveries where raw RRR reached crisis saturation. |
| 48 | `is_target_met_delivery` | `bool` | `[True, False]` | `required_runs_before <= 0` | Flags terminal delivery states where pressure collapses to 0.0. |

> [!NOTE]
> **Terminal State Exclusion Policy:**  
> Terminal delivery states (e.g. `required_runs_before <= 0` or `legal_balls_remaining_before == 0`) represent synthetic boundary conditions and are not ordinary delivery-level observations. In historical match play, innings terminate immediately once the target is reached or scheduled balls expire; no deliveries are bowled post-conclusion. Any delivery flagged with `is_target_met_delivery == True` or `impossible_chase_state == True` is excluded from player reliability scoring in Task 05.

> [!IMPORTANT]
> **Super Over Exclusion Policy & Governance (Task 05 Preparation):**  
> In accordance with the Task 04.2A.2 post-audit reconciliation (**Option A**), deliveries where `innings > 2` represent historical Super Over tie-breakers:
> - `innings == 3`: Super Over first batting innings (target setting).
> - `innings == 4`: Super Over second batting innings (run chase).  
> 
> Across the verified dataset, there are exactly 26 Super Over deliveries across 4 matches (14 IPL, 12 T20I). Super Over deliveries are strictly excluded from standard 20-over batter and bowler reliability calculations in Master Task 05 via the filtering rule:
> $$\text{is\_super\_over} = (\text{innings} > 2) \implies \text{Standard 20-Over Filter: } \text{is\_super\_over} == \text{False}$$
> All original Super Over records are preserved intact in the deliverables for possible separate, dedicated tie-breaker analysis. The legacy 100-point Super Over score is an unapproved legacy implementation artifact that is formally superseded by this downstream exclusion rule; Super Over scores will never be silently treated as ordinary 20-over pressure observations.

---

## 4. Verification Against Actual Processed Deliverables

To guarantee 100% operational feasibility, all 26 source columns were verified against the production deliverables `data/processed/ipl_deliveries.csv` and `data/processed/t20i_deliveries.csv` (both containing 65 columns with 100% identical headers):

### 4.1 All 26 Verified Source Features Present in Processed CSVs
| # | Input Feature Name | Verified in IPL Deliveries? | Verified in T20I Deliveries? | Source Layer | Sample Value (Match 14094, Ball 1) |
|:---:|:---|:---:|:---:|:---:|:---:|
| 1 | `match_id` | **YES ✅** | **YES ✅** | Raw match key | `14094` |
| 2 | `competition_category`| **YES ✅** | **YES ✅** | Tournament tier | `'IPL'` |
| 3 | `comp_id` | **YES ✅** | **YES ✅** | Competition edition | `1358` |
| 4 | `season` | **YES ✅** | **YES ✅** | Season metadata | `2022` |
| 5 | `match_date` | **YES ✅** | **YES ✅** | Match metadata | `'2022-03-26'` |
| 6 | `innings` | **YES ✅** | **YES ✅** | Chronological innings | `1` |
| 7 | `overid` | **YES ✅** | **YES ✅** | Over sequence | `1` |
| 8 | `over_ball_num` | **YES ✅** | **YES ✅** | Ball in over | `1` |
| 9 | `innings_ball_num` | **YES ✅** | **YES ✅** | Ball in innings | `1` |
| 10 | `phase` | **YES ✅** | **YES ✅** | Derived phase | `'Powerplay'` |
| 11 | `batting_team_id` | **YES ✅** | **YES ✅** | Team metadata | `1` |
| 12 | `bowling_team_id` | **YES ✅** | **YES ✅** | Team metadata | `8` |
| 13 | `striker_id` | **YES ✅** | **YES ✅** | Player metadata | `6059` |
| 14 | `striker_name` | **YES ✅** | **YES ✅** | Player metadata | `'Ruturaj Gaikwad'` |
| 15 | `bowler_id` | **YES ✅** | **YES ✅** | Player metadata | `403` |
| 16 | `bowler_name` | **YES ✅** | **YES ✅** | Player metadata | `'Umesh Yadav'` |
| 17 | `score_before` | **YES ✅** | **YES ✅** | Cumulative state | `0` |
| 18 | `wickets_before` | **YES ✅** | **YES ✅** | Cumulative state | `0` |
| 19 | `legal_balls_before` | **YES ✅** | **YES ✅** | Cumulative state | `0` |
| 20 | `total_legal_balls` | **YES ✅** | **YES ✅** | Innings capacity | `120` |
| 21 | `legal_balls_remaining_before` | **YES ✅** | **YES ✅** | Cumulative state | `120` |
| 22 | `target` | **YES ✅** | **YES ✅** | Innings 2 context | `NaN` |
| 23 | `required_runs_before` | **YES ✅** | **YES ✅** | Cumulative state | `NaN` |
| 24 | `current_run_rate_before` | **YES ✅** | **YES ✅** | Cumulative state | `NaN` |
| 25 | `required_run_rate_before` | **YES ✅** | **YES ✅** | Cumulative state | `NaN` |
| 26 | `impossible_chase_state` | **YES ✅** | **YES ✅** | Cumulative state | `False` |

### 4.2 All 22 Derived Features to be Generated by Pressure Engine
1. `par_run_rate_comp` (Group 3)
2. `crr_shrinkage_before` (Group 3)
3. `rrr_bounded` (Group 3)
4. `resource_percentage_depleted` (Group 3)
5. `runs_to_defend_per_ball` (Group 3)
6. `bat_comp_pace_urgency` (Group 4)
7. `bat_comp_resource_stress` (Group 4)
8. `bat_comp_phase_urgency` (Group 4)
9. `bat_comp_crunch_mult` (Group 4)
10. `bowl_comp_containment` (Group 4)
11. `bowl_comp_death_defense` (Group 4)
12. `bowl_comp_runway` (Group 4)
13. `bowl_comp_boundary_threat` (Group 4)
14. `bowl_comp_depth_stress` (Group 4)
15. `batting_pressure_score` (Group 5)
16. `bowling_pressure_score` (Group 5)
17. `batting_pressure_cat` (Group 5)
18. `bowling_pressure_cat` (Group 5)
19. `is_dls_shortened` (Group 6)
20. `is_early_delivery` (Group 6)
21. `is_extreme_rrr_bounded` (Group 6)
22. `is_target_met_delivery` (Group 6)

$$\text{Total Schema Features} = 26 \text{ Verified Source Columns} + 22 \text{ Derived Columns} = \mathbf{48 \text{ Standardized Columns}}.$$

---

## 5. Schema Change Log & Unresolved Assumptions

### Schema Change Log
- **v1.0 to v2.0:**
  1. Corrected the stated total column count from 42 to **48 standardized columns**.
  2. Formally added `bat_comp_phase_urgency` (column #34) and `bowl_comp_death_defense` (column #37) to Group 4.
  3. Added verified cross-check against actual processed CSV headers.
  4. Clarified that bowling pressure is team-context defensive pressure.

### Unresolved Schema Assumptions (To Be Finalized in Task 04.2)
1. **Float Precision in Export:** Pressure scores will be stored to 2 decimal places (`round(2)`), matching standard cricket reporting conventions.
2. **Player-Centric Export Storage:** Whether to store `pressure_deliveries.csv` as a single 194,014-row master file or pre-split into `batting_pressure_deliveries.csv` and `bowling_pressure_deliveries.csv` will be finalized based on dashboard query performance in Task 06.
