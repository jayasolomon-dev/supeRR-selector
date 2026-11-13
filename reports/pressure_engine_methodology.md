# SUPERR SELECTOR — PRESSURE ENGINE METHODOLOGY DESIGN (REVISED)
**Document Reference:** `reports/pressure_engine_methodology.md`  
**Task Reference:** Master Task 04.1 (Pressure Engine: Methodology Design & Feature Specification)  
**Author:** Senior Cricket Data Scientist, T20 Performance Analyst & Machine Learning Architect  
**Project:** SUPERR SELECTOR (Rajasthan Royals SupeRR Selector Season 2 Hackathon)  
**Date:** November 2026 (Revision 2.0)  
**Status:** Approved Methodology Design — Awaiting User Approval Prior to Implementation (Task 04.2)  

---

## Executive Summary

The official problem statement for **Rajasthan Royals SupeRR Selector Season 2** requires identifying the **"Most Reliable Players Under Pressure"**. In competitive T20 cricket (IPL and Men's T20I), aggregate statistics (average, strike rate, economy rate) fail to reflect player value because they treat low-leverage routine play identically to high-crisis situations.

To solve this, **SUPERR SELECTOR** establishes a continuous, transparent, cricket-specific **Pressure Engine** that scores the match context prior to every delivery on a **0.0 to 100.0 continuous scale**.

### Critical Conceptual Distinctions
1. **Match-Situation Difficulty vs. Player Performance Under Pressure:**  
   The Pressure Engine strictly measures **objective match-situation difficulty / contextual leverage**. It is completely player-agnostic. Whether an elite international or an inexperienced tailender is on strike, a match situation requiring 18 runs off 6 balls has identical situational leverage. How an individual player executes under that pressure is evaluated separately in **Master Task 05 (Player Reliability & Performance Engine)**.
2. **Bowling Pressure Defined as Team-Context Pressure:**  
   Bowling pressure is explicitly defined as the **objective team-context defensive pressure faced by the bowler** (defensive runway, margin for error, proximity to defeat, boundary vulnerability). It is **not** a direct measurement of biometric heart rate, subjective bowler anxiety, or individual bowler execution difficulty.
3. **Decoupled Asymmetric Modeling:**  
   Batting and bowling pressures are modeled through independent, decoupled mathematical engines: **Batting Pressure ($P_{\text{bat}}$)** and **Bowling Pressure ($P_{\text{bowl}}$)**.
4. **Contextual Par Model in Innings 1:**  
   Required Run Rate (RRR) does not exist in the first innings. We strictly prohibit forcing synthetic chase metrics into Innings 1, instead using format-specific par baselines, wicket depletion curves, and phase acceleration.
5. **Proposed Status of Transformations & Cutoffs:**  
   The sigmoidal RRR formulation and categorical tier thresholds are documented as **proposed baseline hypotheses**, subject to empirical verification and calibration in Master Task 04.2.
6. **Structural Anti-Leakage Verification:**  
   Correlation-based leakage tests have been replaced with four rigorous data-engineering proofs: Feature Lineage Audit, Prefix Invariance, Future Invariance, and Production Dependency Audits.

---

## 1. Defining Pressure: The Asymmetry Principle

Pressure in cricket is the **mathematical consequence of asymmetric risk and required execution under finite resource constraints**.

### 1.1 Team-Context Asymmetry

A delivery represents a confrontation between two opposing teams with diametrically opposed objective functions:
- **Batting Objective:** Accumulate runs at or above the required scoring rate while preserving wickets (discrete non-renewable resources).
- **Bowling Objective:** Restrict runs below the required rate and capture wickets to deplete opponent batting resources.

```
                          MATCH STATE: 8 RUNS NEEDED FROM 6 BALLS (6 WICKETS DOWN)
                                                  │
                       ┌──────────────────────────┴──────────────────────────┐
                       ▼                                                     ▼
           BATTER'S PERSPECTIVE                                   BOWLER'S PERSPECTIVE
    - RRR = 8.00 RPO (Very achievable in modern T20)        - Team Runway: Only 8 runs to defend!
    - Win Expectancy: ~65-70%                               - Margin for Error: Zero (1 boundary = fatal)
    - Tactical Need: 1 boundary or couple of twos           - Tactical Need: 4-5 dots/wickets, yorkers
    - Situational Pressure: MODERATE-HIGH (~46 / 100)       - Team Defensive Pressure: HIGH (~68 / 100)
```

### 1.2 Scenario Comparison: Canonical Match States

| Scenario | Match Situation | Batting Perspective ($P_{\text{bat}}$) | Bowling Perspective ($P_{\text{bowl}}$) | Tactical Reason for Divergence |
|:---|:---|:---:|:---:|:---|
| **1. Tight Death Defense** | Innings 2, 20th Over, 8 runs needed off 6 balls, 6 wkts down | **45.8 / 100** *(Moderate)* | **67.5 / 100** *(High)* | Bowler's team has narrow defensive runway; single boundary fatal. Batter has favorable win expectancy. |
| **2. Steep Chase Crisis** | Innings 2, 20th Over, 24 runs needed off 6 balls, 7 wkts down | **100.0 / 100** *(Extreme)* | **23.5 / 100** *(Low)* | Batter must hit 4 sixes in 6 balls. Bowler's team has 23-run buffer; execution pressure is low. |
| **3. Powerplay Collapse** | Innings 1, 3rd Over, 15/3, early swing conditions | **61.6 / 100** *(Moderate-High)* | **32.9 / 100** *(Low)* | Batter faces severe resource crisis; must rebuild without stalling. Bowling team on the attack. |
| **4. Middle-Overs Cruise** | Innings 2, 10th Over, chasing 160, score is 100/1 (60 off 60 balls) | **18.0 / 100** *(Low)* | **60.4 / 100** *(Moderate)* | Batting team cruising at 6.0 RRR with 9 wickets in hand. Bowling team under pressure for breakthrough. |
| **5. Death Acceleration** | Innings 1, 17th Over, score is 170/3, set top-order | **43.4 / 100** *(Moderate)* | **67.4 / 100** *(High)* | Batting team scoring above par with wickets in hand (low pace pressure). Bowlers facing late-innings onslaught. |

---

## 2. First-Innings Pressure Model (Target Setting)

### 2.1 The Cricket Reality: No RRR in Innings 1
In the first innings, there is no target. Therefore, `target`, `required_runs_before`, and `required_run_rate_before` are mathematically undefined (`NaN`). 

Forcing a synthetic target (e.g., assuming an arbitrary 180 target) introduces artificial assumptions that distort analysis. Instead, Innings 1 pressure is modeled through **available pre-delivery resource dynamics**:
1. Scoring rate relative to competition baseline ($\text{PAR}_{\text{comp}}$).
2. Wicket resource depletion relative to expected wickets.
3. Phase acceleration urgency as overs expire.

### 2.2 Baseline Scoring Environments ($\text{PAR}_{\text{comp}}$)
Empirical analysis of the 837 matches in the verified dataset establishes format-specific medians:
- **IPL Baseline ($\text{PAR}_{\text{IPL}}$):** Median 1st innings run rate is **9.35 RPO** (Median total: 187 runs).
- **Men's T20I Baseline ($\text{PAR}_{\text{T20I}}$):** Median 1st innings run rate is **8.59 RPO** (Median total: 169 runs).

$$\text{PAR}_{\text{comp}} = \begin{cases} 9.35 & \text{if } \text{competition\_category} == \text{'IPL'} \\ 8.59 & \text{if } \text{competition\_category} == \text{'T20I'} \end{cases}$$

### 2.3 Batting First-Innings Formulation ($P_{\text{bat}, \text{inn}1}$)

$$P_{\text{bat}, \text{inn}1} = \text{clip}\left(w_1 \cdot I_{\text{pace\_deficit}} + w_2 \cdot I_{\text{resource\_depletion}} + w_3 \cdot I_{\text{phase\_urgency}}, 0.0, 100.0\right)$$
Proposed weights: $w_1 = 0.45, w_2 = 0.35, w_3 = 0.20$.

#### 1. Pace Deficit Indicator ($I_{\text{pace\_deficit}}$)
Measures how far current scoring rate lags $\text{PAR}_{\text{comp}}$. For early deliveries ($\text{legal\_balls\_before} < 12$), Bayesian shrinkage prevents extreme early variance:
$$\text{CRR}_{\text{adj}} = \frac{\text{score\_before} + \text{PAR}_{\text{comp}} \times 2.0}{\frac{\text{legal\_balls\_before}}{6.0} + 2.0}$$
$$I_{\text{pace\_deficit}} = \text{clip}\left(50.0 + 7.5 \times (\text{PAR}_{\text{comp}} - \text{CRR}_{\text{adj}}), 0.0, 100.0\right)$$

#### 2. Resource Depletion Indicator ($I_{\text{resource\_depletion}}$)
Compares actual wickets lost to an expected wickets heuristic:
$$W_{\text{exp}}(t) = 6.0 \times \left(\frac{\text{legal\_balls\_before}}{\text{total\_legal\_balls}}\right)^{0.80}$$
$$\Delta_{\text{wkt}} = \text{wickets\_before} - W_{\text{exp}}(t)$$
$$I_{\text{resource\_depletion}} = \text{clip}\left(50.0 + 12.0 \times \Delta_{\text{wkt}}, 0.0, 100.0\right)$$

#### 3. Phase Urgency Indicator ($I_{\text{phase\_urgency}}$)
Captures the increasing urgency to accelerate as remaining legal balls expire:
$$I_{\text{phase\_urgency}} = 35.0 + 50.0 \times \left(\frac{\text{legal\_balls\_before}}{\text{total\_legal\_balls}}\right)^{1.5}$$

---

### 2.4 Empirical Analysis of the Expected Wickets Curve

To ensure scientific honesty, we compare the proposed theoretical heuristic $W_{\text{exp}}(t) = 6.0 \times (t/120)^{0.80}$ against observed 1st innings wickets across the 837 matches:

| Over Completed | Legal Balls Bowled | Observed Mean Wickets | Proposed Heuristic $W_{\text{exp}}(t)$ | Residual Gap |
|:---:|:---:|:---:|:---:|:---:|
| **Over 2.0** | 12 | **0.47** | 0.95 | +0.48 (Overestimates) |
| **Over 4.0** | 24 | **1.07** | 1.66 | +0.59 (Overestimates) |
| **Over 6.0 (PP end)**| 36 | **1.61** | 2.29 | +0.68 (Overestimates) |
| **Over 8.0** | 48 | **2.06** | 2.88 | +0.82 (Overestimates) |
| **Over 10.0 (Mid)** | 60 | **2.58** | 3.45 | +0.87 (Overestimates) |
| **Over 12.0** | 72 | **3.10** | 3.99 | +0.88 (Overestimates) |
| **Over 14.0** | 84 | **3.72** | 4.51 | +0.79 (Overestimates) |
| **Over 15.0** | 90 | **4.03** | 4.77 | +0.73 (Overestimates) |
| **Over 17.0** | 102 | **4.64** | 5.27 | +0.63 (Overestimates) |
| **Over 19.0** | 114 | **5.58** | 5.76 | +0.18 (Overestimates) |

> [!NOTE]
> **Empirical Finding:** The proposed $6.0 \times (f^{0.80})$ curve is an *a priori* concave theoretical heuristic. Real-world T20 cricket exhibits a slightly *convex* wicket progression (wickets fall slower during the Powerplay as top orders consolidate, and accelerate sharply during the Death overs).  
> **Status:** We retain the proposed formula as a baseline design heuristic for Task 04.1 and track this curvature difference as an explicit unresolved assumption to be empirically calibrated in Task 04.2.

---

### 2.5 Bowling First-Innings Formulation ($P_{\text{bowl}, \text{inn}1}$)

$$P_{\text{bowl}, \text{inn}1} = \text{clip}\left(u_1 \cdot I_{\text{containment\_stress}} + u_2 \cdot I_{\text{wicket\_drought}} + u_3 \cdot I_{\text{death\_defense}}, 0.0, 100.0\right)$$
Proposed weights: $u_1 = 0.40, u_2 = 0.35, u_3 = 0.25$.

#### 1. Containment Stress ($I_{\text{containment\_stress}}$)
Measures defensive stress when the batting side scores above par:
$$I_{\text{containment\_stress}} = \text{clip}\left(50.0 + 7.5 \times (\text{CRR}_{\text{adj}} - \text{PAR}_{\text{comp}}), 0.0, 100.0\right)$$

#### 2. Wicket Drought ($I_{\text{wicket\_drought}}$)
Elevated when the bowling team fails to take wickets, allowing opponent top-order batters to settle:
$$I_{\text{wicket\_drought}} = \text{clip}\left(50.0 - 10.0 \times \Delta_{\text{wkt}}, 0.0, 100.0\right)$$

#### 3. Death Defense Crunch ($I_{\text{death\_defense}}$)
Inherent execution demand placed on the bowling unit during late overs:
$$I_{\text{death\_defense}} = \begin{cases} 
30.0 & \text{if Phase == 'Powerplay'} \\
45.0 & \text{if Phase == 'Middle'} \\
75.0 + 15.0 \times \left(\frac{\text{legal\_balls\_before} - 90}{30}\right) & \text{if Phase == 'Death'}
\end{cases}$$

---

## 3. Second-Innings Pressure Model (The Run Chase)

### 3.1 Proposed Bounded Sigmoidal Transformation ($S_{\text{RRR}}$)

Raw Required Run Rate (`required_run_rate_before`) has an extreme mathematical right tail (90th percentile = 16.0 RPO, 99th percentile = 49.8 RPO, maximum = 810.0 RPO in the verified dataset). A linear model collapses under these outliers.

We propose a bounded sigmoidal feature:
$$S_{\text{RRR}} = \frac{100.0}{1.0 + \exp\left(-k \cdot (\text{RRR} - \text{PAR}_{\text{comp}})\right)}$$
- Proposed midpoint: $\text{PAR}_{\text{comp}}$ (9.35 for IPL, 8.59 for T20I).
- Proposed steepness: $k = 0.35$.
- *Proposed Status:* This formula is a proposed design hypothesis. Formal validation of $k$ and the midpoint will be conducted in Task 04.2 via win-probability calibration curves.
- *Preservation Guarantee:* `required_run_rate_before` is preserved verbatim in the dataset for reporting and auditability.

---

### 3.2 Batting Second-Innings Formulation ($P_{\text{bat}, \text{inn}2}$)

$$P_{\text{bat}, \text{inn}2} = \text{clip}\left(\left[ c_1 \cdot S_{\text{RRR}} + c_2 \cdot I_{\text{wkt\_stress}} \right] \times M_{\text{crunch}}(t), 0.0, 100.0\right)$$
Proposed weights: $c_1 = 0.60, c_2 = 0.40$.

#### 1. Wicket Depletion Stress ($I_{\text{wkt\_stress}}$)
$$I_{\text{wkt\_stress}} = 100.0 \times \left(\frac{\text{wickets\_before}}{10.0}\right)^{1.35}$$

#### 2. Ball Crunch Multiplier ($M_{\text{crunch}}$)
Magnifies pressure as balls remaining decreases, but only when the chase is above par:
$$f_{\text{bowled}} = \frac{\text{legal\_balls\_before}}{\text{total\_legal\_balls}}$$
$$M_{\text{crunch}} = \begin{cases}
1.0 + 0.30 \times f_{\text{bowled}} \times \left(\frac{S_{\text{RRR}} - 50.0}{50.0}\right) & \text{if } S_{\text{RRR}} \ge 50.0 \\
1.0 - 0.25 \times f_{\text{bowled}} \times \left(\frac{50.0 - S_{\text{RRR}}}{50.0}\right) & \text{if } S_{\text{RRR}} < 50.0
\end{cases}$$

---

### 3.3 Bowling Second-Innings Formulation ($P_{\text{bowl}, \text{inn}2}$)

$$P_{\text{bowl}, \text{inn}2} = \text{clip}\left(d_1 \cdot I_{\text{runway\_crunch}} + d_2 \cdot I_{\text{boundary\_vulnerability}} + d_3 \cdot I_{\text{batting\_depth}}, 0.0, 100.0\right)$$
Proposed weights: $d_1 = 0.50, d_2 = 0.30, d_3 = 0.20$.

#### 1. Defensive Runway Crunch ($I_{\text{runway\_crunch}}$)
Measures runs to defend per legal ball: $\text{RPB}_{\text{defend}} = \frac{\text{required\_runs\_before}}{\max(\text{legal\_balls\_remaining\_before}, 1)}$.
$$I_{\text{runway\_crunch}} = \begin{cases}
100.0 & \text{if } \text{RPB}_{\text{defend}} \le 0.5 \\
100.0 - 35.0 \times (\text{RPB}_{\text{defend}} - 0.5) & \text{if } 0.5 < \text{RPB}_{\text{defend}} \le 2.0 \\
\max(15.0, 47.5 - 12.0 \times (\text{RPB}_{\text{defend}} - 2.0)) & \text{if } \text{RPB}_{\text{defend}} > 2.0
\end{cases}$$

#### 2. Boundary Vulnerability ($I_{\text{boundary\_vulnerability}}$)
$$\text{Boundaries\_Allowed} = \frac{\text{required\_runs\_before} - 1}{4.0}$$
$$I_{\text{boundary\_vulnerability}} = \text{clip}\left(100.0 - 15.0 \times \text{Boundaries\_Allowed}, 0.0, 100.0\right)$$

#### 3. Chasing Team Wickets Remaining ($I_{\text{batting\_depth}}$)
$$I_{\text{batting\_depth}} = 100.0 \times \left(1.0 - \left(\frac{\text{wickets\_before}}{10.0}\right)^{1.35}\right)$$

---

### 3.4 Terminal State Policy & Synthetic Edge-Case Handling

> [!IMPORTANT]
> **Terminal State Policy:**  
> In real cricket, deliveries only occur while an innings is actively underway. Once the winning run is scored on delivery $t$ (or the final scheduled ball is completed), the match concludes immediately. No delivery is ever bowled when `required_runs_before <= 0` or when `legal_balls_remaining_before == 0`.  
> 
> Therefore, **terminal states (such as SYN-08 and SYN-09) are NOT ordinary delivery-level pressure observations**. They are synthetic boundary unit tests designed exclusively to verify that mathematical functions terminate gracefully without dividing by zero or producing `NaN`s.
> 
> **Operational Guarantees:**
> 1. **Zero Post-Delivery Leakage in Real Deliveries:** No actual historical delivery row is ever assigned a pressure score using post-delivery target-reached or innings-completed information. Every delivery is evaluated strictly *ex-ante* (based on match state prior to the ball being bowled).
> 2. **Audit Flags & Exclusion:** If any anomalous or dead-rubber delivery ever occurs after a target is achieved, it is explicitly flagged via `is_target_met_delivery = True` (or `impossible_chase_state = True`), allowing downstream player evaluation in Task 05 to exclude non-competitive deliveries.
> 3. **Mathematical Boundary Definitions (for Synthetic Robustness):**
>    - **Target Reached / Overshot (`required_runs_before <= 0`):** Both $P_{\text{bat}} = 0.00$ and $P_{\text{bowl}} = 0.00$ (SYN-09).
>    - **Zero Balls Remaining with Runs Needed (`legal_balls_remaining_before == 0` and `required_runs_before > 0`):** Batting side has failed target ($P_{\text{bat}} = 100.00$); bowling side has secured victory ($P_{\text{bowl}} = 0.00$) (SYN-08).
> 4. **DLS Innings-Specific Capacity:**
>    - In shortened matches, scheduled capacity varies by innings (`total_legal_balls`). All fraction calculations ($f_{\text{bowled}}$) use the specific innings capacity from the match-state table.

---

## 4. Proposed Categorization Framework

Deliveries are grouped into four ordinal tiers for dashboard filtering:
- **Low:** $[0.0, 40.0)$ (~35–40% empirical expectation) — Routine play.
- **Moderate:** $[40.0, 65.0)$ (~30–35% empirical expectation) — Standard competitive play.
- **High:** $[65.0, 85.0)$ (~18–22% empirical expectation) — Serious pressure crunch.
- **Extreme:** $[85.0, 100.0]$ (~8–12% empirical expectation) — Crisis situations.

> [!IMPORTANT]
> **Proposed Status:** These threshold cutoffs are proposed design values based on preliminary domain analysis. They will be formally evaluated in Task 04.2 through empirical quantile analysis and win-expectancy inflection point testing.

---

## 5. Structural Anti-Leakage Governance

Rather than using statistical correlation thresholds with current ball runs or wickets (which can be confounded by legitimate cricket dynamics), anti-leakage is enforced through four strict software and data-engineering tests:

1. **Feature Lineage Audit:** Static code inspection and AST verification proving that no post-delivery column (`runs`, `ball_total_runs`, `is_wicket`, `dismissal_type`) appears in the pressure calculation DAG.
2. **Prefix Invariance Test:** Slicing the delivery table at ball $t$ ($df[:t]$) and verifying that $P(t)$ computed on the historical prefix is bit-for-bit identical to $P(t)$ computed on the full dataset.
3. **Future Invariance Test:** Perturbing future rows ($t+1 \dots T$) with random noise and confirming that $P(t)$ does not change by even $10^{-9}$.
4. **Production Dependency Audit:** Runtime assertion checking that only columns ending in `_before`, match-level metadata, or tournament constants are ingested.

---

## 6. Methodology Change Log

| Revision | Date | Section Affected | Change Description & Rationale |
|:---:|:---:|:---|:---|
| **v1.0** | 2026-11-12 | All | Initial methodology proposal for Master Task 04.1. |
| **v2.0** | 2026-11-12 | Executive Summary | Clarified distinction between match difficulty (Task 04) and player performance (Task 05). |
| **v2.0** | 2026-11-12 | Section 1.1 | Defined bowling pressure as objective team-context defensive pressure, not individual stress. |
| **v2.0** | 2026-11-12 | Section 2.4 | Added empirical validation comparison of expected-wickets curve against observed wicket distribution. |
| **v2.0** | 2026-11-12 | Section 2.3 & 2.5 | Formally detailed missing components: $I_{\text{phase\_urgency}}$ and $I_{\text{death\_defense}}$. |
| **v2.0** | 2026-11-12 | Section 3.1 & 4.0 | Designated RRR sigmoid parameters ($k=0.35, \text{PAR}$) and category cutoffs as proposed methodology. |
| **v2.0** | 2026-11-12 | Section 3.4 | Clarified DLS innings-specific capacity scaling and terminal state handling (0 balls, target met). |
| **v2.0** | 2026-11-12 | Section 5.0 | Replaced correlation-based anti-leakage tests with 4 structural data engineering invariance proofs. |

---

## 7. List of Unresolved Assumptions (To Be Resolved in Task 04.2)

1. **Expected Wickets Curvature Assumption:** The proposed formula $W_{\text{exp}}(t) = 6.0 \times (t/120)^{0.80}$ overestimates observed wickets in the Powerplay by ~0.6–0.8 wickets. Task 04.2 will evaluate whether an empirically fitted polynomial $W_{\text{exp}}(t) = 6.2 \times (t/120)^{1.25}$ improves calibration.
2. **Sigmoid Steepness Parameter ($k=0.35$):** Assumes an RRR of 16.0 RPO corresponds to ~91% saturation. Task 04.2 will test sensitivity to $k \in [0.30, 0.40]$.
3. **Static Category Cutoffs ($40, 65, 85$):** Assumes fixed thresholds align with empirical quartiles across both IPL and T20I. Task 04.2 will verify whether format-specific quantile thresholds are required.
4. **Associate vs Full Member Par Variance in T20I:** Assumes a single unified par of 8.59 RPO for all Men's T20Is. Task 04.2 will inspect whether Associate-only matches warrant a lower baseline (~7.80 RPO).
5. **Component Weight Perturbation:** Assumes weights ($0.60/0.40$ chase, $0.45/0.35/0.20$ 1st inn) represent optimal domain balance. Task 04.2 will run sensitivity analysis verifying rank correlation stability ($r_s \ge 0.95$).
