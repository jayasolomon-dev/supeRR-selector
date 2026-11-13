"""
SUPERR SELECTOR - Configuration & Path Management
Centralized system configuration for Windows 11 and cross-platform compatibility.
"""

from pathlib import Path
import os
import sys

# ------------------------------------------------------------------------------
# Base Directory Resolution
# ------------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ------------------------------------------------------------------------------
# Directory Hierarchy
# ------------------------------------------------------------------------------
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
DATA_PACK_DIR = BASE_DIR / "Data" / "Data Pack"
EXTERNAL_DATA_DIR = DATA_DIR / "external"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Player images can reside in assets/player_images or data/player_images
ASSETS_DIR = BASE_DIR / "assets"
PLAYER_IMAGES_DIR = ASSETS_DIR / "player_images"
DATA_PLAYER_IMAGES_DIR = DATA_DIR / "player_images"

# Outputs & Reports
OUTPUTS_DIR = BASE_DIR / "outputs"
MODELS_OUTPUT_DIR = OUTPUTS_DIR / "models"
TABLES_OUTPUT_DIR = OUTPUTS_DIR / "tables"

REPORTS_DIR = BASE_DIR / "reports"
FIGURES_REPORT_DIR = REPORTS_DIR / "figures"

# ------------------------------------------------------------------------------
# Raw Data File Resolution
# Automatically discovers raw CSV files whether they are in data/raw or Data/Data Pack
# ------------------------------------------------------------------------------
def get_raw_data_directory() -> Path:
    """
    Returns the active raw data directory containing the cricket CSV files.
    Prefers data/raw if populated, otherwise seamlessly falls back to Data/Data Pack.
    """
    if RAW_DATA_DIR.exists() and any(RAW_DATA_DIR.glob("*.csv")):
        return RAW_DATA_DIR
    if DATA_PACK_DIR.exists() and any(DATA_PACK_DIR.glob("*.csv")):
        return DATA_PACK_DIR
    return RAW_DATA_DIR

# CSV File Names
BALL_BY_BALL_FILE = "ball_by_ball.csv"
MATCHES_FILE = "matches.csv"
PLAYING_ELEVEN_FILE = "playing_eleven.csv"
MAPPING_FILE = "competition_team_player_mapping.csv"
COMPETITIONS_FILE = "competitions.csv"
TEAMS_FILE = "teams.csv"

# ------------------------------------------------------------------------------
# Cricket Domain Rules & Constants
# ------------------------------------------------------------------------------
# T20 Match Phases by Over ID (1-indexed)
PHASE_POWERPLAY = "Powerplay"      # Overs 1 to 6
PHASE_MIDDLE = "Middle"            # Overs 7 to 15
PHASE_DEATH = "Death"              # Overs 16 to 20

def get_match_phase(over_id: int) -> str:
    """Categorizes over number (1-20) into T20 match phase."""
    if over_id <= 6:
        return PHASE_POWERPLAY
    elif over_id <= 15:
        return PHASE_MIDDLE
    return PHASE_DEATH

# Bowler Credited Dismissals (Excludes Run Out, Retired Out, Obstructing field)
BOWLER_CREDITED_DISMISSALS = {
    "Caught",
    "Bowled",
    "LBW",
    "Stump",
    "Hit Wicket",
}

# ------------------------------------------------------------------------------
# Visual Styling & Palette (Navy Blue & Gold Cricket Palette)
# ------------------------------------------------------------------------------
COLORS = {
    "primary": "#0E1117",
    "accent_gold": "#FFB703",
    "accent_blue": "#219EBC",
    "dark_blue": "#023047",
    "accent_red": "#FB8500",
    "text_dark": "#2B2D42",
    "bg_card": "#FFFFFF",
    "success": "#2A9D8F",
    "danger": "#E76F51",
}

PLOTLY_TEMPLATE = "plotly_white"

