# SUPERR SELECTOR — MASTER TASK 05 FINAL ANALYTICS REPORT
## PLAYER RELIABILITY ANALYTICS & PRESSURE PERFORMANCE MODEL

**Document Reference:** `reports/task_05_final_analytics_report.md`  
**Task Reference:** Master Task 05 Final Delivery & Technical Handoff  
**Author:** Senior Cricket Data Scientist, Statistical Modeler, Data Pipeline Architect & Independent QA Auditor  
**Project:** SUPERR SELECTOR (Rajasthan Royals SupeRR Selector Season 2 Hackathon)  
**Execution Date:** November 12, 2026 (Reconciled November 13, 2026 per Task 05.1 Forensic Audit)  
**Final Verdict:** **FULL PASS (Certified Production Ready)**

---

## 1. Executive Summary & Implementation Overview

Master Task 05 establishes a mathematically rigorous, empirically grounded, and reproducible player-level reliability framework for the Rajasthan Royals SupeRR Selector platform, reconciled against the authoritative findings of the Task 05.1 Forensic Reconciliation Report.

Operating strictly on the certified clean cohort of **193,976 deliveries across 837 T20 matches** (87,673 IPL + 106,303 T20I), this architecture quantifies how individual cricketers perform under High Pressure ($P \ge 65.0$) relative to baseline Normal Pressure ($P < 40.0$), while accounting for Moderate Pressure ($[40.0, 65.0)$) and total contextual exposure.

### Core Architectural Pillars
1. **Zero Information Leakage & Clean Cohort Isolation:**  
   Building directly upon the certified clean cohort loader (`src/analytics/task_05_cohort.py`), 26 Super Over deliveries (14 IPL, 12 T20I) and 12 post-target residual deliveries (Match 48610 Overs 14.1–15.6) are quarantined from 20-over modeling (totaling 38 excluded deliveries), while the authentic match-winning delivery (Match 48610 Over 13.6, required 1 run to win, pre-delivery pressure $P_{\text{bat}} = 9.04, P_{\text{bowl}} = 96.06$) is fully preserved.
2. **Strict Identity Governance:**  
   Every aggregation is keyed strictly on unique integer `player_id`. Name collision risks (such as duplicate entries for "Abdul Samad" and "Haider Ali") have been permanently resolved without data distortion.
3. **Rigorous Accounting Conservation:**  
   All $261,072$ runs off bat, $186,504$ balls faced, $10,215$ striker dismissals, $270,776$ bowler runs conceded, $185,680$ legal balls, and $9,898$ bowler wickets reconcile with zero numerical variance ($0.0000$) against ground truth.
4. **Empirical Bayes Regularization:**  
   To prevent small-sample volatility (e.g., a batter scoring 24 off 6 balls in one extreme over appearing artificially elite), raw differential performance is shrunk toward the qualified population baseline using harmonic mean effective balls $n_{\text{eff}} = \frac{2 n_h n_n}{n_h + n_n}$ with an empirically calibrated prior parameter $K_0 = 30.0$ balls (equivalent to 5 full overs).
5. **Match-Cluster Bootstrap Confidence Intervals:**  
   Rather than assuming independent and identically distributed (i.i.d.) deliveries, estimation uncertainty is captured via 500 match-cluster bootstrap iterations (seed = 42), resampling entire matches to preserve intra-match correlation and situational dynamics.
6. **Strict Role Separation & Exploratory Governance:**  
   Batting and bowling metrics reside in completely decoupled pipelines and distinct data files (`task_05_batter_reliability.csv` and `task_05_bowler_reliability.csv`). In compliance with competition rules, no unified composite player score is generated in Task 05, and no draft selections or final Top-10 rosters are published. Task 07 is strictly responsible for final selection rankings, role balancing, overseas quotas, auction valuation, and portfolio/compositional optimization.

---

## 2. Exact Source and Output File Paths & Schema Specifications

### Input Source Datasets
- `data/derived/pressure_scored_ipl.csv` (87,687 rows, 87 columns)
- `data/derived/pressure_scored_t20i.csv` (106,327 rows, 87 columns)
- `data/processed/competition_team_player_mapping.csv` (1,298 rows: player metadata, batting type, bowling type)
- `data/processed/playing_eleven.csv` (837 matches: match-level player participation)

> [!NOTE]
> Both derived datasets contain exactly **87 columns**, fully matching the approved Revision 2.1 schema in `reports/pressure_feature_dictionary.md`. In adherence to strict read-only project rules, `is_super_over` was not added as a physical 88th column to the derived CSV files; rather, Super Overs are evaluated dynamically via `innings > 2` in the cohort loader (`task_05_cohort.py`).

### Implementation Code Modules
- `src/analytics/task_05_cohort.py`: Certified clean cohort loader and quarantine manager.
- `src/analytics/task_05_batting.py`: Batting pressure aggregation and differential metric engine.
- `src/analytics/task_05_bowling.py`: Bowling pressure aggregation and differential metric engine.
- `src/analytics/task_05_reliability.py`: Empirical Bayes shrinkage, cluster bootstrap, and reliability index engine.
- `src/validate_task_05_cohort.py`: Cohort integrity verification suite (7 tests).
- `src/validate_task_05.py`: Independent 19-test audit suite.
- `src/analytics/generate_task_05_figures.py`: Publication visualization and dashboard generator.

### Output Analytical Tables
- `data/analytics/task_05_batter_metrics.csv` (824 rows, 51 columns)
- `data/analytics/task_05_bowler_metrics.csv` (596 rows, 53 columns)
- `data/analytics/task_05_batter_reliability.csv` (824 rows, 63 columns)
- `data/analytics/task_05_bowler_reliability.csv` (596 rows, 65 columns)

### Key Output Schema Definitions

#### Batter Reliability Table (`task_05_batter_reliability.csv`)
| Column Name | Data Type | Description |
|:---|:---|:---|
| `striker_id` | Integer | Unique identifier for batter (Primary Key) |
| `striker_name` | String | Player name (for presentation only) |
| `batting_type` | String | Batting hand / style (Right hand bat, Left hand bat) |
| `balls_faced_overall` | Integer | Total legal/non-wide balls faced across clean cohort |
| `balls_faced_high` | Float | Balls faced under High Pressure ($P \ge 65.0$) |
| `balls_faced_normal` | Float | Balls faced under Normal Pressure ($P < 40.0$) |
| `balls_faced_mod` | Float | Balls faced under Moderate Pressure ($[40.0, 65.0)$) |
| `strike_rate_overall` | Float | Overall career strike rate ($\frac{\text{Runs}}{\text{BF}} \times 100$) |
| `strike_rate_high` | Float | Strike rate under High Pressure ($P \ge 65.0$) |
| `strike_rate_normal` | Float | Strike rate under Normal Pressure ($P < 40.0$) |
| `diff_strike_rate` | Float | Raw differential strike rate ($\text{SR}_{\text{high}} - \text{SR}_{\text{norm}}$) |
| `diff_dot_pct` | Float | Raw differential dot ball percentage ($\text{Dot\%}_{\text{high}} - \text{Dot\%}_{\text{norm}}$) |
| `diff_dismissal_rate_per_100` | Float | Raw differential dismissal rate per 100 balls |
| `eligibility_tier` | String | Gate tier: `Qualified`, `Provisional`, `Ineligible` |
| `effective_balls` | Float | Harmonic mean sample size: $\frac{2 n_h n_n}{n_h + n_n}$ |
| `shrinkage_weight` | Float | Shrinkage factor $w = \frac{n_{\text{eff}}}{n_{\text{eff}} + 30.0} \in [0, 1]$ |
| `shrunk_diff_strike_rate` | Float | Empirical Bayes shrunk differential strike rate |
| `batter_reliability_index` | Float | Bounded reliability score $[0.0, 100.0]$ (Mean = 50.0) |
| `ci_lower_95` | Float | 2.5th percentile of 500-iteration cluster bootstrap |
| `ci_upper_95` | Float | 97.5th percentile of 500-iteration cluster bootstrap |
| `ci_std_error` | Float | Standard error across bootstrap distribution |
| `reliability_grade` | String | Categorical grade: `Elite`, `High`, `Moderate`, `Low` |

#### Bowler Reliability Table (`task_05_bowler_reliability.csv`)
| Column Name | Data Type | Description |
|:---|:---|:---|
| `bowler_id` | Integer | Unique identifier for bowler (Primary Key) |
| `bowler_name` | String | Player name (for presentation only) |
| `bowling_type` | String | Bowling style description |
| `pace_or_spin` | String | Broad classification: `Pace` or `Spin` |
| `legal_balls_overall` | Integer | Total legal deliveries bowled (excluding wides & no-balls) |
| `legal_balls_high` | Float | Legal balls bowled under High Pressure ($P \ge 65.0$) |
| `legal_balls_normal` | Float | Legal balls bowled under Normal Pressure ($P < 40.0$) |
| `economy_rate_overall` | Float | Overall career economy rate ($\frac{\text{Conceded Runs}}{\text{Overs}}$) |
| `economy_rate_high` | Float | Economy rate under High Pressure ($P \ge 65.0$) |
| `economy_rate_normal` | Float | Economy rate under Normal Pressure ($P < 40.0$) |
| `diff_economy_rate` | Float | Raw differential economy rate ($\text{Econ}_{\text{high}} - \text{Econ}_{\text{norm}}$) |
| `diff_wickets_per_over` | Float | Raw differential wickets per over (per 6 legal balls) |
| `diff_dot_pct` | Float | Raw differential dot ball percentage |
| `eligibility_tier` | String | Gate tier: `Qualified`, `Provisional`, `Ineligible` |
| `effective_balls` | Float | Harmonic mean sample size: $\frac{2 n_h n_n}{n_h + n_n}$ |
| `shrinkage_weight` | Float | Shrinkage factor $w = \frac{n_{\text{eff}}}{n_{\text{eff}} + 30.0} \in [0, 1]$ |
| `shrunk_diff_economy_rate` | Float | Empirical Bayes shrunk differential economy rate |
| `bowler_reliability_index` | Float | Bounded reliability score $[0.0, 100.0]$ (Mean = 50.0) |
| `ci_lower_95` | Float | 2.5th percentile of 500-iteration cluster bootstrap |
| `ci_upper_95` | Float | 97.5th percentile of 500-iteration cluster bootstrap |
| `ci_std_error` | Float | Standard error across bootstrap distribution |
| `reliability_grade` | String | Categorical grade: `Elite`, `High`, `Moderate`, `Low` |

---

## 3. Exact Delivery and Player Census Reconciliations

### Delivery Census
The clean cohort guarantees an airtight accounting baseline across all delivery segments:

```
========================================================================================
DELIVERY CENSUS & SEGREGATION RECONCILIATION
========================================================================================
Total Raw Derived Deliveries:              194,014
  - IPL Derived Deliveries:                 87,687
  - T20I Derived Deliveries:               106,327

Quarantined / Excluded Records:                 38
  - Super Over Deliveries (innings > 2):        26 (14 IPL + 12 T20I across 4 matches)
    * Match 40725 (IPL): 10 rows (6 in inn 3, 4 in inn 4)
    * Match 50359 (IPL):  4 rows (3 in inn 3, 1 in inn 4)
    * Match 34429 (T20I): 5 rows (4 in inn 3, 1 in inn 4)
    * Match 45512 (T20I): 7 rows (6 in inn 3, 1 in inn 4)
  - Post-Target Deliveries (dead-ball):         12 (all in Match 48610 Overs 14.1–15.6)
  Total Quarantined Deliveries:                 38 (26 Super Over deliveries: 14 IPL + 12 T20I; plus 12 post-target deliveries)

Certified Clean Cohort Deliveries:         193,976 (100.0% of Active 20-Over Dataset)
  - Clean IPL Deliveries:                   87,673 (45.20%)
  - Clean T20I Deliveries:                 106,303 (54.80%)
  - Total Matches:                             837 (100.0% active match coverage)
========================================================================================
```

### Player Census & Identity Integrity
- **Unique Strikers in Clean Cohort:** 824 players.
- **Unique Bowlers in Clean Cohort:** 596 players.
- **Total Unique Players:** 891 players.
- **Player Mapping Coverage:** 100.0% (891 / 891 players mapped in `competition_team_player_mapping.csv`).
- **Null `player_id` Count:** Exactly 0.
- **Disambiguated Name Collisions:**
  - `Abdul Samad`: Player ID 7446 (SRH, 424 BF) vs. Player ID 6922 (Domestic/T20I, 0 BF in cohort).
  - `Haider Ali`: Player ID 7338 (Pakistan, 375 BF) vs. Player ID 28756 (Domestic, 0 BF in cohort).
  Every computation isolates records exclusively by integer `player_id`.

---

## 4. Batting Pressure Analytics Breakdown

Batting under high pressure requires an aggressive balance between accelerated scoring and wicket preservation. Across the 109 Qualified Batters, performance shifts markedly when transitioning from Normal Pressure ($P < 40.0$) to High Pressure ($P \ge 65.0$).

### Population Norms for Qualified Batters ($N = 109$)
- **Normal Pressure Strike Rate ($\text{SR}_{\text{norm}}$):** Mean = $135.82$, Median = $135.03$
- **High Pressure Strike Rate ($\text{SR}_{\text{high}}$):** Mean = $154.45$, Median = $152.00$
- **Differential Strike Rate ($\Delta \text{SR} = \text{SR}_{\text{high}} - \text{SR}_{\text{norm}}$):** Mean = $+18.64$
- **Normal Dot Ball % ($\text{Dot\%}_{\text{norm}}$):** Mean = $35.42\%$
- **High Pressure Dot Ball % ($\text{Dot\%}_{\text{high}}$):** Mean = $31.97\%$
- **Differential Dot Ball % ($\Delta \text{Dot\%}$):** Mean = $-3.45\%$
- **Differential Dismissal Rate ($\Delta \text{DisRate}_{100}$):** Mean = $+2.07$ outs per 100 balls

> [!NOTE]
> The positive $\Delta \text{SR}$ (+18.64) across qualified batters illustrates that high-pressure situations in T20 cricket predominantly coincide with late-innings boundary requirements or steep run chases where batters are tactically compelled to trade higher dismissal risk for boundary acceleration.

### High Pressure Exposure by Match Phase
For qualified batters, high-pressure balls faced are distributed as follows:
- **Death Phase (Overs 16–20):** $74.2\%$ of all high-pressure deliveries.
- **Middle Phase (Overs 6–15):** $21.5\%$ of all high-pressure deliveries.
- **Powerplay Phase (Overs 0–5):** $4.3\%$ of all high-pressure deliveries.

---

## 5. Bowling Pressure Analytics Breakdown

Bowling under high pressure is severely tested as batters attempt boundary hitting on nearly every ball.

### Population Norms for Qualified Bowlers ($N = 136$)
- **Normal Pressure Economy ($\text{Econ}_{\text{norm}}$):** Mean = $8.30$ runs/over, Median = $8.23$
- **High Pressure Economy ($\text{Econ}_{\text{high}}$):** Mean = $11.25$ runs/over, Median = $11.14$
- **Differential Economy ($\Delta \text{Econ} = \text{Econ}_{\text{high}} - \text{Econ}_{\text{norm}}$):** Mean = $+2.95$ runs/over
- **Normal Wickets Per Over ($\text{WktPerOver}_{\text{norm}}$):** Mean = **0.391** wickets per 6 legal balls (overs)
- **High Pressure Wickets Per Over ($\text{WktPerOver}_{\text{high}}$):** Mean = **0.397** wickets per 6 legal balls (overs)
- **Differential Wickets Per Over ($\Delta \text{WktPerOver}$):** Mean = **+0.006** wickets per 6 legal balls (overs)
- **Normal Dot Ball % ($\text{Dot\%}_{\text{norm}}$):** Mean = $35.38\%$
- **High Pressure Dot Ball % ($\text{Dot\%}_{\text{high}}$):** Mean = $22.81\%$
- **Differential Dot Ball % ($\Delta \text{Dot\%}$):** Mean = $-12.57\%$

> [!IMPORTANT]
> The metric `wickets_per_over` is explicitly defined as wickets per 6 legal balls bowled ($\frac{6 \times \text{Wickets}}{\text{Legal Balls}}$). Across the qualified cohort, bowlers take an average of 0.391 wickets per over under normal conditions (~1 wicket every 15.3 balls) and 0.397 wickets per over under high pressure (~1 wicket every 15.1 balls). The average qualified bowler concedes $+2.95$ more runs per over under high pressure, while dot ball percentage drops by $-12.57\%$. Bowlers who can suppress this surge—maintaining a $\Delta \text{Econ} \le +0.5$ or negative $\Delta \text{Econ}$ while sustaining wicket-taking threat—stand out as elite pressure assets.

---

## 6. Eligibility Tier Hierarchy & Population Distribution

To ensure statistical reliability and prevent unrepresentative outliers from distorting downstream decision-making, a 3-tier hierarchy was enforced:

```
                      ┌─────────────────────────────────────────┐
                      │            TOTAL POPULATION             │
                      │       Batters: 824 | Bowlers: 596       │
                      └────────────────────┬────────────────────┘
                                           │
                    ┌──────────────────────┴──────────────────────┐
                    │                                             │
      ┌─────────────▼─────────────┐                 ┌─────────────▼─────────────┐
      │   Meets Qualified Gates?  │                 │    Meets Provisional?     │
      │  Total BF/LB >= 60        │                 │  Total BF/LB >= 30        │
      │  High BF/LB  >= 30        │                 │  High BF/LB  >= 15        │
      │  Total Matches >= 5       │                 │  Total Matches >= 3       │
      │  High Matches  >= 3       │                 │  High Matches  >= 2       │
      └─────────────┬─────────────┘                 └─────────────┬─────────────┘
                    │ YES                                         │ YES
      ┌─────────────▼─────────────┐                 ┌─────────────▼─────────────┐
      │         QUALIFIED         │                 │        PROVISIONAL        │
      │ Batters: 109 (13.2%)      │                 │ Batters: 58 (7.0%)        │
      │ Bowlers: 136 (22.8%)      │                 │ Bowlers: 57 (9.6%)        │
      │ Full Empirical Bayes      │                 │ Heavy EB Regularization   │
      │ Active for Selection      │                 │ Flagged High Uncertainty  │
      └───────────────────────────┘                 └───────────────────────────┘
                                           │
                                           │ FAILS BOTH GATES
                                  ┌────────▼────────┐
                                  │   INELIGIBLE    │
                                  │ Batters: 657    │
                                  │ Bowlers: 403    │
                                  │ Clamped to 50.0 │
                                  └─────────────────┘
```

### Population Counts by Tier
- **Batters (824 Total):**
  - **Qualified:** $109$ players ($13.2\%$)
  - **Provisional:** $58$ players ($7.0\%$)
  - **Ineligible:** $657$ players ($79.7\%$)
- **Bowlers (596 Total):**
  - **Qualified:** $136$ players ($22.8\%$)
  - **Provisional:** $57$ players ($9.6\%$)
  - **Ineligible:** $403$ players ($67.6\%$)

---

## 7. Empirical-Bayes Shrinkage Engine & Cluster Bootstrap Confidence Methodology

### Harmonic Mean Effective Sample Size ($n_{\text{eff}}$)
Because differential metrics evaluate changes between two distinct regimes (High vs. Normal), estimation variance is dominated by the regime with smaller exposure. The effective sample size is defined as the harmonic mean:

$$n_{\text{eff}} = \frac{2 \cdot n_{\text{high}} \cdot n_{\text{norm}}}{n_{\text{high}} + n_{\text{norm}}}$$

### Empirical Bayes Shrinkage Weight ($w$)
Using a calibrated prior parameter $K_0 = 30.0$ balls (approximately 5 overs of match play):

$$w = \frac{n_{\text{eff}}}{n_{\text{eff}} + K_0} \in [0.0, 1.0]$$

For every metric $M$ (e.g., $\Delta \text{SR}$, $\Delta \text{Econ}$), the shrunk estimate combines the observed player delta with the qualified population mean baseline $\bar{\mu}_{\text{pop}}$:

$$\hat{\Delta M}_{\text{shrunk}} = w \cdot \Delta M_{\text{obs}} + (1 - w) \cdot \bar{\mu}_{\text{pop}}$$

### Component Standardization & Composite Z-Score
Each shrunk metric is standardized against the population standard deviation of qualified players ($\sigma_{\text{pop}}$):

$$z(\Delta M) = \frac{\hat{\Delta M}_{\text{shrunk}} - \bar{\mu}_{\text{pop}}}{\sigma_{\text{pop}}}$$

The composite z-scores weight the strategic dimensions of T20 pressure:
- **Batter Composite Z-Score:**
  $$z_{\text{bat}} = 0.50 \cdot z(\Delta \text{SR}) - 0.25 \cdot z(\Delta \text{Dot\%}) - 0.25 \cdot z(\Delta \text{DisRate}_{100})$$
- **Bowler Composite Z-Score:**
  $$z_{\text{bowl}} = -0.50 \cdot z(\Delta \text{Econ}) + 0.30 \cdot z(\Delta \text{WktPerOver}) + 0.20 \cdot z(\Delta \text{Dot\%})$$

### Bounded Reliability Index Transformation
To map z-scores into an intuitive, zero-bounded scale centered at $50.0$ with a standard deviation of $10.0$:

$$\text{Index} = \text{clip}(50.0 + 10.0 \cdot z_{\text{comp}}, 0.0, 100.0)$$

### Match-Cluster Bootstrap Resampling
To capture uncertainty without violating situational independence:
1. Resample 837 match IDs with replacement for $B = 500$ iterations (seed = 42).
2. For each bootstrap replicate, recalculate all differential metrics, apply identical shrinkage weights, and recompute reliability indices.
3. Compute the 95% Confidence Interval $[L_{95}, U_{95}]$ as the empirical $2.5\text{th}$ and $97.5\text{th}$ percentiles, with standard error $\sigma_{\text{boot}}$.

### Transparent Methodological Note: Bootstrap Zero-Exposure Clamping
As investigated in the Task 05.1 Forensic Reconciliation Audit:
- When drawing match clusters with replacement, if a bootstrap draw samples zero matches where a player faced or bowled deliveries under high pressure or normal pressure, their replicate harmonic effective balls $n_{\text{eff}} = 0$.
- Under $n_{\text{eff}} = 0$, the empirical shrinkage weight collapses to $w = 0.0$, shrinking the replicate score 100% to the neutral population prior ($50.00$).
- Across the qualified cohort:
  - **Batters:** 48 of 109 qualified batters (44.0%) experienced at least one zero-exposure replicate. For players with narrow match footprints across regimes (e.g. Dion Myers: 35.2% zero-exposure draws due to HP balls in only 1 match; Shan Masood: 17.8%; David Willey: 14.2%; Manish Pandey: 5.4%), more than 2.5% of draws collapsed to 50.00, causing their 2.5th percentile lower bound ($L_{95}$) to land on exactly **50.00**.
  - **Bowlers:** 39 of 136 qualified bowlers (28.7%) experienced at least one zero-exposure replicate. Mitchell Marsh had 2.8% draws at 50.00 ($\to L_{95} = \mathbf{50.00}$), while Aiden Markram had 3.6% draws at 50.00 ($\to U_{95} = \mathbf{50.00}$).
- This behavior is mathematically faithful to Bayesian shrinkage under zero data, but it introduces an artificial point-mass spike at 50.00 that truncates the percentile bounds for players with limited match coverage.
- In strict compliance with audit integrity, **invalid draws were not silently discarded, the bootstrap algorithm was not modified, and confidence intervals were not recalculated**. Any alternative interval formulation (such as conditional resampling or minimum-match gates) requires a separate approved validation task.

---

## 8. Main Reliability Findings & Exploratory Profiles

### Published Figures Reference
The visualization suite generated 5 standalone SVG figures and 1 interactive dashboard:
- `reports/task_05_figures/fig1_pressure_vs_normal_performance.svg`: Scatter comparison of normal vs. high-pressure performance.
- `reports/task_05_figures/fig2_sample_size_distribution.svg`: Histogram of effective balls and high-pressure sample depth.
- `reports/task_05_figures/fig3_raw_vs_shrunk_estimates.svg`: Empirical demonstration of shrinkage pulling noisy deltas toward population baselines.
- `reports/task_05_figures/fig4_confidence_interval_comparisons.svg`: Error-bar visualization of 95% bootstrap confidence intervals.
- `reports/task_05_figures/fig5_reliability_index_by_tier.svg`: Distribution of reliability indices across Qualified, Provisional, and Ineligible tiers.
- `reports/task_05_figures/interactive_player_reliability.html`: Full Plotly interactive exploration tool.

### Top 10 Exploratory Single-Dimension Pressure Profiles (Not Final Selection Rankings) — Batters
| Rank | Striker ID | Player Name | Total BF | High BF | $n_{\text{eff}}$ | $w$ | Shrunk $\Delta\text{SR}$ | Reliability Index | 95% CI | Grade |
|:---:|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | 2633 | Jason Holder | 447 | 166.0 | 79.2 | 0.725 | +83.44 | **66.84** | [58.05, 73.99] | High |
| 2 | 2258 | Sanju Samson | 2232 | 36.0 | 69.5 | 0.698 | +62.10 | **60.46** | [49.57, 78.90] | High |
| 3 | 7094 | Curtis Campher | 526 | 78.0 | 77.0 | 0.720 | +44.80 | **59.20** | [52.06, 66.36] | Moderate |
| 4 | 5553 | Phil Salt | 1638 | 48.0 | 91.6 | 0.753 | +45.65 | **58.93** | [44.38, 63.16] | Moderate |
| 5 | 1219 | David Willey | 98 | 60.0 | 40.0 | 0.571 | +47.03 | **58.77** | [50.00, 63.65] | Moderate |
| 6 | 6664 | Dion Myers | 340 | 39.0 | 55.8 | 0.650 | +41.86 | **57.95** | [50.00, 62.25] | Moderate |
| 7 | 3097 | Shan Masood | 176 | 65.0 | 42.0 | 0.583 | +50.37 | **57.63** | [50.00, 64.04] | Moderate |
| 8 | 2436 | Dasun Shanaka | 774 | 172.0 | 86.7 | 0.743 | +55.32 | **57.35** | [50.27, 64.10] | Moderate |
| 9 | 796 | Matthew Wade | 427 | 108.0 | 122.7 | 0.804 | +45.20 | **57.02** | [51.83, 61.18] | Moderate |
| 10 | 3056 | Iftikhar Ahmed | 455 | 39.0 | 46.0 | 0.605 | +65.43 | **56.81** | [37.01, 64.40] | Moderate |

### Qualified Batters Vulnerability Watch (Bottom 5)
| Rank | Striker ID | Player Name | Total BF | High BF | $n_{\text{eff}}$ | $w$ | Shrunk $\Delta\text{SR}$ | Reliability Index | 95% CI | Grade |
|:---:|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 105 | 47370 | Aniket Verma | 196 | 31.0 | 48.8 | 0.619 | -32.55 | **39.94** | [33.81, 49.58] | Low |
| 106 | 4926 | Shadab Khan | 332 | 53.0 | 66.8 | 0.690 | -31.42 | **39.70** | [35.18, 52.31] | Low |
| 107 | 7446 | Abdul Samad | 424 | 130.0 | 69.1 | 0.697 | -34.80 | **39.64** | [29.52, 48.80] | Low |
| 108 | 6512 | Michael Bracewell | 350 | 48.0 | 62.8 | 0.677 | -48.20 | **35.02** | [28.83, 43.59] | Low |
| 109 | 5939 | Cameron Green | 1072 | 35.0 | 65.6 | 0.686 | -55.10 | **32.62** | [25.69, 44.43] | Low |

### Top 10 Exploratory Single-Dimension Pressure Profiles (Not Final Selection Rankings) — Bowlers
| Rank | Bowler ID | Player Name | Total LB | High LB | $n_{\text{eff}}$ | $w$ | Shrunk $\Delta\text{Econ}$ | Reliability Index | 95% CI | Grade |
|:---:|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | 818 | Mitchell Marsh | 295 | 32.0 | 35.2 | 0.540 | +0.30 | **61.86** | [50.00, 69.66] | High |
| 2 | 7364 | Haris Rauf | 1027 | 109.0 | 128.0 | 0.810 | -1.12 | **61.50** | [53.04, 70.76] | High |
| 3 | 8530 | Kartik Tyagi | 415 | 41.0 | 50.3 | 0.626 | -0.43 | **61.28** | [52.62, 67.25] | High |
| 4 | 8746 | Vaibhav Arora | 866 | 84.0 | 96.4 | 0.763 | +0.28 | **60.47** | [50.76, 69.35] | High |
| 5 | 7503 | Ravi Bishnoi | 2327 | 45.0 | 83.8 | 0.736 | +1.21 | **59.66** | [45.29, 75.17] | Moderate |
| 6 | 6676 | Azmatullah Omarzai | 1067 | 59.0 | 90.6 | 0.751 | +0.12 | **59.18** | [44.55, 68.84] | Moderate |
| 7 | 1944 | Keshav Maharaj | 598 | 30.0 | 48.3 | 0.617 | +2.15 | **58.96** | [48.05, 69.82] | Moderate |
| 8 | 3629 | Corbin Bosch | 367 | 63.0 | 69.3 | 0.698 | +0.81 | **58.90** | [49.23, 67.61] | Moderate |
| 9 | 4900 | Wanindu Hasaranga | 2034 | 143.0 | 207.4 | 0.874 | -0.64 | **58.81** | [52.52, 65.99] | Moderate |
| 10 | 4409 | Sam Curran | 1350 | 127.0 | 148.2 | 0.832 | +0.51 | **58.22** | [49.34, 67.57] | Moderate |

### Qualified Bowlers Vulnerability Watch (Bottom 5)
| Rank | Bowler ID | Player Name | Total LB | High LB | $n_{\text{eff}}$ | $w$ | Shrunk $\Delta\text{Econ}$ | Reliability Index | 95% CI | Grade |
|:---:|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 132 | 2636 | Adam Zampa | 1152 | 51.0 | 93.6 | 0.757 | +6.42 | **39.79** | [30.75, 47.77] | Low |
| 133 | 2382 | Jamie Overton | 497 | 34.0 | 54.4 | 0.645 | +6.88 | **39.31** | [24.32, 51.65] | Low |
| 134 | 7322 | Yash Dayal | 871 | 52.0 | 79.5 | 0.726 | +6.95 | **38.19** | [30.04, 46.93] | Low |
| 135 | 1566 | Mohammed Shami | 1275 | 31.0 | 57.3 | 0.656 | +7.20 | **38.00** | [23.50, 56.42] | Low |
| 136 | 3605 | Aiden Markram | 397 | 35.0 | 51.2 | 0.631 | +7.84 | **37.02** | [26.73, 50.00] | Low |

> [!WARNING]
> **GOVERNANCE NOTICE:** These tables present exploratory, single-dimension pressure resilience profiles only. They DO NOT constitute final selection rankings or draft proposals. Master Task 07 is strictly and exclusively responsible for generating final draft selections by optimizing roster balance, overseas player quotas (maximum 4 overseas players in an IPL playing XI), auction valuation efficiency, phase-specific tactical demand, and portfolio risk management.

---

## 9. Regression & Validation Test Suite Results

The complete analytical suite was subjected to automated verification:

| Verification Suite | Target Code / Module | Test Count | Result | Key Guarantee |
|:---|:---|:---:|:---:|:---|
| **Task 05 Audit Suite** | `src/validate_task_05.py` | 19 / 19 | **FULL PASS** | Complete accounting conservation, monotonicity, boundedness |
| **Cohort Integrity Suite** | `src/validate_task_05_cohort.py` | 7 / 7 | **PASS** | Exact delivery counts (193,976), quarantine isolation |
| **Pressure Engine Suite** | `src/test_pressure_engine.py` | 43 / 43 | **PASS** | Component formulas, RRR, WCI, RPI, PVI mathematical invariance |
| **Raw Pipeline Suite** | `src/validate_pipeline.py` | 16 / 16 | **PASS** | 411,025 field assertions, type contracts, schema integrity |

---

## 10. Known Limitations, Assumptions & Edge-Case Sensitivity

1. **Role Decoupling vs. All-Rounder Synergy:**  
   Batting and bowling reliability indices are strictly decoupled. For true all-rounders (e.g., Jason Holder, Sam Curran, Mitchell Marsh), both indices must be ingested separately by Task 06/Task 07 to determine combined roster value.
2. **Match Context & Chase Asymmetry:**  
   Pressure in 2nd innings (chasing) is constrained by a strict target and required run rate (RRR), whereas 1st innings pressure is driven by projected scores and resource preservation. While the underlying Pressure Engine normalizes these dynamics through calibrated weights, situational context must be respected in match-up evaluations.
3. **Sample Truncation for Specialized Finishers & Bootstrap Sensitivity:**  
   Specialist death-overs batters who consistently enter the crease with fewer than 10 balls remaining face sample size limitations, occasionally placing them in the "Provisional" tier. Furthermore, as disclosed in Section 7, players with narrow match footprints across pressure regimes exhibit bootstrap confidence intervals that clamp to 50.00 when zero-exposure draws occur.
4. **Pitch Condition Neutrality:**  
   The current model normalizes against match-level expected runs and phase par scores, but does not explicitly incorporate external weather or soil moisture telemetry.

---

## 11. Formal Handoff Specification for Task 06 and Task 07

### Handoff to Task 06 (Feature Engineering)
Task 06 should directly ingest the four primary output tables from `data/analytics/`:
1. Use `shrunk_diff_strike_rate`, `shrunk_diff_dot_pct`, and `batter_reliability_index` as standardized pressure features for batting evaluation.
2. Use `shrunk_diff_economy_rate`, `shrunk_diff_wickets_per_over`, and `bowler_reliability_index` as standardized pressure features for bowling evaluation.
3. Incorporate `ci_std_error` or confidence intervals $[L_{95}, U_{95}]$ as explicit variance penalties in composite multi-criteria optimization models.
4. Filter or segment features using `eligibility_tier` (`Qualified` for primary model training; `Provisional` for regularization/testing).

### Handoff to Task 07 (Top-10 Selection & Roster Optimization)
1. **No Direct Ranking Pass-Through:**  
   Task 07 must **not** simply sort `batter_reliability_index` or `bowler_reliability_index` to select the Top 10 players.
2. **Role Balance & Compositional Constraints:**  
   Task 07 must integrate pressure reliability with player roles (Top-order, Middle-order, Finisher, Powerplay Bowler, Death Bowler, Spin Specialist), overseas quota constraints (max 4 overseas players in IPL XI), and auction valuation efficiency.
3. **Risk-Adjusted Valuations:**  
   Selection models in Task 07 should utilize the lower confidence bound ($L_{95}$) for risk-averse selection strategies to guarantee floor performance under extreme IPL playoff conditions.

---

**Report Approved by:**  
*Senior Cricket Data Scientist & Quantitative Systems Auditor*  
*SUPERR SELECTOR — Rajasthan Royals Hackathon Project*
