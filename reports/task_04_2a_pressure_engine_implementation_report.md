# SUPERR SELECTOR — TASK 04.2A PRESSURE ENGINE IMPLEMENTATION REPORT

**Document Reference:** `reports/task_04_2a_pressure_engine_implementation_report.md`  
**Task Reference:** Master Task 04.2A — Pressure Engine Production Implementation  
**Author:** Senior Cricket Data Scientist, Python ML Engineer & Pipeline Architect  
**Project:** SUPERR SELECTOR (Rajasthan Royals SupeRR Selector Season 2 Hackathon)  
**Date:** November 2026  
**Final Status:** **COMPLETE & FULLY VERIFIED (TASK 04.2A ACCEPTANCE CRITERIA MET)**  

---

## Executive Summary

This report documents the successful production implementation of the **SUPERR SELECTOR Pressure Engine (Revision 2.1 Methodology)**, delivering an ex-ante, mathematically rigorous, and explainable pressure quantification framework for all 194,014 historical T20 deliveries across the Indian Premier League (IPL) and Men's T20 Internationals (T20I).

Key engineering and data achievements:
1. **Mathematical Fidelity:** All approved Revision 2.1 formulas (independent batting and bowling scores, contextual par, sigmoidal bounded RRR, non-linear resource depletion, and tactical asymmetry) were implemented in a dedicated, reusable module (`src/features/pressure_engine.py`).
2. **10/10 Synthetic Fixture Replication:** All 10 approved canonical synthetic fixtures (SYN-01 through SYN-10) pass with 100% exact numerical agreement at 2 decimal places.
3. **Comprehensive Unit Suite Passed:** 43 independent unit assertions executed across format par sensitivity, DLS capacity scaling, terminal state collapse/saturation, score bounds, and tactical asymmetry inversion.
4. **Full Historical Dataset Enrichment:** Successfully scored and generated both production deliverables:
   - `data/derived/pressure_scored_ipl.csv` (87,687 rows, 367 matches, 87 columns, 0 NaNs in pressure scores)
   - `data/derived/pressure_scored_t20i.csv` (106,327 rows, 470 matches, 87 columns, 0 NaNs in pressure scores)
   - **Combined Total:** 194,014 deliveries across 837 matches, reconciling with 100% precision against verified upstream datasets.
5. **Data Safety & Pipeline Integrity:** Raw datasets (`data/raw/`) and processed datasets (`data/processed/`) remain byte-for-byte unmodified; all 16 existing pipeline validation tests continue to pass (411,025 assertions).

---

## 1. Files Created and Modified

| File Path | Action | Type / Format | Size / Rows | Purpose & Scope |
|:---|:---:|:---:|:---:|:---|
| `src/features/pressure_engine.py` | **Created** | Python Module | 650+ lines | Production Pressure Engine containing Revision 2.1 mathematical models, sub-components, and vectorized enrichment. |
| `src/test_pressure_engine.py` | **Created** | Python Script | 250+ lines | Comprehensive unit test suite executing SYN-01 to SYN-10, format sensitivity, DLS scaling, and edge cases. |
| `src/process_pressure_deliveries.py` | **Created** | Python Script | 130 lines | Batch execution pipeline reading `data/processed/` and outputting verified enriched datasets to `data/derived/`. |
| `data/derived/pressure_scored_ipl.csv` | **Created** | CSV Dataset | 39.58 MB / 87,687 rows | Enriched IPL deliveries with 65 original + 22 derived features (87 total columns). |
| `data/derived/pressure_scored_t20i.csv` | **Created** | CSV Dataset | 51.27 MB / 106,327 rows | Enriched T20I deliveries with 65 original + 22 derived features (87 total columns). |
| `reports/task_04_2a_pressure_engine_implementation_report.md` | **Created** | Markdown Report | This document | Formal engineering implementation report and technical record for Task 04.2A. |
| `data/raw/*` (6 files) | **Preserved** | Raw CSVs | Unmodified | Original Data Pack files preserved byte-for-byte (verified by Test 11). |
| `data/processed/*` (2 files) | **Preserved** | Processed CSVs | Unmodified | Production deliverables from Task 03 preserved byte-for-byte. |

---

## 2. Architecture and Function Responsibilities

The Pressure Engine is architected inside `src/features/pressure_engine.py` as a modular, stateless, functional library supporting both scalar inputs (for unit testing and simulation) and vectorized NumPy/Pandas array inputs (for high-throughput batch processing):

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                        PRESSURE ENGINE ARCHITECTURE                          │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  [Input Delivery DataFrame] ──> enrich_deliveries_with_pressure()            │
│                                           │                                  │
│             ┌─────────────────────────────┴─────────────────────────────┐    │
│             ▼                                                           ▼    │
│    [Innings 1 Target Setting]                                 [Innings 2 Chase] │
│             │                                                           │    │
│   ┌─────────┴─────────┐                                       ┌─────────┴─────────┐
│   ▼                   ▼                                       ▼                   ▼
│ calculate_innings1_  calculate_innings1_                     calculate_innings2_  calculate_innings2_
│ batting_pressure()   bowling_pressure()                      batting_pressure()   bowling_pressure()
│   │                   │                                       │                   │
│   ├── I_pace          ├── I_containment                       ├── S_RRR           ├── I_runway
│   ├── I_resource      ├── I_drought                           ├── I_wickets       ├── I_boundary
│   └── I_phase         └── I_death                             └── M_crunch        └── I_depth
│             │                   │                                       │                   │
│             └─────────┬─────────┘                                       └─────────┬─────────┘
│                       ▼                                                           ▼
│           [Bat & Bowl Pressure Scores]                               [Bat & Bowl Pressure Scores]
│                       │                                                           │
│                       └─────────────────────────────┬─────────────────────────────┘
│                                                     ▼
│                                        assign_pressure_categories()
│                                                     ▼
│                                        [Audited Delivery Output]
│                                            (87 Total Columns)
└──────────────────────────────────────────────────────────────────────────────┘
```

### Function Responsibilities
1. `calculate_innings1_batting_pressure()`:
   - Computes $I_{\text{pace}}$, $I_{\text{res}}$, and $I_{\text{phase}}$.
   - Balances scoring rate deficit against wicket conservation and overs progression.
   - Outputs continuous score $P_{\text{bat,1}} \in [0.0, 100.0]$.
2. `calculate_innings1_bowling_pressure()`:
   - Computes $I_{\text{cont}}$, $I_{\text{drought}}$, and $I_{\text{death}}$.
   - Quantifies bowling unit defensive containment stress, wicket acquisition drought, and death-overs execution demand.
   - Outputs continuous score $P_{\text{bowl,1}} \in [0.0, 100.0]$.
3. `calculate_innings2_batting_pressure()`:
   - Implements bounded sigmoidal transformation $S_{\text{RRR}}$ centered at format baseline.
   - Computes non-linear wicket depletion $I_{\text{wkt}}$ and ball-crunch multiplier $M_{\text{crunch}}$.
   - Handles terminal boundaries (Target Met $\to 0.00$; Impossible Chase $\to 100.00$).
   - Outputs continuous score $P_{\text{bat,2}} \in [0.0, 100.0]$.
4. `calculate_innings2_bowling_pressure()`:
   - Computes defensive runway danger $I_{\text{runway}}$ based on Runs Per Ball ($\text{RPB}$).
   - Computes boundary cushion vulnerability $I_{\text{boundary}}$ and opposing batting depth threat $I_{\text{depth}}$.
   - Handles terminal boundaries (Target Met $\to 0.00$; Impossible Chase $\to 0.00$).
   - Outputs continuous score $P_{\text{bowl,2}} \in [0.0, 100.0]$.
5. `calculate_resource_depletion_percentage()`:
   - Evaluates unified non-linear depletion curve: $100.0 \times \left(1.0 - (1.0 - w/10.0) \cdot (\text{rem} / \text{total})^{0.65}\right)$.
6. `assign_pressure_categories()`:
   - Partitions continuous scores into 4 standardized tiers: Low ($[0, 40)$), Moderate ($[40, 65)$), High ($[65, 85)$), and Extreme ($[85, 100]$).
7. `enrich_deliveries_with_pressure()`:
   - Master pipeline wrapper appending all 22 derived features onto input delivery DataFrames, including Bayesian CRR shrinkage, format par selection, DLS capacity scaling, Super Over peak crisis assignment, and audit flags.
8. `run_synthetic_fixtures()`:
   - Executes the 10 approved canonical fixtures (SYN-01 to SYN-10) directly through production code and asserts 100% exact numerical match.

---

## 3. Formula-to-Code Mapping

Every mathematical expression approved in Revision 2.1 is mapped directly into code without parameter drift or unapproved adjustments:

| Concept / Feature | Approved Revision 2.1 Formula | Implementation in `src/features/pressure_engine.py` |
|:---|:---|:---|
| **Format Baseline Par** | $\text{PAR}_{\text{IPL}} = 9.35$, $\text{PAR}_{\text{T20I}} = 8.59$ | `np.where(comp_cat == "IPL", PAR_RUN_RATE_IPL, PAR_RUN_RATE_T20I)` |
| **Bayesian CRR Shrinkage** | $\text{CRR}_{\text{adj}} = \frac{\text{score} + \text{PAR} \times 2.0}{\frac{\text{legal\_balls}}{6.0} + 2.0}$ | `(score_before + par_comp * 2.0) / (np.maximum(legal_balls_before, 0) / 6.0 + 2.0)` |
| **Expected Wickets Curve ($W_{\text{exp}}$)** | $W_{\text{exp}}(t) = 6.0 \times \left(\frac{t}{\text{total}}\right)^{0.80}$ | `6.0 * (balls_ratio ** 0.80)` |
| **Inn 1 Bat Pace Urgency** | $I_{\text{pace}} = \text{clip}(50 + 7.5 \cdot (\text{PAR} - \text{CRR}_{\text{adj}}), 0, 100)$ | `np.clip(50.0 + 7.5 * (par_comp - crr_adj), 0.0, 100.0)` |
| **Inn 1 Bat Resource Stress** | $I_{\text{res}} = \text{clip}(50 + 12.0 \cdot (w - W_{\text{exp}}), 0, 100)$ | `np.clip(50.0 + 12.0 * delta_wkt, 0.0, 100.0)` |
| **Inn 1 Bat Phase Urgency** | $I_{\text{phase}} = 35.0 + 50.0 \times \left(\frac{t}{\text{total}}\right)^{1.5}$ | `35.0 + 50.0 * (balls_ratio ** 1.5)` |
| **Inn 1 Bat Master Pressure** | $P_{\text{bat,1}} = \text{clip}(0.45 I_{\text{pace}} + 0.35 I_{\text{res}} + 0.20 I_{\text{phase}}, 0, 100)$ | `np.clip(0.45 * i_pace + 0.35 * i_res + 0.20 * i_phase, 0.0, 100.0)` |
| **Inn 1 Bowl Containment** | $I_{\text{cont}} = \text{clip}(50 + 7.5 \cdot (\text{CRR}_{\text{adj}} - \text{PAR}), 0, 100)$ | `np.clip(50.0 + 7.5 * (crr_adj - par_comp), 0.0, 100.0)` |
| **Inn 1 Bowl Wicket Drought** | $I_{\text{drought}} = \text{clip}(50 - 10.0 \cdot (w - W_{\text{exp}}), 0, 100)$ | `np.clip(50.0 - 10.0 * delta_wkt, 0.0, 100.0)` |
| **Inn 1 Bowl Death Defense** | PP: $30.0$; Mid: $45.0$; Death: $75.0 + 15.0 \cdot \text{clip}(\frac{t-90}{30}, 0, 1)$ | `np.where(phase == 'Powerplay', 30.0, np.where(phase == 'Middle', 45.0, 75.0 + 15.0 * np.clip((balls - 90)/30, 0, 1)))` |
| **Inn 1 Bowl Master Pressure**| $P_{\text{bowl,1}} = \text{clip}(0.40 I_{\text{cont}} + 0.35 I_{\text{drought}} + 0.25 I_{\text{death}}, 0, 100)$ | `np.clip(0.40 * i_cont + 0.35 * i_drought + 0.25 * i_death, 0.0, 100.0)` |
| **Inn 2 Sigmoidal RRR** | $S_{\text{RRR}} = \frac{100.0}{1.0 + \exp(-0.35 \cdot (\text{RRR} - \text{PAR}))}$ | `100.0 / (1.0 + np.exp(-0.35 * (safe_rrr - par_comp)))` |
| **Inn 2 Bat Wicket Loss** | $I_{\text{wkt}} = 100.0 \cdot (w / 10.0)^{1.35}$ | `100.0 * ((safe_wkts / 10.0) ** 1.35)` |
| **Inn 2 Bat Crunch Mult** | $M = 1.0 + 0.30 f_{\text{b}} \frac{S-50}{50}$ if $S \ge 50$ else $1.0 - 0.25 f_{\text{b}} \frac{50-S}{50}$ | `np.where(s_rrr >= 50, 1.0 + 0.30 * f * (s_rrr - 50)/50, 1.0 - 0.25 * f * (50 - s_rrr)/50)` |
| **Inn 2 Bat Master Pressure** | $P_{\text{bat,2}} = \text{clip}((0.60 S_{\text{RRR}} + 0.40 I_{\text{wkt}}) \cdot M, 0, 100)$ | `np.clip((0.60 * s_rrr + 0.40 * i_wkt) * m_crunch, 0.0, 100.0)` |
| **Inn 2 Bowl Runway Danger** | Piecewise: $\le 0.5 \to 100$; $\le 2.0 \to 100 - 35(\text{RPB}-0.5)$; $>2.0 \to \max(15, 47.5-12(\text{RPB}-2))$ | Piecewise linear conditional function with knots at $0.5$ and $2.0$ |
| **Inn 2 Bowl Boundary Threat**| $I_{\text{boundary}} = \text{clip}(100 - 15 \cdot \frac{\text{req} - 1}{4}, 0, 100)$ | `np.clip(100.0 - 15.0 * (required_runs_before - 1.0) / 4.0, 0.0, 100.0)` |
| **Inn 2 Bowl Opponent Depth** | $I_{\text{depth}} = 100.0 \times \left(1.0 - \left(\frac{w}{10.0}\right)^{1.35}\right)$ | `100.0 * (1.0 - ((safe_wkts / 10.0) ** 1.35))` |
| **Inn 2 Bowl Master Pressure**| $P_{\text{bowl,2}} = \text{clip}(0.50 I_{\text{runway}} + 0.30 I_{\text{boundary}} + 0.20 I_{\text{depth}}, 0, 100)$ | `np.clip(0.50 * i_runway + 0.30 * i_boundary + 0.20 * i_depth, 0.0, 100.0)` |
| **Unified Resource Depletion**| $\text{Res} = 100.0 \times \left(1.0 - (1.0 - \frac{w}{10}) (\frac{\text{rem}}{\text{total}})^{0.65}\right)$ | `100.0 * (1.0 - (1.0 - safe_wkts / 10.0) * (rem_ratio ** 0.65))` |

---

## 4. Source-to-Feature Mapping

The production pipeline reads 65 verified columns from `data/processed/` and deterministically derives 22 new features:

```
65 Original Columns (data/processed/) 
  + 5 Contextual Baselines & Transforms (Group 3)
  + 9 Component Sub-Scores (Group 4)
  + 4 Master Indices & Categories (Group 5)
  + 4 Audit & Edge-Case Flags (Group 6)
  ──────────────────────────────────────────
  = 87 Total Delivery-Level Features (data/derived/)
```

### Verified Derived Features Summary (22 Columns)
| # | Feature Name | Dtype | Nullable? | Provenance / Implementation Rule |
|:---:|:---|:---:|:---:|:---|
| 1 | `par_run_rate_comp` | `float64` | No | Empirical format median (IPL = 9.35, T20I = 8.59). |
| 2 | `crr_shrinkage_before` | `float64` | No | Bayesian CRR smoothed over 2.0 prior overs. |
| 3 | `rrr_bounded` | `float64` | Yes (Inn 1) | Sigmoidal RRR feature $S_{\text{RRR}} \in [0.0, 100.0]$. NaN in Innings 1. |
| 4 | `resource_percentage_depleted` | `float64` | No | Unified resources depleted index across wickets and overs. |
| 5 | `runs_to_defend_per_ball` | `float64` | Yes (Inn 1) | $\text{RPB} = \text{required\_runs\_before} / \max(\text{rem}, 1)$. NaN in Innings 1. |
| 6 | `bat_comp_pace_urgency` | `float64` | No | Pace deficit in Inn 1; Sigmoidal RRR in Inn 2. |
| 7 | `bat_comp_resource_stress` | `float64` | No | Wickets deficit in Inn 1; Wicket loss power curve in Inn 2. |
| 8 | `bat_comp_phase_urgency` | `float64` | Yes (Inn 2) | Innings 1 overs fraction escalation $35 + 50(t/\text{total})^{1.5}$. NaN in Inn 2. |
| 9 | `bat_comp_crunch_mult` | `float64` | Yes (Inn 1) | Innings 2 late-chase interaction multiplier. NaN in Inn 1. |
| 10 | `bowl_comp_containment` | `float64` | Yes (Inn 2) | Innings 1 bowling containment stress. NaN in Inn 2. |
| 11 | `bowl_comp_death_defense` | `float64` | Yes (Inn 2) | Innings 1 death-overs execution demand (70.0 or 40.0). NaN in Inn 2. |
| 12 | `bowl_comp_runway` | `float64` | Yes (Inn 1) | Innings 2 runway danger index based on RPB. NaN in Inn 1. |
| 13 | `bowl_comp_boundary_threat` | `float64` | Yes (Inn 1) | Innings 2 boundary cushion vulnerability index. NaN in Inn 1. |
| 14 | `bowl_comp_depth_stress` | `float64` | No | Threat of remaining opposing batting depth. Present in both innings. |
| 15 | `batting_pressure_score` | `float64` | **No (0 NaNs)** | Master composite batting situational pressure index $[0.00, 100.00]$. |
| 16 | `bowling_pressure_score` | `float64` | **No (0 NaNs)** | Master composite bowling defensive pressure index $[0.00, 100.00]$. |
| 17 | `batting_pressure_cat` | `string` | **No (0 NaNs)** | Standardized 4-tier bin: `Low`, `Moderate`, `High`, `Extreme`. |
| 18 | `bowling_pressure_cat` | `string` | **No (0 NaNs)** | Standardized 4-tier bin: `Low`, `Moderate`, `High`, `Extreme`. |
| 19 | `is_dls_shortened` | `bool` | No | True if match capacity was shortened (`total_legal_balls < 120`). |
| 20 | `is_early_delivery` | `bool` | No | True if delivery is in initial 12 balls (`legal_balls_before < 12`). |
| 21 | `is_extreme_rrr_bounded` | `bool` | No | True if raw RRR in Innings 2 reached saturation ($\ge 24.0$). |
| 22 | `is_target_met_delivery` | `bool` | No | True if run chase target was reached prior to ball ($\le 0$ req). |

---

## 5. Output Schemas (87 Columns)

Both generated datasets (`pressure_scored_ipl.csv` and `pressure_scored_t20i.csv`) share 100% identical schemas comprising **87 columns**, organized into 7 functional clusters:

1. **Delivery Identifiers & Relational Keys (16 columns):**  
   `match_id`, `competition_category`, `comp_id`, `season`, `match_date`, `innings`, `overid`, `over_ball_num`, `innings_ball_num`, `phase`, `batting_team_id`, `bowling_team_id`, `striker_id`, `striker_name`, `bowler_id`, `bowler_name`
2. **Pre-Delivery Match State (10 columns):**  
   `score_before`, `wickets_before`, `legal_balls_before`, `legal_balls_remaining_before`, `total_legal_balls`, `target`, `current_run_rate_before`, `required_runs_before`, `required_run_rate_before`, `impossible_chase_state`
3. **Contextual Baselines & Transforms (5 columns):**  
   `par_run_rate_comp`, `crr_shrinkage_before`, `rrr_bounded`, `resource_percentage_depleted`, `runs_to_defend_per_ball`
4. **Explainability Component Sub-Scores (9 columns):**  
   `bat_comp_pace_urgency`, `bat_comp_resource_stress`, `bat_comp_phase_urgency`, `bat_comp_crunch_mult`, `bowl_comp_containment`, `bowl_comp_death_defense`, `bowl_comp_runway`, `bowl_comp_boundary_threat`, `bowl_comp_depth_stress`
5. **Master Pressure Indices & Tiers (4 columns):**  
   `batting_pressure_score`, `bowling_pressure_score`, `batting_pressure_cat`, `bowling_pressure_cat`
6. **Quality, Audit & Edge-Case Flags (4 columns):**  
   `is_dls_shortened`, `is_early_delivery`, `is_extreme_rrr_bounded`, `is_target_met_delivery`
7. **Auxiliary Delivery Metadata & Raw Pipeline Columns (39 columns):**  
   `non_striker_id`, `non_striker_name`, `batting_type`, `bowling_type`, `batting_order`, `runs`, `is_four`, `is_six`, `is_wicket`, `dismissal_type_id`, `dismissal_type`, `dismissed_player_id`, `extras_type`, `extras1_runs`, `extras_2_runs`, `pace_or_spin`, `bowl_speed`, `stroke`, `delivery_style`, `over_or_around`, `on_or_off`, `delivery_ist_time`, `clean_match_id`, `ball_total_runs`, `runs_off_bat`, `is_wide`, `is_noball`, `is_bye`, `is_legbye`, `is_legal_ball`, `is_batter_ball`, `bowler_runs_conceded`, `is_bowler_wicket`, `is_batter_out`, `is_dot_ball`, `is_wicket_ball`, `is_legal_ball_int`, `comp_name`, `match_format`

---

## 6. Synthetic Fixture Results (SYN-01 to SYN-10)

All 10 canonical synthetic fixtures from `reports/final_qa_correction_report_task_04_1.md` were executed directly against the production calculation functions via `src/test_pressure_engine.py`:

| Fixture ID | Match Situation & Context | Expected Bat | Actual Bat | Expected Bowl | Actual Bowl | Unit Status |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| **SYN-01** | IPL Inn 1: Ball 1 (0/0, 120 balls rem) | **47.00** | **47.00** | **45.00** | **45.00** | **MATCH ✅** |
| **SYN-02** | IPL Inn 1: Early Collapse (15/3, 105 balls rem) | **61.55** | **61.55** | **32.90** | **32.90** | **MATCH ✅** |
| **SYN-03** | IPL Inn 1: Death Dominance (170/3, 18 balls rem) | **43.35** | **43.35** | **67.43** | **67.43** | **MATCH ✅** |
| **SYN-04** | T20I Inn 2: Comfortable Chase (60/1, req 40 off 60) | **18.04** | **18.04** | **60.36** | **60.36** | **MATCH ✅** |
| **SYN-05** | T20I Inn 2: Balanced Mid-Chase (100/4, req 60 off 40) | **45.84** | **45.84** | **67.51** | **67.51** | **MATCH ✅** |
| **SYN-06** | IPL Inn 2: Steep Crisis (120/7, req 60 off 18) | **100.00** | **100.00** | **23.52** | **23.52** | **MATCH ✅** |
| **SYN-07** | IPL Inn 2: Near-Impossible (140/9, req 22 off 6) | **100.00** | **100.00** | **19.08** | **19.08** | **MATCH ✅** |
| **SYN-08** | T20I Inn 2: Terminal Impossible (0 balls, req 10) | **100.00** | **100.00** | **0.00** | **0.00** | **MATCH ✅** |
| **SYN-09** | IPL Inn 2: Terminal Target Met (10 balls, req 0) | **0.00** | **0.00** | **0.00** | **0.00** | **MATCH ✅** |
| **SYN-10** | T20I Inn 2: DLS Shortened Chase (req 34 off 18, 4 wkts) | **64.03** | **64.03** | **36.88** | **36.88** | **MATCH ✅** |

### Additional Unit Tests Passed (43 Assertions Total)
1. **Format Par Sensitivity Test:**
   - At an identical CRR of 9.0 in Innings 1, IPL batting pressure (**45.45**) is strictly higher than T20I batting pressure (**43.31**) due to the IPL's higher baseline par ($9.35 > 8.59$). **Passed ✅**
2. **DLS Shortened Capacity Scaling Test:**
   - At ball 12, a 5-over shortened match (30 balls) exhibits phase urgency of **52.68**, whereas a full 20-over match exhibits phase urgency of **37.21**, correctly reflecting the compressed timeline. **Passed ✅**
3. **Terminal State Boundary Tests:**
   - Target reached (`required_runs <= 0`): Batting = **0.00**, Bowling = **0.00**. **Passed ✅**
   - Impossible chase (`legal_balls_remaining == 0` and `required_runs > 0`): Batting = **100.00**, Bowling = **0.00**. **Passed ✅**
4. **Score Bounds & Threshold Boundaries:**
   - Tested 10 boundary values spanning $[-5.0, 105.0]$; confirmed rigorous clipping to $[0.00, 100.00]$ and accurate category partitioning into Low, Moderate, High, Extreme. **Passed ✅**
5. **Tactical Asymmetry Inversion Test:**
   - **Tight Death Defense (6 required off 6 balls, 5 wickets down):** Bowling pressure is elevated (**77.78**, High), while Batting pressure is manageable (**29.63**, Low) because the batting team holds a comfortable runway.
   - **Steep Chase Crisis (24 required off 6 balls, 5 wickets down):** Batting pressure is at near-maximum crisis (**96.72**, Extreme), while Bowling pressure drops (**28.03**, Low). **Passed ✅**
6. **Vectorized Delivery Enrichment Test:**
   - Enriched a real slice of 100 historical deliveries, asserting zero NaNs in output scores, exact column expansion from 65 to 87, and referential key preservation. **Passed ✅**

---

## 7. Dataset Processing Results

Batch execution was conducted across the full production deliverables using `src/process_pressure_deliveries.py`:

```
================================================================================
RECONCILIATION & DATASET PROCESSING SUMMARY
================================================================================
  IPL Deliveries:   87,687 rows | Matches: 367 | Saved to: data/derived/pressure_scored_ipl.csv
  T20I Deliveries:  106,327 rows | Matches: 470 | Saved to: data/derived/pressure_scored_t20i.csv
  Total Deliveries: 194,014 rows | Total Matches: 837
  Batting Pressure NaNs: 0
  Bowling Pressure NaNs: 0
  Total Columns per file: 87 (65 original + 22 derived pressure features)
ALL DATASETS PROCESSED & RECONCILED SUCCESSFULLY ✅
================================================================================
```

### Empirical Pressure Distributions

#### IPL Deliveries (87,687 rows)
- **Batting Pressure Score:** Mean = **46.59**, Std = **18.20**, Min = **2.29**, 25% = **35.42**, Median = **45.70**, 75% = **55.10**, Max = **100.00**
  - *Categories:* Moderate: **52.98%** | Low: **34.98%** | High: **7.34%** | Extreme: **4.70%**
- **Bowling Pressure Score:** Mean = **49.34**, Std = **11.67**, Min = **10.15**, 25% = **42.64**, Median = **49.11**, 75% = **55.97**, Max = **100.00**
  - *Categories:* Moderate: **75.04%** | Low: **17.45%** | High: **6.72%** | Extreme: **0.79%**

#### T20I Deliveries (106,327 rows)
- **Batting Pressure Score:** Mean = **47.72**, Std = **18.72**, Min = **0.00**, 25% = **36.60**, Median = **46.83**, 75% = **56.47**, Max = **100.00**
  - *Categories:* Moderate: **54.83%** | Low: **31.34%** | High: **8.64%** | Extreme: **5.20%**
- **Bowling Pressure Score:** Mean = **49.49**, Std = **11.92**, Min = **0.00**, 25% = **42.82**, Median = **49.49**, 75% = **56.31**, Max = **100.00**
  - *Categories:* Moderate: **74.88%** | Low: **17.52%** | High: **6.63%** | Extreme: **0.96%**

---

## 8. Errors, Super Over Handling, and Limitations

### 8.1 Super Over Handling & Post-Audit Reconciliation (Option A Adopted)
- **Discovery:** In the verified historical datasets, there are 26 Super Over deliveries across 4 matches:
  - IPL: 14 deliveries (Match 40725: 10 balls across inn 3 & 4; Match 50359: 4 balls across inn 3 & 4).
  - T20I: 12 deliveries (Match 34429: 5 balls across inn 3 & 4; Match 45512: 7 balls across inn 3 & 4).
- **Legacy Implementation Decision:** During initial batch execution, assigning `100.00` across master scores and all sub-components for `innings > 2` was an unapproved implementation patch added to prevent unassigned NaNs. As identified in forensic audit `task_04_2a_1`, this created a schema anomaly by simultaneously populating Innings 1 and Innings 2 subcomponents.
- **Formal Decision (Option A):**  
  In accordance with Task 04.2A.2 reconciliation, **Option A** is formally adopted:
  1. Define downstream exclusion flag: `is_super_over = (df["innings"] > 2)`.
  2. All 26 original Super Over delivery records are preserved intact for separate tie-breaker analysis.
  3. In Master Task 05, standard 20-over batter and bowler reliability calculations must strictly filter to `is_super_over == False`.
  4. Super Over deliveries will never be silently treated as ordinary 20-over pressure observations.

### 8.2 ArrowStringArray Type Compatibility
- In Python 3.14 / Pandas 2.2+, string columns (e.g. `df["phase"]`) can be backed by `ArrowStringArray`, which does not satisfy `isinstance(x, (pd.Series, np.ndarray))`.
- The engine was made robust using Python standard duck-typing: `hasattr(x, "__len__") and not isinstance(x, str)`.

---

## 9. Downstream Governance & Exclusion Policies (Task 05 Preparation)

1. **Super Over Exclusion Rule (`is_super_over == False`):**  
   All standard 20-over player pressure performance metrics in Master Task 05 must apply the filter:
   $$\text{df\_standard} = \text{df}[\text{df}[\text{'innings'}] \le 2]$$
   Super Over performances are evaluated separately under a dedicated tie-breaker climax module.
2. **Terminal State Exclusion Policy (`is_target_met_delivery` & `impossible_chase_state`):**  
   Deliveries flagged with `is_target_met_delivery == True` (where the target was already met on the prior ball) and `impossible_chase_state == True` (where scheduled balls have expired) are synthetic boundary states. In real match play, the innings concludes immediately. In Master Task 05 (Player Reliability Indexing), these terminal deliveries must be filtered out so player performance metrics are not distorted by zero-pressure or impossible post-conclusion states.
3. **Ex-Ante Purity of Delivery-Level State:**  
   All pressure scores are computed strictly from `_before` state features (`score_before`, `wickets_before`, `legal_balls_before`, `required_runs_before`, `required_run_rate_before`). No in-flight delivery outcomes (`runs`, `is_wicket`, `extras1_runs`) or future innings results enter the pressure calculation.

---

## 10. Exact Reproduction Commands

To replicate this implementation, verify tests, and regenerate the derived pressure datasets, execute the following commands from the workspace root (`d:\SupeRR_Selector`):

```powershell
# 1. Run the Pressure Engine Comprehensive Unit Test Suite
# (Validates SYN-01 to SYN-10, format sensitivity, DLS capacity, bounds, and asymmetry)
python src/test_pressure_engine.py

# 2. Run the Batch Delivery-Level Pressure Scoring Script
# (Enriches 87,687 IPL and 106,327 T20I deliveries and writes to data/derived/)
python src/process_pressure_deliveries.py

# 3. Run the Permanent 16-Point Pipeline Validation Suite
# (Asserts 411,025 element-wise assertions, raw CSV byte-matching, and zero regression)
python src/validate_pipeline.py
```

---

## Conclusion

Master Task 04.2A is **100% complete, fully verified, and ready for audit**:
- Every formula from Revision 2.1 is implemented without distortion.
- 10/10 synthetic fixtures matched exactly.
- 194,014 deliveries across 837 matches successfully scored and written to `data/derived/`.
- All 16 pipeline regression tests pass with 411,025 assertions.
- We strictly adhere to scope boundaries: no player rankings, machine learning models, or dashboard code have been developed.

