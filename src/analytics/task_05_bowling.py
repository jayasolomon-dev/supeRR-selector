"""
SUPERR SELECTOR - Master Task 05 Bowling Analytics Pipeline
Module: src/analytics/task_05_bowling.py

Calculates comprehensive, verified delivery-level bowling analytics partitioned into:
- High Pressure: bowling_pressure_score >= 65.0 (High + Extreme tiers)
- Normal Pressure: bowling_pressure_score < 40.0 (Low tier)
- Moderate Pressure: 40.0 <= bowling_pressure_score < 65.0 (Intermediate tier)
- Overall Standard Competitive Cohort

All metrics preserve raw numerators and denominators to prevent division-by-zero distortion.
Outputs data/analytics/task_05_bowler_metrics.csv.
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

logger = logging.getLogger("task_05_bowling")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s [%(name)s]: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

OUTPUT_DIR = os.path.join(ROOT_DIR, "data", "analytics")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "task_05_bowler_metrics.csv")


def compute_bowler_cohort_metrics(sub_df: pd.DataFrame, prefix: str) -> pd.DataFrame:
    """
    Computes aggregated bowling metrics for a specific pressure subset of deliveries.
    """
    if sub_df.empty:
        return pd.DataFrame()

    grouped = sub_df.groupby("bowler_id")

    # Legal deliveries (excludes wides and noballs)
    legal_balls = sub_df[sub_df["is_legal_ball"]].groupby("bowler_id").size().rename(f"legal_balls_{prefix}")
    runs = sub_df.groupby("bowler_id")["bowler_runs_conceded"].sum().rename(f"runs_conceded_{prefix}")
    wickets = sub_df[sub_df["is_bowler_wicket"]].groupby("bowler_id").size().rename(f"wickets_{prefix}")
    # Correct cricket bowling dot balls: legal ball where 0 runs conceded by bowler
    is_dot_ball_bowl = sub_df["is_legal_ball"] & (sub_df["bowler_runs_conceded"] == 0)
    dots = sub_df[is_dot_ball_bowl].groupby("bowler_id").size().rename(f"dots_{prefix}")
    fours = sub_df[sub_df["is_four"]].groupby("bowler_id").size().rename(f"fours_conceded_{prefix}")
    sixes = sub_df[sub_df["is_six"]].groupby("bowler_id").size().rename(f"sixes_conceded_{prefix}")
    wides = sub_df[sub_df["is_wide"]].groupby("bowler_id").size().rename(f"wides_{prefix}")
    noballs = sub_df[sub_df["is_noball"]].groupby("bowler_id").size().rename(f"noballs_{prefix}")
    matches = grouped["match_id"].nunique().rename(f"matches_{prefix}")
    innings = sub_df.groupby("bowler_id").apply(lambda x: len(x[["match_id", "innings"]].drop_duplicates()), include_groups=False).rename(f"innings_{prefix}")
    opponents = grouped["batting_team_id"].nunique().rename(f"opponents_{prefix}")

    res = pd.concat([legal_balls, runs, wickets, dots, fours, sixes, wides, noballs, matches, innings, opponents], axis=1).fillna(0)

    # Derived rates
    lb_col = f"legal_balls_{prefix}"
    runs_col = f"runs_conceded_{prefix}"
    wkt_col = f"wickets_{prefix}"
    dots_col = f"dots_{prefix}"
    fours_col = f"fours_conceded_{prefix}"
    sixes_col = f"sixes_conceded_{prefix}"

    # Overs bowled (legal balls / 6)
    res[f"overs_{prefix}"] = np.round(res[lb_col] / 6.0, 2)

    # Economy rate (6 * runs / legal balls)
    res[f"economy_rate_{prefix}"] = np.where(res[lb_col] > 0, np.round(6.0 * res[runs_col] / res[lb_col], 2), np.nan)

    # Wickets per over (6 * wickets / legal balls)
    res[f"wickets_per_over_{prefix}"] = np.where(res[lb_col] > 0, np.round(6.0 * res[wkt_col] / res[lb_col], 3), np.nan)

    # Bowling strike rate (legal balls / wickets)
    res[f"bowling_strike_rate_{prefix}"] = np.where(res[wkt_col] > 0, np.round(res[lb_col] / res[wkt_col], 2), np.nan)

    # Dot ball percentage (dots / legal balls * 100)
    res[f"dot_pct_{prefix}"] = np.where(res[lb_col] > 0, np.round(100.0 * res[dots_col] / res[lb_col], 2), np.nan)

    # Boundary conceded percentage ((fours + sixes) / legal balls * 100)
    res[f"boundary_conceded_pct_{prefix}"] = np.where(
        res[lb_col] > 0,
        np.round(100.0 * (res[fours_col] + res[sixes_col]) / res[lb_col], 2),
        np.nan
    )

    return res


def build_bowler_analytics(df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """
    Builds the complete bowler analytics dataset across High, Normal, Moderate, and Overall cohorts.
    """
    if df is None:
        logger.info("Loading clean cohort via task_05_cohort loader...")
        df = load_clean_cohort()

    logger.info(f"Computing bowler analytics across {len(df)} deliveries...")

    # Canonical player name map and style
    name_map = df.groupby("bowler_id")["bowler_name"].agg(lambda x: x.mode().iloc[0] if not x.empty else x.iloc[0]).to_dict()
    bowling_type_map = df.groupby("bowler_id")["bowling_type"].agg(lambda x: x.mode().iloc[0] if not x.empty and not x.isna().all() else "Unknown").to_dict()
    pace_spin_map = df.groupby("bowler_id")["pace_or_spin"].agg(lambda x: x.mode().iloc[0] if not x.empty and not x.isna().all() else "Unknown").to_dict()

    # Cohort masks using authoritative thresholds
    mask_high = df["bowling_pressure_score"] >= 65.0
    mask_normal = df["bowling_pressure_score"] < 40.0
    mask_mod = (df["bowling_pressure_score"] >= 40.0) & (df["bowling_pressure_score"] < 65.0)

    logger.info(f"Bowling pressure delivery partition: High={mask_high.sum()}, Normal={mask_normal.sum()}, Moderate={mask_mod.sum()}")

    # Aggregations for each cohort
    df_high = df[mask_high]
    df_normal = df[mask_normal]
    df_mod = df[mask_mod]

    met_high = compute_bowler_cohort_metrics(df_high, "high")
    met_normal = compute_bowler_cohort_metrics(df_normal, "normal")
    met_mod = compute_bowler_cohort_metrics(df_mod, "mod")
    met_overall = compute_bowler_cohort_metrics(df, "overall")

    # Combine all unique bowler IDs
    all_bowlers = sorted(list(set(df["bowler_id"].unique())))
    master_df = pd.DataFrame({"bowler_id": all_bowlers})
    master_df["bowler_name"] = master_df["bowler_id"].map(name_map)
    master_df["bowling_type"] = master_df["bowler_id"].map(bowling_type_map)
    master_df["pace_or_spin"] = master_df["bowler_id"].map(pace_spin_map)

    # Merge cohort metrics
    for m in [met_overall, met_high, met_normal, met_mod]:
        if not m.empty:
            master_df = master_df.merge(m, on="bowler_id", how="left")

    # Fill count fields with 0 where player had no exposure in that cohort
    count_cols = [c for c in master_df.columns if c.startswith(("legal_balls_", "runs_conceded_", "wickets_", "dots_", "fours_conceded_", "sixes_conceded_", "wides_", "noballs_", "matches_", "innings_", "opponents_"))]
    master_df[count_cols] = master_df[count_cols].fillna(0)

    # Format-specific volume breakdowns
    ipl_mask = df["competition_category"].str.upper() == "IPL"
    t20i_mask = df["competition_category"].str.upper() == "T20I"

    lb_ipl = df[ipl_mask & df["is_legal_ball"]].groupby("bowler_id").size().rename("legal_balls_ipl")
    lb_t20i = df[t20i_mask & df["is_legal_ball"]].groupby("bowler_id").size().rename("legal_balls_t20i")

    lb_high_ipl = df[ipl_mask & mask_high & df["is_legal_ball"]].groupby("bowler_id").size().rename("high_legal_balls_ipl")
    lb_high_t20i = df[t20i_mask & mask_high & df["is_legal_ball"]].groupby("bowler_id").size().rename("high_legal_balls_t20i")

    format_df = pd.concat([lb_ipl, lb_t20i, lb_high_ipl, lb_high_t20i], axis=1).fillna(0)
    master_df = master_df.merge(format_df, on="bowler_id", how="left").fillna({
        "legal_balls_ipl": 0, "legal_balls_t20i": 0,
        "high_legal_balls_ipl": 0, "high_legal_balls_t20i": 0
    })

    # Phase exposure in high pressure
    phase_clean = df["phase"].astype(str).str.strip().str.lower()
    high_pp = df[mask_high & df["is_legal_ball"] & (phase_clean == "powerplay")].groupby("bowler_id").size().rename("high_balls_pp")
    high_mid = df[mask_high & df["is_legal_ball"] & (phase_clean == "middle")].groupby("bowler_id").size().rename("high_balls_mid")
    high_death = df[mask_high & df["is_legal_ball"] & (phase_clean == "death")].groupby("bowler_id").size().rename("high_balls_death")

    phase_df = pd.concat([high_pp, high_mid, high_death], axis=1).fillna(0)
    master_df = master_df.merge(phase_df, on="bowler_id", how="left").fillna({
        "high_balls_pp": 0, "high_balls_mid": 0, "high_balls_death": 0
    })

    # --------------------------------------------------------------------------
    # Differentials (High Pressure vs Normal Pressure)
    # --------------------------------------------------------------------------
    # Delta Economy Rate = Econ_high - Econ_normal (negative indicates tighter bowling under pressure; favorable)
    master_df["diff_economy_rate"] = np.where(
        (master_df["legal_balls_high"] > 0) & (master_df["legal_balls_normal"] > 0),
        np.round(master_df["economy_rate_high"] - master_df["economy_rate_normal"], 2),
        np.nan
    )

    # Relative Delta Economy Rate = (Econ_high - Econ_normal) / Econ_normal
    master_df["rel_diff_economy_rate"] = np.where(
        (master_df["legal_balls_high"] > 0) & (master_df["legal_balls_normal"] > 0) & (master_df["economy_rate_normal"] > 0),
        np.round((master_df["economy_rate_high"] - master_df["economy_rate_normal"]) / master_df["economy_rate_normal"], 4),
        np.nan
    )

    # Delta Wickets per Over = WktPerOver_high - WktPerOver_normal (positive is favorable)
    master_df["diff_wickets_per_over"] = np.where(
        (master_df["legal_balls_high"] > 0) & (master_df["legal_balls_normal"] > 0),
        np.round(master_df["wickets_per_over_high"] - master_df["wickets_per_over_normal"], 3),
        np.nan
    )

    # Delta Dot Percentage = Dot%_high - Dot%_normal (positive is favorable)
    master_df["diff_dot_pct"] = np.where(
        (master_df["legal_balls_high"] > 0) & (master_df["legal_balls_normal"] > 0),
        np.round(master_df["dot_pct_high"] - master_df["dot_pct_normal"], 2),
        np.nan
    )

    # Delta Boundary Conceded % = Boundary%_high - Boundary%_normal (negative is favorable)
    master_df["diff_boundary_conceded_pct"] = np.where(
        (master_df["legal_balls_high"] > 0) & (master_df["legal_balls_normal"] > 0),
        np.round(master_df["boundary_conceded_pct_high"] - master_df["boundary_conceded_pct_normal"], 2),
        np.nan
    )

    # Sort descending by high pressure legal balls bowled
    master_df = master_df.sort_values(by=["legal_balls_high", "legal_balls_overall"], ascending=[False, False]).reset_index(drop=True)

    # Export CSV
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    master_df.to_csv(OUTPUT_PATH, index=False)
    logger.info(f"Bowler metrics generated successfully for {len(master_df)} unique bowlers -> {OUTPUT_PATH}")
    return master_df


if __name__ == "__main__":
    df_metrics = build_bowler_analytics()
    print(f"Top 10 bowlers by high-pressure exposure:")
    cols = ["bowler_id", "bowler_name", "legal_balls_overall", "legal_balls_high", "economy_rate_high", "legal_balls_normal", "economy_rate_normal", "diff_economy_rate"]
    print(df_metrics[cols].head(10).to_string())
