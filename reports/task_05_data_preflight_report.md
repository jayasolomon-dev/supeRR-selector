# SUPERR SELECTOR — TASK 05 DATA PREFLIGHT REPORT

**Document Reference:** `reports/task_05_data_preflight_report.md`  
**Task Reference:** Master Task 05 — Phase A: Data Preflight & Identity Verification  
**Author:** Senior Cricket Data Scientist, Python Data Engineer & QA Auditor  
**Project:** Rajasthan Royals SupeRR Selector Season 2 Hackathon  
**Target Ingestion Files:**
- `data/derived/pressure_scored_ipl.csv` (87 columns, 87,687 raw deliveries)
- `data/derived/pressure_scored_t20i.csv` (87 columns, 106,327 raw deliveries)
- Raw and processed relational tables in `data/raw/` and `data/processed/`  
**Date:** November 12, 2026  
**Gate 05.0 Verdict:** **PASS (100% Player Identity Reconciliation; Certified Safe for Player Aggregations)**  

---

## 1. Executive Summary & Gate 05.0 Verification

Before executing player reliability modeling in Master Task 05, this preflight audit inspected all raw, processed, and derived datasets to establish verified source-to-feature mappings, validate delivery accounting semantics, audit player primary key uniqueness, and confirm match/team coverage.

### Key Preflight Findings
1. **Clean Cohort Reconciliation:** Confirmed exact target counts for the clean standard competitive cohort (`innings <= 2 & ~is_target_met_delivery`):
   - IPL: **87,673 deliveries** (367 matches)
   - T20I: **106,303 deliveries** (470 matches)
   - Combined: **193,976 deliveries** (837 matches)
2. **Zero Nulls in Critical Identifiers:** Confirmed 0 null values across `striker_id`, `striker_name`, `bowler_id`, `bowler_name`, `non_striker_id`, `non_striker_name`, `match_id`, and `innings`.
3. **Player Primary Key Integrity:**
   - Total distinct players active in the clean cohort: **891 players** (824 distinct batters, 596 distinct bowlers).
   - Bijective ID-to-Name Mapping: **0 player IDs map to multiple names**.
   - Name Collisions Detected: Exactly 2 player names map to multiple IDs ("Abdul Samad" and "Haider Ali"), conclusively proving that **all player-level aggregations and models must group strictly by `player_id`**, treating `player_name` solely as a display label.
4. **Relational Table Coverage:**
   - `competition_team_player_mapping.csv`: **891 / 891 players (100.00%)** successfully resolved.
   - `playing_eleven.csv`: **837 / 837 matches (100.00%)** successfully resolved.
   - `matches.csv`: **837 / 837 matches (100.00%)** successfully resolved.
5. **Authoritative Delivery Accounting Confirmed:** Verified that the derived datasets already contain the verified, validated execution tags (`is_batter_ball`, `runs_off_bat`, `bowler_runs_conceded`, `is_bowler_wicket`, `is_batter_out`, `is_dot_ball`, `is_legal_ball`) from the upstream pipeline.

---

## 2. File Schemas & Column Inventories

The audit verified schemas across all ten target files:

### 2.1 Derived Datasets (`data/derived/`)
- **`pressure_scored_ipl.csv` & `pressure_scored_t20i.csv` (87 columns each):**
  - Columns 0–32: Original delivery fields from `ball_by_ball.csv`.
  - Columns 33–64: Upstream match-state, legality, and execution tags from `data_pipeline.py`.
  - Columns 65–86: Derived pressure features, baseline par rates, continuous scores, categorical bins, and quality flags from `pressure_engine.py`.

### 2.2 Processed Datasets (`data/processed/`)
- **`ipl_deliveries.csv` & `t20i_deliveries.csv` (65 columns each):**
  - Baseline feature tables containing all pre-delivery game state features before pressure engine derivation.

### 2.3 Raw Relational Tables (`data/raw/`)
| File Name | Row Count | Column Count | Primary Key / Indexing Columns |
| :--- | :---: | :---: | :--- |
| `ball_by_ball.csv` | 194,014 | 33 | `[match_id, innings, overid, over_ball_num]` |
| `competition_team_player_mapping.csv` | 6,413 | 6 | `[comp_id, team_id, player_id]` |
| `playing_eleven.csv` | 28,381 | 9 | `[match_id, team_id, player_id]` |
| `teams.csv` | 185 | 3 | `[comp_id, team_id]` |
| `matches.csv` | 837 | 22 | `[match_id]` |
| `competitions.csv` | 33 | 4 | `[comp_id]` |

---

## 3. Delivery Accounting & Rule Specifications

To ensure strict cricket statistical compliance, the accounting rules already validated in `src/data_pipeline.py` and stored in `data/derived/` are formally documented:

### 3.1 Batting Metrics Accounting
- **Batter Balls Faced (`is_batter_ball`):**
  $$\text{is\_batter\_ball} = (\text{extras\_type} \ne \text{'wide'})$$
  - Wides do **not** count as a ball faced by the batter ($7,472$ wide deliveries across the cohort).
  - No-balls **do** count as a ball faced ($824$ no-ball deliveries: $565$ Overstep + $259$ other).
  - Total batter balls faced in clean cohort: **186,504 balls**.
- **Runs Scored off Bat (`runs_off_bat`):**
  - Uses `runs_off_bat` (or `runs`), strictly isolating runs scored by the batter's stroke.
  - Excludes wide penalties, no-ball penalties, byes, and leg-byes.
  - Total batter runs in clean cohort: **261,072 runs**.
- **Boundaries (`is_four`, `is_six`):**
  - Fours: $21,114$ | Sixes: $9,680$.
- **Batter Dismissal (`is_batter_out`):**
  - Evaluates: `is_wicket & (striker_id == dismissed_player_id)`.
  - Accurately accounts for non-striker run-outs ($259$ deliveries) where a wicket fell but the striker was not dismissed.
  - Total striker dismissals in clean cohort: **10,215 dismissals**.

### 3.2 Bowling Metrics Accounting
- **Bowler Legal Balls (`is_legal_ball`):**
  $$\text{is\_legal\_ball} = \sim\text{extras\_type}.\text{isin}([\text{'wide'}, \text{'overstep'}, \text{'other'}])$$
  - Wides ($7,472$) and no-balls ($824$) do **not** increment the legal delivery count.
  - Total bowler legal balls in clean cohort: **185,680 balls** ($30,946.4$ overs).
- **Bowler Runs Conceded (`bowler_runs_conceded`):**
  $$\text{bowler\_runs\_conceded} = \text{runs\_off\_bat} + \mathbb{I}_{[\text{wide, noball}]} \times \text{extras1\_runs}$$
  - Byes ($505$ balls) and leg-byes ($2,661$ balls) are **not** debited to the bowler.
  - Total bowler runs conceded in clean cohort: **270,776 runs**.
- **Bowler-Credited Wickets (`is_bowler_wicket`):**
  - Credited dismissals strictly include: `Caught` ($7,326$), `Bowled` ($1,689$), `LBW` ($666$), `Stumped` ($200$), and `Hit Wicket` ($17$).
  - Uncredited dismissals excluded from bowler wickets: `RunOut` ($571$), `Retire Out` ($6$), `Obstructing the Field` ($2$).
  - Total bowler credited wickets in clean cohort: **9,898 wickets**.
- **Bowler Dot Balls (`is_dot_ball`):**
  $$\text{is\_dot\_ball} = (\text{runs\_off\_bat} == 0) \ \& \ (\text{clean\_extras} == \text{'none'})$$
  - Total dot balls in clean cohort: **68,172 balls** ($36.71\%$ of legal balls).

---

## 4. Player Identity Census & Disambiguation

### 4.1 Population Counts by Role and Format
In the standard competitive cohort ($193,976$ deliveries):

| Competition Format | Total Deliveries | Unique Strikers | Unique Bowlers | Total Unique Players |
| :--- | :---: | :---: | :---: | :---: |
| **IPL Cohort** | 87,673 | 341 | 260 | 381 |
| **T20I Cohort** | 106,303 | 665 | 479 | 709 |
| **Combined Cohort** | **193,976** | **824** | **596** | **891** |

### 4.2 Disambiguation Audit: Name Collisions
A cross-check of `player_id` vs. `player_name` revealed:
- **0 Player IDs map to multiple names** (every ID has a single unambiguous name string).
- **2 Player Names map to multiple IDs:**
  1. `"Abdul Samad"`:
     - `player_id = 7446`: Abdul Samad (Sunrisers Hyderabad, IPL / India domestic).
     - `player_id = 6922`: Abdul Samad (Canada, Men's T20I Associate).
  2. `"Haider Ali"`:
     - `player_id = 7338`: Haider Ali (Pakistan national team).
     - `player_id = 28756`: Haider Ali (Norway / Associate cricket).

> [!IMPORTANT]
> **Mandatory Modeling Rule:** All aggregations, groupings, shrinkage estimators, and reliability tables in Task 05 must use `player_id` as the primary key. Merging on `player_name` is strictly prohibited to prevent conflating distinct players.

---

## 5. Pressure Cohort Distribution in Clean Data

Using the authoritative thresholds ($[0, 40)$ Low, $[40, 65)$ Moderate, $[65, 85)$ High, $[85, 100]$ Extreme):

### 5.1 Batting Pressure Distribution
- **Normal Pressure Cohort ($P_{\text{bat}} < 40$):** **64,008 balls** ($33.00\%$)
- **Moderate Pressure Cohort ($40 \le P_{\text{bat}} < 65$):** **104,755 balls** ($54.00\%$)
- **High Pressure Cohort ($P_{\text{bat}} \ge 65$):** **25,213 balls** ($13.00\%$)
  - High Tier ($65 \le P_{\text{bat}} < 85$): $15,617$ balls ($8.05\%$)
  - Extreme Tier ($P_{\text{bat}} \ge 85$): $9,596$ balls ($4.95\%$)

### 5.2 Bowling Pressure Distribution
- **Normal Pressure Cohort ($P_{\text{bowl}} < 40$):** **33,929 balls** ($17.49\%$)
- **Moderate Pressure Cohort ($40 \le P_{\text{bowl}} < 65$):** **145,419 balls** ($74.97\%$)
- **High Pressure Cohort ($P_{\text{bowl}} \ge 65$):** **14,628 balls** ($7.54\%$)
  - High Tier ($65 \le P_{\text{bowl}} < 85$): $12,945$ balls ($6.67\%$)
  - Extreme Tier ($P_{\text{bowl}} \ge 85$): $1,683$ balls ($0.87\%$)

---

## 6. Gate 05.0 Audit Determination

- **Completeness:** 100% of rows have verified player IDs and outcomes.
- **Relational Integrity:** 0 orphan players, 0 orphan matches.
- **Delivery Accounting:** 100% verified against approved pipeline definitions.
- **Gate 05.0 Status:** **PASS ✅ — Cleared to proceed to Phase B (Clean Player Analytics Cohort Loader).**

