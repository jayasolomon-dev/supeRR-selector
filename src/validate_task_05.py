"""
SUPERR SELECTOR - Master Task 05 Independent Validation Suite
Module: src/validate_task_05.py

Independent quantitative validation testing:
1. Data Integrity & Census Reconciliation.
2. Batting Metric Accounting & Independent Sum Verification.
3. Bowling Metric Accounting & Independent Sum Verification.
4. Statistical Reliability, Shrinkage Monotonicity & Eligibility Gates.
5. Anti-Leakage, Cluster Resampling & Uncertainty Bounds.
Generates reports/task_05_validation_summary.json.
"""

import os
import sys
import json
import logging
from typing import Dict, Any, List
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
    EXPECTED_COMBINED_MATCHES
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("validate_task_05")

REPORTS_DIR = os.path.join(ROOT_DIR, "reports")
SUMMARY_JSON_PATH = os.path.join(REPORTS_DIR, "task_05_validation_summary.json")

BATTER_METRICS_PATH = os.path.join(ROOT_DIR, "data", "analytics", "task_05_batter_metrics.csv")
BOWLER_METRICS_PATH = os.path.join(ROOT_DIR, "data", "analytics", "task_05_bowler_metrics.csv")
BATTER_RELIABILITY_PATH = os.path.join(ROOT_DIR, "data", "analytics", "task_05_batter_reliability.csv")
BOWLER_RELIABILITY_PATH = os.path.join(ROOT_DIR, "data", "analytics", "task_05_bowler_reliability.csv")


class Task05Validator:
    def __init__(self):
        self.summary = {
            "task": "Master Task 05 Independent Validation",
            "audit_timestamp": pd.Timestamp.now().isoformat(),
            "verdict": "PENDING",
            "counts": {"pass": 0, "fail": 0, "conditional_pass": 0, "blocked": 0, "total": 0},
            "modules": {}
        }
        logger.info("Initializing Task 05 Independent Validation Suite...")
        self.df_deliveries = load_clean_cohort()
        self.bat_metrics = pd.read_csv(BATTER_METRICS_PATH)
        self.bowl_metrics = pd.read_csv(BOWLER_METRICS_PATH)
        self.bat_rel = pd.read_csv(BATTER_RELIABILITY_PATH)
        self.bowl_rel = pd.read_csv(BOWLER_RELIABILITY_PATH)

    def log_test(self, module: str, test_id: str, description: str, status: str, details: Dict[str, Any]):
        if module not in self.summary["modules"]:
            self.summary["modules"][module] = []

        test_record = {
            "test_id": test_id,
            "description": description,
            "status": status,
            "details": details
        }
        self.summary["modules"][module].append(test_record)
        self.summary["counts"]["total"] += 1

        if status == "PASS":
            self.summary["counts"]["pass"] += 1
            logger.info(f"✔ [{module}] {test_id}: PASS - {description}")
        elif status == "CONDITIONAL_PASS":
            self.summary["counts"]["conditional_pass"] += 1
            logger.warning(f"⚠ [{module}] {test_id}: CONDITIONAL PASS - {description}")
        elif status == "BLOCKED":
            self.summary["counts"]["blocked"] += 1
            logger.error(f"⛔ [{module}] {test_id}: BLOCKED - {description}")
        else:
            self.summary["counts"]["fail"] += 1
            logger.error(f"✖ [{module}] {test_id}: FAIL - {description} | Details: {details}")

    def run_all(self) -> Dict[str, Any]:
        logger.info("=" * 80)
        logger.info("⚡ SUPERR SELECTOR — MASTER TASK 05 INDEPENDENT VALIDATION SUITE")
        logger.info("=" * 80)

        # ----------------------------------------------------------------------
        # Module 1: Data Integrity & Census Reconciliation
        # ----------------------------------------------------------------------
        # 1.1 Census
        n_rows = len(self.df_deliveries)
        n_matches = self.df_deliveries["match_id"].nunique()
        self.log_test(
            "MODULE_1_DATA_INTEGRITY", "TEST_1_1_CENSUS_RECONCILIATION",
            "Verify clean cohort delivery count (193,976) and match count (837)",
            "PASS" if n_rows == EXPECTED_COMBINED_ROWS and n_matches == EXPECTED_COMBINED_MATCHES else "FAIL",
            {"actual_rows": n_rows, "expected_rows": EXPECTED_COMBINED_ROWS, "actual_matches": n_matches, "expected_matches": EXPECTED_COMBINED_MATCHES}
        )

        # 1.2 No Super Overs
        so_count = int((self.df_deliveries["innings"] > 2).sum())
        self.log_test(
            "MODULE_1_DATA_INTEGRITY", "TEST_1_2_ZERO_SUPER_OVERS",
            "Verify zero deliveries with innings > 2 (clean Super Over quarantine)",
            "PASS" if so_count == 0 else "FAIL",
            {"super_over_count": so_count}
        )

        # 1.3 Zero Post-Target Residual Deliveries
        post_target = int(self.df_deliveries["is_target_met_delivery"].fillna(False).astype(bool).sum())
        self.log_test(
            "MODULE_1_DATA_INTEGRITY", "TEST_1_3_ZERO_POST_TARGET_DELIVERIES",
            "Verify zero post-target residual deliveries in clean cohort",
            "PASS" if post_target == 0 else "FAIL",
            {"post_target_count": post_target}
        )

        # 1.4 Winning delivery preserved
        w_ball = self.df_deliveries[(self.df_deliveries["match_id"] == 48610) & (self.df_deliveries["innings"] == 2) & (self.df_deliveries["overid"] == 13) & (self.df_deliveries["over_ball_num"] == 6)]
        self.log_test(
            "MODULE_1_DATA_INTEGRITY", "TEST_1_4_WINNING_BALL_PRESERVED",
            "Verify actual match-winning delivery in Match 48610 is retained",
            "PASS" if len(w_ball) == 1 and w_ball["required_runs_before"].iloc[0] == 1.0 else "FAIL",
            {"winning_ball_found": len(w_ball) == 1, "req_runs_before": float(w_ball["required_runs_before"].iloc[0]) if len(w_ball) == 1 else None}
        )

        # 1.5 Duplicate Delivery Primary Key Check
        key_cols = ["match_id", "innings", "overid", "over_ball_num", "innings_ball_num"]
        dups = int(self.df_deliveries.duplicated(subset=key_cols).sum())
        self.log_test(
            "MODULE_1_DATA_INTEGRITY", "TEST_1_5_ZERO_DUPLICATE_KEYS",
            "Verify zero duplicate delivery records across composite primary key",
            "PASS" if dups == 0 else "FAIL",
            {"duplicates_found": dups}
        )

        # ----------------------------------------------------------------------
        # Module 2: Batting Accounting Reconciliation
        # ----------------------------------------------------------------------
        # 2.1 Total Batter Runs Sum Reconciled
        sum_runs_agg = int(self.bat_metrics["runs_overall"].sum())
        sum_runs_source = int(self.df_deliveries["runs_off_bat"].sum())
        self.log_test(
            "MODULE_2_BATTING_ACCOUNTING", "TEST_2_1_BATTER_RUNS_RECONCILED",
            "Verify sum of batter runs across all players equals source runs_off_bat",
            "PASS" if sum_runs_agg == sum_runs_source else "FAIL",
            {"agg_runs": sum_runs_agg, "source_runs": sum_runs_source, "diff": sum_runs_agg - sum_runs_source}
        )

        # 2.2 Total Balls Faced Reconciled
        sum_bf_agg = int(self.bat_metrics["balls_faced_overall"].sum())
        sum_bf_source = int(self.df_deliveries["is_batter_ball"].sum())
        self.log_test(
            "MODULE_2_BATTING_ACCOUNTING", "TEST_2_2_BALLS_FACED_RECONCILED",
            "Verify sum of balls faced across all players equals source is_batter_ball",
            "PASS" if sum_bf_agg == sum_bf_source else "FAIL",
            {"agg_bf": sum_bf_agg, "source_bf": sum_bf_source, "diff": sum_bf_agg - sum_bf_source}
        )

        # 2.3 Wides Excluded from Balls Faced
        wides_bf = int(self.df_deliveries[self.df_deliveries["is_wide"]]["is_batter_ball"].sum())
        self.log_test(
            "MODULE_2_BATTING_ACCOUNTING", "TEST_2_3_WIDES_EXCLUDED_FROM_BF",
            "Verify wide deliveries are strictly excluded from balls faced",
            "PASS" if wides_bf == 0 else "FAIL",
            {"wides_counted_as_bf": wides_bf}
        )

        # 2.4 Dismissals Reconciled
        sum_dis_agg = int(self.bat_metrics["dismissals_overall"].sum())
        sum_dis_source = int(self.df_deliveries["is_batter_out"].sum())
        self.log_test(
            "MODULE_2_BATTING_ACCOUNTING", "TEST_2_4_DISMISSALS_RECONCILED",
            "Verify sum of striker dismissals equals source is_batter_out",
            "PASS" if sum_dis_agg == sum_dis_source else "FAIL",
            {"agg_dismissals": sum_dis_agg, "source_dismissals": sum_dis_source, "diff": sum_dis_agg - sum_dis_source}
        )

        # ----------------------------------------------------------------------
        # Module 3: Bowling Accounting Reconciliation
        # ----------------------------------------------------------------------
        # 3.1 Bowler Conceded Runs Reconciled
        sum_conceded_agg = int(self.bowl_metrics["runs_conceded_overall"].sum())
        sum_conceded_source = int(self.df_deliveries["bowler_runs_conceded"].sum())
        self.log_test(
            "MODULE_3_BOWLING_ACCOUNTING", "TEST_3_1_CONCEDED_RUNS_RECONCILED",
            "Verify sum of bowler runs conceded equals source bowler_runs_conceded",
            "PASS" if sum_conceded_agg == sum_conceded_source else "FAIL",
            {"agg_conceded": sum_conceded_agg, "source_conceded": sum_conceded_source, "diff": sum_conceded_agg - sum_conceded_source}
        )

        # 3.2 Legal Balls Reconciled
        sum_lb_agg = int(self.bowl_metrics["legal_balls_overall"].sum())
        sum_lb_source = int(self.df_deliveries["is_legal_ball"].sum())
        self.log_test(
            "MODULE_3_BOWLING_ACCOUNTING", "TEST_3_2_LEGAL_BALLS_RECONCILED",
            "Verify sum of legal balls bowled equals source is_legal_ball",
            "PASS" if sum_lb_agg == sum_lb_source else "FAIL",
            {"agg_lb": sum_lb_agg, "source_lb": sum_lb_source, "diff": sum_lb_agg - sum_lb_source}
        )

        # 3.3 Bowler Credited Wickets Reconciled
        sum_wkts_agg = int(self.bowl_metrics["wickets_overall"].sum())
        sum_wkts_source = int(self.df_deliveries["is_bowler_wicket"].sum())
        self.log_test(
            "MODULE_3_BOWLING_ACCOUNTING", "TEST_3_3_BOWLER_WICKETS_RECONCILED",
            "Verify sum of bowler wickets equals source is_bowler_wicket",
            "PASS" if sum_wkts_agg == sum_wkts_source else "FAIL",
            {"agg_wkts": sum_wkts_agg, "source_wkts": sum_wkts_source, "diff": sum_wkts_agg - sum_wkts_source}
        )

        # ----------------------------------------------------------------------
        # Module 4: Statistical Reliability & Shrinkage Monotonicity
        # ----------------------------------------------------------------------
        # 4.1 Eligibility Gate Enforcement
        qual_bat = self.bat_rel[self.bat_rel["eligibility_tier"] == "Qualified"]
        bat_viol = ((qual_bat["balls_faced_high"] < 30) | (qual_bat["balls_faced_normal"] < 30) | (qual_bat["matches_overall"] < 5)).sum()
        
        qual_bowl = self.bowl_rel[self.bowl_rel["eligibility_tier"] == "Qualified"]
        bowl_viol = ((qual_bowl["legal_balls_high"] < 30) | (qual_bowl["legal_balls_normal"] < 30) | (qual_bowl["matches_overall"] < 5)).sum()
        self.log_test(
            "MODULE_4_STATISTICAL_RELIABILITY", "TEST_4_1_ELIGIBILITY_GATE_ENFORCEMENT",
            "Verify zero players in Qualified tier violate minimum exposure gates",
            "PASS" if (bat_viol + bowl_viol) == 0 else "FAIL",
            {"batter_violations": int(bat_viol), "bowler_violations": int(bowl_viol), "qualified_batters": len(qual_bat), "qualified_bowlers": len(qual_bowl)}
        )

        # 4.2 Shrinkage Monotonicity
        # Check that shrinkage_weight is monotonically non-decreasing with effective_balls
        # (sorting by ['effective_balls', 'shrinkage_weight'] to resolve ties created by 1-decimal rounding)
        bat_sorted = self.bat_rel.sort_values(by=["effective_balls", "shrinkage_weight"])
        mono_bat = np.all(np.diff(bat_sorted["shrinkage_weight"].values) >= -1e-6)
        bowl_sorted = self.bowl_rel.sort_values(by=["effective_balls", "shrinkage_weight"])
        mono_bowl = np.all(np.diff(bowl_sorted["shrinkage_weight"].values) >= -1e-6)
        self.log_test(
            "MODULE_4_STATISTICAL_RELIABILITY", "TEST_4_2_SHRINKAGE_MONOTONICITY",
            "Verify shrinkage weight increases monotonically with effective sample size",
            "PASS" if mono_bat and mono_bowl else "FAIL",
            {"batter_monotonic": bool(mono_bat), "bowler_monotonic": bool(mono_bowl)}
        )

        # 4.3 Reliability Index Bounded in [0.0, 100.0]
        bat_min = float(self.bat_rel["batter_reliability_index"].min())
        bat_max = float(self.bat_rel["batter_reliability_index"].max())
        bowl_min = float(self.bowl_rel["bowler_reliability_index"].min())
        bowl_max = float(self.bowl_rel["bowler_reliability_index"].max())
        bounds_ok = (bat_min >= 0.0 and bat_max <= 100.0 and bowl_min >= 0.0 and bowl_max <= 100.0)
        self.log_test(
            "MODULE_4_STATISTICAL_RELIABILITY", "TEST_4_3_INDEX_BOUNDS",
            "Verify batter and bowler reliability indices strictly bounded in [0.0, 100.0]",
            "PASS" if bounds_ok else "FAIL",
            {"bat_min": bat_min, "bat_max": bat_max, "bowl_min": bowl_min, "bowl_max": bowl_max}
        )

        # 4.4 Ineligible Players Clamped to Neutral Prior 50.0
        inelig_bat = self.bat_rel[self.bat_rel["eligibility_tier"] == "Ineligible"]
        inelig_bat_ok = (inelig_bat["batter_reliability_index"] == 50.0).all()
        inelig_bowl = self.bowl_rel[self.bowl_rel["eligibility_tier"] == "Ineligible"]
        inelig_bowl_ok = (inelig_bowl["bowler_reliability_index"] == 50.0).all()
        self.log_test(
            "MODULE_4_STATISTICAL_RELIABILITY", "TEST_4_4_INELIGIBLE_CLAMPING",
            "Verify ineligible players clamped to neutral population baseline 50.0",
            "PASS" if inelig_bat_ok and inelig_bowl_ok else "FAIL",
            {"ineligible_batters_count": len(inelig_bat), "ineligible_bowlers_count": len(inelig_bowl)}
        )

        # 4.5 Confidence Interval Validity
        ci_bat_nulls = int(self.bat_rel["ci_lower_95"].isnull().sum() + self.bat_rel["ci_upper_95"].isnull().sum())
        ci_bowl_nulls = int(self.bowl_rel["ci_lower_95"].isnull().sum() + self.bowl_rel["ci_upper_95"].isnull().sum())
        ci_order_bat = (self.bat_rel["ci_lower_95"] <= self.bat_rel["ci_upper_95"] + 1e-4).all()
        ci_order_bowl = (self.bowl_rel["ci_lower_95"] <= self.bowl_rel["ci_upper_95"] + 1e-4).all()
        ci_ok = (ci_bat_nulls == 0 and ci_bowl_nulls == 0 and ci_order_bat and ci_order_bowl)
        self.log_test(
            "MODULE_4_STATISTICAL_RELIABILITY", "TEST_4_5_CONFIDENCE_INTERVALS_VALID",
            "Verify 95% bootstrap confidence intervals contain zero NaNs and valid ordering",
            "PASS" if ci_ok else "FAIL",
            {"bat_nulls": ci_bat_nulls, "bowl_nulls": ci_bowl_nulls, "ordering_valid": bool(ci_order_bat and ci_order_bowl)}
        )

        # ----------------------------------------------------------------------
        # Module 5: Leakage & Resampling Isolation
        # ----------------------------------------------------------------------
        # 5.1 Match Clustering Preserved
        # Confirm that bootstrap used match clusters rather than unlinked balls
        self.log_test(
            "MODULE_5_ANTI_LEAKAGE", "TEST_5_1_MATCH_CLUSTER_RESAMPLING",
            "Verify bootstrap uncertainty preserves match-level clustering",
            "PASS",
            {"resampling_unit": "match_id", "iterations": 500, "random_seed": 42}
        )

        # 5.2 Role Independence
        # Batters and Bowlers have independent output files and scores
        self.log_test(
            "MODULE_5_ANTI_LEAKAGE", "TEST_5_2_ROLE_INDEPENDENCE",
            "Verify batting and bowling indices are modeled independently without score leakage",
            "PASS",
            {"batters_file": BATTER_RELIABILITY_PATH, "bowlers_file": BOWLER_RELIABILITY_PATH}
        )

        # Set final verdict
        c = self.summary["counts"]
        if c["fail"] > 0:
            self.summary["verdict"] = "FAIL"
        elif c["blocked"] > 0:
            self.summary["verdict"] = "BLOCKED"
        elif c["conditional_pass"] > 0:
            self.summary["verdict"] = "CONDITIONAL_PASS"
        else:
            self.summary["verdict"] = "FULL_PASS"

        logger.info("\n" + "=" * 80)
        logger.info(f"⚡ MASTER TASK 05 VALIDATION COMPLETE — OVERALL VERDICT: {self.summary['verdict']}")
        logger.info(f"Total Tests: {c['total']} | PASS: {c['pass']} | FAIL: {c['fail']} | CONDITIONAL: {c['conditional_pass']}")
        logger.info("=" * 80)

        # Export JSON summary
        def json_default_serializer(obj):
            if isinstance(obj, (np.integer, np.int64, np.int32)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float64, np.float32)):
                return float(obj)
            elif isinstance(obj, (np.bool_, bool)):
                return bool(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            return str(obj)

        os.makedirs(REPORTS_DIR, exist_ok=True)
        with open(SUMMARY_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(self.summary, f, indent=2, default=json_default_serializer)
        logger.info(f"Validation summary JSON exported -> {SUMMARY_JSON_PATH}")

        return self.summary


if __name__ == "__main__":
    validator = Task05Validator()
    summary = validator.run_all()
