# 📋 SUPERR SELECTOR — Dataset Audit Report (Master Task 02)

> **Project:** SUPERR SELECTOR — Advanced Cricket Pressure-Performance Analytics  
> **Auditor:** Senior Python Data Analyst & Cricket Data Engineer  
> **Target Scope:** IPL & T20I Competitions Only (2022–2026)  
> **Data Location:** `data/raw/`  
> **Generated Artifacts:** [`outputs/dataset_summary.csv`](file:///d:/SupeRR_Selector/outputs/dataset_summary.csv) & [`outputs/data_quality_issues.csv`](file:///d:/SupeRR_Selector/outputs/data_quality_issues.csv)  
> **Audit Status:** 100% Complete & Verified (Zero Records Altered or Overwritten)  

---

## 1. Executive Summary

This report delivers a comprehensive data audit of all six CSV files located in `data/raw/`. The primary objective is to establish an unshakeable empirical foundation for calculating player pressure performance across **IPL (Indian Premier League)** and **ICC Men's T20I (International)** competitions from 2022 onwards.

### Core Headline Metrics
* **Total Matches:** **883 matches** (IPL: 371, T20I: 482, Other regional: 30)
* **Total Deliveries:** **200,999 balls** (IPL: 87,687, T20I: 106,327, Other regional: 6,985)
* **Total Unique Players:** **1,217 players** (All 1,217 are mapped in `competition_team_player_mapping.csv`; 959 active in delivery data)
* **Total Teams:** **38 distinct teams**
* **Total Competitions:** **141 competitions** (IPL: 5, T20I: 134, Other: 2)
* **Date Range:** **2022-01-22 to 2026-11-01** (100% of matches are from 2022 onwards)
* **Referential Join Coverage:** **100.0%** across matches, competitions, balls, and teams. Zero orphan records.
* **Duplicate Rows:** **0 duplicate rows** across all 237,170 aggregate dataset rows.

---

## 2. Dataset-by-Dataset Inventory & Schema Audit

| Dataset Name | Row Count | Column Count | File Size (MB) | Duplicate Rows | Total Cells | Missing Cells | Missing % | Primary / Natural Key |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`ball_by_ball.csv`** | 200,999 | 33 | 39.17 | 0 | 6,632,967 | 766,466 | 11.56% | `(match_id, innings, overid, over_ball_num)` |
| **`matches.csv`** | 883 | 22 | 0.12 | 0 | 19,426 | 2,736 | 14.08% | `match_id` |
| **`competitions.csv`** | 141 | 4 | 0.01 | 0 | 564 | 0 | 0.00% | `comp_id` |
| **`teams.csv`** | 353 | 3 | 0.01 | 0 | 1,059 | 0 | 0.00% | `(comp_id, team_id)` |
| **`playing_eleven.csv`** | 28,381 | 9 | 0.92 | 0 | 255,429 | 26,012 | 10.18% | `(match_id, team_id, player_id)` |
| **`competition_team_player_mapping.csv`** | 6,413 | 6 | 0.44 | 0 | 38,478 | 0 | 0.00% | `(comp_id, team_id, player_id)` |
| **Total Ecosystem** | **237,170** | **77** | **40.67** | **0** | **6,947,923** | **795,214** | **11.45%** | |

### Column Dictionary & Missing Data Analysis
1. **`ball_by_ball.csv` (33 columns):**
   - **Delivery Identifiers:** `match_id` (int64), `innings` (int64), `overid` (int64), `over_ball_num` (int64), `innings_ball_num` (int64).
   - **Teams & Participants:** `batting_team_id` (int64), `bowling_team_id` (int64), `striker_id` (int64), `striker_name` (object), `non_striker_id` (int64), `non_striker_name` (object), `bowler_id` (int64), `bowler_name` (object).
   - **Tactical Types:** `batting_type` (object), `bowling_type` (object), `batting_order` (float64), `pace_or_spin` (object).
   - **Scoring & Outcomes:** `runs` (int64), `is_four` (bool/object), `is_six` (bool/object), `is_wicket` (bool/object).
   - **Dismissals (Populated only on wickets, ~94.6% null):** `dismissal_type_id` (190,118 nulls), `dismissal_type` (190,118 nulls), `dismissed_player_id` (190,107 nulls).
   - **Extras (Populated only on extras, 94.1% null):** `extras_type` (189,167 nulls), `extras1_runs` (int64), `extras_2_runs` (int64).
   - **Shot & Ball Tracking:** `stroke` (6,158 nulls, 3.06%), `delivery_style` (391 nulls, 0.19%), `over_or_around` (407 nulls, 0.20%), `on_or_off` (object), `bowl_speed` (int64, 97.7% unrecorded zero values), `delivery_ist_time` (object).
2. **`matches.csv` (22 columns):**
   - Core match metadata (100% complete): `match_id`, `comp_id`, `match_number`, `match_date`, `stage`, `venue_id`, `venue_country`, `home_team_id`, `home_team`, `away_team_id`, `away_team`, `result`.
   - DLS / Rain-affected features (null for standard games): `first_inn_revised_overs` (858 nulls), `second_inn_revised_overs` (858 nulls), `revised_target` (860 nulls).
   - Match condition features: `toss_win_team_id` (15 nulls), `toss_opted` (15 nulls), `win_team_id` (41 nulls), `man_of_the_match` (int64), `home_team_captain_id` (44 nulls), `away_team_captain_id` (45 nulls).
3. **`competitions.csv`, `teams.csv`, `mapping.csv`:**
   - **100% complete across all rows and columns.**

---

## 3. Unique Entities Identified

* **Unique Matches:** **883**
  - Matches with recorded deliveries: **867**
  - Matches with 0 deliveries: **16** (all officially `Match Abandoned` due to rain).
* **Unique Players:** **1,217**
  - 100% of these 1,217 players are registered in `competition_team_player_mapping.csv`.
  - Active Strikers in delivery records: **888**
  - Active Bowlers in delivery records: **647**
  - Active Non-strikers: **867**
  - Dismissed Batsmen: **814**
  - Match-Day Playing XI Squad entries: **1,082**
* **Unique Teams:** **38** (10 IPL franchises + 28 international/emerging teams).
* **Unique Competitions:** **141** (134 T20I, 5 IPL, 2 other emerging cups).
* **Unique Seasons:** **8** distinct season tags: `2022`, `2022/23`, `2023`, `2023/24`, `2024`, `2024/25`, `2025`, `2026`.

---

## 4. Identification of IPL & T20I Competitions

The project scope strictly targets **IPL and T20I competitions** for official player pressure rankings.

### 4.1 IPL Competitions (5 Tournaments)
Identified using pattern `comp_name.str.contains('IPL', case=False)`:
1. **Comp ID 1358:** *IPL 2022* (Season 2022) — 74 matches, 17,909 deliveries.
2. **Comp ID 1715:** *IPL 2023* (Season 2023) — 74 matches, 17,863 deliveries.
3. **Comp ID 2193:** *IPL 2024* (Season 2024) — 74 matches (3 abandoned), 17,103 deliveries.
4. **Comp ID 2725:** *IPL 2025* (Season 2025) — 75 matches (1 abandoned), 17,285 deliveries.
5. **Comp ID 3298:** *IPL 2026* (Season 2026) — 74 matches, 17,527 deliveries.
* **IPL Subtotal:** **371 matches** (366 played, 5 abandoned) and **87,687 deliveries**.

### 4.2 T20I Competitions (134 Tournaments)
Identified using `match_format == 'T20I'`:
* Spans 134 international bilateral series, World Cups, and continental tournaments.
* 131 competitions have recorded matches in `matches.csv`; 3 were unplayed/scheduled series.
* **T20I Subtotal:** **482 matches** (470 played, 12 abandoned without balls) and **106,327 deliveries**.

### 4.3 Other Competitions (Exclusion Scope)
* **Comp ID 2670:** *Mens T20 Emerging Teams Asia Cup 2024* (15 matches, 3,519 deliveries).
* **Comp ID 3289:** *Asia Cup Rising Stars 2025* (15 matches, 3,466 deliveries).
* **Scope Exclusion Recommendation:** These 30 matches and 6,985 deliveries must be excluded from official IPL and T20I pressure rankings to prevent skew from regional developmental tournaments.

---

## 5. Temporal Coverage & Competition Formats

* **Date Range:** **2022-01-22** (England in West Indies 1st T20I) to **2026-11-01** (India in Japan T20I Match).
* **2022 Onwards Verification:** **100.0% of matches (883 / 883)** occurred on or after January 1, 2022. No legacy matches precede 2022.
* **Competition Formats:**
  * **`T20I` (International):** 134 tournaments.
  * **`T20` (Franchise / Tournament):** 7 tournaments (5 IPL seasons + 2 emerging cups).

---

## 6. Relational Integrity & Join Validation

| Relationship | Join Key | Source Rows | Matched Rows | Join Match % | Integrity Findings |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `matches` → `competitions` | `comp_id` | 883 | 883 | **100.0%** | Zero orphan matches. 3 competitions in `competitions.csv` have 0 matches (unplayed series). |
| `ball_by_ball` → `matches` | `match_id` | 200,999 | 200,999 | **100.0%** | Zero orphan deliveries. Exactly 16 matches in `matches.csv` have 0 deliveries (official rain abandonments). |
| `playing_eleven` → `matches` | `match_id` | 28,381 | 28,381 | **100.0%** | Zero orphan records. 3 matches in `matches.csv` have no playing eleven (abandoned prior to toss). |
| `matches` → `teams` (Home) | `home_team_id` → `team_id` | 883 | 883 | **100.0%** | All 38 unique home teams present in master teams table. |
| `matches` → `teams` (Away) | `away_team_id` → `team_id` | 883 | 883 | **100.0%** | All 38 unique away teams present in master teams table. |
| `ball_by_ball` → `teams` (Batting) | `batting_team_id` → `team_id` | 200,999 | 200,999 | **100.0%** | Zero unmapped batting teams. |
| `ball_by_ball` → `teams` (Bowling) | `bowling_team_id` → `team_id` | 200,999 | 200,999 | **100.0%** | Zero unmapped bowling teams. |
| `playing_eleven` → `mapping` | `player_id` | 28,381 | 28,381 | **100.0%** | 100% of squad appearance IDs map to player master mapping registry. |

---

## 7. Data Quality Issues & Technical Edge Cases

The following 9 specific data quality items were identified and exported to [`outputs/data_quality_issues.csv`](file:///d:/SupeRR_Selector/outputs/data_quality_issues.csv):

| ID | Dataset | Affected Field | Severity | Impact & Technical Root Cause | Recommended Engineering Remedy |
| :---: | :--- | :--- | :---: | :--- | :--- |
| **DQI-01** | `ball_by_ball.csv` | `dismissed_player_id` | **Medium** | Pandas type inference casts nullable integer to `float64`, converting ID `1187` into `1187.0`. | Explicitly cast to string and apply regex strip `.replace(r'\.0$', '', regex=True)` or use nullable `Int64`. |
| **DQI-02** | `matches.csv` | `match_id` | **High (Domain Expected)** | 16 matches have 0 deliveries in `ball_by_ball.csv` due to rain abandonments without a ball bowled. | Do not use inner joins without handling abandoned matches; inner joins silently drop these 16 matches. |
| **DQI-03** | `playing_eleven.csv` | `match_id` | **Medium** | 3 matches (36210, 41503, 48513) have no squad records because matches were abandoned before the toss. | Use left joins from `matches.csv` with null-safe handling. |
| **DQI-04** | `ball_by_ball.csv` | `player_id` | **Low** | 2 UAE players (Basil Hameed: 39444, Syed Haider: 36153) batted/bowled in 3 matches but were missing from `playing_eleven.csv`. | Use `competition_team_player_mapping.csv` as the single source of truth for player identity. |
| **DQI-05** | `competitions.csv` | `comp_id` | **Low** | 3 competitions (3405, 3473, 2940) have zero scheduled/recorded matches in `matches.csv`. | Filter competitions based on inner join with `matches.csv` when listing active tournament views. |
| **DQI-06** | `matches.csv` | `revised_overs`, `revised_target` | **Medium** | DLS columns are null for 97.2% of matches (populated only for rain-shortened matches). | When null, fallback to standard 120 legal balls and $(\text{Innings 1 score} + 1)$ for chase target. |
| **DQI-07** | `matches.csv` | `home_team_captain_id` | **Low** | Captaincy IDs are null in ~5% of matches. | Cross-reference `is_captain == True` from `playing_eleven.csv` to backfill captain IDs. |
| **DQI-08** | `ball_by_ball.csv` | `bowl_speed` | **Low** | Speed gun telemetry recorded as 0 in 97.7% of deliveries. | Do not use `bowl_speed` as a primary feature; rely on `pace_or_spin` and `bowling_type`. |
| **DQI-09** | `competitions.csv` | `comp_name` | **High (Scope Filtering)** | Contains 30 matches from 2 non-IPL/non-T20I emerging regional cups. | Filter out comp_ids 2670 and 3289 before computing official pressure rankings. |

---

## 8. Columns Required for Future Feature Engineering

### 8.1 Batting Pressure & Performance Features
* `match_id`, `innings`, `overid`, `over_ball_num`, `innings_ball_num`
* `striker_id`, `striker_name`, `non_striker_id`, `batting_team_id`, `batting_type`, `batting_order`
* `runs` (runs off bat)
* `is_four`, `is_six` (boundary acceleration)
* `is_wicket`, `dismissal_type`, `dismissed_player_id` (dismissal cost)
* `extras_type` (to determine legal balls faced: all balls excluding `wide`)
* `pace_or_spin` (pace vs spin tactical split)

### 8.2 Bowling Pressure & Execution Features
* `match_id`, `innings`, `overid`, `over_ball_num`
* `bowler_id`, `bowler_name`, `bowling_team_id`, `bowling_type`, `pace_or_spin`
* `runs`, `extras_type`, `extras1_runs`, `extras_2_runs` (to compute bowler runs conceded: bat runs + wide + no-ball extras, excluding byes and leg-byes)
* `is_wicket`, `dismissal_type` (to credit bowler wickets: Caught, Bowled, LBW, Stumped, Hit Wicket, excluding Run Outs and Retired Out)

### 8.3 Prior Match-State & Pressure Context Features
* `score_before`: Cumulative runs prior to delivery
* `wickets_before`: Cumulative wickets fallen prior to delivery
* `legal_balls_bowled_before` & `legal_balls_remaining_before`
* `target` & `required_runs_before` (for Innings 2)
* `required_run_rate_before` (RRR) & `current_run_rate_before` (CRR)
* `first_inn_revised_overs`, `second_inn_revised_overs`, `revised_target` (for DLS match capacity)
* `pressure_score_before`: Continuous index $[0.0, 100.0]$ modeling situational tension

---

## 9. Key Analytical Limitations & Ranking Guardrails

1. **Volume & Sample Size Bias:**
   Certain elite players have played 70+ IPL matches, while other players in short bilateral tours have faced fewer than 20 balls. A player scoring 30 runs off 15 balls (SR 200) must not outrank a proven performer over 1,500 balls. Minimum delivery qualification thresholds (e.g., minimum 50 balls faced for batters, 60 legal balls bowled for bowlers) are mandatory.
2. **Innings Phase Confounding:**
   Batters opening in the Powerplay (overs 1–6) enjoy field restrictions (only 2 boundary riders), whereas Death-overs finishers (overs 16–20) face 5 boundary fielders and defensive yorkers/slower balls. Rankings must segment performance into phase-adjusted metrics (Powerplay vs Middle vs Death).
3. **Telemetry Gaps:**
   Because `bowl_speed` is 97.7% unrecorded, models cannot rely on radar gun speed. All pace-spin classifications must use the categorical `pace_or_spin` and `bowling_type` fields.
4. **Rain Abandonment Adjustments:**
   16 matches were abandoned without a ball bowled. Win percentage calculations must use $(\text{Wins} / \text{Completed Matches})$ rather than penalizing teams for weather abandonments.

---

## 10. Audit Sign-Off

The six CSV datasets inside `data/raw/` are verified as authentic, comprehensive, and referentially sound. All data quality edge cases have been identified with explicit engineering fixes.

**Status:** Awaiting user approval to proceed to Master Task 03 (IPL & T20I Data Filtering and Feature Pipeline).

