# ⚡ T20 Match-State & Pressure Detection Engine Documentation

> **Module:** `src/features/match_state.py`  
> **Unit Tests:** `tests/test_match_state.py` (8/8 Passed)  
> **Dataset Verified:** `ball_by_ball.csv` (200,999 deliveries, 883 matches)  
> **Execution Speed:** 2.5 seconds vectorized for the entire dataset  

---

## 1. Theoretical Architecture & Core Objectives

The **Match-State & Pressure Detection Engine** reconstructs the exact state of a T20 match immediately **prior to every single delivery**.

### Absolute Guarantee: Zero Future-Data Leakage
To ensure strict econometric and machine learning integrity:
- Every feature marked with suffix `_before` (`score_before`, `wickets_before`, `legal_balls_remaining_before`, `required_runs_before`, `required_run_rate_before`, `current_run_rate_before`, `pressure_score_before`) is computed strictly from events occurring between ball $0$ and ball $t-1$.
- The outcome of delivery $t$ (runs, boundaries, extras, wickets) is strictly unknown at delivery $t$.

---

## 2. Reconstructed Match-State Variables

Before delivery $t$, the engine computes:

1. **`score_before` (int):** Cumulative team runs scored prior to delivery $t$ in that innings.
   $$\text{score\_before}_t = \sum_{k=0}^{t-1} (\text{runs}_k + \text{extras1\_runs}_k + \text{extras\_2\_runs}_k)$$
2. **`wickets_before` (int):** Total wickets fallen in that innings prior to delivery $t$.
   $$\text{wickets\_before}_t = \sum_{k=0}^{t-1} \mathbb{I}(\text{is\_wicket}_k == \text{True})$$
3. **`legal_balls_bowled_before` (int):** Total legal deliveries bowled prior to delivery $t$.
   $$\text{legal\_balls\_bowled\_before}_t = \sum_{k=0}^{t-1} \mathbb{I}(\text{extras\_type}_k \notin \{\text{'wide'}, \text{'overstep'}\})$$
4. **`legal_balls_remaining_before` (int):**
   $$\text{legal\_balls\_remaining\_before}_t = \max\left(0, \text{total\_legal\_balls} - \text{legal\_balls\_bowled\_before}_t\right)$$
5. **`target` (float/int):**
   - **Innings 1:** `NaN` (setting target).
   - **Innings 2:** $\text{revised\_target}$ from `matches.csv` (if DLS match) or $\text{Innings 1 Final Score} + 1$.
6. **`required_runs_before` (float/int):**
   - **Innings 1:** `NaN`.
   - **Innings 2:** $\max(0, \text{target} - \text{score\_before}_t)$.
7. **`required_run_rate_before` (float):**
   - **Innings 1:** `NaN`.
   - **Innings 2:** If $\text{legal\_balls\_remaining} > 0$:
     $$RRR = \frac{\text{required\_runs\_before}}{\text{legal\_balls\_remaining\_before}} \times 6.0$$
     - If $\text{required\_runs} \le 0$: $RRR = 0.0$ (target reached).
     - If $\text{legal\_balls\_remaining} == 0$ and runs needed $> 0$: $RRR = 36.0$ (capped).
8. **`current_run_rate_before` (float):**
   $$CRR = \begin{cases} \frac{\text{score\_before}}{\text{legal\_balls\_bowled\_before}} \times 6.0 & \text{if legal balls bowled} > 0 \\ 0.0 & \text{otherwise} \end{cases}$$
9. **`pressure_score_before` (float):** Continuous, reproducible index bounded in $[0.0, 100.0]$.

---

## 3. Mathematical Formulation of the Pressure Score

The pressure score models psychological and tactical tension on a continuous $[0, 100]$ scale.

### 3.1 Innings 2 (The Run Chase)
In the 2nd innings, pressure is governed by the Required Run Rate ($RRR$), available wickets, and the fraction of the innings completed ($f_{\text{bowled}} = \frac{\text{legal\_balls\_bowled}}{\text{total\_legal\_balls}}$).

1. **Base RRR Sigmoid ($P_{\text{base}}$):**
   Centered at the empirical T20 median par run rate ($RR_{\text{par}} = 8.5$ RPO):
   $$P_{\text{base}} = \frac{100.0}{1.0 + \exp\left(-0.45 \cdot (RRR - 8.5)\right)}$$
2. **Wicket Depletion Multiplier ($W_{\text{mult}}$):**
   Reflects batting resource scarcity (from 0.80 at 0 wickets to 1.40 at 9 wickets):
   $$W_{\text{mult}} = 0.80 + 0.60 \cdot \left(\frac{\text{wickets\_lost}}{10.0}\right)^{1.25}$$
3. **Urgency / Time Leverage Multiplier ($U_{\text{mult}}$):**
   As balls run out, high RRR creates exponential stress, while low RRR provides comfort:
   $$U_{\text{mult}} = \begin{cases} 
   1.0 + 0.35 \cdot f_{\text{bowled}} \cdot \min\left(2.0, \frac{RRR - 8.5}{8.5}\right) & \text{if } RRR > 8.5 \\
   1.0 - 0.20 \cdot f_{\text{bowled}} \cdot \min\left(1.0, \frac{8.5 - RRR}{8.5}\right) & \text{if } RRR \le 8.5
   \end{cases}$$
4. **Composite Innings 2 Pressure:**
   $$\text{Pressure} = \text{clip}\left(P_{\text{base}} \cdot W_{\text{mult}} \cdot U_{\text{mult}}, 0.0, 100.0\right)$$
   *(If $\text{required\_runs} \le 0$, $\text{Pressure} = 0.0$).*

### 3.2 Innings 1 (Target Setting)
In the 1st innings, pressure is driven by pacing against benchmark T20 totals and early wicket preservation.

1. **Pace Deficit ($P_{\text{pace}}$):**
   $$\text{Deficit} = 8.5 - CRR$$
   $$P_{\text{pace}} = \begin{cases} 45.0 & \text{if legal balls bowled} < 12 \\ \text{clip}(50.0 + \text{Deficit} \cdot 4.5, 15.0, 85.0) & \text{otherwise} \end{cases}$$
2. **Wicket Depletion vs Par ($W_{\text{adj}}$):**
   $$\text{Expected Wickets} = 6.5 \cdot \left(f_{\text{bowled}}\right)^{0.85}$$
   $$W_{\text{adj}} = (\text{wickets\_lost} - \text{Expected Wickets}) \cdot 6.5$$
3. **Death Phase Urgency:** $+5.0$ bump during final 5 overs ($f_{\text{bowled}} \ge 0.75$).
4. **Composite Innings 1 Pressure:**
   $$\text{Pressure} = \text{clip}\left(P_{\text{pace}} + W_{\text{adj}} + \text{Death Bump}, 0.0, 100.0\right)$$

---

## 4. Handling of Edge Cases

| Event / Scenario | Engine Handling | Integrity Verification |
| :--- | :--- | :--- |
| **Wides (`extras_type == 'wide'`)** | Score increases by `extras1_runs + extras_2_runs`. Legal ball count does **NOT** increment. Balls remaining does not change. | Verified in unit test `test_legal_ball_counting` |
| **No-Balls (`extras_type == 'Overstep'`)** | Score increases by `runs + extras1_runs + extras_2_runs`. Legal ball count does **NOT** increment. | Verified in unit test `test_legal_ball_counting` |
| **Byes / Leg-byes** | Score increases by `extras1_runs`. Delivery **is legal** and increments legal ball count. | Verified in unit test `test_ball_runs_calculation` |
| **Wickets (`is_wicket == True`)** | `wickets_before` for the *next* delivery increments by 1. Current delivery retains prior wicket count. | Verified in unit test `test_wicket_accumulation` |
| **Innings Reset** | Innings 2 starts at `score_before = 0`, `wickets_before = 0`, `legal_balls_bowled = 0`. Target is resolved. | Verified in unit test `test_innings_transition_and_target_setting` |
| **Shortened Matches (DLS)** | Reads `first_inn_revised_overs` & `second_inn_revised_overs` from `matches.csv` (in balls). Reads `revised_target`. | Verified in unit test `test_revised_target_and_shortened_matches` and real IPL 2023 final match 21586 |
| **Target Reached Early** | When `score_before >= target`, `required_runs_before = 0`, `rrr_before = 0.0`, `pressure_score_before = 0.0`. | Verified in unit test `test_pressure_score_bounds_and_behavior` |

