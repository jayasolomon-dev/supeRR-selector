"""
SUPERR SELECTOR - Master Data Preparation & Feature Pipeline
Prepares verified, reproducible delivery-level datasets for IPL and Men's T20I (2022+).
Calculates exact pre-delivery match state without future-data leakage.
"""

from pathlib import Path
from typing import Dict, Optional, Tuple
import logging
import sys
import numpy as np
import pandas as pd

# Ensure project root is in sys.path when script is run directly
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.features.match_state import compute_required_run_rate_and_chase_state

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# Cricket Constants & Ground Truth Rules
# ------------------------------------------------------------------------------
STANDARD_T20_LEGAL_BALLS = 120
STANDARD_T20_PAR_RUN_RATE = 8.5

BOWLER_CREDITED_DISMISSALS = {
    "Caught",
    "Bowled",
    "LBW",
    "Stump",
    "Hit Wicket",
}

NON_BOWLER_DISMISSALS = {
    "RunOut",
    "Retire Out",
    "Obstructing the field",
    "Obstracting the field",
}

# Competitions to exclude from official IPL and T20I rankings
EXCLUDED_COMPETITION_IDS = {"2670", "3289"}  # Regional developmental cups


def clean_id(val) -> str:
    """Standardizes IDs to clean strings, stripping any float '.0' artifacts."""
    if pd.isna(val) or val is None:
        return ""
    s = str(val).strip()
    if s.endswith(".0"):
        s = s[:-2]
    return s


def load_raw_datasets(data_dir: Path) -> Dict[str, pd.DataFrame]:
    """Loads all six audited raw CSV datasets."""
    files = {
        "competitions": "competitions.csv",
        "matches": "matches.csv",
        "ball_by_ball": "ball_by_ball.csv",
        "teams": "teams.csv",
        "playing_eleven": "playing_eleven.csv",
        "mapping": "competition_team_player_mapping.csv",
    }
    data = {}
    for key, filename in files.items():
        file_path = data_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Required CSV file missing: {file_path}")
        logger.info(f"Loading {filename} from {data_dir}...")
        data[key] = pd.read_csv(file_path, low_memory=False)
    return data


def filter_ipl_and_t20i(
    competitions_df: pd.DataFrame,
    matches_df: pd.DataFrame,
    bbb_df: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Filters datasets strictly to IPL and Men's T20I competitions from 2022 onwards.
    Excludes regional developmental tournaments (e.g. comp_id 2670, 3289).
    Preserves competition category, match ID, season, and format.
    """
    comps = competitions_df.copy()
    comps["clean_comp_id"] = comps["comp_id"].apply(clean_id)

    # Classify competition categories
    is_ipl = comps["comp_name"].str.contains("IPL", case=False, na=False)
    is_t20i = comps["match_format"].astype(str).str.upper() == "T20I"

    comps["competition_category"] = np.where(
        is_ipl, "IPL", np.where(is_t20i, "T20I", "Other")
    )

    # Filter out excluded regional competitions
    valid_comps = comps[
        comps["competition_category"].isin(["IPL", "T20I"]) &
        (~comps["clean_comp_id"].isin(EXCLUDED_COMPETITION_IDS))
    ].copy()

    valid_comp_ids = set(valid_comps["clean_comp_id"])

    # Filter matches
    matches = matches_df.copy()
    matches["clean_comp_id"] = matches["comp_id"].apply(clean_id)
    matches["clean_match_id"] = matches["match_id"].apply(clean_id)

    # Filter 2022 onwards and valid competitions
    matches["parsed_date"] = pd.to_datetime(matches["match_date"], errors="coerce")
    valid_matches = matches[
        matches["clean_comp_id"].isin(valid_comp_ids) &
        (matches["parsed_date"] >= "2022-01-01")
    ].copy()

    # Map competition metadata onto matches
    comp_meta = valid_comps.set_index("clean_comp_id")[["competition_category", "comp_name", "match_format", "season"]]
    valid_matches = valid_matches.join(comp_meta, on="clean_comp_id", how="inner")

    valid_match_ids = set(valid_matches["clean_match_id"])

    # Filter ball_by_ball deliveries
    bbb = bbb_df.copy()
    bbb["clean_match_id"] = bbb["match_id"].apply(clean_id)
    valid_bbb = bbb[bbb["clean_match_id"].isin(valid_match_ids)].copy()

    logger.info(
        f"Filtered Scope: {len(valid_comps)} Comps ({len(valid_comps[valid_comps['competition_category']=='IPL'])} IPL, "
        f"{len(valid_comps[valid_comps['competition_category']=='T20I'])} T20I), "
        f"{len(valid_matches)} Matches ({len(valid_matches[valid_matches['competition_category']=='IPL'])} IPL, "
        f"{len(valid_matches[valid_matches['competition_category']=='T20I'])} T20I), "
        f"{len(valid_bbb)} Deliveries."
    )

    return valid_comps, valid_matches, valid_bbb


def build_delivery_match_state(
    deliveries_df: pd.DataFrame,
    matches_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculates exact pre-delivery match state variables without future-data leakage:
    - score_before, wickets_before, legal_balls_before, legal_balls_remaining_before
    - target, required_runs_before, required_run_rate_before, current_run_rate_before
    - match phase (Powerplay, Middle, Death)
    - delivery execution tags: is_legal_ball, is_batter_ball, bowler_runs_conceded, is_bowler_wicket
    """
    df = deliveries_df.copy()

    # 1. Strictly Chronological Ordering within each match and innings
    df["clean_match_id"] = df["match_id"].apply(clean_id)
    df = df.sort_values(["clean_match_id", "innings", "innings_ball_num", "overid", "over_ball_num"]).reset_index(drop=True)

    # 2. Extract Delivery Runs and Extras
    runs_bat = pd.to_numeric(df.get("runs", 0), errors="coerce").fillna(0).astype(int)
    ext1 = pd.to_numeric(df.get("extras1_runs", 0), errors="coerce").fillna(0).astype(int)
    ext2 = pd.to_numeric(df.get("extras_2_runs", 0), errors="coerce").fillna(0).astype(int)

    df["ball_total_runs"] = runs_bat + ext1 + ext2
    df["runs_off_bat"] = runs_bat

    # 3. Classify Legality and Balls Faced
    clean_extras = df["extras_type"].astype(str).str.strip().str.lower()
    df["is_wide"] = clean_extras == "wide"
    df["is_noball"] = clean_extras.isin(["overstep", "other"])
    df["is_bye"] = clean_extras == "byes"
    df["is_legbye"] = clean_extras == "legbyes"

    # Bowler legal deliveries: exclude wides and no-balls (overstep and other)
    df["is_legal_ball"] = ~clean_extras.isin(["wide", "overstep", "other"])

    # Batter balls faced: exclude wides only (no-balls count as balls faced)
    df["is_batter_ball"] = clean_extras != "wide"

    # 4. Bowler Runs Conceded & Wicket Credits
    # Bowler runs conceded = bat runs + wide penalties + no-ball penalties (ext1 only).
    # Secondary extras (ext2 = byes/leg-byes off no-balls) are team extras and NOT debited to bowler.
    is_bowler_penalty = clean_extras.isin(["wide", "overstep", "other"])
    df["bowler_runs_conceded"] = runs_bat + np.where(is_bowler_penalty, ext1, 0)

    is_wkt_bool = df["is_wicket"].astype(str).str.strip().str.lower().isin(["true", "1", "t", "yes"])
    dismissal_clean = df["dismissal_type"].astype(str).str.strip()
    df["is_bowler_wicket"] = is_wkt_bool & dismissal_clean.isin(BOWLER_CREDITED_DISMISSALS)

    # Striker dismissed flag
    striker_str = df["striker_id"].apply(clean_id)
    dismissed_str = df["dismissed_player_id"].apply(clean_id)
    df["is_batter_out"] = is_wkt_bool & (striker_str == dismissed_str)

    # Dot balls
    df["is_dot_ball"] = (runs_bat == 0) & (clean_extras == "none")

    # 5. Match Phase Categorization
    conditions = [
        df["overid"] <= 6,
        (df["overid"] >= 7) & (df["overid"] <= 15),
        df["overid"] >= 16,
    ]
    df["phase"] = np.select(conditions, ["Powerplay", "Middle", "Death"], default="Middle")

    # 6. Grouped Cumulative Sums (Shifted for Pre-Delivery State)
    df["is_wicket_ball"] = is_wkt_bool.astype(int)
    df["is_legal_ball_int"] = df["is_legal_ball"].astype(int)

    grp = df.groupby(["clean_match_id", "innings"], observed=True)
    df["score_before"] = grp["ball_total_runs"].cumsum() - df["ball_total_runs"]
    df["wickets_before"] = grp["is_wicket_ball"].cumsum() - df["is_wicket_ball"]
    df["legal_balls_before"] = grp["is_legal_ball_int"].cumsum() - df["is_legal_ball_int"]

    # 7. Match Metadata Lookup for DLS Revised Targets & Overs
    # DLS Unit Guardrails:
    # - first_inn_revised_overs and second_inn_revised_overs in matches.csv are in LEGAL BALLS (not overs).
    #   (e.g., 90.0 = 15 overs = 90 legal balls; 48.0 = 8 overs = 48 legal balls; 30.0 = 5 overs = 30 legal balls).
    # - revised_target is in RUNS.
    matches_meta = {}
    for _, r in matches_df.iterrows():
        mid = clean_id(r["match_id"])
        rev1 = r.get("first_inn_revised_overs")
        rev2 = r.get("second_inn_revised_overs")
        rev_t = r.get("revised_target")
        matches_meta[mid] = {
            "rev_inn1_balls": int(float(rev1)) if pd.notnull(rev1) and float(rev1) > 0 else None,
            "rev_inn2_balls": int(float(rev2)) if pd.notnull(rev2) and float(rev2) > 0 else None,
            "rev_target": int(float(rev_t)) if pd.notnull(rev_t) and float(rev_t) > 0 else None,
            "comp_id": clean_id(r.get("comp_id")),
            "comp_name": r.get("comp_name"),
            "competition_category": r.get("competition_category"),
            "match_format": r.get("match_format"),
            "season": str(r.get("season")),
            "match_date": r.get("match_date"),
        }

    # Innings 1 Final Scores
    inn1_totals = {}
    for mid, sub_grp in df[df["innings"] == 1].groupby("clean_match_id", observed=True):
        inn1_totals[clean_id(mid)] = int(sub_grp["ball_total_runs"].sum())

    # Map Total Legal Balls per Innings
    def get_innings_capacity(row) -> int:
        mid = row["clean_match_id"]
        inn = int(row["innings"])
        m_info = matches_meta.get(mid, {})
        if inn == 1:
            return m_info.get("rev_inn1_balls") or STANDARD_T20_LEGAL_BALLS
        else:
            return m_info.get("rev_inn2_balls") or m_info.get("rev_inn1_balls") or STANDARD_T20_LEGAL_BALLS

    # Map Target for Innings 2
    def get_innings_target(row) -> float:
        if int(row["innings"]) != 2:
            return np.nan
        mid = row["clean_match_id"]
        m_info = matches_meta.get(mid, {})
        rev_t = m_info.get("rev_target")
        if rev_t is not None:
            return float(rev_t)
        inn1_score = inn1_totals.get(mid, 0)
        return float(inn1_score + 1)

    df["total_legal_balls"] = df.apply(get_innings_capacity, axis=1)
    df["target"] = df.apply(get_innings_target, axis=1)

    # 8. Remaining Legal Balls Before Delivery
    df["legal_balls_remaining_before"] = np.maximum(
        0, df["total_legal_balls"] - df["legal_balls_before"]
    )

    # 9. Current Run Rate Before Delivery (Safe division: NaN before first legal ball)
    safe_balls_bowled = np.where(df["legal_balls_before"] > 0, df["legal_balls_before"], 1)
    df["current_run_rate_before"] = np.where(
        df["legal_balls_before"] > 0,
        np.round((df["score_before"] / safe_balls_bowled) * 6.0, 2),
        np.nan
    )

    # 10. Required Runs, Required Run Rate & Impossible Chase State Before Delivery (Innings 2)
    is_inn2 = df["innings"] == 2
    df["required_runs_before"] = np.where(
        is_inn2,
        np.maximum(0, df["target"] - df["score_before"]),
        np.nan
    )

    df["required_run_rate_before"], df["impossible_chase_state"] = compute_required_run_rate_and_chase_state(
        innings=df["innings"],
        legal_balls_remaining_before=df["legal_balls_remaining_before"],
        required_runs_before=df["required_runs_before"],
    )

    # 11. Add Match & Tournament Metadata
    df["comp_id"] = df["clean_match_id"].map(lambda m: matches_meta.get(m, {}).get("comp_id"))
    df["comp_name"] = df["clean_match_id"].map(lambda m: matches_meta.get(m, {}).get("comp_name"))
    df["competition_category"] = df["clean_match_id"].map(lambda m: matches_meta.get(m, {}).get("competition_category"))
    df["match_format"] = df["clean_match_id"].map(lambda m: matches_meta.get(m, {}).get("match_format"))
    df["season"] = df["clean_match_id"].map(lambda m: matches_meta.get(m, {}).get("season"))
    df["match_date"] = df["clean_match_id"].map(lambda m: matches_meta.get(m, {}).get("match_date"))

    return df


def build_batting_performance_dataset(deliveries_df: pd.DataFrame) -> pd.DataFrame:
    """Prepares structured delivery dataset from the striker/batter perspective."""
    cols = [
        "striker_id", "striker_name", "match_id", "comp_id", "competition_category",
        "match_format", "season", "match_date", "innings", "overid", "over_ball_num",
        "innings_ball_num", "phase", "score_before", "wickets_before", "legal_balls_before",
        "legal_balls_remaining_before", "target", "required_runs_before", "required_run_rate_before",
        "current_run_rate_before", "impossible_chase_state", "batting_type", "batting_order", "runs_off_bat",
        "is_four", "is_six", "is_wicket", "is_batter_out", "is_batter_ball",
        "is_dot_ball", "pace_or_spin", "stroke", "bowler_id", "bowler_name"
    ]
    clean_cols = [c for c in cols if c in deliveries_df.columns]
    bat_df = deliveries_df[clean_cols].copy().rename(columns={
        "striker_id": "player_id",
        "striker_name": "player_name",
        "runs_off_bat": "runs_scored",
    })
    return bat_df


def build_bowling_performance_dataset(deliveries_df: pd.DataFrame) -> pd.DataFrame:
    """Prepares structured delivery dataset from the bowler perspective."""
    cols = [
        "bowler_id", "bowler_name", "match_id", "comp_id", "competition_category",
        "match_format", "season", "match_date", "innings", "overid", "over_ball_num",
        "innings_ball_num", "phase", "score_before", "wickets_before", "legal_balls_before",
        "legal_balls_remaining_before", "target", "required_runs_before", "required_run_rate_before",
        "current_run_rate_before", "impossible_chase_state", "bowling_type", "pace_or_spin", "is_legal_ball",
        "is_wide", "is_noball", "is_bye", "is_legbye", "bowler_runs_conceded",
        "is_bowler_wicket", "is_dot_ball", "striker_id", "striker_name"
    ]
    clean_cols = [c for c in cols if c in deliveries_df.columns]
    bowl_df = deliveries_df[clean_cols].copy().rename(columns={
        "bowler_id": "player_id",
        "bowler_name": "player_name",
    })
    return bowl_df


def run_pipeline(
    data_dir: Path = Path("data/raw"),
    output_dir: Path = Path("data/processed"),
) -> Dict[str, pd.DataFrame]:
    """Executes the complete end-to-end data preparation pipeline."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load Raw Datasets
    raw_data = load_raw_datasets(data_dir)

    # 2. Filter Scope (IPL & Men's T20I, 2022 onwards)
    v_comps, v_matches, v_bbb = filter_ipl_and_t20i(
        raw_data["competitions"], raw_data["matches"], raw_data["ball_by_ball"]
    )

    # 3. Build Pre-Delivery Match States
    logger.info("Computing pre-delivery match states without future leakage...")
    processed_deliveries = build_delivery_match_state(v_bbb, v_matches)

    # 4. Generate Core Output Datasets
    logger.info("Generating specialized tournament and player performance datasets...")
    ipl_deliveries = processed_deliveries[processed_deliveries["competition_category"] == "IPL"].copy()
    t20i_deliveries = processed_deliveries[processed_deliveries["competition_category"] == "T20I"].copy()
    batting_deliveries = build_batting_performance_dataset(processed_deliveries)
    bowling_deliveries = build_bowling_performance_dataset(processed_deliveries)

    # 5. Save to data/processed/
    logger.info(f"Writing CSV deliverables to {output_dir}...")
    ipl_deliveries.to_csv(output_dir / "ipl_deliveries.csv", index=False)
    t20i_deliveries.to_csv(output_dir / "t20i_deliveries.csv", index=False)
    batting_deliveries.to_csv(output_dir / "batting_deliveries.csv", index=False)
    bowling_deliveries.to_csv(output_dir / "bowling_deliveries.csv", index=False)

    logger.info("Pipeline execution completed successfully.")
    return {
        "processed_deliveries": processed_deliveries,
        "ipl_deliveries": ipl_deliveries,
        "t20i_deliveries": t20i_deliveries,
        "batting_deliveries": batting_deliveries,
        "bowling_deliveries": bowling_deliveries,
    }


if __name__ == "__main__":
    run_pipeline()
