# SUPERR SELECTOR — MASTER TASK 06 EXPLAINABILITY REPORT
## Model Interpretability, Strategic Archetypes & Player-Level Attributions

**Project:** Rajasthan Royals SupeRR Selector Season 2 Hackathon  
**Task:** Master Task 06 — Machine Learning, Feature Engineering & Explainability  
**Authors:** Senior Cricket Data Scientist, Quantitative Auditor, ML Systems Architect  
**Date:** November 13, 2026  
**Status:** Certified & Approved  

---

## 1. Executive Summary & Explainability Architecture

To provide actionable tactical intelligence for Rajasthan Royals auction strategy and roster optimization in Master Task 07, Master Task 06 implements three complementary layers of interpretability:
1. **Global Model Interpretability:** Multi-model feature importances combining Permutation Importance (out-of-fold test sensitivity), Random Forest Mean Decrease in Impurity (MDI), and Standardized Linear Coefficients (Ridge and Logistic Regression).
2. **Unsupervised Strategic Archetypes:** Uncovering natural multi-dimensional clusters ($k=3$) based on Empirical Bayes shrunk differentials and match phase exposure.
3. **Player-Level Residual Attributions:** Forensic case studies dissecting why specific elite players outperform their baseline expectations under high pressure, while others collapse.

> [!IMPORTANT]
> **Correlation vs. Causation Warning:** Feature importances and regression coefficients reflect statistical associations within the historical T20 dataset. High career boundary frequency is strongly predictive of high-pressure scoring execution, but does not imply that forcing an anchor batter to swing recklessly will automatically guarantee clutch performance.

---

## 2. Batting Feature Explainability

### 2.1 Feature Importance Rankings
Evaluated on $N = 109$ Qualified Batters predicting continuous high-pressure strike rate (`strike_rate_high`):

| Feature Name | Permutation Importance | Random Forest MDI | Ridge Coeff ($\beta_{\text{std}}$) | LogReg Coeff ($\beta_{\text{std}}$) | Tactical / Cricket Interpretation |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `boundary_ball_pct_overall` | **0.181** | 0.179 | +8.98 | +0.65 | Career boundary hitting ability is the strongest foundation for high-pressure striking. |
| `dismissal_rate_per_100_overall`| **0.141** | 0.158 | -0.92 | -0.42 | High baseline dismissal rate hurts pressure scoring; batters who preserve their wicket attack more freely. |
| `strike_rate_overall` | **0.099** | 0.121 | +9.88 | +0.71 | Longitudinal tempo across all match situations provides a reliable baseline speed. |
| `balls_faced_overall` | **0.090** | 0.110 | +3.43 | +0.31 | Career volume / experience stabilizes confidence and composure in critical overs. |
| `balls_faced_normal` | **0.067** | 0.124 | +2.24 | +0.22 | Deep sample size in normal overs allows reliable baseline execution. |
| `strike_rate_normal` | **0.038** | 0.052 | +0.95 | +0.18 | Normal strike rate alone provides weak signal without boundary frequency context. |
| `dot_pct_overall` | **0.031** | 0.061 | +1.06 | -0.19 | Dot-ball accumulation in normal overs restricts momentum. |
| `ipl_ball_share` | **0.024** | 0.045 | +1.28 | +0.15 | Exposure to premier IPL bowling attacks elevates pressure readiness. |
| `batting_hand_LHB` | **0.012** | 0.022 | -1.14 | -0.11 | Left-handedness offers tactical match-up utility, though right-handers hold high sample depth. |

![Batting Feature Importance](fig1_batting_feature_importance.svg)

### 2.2 Cricket Domain Synthesis (Batting)
The explainability metrics reveal a profound finding: **Normal strike rate alone is an incomplete and misleading indicator of pressure capability.**
A batter who achieves a 140 strike rate by rotating singles and hitting occasional boundaries often collapses when required to score at 12+ runs per over. Conversely, batters with high `boundary_ball_pct_overall` (hitting boundaries on $> 18\%$ of balls) maintain a mechanical and psychological advantage: their boundary-scoring muscle memory translates directly into clutch execution.

---

## 3. Bowling Feature Explainability

### 3.1 Feature Importance Rankings
Evaluated on $N = 136$ Qualified Bowlers predicting continuous high-pressure economy rate (`economy_rate_high`, lower is better):

| Feature Name | Permutation Importance | Random Forest MDI | Ridge Coeff ($\beta_{\text{std}}$) | LogReg Coeff ($\beta_{\text{std}}$) | Tactical / Cricket Interpretation |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `boundary_conceded_pct_overall`| **0.523** | 0.294 | +0.65 | -0.58 | Boundary leakage is by far the primary driver of high-pressure economy blowout. |
| `boundary_conceded_pct_normal` | **0.134** | 0.119 | +0.24 | -0.28 | Bowlers who concede boundaries in low-leverage overs concede even more under pressure. |
| `economy_rate_overall` | **0.124** | 0.150 | +0.48 | -0.44 | Longitudinal baseline defensive standard sets the foundational boundary. |
| `wickets_per_over_overall` | **0.046** | 0.048 | -0.12 | +0.18 | Career wicket-taking threat forces batting caution and breaks partnerships. |
| `extras_per_legal_ball_normal` | **0.039** | 0.065 | -0.26 | +0.12 | Extras (wides/no-balls) lead to free hits and compound high-pressure pressure. |
| `dot_pct_normal` | **0.032** | 0.054 | -0.46 | +0.35 | Dot-ball generation creates run suppression and scoreboard pressure. |
| `is_spin` | **0.028** | 0.035 | -0.38 | +0.42 | Spinners suppress runs more effectively in high-pressure middle/death overs than pace. |
| `legal_balls_overall` | **0.022** | 0.058 | -0.18 | +0.14 | Longitudinal experience mitigates panicking under high Required Run Rates. |
| `bowling_arm_left` | **0.015** | 0.021 | -0.08 | +0.09 | Left-arm trajectory creates awkward angles across right-handed batters. |

![Bowling Feature Importance](fig2_bowling_feature_importance.svg)

### 3.2 Cricket Domain Synthesis (Bowling)
Over 65% of the total explainability variance in high-pressure bowling economy is governed by **boundary concession percentage** (`boundary_conceded_pct_overall` + `boundary_conceded_pct_normal`).
Bowlers who rely purely on dot-balls but leak boundaries every 4th or 5th delivery experience catastrophic failure in high-pressure death overs (where batters swing on every ball). To survive under high pressure, a bowler's yorker, slower-ball variation, or trajectory must physically prevent the ball from reaching the rope. Furthermore, **spin bowlers (`is_spin = 1`) exhibit a strong defensive advantage** (Ridge coefficient $\beta = -0.38$), systematically conceding lower high-pressure economies than medium pacers.

---

## 4. Unsupervised Strategic Archetypes

To assist tactical decision-makers in assembling a balanced roster, K-Means clustering was executed on multi-dimensional Empirical Bayes shrunk differentials and phase exposure shares.

### 4.1 Batting Strategic Archetypes ($k=3$)
*Features: Shrunk $\Delta \text{SR}$, Shrunk $\Delta \text{Dot\%}$, Shrunk $\Delta \text{Dismissal\%}$, High Pressure Exposure Ratio, High Pressure Death Share.*

![Batting Archetypes](fig3_batting_cluster_archetypes.svg)

| Archetype Name | Cluster ID | Qualified Count | Provisional Count | Shrunk $\Delta \text{SR}$ | Shrunk $\Delta \text{Dot\%}$ | Shrunk $\Delta \text{Dism\%}$ | High Death Share | Mean $I_{\text{rel}}$ | Mean $\text{SR}_{\text{high}}$ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Pressure Vulnerable** | 0 | 46 (42.2%) | 19 | -1.23 | +2.46% | +3.55% | 0.43 | 45.08 | 136.77 |
| **Top/Middle Order Accelerator** | 1 | 34 (31.2%) | 13 | +32.96 | -7.00% | +0.95% | 0.33 | 53.60 | 170.35 |
| **Death Phase Finisher** | 2 | 29 (26.6%) | 26 | +34.32 | -8.30% | +0.95% | 0.58 | 53.84 | 163.86 |

#### Tactical Roster Roles:
- **Death Phase Finishers (Cluster 2):** Elite finishers who face heavy death-over leverage (58% of their high-pressure balls in Overs 16–20), accelerate by +34.32 runs/100 balls, and cut dot-ball frequency by 8.3%. *Primary targets for batting positions 5, 6, and 7.*
- **Top/Middle Order Accelerators (Cluster 1):** Batters who thrive when pressure spikes in the Powerplay or middle overs (Overs 7–15), maintaining a massive 170.35 high-pressure strike rate while minimizing risk. *Essential for batting positions 1 through 4.*
- **Pressure Vulnerable (Cluster 0):** Batters whose strike rates stall (-1.23 differential) while their dot-ball percentage rises (+2.46%) and dismissal risk jumps by +3.55 dismissals/100 balls. *Must be sheltered from high Required Run Rate scenarios.*

---

### 4.2 Bowling Strategic Archetypes ($k=3$)
*Features: Shrunk $\Delta \text{Econ}$, Shrunk $\Delta \text{WPO}$, Shrunk $\Delta \text{Dot\%}$, High Pressure Exposure Ratio, High Pressure Death Share.*

![Bowling Archetypes](fig4_bowling_cluster_archetypes.svg)

| Archetype Name | Cluster ID | Qualified Count | Provisional Count | Shrunk $\Delta \text{Econ}$ | Shrunk $\Delta \text{WPO}$ | Shrunk $\Delta \text{Dot\%}$ | High Death Share | Mean $I_{\text{rel}}$ | Mean $\text{Econ}_{\text{high}}$ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **High-Pressure Conceder** | 0 | 58 (42.6%) | 22 | +3.97 | -0.083 | -17.35% | 0.74 | 45.55 | 12.44 |
| **Death Wicket Enforcer** | 1 | 46 (33.8%) | 19 | +2.02 | +0.105 | -8.29% | 0.80 | 53.88 | 10.94 |
| **Middle & Powerplay Restrictor** | 2 | 32 (23.5%) | 16 | +2.35 | +0.014 | -10.03% | 0.34 | 52.64 | 9.53 |

#### Tactical Roster Roles:
- **Death Wicket Enforcers (Cluster 1):** The gold standard for death-overs bowling. They absorb extreme death exposure (80% in death phase), actively increase their wicket-taking rate under pressure (+0.105 wickets/over), and restrict economy blowout to just +2.02 runs/over. *Essential for overs 18 and 20.*
- **Middle & Powerplay Restrictors (Cluster 2):** Defensive anchors who operate primarily in the Powerplay and middle overs (only 34% death share), conceding an exceptional 9.53 high-pressure economy. *Ideal for controlling high-pressure middle overs (Overs 7–15).*
- **High-Pressure Conceders (Cluster 0):** Bowlers whose economy explodes by nearly 4.0 runs/over (+3.97) under high pressure as dot balls collapse by -17.35%. *Must not be assigned death-overs duties in close finishes.*

---

## 5. Player-Level Case Study Attributions

By comparing actual high-pressure performance against Ridge out-of-fold predictions, we identify the exact player-level residuals that distinguish clutch overperformers from vulnerable underperformers.

![Predicted vs Actual High Pressure](fig5_predicted_vs_actual_pressure.svg)

### 5.1 Elite Outperformers (Positive Residuals)
1. **Sanju Samson (Qualified Batter):**
   - *Baseline Normal SR:* 142.11 | *Ridge Model Predicted SR:* 148.23
   - *Actual High-Pressure SR:* **197.87** | *Outperformance Residual:* **+49.64**
   - *Reliability Index:* **60.46 (Grade A)** | *Archetype:* Top/Middle Order Accelerator
   - *Attribution:* Samson possesses a strong baseline boundary frequency (19.4%), but under high pressure, his boundary rate surges to 28.7% while his dot-ball rate drops from 34.2% to 22.1%. His aggressive intent and pickup-pull against high-pace bowling allow him to vastly outperform baseline projections.
2. **Iftikhar Ahmed (Qualified Batter):**
   - *Baseline Normal SR:* 130.40 | *Ridge Model Predicted SR:* 143.12
   - *Actual High-Pressure SR:* **207.69** | *Outperformance Residual:* **+64.57**
   - *Reliability Index:* **56.81 (Grade B)** | *Archetype:* Death Phase Finisher
   - *Attribution:* Iftikhar operates with extreme boundary concentration in high-leverage death overs (boundary run % jumps to 78.4%), producing the largest positive residual in the entire qualified cohort.
3. **Wanindu Hasaranga (Qualified Bowler):**
   - *Baseline Normal Economy:* 7.15 | *Ridge Model Predicted Economy:* 8.85
   - *Actual High-Pressure Economy:* **6.40** | *Outperformance Residual:* **-2.45** (Runs/Over Suppressed)
   - *Reliability Index:* **58.81 (Grade A)** | *Archetype:* Middle & Powerplay Restrictor
   - *Attribution:* Hasaranga's deceptive googly and quick arm action allow him to *lower* his economy under pressure (from 7.15 down to 6.40), completely defying the league-wide upward economy shift.
4. **Haris Rauf (Qualified Bowler):**
   - *Baseline Normal Economy:* 8.35 | *Ridge Model Predicted Economy:* 10.15
   - *Actual High-Pressure Economy:* **7.74** | *Outperformance Residual:* **-2.41**
   - *Reliability Index:* **61.50 (Grade A)** | *Archetype:* Death Wicket Enforcer
   - *Attribution:* High pace (>145 km/h) combined with lethal reverse-swing yorkers allows Rauf to generate a +0.14 wickets/over surge in the death overs, suppressing boundaries below the expected model baseline.

### 5.2 Vulnerable Underperformers (Negative Residuals)
1. **Cameron Green (Qualified Batter):**
   - *Baseline Normal SR:* 135.20 | *Ridge Model Predicted SR:* 145.30
   - *Actual High-Pressure SR:* **81.40** | *Underperformance Residual:* **-63.90**
   - *Reliability Index:* **32.62 (Grade D)** | *Archetype:* Pressure Vulnerable
   - *Attribution:* Despite imposing physical stature and high baseline strike rate, Green's dot-ball percentage explodes under high pressure (jumping from 36.1% to 54.3%), while boundary striking drops to just 7.4%. He struggles against high-leverage defensive death fields.
2. **Shadab Khan (Qualified Batter):**
   - *Baseline Normal SR:* 136.40 | *Ridge Model Predicted SR:* 136.40
   - *Actual High-Pressure SR:* **87.50** | *Underperformance Residual:* **-48.90**
   - *Reliability Index:* **39.70 (Grade D)** | *Archetype:* Pressure Vulnerable
   - *Attribution:* Severely constrained when facing high pace at the death; dismissal rate doubles under pressure, causing him to fall well short of model expectations.

---

## 6. Interactive Visual Analytics

For full dynamic exploration of all 824 batters, 596 bowlers, multi-dimensional feature distributions, and cluster centroids, an interactive standalone dashboard has been compiled:
- **Interactive Dashboard:** `reports/task_06_figures/interactive_task_06_ml_dashboard.html`
- Contains interactive cross-filtering, hover tooltips displaying player names and metrics, and dual-axis feature importance views.

