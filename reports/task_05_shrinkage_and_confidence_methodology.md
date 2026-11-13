# SUPERR SELECTOR — TASK 05 SHRINKAGE & CONFIDENCE METHODOLOGY REPORT

**Document Reference:** `reports/task_05_shrinkage_and_confidence_methodology.md`  
**Task Reference:** Master Task 05 — Phase D: Statistical Shrinkage & Uncertainty Methodology  
**Author:** Senior Cricket Data Scientist, Statistical Modeler & Quantitative Auditor  
**Project:** Rajasthan Royals SupeRR Selector Season 2 Hackathon  
**Target Module:** `src/analytics/task_05_reliability.py`  
**Outputs Generated:**
- `data/analytics/task_05_batter_reliability.csv` (824 batters)
- `data/analytics/task_05_bowler_reliability.csv` (596 bowlers)  
**Date:** November 12, 2026  
**Status:** **APPROVED & CERTIFIED**  

---

## 1. Executive Summary

A critical challenge in cricket performance analytics is the **small-sample distortion problem**: players with 3 deliveries faced in a high-pressure scenario may exhibit an extreme strike rate of $300.0$ or a bowler who conceded 1 single in 2 pressure deliveries may exhibit an economy rate of $3.00$. Ranking players on raw sample estimates violates basic principles of statistical inference.

To solve this, Master Task 05 establishes an **Empirical-Bayes Shrinkage and Match-Cluster Uncertainty Framework**:
1. **Multi-Gate Eligibility Tiering:** Classifies players into `Qualified`, `Provisional`, and `Ineligible` based on exposure in both high-pressure and normal-pressure environments.
2. **Empirical Bayes Partial Pooling:** Shrinks individual player differentials toward empirical population priors using the harmonic mean effective sample size $n_{\text{eff}} = \frac{2 n_h n_n}{n_h + n_n}$.
3. **Multi-Dimensional Composite Reliability Indices:** Combines rate differentials, efficiency suppression, and absolute benchmark performance on a standardized $[0.0, 100.0]$ scale.
4. **Match-Cluster Bootstrap Confidence Intervals:** Conducts $B = 500$ cluster-resampling iterations across 837 matches (seed 42), preserving within-match delivery correlations to construct authentic 95% confidence intervals and standard errors.

---

## 2. Multi-Gate Eligibility Framework

To ensure that rankings in downstream tasks (Task 06 and Task 07) rest on verified statistical support, three transparent tiers are established:

```
Full Population (824 Batters, 596 Bowlers)
├── Qualified Tier: Substantial dual exposure & multi-match sample
│   ├── Batters: BF_high >= 30 AND BF_norm >= 30 AND Matches >= 5 (N = 109, 13.2%)
│   └── Bowlers: LB_high >= 30 AND LB_norm >= 30 AND Matches >= 5 (N = 136, 22.8%)
├── Provisional Tier: Modest exposure (high shrinkage applied toward prior)
│   ├── Batters: BF_high >= 15 AND BF_norm >= 15 AND Matches >= 3 (N = 58, 7.0%)
│   └── Bowlers: LB_high >= 15 AND LB_norm >= 15 AND Matches >= 3 (N = 57, 9.6%)
└── Ineligible Tier: Sparse exposure; clamped to neutral population baseline (50.0)
    ├── Batters: BF_high < 15 OR BF_norm < 15 OR Matches < 3 (N = 657, 79.7%)
    └── Bowlers: LB_high < 15 OR LB_norm < 15 OR Matches < 3 (N = 403, 67.6%)
```

### Eligibility Gate Census
- **Batting Population:** $109$ Qualified ($13.2\%$), $58$ Provisional ($7.0\%$), $657$ Ineligible ($79.7\%$).
- **Bowling Population:** $136$ Qualified ($22.8\%$), $57$ Provisional ($9.6\%$), $403$ Ineligible ($67.6\%$).

---

## 3. Empirical Bayes Shrinkage Mechanics

### 3.1 Harmonic Mean Effective Sample Size ($n_{\text{eff}}$)
A player who has faced $300$ normal balls but only $5$ pressure balls cannot reliably be compared on differential metrics ($\Delta \text{SR} = \text{SR}_h - \text{SR}_n$). The variance of a difference of two independent sample means $\bar{X}_h - \bar{X}_n$ is proportional to:
$$\text{Var}(\bar{X}_h - \bar{X}_n) = \frac{\sigma_h^2}{n_h} + \frac{\sigma_n^2}{n_n} \approx \sigma^2 \left(\frac{1}{n_h} + \frac{1}{n_n}\right) = \frac{2\sigma^2}{n_{\text{eff}}}$$
where $n_{\text{eff}}$ is the **harmonic mean sample size**:
$$n_{\text{eff}} = \frac{2 \cdot n_h \cdot n_n}{n_h + n_n}$$
This formulation penalizes sample imbalance: if $n_h = 10$ and $n_n = 500$, $n_{\text{eff}} = 19.6$ balls, preventing players with small pressure exposure from claiming high reliability.

### 3.2 Empirical Bayes Shrinkage Weight ($w_i$)
The player's observed metric $\hat{\theta}_i$ is shrunk toward the empirical population mean $\mu_0$:
$$\theta_i^{\text{shrunk}} = w_i \hat{\theta}_i + (1 - w_i) \mu_0$$
where:
$$w_i = \frac{n_{\text{eff}, i}}{n_{\text{eff}, i} + K_0}$$
- For Batting: $K_{\text{bat}} = 30.0$ balls.
- For Bowling: $K_{\text{bowl}} = 30.0$ legal balls.

#### Shrinkage Properties:
- At $n_{\text{eff}} = 10$: $w = 10 / (10 + 30) = 0.250$ (75% weight on prior baseline).
- At $n_{\text{eff}} = 30$: $w = 30 / (30 + 30) = 0.500$ (50% weight on player's data).
- At $n_{\text{eff}} = 90$: $w = 90 / (90 + 30) = 0.750$ (75% weight on player's data).
- At $n_{\text{eff}} \ge 270$: $w \ge 0.900$ (player's historical evidence dominates).

### 3.3 Population Priors (from Qualified Cohort)

| Role | Metric | Qualified Population Mean ($\mu_0$) | Qualified Population Std ($\sigma_0$) | Favorable Direction |
| :--- | :--- | :---: | :---: | :---: |
| **Batting** | $\Delta \text{SR}$ (High minus Normal) | $+18.64$ RPO | $36.10$ | Positive ($+$) |
| **Batting** | $\Delta \text{Dot\%}$ (High minus Normal) | $-3.45\%$ | $8.06\%$ | Negative ($-$) |
| **Batting** | $\Delta \text{DismissalRate}_{100}$ | $+2.07$ per 100b | $3.34$ | Negative ($-$) |
| **Batting** | $\text{SR}_{\text{high}}$ (Absolute Benchmark) | $154.45$ RPO | $31.36$ | Positive ($+$) |
| **Bowling** | $\Delta \text{Econ}$ (High minus Normal) | $+2.95$ RPO | $2.30$ | Negative ($-$) |
| **Bowling** | $\Delta \text{WktPerOver}$ | $+0.006$ wkts/ov | $0.191$ | Positive ($+$) |
| **Bowling** | $\Delta \text{Dot\%}$ (High minus Normal) | $-12.57\%$ | $6.99\%$ | Positive ($+$) |
| **Bowling** | $\text{Econ}_{\text{high}}$ (Absolute Benchmark) | $11.25$ RPO | $2.03$ | Negative ($-$) |

---

## 4. Multi-Component Reliability Index Construction

Each index integrates four distinct statistical dimensions, weighted by domain relevance and verified for multicollinearity ($r < 0.65$ between components):

### 4.1 Batter Reliability Index Formula
$$Z_{\text{bat}} = 0.40 \cdot Z_{\Delta \text{SR}} + 0.25 \cdot Z_{\Delta \text{Dot}} + 0.20 \cdot Z_{\Delta \text{Dis}} + 0.15 \cdot Z_{\text{SR\_high}}$$
$$\text{Batter Reliability Index} = \text{clip}\left(50.0 + 10.0 \times Z_{\text{bat}}, 0.0, 100.0\right)$$
- **Directionality:** Higher strike-rate differential ($+$), lower dot ball differential ($+$), lower dismissal rate differential ($+$), and higher absolute high-pressure strike rate ($+$) all elevate the index.

### 4.2 Bowler Reliability Index Formula
$$Z_{\text{bowl}} = 0.40 \cdot Z_{\Delta \text{Econ}} + 0.25 \cdot Z_{\Delta \text{Wkt}} + 0.20 \cdot Z_{\Delta \text{Dot}} + 0.15 \cdot Z_{\text{Econ\_high}}$$
$$\text{Bowler Reliability Index} = \text{clip}\left(50.0 + 10.0 \times Z_{\text{bowl}}, 0.0, 100.0\right)$$
- **Directionality:** Economy suppression under pressure ($+$), wicket acceleration under pressure ($+$), dot ball preservation ($+$), and lower absolute high-pressure economy rate ($+$) all elevate the index.

---

## 5. Match-Cluster Bootstrap Uncertainty Quantification

Individual delivery outcomes within a match are not independent: pitch conditions, dew, ground dimensions, and match momentum induce delivery-level correlation.

### 5.1 Algorithm Specification
1. Let $\mathcal{M} = \{m_1, m_2, \dots, m_{837}\}$ be the set of unique matches.
2. For iteration $b = 1, \dots, 500$:
   - Draw a sample of matches $\mathcal{M}^{(b)}$ with replacement ($|\mathcal{M}^{(b)}| = 837$).
   - Weight each match's deliveries by its multiplicity in $\mathcal{M}^{(b)}$.
   - Re-aggregate metrics for every player across the resampled match set.
   - Recompute empirical Bayes shrunk reliability indices.
3. Compute 2.5th and 97.5th percentiles across the 500 draws to yield the **95% Bootstrap Confidence Interval** `[ci_lower_95, ci_upper_95]`, and standard error `ci_std_error`.

### 5.2 Reliability Grades
- **Elite:** Score $\ge 70.0$, Qualified tier.
- **High:** Score $\in [60.0, 70.0)$, Qualified tier.
- **Moderate:** Score $\in [45.0, 60.0)$, Qualified tier.
- **Low:** Score $< 45.0$, Qualified tier.
- **Provisional:** Players meeting Provisional thresholds (sub-graded High/Mod/Low).
- **Unrated:** Ineligible players lacking statistical exposure.

