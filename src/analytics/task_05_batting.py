"""
SUPERR SELECTOR - Master Task 05 Batting Analytics Pipeline
Module: src/analytics/task_05_batting.py

Calculates comprehensive, verified delivery-level batting analytics partitioned into:
- High Pressure: batting_pressure_score >= 65.0 (High + Extreme tiers)
- Normal Pressure: batting_pressure_score < 40.0 (Low tier)
- Moderate Pressure: 40.0 <= batting_pressure_score < 65.0 (Intermediate tier)
- Overall Standard Competitive Cohort

All metrics preserve raw numerators and denominators to prevent division-by-zero distortion.
Outputs data/analytics/task_05_batter_metrics.csv.
"""

import os
import sys
import logging
from typing import Optional, Dict, Any
import pandas as pd
import numpy as np

# Ensure root directory is on path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.analytics.task_05_cohort import load_clean_cohort

logger = logging.getLogger("task_05_batting")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s [%(name)s]: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

OUTPUT_DIR = os.path.join(ROOT_DIR, "data", "analytics")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "task_05_batter_metrics.csv")


def compute_batter_cohort_metrics(sub_df: pd.DataFrame, prefix: str) -> pd.DataFrame:
    """
    Computes aggregated batting metrics for a specific pressure subset of deliveries.
    """
    if sub_df.empty:
        return pd.DataFrame()

    # Aggregate by striker_id
    grouped = sub_df.groupby("striker_id")

    # Only count balls where is_batter_ball == True (excludes wides, includes noballs)
    bf = sub_df[sub_df["is_batter_ball"]].groupby("striker_id").size().rename(f"balls_faced_{prefix}")
    runs = sub_df.groupby("striker_id")["runs_off_bat"].sum().rename(f"runs_{prefix}")
    fours = sub_df[sub_df["is_four"]].groupby("striker_id").size().rename(f"fours_{prefix}")
    sixes = sub_df[sub_df["is_six"]].groupby("striker_id").size().rename(f"sixes_{prefix}")
    # Correct cricket dot balls faced: ball faced where 0 runs scored off the bat
    is_dot_ball_bat = sub_df["is_batter_ball"] & (sub_df["runs_off_bat"] == 0)
    dots = sub_df[is_dot_ball_bat].groupby("striker_id").size().rename(f"dots_{prefix}")
    dismissals = sub_df[sub_df["is_batter_out"]].groupby("striker_id").size().rename(f"dismissals_{prefix}")
    matches = grouped["match_id"].nunique().rename(f"matches_{prefix}")
    innings = sub_df.groupby("striker_id").apply(lambda x: len(x[["match_id", "innings"]].drop_duplicates()), include_groups=False).rename(f"innings_{prefix}")
    opponents = grouped["bowling_team_id"].nunique().rename(f"opponents_{prefix}")

    res = pd.concat([bf, runs, fours, sixes, dots, dismissals, matches, innings, opponents], axis=1).fillna(0)

    # Derived rates
    bf_col = f"balls_faced_{prefix}"
    runs_col = f"runs_{prefix}"
    dots_col = f"dots_{prefix}"
    fours_col = f"fours_{prefix}"
    sixes_col = f"sixes_{prefix}"
    dis_col = f"dismissals_{prefix}"

    # Boundary runs
    res[f"boundary_runs_{prefix}"] = 4 * res[fours_col] + 6 * res[sixes_col]

    # Strike rate (runs / balls * 100)
    res[f"strike_rate_{prefix}"] = np.where(res[bf_col] > 0, np.round(100.0 * res[runs_col] / res[bf_col], 2), np.nan)

    # Dot percentage (dots / balls * 100)
    res[f"dot_pct_{prefix}"] = np.where(res[bf_col] > 0, np.round(100.0 * res[dots_col] / res[bf_col], 2), np.nan)

    # Boundary ball percentage (boundaries / balls * 100)
    res[f"boundary_ball_pct_{prefix}"] = np.where(res[bf_col] > 0, np.round(100.0 * (res[fours_col] + res[sixes_col]) / res[bf_col], 2), np.nan)

    # Boundary run percentage (boundary runs / total runs * 100)
    res[f"boundary_run_pct_{prefix}"] = np.where(res[runs_col] > 0, np.round(100.0 * res[f"boundary_runs_{prefix}"] / res[runs_col], 2), np.nan)

    # Dismissal rate per 100 balls
    res[f"dismissal_rate_per_100_{prefix}"] = np.where(res[bf_col] > 0, np.round(100.0 * res[dis_col] / res[bf_col], 2), np.nan)

    return res


def build_batter_analytics(df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """
    Builds the complete batter analytics dataset across High, Normal, Moderate, and Overall cohorts.
    """
    if df is None:
        logger.info("Loading clean cohort via task_05_cohort loader...")
        df = load_clean_cohort()

    logger.info(f"Computing batter analytics across {len(df)} deliveries...")

    # Canonical player name map (striker_id -> latest/most frequent striker_name)
    name_map = df.groupby("striker_id")["striker_name"].agg(lambda x: x.mode().iloc[0] if not x.empty else x.iloc[0]).to_dict()
    batting_hand_map = df.groupby("striker_id")["batting_type"].agg(lambda x: x.mode().iloc[0] if not x.empty and not x.isna().all() else "Unknown").to_dict()

    # Cohort masks using authoritative thresholds
    mask_high = df["batting_pressure_score"] >= 65.0
    mask_normal = df["batting_pressure_score"] < 40.0
    mask_mod = (df["batting_pressure_score"] >= 40.0) & (df["batting_pressure_score"] < 65.0)

    logger.info(f"Batting pressure delivery partition: High={mask_high.sum()}, Normal={mask_normal.sum()}, Moderate={mask_mod.sum()}")

    # Aggregations for each cohort
    df_high = df[mask_high]
    df_normal = df[mask_normal]
    df_mod = df[mask_mod]

    met_high = compute_batter_cohort_metrics(df_high, "high")
    met_normal = compute_batter_cohort_metrics(df_normal, "normal")
    met_mod = compute_batter_cohort_metrics(df_mod, "mod")
    met_overall = compute_batter_cohort_metrics(df, "overall")

    # Combine all unique striker IDs
    all_strikers = sorted(list(set(df["striker_id"].unique())))
    master_df = pd.DataFrame({"striker_id": all_strikers})
    master_df["striker_name"] = master_df["striker_id"].map(name_map)
    master_df["batting_type"] = master_df["striker_id"].map(batting_hand_map)

    # Merge cohort metrics
    for m in [met_overall, met_high, met_normal, met_mod]:
        if not m.empty:
            master_df = master_df.merge(m, on="striker_id", how="left")

    # Fill count fields with 0 where player had no exposure in that cohort
    count_cols = [c for c in master_df.columns if c.startswith(("balls_faced_", "runs_", "fours_", "sixes_", "dots_", "dismissals_", "matches_", "innings_", "opponents_", "boundary_runs_"))]
    master_df[count_cols] = master_df[count_cols].fillna(0)

    # Format-specific volume breakdowns
    ipl_mask = df["competition_category"].str.upper() == "IPL"
    t20i_mask = df["competition_category"].str.upper() == "T20I"

    bf_ipl = df[ipl_mask & df["is_batter_ball"]].groupby("striker_id").size().rename("balls_faced_ipl")
    bf_t20i = df[t20i_mask & df["is_batter_ball"]].groupby("striker_id").size().rename("balls_faced_t20i")

    bf_high_ipl = df[ipl_mask & mask_high & df["is_batter_ball"]].groupby("striker_id").size().rename("high_balls_faced_ipl")
    bf_high_t20i = df[t20i_mask & mask_high & df["is_batter_ball"]].groupby("striker_id").size().rename("high_balls_faced_t20i")

    format_df = pd.concat([bf_ipl, bf_t20i, bf_high_ipl, bf_high_t20i], axis=1).fillna(0)
    master_df = master_df.merge(format_df, on="striker_id", how="left").fillna({
        "balls_faced_ipl": 0, "balls_faced_t20i": 0,
        "high_balls_faced_ipl": 0, "high_balls_faced_t20i": 0
    })

    # Phase exposure in high pressure
    phase_clean = df["phase"].astype(str).str.strip().str.lower()
    high_pp = df[mask_high & df["is_batter_ball"] & (phase_clean == "powerplay")].groupby("striker_id").size().rename("high_balls_pp")
    high_mid = df[mask_high & df["is_batter_ball"] & (phase_clean == "middle")].groupby("striker_id").size().rename("high_balls_mid")
    high_death = df[mask_high & df["is_batter_ball"] & (phase_clean == "death")].groupby("striker_id").size().rename("high_balls_death")

    phase_df = pd.concat([high_pp, high_mid, high_death], axis=1).fillna(0)
    master_df = master_df.merge(phase_df, on="striker_id", how="left").fillna({
        "high_balls_pp": 0, "high_balls_mid": 0, "high_balls_death": 0
    })

    # --------------------------------------------------------------------------
    # Differentials (High Pressure vs Normal Pressure)
    # --------------------------------------------------------------------------
    # Delta Strike Rate = SR_high - SR_normal
    master_df["diff_strike_rate"] = np.where(
        master_df["balls_faced_high"] > 0 & (master_df["balls_faced_normal"] > 0),
        np.round(master_df["strike_rate_high"] - master_df["strike_rate_normal"], 2),
        np.nan
    )

    # Relative Delta Strike Rate = (SR_high - SR_normal) / SR_normal
    master_df["rel_diff_strike_rate"] = np.where(
        (master_df["balls_faced_high"] > 0) & (master_df["balls_faced_normal"] > 0) & (master_df["strike_rate_normal"] > 0),
        np.round((master_df["strike_rate_high"] - master_df["strike_rate_normal"]) / master_df["strike_rate_normal"], 4),
        np.nan
    )

    # Delta Dot Percentage = Dot%_high - Dot%_normal (negative is favorable)
    master_df["diff_dot_pct"] = np.where(
        (master_df["balls_faced_high"] > 0) & (master_df["balls_faced_normal"] > 0),
        np.round(master_df["dot_pct_high"] - master_df["dot_pct_normal"], 2),
        np.nan
    )

    # Delta Boundary Ball Percentage = Boundary%_high - Boundary%_normal (positive is favorable)
    master_df["diff_boundary_ball_pct"] = np.where(
        (master_df["balls_faced_high"] > 0) & (master_df["balls_faced_normal"] > 0),
        np.round(master_df["boundary_ball_pct_high"] - master_df["boundary_ball_pct_normal"], 2),
        np.nan
    )

    # Delta Dismissal Rate per 100 balls = DismissalRate_high - DismissalRate_normal (negative is favorable)
    master_df["diff_dismissal_rate_per_100"] = np.where(
        (master_df["balls_faced_high"] > 0) & (master_df["balls_faced_normal"] > 0),
        np.round(master_df["dismissal_rate_per_100_high"] - master_df["dismissal_rate_per_100_normal"], 2),
        np.nan
    )

    # Sort descending by high pressure balls faced
    master_df = master_df.sort_values(by=["balls_faced_high", "balls_faced_overall"], ascending=[False, False]).reset_index(drop=True)

    # Export CSV
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    master_df.to_csv(OUTPUT_PATH, index=False)
    logger.info(f"Batter metrics generated successfully for {len(master_df)} unique batters -> {OUTPUT_PATH}")
    return master_df


if __name__ == "__main__":
    df_metrics = build_batter_analytics()
    print(f"Top 5 batters by high-pressure exposure:")
    cols = ["striker_id", "striker_name", "balls_faced_overall", "balls_faced_high", "strike_rate_high", "balls_faced_normal", "strike_rate_normal", "diff_strike_rate"]
    print(df_metrics[cols].head(10).to_string())
