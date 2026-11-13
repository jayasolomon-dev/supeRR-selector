"""
SUPERR SELECTOR - Data Ingestion & Loader Module
Loads, validates, and cleans raw cricket CSV data without modifying source files.
"""

from pathlib import Path
import logging
from typing import Dict, Optional, Tuple
import pandas as pd
import numpy as np

try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

from src.config import (
    get_raw_data_directory,
    BALL_BY_BALL_FILE,
    MATCHES_FILE,
    PLAYING_ELEVEN_FILE,
    MAPPING_FILE,
    COMPETITIONS_FILE,
    TEAMS_FILE,
)

logger = logging.getLogger(__name__)


def _cache_decorator(func):
    """Applies st.cache_data if running within Streamlit, else returns unmodified func."""
    if HAS_STREAMLIT:
        return st.cache_data(show_spinner="Loading cricket analytics datasets...")(func)
    return func


def _to_bool_series(series: pd.Series) -> pd.Series:
    """Converts mixed string/bool representations ('true', 'false', '1', '0') to boolean."""
    return (
        series.astype(str)
        .str.strip()
        .str.lower()
        .isin(["true", "1", "t", "yes", "y"])
    )


def load_competitions(data_dir: Optional[Path] = None) -> pd.DataFrame:
    """Loads competitions metadata."""
    dir_path = data_dir or get_raw_data_directory()
    file_path = dir_path / COMPETITIONS_FILE
    if not file_path.exists():
        logger.warning(f"File not found: {file_path}")
        return pd.DataFrame()
    
    df = pd.read_csv(file_path, dtype={"comp_id": str, "season": str})
    df.columns = [c.strip() for c in df.columns]
    return df


def load_teams(data_dir: Optional[Path] = None) -> pd.DataFrame:
    """Loads team metadata and mappings."""
    dir_path = data_dir or get_raw_data_directory()
    file_path = dir_path / TEAMS_FILE
    if not file_path.exists():
        logger.warning(f"File not found: {file_path}")
        return pd.DataFrame()
    
    df = pd.read_csv(file_path, dtype={"comp_id": str, "team_id": str})
    df.columns = [c.strip() for c in df.columns]
    return df


def load_matches(data_dir: Optional[Path] = None) -> pd.DataFrame:
    """Loads match level records with parsed dates and clean identifiers."""
    dir_path = data_dir or get_raw_data_directory()
    file_path = dir_path / MATCHES_FILE
    if not file_path.exists():
        logger.warning(f"File not found: {file_path}")
        return pd.DataFrame()
    
    df = pd.read_csv(
        file_path,
        dtype={
            "match_id": str,
            "comp_id": str,
            "venue_id": str,
            "home_team_id": str,
            "away_team_id": str,
            "toss_win_team_id": str,
            "win_team_id": str,
        },
    )
    df.columns = [c.strip() for c in df.columns]
    if "match_date" in df.columns:
        df["match_date"] = pd.to_datetime(df["match_date"], errors="coerce")
    return df


def load_playing_eleven(data_dir: Optional[Path] = None) -> pd.DataFrame:
    """Loads match playing XI appearances and roles."""
    dir_path = data_dir or get_raw_data_directory()
    file_path = dir_path / PLAYING_ELEVEN_FILE
    if not file_path.exists():
        logger.warning(f"File not found: {file_path}")
        return pd.DataFrame()
    
    df = pd.read_csv(
        file_path,
        dtype={
            "match_id": str,
            "team_id": str,
            "player_id": str,
        },
    )
    df.columns = [c.strip() for c in df.columns]
    for col in ["is_played", "is_captain", "is_wk"]:
        if col in df.columns:
            df[col] = _to_bool_series(df[col])
    return df


def load_player_mappings(data_dir: Optional[Path] = None) -> pd.DataFrame:
    """Loads competition-team-player name and ID mappings."""
    dir_path = data_dir or get_raw_data_directory()
    file_path = dir_path / MAPPING_FILE
    if not file_path.exists():
        logger.warning(f"File not found: {file_path}")
        return pd.DataFrame()
    
    df = pd.read_csv(
        file_path,
        dtype={"comp_id": str, "team_id": str, "player_id": str},
    )
    df.columns = [c.strip() for c in df.columns]
    return df


def load_ball_by_ball(data_dir: Optional[Path] = None, nrows: Optional[int] = None) -> pd.DataFrame:
    """
    Loads ball-by-ball delivery events with optimized dtypes.
    Source CSV files are read-only and never modified.
    """
    dir_path = data_dir or get_raw_data_directory()
    file_path = dir_path / BALL_BY_BALL_FILE
    if not file_path.exists():
        logger.error(f"Ball by ball CSV missing at {file_path}")
        return pd.DataFrame()
    
    dtypes = {
        "match_id": str,
        "innings": np.int8,
        "overid": np.int8,
        "over_ball_num": np.int8,
        "innings_ball_num": np.int16,
        "batting_team_id": str,
        "bowling_team_id": str,
        "striker_id": str,
        "striker_name": str,
        "non_striker_id": str,
        "non_striker_name": str,
        "bowler_id": str,
        "bowler_name": str,
        "batting_type": "category",
        "bowling_type": "category",
        "batting_order": np.float32,
        "runs": np.int8,
        "dismissal_type_id": str,
        "dismissal_type": str,
        "dismissed_player_id": str,
        "extras_type": "category",
        "extras1_runs": np.int8,
        "extras_2_runs": np.int8,
        "pace_or_spin": "category",
        "delivery_style": "category",
        "over_or_around": "category",
        "on_or_off": "category",
    }
    
    df = pd.read_csv(file_path, nrows=nrows, dtype=dtypes, low_memory=False)
    df.columns = [c.strip() for c in df.columns]
    
    # Standardize boolean columns
    for bool_col in ["is_four", "is_six", "is_wicket"]:
        if bool_col in df.columns:
            df[bool_col] = _to_bool_series(df[bool_col])
            
    return df


@_cache_decorator
def load_all_cricket_data(data_dir_str: Optional[str] = None) -> Dict[str, pd.DataFrame]:
    """
    Unified cached loader returning all cricket datasets in a structured dictionary.
    Safe for multi-threaded Streamlit dashboard access.
    """
    data_dir = Path(data_dir_str) if data_dir_str else get_raw_data_directory()
    
    return {
        "ball_by_ball": load_ball_by_ball(data_dir),
        "matches": load_matches(data_dir),
        "playing_eleven": load_playing_eleven(data_dir),
        "player_mappings": load_player_mappings(data_dir),
        "competitions": load_competitions(data_dir),
        "teams": load_teams(data_dir),
    }

