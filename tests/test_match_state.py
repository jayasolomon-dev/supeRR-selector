"""
Unit tests for T20 Match-State & Pressure Detection Engine.
Verifies prior score reconstruction, legal ball counting, extras handling,
innings reset, shortened matches, and pressure index monotonicity.
"""

import unittest
import pandas as pd
import numpy as np

from src.features.match_state import (
    reconstruct_match_states,
    calculate_ball_runs,
    identify_legal_deliveries,
    compute_innings_pressure_vectorized,
)


class TestMatchStateEngine(unittest.TestCase):

    def setUp(self):
        """Create controlled synthetic ball-by-ball sequence for deterministic testing."""
        # Innings 1: 5 deliveries (dot, four, wide, six off no-ball, wicket)
        self.inn1_deliveries = pd.DataFrame([
            {"match_id": 101, "innings": 1, "overid": 1, "over_ball_num": 1, "runs": 0, "extras_type": "None", "extras1_runs": 0, "extras_2_runs": 0, "is_wicket": False},
            {"match_id": 101, "innings": 1, "overid": 1, "over_ball_num": 2, "runs": 4, "extras_type": "None", "extras1_runs": 0, "extras_2_runs": 0, "is_wicket": False},
            {"match_id": 101, "innings": 1, "overid": 1, "over_ball_num": 3, "runs": 0, "extras_type": "wide", "extras1_runs": 1, "extras_2_runs": 0, "is_wicket": False},
            {"match_id": 101, "innings": 1, "overid": 1, "over_ball_num": 3, "runs": 6, "extras_type": "Overstep", "extras1_runs": 1, "extras_2_runs": 0, "is_wicket": False},
            {"match_id": 101, "innings": 1, "overid": 1, "over_ball_num": 3, "runs": 0, "extras_type": "None", "extras1_runs": 0, "extras_2_runs": 0, "is_wicket": True},
        ])

        # Innings 2: 4 deliveries (target chase)
        self.inn2_deliveries = pd.DataFrame([
            {"match_id": 101, "innings": 2, "overid": 1, "over_ball_num": 1, "runs": 1, "extras_type": "None", "extras1_runs": 0, "extras_2_runs": 0, "is_wicket": False},
            {"match_id": 101, "innings": 2, "overid": 1, "over_ball_num": 2, "runs": 0, "extras_type": "legbyes", "extras1_runs": 4, "extras_2_runs": 0, "is_wicket": False},
            {"match_id": 101, "innings": 2, "overid": 1, "over_ball_num": 3, "runs": 6, "extras_type": "None", "extras1_runs": 0, "extras_2_runs": 0, "is_wicket": False},
            {"match_id": 101, "innings": 2, "overid": 1, "over_ball_num": 4, "runs": 2, "extras_type": "None", "extras1_runs": 0, "extras_2_runs": 0, "is_wicket": False},
        ])

        self.full_match_df = pd.concat([self.inn1_deliveries, self.inn2_deliveries], ignore_index=True)

    def test_ball_runs_calculation(self):
        """Verify total team runs per delivery includes bat runs and extras."""
        ball_runs = calculate_ball_runs(self.inn1_deliveries)
        # Expected:
        # ball 0: 0
        # ball 1: 4
        # ball 2 (wide): 0 + 1 + 0 = 1
        # ball 3 (no-ball with 6): 6 + 1 + 0 = 7
        # ball 4 (wicket dot): 0
        expected = [0, 4, 1, 7, 0]
        self.assertEqual(ball_runs.tolist(), expected)

    def test_legal_delivery_identification(self):
        """Verify wides and oversteps are classified as illegal deliveries."""
        is_legal = identify_legal_deliveries(self.inn1_deliveries["extras_type"])
        # Expected: True, True, False (wide), False (Overstep), True
        expected = [True, True, False, False, True]
        self.assertEqual(is_legal.tolist(), expected)

    def test_score_reconstruction_no_future_leakage(self):
        """Verify score_before strictly represents cumulative runs prior to delivery t."""
        df_recon = reconstruct_match_states(self.inn1_deliveries)
        
        # Ball 0: score before is 0
        self.assertEqual(df_recon.loc[0, "score_before"], 0)
        # Ball 1: score before is 0 (first ball was 0)
        self.assertEqual(df_recon.loc[1, "score_before"], 0)
        # Ball 2 (wide): score before is 4 (ball 1 was 4)
        self.assertEqual(df_recon.loc[2, "score_before"], 4)
        # Ball 3 (no-ball): score before is 5 (4 + 1 from wide)
        self.assertEqual(df_recon.loc[3, "score_before"], 5)
        # Ball 4 (wicket): score before is 12 (5 + 7 from no-ball)
        self.assertEqual(df_recon.loc[4, "score_before"], 12)

    def test_legal_ball_counting(self):
        """Verify legal balls remaining correctly skips wides and no-balls."""
        df_recon = reconstruct_match_states(self.inn1_deliveries)
        
        # Total legal balls for T20 = 120
        # Ball 0: 0 bowled, 120 remaining
        self.assertEqual(df_recon.loc[0, "legal_balls_bowled_before"], 0)
        self.assertEqual(df_recon.loc[0, "legal_balls_remaining_before"], 120)
        
        # Ball 1: 1 bowled (ball 0 was legal), 119 remaining
        self.assertEqual(df_recon.loc[1, "legal_balls_bowled_before"], 1)
        self.assertEqual(df_recon.loc[1, "legal_balls_remaining_before"], 119)
        
        # Ball 2 (wide): 2 bowled, 118 remaining
        self.assertEqual(df_recon.loc[2, "legal_balls_bowled_before"], 2)
        self.assertEqual(df_recon.loc[2, "legal_balls_remaining_before"], 118)
        
        # Ball 3 (no-ball): STILL 2 bowled (wide did not advance legal ball count!)
        self.assertEqual(df_recon.loc[3, "legal_balls_bowled_before"], 2)
        self.assertEqual(df_recon.loc[3, "legal_balls_remaining_before"], 118)
        
        # Ball 4 (wicket): STILL 2 bowled (no-ball did not advance legal ball count!)
        self.assertEqual(df_recon.loc[4, "legal_balls_bowled_before"], 2)
        self.assertEqual(df_recon.loc[4, "legal_balls_remaining_before"], 118)

    def test_wicket_accumulation(self):
        """Verify wickets_before increments only after a wicket is taken."""
        df_recon = reconstruct_match_states(self.inn1_deliveries)
        # Before ball 4 (where wicket falls), wickets_before is 0
        self.assertEqual(df_recon.loc[4, "wickets_before"], 0)

    def test_innings_transition_and_target_setting(self):
        """Verify Innings 2 starts fresh at score 0, with target = Innings 1 + 1."""
        df_recon = reconstruct_match_states(self.full_match_df)
        
        # Innings 1 final score was 12 runs
        # Target for Innings 2 should be 12 + 1 = 13 runs
        inn2_start = df_recon[df_recon["innings"] == 2].iloc[0]
        self.assertEqual(inn2_start["score_before"], 0)
        self.assertEqual(inn2_start["wickets_before"], 0)
        self.assertEqual(inn2_start["legal_balls_bowled_before"], 0)
        self.assertEqual(inn2_start["target"], 13)
        self.assertEqual(inn2_start["required_runs_before"], 13)

    def test_revised_target_and_shortened_matches(self):
        """Verify DLS shortened matches respect revised_target and revised_overs."""
        matches_mock = pd.DataFrame([{
            "match_id": 101,
            "first_inn_revised_overs": 30.0,    # 5 overs = 30 balls
            "second_inn_revised_overs": 30.0,   # 5 overs = 30 balls
            "revised_target": 45.0,             # Target is 45
        }])

        df_recon = reconstruct_match_states(self.full_match_df, df_matches=matches_mock)
        
        # Check Innings 1 total legal balls is 30
        inn1_start = df_recon.iloc[0]
        self.assertEqual(inn1_start["total_legal_balls"], 30)
        self.assertEqual(inn1_start["legal_balls_remaining_before"], 30)

        # Check Innings 2 target is 45 and max balls is 30
        inn2_start = df_recon[df_recon["innings"] == 2].iloc[0]
        self.assertEqual(inn2_start["target"], 45)
        self.assertEqual(inn2_start["required_runs_before"], 45)
        self.assertEqual(inn2_start["total_legal_balls"], 30)
        self.assertEqual(inn2_start["legal_balls_remaining_before"], 30)

    def test_pressure_score_bounds_and_behavior(self):
        """Verify pressure score stays bounded [0, 100] and increases monotonically with RRR and wickets."""
        # Test 1: Low pressure cruise chase (RRR = 4.0, 0 wickets, 20 balls left, 13 needed)
        p_low = compute_innings_pressure_vectorized(
            innings_num=2,
            crr=np.array([8.0]),
            rrr=np.array([4.0]),
            wickets_before=np.array([0]),
            legal_balls_bowled=np.array([100]),
            legal_balls_remaining=np.array([20]),
            total_legal_balls=np.array([120]),
            required_runs=np.array([13]),
        )[0]

        # Test 2: High pressure chase (RRR = 14.0, 7 wickets, 12 balls left, 28 needed)
        p_high = compute_innings_pressure_vectorized(
            innings_num=2,
            crr=np.array([7.0]),
            rrr=np.array([14.0]),
            wickets_before=np.array([7]),
            legal_balls_bowled=np.array([108]),
            legal_balls_remaining=np.array([12]),
            total_legal_balls=np.array([120]),
            required_runs=np.array([28]),
        )[0]

        # Test 3: Target reached (0 needed)
        p_zero = compute_innings_pressure_vectorized(
            innings_num=2,
            crr=np.array([9.0]),
            rrr=np.array([0.0]),
            wickets_before=np.array([3]),
            legal_balls_bowled=np.array([110]),
            legal_balls_remaining=np.array([10]),
            total_legal_balls=np.array([120]),
            required_runs=np.array([0]),
        )[0]

        self.assertGreater(p_high, p_low)
        self.assertEqual(p_zero, 0.0)
        self.assertTrue(0.0 <= p_low <= 100.0)
        self.assertTrue(0.0 <= p_high <= 100.0)


if __name__ == "__main__":
    unittest.main()

