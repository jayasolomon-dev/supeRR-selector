"""
SUPERR SELECTOR - Master Task 05 Player Reliability & Shrinkage Engine
Module: src/analytics/task_05_reliability.py

Implements statistically defensible player reliability modeling:
1. Transparent, objective eligibility tiering (Qualified, Provisional, Ineligible).
2. Empirical-Bayes partial pooling and shrinkage toward role/population priors.
3. Separate, independent indices for Batters and Bowlers on [0.0, 100.0] scale.
4. Match-cluster bootstrap (B = 500 iterations, seed = 42) for 95% confidence intervals.
5. Exports:
   - data/analytics/task_05_batter_reliability.csv
   - data/analytics/task_05_bowler_reliability.csv
"""

import os
import sys
import logging
from typing import Optional, Dict, Tuple, List
import pandas as pd
import numpy as np
from scipy import stats

# Ensure root directory is on path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.analytics.task_05_cohort import load_clean_cohort

logger = logging.getLogger("task_05_reliability")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s [%(name)s]: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

ANALYTICS_DIR = os.path.join(ROOT_DIR, "data", "analytics")
BATTER_METRICS_PATH = os.path.join(ANALYTICS_DIR, "task_05_batter_metrics.csv")
BOWLER_METRICS_PATH = os.path.join(ANALYTICS_DIR, "task_05_bowler_metrics.csv")

BATTER_RELIABILITY_PATH = os.path.join(ANALYTICS_DIR, "task_05_batter_reliability.csv")
BOWLER_RELIABILITY_PATH = os.path.join(ANALYTICS_DIR, "task_05_bowler_reliability.csv")

# ------------------------------------------------------------------------------
# Eligibility Thresholds
# ------------------------------------------------------------------------------
# Core Qualified Tier: Substantial pressure exposure and multi-match experience
BATTER_MIN_HIGH_BALLS_QUAL = 30
BATTER_MIN_NORM_BALLS_QUAL = 30
BATTER_MIN_MATCHES_QUAL = 5

BOWLER_MIN_HIGH_BALLS_QUAL = 30
BOWLER_MIN_NORM_BALLS_QUAL = 30
BOWLER_MIN_MATCHES_QUAL = 5

# Provisional Tier: Modest exposure (high shrinkage applied)
MIN_BALLS_PROVISIONAL = 15
MIN_MATCHES_PROVISIONAL = 3

# Empirical Bayes Prior Sample Size Parameters (Balls)
K_BATTER_SHRINKAGE = 30.0
K_BOWLER_SHRINKAGE = 30.0

# Number of match-cluster bootstrap iterations
BOOTSTRAP_ITERATIONS = 500
RANDOM_SEED = 42


def classify_batter_eligibility(row: pd.Series) -> str:
    """Classifies batter into Qualified, Provisional, or Ineligible."""
    bf_h = row["balls_faced_high"]
    bf_n = row["balls_faced_normal"]
    m = row["matches_overall"]

    if bf_h >= BATTER_MIN_HIGH_BALLS_QUAL and bf_n >= BATTER_MIN_NORM_BALLS_QUAL and m >= BATTER_MIN_MATCHES_QUAL:
        return "Qualified"
    elif bf_h >= MIN_BALLS_PROVISIONAL and bf_n >= MIN_BALLS_PROVISIONAL and m >= MIN_MATCHES_PROVISIONAL:
        return "Provisional"
    else:
        return "Ineligible"


def classify_bowler_eligibility(row: pd.Series) -> str:
    """Classifies bowler into Qualified, Provisional, or Ineligible."""
    lb_h = row["legal_balls_high"]
    lb_n = row["legal_balls_normal"]
    m = row["matches_overall"]

    if lb_h >= BOWLER_MIN_HIGH_BALLS_QUAL and lb_n >= BOWLER_MIN_NORM_BALLS_QUAL and m >= BOWLER_MIN_MATCHES_QUAL:
        return "Qualified"
    elif lb_h >= MIN_BALLS_PROVISIONAL and lb_n >= MIN_BALLS_PROVISIONAL and m >= MIN_MATCHES_PROVISIONAL:
        return "Provisional"
    else:
        return "Ineligible"


def assign_reliability_grade(score: float, tier: str) -> str:
    """Assigns an ordinal reliability grade based on score and eligibility tier."""
    if tier == "Ineligible" or np.isnan(score):
        return "Unrated"
    elif tier == "Provisional":
        if score >= 65.0:
            return "Provisional-High"
        elif score >= 50.0:
            return "Provisional-Mod"
        else:
            return "Provisional-Low"
    else:
        if score >= 70.0:
            return "Elite"
        elif score >= 60.0:
            return "High"
        elif score >= 45.0:
            return "Moderate"
        else:
            return "Low"


# ==============================================================================
# Batter Reliability Model
# ==============================================================================
def compute_batter_reliability(bat_df: pd.DataFrame, deliveries_df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes Empirical-Bayes shrunk Batter Reliability Index with match-cluster bootstrap CIs.
    """
    logger.info("Computing Batter Reliability Index & Uncertainty intervals...")
    res = bat_df.copy()

    # 1. Eligibility Classification
    res["eligibility_tier"] = res.apply(classify_batter_eligibility, axis=1)
    tier_counts = res["eligibility_tier"].value_counts().to_dict()
    logger.info(f"Batter eligibility breakdown: {tier_counts}")

    # 2. Population Baselines (from Qualified cohort)
    qual = res[res["eligibility_tier"] == "Qualified"]
    mu_sr_high = qual["strike_rate_high"].mean()
    sd_sr_high = qual["strike_rate_high"].std(ddof=1) or 1.0

    mu_diff_sr = qual["diff_strike_rate"].mean()
    sd_diff_sr = qual["diff_strike_rate"].std(ddof=1) or 1.0

    mu_diff_dot = qual["diff_dot_pct"].mean()
    sd_diff_dot = qual["diff_dot_pct"].std(ddof=1) or 1.0

    mu_diff_dis = qual["diff_dismissal_rate_per_100"].mean()
    sd_diff_dis = qual["diff_dismissal_rate_per_100"].std(ddof=1) or 1.0

    logger.info(f"Batter Population Priors (N={len(qual)}): mu_diff_sr={mu_diff_sr:.2f}, mu_diff_dot={mu_diff_dot:.2f}, mu_diff_dis={mu_diff_dis:.2f}")

    # 3. Harmonic Mean Effective Sample Size & Shrinkage Weights
    # n_eff = 2 * n_high * n_norm / (n_high + n_norm)
    h_bf = res["balls_faced_high"].values
    n_bf = res["balls_faced_normal"].values
    denom = np.where((h_bf + n_bf) > 0, (h_bf + n_bf), np.nan)
    n_eff = np.where((h_bf > 0) & (n_bf > 0), 2.0 * h_bf * n_bf / denom, 0.0)
    res["effective_balls"] = np.round(n_eff, 1)

    shrink_weight = np.where(n_eff > 0, n_eff / (n_eff + K_BATTER_SHRINKAGE), 0.0)
    res["shrinkage_weight"] = np.round(shrink_weight, 4)

    # 4. Apply Empirical Bayes Shrinkage to Observed Metrics
    res["shrunk_diff_strike_rate"] = np.round(
        shrink_weight * res["diff_strike_rate"].fillna(mu_diff_sr) + (1.0 - shrink_weight) * mu_diff_sr, 2
    )
    res["shrunk_diff_dot_pct"] = np.round(
        shrink_weight * res["diff_dot_pct"].fillna(mu_diff_dot) + (1.0 - shrink_weight) * mu_diff_dot, 2
    )
    res["shrunk_diff_dismissal_rate"] = np.round(
        shrink_weight * res["diff_dismissal_rate_per_100"].fillna(mu_diff_dis) + (1.0 - shrink_weight) * mu_diff_dis, 2
    )
    res["shrunk_strike_rate_high"] = np.round(
        shrink_weight * res["strike_rate_high"].fillna(mu_sr_high) + (1.0 - shrink_weight) * mu_sr_high, 2
    )

    # 5. Standardized Sub-Component Z-Scores
    # Directionality: higher SR is positive; lower dot% is positive (-); lower dismissal rate is positive (-)
    z_diff_sr = (res["shrunk_diff_strike_rate"] - mu_diff_sr) / sd_diff_sr
    z_diff_dot = -(res["shrunk_diff_dot_pct"] - mu_diff_dot) / sd_diff_dot
    z_diff_dis = -(res["shrunk_diff_dismissal_rate"] - mu_diff_dis) / sd_diff_dis
    z_sr_high = (res["shrunk_strike_rate_high"] - mu_sr_high) / sd_sr_high

    # Component weights: 0.40 SR diff, 0.25 Dot% diff, 0.20 Dismissal diff, 0.15 Abs High SR
    z_composite = 0.40 * z_diff_sr + 0.25 * z_diff_dot + 0.20 * z_diff_dis + 0.15 * z_sr_high
    res["raw_composite_z"] = np.round(z_composite, 3)

    # Scaled to [0.0, 100.0] with 50.0 as population baseline, SD = 10.0
    res["batter_reliability_index"] = np.round(np.clip(50.0 + 10.0 * z_composite, 0.0, 100.0), 2)

    # Ineligible batters with zero effective balls clamped to neutral prior 50.0
    res.loc[res["eligibility_tier"] == "Ineligible", "batter_reliability_index"] = 50.00

    # 6. Match-Cluster Bootstrap for 95% Confidence Intervals
    logger.info(f"Running {BOOTSTRAP_ITERATIONS} match-cluster bootstrap iterations for batters (seed={RANDOM_SEED})...")
    np.random.seed(RANDOM_SEED)

    # Pre-aggregate match-batter table
    mask_h = deliveries_df["batting_pressure_score"] >= 65.0
    mask_n = deliveries_df["batting_pressure_score"] < 40.0

    deliveries_df["_bf_h"] = mask_h & deliveries_df["is_batter_ball"]
    deliveries_df["_bf_n"] = mask_n & deliveries_df["is_batter_ball"]
    deliveries_df["_r_h"] = np.where(mask_h, deliveries_df["runs_off_bat"], 0)
    deliveries_df["_r_n"] = np.where(mask_n, deliveries_df["runs_off_bat"], 0)
    deliveries_df["_dot_h"] = mask_h & deliveries_df["is_batter_ball"] & (deliveries_df["runs_off_bat"] == 0)
    deliveries_df["_dot_n"] = mask_n & deliveries_df["is_batter_ball"] & (deliveries_df["runs_off_bat"] == 0)
    deliveries_df["_dis_h"] = mask_h & deliveries_df["is_batter_out"]
    deliveries_df["_dis_n"] = mask_n & deliveries_df["is_batter_out"]

    mb_agg = deliveries_df.groupby(["match_id", "striker_id"])[
        ["_bf_h", "_bf_n", "_r_h", "_r_n", "_dot_h", "_dot_n", "_dis_h", "_dis_n"]
    ].sum().reset_index()

    matches = deliveries_df["match_id"].unique()
    n_matches = len(matches)
    striker_ids = res["striker_id"].values
    id_to_idx = {sid: i for i, sid in enumerate(striker_ids)}
    boot_matrix = np.full((BOOTSTRAP_ITERATIONS, len(striker_ids)), np.nan)

    # Pre-index mb_agg for vector operations
    mb_striker_idx = mb_agg["striker_id"].map(id_to_idx).values
    mb_match_id = mb_agg["match_id"].values
    bf_h_arr = mb_agg["_bf_h"].values
    bf_n_arr = mb_agg["_bf_n"].values
    r_h_arr = mb_agg["_r_h"].values
    r_n_arr = mb_agg["_r_n"].values
    dot_h_arr = mb_agg["_dot_h"].values
    dot_n_arr = mb_agg["_dot_n"].values
    dis_h_arr = mb_agg["_dis_h"].values
    dis_n_arr = mb_agg["_dis_n"].values

    with np.errstate(divide='ignore', invalid='ignore'):
        for b in range(BOOTSTRAP_ITERATIONS):
            resampled_m = np.random.choice(matches, size=n_matches, replace=True)
            m_counts = pd.Series(resampled_m).value_counts().to_dict()
            w_matches = np.array([m_counts.get(m, 0) for m in mb_match_id])

            # Aggregate for this draw
            sum_bf_h = np.bincount(mb_striker_idx, weights=bf_h_arr * w_matches, minlength=len(striker_ids))
            sum_bf_n = np.bincount(mb_striker_idx, weights=bf_n_arr * w_matches, minlength=len(striker_ids))
            sum_r_h = np.bincount(mb_striker_idx, weights=r_h_arr * w_matches, minlength=len(striker_ids))
            sum_r_n = np.bincount(mb_striker_idx, weights=r_n_arr * w_matches, minlength=len(striker_ids))
            sum_dot_h = np.bincount(mb_striker_idx, weights=dot_h_arr * w_matches, minlength=len(striker_ids))
            sum_dot_n = np.bincount(mb_striker_idx, weights=dot_n_arr * w_matches, minlength=len(striker_ids))
            sum_dis_h = np.bincount(mb_striker_idx, weights=dis_h_arr * w_matches, minlength=len(striker_ids))
            sum_dis_n = np.bincount(mb_striker_idx, weights=dis_n_arr * w_matches, minlength=len(striker_ids))

            # Rates
            sr_h = np.where(sum_bf_h > 0, 100.0 * sum_r_h / sum_bf_h, np.nan)
            sr_n = np.where(sum_bf_n > 0, 100.0 * sum_r_n / sum_bf_n, np.nan)
            diff_sr = sr_h - sr_n

            dot_h = np.where(sum_bf_h > 0, 100.0 * sum_dot_h / sum_bf_h, np.nan)
            dot_n = np.where(sum_bf_n > 0, 100.0 * sum_dot_n / sum_bf_n, np.nan)
            diff_dot = dot_h - dot_n

            dis_h = np.where(sum_bf_h > 0, 100.0 * sum_dis_h / sum_bf_h, np.nan)
            dis_n = np.where(sum_bf_n > 0, 100.0 * sum_dis_n / sum_bf_n, np.nan)
            diff_dis = dis_h - dis_n

            # Shrinkage
            denom_b = sum_bf_h + sum_bf_n
            n_eff_b = np.where((sum_bf_h > 0) & (sum_bf_n > 0), 2.0 * sum_bf_h * sum_bf_n / np.where(denom_b > 0, denom_b, 1), 0.0)
            w_b = np.where(n_eff_b > 0, n_eff_b / (n_eff_b + K_BATTER_SHRINKAGE), 0.0)

            s_diff_sr = w_b * np.nan_to_num(diff_sr, nan=mu_diff_sr) + (1.0 - w_b) * mu_diff_sr
            s_diff_dot = w_b * np.nan_to_num(diff_dot, nan=mu_diff_dot) + (1.0 - w_b) * mu_diff_dot
            s_diff_dis = w_b * np.nan_to_num(diff_dis, nan=mu_diff_dis) + (1.0 - w_b) * mu_diff_dis
            s_sr_h = w_b * np.nan_to_num(sr_h, nan=mu_sr_high) + (1.0 - w_b) * mu_sr_high

            z_b = (
                0.40 * (s_diff_sr - mu_diff_sr) / sd_diff_sr
                - 0.25 * (s_diff_dot - mu_diff_dot) / sd_diff_dot
                - 0.20 * (s_diff_dis - mu_diff_dis) / sd_diff_dis
                + 0.15 * (s_sr_h - mu_sr_high) / sd_sr_high
            )
            idx_b = np.clip(50.0 + 10.0 * z_b, 0.0, 100.0)
            boot_matrix[b, :] = idx_b

    # Calculate percentiles and standard error
    ci_lower = np.percentile(boot_matrix, 2.5, axis=0)
    ci_upper = np.percentile(boot_matrix, 97.5, axis=0)
    ci_se = np.std(boot_matrix, axis=0)

    res["ci_lower_95"] = np.round(ci_lower, 2)
    res["ci_upper_95"] = np.round(ci_upper, 2)
    res["ci_std_error"] = np.round(ci_se, 2)

    # 7. Assign Ordinal Reliability Grade
    res["reliability_grade"] = res.apply(
        lambda r: assign_reliability_grade(r["batter_reliability_index"], r["eligibility_tier"]), axis=1
    )

    # Clean up deliveries temp columns
    deliveries_df.drop(columns=["_bf_h", "_bf_n", "_r_h", "_r_n", "_dot_h", "_dot_n", "_dis_h", "_dis_n"], inplace=True)

    # Export
    os.makedirs(ANALYTICS_DIR, exist_ok=True)
    res.to_csv(BATTER_RELIABILITY_PATH, index=False)
    logger.info(f"Batter reliability model complete -> {BATTER_RELIABILITY_PATH}")
    return res


# ==============================================================================
# Bowler Reliability Model
# ==============================================================================
def compute_bowler_reliability(bowl_df: pd.DataFrame, deliveries_df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes Empirical-Bayes shrunk Bowler Reliability Index with match-cluster bootstrap CIs.
    """
    logger.info("Computing Bowler Reliability Index & Uncertainty intervals...")
    res = bowl_df.copy()

    # 1. Eligibility Classification
    res["eligibility_tier"] = res.apply(classify_bowler_eligibility, axis=1)
    tier_counts = res["eligibility_tier"].value_counts().to_dict()
    logger.info(f"Bowler eligibility breakdown: {tier_counts}")

    # 2. Population Baselines (from Qualified cohort)
    qual = res[res["eligibility_tier"] == "Qualified"]
    mu_econ_high = qual["economy_rate_high"].mean()
    sd_econ_high = qual["economy_rate_high"].std(ddof=1) or 1.0

    mu_diff_econ = qual["diff_economy_rate"].mean()
    sd_diff_econ = qual["diff_economy_rate"].std(ddof=1) or 1.0

    mu_diff_wkt = qual["diff_wickets_per_over"].mean()
    sd_diff_wkt = qual["diff_wickets_per_over"].std(ddof=1) or 1.0

    mu_diff_dot = qual["diff_dot_pct"].mean()
    sd_diff_dot = qual["diff_dot_pct"].std(ddof=1) or 1.0

    logger.info(f"Bowler Population Priors (N={len(qual)}): mu_diff_econ={mu_diff_econ:.2f}, mu_diff_wkt={mu_diff_wkt:.3f}, mu_diff_dot={mu_diff_dot:.2f}")

    # 3. Harmonic Mean Effective Sample Size & Shrinkage Weights
    h_lb = res["legal_balls_high"].values
    n_lb = res["legal_balls_normal"].values
    denom = np.where((h_lb + n_lb) > 0, (h_lb + n_lb), np.nan)
    n_eff = np.where((h_lb > 0) & (n_lb > 0), 2.0 * h_lb * n_lb / denom, 0.0)
    res["effective_balls"] = np.round(n_eff, 1)

    shrink_weight = np.where(n_eff > 0, n_eff / (n_eff + K_BOWLER_SHRINKAGE), 0.0)
    res["shrinkage_weight"] = np.round(shrink_weight, 4)

    # 4. Apply Empirical Bayes Shrinkage to Observed Metrics
    res["shrunk_diff_economy_rate"] = np.round(
        shrink_weight * res["diff_economy_rate"].fillna(mu_diff_econ) + (1.0 - shrink_weight) * mu_diff_econ, 2
    )
    res["shrunk_diff_wickets_per_over"] = np.round(
        shrink_weight * res["diff_wickets_per_over"].fillna(mu_diff_wkt) + (1.0 - shrink_weight) * mu_diff_wkt, 3
    )
    res["shrunk_diff_dot_pct"] = np.round(
        shrink_weight * res["diff_dot_pct"].fillna(mu_diff_dot) + (1.0 - shrink_weight) * mu_diff_dot, 2
    )
    res["shrunk_economy_rate_high"] = np.round(
        shrink_weight * res["economy_rate_high"].fillna(mu_econ_high) + (1.0 - shrink_weight) * mu_econ_high, 2
    )

    # 5. Standardized Sub-Component Z-Scores
    # Directionality: lower economy diff is positive (-); higher wkt diff is positive (+); higher dot diff is positive (+)
    z_diff_econ = -(res["shrunk_diff_economy_rate"] - mu_diff_econ) / sd_diff_econ
    z_diff_wkt = (res["shrunk_diff_wickets_per_over"] - mu_diff_wkt) / sd_diff_wkt
    z_diff_dot = (res["shrunk_diff_dot_pct"] - mu_diff_dot) / sd_diff_dot
    z_econ_high = -(res["shrunk_economy_rate_high"] - mu_econ_high) / sd_econ_high

    # Component weights: 0.40 Econ diff, 0.25 Wkt diff, 0.20 Dot% diff, 0.15 Abs High Econ
    z_composite = 0.40 * z_diff_econ + 0.25 * z_diff_wkt + 0.20 * z_diff_dot + 0.15 * z_econ_high
    res["raw_composite_z"] = np.round(z_composite, 3)

    # Scaled to [0.0, 100.0] with 50.0 as population baseline, SD = 10.0
    res["bowler_reliability_index"] = np.round(np.clip(50.0 + 10.0 * z_composite, 0.0, 100.0), 2)

    # Ineligible bowlers with zero effective balls clamped to neutral prior 50.0
    res.loc[res["eligibility_tier"] == "Ineligible", "bowler_reliability_index"] = 50.00

    # 6. Match-Cluster Bootstrap for 95% Confidence Intervals
    logger.info(f"Running {BOOTSTRAP_ITERATIONS} match-cluster bootstrap iterations for bowlers (seed={RANDOM_SEED})...")
    np.random.seed(RANDOM_SEED)

    # Pre-aggregate match-bowler table
    mask_h = deliveries_df["bowling_pressure_score"] >= 65.0
    mask_n = deliveries_df["bowling_pressure_score"] < 40.0

    deliveries_df["_lb_h"] = mask_h & deliveries_df["is_legal_ball"]
    deliveries_df["_lb_n"] = mask_n & deliveries_df["is_legal_ball"]
    deliveries_df["_r_h"] = np.where(mask_h, deliveries_df["bowler_runs_conceded"], 0)
    deliveries_df["_r_n"] = np.where(mask_n, deliveries_df["bowler_runs_conceded"], 0)
    deliveries_df["_w_h"] = mask_h & deliveries_df["is_bowler_wicket"]
    deliveries_df["_w_n"] = mask_n & deliveries_df["is_bowler_wicket"]
    deliveries_df["_dot_h"] = mask_h & deliveries_df["is_legal_ball"] & (deliveries_df["bowler_runs_conceded"] == 0)
    deliveries_df["_dot_n"] = mask_n & deliveries_df["is_legal_ball"] & (deliveries_df["bowler_runs_conceded"] == 0)

    mb_agg = deliveries_df.groupby(["match_id", "bowler_id"])[
        ["_lb_h", "_lb_n", "_r_h", "_r_n", "_w_h", "_w_n", "_dot_h", "_dot_n"]
    ].sum().reset_index()

    matches = deliveries_df["match_id"].unique()
    n_matches = len(matches)
    bowler_ids = res["bowler_id"].values
    id_to_idx = {bid: i for i, bid in enumerate(bowler_ids)}
    boot_matrix = np.full((BOOTSTRAP_ITERATIONS, len(bowler_ids)), np.nan)

    # Pre-index mb_agg for vector operations
    mb_bowler_idx = mb_agg["bowler_id"].map(id_to_idx).values
    mb_match_id = mb_agg["match_id"].values
    lb_h_arr = mb_agg["_lb_h"].values
    lb_n_arr = mb_agg["_lb_n"].values
    r_h_arr = mb_agg["_r_h"].values
    r_n_arr = mb_agg["_r_n"].values
    w_h_arr = mb_agg["_w_h"].values
    w_n_arr = mb_agg["_w_n"].values
    dot_h_arr = mb_agg["_dot_h"].values
    dot_n_arr = mb_agg["_dot_n"].values

    with np.errstate(divide='ignore', invalid='ignore'):
        for b in range(BOOTSTRAP_ITERATIONS):
            resampled_m = np.random.choice(matches, size=n_matches, replace=True)
            m_counts = pd.Series(resampled_m).value_counts().to_dict()
            w_matches = np.array([m_counts.get(m, 0) for m in mb_match_id])

            # Aggregate for this draw
            sum_lb_h = np.bincount(mb_bowler_idx, weights=lb_h_arr * w_matches, minlength=len(bowler_ids))
            sum_lb_n = np.bincount(mb_bowler_idx, weights=lb_n_arr * w_matches, minlength=len(bowler_ids))
            sum_r_h = np.bincount(mb_bowler_idx, weights=r_h_arr * w_matches, minlength=len(bowler_ids))
            sum_r_n = np.bincount(mb_bowler_idx, weights=r_n_arr * w_matches, minlength=len(bowler_ids))
            sum_w_h = np.bincount(mb_bowler_idx, weights=w_h_arr * w_matches, minlength=len(bowler_ids))
            sum_w_n = np.bincount(mb_bowler_idx, weights=w_n_arr * w_matches, minlength=len(bowler_ids))
            sum_dot_h = np.bincount(mb_bowler_idx, weights=dot_h_arr * w_matches, minlength=len(bowler_ids))
            sum_dot_n = np.bincount(mb_bowler_idx, weights=dot_n_arr * w_matches, minlength=len(bowler_ids))

            # Rates
            econ_h = np.where(sum_lb_h > 0, 6.0 * sum_r_h / sum_lb_h, np.nan)
            econ_n = np.where(sum_lb_n > 0, 6.0 * sum_r_n / sum_lb_n, np.nan)
            diff_econ = econ_h - econ_n

            wkt_h = np.where(sum_lb_h > 0, 6.0 * sum_w_h / sum_lb_h, np.nan)
            wkt_n = np.where(sum_lb_n > 0, 6.0 * sum_w_n / sum_lb_n, np.nan)
            diff_wkt = wkt_h - wkt_n

            dot_h = np.where(sum_lb_h > 0, 100.0 * sum_dot_h / sum_lb_h, np.nan)
            dot_n = np.where(sum_lb_n > 0, 100.0 * sum_dot_n / sum_lb_n, np.nan)
            diff_dot = dot_h - dot_n

            # Shrinkage
            denom_b = sum_lb_h + sum_lb_n
            n_eff_b = np.where((sum_lb_h > 0) & (sum_lb_n > 0), 2.0 * sum_lb_h * sum_lb_n / np.where(denom_b > 0, denom_b, 1), 0.0)
            w_b = np.where(n_eff_b > 0, n_eff_b / (n_eff_b + K_BOWLER_SHRINKAGE), 0.0)

            s_diff_econ = w_b * np.nan_to_num(diff_econ, nan=mu_diff_econ) + (1.0 - w_b) * mu_diff_econ
            s_diff_wkt = w_b * np.nan_to_num(diff_wkt, nan=mu_diff_wkt) + (1.0 - w_b) * mu_diff_wkt
            s_diff_dot = w_b * np.nan_to_num(diff_dot, nan=mu_diff_dot) + (1.0 - w_b) * mu_diff_dot
            s_econ_h = w_b * np.nan_to_num(econ_h, nan=mu_econ_high) + (1.0 - w_b) * mu_econ_high

            z_b = (
                - 0.40 * (s_diff_econ - mu_diff_econ) / sd_diff_econ
                + 0.25 * (s_diff_wkt - mu_diff_wkt) / sd_diff_wkt
                + 0.20 * (s_diff_dot - mu_diff_dot) / sd_diff_dot
                - 0.15 * (s_econ_h - mu_econ_high) / sd_econ_high
            )
            idx_b = np.clip(50.0 + 10.0 * z_b, 0.0, 100.0)
            boot_matrix[b, :] = idx_b

    # Calculate percentiles and standard error
    ci_lower = np.percentile(boot_matrix, 2.5, axis=0)
    ci_upper = np.percentile(boot_matrix, 97.5, axis=0)
    ci_se = np.std(boot_matrix, axis=0)

    res["ci_lower_95"] = np.round(ci_lower, 2)
    res["ci_upper_95"] = np.round(ci_upper, 2)
    res["ci_std_error"] = np.round(ci_se, 2)

    # 7. Assign Ordinal Reliability Grade
    res["reliability_grade"] = res.apply(
        lambda r: assign_reliability_grade(r["bowler_reliability_index"], r["eligibility_tier"]), axis=1
    )

    # Clean up deliveries temp columns
    deliveries_df.drop(columns=["_lb_h", "_lb_n", "_r_h", "_r_n", "_w_h", "_w_n", "_dot_h", "_dot_n"], inplace=True)

    # Export
    os.makedirs(ANALYTICS_DIR, exist_ok=True)
    res.to_csv(BOWLER_RELIABILITY_PATH, index=False)
    logger.info(f"Bowler reliability model complete -> {BOWLER_RELIABILITY_PATH}")
    return res


def run_reliability_pipelines():
    """Executes both Batting and Bowling reliability models."""
    logger.info("=" * 80)
    logger.info("⚡ SUPERR SELECTOR — MASTER TASK 05 RELIABILITY PIPELINE")
    logger.info("=" * 80)

    deliveries_df = load_clean_cohort()
    bat_df = pd.read_csv(BATTER_METRICS_PATH)
    bowl_df = pd.read_csv(BOWLER_METRICS_PATH)

    bat_rel = compute_batter_reliability(bat_df, deliveries_df.copy())
    bowl_rel = compute_bowler_reliability(bowl_df, deliveries_df.copy())

    logger.info("✔ Task 05 Reliability Engine execution completed successfully.")
    return bat_rel, bowl_rel


if __name__ == "__main__":
    bat_rel, bowl_rel = run_reliability_pipelines()

    print("\n--- TOP 10 QUALIFIED BATTERS BY RELIABILITY INDEX ---")
    cols_bat = ["striker_id", "striker_name", "balls_faced_high", "effective_balls", "strike_rate_high", "diff_strike_rate", "batter_reliability_index", "ci_lower_95", "ci_upper_95", "reliability_grade"]
    q_bat = bat_rel[bat_rel["eligibility_tier"] == "Qualified"].sort_values(by="batter_reliability_index", ascending=False)
    print(q_bat[cols_bat].head(10).to_string())

    print("\n--- TOP 10 QUALIFIED BOWLERS BY RELIABILITY INDEX ---")
    cols_bowl = ["bowler_id", "bowler_name", "legal_balls_high", "effective_balls", "economy_rate_high", "diff_economy_rate", "bowler_reliability_index", "ci_lower_95", "ci_upper_95", "reliability_grade"]
    q_bowl = bowl_rel[bowl_rel["eligibility_tier"] == "Qualified"].sort_values(by="bowler_reliability_index", ascending=False)
    print(q_bowl[cols_bowl].head(10).to_string())
