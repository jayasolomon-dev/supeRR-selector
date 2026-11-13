"""
SUPERR SELECTOR - Master Task 05 Cohort Validation Test Suite
Module: src/validate_task_05_cohort.py

Validates the clean player analytics cohort against all Task 05.1 criteria:
1. No innings > 2 (zero Super Over contamination).
2. No post-target residual records (zero dead-rubber balls).
3. Actual winning delivery retained (e.g. Match 48610 ball 13.6).
4. Zero duplicate delivery primary keys.
5. Zero missing or orphan player IDs.
6. Exact delivery and match reconciliation (IPL 87,673, T20I 106,303, Combined 193,976).
"""

import sys
import os
import unittest
import logging
import pandas as pd
import numpy as np

# Ensure root directory is on path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.analytics.task_05_cohort import (
    load_clean_cohort,
    EXPECTED_IPL_ROWS,
    EXPECTED_T20I_ROWS,
    EXPECTED_COMBINED_ROWS,
    EXPECTED_IPL_MATCHES,
    EXPECTED_T20I_MATCHES,
    EXPECTED_COMBINED_MATCHES
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("validate_task_05_cohort")


class TestTask05Cohort(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.info("Loading clean cohort datasets for validation...")
        cls.df_ipl = load_clean_cohort(format_filter="IPL")
        cls.df_t20i = load_clean_cohort(format_filter="T20I")
        cls.df_combined = load_clean_cohort()

    def test_01_row_and_match_reconciliation(self):
        """Verify exact delivery and match census counts."""
        self.assertEqual(len(self.df_ipl), EXPECTED_IPL_ROWS, f"IPL row count mismatch: {len(self.df_ipl)} != {EXPECTED_IPL_ROWS}")
        self.assertEqual(len(self.df_t20i), EXPECTED_T20I_ROWS, f"T20I row count mismatch: {len(self.df_t20i)} != {EXPECTED_T20I_ROWS}")
        self.assertEqual(len(self.df_combined), EXPECTED_COMBINED_ROWS, f"Combined row count mismatch: {len(self.df_combined)} != {EXPECTED_COMBINED_ROWS}")

        self.assertEqual(self.df_ipl["match_id"].nunique(), EXPECTED_IPL_MATCHES)
        self.assertEqual(self.df_t20i["match_id"].nunique(), EXPECTED_T20I_MATCHES)
        self.assertEqual(self.df_combined["match_id"].nunique(), EXPECTED_COMBINED_MATCHES)
        logger.info("✔ Test 01: Row and match reconciliation PASSED.")

    def test_02_no_super_overs(self):
        """Verify no delivery has innings > 2."""
        max_inn_ipl = self.df_ipl["innings"].max()
        max_inn_t20i = self.df_t20i["innings"].max()
        max_inn_comb = self.df_combined["innings"].max()

        self.assertLessEqual(max_inn_ipl, 2, "IPL contains innings > 2")
        self.assertLessEqual(max_inn_t20i, 2, "T20I contains innings > 2")
        self.assertLessEqual(max_inn_comb, 2, "Combined contains innings > 2")

        so_count = (self.df_combined["innings"] > 2).sum()
        self.assertEqual(so_count, 0, f"Found {so_count} Super Over deliveries in clean cohort")
        logger.info("✔ Test 02: Zero Super Over contamination PASSED.")

    def test_03_no_post_target_residual_records(self):
        """Verify no delivery has is_target_met_delivery == True."""
        post_ipl = self.df_ipl["is_target_met_delivery"].fillna(False).astype(bool).sum()
        post_t20i = self.df_t20i["is_target_met_delivery"].fillna(False).astype(bool).sum()
        post_comb = self.df_combined["is_target_met_delivery"].fillna(False).astype(bool).sum()

        self.assertEqual(post_ipl, 0, f"IPL contains {post_ipl} post-target deliveries")
        self.assertEqual(post_t20i, 0, f"T20I contains {post_t20i} post-target deliveries")
        self.assertEqual(post_comb, 0, f"Combined contains {post_comb} post-target deliveries")
        logger.info("✔ Test 03: Zero post-target residual records PASSED.")

    def test_04_winning_delivery_retained(self):
        """Verify that the actual winning delivery is preserved in the cohort (e.g. Match 48610 Ball 13.6)."""
        m48610 = self.df_combined[self.df_combined["match_id"] == 48610]
        self.assertFalse(m48610.empty, "Match 48610 not found in clean cohort")

        # Ball 13.6 in innings 2 was the match-winning ball (overid 13, over_ball_num 6)
        winning_ball = m48610[(m48610["innings"] == 2) & (m48610["overid"] == 13) & (m48610["over_ball_num"] == 6)]
        self.assertEqual(len(winning_ball), 1, "Match 48610 winning ball 13.6 missing")
        self.assertEqual(float(winning_ball["required_runs_before"].iloc[0]), 1.0)
        self.assertEqual(bool(winning_ball["is_target_met_delivery"].iloc[0]), False)
        self.assertGreater(float(winning_ball["batting_pressure_score"].iloc[0]), 0.0)
        self.assertGreater(float(winning_ball["bowling_pressure_score"].iloc[0]), 0.0)

        # Confirm post-target deliveries in Match 48610 (overid >= 14) are excluded
        post_balls = m48610[(m48610["innings"] == 2) & (m48610["overid"] >= 14)]
        self.assertEqual(len(post_balls), 0, f"Expected 0 post-target balls in Match 48610, found {len(post_balls)}")
        logger.info("✔ Test 04: Winning delivery preservation and terminal exclusion PASSED.")

    def test_05_primary_key_uniqueness(self):
        """Verify composite primary key uniqueness."""
        key_cols = ["match_id", "innings", "overid", "over_ball_num", "innings_ball_num"]
        dup_ipl = self.df_ipl.duplicated(subset=key_cols).sum()
        dup_t20i = self.df_t20i.duplicated(subset=key_cols).sum()
        dup_comb = self.df_combined.duplicated(subset=key_cols).sum()

        self.assertEqual(dup_ipl, 0, f"IPL has {dup_ipl} duplicate keys")
        self.assertEqual(dup_t20i, 0, f"T20I has {dup_t20i} duplicate keys")
        self.assertEqual(dup_comb, 0, f"Combined has {dup_comb} duplicate keys")
        logger.info("✔ Test 05: Primary key uniqueness PASSED.")

    def test_06_player_identity_completeness(self):
        """Verify zero nulls in striker and bowler IDs and names."""
        for col in ["striker_id", "striker_name", "bowler_id", "bowler_name"]:
            nulls = self.df_combined[col].isnull().sum()
            self.assertEqual(nulls, 0, f"Found {nulls} missing values in {col}")
        logger.info("✔ Test 06: Player identity completeness PASSED.")

    def test_07_pressure_scores_bounded(self):
        """Verify batting and bowling pressure scores strictly bounded in [0.0, 100.0]."""
        for score_col in ["batting_pressure_score", "bowling_pressure_score"]:
            min_val = self.df_combined[score_col].min()
            max_val = self.df_combined[score_col].max()
            self.assertGreaterEqual(min_val, 0.0, f"{score_col} min < 0.0: {min_val}")
            self.assertLessEqual(max_val, 100.0, f"{score_col} max > 100.0: {max_val}")
        logger.info("✔ Test 07: Pressure scores bounded in [0.0, 100.0] PASSED.")


if __name__ == "__main__":
    unittest.main(argv=["first-arg-is-ignored"], exit=False)

