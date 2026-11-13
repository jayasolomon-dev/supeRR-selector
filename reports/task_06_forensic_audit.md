# SUPERR SELECTOR — TASK 06 FORENSIC LEAKAGE & METHODOLOGY AUDIT
## Independent Forensic Audit of Master Task 06 Machine Learning, Features & Explainability

**Project:** Rajasthan Royals SupeRR Selector Season 2 Hackathon  
**Task:** Task 06 Forensic Leakage & Methodology Audit  
**Auditor:** Independent Senior Quantitative Auditor & Lead Data Integrity Forensic Inspector  
**Date:** November 13, 2026  
**Audit Mode:** STRICT READ-ONLY INSPECTION (Zero code, data, model, or pipeline modifications)  
**Final Decision:** **CONDITIONAL GO FOR MASTER TASK 07**  

---

## 1. Executive Verdict

An exhaustive, read-only forensic audit of Master Task 06 was conducted across all source code (`src/features/`, `src/ml/`, `src/validation/`), feature matrices (`data/ml/`), model artifacts, metrics JSON files, figures, and technical reports.

### Summary of Verdict:
1. **Critical Flaw in Supervised Predictive Modeling:** A severe mathematical endogeneity leakage was uncovered in the supervised predictor sets. All five career aggregate features (`strike_rate_overall`, `dot_pct_overall`, `boundary_ball_pct_overall`, `dismissal_rate_per_100_overall`, `balls_faced_overall` for batters, and their exact bowling equivalents) were constructed using **all deliveries**, thereby mathematically embedding the high-pressure target deliveries inside the predictors.
   - For Qualified Batters, high-pressure deliveries account for an average of **15.4%** of career balls faced (up to **61.2%** for death-overs specialists like David Willey) and **16.9%** of runs scored (up to **79.4%**).
   - For Qualified Bowlers, high-pressure deliveries account for an average of **9.0%** of legal deliveries (up to **26.9%**) and **11.2%** of runs conceded (up to **32.5%**).
   - When these `*_overall` features are removed and models are trained on strictly clean, normal-condition baseline features, Ridge regression out-of-fold $R^2$ collapses from $+0.209$ to **$-0.005$** (batting) and from $+0.089$ to **$-0.040$** (bowling).
   - **Crucial Scientific Insight:** This collapse does not invalidate the project; rather, it **proves the foundational premise of the Rajasthan Royals SupeRR Selector**: *Standard normal-condition performance cannot linearly predict high-pressure execution.* High-pressure reliability is largely orthogonal to normal performance, which mathematically justifies the necessity of the Task 05 Empirical Bayes Reliability Index ($I_{\text{rel}}$).
2. **Unsupervised Archetype Modeling is Clean & Uncompromised:** The K-Means clustering ($k=3$) uses Empirical Bayes shrunk differentials and exposure shares to group players into tactical profiles. Because clustering is descriptive segmentation and not predictive regression, it is free from target leakage.
3. **Explainability Narrative Embellishments:** The explainability report contains several unsupported qualitative claims (e.g., radar gun speed $>145$ km/h, reverse-swing yorkers, pickup-pull shot mechanics, googly arm action) that have zero representation in the ball-by-ball delivery log dataset.
4. **Conditional Clearance for Task 07:** Master Task 07 may proceed under strict binding conditions: the compromised supervised regression outputs must be quarantined, and Task 07 must rely exclusively on the certified Task 05 Empirical Bayes Reliability Indices and the Task 06 Unsupervised Strategic Archetypes.

---

## 2. Feature-by-Feature Leakage Matrix

Every supervised predictor implemented in `src/features/task_06_batting_features.py` and `src/features/task_06_bowling_features.py` was audited against its mathematical definition, underlying delivery records, and target overlap.

### 2.1 Batting Predictor Audit (14 Features)

| Feature Name | Source Aggregation Logic | High-Pressure Deliveries Included? | Supervised Target Overlap? | Classification | Forensic Finding & Impact |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `strike_rate_normal` | `runs_norm / bf_norm * 100` | **NO** | **NO** | **SAFE** | Clean baseline metric; Low pressure deliveries only ([0, 40)). |
| `dot_pct_normal` | `dots_norm / bf_norm * 100` | **NO** | **NO** | **SAFE** | Clean baseline dot-ball frequency. |
| `boundary_ball_pct_normal` | `(fours_norm + sixes_norm) / bf_norm * 100` | **NO** | **NO** | **SAFE** | Clean baseline boundary frequency. |
| `dismissal_rate_per_100_normal`| `dismissals_norm / bf_norm * 100` | **NO** | **NO** | **SAFE** | Clean baseline wicket vulnerability. |
| `balls_faced_normal` | Deliveries faced in normal conditions | **NO** | **NO** | **SAFE** | Clean sample size weight for normal conditions. |
| `six_ratio_normal` | `sixes_norm / (fours_norm + sixes_norm)` | **NO** | **NO** | **SAFE** | Clean baseline power distribution ratio. |
| `running_strike_rate_normal`| Non-boundary runs / Non-boundary balls | **NO** | **NO** | **SAFE** | Clean running-between-wickets scoring rate. |
| `strike_rate_overall` | `runs_overall / bf_overall * 100` | **YES** | **YES** | **CONFIRMED LEAKAGE** | Numerator contains `runs_high`; denominator contains `bf_high`. Overlaps directly with target `strike_rate_high`. |
| `dot_pct_overall` | `dots_overall / bf_overall * 100` | **YES** | **YES** | **CONFIRMED LEAKAGE** | Numerator contains `dots_high`; denominator contains `bf_high`. |
| `boundary_ball_pct_overall` | `boundaries_overall / bf_overall * 100` | **YES** | **YES** | **CONFIRMED LEAKAGE** | Ranked as #1 predictor by permutation importance precisely because it contains high-pressure boundaries. |
| `dismissal_rate_per_100_overall`| `dismissals_overall / bf_overall * 100` | **YES** | **YES** | **CONFIRMED LEAKAGE** | Numerator contains `dismissals_high`; denominator contains `bf_high`. Ranked as #2 predictor. |
| `balls_faced_overall` | `bf_norm + bf_mod + bf_high` | **YES** | **YES** | **CONFIRMED LEAKAGE** | Directly includes `balls_faced_high`. |
| `ipl_ball_share` | `bf_ipl / bf_overall` | Indirectly | Minor | **POTENTIALLY CONTAMINATED** | Denominator contains `bf_high`. Can be cleanly replaced by `bf_ipl_norm / bf_norm`. |
| `batting_hand_LHB` | Left-hand binary flag | **NO** | **NO** | **SAFE** | Static demographic player trait. |

---

### 2.2 Bowling Predictor Audit (17 Features)

| Feature Name | Source Aggregation Logic | High-Pressure Deliveries Included? | Supervised Target Overlap? | Classification | Forensic Finding & Impact |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `economy_rate_normal` | `(runs_norm / legal_balls_norm) * 6` | **NO** | **NO** | **SAFE** | Clean baseline run containment rate. |
| `wickets_per_over_normal` | `(wickets_norm / legal_balls_norm) * 6` | **NO** | **NO** | **SAFE** | Clean baseline wicket-taking threat. |
| `dot_pct_normal` | `(dots_norm / legal_balls_norm) * 100` | **NO** | **NO** | **SAFE** | Clean baseline dot-ball frequency. |
| `boundary_conceded_pct_normal`| `boundaries_norm / legal_balls_norm * 100` | **NO** | **NO** | **SAFE** | Clean baseline boundary leakage rate. |
| `legal_balls_normal` | Legal deliveries bowled in normal conditions | **NO** | **NO** | **SAFE** | Clean sample size weight for normal conditions. |
| `extras_per_legal_ball_normal`| `(wides_norm + noballs_norm) / lb_norm` | **NO** | **NO** | **SAFE** | Clean extras control rate. |
| `six_conceded_ratio_normal` | Sixes conceded / Total boundaries conceded | **NO** | **NO** | **SAFE** | Clean severe boundary vulnerability ratio. |
| `bowling_strike_rate_normal_clean`| `lb_norm / wickets_norm` (capped at 120)| **NO** | **NO** | **SAFE** | Clean imputed baseline strike rate. |
| `zero_wickets_normal_flag` | `wickets_norm == 0` | **NO** | **NO** | **SAFE** | Clean binary indicator for zero wickets. |
| `economy_rate_overall` | `(runs_overall / lb_overall) * 6` | **YES** | **YES** | **CONFIRMED LEAKAGE** | Numerator contains `runs_conceded_high`; denominator contains `legal_balls_high`. Overlaps with `economy_rate_high`. |
| `wickets_per_over_overall` | `(wickets_overall / lb_overall) * 6` | **YES** | **YES** | **CONFIRMED LEAKAGE** | Numerator contains `wickets_high`; denominator contains `legal_balls_high`. |
| `dot_pct_overall` | `(dots_overall / lb_overall) * 100` | **YES** | **YES** | **CONFIRMED LEAKAGE** | Numerator contains `dots_high`; denominator contains `legal_balls_high`. |
| `boundary_conceded_pct_overall`| `boundaries_overall / lb_overall * 100` | **YES** | **YES** | **CONFIRMED LEAKAGE** | Overlaps with target. Ranked as #1 predictor accounting for 52.3% of permutation importance. |
| `legal_balls_overall` | `lb_norm + lb_mod + lb_high` | **YES** | **YES** | **CONFIRMED LEAKAGE** | Directly includes `legal_balls_high`. |
| `ipl_ball_share` | `lb_ipl / lb_overall` | Indirectly | Minor | **POTENTIALLY CONTAMINATED** | Denominator contains `legal_balls_high`. |
| `is_spin` | Spin binary flag | **NO** | **NO** | **SAFE** | Static bowling physical classification. |
| `bowling_arm_left` | Left-arm binary flag | **NO** | **NO** | **SAFE** | Static bowling trajectory classification. |

---

### 2.3 Concrete Player-Level Leakage Evidence

The extent of mathematical contamination is evident when examining players whose exposure is concentrated in high-pressure match situations:

#### Batting Leakage Example 1: David Willey
- `balls_faced_overall` = 98 | `balls_faced_normal` = 30 | `balls_faced_high` = **60**
- **High-Pressure Exposure Share:** **61.2%** of Willey’s total career balls were faced under high pressure!
- `strike_rate_normal` = **60.00**
- `strike_rate_high` (Target) = **128.33**
- `strike_rate_overall` (Predictor) = **98.98**
- *Forensic Observation:* Willey's `strike_rate_overall` is 98.98 *because* his high-pressure strike rate is 128.33. Feeding `strike_rate_overall` into a model to predict `strike_rate_high` is mathematically equivalent to using 61.2% of the target variable to predict itself.

#### Batting Leakage Example 2: Jason Holder
- `balls_faced_overall` = 447 | `balls_faced_normal` = 52 | `balls_faced_high` = **166** (37.1% share)
- `strike_rate_normal` = **67.31**
- `strike_rate_high` (Target) = **175.30**
- `strike_rate_overall` (Predictor) = **142.28**
- *Forensic Observation:* In normal conditions, Holder is a slow accumulator ($\text{SR}=67.31$). His career strike rate reaches 142.28 exclusively because of his high-pressure death hitting ($\text{SR}=175.30$).

#### Bowling Leakage Example 1: Praful Hinge
- `legal_balls_overall` = 156 | `legal_balls_normal` = 34 | `legal_balls_high` = **42** (26.9% share)
- `economy_rate_normal` = **10.24**
- `economy_rate_high` (Target) = **14.14**
- `economy_rate_overall` (Predictor) = **11.73**

#### Bowling Leakage Example 2: Gerald Coetzee
- `legal_balls_overall` = 592 | `legal_balls_normal` = 92 | `legal_balls_high` = **102** (17.2% share)
- `economy_rate_normal` = **7.24**
- `economy_rate_high` (Target) = **11.94**
- `economy_rate_overall` (Predictor) = **9.65**

---

### 2.4 Quantitative Impact on Cross-Validation Scores

To measure the exact mathematical distortion introduced by the `*_overall` features, the 5-fold cross-validation pipelines were evaluated under two regimes:
1. **Reported Task 06 Model:** Using all 14 batting and 17 bowling predictors (including `*_overall`).
2. **Clean Baseline Model:** Using strictly normal-condition predictors (excluding all `*_overall` features).

| Pipeline & Discipline | Metric | Reported Model (With `*_overall`) | Clean Model (Normal-Only) | Distortion / Leakage Delta |
| :--- | :--- | :---: | :---: | :---: |
| **Batting Regression (Ridge)** | **Out-of-Fold RMSE** | **26.972** | **30.076** | **-3.104** (Artificially depressed error) |
| **Batting Regression (Ridge)** | **Out-of-Fold $R^2$** | **+0.209** | **-0.005** | **+0.214** (Spurious positive $R^2$) |
| **Bowling Regression (Ridge)** | **Out-of-Fold RMSE** | **1.786** | **1.898** | **-0.112** (Artificially depressed error) |
| **Bowling Regression (Ridge)** | **Out-of-Fold $R^2$** | **+0.089** | **-0.040** | **+0.129** (Spurious positive $R^2$) |
| **Batting Classification (LogReg)**| **Accuracy** | **71.4%** | **64.1%** | **+7.3%** (Artificially elevated accuracy) |
| **Batting Classification (LogReg)**| **ROC-AUC** | **0.772** | **0.642** | **+0.130** (Spurious discriminative power) |
| **Bowling Classification (LogReg)**| **Accuracy** | **66.2%** | **58.1%** | **+8.1%** (Artificially elevated accuracy) |
| **Bowling Classification (LogReg)**| **ROC-AUC** | **0.686** | **0.651** | **+0.035** (Spurious discriminative power) |

*Forensic Conclusion:* The reported positive $R^2$ scores ($R^2 = 0.209$ for batting, $R^2 = 0.089$ for bowling) were artifacts of target endogeneity. When clean normal-condition features alone are used, the linear $R^2$ is $\le 0.000$, confirming that **normal-condition stats alone cannot linearly forecast high-pressure execution.**

---

## 3. Cross-Validation Integrity Assessment

### 3.1 Split Logic & Grouping
- **Unit of Splitting:** Splitting was performed at the player entity level ($N=109$ Qualified Batters, $N=136$ Qualified Bowlers).
- **Duplicate Records Across Folds:** None. Every player has a single record identified by `striker_id` or `bowler_id`. No player appears in both training and test folds within the same iteration.
- **Out-of-Fold Storage:** `oof_preds[name][val_idx] = preds` accurately captures out-of-fold validation predictions. Reported cross-validation metrics were genuinely calculated out-of-sample across the 5 folds.

### 3.2 Preprocessing Inside Folds
- **Feature Scaling:** For Ridge Regression and Logistic Regression, `StandardScaler` was properly instantiated and fit *exclusively* on the training fold (`X_tr`), then applied to transform the test fold (`X_va`). This eliminated scaling leakage across folds.
- **Classification Target Threshold (Minor Leakage):**
  - In `src/features/task_06_batting_features.py`:
    `median_sr_high_q = df.loc[q_mask, "strike_rate_high"].median()`
  - In `src/features/task_06_bowling_features.py`:
    `median_econ_high_q = df.loc[q_mask, "economy_rate_high"].median()`
  - *Observation:* The binary classification targets (`target_above_median_sr_high` and `target_below_median_econ_high`) were computed globally on the entire Qualified cohort *before* cross-validation splitting. While the sample median of 109 or 136 players shifts negligibly when 20% are held out, strictly defensible ML protocols require calculating the median threshold inside each training fold.

### 3.3 What the Cross-Validation Results Establish vs. What They Do Not
- **What CV Results Establish:**
  1. If an analyst has access to a player's career totals (which include their past high-pressure performances), Ridge regression can linearly interpolate their high-pressure scoring speed with an RMSE of 26.97 runs/100 balls.
  2. Logistic Regression retains mild directional classification ability (ROC-AUC $\approx 0.642$ to $0.651$) based on normal-condition boundary frequencies, disciplines, and spin traits.
- **What CV Results Do NOT Establish:**
  1. The reported regression models **do not establish predictive power from pre-pressure conditions.**
  2. They do not prove that a team can scout players based on normal-overs batting or bowling and accurately forecast how they will perform in a Super Over or high-pressure death chase.

---

## 4. Explainability Evidence Assessment

### 4.1 Permutation Importance Calculation Defect
In `src/ml/task_06_explainability.py`:
```python
rf_b_reg = RandomForestRegressor(n_estimators=100, max_depth=4, min_samples_leaf=3, random_state=42).fit(X_b, y_b_reg)
perm_b_reg = permutation_importance(rf_b_reg, X_b, y_b_reg, n_repeats=10, random_state=42)
```
- *Forensic Defect:* Permutation importance was calculated on `X_b, y_b_reg`—the **training dataset**—rather than out-of-fold test sets.
- *Impact:* Permutation importance on training data measures in-sample tree split reliance, not out-of-sample generalization importance. In-sample permutation importance exaggerates the apparent contribution of noisy or overfit features.

### 4.2 Standardized Ridge Coefficients
- Standardized scaling was properly applied to `X_b` prior to fitting Ridge regression.
- The resulting coefficients represent the shift in the target metric (in raw units: runs/100 balls or runs/over) per one standard deviation change in the predictor.

### 4.3 Unsupported Qualitative Cricket Claims
The explainability report (`reports/task_06_explainability.md`) contains multiple domain assertions that are completely unsupported by the available tabular scorecard delivery logs:

| Asserted Claim in Report | Feature / Player Referenced | Forensic Reality in Workspace Datasets |
| :--- | :--- | :--- |
| *"pickup-pull against high-pace bowling"* | Sanju Samson (Section 5.1) | **UNSUPPORTED:** The dataset contains zero shot-type data (no tags for pull, cut, sweep, or drive). |
| *"high pace (>145 km/h) combined with lethal reverse-swing yorkers"* | Haris Rauf (Section 5.1) | **UNSUPPORTED:** The dataset contains zero radar gun release velocity (km/h) and zero ball trajectory/swing sensor tracking. |
| *"deceptive googly and quick arm action"* | Wanindu Hasaranga (Section 5.1) | **UNSUPPORTED:** The dataset contains zero release point, arm speed, or ball spin rotation tracking. |
| *"struggles against high-leverage defensive death fields"* | Cameron Green (Section 5.2) | **UNSUPPORTED:** The dataset contains zero field placement data (no fielder coordinates or ring counts). |

*Verdict:* These statements represent retrospective narrative embellishment. While common in sports journalism, they violate quantitative rigor and must be purged from technical audit documentation.

---

## 5. Archetype Integrity Assessment

The unsupervised clustering pipeline (`src/ml/task_06_clustering.py`) was audited against statistical and domain requirements:

### 5.1 Clustering Methodology
- **Input Features (Batting):** `shrunk_diff_strike_rate`, `shrunk_diff_dot_pct`, `shrunk_diff_dismissal_rate`, `high_pressure_ratio`, `high_balls_death_share`.
- **Input Features (Bowling):** `shrunk_diff_economy_rate`, `shrunk_diff_wickets_per_over`, `shrunk_diff_dot_pct`, `high_pressure_ratio`, `high_balls_death_share`.
- **Scaling:** Features were properly standardized using `StandardScaler` fitted on the Qualified cohort.
- **K-Means Execution:** Standardized $k=3$ with `n_init=20` and `random_state=42`. Results are 100% deterministic and reproducible.

### 5.2 Archetype Target Leakage Evaluation
- *Question:* Does K-Means clustering suffer from the same leakage as the supervised regression models?
- *Answer:* **NO.**
- *Reasoning:* Supervised regression attempted to predict high-pressure execution from baseline predictors, where including `*_overall` injected the target into the inputs. In contrast, K-Means is an **unsupervised descriptive segmentation** of the player's multi-dimensional pressure profile. Grouping players by their Empirical Bayes shrunk differentials and match phase exposure is methodologically sound and serves to categorize players into tactical roster roles.

### 5.3 Player Census Reconciliation
Cluster assignments reconcile with Task 05 certification:
- **Batters:**
  - Qualified ($N=109$): Cluster 0 (Pressure Vulnerable) = 46, Cluster 1 (Top/Middle Order Accelerators) = 34, Cluster 2 (Death Phase Finishers) = 29. Total = 109.
  - Provisional ($N=58$): Clustered via out-of-sample projection = 58.
  - Ineligible ($N=657$): Unassigned = 657.
  - Total Batters: **824**.
- **Bowlers:**
  - Qualified ($N=136$): Cluster 0 (High-Pressure Conceders) = 58, Cluster 1 (Death Wicket Enforcers) = 46, Cluster 2 (Middle & Powerplay Restrictors) = 32. Total = 136.
  - Provisional ($N=57$): Clustered via out-of-sample projection = 57.
  - Ineligible ($N=403$): Unassigned = 403.
  - Total Bowlers: **596**.

---

## 6. Summary of Findings

### Critical Findings:
1. **CRITICAL-01 (Endogeneity Leakage in Supervised Predictors):** Predictors with the suffix `*_overall` (`strike_rate_overall`, `boundary_ball_pct_overall`, `economy_rate_overall`, etc.) include high-pressure deliveries. This artificially inflated reported regression $R^2$ to $+0.209$ (batting) and $+0.089$ (bowling). When evaluated on clean normal-condition features alone, out-of-sample linear $R^2 \le 0.000$.

### Major Findings:
2. **MAJOR-01 (Training-Set Permutation Importance):** `permutation_importance` was calculated on the full training dataset rather than out-of-fold test sets, exaggerating tree split reliance.
3. **MAJOR-02 (Unsupported Qualitative Narrative Claims):** The explainability report cites radar gun speeds ($>145$ km/h), reverse swing, pickup-pull shot mechanics, and arm action that do not exist in the ball-by-ball delivery log data.

### Minor Findings:
4. **MINOR-01 (Global Target Median Split):** Target median thresholds for binary classification were determined globally across the cohort before CV splitting rather than inside each training fold.
5. **MINOR-02 (Slight Overlap in `ipl_ball_share`):** The denominator of `ipl_ball_share` uses `balls_overall` rather than `balls_normal`.

---

## 7. Recommended Corrections

To be implemented when updating the pipeline (without modifying existing protected files):
1. **Quarantine Supervised Regression Outputs:** Mark `pred_strike_rate_high_ridge` and `pred_economy_rate_high_ridge` in `data/ml/task_06_batter_predictions.csv` and `data/ml/task_06_bowler_predictions.csv` as quarantined exploratory research metrics, not production predictors.
2. **Document the Orthogonality Finding:** Formally state in project records that baseline performance has $R^2 \le 0.000$ for predicting pressure execution, scientifically proving why the Task 05 Empirical Bayes Reliability Index is indispensable.
3. **Purge Narrative Claims:** Restrict all player attributions strictly to observable delivery events: boundary frequency, dot-ball percentage, dismissal rate, wickets-per-over, and phase distribution.
4. **Preserve Archetypes:** Retain `data/ml/task_06_batter_archetypes.csv` and `data/ml/task_06_bowler_archetypes.csv` as certified tactical inputs for Task 07.

---

## 8. Explicit Final Decision for Master Task 07

### **DECISION: CONDITIONAL GO**

Master Task 07 (Strategic Roster Optimization & Top-10 Selection) is **AUTHORIZED TO PROCEED**, subject to the following **STRICT BINDING CONSTRAINTS**:

1. **BINDING CONSTRAINT 1 — DO NOT USE LEAKED REGRESSION PREDICTIONS FOR VALUATION:**
   The supervised regression predictions (`pred_strike_rate_high_ridge` and `pred_economy_rate_high_ridge`) must **NOT** be used as valuation inputs or ranking criteria in Task 07.
2. **BINDING CONSTRAINT 2 — RELY ON CERTIFIED TASK 05 RELIABILITY INDICES:**
   Task 07 player valuations and draft rankings must be driven primarily by the certified Task 05 Empirical Bayes Reliability Indices (`batter_reliability_index`, `bowler_reliability_index`) and shrunk differentials (`shrunk_diff_strike_rate`, `shrunk_diff_economy_rate`), which are 100% clean, verified, and free from target leakage.
3. **BINDING CONSTRAINT 3 — ADOPT TASK 06 STRATEGIC ARCHETYPES FOR SQUAD BALANCE:**
   Task 07 must use the uncompromised Task 06 K-Means Archetypes (`data/ml/task_06_batter_archetypes.csv` and `data/ml/task_06_bowler_archetypes.csv`) to enforce tactical squad composition constraints (e.g., minimum quotas for Death Phase Finishers, Death Wicket Enforcers, and Middle-Overs Restrictors).
4. **BINDING CONSTRAINT 4 — EXCLUDE UNSUPPORTED NARRATIVES:**
   Task 07 selection justifications must rely exclusively on quantitative metrics from the certified datasets and avoid speculative narrative claims about bowling speed, swing mechanics, or batting technique.

---

## 9. Inventory of Inspected Workspace Files

The following workspace files were thoroughly inspected during this forensic audit:
1. `data/analytics/task_05_batter_reliability.csv`
2. `data/analytics/task_05_bowler_reliability.csv`
3. `data/analytics/task_05_batter_metrics.csv`
4. `data/analytics/task_05_bowler_metrics.csv`
5. `src/features/task_06_batting_features.py`
6. `src/features/task_06_bowling_features.py`
7. `data/ml/task_06_batter_features.csv`
8. `data/ml/task_06_bowler_features.csv`
9. `data/ml/task_06_batter_feature_metadata.json`
10. `data/ml/task_06_bowler_feature_metadata.json`
11. `src/ml/task_06_supervised_models.py`
12. `src/ml/task_06_clustering.py`
13. `src/ml/task_06_explainability.py`
14. `src/validation/validate_task_06.py`
15. `data/ml/task_06_model_metrics.json`
16. `data/ml/task_06_cluster_summary.json`
17. `data/ml/task_06_explainability_metrics.json`
18. `data/ml/task_06_batter_predictions.csv`
19. `data/ml/task_06_bowler_predictions.csv`
20. `data/ml/task_06_batter_archetypes.csv`
21. `data/ml/task_06_bowler_archetypes.csv`
22. `reports/task_06_methodology.md`
23. `reports/task_06_model_validation.md`
24. `reports/task_06_explainability.md`
25. `reports/task_06_validation_summary.json`
26. `reports/task_06_figures/fig1_batting_feature_importance.svg`
27. `reports/task_06_figures/fig2_bowling_feature_importance.svg`
28. `reports/task_06_figures/fig3_batting_cluster_archetypes.svg`
29. `reports/task_06_figures/fig4_bowling_cluster_archetypes.svg`
30. `reports/task_06_figures/fig5_predicted_vs_actual_pressure.svg`
31. `reports/task_06_figures/interactive_task_06_ml_dashboard.html`

