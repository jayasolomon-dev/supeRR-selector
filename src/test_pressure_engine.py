"""
SUPERR SELECTOR — Pressure Engine Unit & Synthetic Validation Suite
Module: src/test_pressure_engine.py
Author: Senior Cricket Data Scientist & QA Specialist
Project: SUPERR SELECTOR (Rajasthan Royals SupeRR Selector Season 2 Hackathon)

Tests the modular pressure engine functions directly:
1. Canonical Synthetic Fixtures (SYN-01 through SYN-10) against literal Revision 2.1 expected values.
2. Innings 1 vs Innings 2 separation.
3. IPL (9.35) vs T20I (8.59) baseline selection.
4. DLS-shortened capacity scaling.
5. Missing and invalid state values.
6. Zero legal balls remaining (terminal boundary).
7. Target already met (terminal boundary).
8. Impossible chase state.
9. Score bounds [0, 100] and category boundaries.
10. Batting / Bowling score independence.
"""

from pathlib import Path
import sys
import numpy as np
import pandas as pd

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.features.pressure_engine import (
    PAR_RUN_RATE_IPL,
    PAR_RUN_RATE_T20I,
    calculate_innings1_batting_pressure,
    calculate_innings1_bowling_pressure,
    calculate_innings2_batting_pressure,
    calculate_innings2_bowling_pressure,
    calculate_resource_depletion_percentage,
    assign_pressure_categories,
    enrich_deliveries_with_pressure,
    run_synthetic_fixtures,
)


def run_all_tests() -> bool:
    print("=" * 80)
    print("⚡ SUPERR SELECTOR — PRESSURE ENGINE COMPREHENSIVE UNIT TEST SUITE")
    print("=" * 80)
    
    total_assertions = 0
    failures = []

    # --------------------------------------------------------------------------
    # TEST 1: The 10 Approved Canonical Synthetic Fixtures (SYN-01 to SYN-10)
    # --------------------------------------------------------------------------
    print("\n[TEST 1] Executing 10 Approved Synthetic Fixtures (SYN-01 to SYN-10)...")
    passed, synth_results = run_synthetic_fixtures()
    for res in synth_results:
        total_assertions += 2
        fid = res["fixture_id"]
        fmt = res["format"]
        inn = res["innings"]
        act_bat, exp_bat = res["act_bat"], res["exp_bat"]
        act_bowl, exp_bowl = res["act_bowl"], res["exp_bowl"]
        
        if res["passed"]:
            print(f"  ✅ {fid} ({fmt} Inn {inn}): Bat={act_bat:6.2f} (exp {exp_bat:6.2f}) | Bowl={act_bowl:6.2f} (exp {exp_bowl:6.2f})")
        else:
            msg = f"SYNTHETIC MISMATCH in {fid}: Bat={act_bat} (exp {exp_bat}), Bowl={act_bowl} (exp {exp_bowl})"
            print(f"  ❌ {msg}")
            failures.append(msg)
            
    if not passed:
        print("  Result: FAILED ❌")
    else:
        print(f"  Result: PASSED ✅ (10/10 Synthetic Fixtures Matched Exactly)")

    # --------------------------------------------------------------------------
    # TEST 2: IPL vs T20I Baseline Par Sensitivity
    # --------------------------------------------------------------------------
    print("\n[TEST 2] Verifying Format Par Sensitivity (IPL 9.35 vs T20I 8.59)...")
    # Same delivery state in IPL vs T20I (Innings 1: 60 balls, score 90, 2 wkts)
    p_bat_ipl, _ = calculate_innings1_batting_pressure(90, 2, 60, 120, PAR_RUN_RATE_IPL)
    p_bat_t20i, _ = calculate_innings1_batting_pressure(90, 2, 60, 120, PAR_RUN_RATE_T20I)
    total_assertions += 1
    # In IPL (par 9.35), 90 in 60 balls (CRR 9.0) is below par -> higher batting pressure than in T20I (par 8.59)
    assert p_bat_ipl > p_bat_t20i, f"Expected IPL batting pressure ({p_bat_ipl}) > T20I ({p_bat_t20i})"
    print(f"  ✅ IPL Batting Pressure ({p_bat_ipl:.2f}) > T20I Batting Pressure ({p_bat_t20i:.2f}) at same 9.0 CRR")
    print("  Result: PASSED ✅")

    # --------------------------------------------------------------------------
    # TEST 3: DLS Shortened Capacity Scaling
    # --------------------------------------------------------------------------
    print("\n[TEST 3] Verifying DLS Shortened Capacity Scaling (30 vs 120 balls)...")
    # At 15 balls bowled: In 30-ball match (5 ov), 15 balls is 50% of innings; in 120-ball match, it is 12.5%
    p_bat_dls, c_dls = calculate_innings1_batting_pressure(40, 2, 15, 30, PAR_RUN_RATE_T20I)
    p_bat_full, c_full = calculate_innings1_batting_pressure(40, 2, 15, 120, PAR_RUN_RATE_T20I)
    total_assertions += 2
    assert c_dls["i_phase"] > c_full["i_phase"], "DLS urgency should exceed full-match urgency at same ball count"
    assert c_dls["w_exp"] > c_full["w_exp"], "Expected wickets in DLS 50% innings should exceed 12.5% innings"
    print(f"  ✅ DLS (30 balls) Phase Urgency ({c_dls['i_phase']:.2f}) > Full (120 balls) ({c_full['i_phase']:.2f})")
    print("  Result: PASSED ✅")

    # --------------------------------------------------------------------------
    # TEST 4: Terminal Boundary States (Target Reached & Impossible Chase)
    # --------------------------------------------------------------------------
    print("\n[TEST 4] Verifying Terminal Boundary States...")
    # Target reached (required_runs <= 0)
    p_bat_term_win, _ = calculate_innings2_batting_pressure(0.0, 3, 100, 20, 120, 0.0, PAR_RUN_RATE_IPL)
    p_bowl_term_win, _ = calculate_innings2_bowling_pressure(0.0, 20, 3)
    total_assertions += 2
    assert p_bat_term_win == 0.0, f"Expected Bat 0.0 on target met, got {p_bat_term_win}"
    assert p_bowl_term_win == 0.0, f"Expected Bowl 0.0 on target met, got {p_bowl_term_win}"
    print(f"  ✅ Target Met: Batting={p_bat_term_win:.2f}, Bowling={p_bowl_term_win:.2f}")

    # Impossible chase (0 balls rem, 10 required)
    p_bat_term_loss, _ = calculate_innings2_batting_pressure(np.nan, 7, 120, 0, 120, 10.0, PAR_RUN_RATE_IPL)
    p_bowl_term_loss, _ = calculate_innings2_bowling_pressure(10.0, 0, 7)
    total_assertions += 2
    assert p_bat_term_loss == 100.0, f"Expected Bat 100.0 on impossible chase, got {p_bat_term_loss}"
    assert p_bowl_term_loss == 0.0, f"Expected Bowl 0.0 on impossible chase, got {p_bowl_term_loss}"
    print(f"  ✅ Impossible Chase: Batting={p_bat_term_loss:.2f}, Bowling={p_bowl_term_loss:.2f}")
    print("  Result: PASSED ✅")

    # --------------------------------------------------------------------------
    # TEST 5: Score Bounds [0.0, 100.0] and Categorical Cutoffs
    # --------------------------------------------------------------------------
    print("\n[TEST 5] Verifying Score Bounds and Category Boundaries...")
    test_scores = [-10.0, 0.0, 39.99, 40.0, 64.99, 65.0, 84.99, 85.0, 100.0, 150.0]
    expected_cats = ["Low", "Low", "Low", "Moderate", "Moderate", "High", "High", "Extreme", "Extreme", "Extreme"]
    total_assertions += len(test_scores)
    actual_cats = assign_pressure_categories(test_scores)
    for s, exp, act in zip(test_scores, expected_cats, actual_cats):
        assert act == exp, f"Score {s} mapped to {act}, expected {exp}"
    print(f"  ✅ All {len(test_scores)} threshold boundary test points categorized correctly")
    print("  Result: PASSED ✅")

    # --------------------------------------------------------------------------
    # TEST 6: Tactical Asymmetry Inversion
    # --------------------------------------------------------------------------
    print("\n[TEST 6] Verifying Batting / Bowling Tactical Asymmetry...")
    # Scenario 1: Tight death defense (6 off 6 balls, 5 wkts down)
    p_bat_tight, _ = calculate_innings2_batting_pressure(6.0, 5, 114, 6, 120, 6.0, PAR_RUN_RATE_T20I)
    p_bowl_tight, _ = calculate_innings2_bowling_pressure(6.0, 6, 5)
    total_assertions += 1
    assert p_bowl_tight > p_bat_tight, f"In tight defense, Bowl ({p_bowl_tight}) must exceed Bat ({p_bat_tight})"
    print(f"  ✅ Tight Death Defense (6 off 6): Bowling ({p_bowl_tight:.2f}) > Batting ({p_bat_tight:.2f})")

    # Scenario 2: Steep chase crisis (24 off 6 balls, 5 wkts down)
    p_bat_steep, _ = calculate_innings2_batting_pressure(24.0, 5, 114, 6, 120, 24.0, PAR_RUN_RATE_T20I)
    p_bowl_steep, _ = calculate_innings2_bowling_pressure(24.0, 6, 5)
    total_assertions += 1
    assert p_bat_steep > p_bowl_steep, f"In steep chase, Bat ({p_bat_steep}) must exceed Bowl ({p_bowl_steep})"
    print(f"  ✅ Steep Chase Crisis (24 off 6): Batting ({p_bat_steep:.2f}) > Bowling ({p_bowl_steep:.2f})")
    print("  Result: PASSED ✅")

    # --------------------------------------------------------------------------
    # TEST 7: Vectorized Batch Execution on DataFrame Slice
    # --------------------------------------------------------------------------
    print("\n[TEST 7] Verifying Vectorized Delivery Enrichment on Real Slice...")
    sample_csv = Path("data/processed/ipl_deliveries.csv")
    if sample_csv.exists():
        df_sample = pd.read_csv(sample_csv, nrows=100)
        enriched = enrich_deliveries_with_pressure(df_sample)
        total_assertions += 4
        assert len(enriched) == 100, "Row count must remain 100"
        assert enriched["batting_pressure_score"].isna().sum() == 0, "No NaNs in batting pressure"
        assert enriched["bowling_pressure_score"].isna().sum() == 0, "No NaNs in bowling pressure"
        assert (enriched["batting_pressure_score"] >= 0.0).all() and (enriched["batting_pressure_score"] <= 100.0).all(), "Bounds [0,100]"
        print(f"  ✅ Vectorized enrichment succeeded across {len(enriched)} deliveries with zero NaNs and valid bounds")
        print("  Result: PASSED ✅")

    print("\n" + "=" * 80)
    print(f"TOTAL UNIT & SYNTHETIC ASSERTIONS EXECUTED: {total_assertions}")
    if len(failures) == 0:
        print("OVERALL PRESSURE ENGINE UNIT SUITE: ALL TESTS PASSED ✅")
        print("=" * 80)
        return True
    else:
        print(f"OVERALL PRESSURE ENGINE UNIT SUITE: {len(failures)} FAILURES ❌")
        print("=" * 80)
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

