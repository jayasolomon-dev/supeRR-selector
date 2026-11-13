# SUPERR SELECTOR — TASK 05 ANALYSIS SPECIFICATION

**Document Reference:** `reports/task_05_analysis_specification.md`  
**Task Reference:** Master Task 05 — Phase C: Player Reliability Analysis Specification  
**Author:** Senior Cricket Data Scientist, Statistical Modeler & Lead Performance Analyst  
**Project:** Rajasthan Royals SupeRR Selector Season 2 Hackathon  
**Target Pipelines:** `src/analytics/task_05_batting.py` & `src/analytics/task_05_bowling.py`  
**Date:** November 12, 2026  
**Status:** **AUTHORITATIVE SPECIFICATION**  

---

## 1. Objective & Analytical Architecture

The objective of Master Task 05 is to establish an objective, statistically defensible framework that evaluates **player reliability under pressure** compared with normal match conditions in competitive T20 cricket (IPL and Men's T20I).

Rather than evaluating overall raw volume, this system isolates situational pressure at the delivery level and measures whether a player's performance escalates, maintains stability, or degrades when operating in crisis match contexts.

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                             Clean Analytical Cohort                              │
│                    (193,976 Deliveries: 87,673 IPL + 106,303 T20I)               │
└─────────────────────────────────────────┬────────────────────────────────────────┘
                                          │
                  ┌───────────────────────┴───────────────────────┐
                  ▼                                               ▼
     Batting Pressure Engine                         Bowling Pressure Engine
  (df['batting_pressure_score'])                  (df['bowling_pressure_score'])
                  │                                               │
        ┌─────────┴─────────┐                           ┌─────────┴─────────┐
        ▼                   ▼                           ▼                   ▼
  Normal Cohort       High Pressure               Normal Cohort       High Pressure
     (P < 40)            (P >= 65)                   (P < 40)            (P >= 65)
   [Low: 33.0%]    [High+Ext: 13.0%]               [Low: 17.5%]     [High+Ext: 7.5%]
        │                   │                           │                   │
        └─────────┬─────────┘                           └─────────┬─────────┘
                  │                                               │
                  ▼                                               ▼
         Batting Differential                            Bowling Differential
      ΔSR, ΔDismissal, ΔDot%                          ΔEcon, ΔWktRate, ΔDot%
                  │                                               │
                  ▼                                               ▼
          Empirical-Bayes                                 Empirical-Bayes
        Shrinkage & Priors                              Shrinkage & Priors
                  │                                               │
                  ▼                                               ▼
       Batter Reliability Index                        Bowler Reliability Index
```

---

## 2. Pressure & Normal Cohort Definitions

Deliveries are partitioned strictly using pre-delivery continuous master pressure scores:

| Analytical Cohort | Operational Filter | Category Composition | Batting Cohort Count (%) | Bowling Cohort Count (%) | Tactical Meaning |
| :--- | :---: | :--- | :---: | :---: | :--- |
| **Normal Pressure** | $P < 40.0$ | `Low` Tier | **64,008 balls** (33.00%) | **33,929 balls** (17.49%) | Routine game state; low urgency; standard defensive/offensive baselines. |
| **Moderate Pressure** | $40.0 \le P < 65.0$ | `Moderate` Tier | **104,755 balls** (54.00%) | **145,419 balls** (74.97%) | Standard competitive baseline; intermediate leverage; retained separately. |
| **High Pressure** | $P \ge 65.0$ | `High` $[65, 85) \ \cup$ `Extreme` $[85, 100]$ | **25,213 balls** (13.00%) | **14,628 balls** (7.54%) | Critical leverage; steep chase, death defense, or top-order collapse. |

### Strict Non-Negotiable Rules
1. **Role Independence:** Batters are classified strictly by `batting_pressure_score`. Bowlers are classified strictly by `bowling_pressure_score`. Bowling pressure must never be used to evaluate batter pressure exposure, nor vice versa.
2. **No Merging of Moderate:** The `Moderate` cohort is retained as a distinct reference baseline and must **never** be silently merged into the Normal cohort.
3. **Primary Differential:** The core performance contrast is defined as:
   $$\text{High-Pressure Performance } (P \ge 65) \quad \text{vs.} \quad \text{Normal-Pressure Performance } (P < 40)$$

---

## 3. Batting Analytics Specification (`task_05_batting.py`)

For each unique `striker_id`, the pipeline aggregates metrics across four cohorts:
- `high` ($P_{\text{bat}} \ge 65$)
- `normal` ($P_{\text{bat}} < 40$)
- `moderate` ($40 \le P_{\text{bat}} < 65$)
- `overall` (all clean deliveries)

### 3.1 Raw Batting Metrics & Accounting Rules
1. **Balls Faced (`balls_faced`):** Count of deliveries where `is_batter_ball == True` (excludes wides; includes no-balls).
2. **Runs Scored (`runs_scored`):** Sum of `runs_off_bat` (excludes extras).
3. **Strike Rate (`strike_rate`):**
   $$\text{SR} = \begin{cases} 100.0 \times \frac{\text{runs\_scored}}{\text{balls\_faced}}, & \text{if balls\_faced} > 0 \\ \text{NaN}, & \text{otherwise} \end{cases}$$
4. **Boundary Counts & Rates:**
   - `fours`: Sum of `is_four`.
   - `sixes`: Sum of `is_six`.
   - `boundary_runs`: $4 \times \text{fours} + 6 \times \text{sixes}$.
   - `boundary_run_pct`: $100.0 \times \frac{\text{boundary\_runs}}{\text{runs\_scored}}$ (percentage of runs from boundaries).
   - `boundary_ball_pct`: $100.0 \times \frac{\text{fours} + \text{sixes}}{\text{balls\_faced}}$ (percentage of balls hit for boundary).
5. **Dot Ball Percentage (`dot_pct`):**
   $$\text{Dot\%} = 100.0 \times \frac{\sum \text{is\_dot\_ball}}{\text{balls\_faced}}$$
6. **Striker Dismissals (`dismissals`):** Sum of `is_batter_out` (excludes non-striker run-outs).
7. **Dismissal Rate per 100 Balls (`dismissal_rate_per_100`):**
   $$\text{DismissalRate}_{100} = 100.0 \times \frac{\text{dismissals}}{\text{balls\_faced}}$$
8. **Exposure Volume:**
   - `matches_count`: Distinct count of `match_id`.
   - `innings_count`: Distinct count of `(match_id, innings)`.
   - `opponents_count`: Distinct count of `bowling_team_id`.

### 3.2 Batting Differential Metrics
- **Strike Rate Difference:** $\Delta \text{SR} = \text{SR}_{\text{high}} - \text{SR}_{\text{normal}}$
- **Relative Strike Rate Change:** $\text{Rel } \Delta \text{SR} = \frac{\text{SR}_{\text{high}} - \text{SR}_{\text{normal}}}{\text{SR}_{\text{normal}}}$
- **Dot Ball % Difference:** $\Delta \text{Dot\%} = \text{Dot\%}_{\text{high}} - \text{Dot\%}_{\text{normal}}$ (negative is favorable)
- **Dismissal Rate Difference:** $\Delta \text{DismissalRate} = \text{DismissalRate}_{\text{high}} - \text{DismissalRate}_{\text{normal}}$ (negative is favorable)
- **Boundary % Difference:** $\Delta \text{Boundary\%} = \text{Boundary\%}_{\text{high}} - \text{Boundary\%}_{\text{normal}}$ (positive is favorable)

---

## 4. Bowling Analytics Specification (`task_05_bowling.py`)

For each unique `bowler_id`, the pipeline aggregates metrics across `high`, `normal`, `moderate`, and `overall` cohorts.

### 4.1 Raw Bowling Metrics & Accounting Rules
1. **Legal Balls Bowled (`legal_balls`):** Sum of `is_legal_ball` (excludes wides and no-balls).
2. **Overs Bowled (`overs_bowled`):** $\frac{\text{legal\_balls}}{6.0}$.
3. **Runs Conceded (`runs_conceded`):** Sum of `bowler_runs_conceded` (includes batter runs + wide/no-ball penalties in `extras1_runs`; excludes byes/leg-byes).
4. **Wickets Credited (`wickets`):** Sum of `is_bowler_wicket` (strictly bowled, caught, LBW, stumped, hit wicket; excludes run-outs).
5. **Economy Rate (`economy_rate`):**
   $$\text{Econ} = \begin{cases} 6.0 \times \frac{\text{runs\_conceded}}{\text{legal\_balls}}, & \text{if legal\_balls} > 0 \\ \text{NaN}, & \text{otherwise} \end{cases}$$
6. **Wickets per Over (`wickets_per_over`):**
   $$\text{WktPerOver} = \begin{cases} 6.0 \times \frac{\text{wickets}}{\text{legal\_balls}}, & \text{if legal\_balls} > 0 \\ \text{NaN}, & \text{otherwise} \end{cases}$$
7. **Bowling Strike Rate (`bowling_strike_rate`):**
   $$\text{BowlSR} = \begin{cases} \frac{\text{legal\_balls}}{\text{wickets}}, & \text{if wickets} > 0 \\ \text{NaN}, & \text{otherwise} \end{cases}$$
8. **Dot Ball Percentage (`dot_pct`):**
   $$\text{Dot\%} = 100.0 \times \frac{\sum \text{is\_dot\_ball}}{\text{legal\_balls}}$$
9. **Boundary Conceded Percentage (`boundary_conceded_pct`):**
   $$\text{BoundaryConceded\%} = 100.0 \times \frac{\sum (\text{is\_four} + \text{is\_six})}{\text{legal\_balls}}$$
10. **Discipline Counts:** `wide_count` ($\sum \text{is\_wide}$), `noball_count` ($\sum \text{is\_noball}$).
11. **Exposure Volume:** `matches_count`, `innings_count`, `opponents_count`.

### 4.2 Bowling Differential Metrics
- **Economy Rate Difference:** $\Delta \text{Econ} = \text{Econ}_{\text{high}} - \text{Econ}_{\text{normal}}$ (negative indicates bowling tightens under pressure; favorable).
- **Wicket Rate Difference:** $\Delta \text{WktPerOver} = \text{WktPerOver}_{\text{high}} - \text{WktPerOver}_{\text{normal}}$ (positive is favorable).
- **Dot Ball % Difference:** $\Delta \text{Dot\%} = \text{Dot\%}_{\text{high}} - \text{Dot\%}_{\text{normal}}$ (positive is favorable).
- **Boundary Conceded % Difference:** $\Delta \text{BoundaryConceded\%} = \text{BoundaryConceded\%}_{\text{high}} - \text{BoundaryConceded\%}_{\text{normal}}$ (negative is favorable).

---

## 5. Stratification & Confounding Control

Raw comparison between pressure and normal play can be confounded by match phase and format:
1. **Phase Imbalance:** High-pressure deliveries cluster naturally in the Death phase (overs 16–20), where baseline scoring rates and wicket rates are structurally higher than in the Middle phase.
2. **Format Differences:** IPL features higher run-rate ceilings than Associate-heavy T20I fixtures.
3. **Mitigation Strategy:**
   - Report format-stratified summaries (IPL vs. T20I) alongside pooled metrics.
   - Calculate phase exposure breakdowns for every eligible player (e.g., % of high-pressure balls in Death vs. Powerplay).
   - In Task 05.6/05.7, benchmark player differentials against **role- and format-specific population baselines** rather than naive global means.

---

## 6. Missing Data & Numerical Robustness Policy

1. **Undefined Metrics as `NaN`:** If a denominator is 0 (e.g. 0 balls faced in high pressure, or 0 wickets taken), the resulting rate or differential is explicitly assigned `np.nan` with a documented reason. It is **never** replaced with 0.0, which would distort rankings.
2. **Numerical Bounds:** Percentages must be bounded in $[0.0, 100.0]$.
3. **No Imputation of Factual Data:** Player identities, matches, and delivery counts are strictly factual.

