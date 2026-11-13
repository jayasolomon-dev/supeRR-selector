"""
SUPERR SELECTOR - Cricket Analytics Preprocessor
Enriches raw delivery data with cricket metrics, legal delivery tags, and match phases.
"""

from typing import Optional
import pandas as pd
import numpy as np

try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

from src.config import BOWLER_CREDITED_DISMISSALS, PHASE_POWERPLAY, PHASE_MIDDLE, PHASE_DEATH

def _cache_decorator(func):
    if HAS_STREAMLIT:
        return st.cache_data(show_spinner="Preprocessing match phases & ball-by-ball metrics...")(func)
    return func


@_cache_decorator
def preprocess_ball_by_ball(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enriches raw ball-by-ball events with domain cricket classifications:
    - Match phase (Powerplay 1-6, Middle 7-15, Death 16-20)
    - Legal delivery classification
    - Batter balls faced (excluding wides)
    - Bowler runs conceded (excluding legbyes and byes)
    - Bowler-credited wickets (excluding run outs and retirements)
    """
    if df.empty:
        return df
    
    df = df.copy()
    
    # 1. Match Phase Categorization
    conditions = [
        df["overid"] <= 6,
        (df["overid"] >= 7) & (df["overid"] <= 15),
        df["overid"] >= 16,
    ]
    choices = [PHASE_POWERPLAY, PHASE_MIDDLE, PHASE_DEATH]
    df["phase"] = np.select(conditions, choices, default=PHASE_MIDDLE)
    df["phase"] = df["phase"].astype("category")
    
    # 2. Normalize extras_type string
    extras_clean = df["extras_type"].astype(str).str.strip().str.lower()
    
    # 3. Batter Balls Faced (All balls except wides)
    df["is_batter_ball"] = extras_clean != "wide"
    
    # 4. Legal Deliveries for Bowler Overs (All balls except wides & overstep/no-balls)
    df["is_legal_ball"] = ~extras_clean.isin(["wide", "overstep"])
    
    # 5. Bowler Runs Conceded
    # Batter runs + extras that count against bowler (wide, overstep)
    # Leg byes, byes, and penalty runs do NOT count against the bowler
    runs = pd.to_numeric(df["runs"], errors="coerce").fillna(0).astype(int)
    extras_runs = pd.to_numeric(df["extras1_runs"], errors="coerce").fillna(0).astype(int)
    bowler_extra_mask = extras_clean.isin(["wide", "overstep"])
    
    df["bowler_runs"] = runs + np.where(bowler_extra_mask, extras_runs, 0)
    
    # 6. Bowler Credited Wickets (Exclude Run Out, Retired Out, Obstructing Field)
    dismissal_clean = df["dismissal_type"].astype(str).str.strip()
    is_wicket_flag = df["is_wicket"].astype(bool)
    df["is_bowler_wicket"] = is_wicket_flag & dismissal_clean.isin(BOWLER_CREDITED_DISMISSALS)
    
    # 7. Dot Balls (0 runs scored off the bat, no extras)
    df["is_dot_ball"] = (runs == 0) & (extras_clean == "none")
    
    return df

