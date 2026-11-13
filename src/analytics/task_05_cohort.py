"""
SUPERR SELECTOR - Master Task 05 Clean Cohort Loader
Module: src/analytics/task_05_cohort.py

Authoritative clean cohort loader implementing Task 04.2B.1 certified rules:
1. Standard 20-over matches only (innings <= 2), strictly quarantining Super Overs.
2. Terminal post-conclusion residual deliveries excluded (is_target_met_delivery == False).
3. Match-winning deliveries preserved with authentic pre-delivery match pressure.
4. Exact census enforcement:
   - IPL: 87,673 deliveries
   - T20I: 106,303 deliveries
   - Combined: 193,976 deliveries
"""

import os
import logging
from typing import Optional, List, Tuple
import pandas as pd
import numpy as np

logger = logging.getLogger("task_05_cohort")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s [%(name)s]: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# Certified cohort census constants
EXPECTED_IPL_ROWS = 87673
EXPECTED_T20I_ROWS = 106303
EXPECTED_COMBINED_ROWS = 193976

EXPECTED_IPL_MATCHES = 367
EXPECTED_T20I_MATCHES = 470
EXPECTED_COMBINED_MATCHES = 837

DEFAULT_IPL_PATH = os.path.join("data", "derived", "pressure_scored_ipl.csv")
DEFAULT_T20I_PATH = os.path.join("data", "derived", "pressure_scored_t20i.csv")

# Standard columns preserved for Task 05 analytics
ANALYTICS_COLUMNS = [
    # Primary delivery keys & sequence
    "match_id", "innings", "overid", "over_ball_num", "innings_ball_num",
    # Competition & metadata
    "competition_category", "comp_id", "comp_name", "match_format", "season", "match_date",
    # Team & player identifiers
    "batting_team_id", "bowling_team_id",
    "striker_id", "striker_name", "non_striker_id", "non_striker_name",
    "bowler_id", "bowler_name",
    "batting_type", "bowling_type", "batting_order", "pace_or_spin",
    "phase",
    # Ball execution & outcomes
    "runs", "runs_off_bat", "ball_total_runs",
    "is_four", "is_six", "is_dot_ball",
    "is_legal_ball", "is_batter_ball", "is_wide", "is_noball", "is_bye", "is_legbye",
    "extras_type", "extras1_runs", "extras_2_runs",
    "bowler_runs_conceded",
    "is_wicket", "dismissal_type_id", "dismissal_type", "dismissed_player_id",
    "is_bowler_wicket", "is_batter_out",
    # Match state baselines
    "score_before", "wickets_before", "legal_balls_before", "total_legal_balls",
    "legal_balls_remaining_before", "target", "required_runs_before",
    "required_run_rate_before", "current_run_rate_before", "par_run_rate_comp",
    # Pressure continuous scores & categorical bins
    "batting_pressure_score", "bowling_pressure_score",
    "batting_pressure_cat", "bowling_pressure_cat",
    # Explainability subcomponents
    "bat_comp_pace_urgency", "bat_comp_resource_stress", "bat_comp_phase_urgency", "bat_comp_crunch_mult",
    "bowl_comp_containment", "bowl_comp_death_defense", "bowl_comp_runway", "bowl_comp_boundary_threat", "bowl_comp_depth_stress",
    # Edge-case & quality flags
    "is_target_met_delivery", "is_dls_shortened", "is_early_delivery", "is_extreme_rrr_bounded"
]


def load_clean_dataset(filepath: str, format_label: str) -> pd.DataFrame:
    """
    Loads a single derived pressure CSV and applies the certified standard cohort filter:
      (df['innings'] <= 2) & (~df['is_target_met_delivery'])
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Derived pressure dataset not found at: {filepath}")

    logger.info(f"Loading {format_label} dataset from {filepath}...")
    df = pd.read_csv(filepath, low_memory=False)

    raw_count = len(df)
    clean_mask = (df["innings"] <= 2) & (~df["is_target_met_delivery"].fillna(False).astype(bool))
    clean_df = df.loc[clean_mask].copy()

    # Verify column presence and subset safely
    available_cols = [c for c in ANALYTICS_COLUMNS if c in clean_df.columns]
    missing_cols = set(ANALYTICS_COLUMNS) - set(available_cols)
    if missing_cols:
        logger.warning(f"{format_label}: {len(missing_cols)} requested columns missing: {missing_cols}")
    clean_df = clean_df[available_cols].copy()

    # Format label guarantee
    if "competition_category" not in clean_df.columns or clean_df["competition_category"].isnull().all():
        clean_df["competition_category"] = format_label
    else:
        clean_df["competition_category"] = clean_df["competition_category"].fillna(format_label)

    # Composite primary key verification
    clean_df["delivery_index"] = clean_df.groupby(["match_id", "innings"]).cumcount() + 1

    clean_count = len(clean_df)
    logger.info(f"{format_label}: Raw rows = {raw_count} -> Clean cohort rows = {clean_count}")
    return clean_df


def load_clean_cohort(
    ipl_path: str = DEFAULT_IPL_PATH,
    t20i_path: str = DEFAULT_T20I_PATH,
    format_filter: Optional[str] = None,
    enforce_census: bool = True
) -> pd.DataFrame:
    """
    Loads and reconciles the clean player analytics cohort.
    
    Args:
        ipl_path: Path to pressure_scored_ipl.csv
        t20i_path: Path to pressure_scored_t20i.csv
        format_filter: Optional filter ('IPL', 'T20I', or None for Combined)
        enforce_census: When True, raises ValueError if counts do not exactly match certified census.
        
    Returns:
        pd.DataFrame containing the validated clean cohort.
    """
    format_clean = format_filter.upper().strip() if format_filter else None

    if format_clean == "IPL":
        df = load_clean_dataset(ipl_path, "IPL")
        if enforce_census and len(df) != EXPECTED_IPL_ROWS:
            raise ValueError(f"IPL census mismatch: Expected {EXPECTED_IPL_ROWS}, got {len(df)}")
        return df

    elif format_clean in ["T20I", "INTERNATIONAL"]:
        df = load_clean_dataset(t20i_path, "T20I")
        if enforce_census and len(df) != EXPECTED_T20I_ROWS:
            raise ValueError(f"T20I census mismatch: Expected {EXPECTED_T20I_ROWS}, got {len(df)}")
        return df

    else:
        df_ipl = load_clean_dataset(ipl_path, "IPL")
        df_t20i = load_clean_dataset(t20i_path, "T20I")

        if enforce_census:
            if len(df_ipl) != EXPECTED_IPL_ROWS:
                raise ValueError(f"IPL census mismatch: Expected {EXPECTED_IPL_ROWS}, got {len(df_ipl)}")
            if len(df_t20i) != EXPECTED_T20I_ROWS:
                raise ValueError(f"T20I census mismatch: Expected {EXPECTED_T20I_ROWS}, got {len(df_t20i)}")

        combined_df = pd.concat([df_ipl, df_t20i], ignore_index=True)

        if enforce_census and len(combined_df) != EXPECTED_COMBINED_ROWS:
            raise ValueError(f"Combined census mismatch: Expected {EXPECTED_COMBINED_ROWS}, got {len(combined_df)}")

        logger.info(f"Successfully loaded combined clean cohort: {len(combined_df)} deliveries across {combined_df['match_id'].nunique()} matches.")
        return combined_df


if __name__ == "__main__":
    df = load_clean_cohort()
    print(f"Loaded clean cohort successfully: {len(df)} deliveries, {df['match_id'].nunique()} matches.")

