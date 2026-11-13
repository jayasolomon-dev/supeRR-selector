# SUPERR SELECTOR — PRESSURE ENGINE VALIDATION PLAN (REVISED)
**Document Reference:** `reports/pressure_engine_validation_plan.md`  
**Task Reference:** Master Task 04.1 (Pressure Engine: Methodology Design & Feature Specification)  
**Author:** Senior Cricket Data Scientist & Quality Assurance Lead  
**Project:** SUPERR SELECTOR (Rajasthan Royals SupeRR Selector Season 2 Hackathon)  
**Date:** November 2026 (Revision 2.0)  
**Status:** Approved Validation Suite Specification — To Be Executed Upon Engine Implementation (Task 04.2)  

---

## 1. Objectives & Quality Standards

Before the Pressure Engine's calculations can be accepted for downstream player reliability ranking in Master Task 05, the implementation in **Master Task 04.2** must pass a rigorous, automated validation suite.

### Core Testing Objectives
1. **Mathematical Integrity:** Guarantee that all scores lie strictly within the closed interval $[0.00, 100.00]$ without `NaN`, nulls, or infinite values.
2. **Edge-Case Resilience:** Verify graceful mathematical behavior under extreme cricket boundary conditions (0 balls remaining, raw RRR exceeding 100+, early innings variance, negative required runs, DLS shortened matches).
3. **Cricket Domain Monotonicity:** Confirm that pressure moves strictly in the direction dictated by cricket logic (e.g., losing wickets increases batting pressure; increasing required runs increases batting pressure).
4. **Tactical Asymmetry Verification:** Confirm that identical match states produce expected divergent outcomes for batter and bowler (e.g. defending 6 off 6 balls produces higher bowler pressure than batter pressure).
5. **Structural Anti-Leakage Proofs:** Eliminate correlation-based heuristics and formally prove zero data leakage via Feature Lineage, Prefix Invariance, Future Invariance, and Production Dependency Audits.
6. **Cross-Format Equity:** Confirm that format-specific calibration produces balanced, unbiased pressure distributions between IPL and Men's T20I.
7. **Weight Robustness:** Confirm through sensitivity perturbation that player rankings do not destabilize if weights shift by $\pm 10\%$.
8. **Deterministic Synthetic Fixtures:** Assert literal, mathematically recalculated expected scores on 10 canonical in-memory fixtures.

---

## 2. Validation Test Suite Architecture (8 Test Groups, 21 Tests)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   PRESSURE ENGINE TEST SUITE (21 TESTS)                     │
├──────────────────────────────┬──────────────────────────────────────────────┤
│ Group 1: Numerical Bounds    │ Tests 01–03: Range [0,100], no NaNs, counts │
│ Group 2: Edge-Case Fixtures  │ Tests 04–08: 0 balls, extreme RRR, target met│
│ Group 3: Innings Separation  │ Tests 09–10: No RRR in Inn 1, format par     │
│ Group 4: Monotonicity Checks │ Tests 11–13: Wicket, run rate & asymmetry    │
│ Group 5: Anti-Leakage Proofs │ Tests 14–17: Lineage, prefix & future invari │
│ Group 6: Cross-Format Equity │ Tests 18–19: Distribution parity IPL vs T20I │
│ Group 7: Synthetic Fixtures  │ Test 20: 10 deterministic in-memory fixtures │
│ Group 8: Weight Sensitivity  │ Test 21: Perturbation stability (rs > 0.95)  │
└──────────────────────────────┴──────────────────────────────────────────────┘
```

---

## 3. Detailed Specification of Validation Tests

### Group 1: Numerical Boundaries & Range Invariants

#### TEST 01: Pressure Score Range Enforcement $[0.00, 100.00]$
- **Scope:** All 194,014 deliveries in processed dataset.
- **Assertion:** 
  $$\forall i \in [1, 194014]: 0.00 \le \text{batting\_pressure\_score}_i \le 100.00$$
  $$\forall i \in [1, 194014]: 0.00 \le \text{bowling\_pressure\_score}_i \le 100.00$$
- **Failure Condition:** Any single float value $< 0.00$ or $> 100.00$.

#### TEST 02: Non-Null / Non-NaN Completeness
- **Scope:** All 194,014 deliveries.
- **Assertion:** Both `batting_pressure_score` and `bowling_pressure_score` must contain exactly **0 missing values** (`isna().sum() == 0`).
- **Failure Condition:** Any `NaN`, `None`, or `inf`.

#### TEST 03: Delivery Volume & Match Preservation
- **Scope:** Output dataset row count.
- **Assertion:** Total rows must equal **exactly 194,014** (IPL: 87,687; T20I: 106,327). Total matches must equal **837** (IPL: 367; T20I: 470).
- **Failure Condition:** Any row dropped, filtered, or duplicated during scoring.

---

### Group 2: Edge-Case & Boundary Condition Handling

#### TEST 04: Early Delivery Bayesian Smoothing ($t < 12$ balls)
- **Scope:** Deliveries where `legal_balls_before < 12` (including ball 1 where `legal_balls_before == 0`).
- **Assertion:** `crr_shrinkage_before` must evaluate cleanly without division by zero. Pressure scores must stay within $[20.0, 60.0]$ under neutral conditions.
- **Failure Condition:** Division-by-zero error, `NaN` output, or unconstrained variance on early balls.

#### TEST 05: Extreme Raw RRR Graceful Saturation
- **Scope:** Deliveries in Innings 2 where `required_run_rate_before >= 24.0` (including astronomical values up to 810.0).
- **Assertion:** `batting_pressure_score` must lie strictly between $90.00$ and $100.00$. The sigmoidal transformation must saturate asymptotically without overflow.
- **Failure Condition:** Float overflow, infinite score, or non-saturated score ($< 90.0$).

#### TEST 06: Zero Balls Remaining / Impossible Chase (Synthetic Boundary Test)
- **Scope:** Synthetic unit fixture (SYN-08) testing edge condition where `legal_balls_remaining_before == 0` and `required_runs_before > 0`.
- **Policy Note:** Terminal states are not ordinary delivery-level observations; in actual cricket, matches end upon completion of legal balls. No historical delivery row is scored using post-innings information.
- **Assertion:** `batting_pressure_score == 100.00` and `bowling_pressure_score == 0.00` (terminal boundary: chase failed, bowling win secured).
- **Failure Condition:** Any division by zero, `NaN`, or non-boundary score.

#### TEST 07: Target Reached / Overshot Target (Synthetic Boundary Test)
- **Scope:** Synthetic unit fixture (SYN-09) testing edge condition where `required_runs_before <= 0` (target met or overshot).
- **Policy Note:** Terminal states are not ordinary delivery-level observations. In real cricket, matches conclude immediately when winning runs are scored on ball $t$; no delivery is bowled when target is already reached. Any anomalous delivery row is flagged with `is_target_met_delivery = True` for exclusion from player evaluation.
- **Assertion:** Both `batting_pressure_score == 0.00` and `bowling_pressure_score == 0.00` (terminal boundary: victory concluded).
- **Failure Condition:** Non-zero pressure when match is won.

#### TEST 08: DLS Shortened Match Resource Rescaling
- **Scope:** Deliveries belonging to rain-reduced matches (Match 21586, 37354, 54711, 21070).
- **Assertion:** Resource curves must scale against the innings-specific scheduled legal balls (`total_legal_balls < 120`). Overs fraction $f_{\text{bowled}} \le 1.0$ at all times.
- **Failure Condition:** Resource depletion exceeding 100% before match conclusion.

---

### Group 3: Innings Separation & Contextual Par Verification

#### TEST 09: Complete Absence of RRR in Innings 1
- **Scope:** All deliveries where `innings == 1`.
- **Assertion:** 
  1. `required_run_rate_before` is strictly `NaN`.
  2. `target` is strictly `NaN`.
  3. `rrr_bounded` is strictly `NaN`.
  4. Innings 1 pressure computation executes exclusively via Target-Setting components ($I_{\text{pace\_deficit}}, I_{\text{resource\_depletion}}, I_{\text{phase\_urgency}}$).
- **Failure Condition:** Any chase formula or non-NaN target leaking into Innings 1.

#### TEST 10: Format Baseline Assignment
- **Scope:** All deliveries.
- **Assertion:** 
  - Every IPL delivery must use $\text{PAR}_{\text{comp}} = 9.35$.
  - Every T20I delivery must use $\text{PAR}_{\text{comp}} = 8.59$.
- **Failure Condition:** Any misassigned baseline or static universal baseline.

---

### Group 4: Cricket Domain Monotonicity & Asymmetry

#### TEST 11: Batting Required Run Rate Monotonicity
- **Scope:** Synthetic comparison: Fix `innings = 2`, `balls_rem = 24`, `wickets = 4`. Vary required runs from $20$ to $60$ (RRR from $5.0$ to $15.0$).
- **Assertion:** $\frac{\partial P_{\text{bat}}}{\partial \text{req}} > 0$ strictly monotonic:
  $$P_{\text{bat}}(\text{RRR}=6.0) < P_{\text{bat}}(\text{RRR}=9.0) < P_{\text{bat}}(\text{RRR}=12.0) < P_{\text{bat}}(\text{RRR}=15.0)$$
- **Failure Condition:** Any decrease in batting pressure as required rate increases.

#### TEST 12: Batting Wicket Depletion Monotonicity
- **Scope:** Synthetic comparison: Fix `innings = 2`, `balls_rem = 30`, `req_runs = 45`. Vary wickets lost from $0$ to $8$.
- **Assertion:** $\frac{\partial P_{\text{bat}}}{\partial w} > 0$ strictly monotonic:
  $$P_{\text{bat}}(w=1) < P_{\text{bat}}(w=3) < P_{\text{bat}}(w=5) < P_{\text{bat}}(w=7)$$
- **Failure Condition:** Any decrease in batting pressure as wickets fall.

#### TEST 13: Tactical Asymmetry Inversion
- **Scope:** Canonical scenario comparison:
  1. **Tight Death Defense:** Innings 2, 6 balls remaining, 6 runs required, 5 wickets down.
  2. **Steep Chase Crisis:** Innings 2, 6 balls remaining, 30 runs required, 5 wickets down.
- **Assertion:**
  - In Scenario 1: $P_{\text{bowl}} > P_{\text{bat}}$ (Bowler has no runway; batter is comfortable).
  - In Scenario 2: $P_{\text{bat}} > P_{\text{bowl}}$ (Batter faces near-impossible task; bowler has huge cushion).
- **Failure Condition:** Bowler pressure $\le$ batter pressure in Scenario 1, or batter pressure $\le$ bowler pressure in Scenario 2.

---

### Group 5: Structural Anti-Leakage & Data Engineering Proofs

*Replaces legacy correlation tests with four mathematically rigorous software invariance tests.*

#### TEST 14: Feature Lineage & Static AST Audit
- **Scope:** Static code analysis of `src/features/match_state.py` and pressure computation functions.
- **Methodology:** Parse function syntax tree via Python `ast` module. Extract all dataframe column access nodes and dictionary lookups.
- **Assertion:** No prohibited post-delivery column appears in the dependency graph:
  $$\text{Prohibited} = \{\text{'runs'}, \text{'ball\_total\_runs'}, \text{'runs\_off\_bat'}, \text{'is\_wicket'}, \text{'is\_bowler\_wicket'}, \text{'is\_batter_out'}, \text{'dismissal_type'}, \text{'extras_type'}\}$$
- **Failure Condition:** Any prohibited column present in the feature calculation AST.

#### TEST 15: Prefix Invariance Test
- **Scope:** 50 randomly sampled delivery index points $t \in [1, 194014]$.
- **Methodology:** Slice the delivery dataframe to prefix $df[:t]$ and evaluate pressure on ball $t$. Compare against pressure computed on the entire dataset $df$.
- **Assertion:**
  $$P_{\text{bat, prefix}}(t) == P_{\text{bat, full}}(t) \quad \text{and} \quad P_{\text{bowl, prefix}}(t) == P_{\text{bowl, full}}(t)$$
- **Failure Condition:** Any difference $> 10^{-9}$ between prefix and full dataset calculations.

#### TEST 16: Future Invariance & Perturbation Test
- **Scope:** 50 randomly sampled match innings.
- **Methodology:** For delivery $t$, perturb all subsequent deliveries ($t+1 \dots T$) by modifying their runs, extras, and wickets with random integer noise. Re-run pressure calculation for delivery $t$.
- **Assertion:**
  $$\Delta P_{\text{bat}}(t) == 0.0000 \quad \text{and} \quad \Delta P_{\text{bowl}}(t) == 0.0000$$
- **Failure Condition:** Any change in delivery $t$'s pressure score when future deliveries are altered.

#### TEST 17: Production-Code Dependency Audit
- **Scope:** Runtime argument inspection of pressure engine function calls.
- **Assertion:** Assert that function signatures accept strictly pre-delivery state variables (`score_before`, `wickets_before`, `legal_balls_before`, `total_legal_balls`, `target`, `required_runs_before`, `par_comp`).
- **Failure Condition:** Any post-delivery outcome variable passed as an input argument.

---

### Group 6: Cross-Format Equity & Distribution Calibration

#### TEST 18: Inter-Format Distribution Balance
- **Scope:** IPL deliveries (87,687) vs T20I deliveries (106,327).
- **Assertion:** 
  $$|\text{Mean}(P_{\text{bat, IPL}}) - \text{Mean}(P_{\text{bat, T20I}})| \le 3.50 \text{ points}$$
  $$|\text{Mean}(P_{\text{bowl, IPL}}) - \text{Mean}(P_{\text{bowl, T20I}})| \le 3.50 \text{ points}$$
- **Failure Condition:** Systematic distributional skew between tournaments ($> 3.50$ points difference).

#### TEST 19: Categorical Tier Proportions
- **Scope:** Full dataset category distribution.
- **Assertion:** 
  - `Low` $[0, 40)$: $30\% - 45\%$ of deliveries.
  - `Moderate` $[40, 65)$: $25\% - 40\%$ of deliveries.
  - `High` $[65, 85)$: $15\% - 25\%$ of deliveries.
  - `Extreme` $[85, 100]$: $5\% - 15\%$ of deliveries.
- **Failure Condition:** Category starvation (e.g. Extreme $< 3\%$ or $> 20\%$).

---

### Group 7: Synthetic Unit Fixture Suite (10 Deterministic In-Memory Cases)

#### TEST 20: Permanent 10-Case Synthetic Fixture Suite
*All expected scores are recalculated directly from the existing methodology formulas without modification. Note: SYN-08 and SYN-09 represent synthetic terminal boundary tests for numerical resilience, not ordinary historical delivery observations.*

| Case ID | Format | Inn | Total Balls | Balls Rem | Wkts | Score | Target | Req Runs | RRR | Phase | Exact $P_{\text{bat}}$ | Exact $P_{\text{bowl}}$ |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **SYN-01** | IPL | 1 | 120 | 120 | 0 | 0 | None | None | None | Powerplay | **47.00** | **45.00** |
| **SYN-02** | IPL | 1 | 120 | 105 | 3 | 15 | None | None | None | Powerplay | **61.55** | **32.90** |
| **SYN-03** | IPL | 1 | 120 | 18 | 3 | 170 | None | None | None | Death | **43.35** | **67.43** |
| **SYN-04** | T20I | 2 | 120 | 60 | 1 | 100 | 160 | 60 | 6.00 | Middle | **18.04** | **60.36** |
| **SYN-05** | T20I | 2 | 120 | 6 | 6 | 152 | 160 | 8 | 8.00 | Death | **45.84** | **67.51** |
| **SYN-06** | IPL | 2 | 120 | 6 | 7 | 176 | 200 | 24 | 24.00 | Death | **100.00** | **23.52** |
| **SYN-07** | IPL | 2 | 120 | 1 | 8 | 178 | 200 | 22 | 132.00 | Death | **100.00** | **19.08** |
| **SYN-08** | T20I | 2 | 120 | 0 | 7 | 155 | 160 | 5 | NaN | Death | **100.00** | **0.00** |
| **SYN-09** | IPL | 2 | 120 | 12 | 4 | 200 | 200 | 0 | 0.00 | Death | **0.00** | **0.00** |
| **SYN-10** | T20I | 2 | 30 | 18 | 5 | 20 | 55 | 35 | 11.67 | Middle | **64.03** | **36.88** |

#### Step-by-Step Mathematical Evidence for Synthetic Assertions:

1. **SYN-01 (IPL Inn 1, Ball 1):**
   - $\text{CRR}_{\text{adj}} = \frac{0 + 9.35 \times 2}{0 + 2} = 9.35 \implies I_{\text{pace}} = 50.00$.
   - $W_{\text{exp}} = 6.0 \times 0^{0.8} = 0.0 \implies \Delta_{\text{wkt}} = 0 \implies I_{\text{res}} = 50.00$.
   - $I_{\text{phase}} = 35.00$.
   - $P_{\text{bat}} = 0.45(50) + 0.35(50) + 0.20(35) = \mathbf{47.00}$.
   - $I_{\text{cont}} = 50.00, I_{\text{drought}} = 50.00, I_{\text{death}} = 30.00 \implies P_{\text{bowl}} = 0.40(50) + 0.35(50) + 0.25(30) = \mathbf{45.00}$.

2. **SYN-02 (IPL Inn 1, 15/3 after 15 balls):**
   - $\text{CRR}_{\text{adj}} = \frac{15 + 18.7}{2.5 + 2} = 7.489 \implies I_{\text{pace}} = 50 + 7.5(9.35 - 7.489) = 63.96$.
   - $W_{\text{exp}} = 6.0(15/120)^{0.8} = 1.137 \implies \Delta_{\text{wkt}} = 1.863 \implies I_{\text{res}} = 50 + 12(1.863) = 72.36$.
   - $I_{\text{phase}} = 35 + 50(15/120)^{1.5} = 37.21$.
   - $P_{\text{bat}} = 0.45(63.96) + 0.35(72.36) + 0.20(37.21) = \mathbf{61.55}$.
   - $I_{\text{cont}} = 36.04, I_{\text{drought}} = 31.37, I_{\text{death}} = 30.00 \implies P_{\text{bowl}} = 0.40(36.04) + 0.35(31.37) + 0.25(30) = \mathbf{32.90}$.

3. **SYN-03 (IPL Inn 1, 170/3 after 102 balls):**
   - $\text{CRR}_{\text{adj}} = \frac{170 + 18.7}{17 + 2} = 9.932 \implies I_{\text{pace}} = 45.64$.
   - $W_{\text{exp}} = 6.0(102/120)^{0.8} = 5.268 \implies \Delta_{\text{wkt}} = -2.268 \implies I_{\text{res}} = 22.78$.
   - $I_{\text{phase}} = 35 + 50(102/120)^{1.5} = 74.18$.
   - $P_{\text{bat}} = 0.45(45.64) + 0.35(22.78) + 0.20(74.18) = \mathbf{43.35}$.
   - $I_{\text{cont}} = 54.36, I_{\text{drought}} = 72.68, I_{\text{death}} = 75 + 15(12/30) = 81.00 \implies P_{\text{bowl}} = \mathbf{67.43}$.

4. **SYN-04 (T20I Inn 2, 60 balls rem, 1 wkt, 100/1 chasing 160, RRR 6.0):**
   - $S_{\text{RRR}} = \frac{100}{1 + \exp(-0.35(6.0 - 8.59))} = 28.77$.
   - $I_{\text{wkt}} = 100(1/10)^{1.35} = 4.47, f_{\text{bowled}} = 0.5 \implies M_{\text{crunch}} = 0.9469$.
   - $P_{\text{bat}} = [0.60(28.77) + 0.40(4.47)] \times 0.9469 = \mathbf{18.04}$.
   - $\text{RPB} = 1.0 \implies I_{\text{runway}} = 82.50, I_{\text{boundary}} = 0.0, I_{\text{depth}} = 95.53 \implies P_{\text{bowl}} = \mathbf{60.36}$.

5. **SYN-05 (T20I Inn 2, 6 balls rem, 6 wkts, 8 needed, RRR 8.0):**
   - $S_{\text{RRR}} = 44.86, I_{\text{wkt}} = 50.18, f_{\text{bowled}} = 0.95 \implies M_{\text{crunch}} = 0.9756$.
   - $P_{\text{bat}} = [0.60(44.86) + 0.40(50.18)] \times 0.9756 = \mathbf{45.84}$.
   - $\text{RPB} = 1.333 \implies I_{\text{runway}} = 70.83, \text{Boundaries} = 1.75 \implies I_{\text{boundary}} = 73.75, I_{\text{depth}} = 49.82 \implies P_{\text{bowl}} = \mathbf{67.51}$.

6. **SYN-06 (IPL Inn 2, 6 balls rem, 7 wkts, 24 needed, RRR 24.0):**
   - $S_{\text{RRR}} = 99.41, I_{\text{wkt}} = 61.78, M_{\text{crunch}} = 1.2816 \implies P_{\text{bat}} = \min(108.11, 100.0) = \mathbf{100.00}$.
   - $\text{RPB} = 4.0 \implies I_{\text{runway}} = 23.50, I_{\text{boundary}} = 13.75, I_{\text{depth}} = 38.22 \implies P_{\text{bowl}} = \mathbf{23.52}$.

7. **SYN-07 (IPL Inn 2, 1 ball rem, 8 wkts, 22 needed, RRR 132.0):**
   - $S_{\text{RRR}} = 100.00, I_{\text{wkt}} = 73.99, M_{\text{crunch}} = 1.297 \implies P_{\text{bat}} = \min(116.20, 100.0) = \mathbf{100.00}$.
   - $\text{RPB} = 22.0 \implies I_{\text{runway}} = 15.00, I_{\text{boundary}} = 21.25, I_{\text{depth}} = 26.01 \implies P_{\text{bowl}} = \mathbf{19.08}$.

8. **SYN-08 (T20I Inn 2, 0 balls rem, 5 needed, Terminal Impossible):**
   - $P_{\text{bat}} = \mathbf{100.00}, P_{\text{bowl}} = \mathbf{0.00}$.

9. **SYN-09 (IPL Inn 2, 12 balls rem, 0 needed, Terminal Won):**
   - $P_{\text{bat}} = \mathbf{0.00}, P_{\text{bowl}} = \mathbf{0.00}$.

10. **SYN-10 (T20I Inn 2 DLS 30 balls, 18 balls rem, 5 wkts, 35 needed, RRR 11.67):**
    - $S_{\text{RRR}} = 74.61, I_{\text{wkt}} = 39.23, f_{\text{bowled}} = 12/30 = 0.40 \implies M_{\text{crunch}} = 1.059$.
    - $P_{\text{bat}} = [0.60(74.61) + 0.40(39.23)] \times 1.059 = \mathbf{64.03}$.
    - $\text{RPB} = 1.944 \implies I_{\text{runway}} = 49.44, I_{\text{boundary}} = 0.0, I_{\text{depth}} = 60.77 \implies P_{\text{bowl}} = \mathbf{36.88}$.

---

### Group 8: Weight Sensitivity & Ranking Robustness

#### TEST 21: Monte Carlo Weight Perturbation Analysis
- **Methodology:** Perturb the proposed indicator weights by $\pm 10\%$ and $\pm 20\%$ using 50 randomized iterations.
- **Assertion:** Spearman rank-order correlation ($r_s$) between base pressure scores and perturbed scores must satisfy:
  $$r_s \ge 0.95$$
- **Purpose:** Formally proves that the methodology is mathematically stable and not sensitive to minor weight calibrations.

---

## 4. Validation Plan Change Log & Unresolved Assumptions

### Validation Plan Change Log
- **v1.0 to v2.0:**
  1. Recalculated all 10 synthetic fixture expected scores to 2 decimal places using the exact methodology formulas, resolving previous heuristic mismatches.
  2. Removed legacy correlation-based tests ($|r| < 0.03$) and added four structural data-engineering invariance tests (Feature Lineage, Prefix Invariance, Future Invariance, and Dependency Audits).
  3. Formally incorporated terminal target-reached and zero-ball states into test specifications.
  4. Explicitly stated proposed status of sigmoid parameters and category cutoffs.

### Unresolved Validation Assumptions (To Be Finalized in Task 04.2)
1. **Sampling Size for Invariance Tests:** 50 sampled prefixes and innings will be tested initially; runtime impact on large-scale regression runs will determine if full-dataset testing is viable.
2. **Monte Carlo Random Seed:** Seed 42 will be permanently fixed to ensure 100% deterministic reproducibility of sensitivity analysis.
