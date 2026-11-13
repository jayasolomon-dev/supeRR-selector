"""
SUPERR SELECTOR — Pressure Engine Implementation Module
Module Reference: src/features/pressure_engine.py
Author: Senior Cricket Data Scientist, Python ML Engineer & Pipeline Architect
Project: SUPERR SELECTOR (Rajasthan Royals SupeRR Selector Season 2 Hackathon)

Implements the approved Revision 2.1 methodology for scoring pre-delivery match pressure:
- Asymmetric modeling: Decoupled Batting Pressure (P_bat) and Bowling Defensive Pressure (P_bowl)
- Contextual Par Model in Innings 1 (No RRR)
- Bounded Sigmoidal Model in Innings 2 (k=0.35, centered at format Par)
- Format-specific baselines: IPL = 9.35 RPO, T20I = 8.59 RPO
- Terminal state safety (target reached = 0.0, impossible chase = 100.0 / 0.0)
- Full explainability vectors (9 sub-components)
- Exact ex-ante temporal purity: strictly relies on match state prior to ball t
"""

from typing import Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd


# ------------------------------------------------------------------------------
# Core Cricket Constants & Approved Methodology Parameters (Revision 2.1)
# ------------------------------------------------------------------------------
PAR_RUN_RATE_IPL = 9.35       # Empirical median 1st innings run rate for IPL
PAR_RUN_RATE_T20I = 8.59      # Empirical median 1st innings run rate for Men's T20I
SIGMOID_K = 0.35              # Proposed steepness parameter for Innings 2 RRR sigmoid
STANDARD_T20_LEGAL_BALLS = 120 # 20 overs * 6 legal deliveries

# Innings 1 Component Weights
W_INN1_BAT_PACE = 0.45        # Weight for pace deficit (CRR vs Par)
W_INN1_BAT_RES = 0.35         # Weight for wicket resource depletion
W_INN1_BAT_PHASE = 0.20       # Weight for phase acceleration urgency

W_INN1_BOWL_CONT = 0.40       # Weight for containment stress (CRR conceded vs Par)
W_INN1_BOWL_DROUGHT = 0.35    # Weight for wicket drought (opponent batting depth)
W_INN1_BOWL_DEATH = 0.25      # Weight for death overs execution crunch

# Innings 2 Component Weights
W_INN2_BAT_RRR = 0.60         # Weight for bounded sigmoidal RRR (S_RRR)
W_INN2_BAT_WKT = 0.40         # Weight for chasing wicket depletion stress

W_INN2_BOWL_RUNWAY = 0.50     # Weight for defensive runway crunch (runs to defend / ball)
W_INN2_BOWL_BOUNDARY = 0.30   # Weight for boundary vulnerability threat
W_INN2_BOWL_DEPTH = 0.20      # Weight for chasing team remaining batting depth

# Categorical Threshold Boundaries
PRESSURE_CAT_BINS = [-np.inf, 40.0, 65.0, 85.0, np.inf]
PRESSURE_CAT_LABELS = ["Low", "Moderate", "High", "Extreme"]


# ------------------------------------------------------------------------------
# 1. Innings 1 Pressure Calculations (Target Setting)
# ------------------------------------------------------------------------------

def calculate_innings1_batting_pressure(
    score_before: Union[float, np.ndarray, pd.Series],
    wickets_before: Union[float, np.ndarray, pd.Series],
    legal_balls_before: Union[float, np.ndarray, pd.Series],
    total_legal_balls: Union[float, np.ndarray, pd.Series],
    par_comp: Union[float, np.ndarray, pd.Series],
) -> Tuple[Union[float, np.ndarray], Dict[str, Union[float, np.ndarray]]]:
    """
    Computes Innings 1 Batting Pressure and explainability sub-components.
    
    Formula:
      CRR_adj = (score_before + par_comp * 2.0) / (legal_balls_before / 6.0 + 2.0)
      I_pace = clip(50.0 + 7.5 * (par_comp - CRR_adj), 0.0, 100.0)
      W_exp = 6.0 * (legal_balls_before / total_legal_balls) ** 0.80
      I_res = clip(50.0 + 12.0 * (wickets_before - W_exp), 0.0, 100.0)
      I_phase = 35.0 + 50.0 * (legal_balls_before / total_legal_balls) ** 1.5
      P_bat = clip(0.45 * I_pace + 0.35 * I_res + 0.20 * I_phase, 0.0, 100.0)
    """
    safe_total = np.where(total_legal_balls > 0, total_legal_balls, STANDARD_T20_LEGAL_BALLS)
    balls_ratio = np.clip(legal_balls_before / safe_total, 0.0, 1.0)
    
    # Bayesian shrinkage for CRR
    crr_adj = (score_before + par_comp * 2.0) / (legal_balls_before / 6.0 + 2.0)
    
    # Pace deficit indicator
    i_pace = np.clip(50.0 + 7.5 * (par_comp - crr_adj), 0.0, 100.0)
    
    # Wicket resource depletion indicator
    w_exp = 6.0 * (balls_ratio ** 0.80)
    delta_wkt = wickets_before - w_exp
    i_res = np.clip(50.0 + 12.0 * delta_wkt, 0.0, 100.0)
    
    # Phase urgency indicator
    i_phase = 35.0 + 50.0 * (balls_ratio ** 1.5)
    
    # Composite score
    raw_p_bat = (
        W_INN1_BAT_PACE * i_pace +
        W_INN1_BAT_RES * i_res +
        W_INN1_BAT_PHASE * i_phase
    )
    p_bat = np.clip(raw_p_bat, 0.0, 100.0)
    
    components = {
        "crr_adj": crr_adj,
        "i_pace": i_pace,
        "w_exp": w_exp,
        "delta_wkt": delta_wkt,
        "i_res": i_res,
        "i_phase": i_phase,
    }
    return p_bat, components


def calculate_innings1_bowling_pressure(
    score_before: Union[float, np.ndarray, pd.Series],
    wickets_before: Union[float, np.ndarray, pd.Series],
    legal_balls_before: Union[float, np.ndarray, pd.Series],
    total_legal_balls: Union[float, np.ndarray, pd.Series],
    par_comp: Union[float, np.ndarray, pd.Series],
    phase: Union[str, np.ndarray, pd.Series],
) -> Tuple[Union[float, np.ndarray], Dict[str, Union[float, np.ndarray]]]:
    """
    Computes Innings 1 Bowling Team-Context Defensive Pressure and explainability sub-components.
    
    Formula:
      I_cont = clip(50.0 + 7.5 * (CRR_adj - par_comp), 0.0, 100.0)
      I_drought = clip(50.0 - 10.0 * delta_wkt, 0.0, 100.0)
      I_death = 30.0 (PP) | 45.0 (Middle) | 75.0 + 15.0 * ((balls - 90) / 30) (Death)
      P_bowl = clip(0.40 * I_cont + 0.35 * I_drought + 0.25 * I_death, 0.0, 100.0)
    """
    safe_total = np.where(total_legal_balls > 0, total_legal_balls, STANDARD_T20_LEGAL_BALLS)
    balls_ratio = np.clip(legal_balls_before / safe_total, 0.0, 1.0)
    
    # Bayesian shrinkage for CRR
    crr_adj = (score_before + par_comp * 2.0) / (legal_balls_before / 6.0 + 2.0)
    
    # Containment stress indicator
    i_cont = np.clip(50.0 + 7.5 * (crr_adj - par_comp), 0.0, 100.0)
    
    # Wicket drought indicator
    w_exp = 6.0 * (balls_ratio ** 0.80)
    delta_wkt = wickets_before - w_exp
    i_drought = np.clip(50.0 - 10.0 * delta_wkt, 0.0, 100.0)
    
    # Death defense execution crunch
    is_series = hasattr(phase, "__len__") and not isinstance(phase, str)
    if is_series:
        phase_arr = np.asarray(phase)
        legal_b = np.asarray(legal_balls_before)
        death_progression = 75.0 + 15.0 * np.clip((legal_b - 90.0) / 30.0, 0.0, 1.0)
        i_death = np.where(
            phase_arr == "Powerplay", 30.0,
            np.where(phase_arr == "Middle", 45.0, death_progression)
        )
    else:
        if phase == "Powerplay":
            i_death = 30.0
        elif phase == "Middle":
            i_death = 45.0
        else:
            death_progression = 75.0 + 15.0 * np.clip((float(legal_balls_before) - 90.0) / 30.0, 0.0, 1.0)
            i_death = float(death_progression)
            
    raw_p_bowl = (
        W_INN1_BOWL_CONT * i_cont +
        W_INN1_BOWL_DROUGHT * i_drought +
        W_INN1_BOWL_DEATH * i_death
    )
    p_bowl = np.clip(raw_p_bowl, 0.0, 100.0)
    
    components = {
        "crr_adj": crr_adj,
        "i_cont": i_cont,
        "i_drought": i_drought,
        "i_death": i_death,
    }
    return p_bowl, components


# ------------------------------------------------------------------------------
# 2. Innings 2 Pressure Calculations (The Run Chase)
# ------------------------------------------------------------------------------

def calculate_innings2_batting_pressure(
    required_run_rate_before: Union[float, np.ndarray, pd.Series],
    wickets_before: Union[float, np.ndarray, pd.Series],
    legal_balls_before: Union[float, np.ndarray, pd.Series],
    legal_balls_remaining_before: Union[float, np.ndarray, pd.Series],
    total_legal_balls: Union[float, np.ndarray, pd.Series],
    required_runs_before: Union[float, np.ndarray, pd.Series],
    par_comp: Union[float, np.ndarray, pd.Series],
) -> Tuple[Union[float, np.ndarray], Dict[str, Union[float, np.ndarray]]]:
    """
    Computes Innings 2 Batting Pressure and explainability sub-components.
    
    Formula:
      S_RRR = 100.0 / (1.0 + exp(-0.35 * (RRR - par_comp)))
      I_wkt = 100.0 * (wickets_before / 10.0) ** 1.35
      M_crunch = 1.0 + 0.30 * f_bowled * ((S_RRR - 50) / 50)  [if S_RRR >= 50]
                 1.0 - 0.25 * f_bowled * ((50 - S_RRR) / 50)  [if S_RRR < 50]
      P_bat = clip((0.60 * S_RRR + 0.40 * I_wkt) * M_crunch, 0.0, 100.0)
      
    Terminal Policy:
      If required_runs_before <= 0 -> 0.0 (Target met/won)
      If legal_balls_remaining_before == 0 and required_runs_before > 0 -> 100.0 (Impossible chase)
    """
    safe_total = np.where(total_legal_balls > 0, total_legal_balls, STANDARD_T20_LEGAL_BALLS)
    f_bowled = np.clip(legal_balls_before / safe_total, 0.0, 1.0)
    
    # Safe RRR for sigmoid computation (handle NaN/infinite gracefully)
    safe_rrr = np.nan_to_num(required_run_rate_before, nan=float(np.mean(par_comp)))
    
    # Bounded sigmoidal RRR feature
    s_rrr = 100.0 / (1.0 + np.exp(-SIGMOID_K * (safe_rrr - par_comp)))
    
    # Wicket depletion stress
    safe_wkts = np.clip(wickets_before, 0.0, 10.0)
    i_wkt = 100.0 * ((safe_wkts / 10.0) ** 1.35)
    
    # Ball crunch interaction multiplier
    is_series = hasattr(s_rrr, "__len__")
    if is_series:
        m_crunch = np.where(
            s_rrr >= 50.0,
            1.0 + 0.30 * f_bowled * ((s_rrr - 50.0) / 50.0),
            1.0 - 0.25 * f_bowled * ((50.0 - s_rrr) / 50.0)
        )
    else:
        if s_rrr >= 50.0:
            m_crunch = 1.0 + 0.30 * f_bowled * ((s_rrr - 50.0) / 50.0)
        else:
            m_crunch = 1.0 - 0.25 * f_bowled * ((50.0 - s_rrr) / 50.0)
            
    raw_p_bat = (W_INN2_BAT_RRR * s_rrr + W_INN2_BAT_WKT * i_wkt) * m_crunch
    p_bat = np.clip(raw_p_bat, 0.0, 100.0)
    
    # Terminal & Boundary conditions enforcement
    if is_series:
        target_met = (required_runs_before <= 0)
        impossible_chase = (legal_balls_remaining_before == 0) & (required_runs_before > 0)
        p_bat = np.where(target_met, 0.0, p_bat)
        p_bat = np.where(impossible_chase, 100.0, p_bat)
    else:
        if required_runs_before <= 0:
            p_bat = 0.0
        elif legal_balls_remaining_before == 0 and required_runs_before > 0:
            p_bat = 100.0
            
    components = {
        "s_rrr": s_rrr,
        "i_wkt": i_wkt,
        "m_crunch": m_crunch,
        "f_bowled": f_bowled,
    }
    return p_bat, components


def calculate_innings2_bowling_pressure(
    required_runs_before: Union[float, np.ndarray, pd.Series],
    legal_balls_remaining_before: Union[float, np.ndarray, pd.Series],
    wickets_before: Union[float, np.ndarray, pd.Series],
) -> Tuple[Union[float, np.ndarray], Dict[str, Union[float, np.ndarray]]]:
    """
    Computes Innings 2 Bowling Team-Context Defensive Pressure and explainability sub-components.
    
    Formula:
      RPB = required_runs_before / max(legal_balls_remaining_before, 1)
      I_runway = 100.0 [RPB <= 0.5]
                 100.0 - 35.0 * (RPB - 0.5) [0.5 < RPB <= 2.0]
                 max(15.0, 47.5 - 12.0 * (RPB - 2.0)) [RPB > 2.0]
      Boundaries = (required_runs_before - 1.0) / 4.0
      I_boundary = clip(100.0 - 15.0 * Boundaries, 0.0, 100.0)
      I_depth = 100.0 * (1.0 - (wickets_before / 10.0) ** 1.35)
      P_bowl = clip(0.50 * I_runway + 0.30 * I_boundary + 0.20 * I_depth, 0.0, 100.0)
      
    Terminal Policy:
      If required_runs_before <= 0 -> 0.0 (Target met, match lost)
      If legal_balls_remaining_before == 0 and required_runs_before > 0 -> 0.0 (Match won)
    """
    safe_balls_rem = np.maximum(legal_balls_remaining_before, 1.0)
    rpb = required_runs_before / safe_balls_rem
    
    is_series = hasattr(rpb, "__len__")
    if is_series:
        i_runway = np.where(
            rpb <= 0.5,
            100.0,
            np.where(
                rpb <= 2.0,
                100.0 - 35.0 * (rpb - 0.5),
                np.maximum(15.0, 47.5 - 12.0 * (rpb - 2.0))
            )
        )
    else:
        if rpb <= 0.5:
            i_runway = 100.0
        elif rpb <= 2.0:
            i_runway = 100.0 - 35.0 * (rpb - 0.5)
        else:
            i_runway = max(15.0, 47.5 - 12.0 * (rpb - 2.0))
            
    boundaries_allowed = (required_runs_before - 1.0) / 4.0
    i_boundary = np.clip(100.0 - 15.0 * boundaries_allowed, 0.0, 100.0)
    
    safe_wkts = np.clip(wickets_before, 0.0, 10.0)
    i_depth = 100.0 * (1.0 - ((safe_wkts / 10.0) ** 1.35))
    
    raw_p_bowl = (
        W_INN2_BOWL_RUNWAY * i_runway +
        W_INN2_BOWL_BOUNDARY * i_boundary +
        W_INN2_BOWL_DEPTH * i_depth
    )
    p_bowl = np.clip(raw_p_bowl, 0.0, 100.0)
    
    # Terminal & Boundary conditions enforcement
    if is_series:
        target_met = (required_runs_before <= 0)
        impossible_chase = (legal_balls_remaining_before == 0) & (required_runs_before > 0)
        p_bowl = np.where(target_met, 0.0, p_bowl)
        p_bowl = np.where(impossible_chase, 0.0, p_bowl)
    else:
        if required_runs_before <= 0:
            p_bowl = 0.0
        elif legal_balls_remaining_before == 0 and required_runs_before > 0:
            p_bowl = 0.0
            
    components = {
        "rpb": rpb,
        "i_runway": i_runway,
        "boundaries_allowed": boundaries_allowed,
        "i_boundary": i_boundary,
        "i_depth": i_depth,
    }
    return p_bowl, components


# ------------------------------------------------------------------------------
# 3. Overall Resource Depletion & Pressure Categorization
# ------------------------------------------------------------------------------

def calculate_resource_depletion_percentage(
    wickets_before: Union[float, np.ndarray, pd.Series],
    legal_balls_remaining_before: Union[float, np.ndarray, pd.Series],
    total_legal_balls: Union[float, np.ndarray, pd.Series],
) -> Union[float, np.ndarray]:
    """
    Computes overall resource depletion percentage [0.0, 100.0] combining wickets and remaining balls.
    Formula: 100.0 * (1.0 - (1.0 - w/10) * (rem / total) ** 0.65)
    """
    safe_total = np.where(total_legal_balls > 0, total_legal_balls, STANDARD_T20_LEGAL_BALLS)
    safe_rem = np.clip(legal_balls_remaining_before / safe_total, 0.0, 1.0)
    safe_w = np.clip(wickets_before, 0.0, 10.0)
    
    w_factor = 1.0 - (safe_w / 10.0)
    b_factor = safe_rem ** 0.65
    res_pct = 100.0 * (1.0 - w_factor * b_factor)
    return np.clip(res_pct, 0.0, 100.0)


def assign_pressure_categories(
    scores: Union[float, np.ndarray, pd.Series, list, tuple]
) -> Union[str, np.ndarray, pd.Series]:
    """
    Maps continuous pressure score [0.0, 100.0] to approved 4-tier categories:
    - Low:      [0.0, 40.0)
    - Moderate: [40.0, 65.0)
    - High:     [65.0, 85.0)
    - Extreme:  [85.0, 100.0]
    """
    if isinstance(scores, (pd.Series, np.ndarray, list, tuple)):
        arr = np.asarray(scores)
        conditions = [
            arr < 40.0,
            (arr >= 40.0) & (arr < 65.0),
            (arr >= 65.0) & (arr < 85.0),
            arr >= 85.0
        ]
        return np.select(conditions, PRESSURE_CAT_LABELS, default="Low")
    else:
        val = float(scores)
        if val < 40.0:
            return "Low"
        elif val < 65.0:
            return "Moderate"
        elif val < 85.0:
            return "High"
        else:
            return "Extreme"


# ------------------------------------------------------------------------------
# 4. Master Pipeline Delivery Enrichment Function
# ------------------------------------------------------------------------------

def enrich_deliveries_with_pressure(deliveries_df: pd.DataFrame) -> pd.DataFrame:
    """
    Takes a verified delivery-level DataFrame (IPL or T20I) and enriches it with all
    approved Revision 2.1 Pressure Engine features:
    - 26 Verified Source Features (retained from input)
    - 22 Derived Features (baselines, sub-components, master pressure scores, categories, audit flags)
    
    Total Output Columns: 65 original + 22 derived = 87 columns (superset containing all 48 required schema features).
    """
    df = deliveries_df.copy()
    n = len(df)
    
    # 1. Format-specific Baseline Par Scoring Rate
    comp_cat = df["competition_category"].astype(str).str.strip().str.upper()
    par_comp = np.where(comp_cat == "IPL", PAR_RUN_RATE_IPL, PAR_RUN_RATE_T20I)
    df["par_run_rate_comp"] = par_comp
    
    # 2. Bayesian CRR Shrinkage (evaluated for all deliveries)
    safe_balls_bowled = np.maximum(df["legal_balls_before"], 0)
    df["crr_shrinkage_before"] = np.round(
        (df["score_before"] + par_comp * 2.0) / (safe_balls_bowled / 6.0 + 2.0), 4
    )
    
    # 3. Overall Resource Percentage Depleted
    df["resource_percentage_depleted"] = np.round(
        calculate_resource_depletion_percentage(
            wickets_before=df["wickets_before"],
            legal_balls_remaining_before=df["legal_balls_remaining_before"],
            total_legal_balls=df["total_legal_balls"],
        ), 2
    )
    
    # Masks for Innings 1 vs Innings 2
    mask_inn1 = df["innings"] == 1
    mask_inn2 = df["innings"] == 2
    
    # Initialize Derived Feature Columns with NaNs or False
    df["rrr_bounded"] = np.nan
    df["runs_to_defend_per_ball"] = np.nan
    
    # 9 Component Columns
    df["bat_comp_pace_urgency"] = np.nan
    df["bat_comp_resource_stress"] = np.nan
    df["bat_comp_phase_urgency"] = np.nan
    df["bat_comp_crunch_mult"] = np.nan
    df["bowl_comp_containment"] = np.nan
    df["bowl_comp_death_defense"] = np.nan
    df["bowl_comp_runway"] = np.nan
    df["bowl_comp_boundary_threat"] = np.nan
    df["bowl_comp_depth_stress"] = np.nan
    
    # Master Pressure Scores
    df["batting_pressure_score"] = np.nan
    df["bowling_pressure_score"] = np.nan
    
    # --------------------------------------------------------------------------
    # Process Innings 1 (Target Setting)
    # --------------------------------------------------------------------------
    if mask_inn1.any():
        df_inn1 = df[mask_inn1]
        
        # Batting Innings 1
        p_bat1, c_bat1 = calculate_innings1_batting_pressure(
            score_before=df_inn1["score_before"].values,
            wickets_before=df_inn1["wickets_before"].values,
            legal_balls_before=df_inn1["legal_balls_before"].values,
            total_legal_balls=df_inn1["total_legal_balls"].values,
            par_comp=df_inn1["par_run_rate_comp"].values,
        )
        df.loc[mask_inn1, "bat_comp_pace_urgency"] = np.round(c_bat1["i_pace"], 4)
        df.loc[mask_inn1, "bat_comp_resource_stress"] = np.round(c_bat1["i_res"], 4)
        df.loc[mask_inn1, "bat_comp_phase_urgency"] = np.round(c_bat1["i_phase"], 4)
        df.loc[mask_inn1, "batting_pressure_score"] = np.round(p_bat1, 2)
        
        # Bowling Innings 1
        p_bowl1, c_bowl1 = calculate_innings1_bowling_pressure(
            score_before=df_inn1["score_before"].values,
            wickets_before=df_inn1["wickets_before"].values,
            legal_balls_before=df_inn1["legal_balls_before"].values,
            total_legal_balls=df_inn1["total_legal_balls"].values,
            par_comp=df_inn1["par_run_rate_comp"].values,
            phase=df_inn1["phase"].values,
        )
        df.loc[mask_inn1, "bowl_comp_containment"] = np.round(c_bowl1["i_cont"], 4)
        df.loc[mask_inn1, "bowl_comp_depth_stress"] = np.round(c_bowl1["i_drought"], 4)
        df.loc[mask_inn1, "bowl_comp_death_defense"] = np.round(c_bowl1["i_death"], 4)
        df.loc[mask_inn1, "bowling_pressure_score"] = np.round(p_bowl1, 2)

    # --------------------------------------------------------------------------
    # Process Innings 2 (The Run Chase)
    # --------------------------------------------------------------------------
    if mask_inn2.any():
        df_inn2 = df[mask_inn2]
        
        # Batting Innings 2
        p_bat2, c_bat2 = calculate_innings2_batting_pressure(
            required_run_rate_before=df_inn2["required_run_rate_before"].values,
            wickets_before=df_inn2["wickets_before"].values,
            legal_balls_before=df_inn2["legal_balls_before"].values,
            legal_balls_remaining_before=df_inn2["legal_balls_remaining_before"].values,
            total_legal_balls=df_inn2["total_legal_balls"].values,
            required_runs_before=df_inn2["required_runs_before"].values,
            par_comp=df_inn2["par_run_rate_comp"].values,
        )
        df.loc[mask_inn2, "rrr_bounded"] = np.round(c_bat2["s_rrr"], 4)
        df.loc[mask_inn2, "bat_comp_pace_urgency"] = np.round(c_bat2["s_rrr"], 4)
        df.loc[mask_inn2, "bat_comp_resource_stress"] = np.round(c_bat2["i_wkt"], 4)
        df.loc[mask_inn2, "bat_comp_crunch_mult"] = np.round(c_bat2["m_crunch"], 4)
        df.loc[mask_inn2, "batting_pressure_score"] = np.round(p_bat2, 2)
        
        # Bowling Innings 2
        p_bowl2, c_bowl2 = calculate_innings2_bowling_pressure(
            required_runs_before=df_inn2["required_runs_before"].values,
            legal_balls_remaining_before=df_inn2["legal_balls_remaining_before"].values,
            wickets_before=df_inn2["wickets_before"].values,
        )
        df.loc[mask_inn2, "runs_to_defend_per_ball"] = np.round(c_bowl2["rpb"], 4)
        df.loc[mask_inn2, "bowl_comp_runway"] = np.round(c_bowl2["i_runway"], 4)
        df.loc[mask_inn2, "bowl_comp_boundary_threat"] = np.round(c_bowl2["i_boundary"], 4)
        df.loc[mask_inn2, "bowl_comp_depth_stress"] = np.round(c_bowl2["i_depth"], 4)
        df.loc[mask_inn2, "bowling_pressure_score"] = np.round(p_bowl2, 2)

    # --------------------------------------------------------------------------
    # Process Super Overs (Innings 3 & 4)
    # --------------------------------------------------------------------------
    mask_super = df["innings"] > 2
    if mask_super.any():
        # Super Overs represent peak crisis / tie-breaker climax (Extreme tier)
        df.loc[mask_super, "rrr_bounded"] = 100.0
        df.loc[mask_super, "bat_comp_pace_urgency"] = 100.0
        df.loc[mask_super, "bat_comp_resource_stress"] = 100.0
        df.loc[mask_super, "bat_comp_phase_urgency"] = 100.0
        df.loc[mask_super, "bat_comp_crunch_mult"] = 1.30
        df.loc[mask_super, "bowl_comp_containment"] = 100.0
        df.loc[mask_super, "bowl_comp_death_defense"] = 100.0
        df.loc[mask_super, "bowl_comp_depth_stress"] = 100.0
        df.loc[mask_super, "bowl_comp_runway"] = 100.0
        df.loc[mask_super, "bowl_comp_boundary_threat"] = 100.0
        df.loc[mask_super, "batting_pressure_score"] = 100.00
        df.loc[mask_super, "bowling_pressure_score"] = 100.00

    # 4. Assign Categorical Tiers
    df["batting_pressure_cat"] = assign_pressure_categories(df["batting_pressure_score"])
    df["bowling_pressure_cat"] = assign_pressure_categories(df["bowling_pressure_score"])

    # 5. Quality, Audit & Edge-Case Flags
    df["is_dls_shortened"] = df["total_legal_balls"] < STANDARD_T20_LEGAL_BALLS
    df["is_early_delivery"] = df["legal_balls_before"] < 12
    df["is_extreme_rrr_bounded"] = mask_inn2 & (df["required_run_rate_before"] >= 24.0)
    df["is_target_met_delivery"] = mask_inn2 & (df["required_runs_before"] <= 0)
    # Note: impossible_chase_state is already present in processed input

    return df


# ------------------------------------------------------------------------------
# 5. Synthetic Unit Fixtures Runner (SYN-01 to SYN-10)
# ------------------------------------------------------------------------------

def run_synthetic_fixtures() -> Tuple[bool, List[Dict[str, Union[str, float, bool]]]]:
    """
    Executes the 10 approved canonical synthetic fixtures (SYN-01 through SYN-10)
    directly through the production functions and asserts exact expected scores.
    """
    fixtures = [
        {
            "id": "SYN-01", "comp": "IPL", "inn": 1, "total_b": 120, "rem_b": 120,
            "wkts": 0, "score": 0, "target": np.nan, "req": np.nan, "rrr": np.nan,
            "phase": "Powerplay", "exp_bat": 47.00, "exp_bowl": 45.00
        },
        {
            "id": "SYN-02", "comp": "IPL", "inn": 1, "total_b": 120, "rem_b": 105,
            "wkts": 3, "score": 15, "target": np.nan, "req": np.nan, "rrr": np.nan,
            "phase": "Powerplay", "exp_bat": 61.55, "exp_bowl": 32.90
        },
        {
            "id": "SYN-03", "comp": "IPL", "inn": 1, "total_b": 120, "rem_b": 18,
            "wkts": 3, "score": 170, "target": np.nan, "req": np.nan, "rrr": np.nan,
            "phase": "Death", "exp_bat": 43.35, "exp_bowl": 67.43
        },
        {
            "id": "SYN-04", "comp": "T20I", "inn": 2, "total_b": 120, "rem_b": 60,
            "wkts": 1, "score": 100, "target": 160.0, "req": 60.0, "rrr": 6.00,
            "phase": "Middle", "exp_bat": 18.04, "exp_bowl": 60.36
        },
        {
            "id": "SYN-05", "comp": "T20I", "inn": 2, "total_b": 120, "rem_b": 6,
            "wkts": 6, "score": 152, "target": 160.0, "req": 8.0, "rrr": 8.00,
            "phase": "Death", "exp_bat": 45.84, "exp_bowl": 67.51
        },
        {
            "id": "SYN-06", "comp": "IPL", "inn": 2, "total_b": 120, "rem_b": 6,
            "wkts": 7, "score": 176, "target": 200.0, "req": 24.0, "rrr": 24.00,
            "phase": "Death", "exp_bat": 100.00, "exp_bowl": 23.52
        },
        {
            "id": "SYN-07", "comp": "IPL", "inn": 2, "total_b": 120, "rem_b": 1,
            "wkts": 8, "score": 178, "target": 200.0, "req": 22.0, "rrr": 132.00,
            "phase": "Death", "exp_bat": 100.00, "exp_bowl": 19.08
        },
        {
            "id": "SYN-08", "comp": "T20I", "inn": 2, "total_b": 120, "rem_b": 0,
            "wkts": 7, "score": 155, "target": 160.0, "req": 5.0, "rrr": np.nan,
            "phase": "Death", "exp_bat": 100.00, "exp_bowl": 0.00
        },
        {
            "id": "SYN-09", "comp": "IPL", "inn": 2, "total_b": 120, "rem_b": 12,
            "wkts": 4, "score": 200, "target": 200.0, "req": 0.0, "rrr": 0.00,
            "phase": "Death", "exp_bat": 0.00, "exp_bowl": 0.00
        },
        {
            "id": "SYN-10", "comp": "T20I", "inn": 2, "total_b": 30, "rem_b": 18,
            "wkts": 5, "score": 20, "target": 55.0, "req": 35.0, "rrr": 11.67,
            "phase": "Middle", "exp_bat": 64.03, "exp_bowl": 36.88
        },
    ]

    all_passed = True
    results = []

    for fix in fixtures:
        par = PAR_RUN_RATE_IPL if fix["comp"] == "IPL" else PAR_RUN_RATE_T20I
        legal_bowled = fix["total_b"] - fix["rem_b"]

        if fix["inn"] == 1:
            p_bat, _ = calculate_innings1_batting_pressure(
                score_before=fix["score"],
                wickets_before=fix["wkts"],
                legal_balls_before=legal_bowled,
                total_legal_balls=fix["total_b"],
                par_comp=par,
            )
            p_bowl, _ = calculate_innings1_bowling_pressure(
                score_before=fix["score"],
                wickets_before=fix["wkts"],
                legal_balls_before=legal_bowled,
                total_legal_balls=fix["total_b"],
                par_comp=par,
                phase=fix["phase"],
            )
        else:
            p_bat, _ = calculate_innings2_batting_pressure(
                required_run_rate_before=fix["rrr"],
                wickets_before=fix["wkts"],
                legal_balls_before=legal_bowled,
                legal_balls_remaining_before=fix["rem_b"],
                total_legal_balls=fix["total_b"],
                required_runs_before=fix["req"],
                par_comp=par,
            )
            p_bowl, _ = calculate_innings2_bowling_pressure(
                required_runs_before=fix["req"],
                legal_balls_remaining_before=fix["rem_b"],
                wickets_before=fix["wkts"],
            )

        p_bat = round(float(p_bat), 2)
        p_bowl = round(float(p_bowl), 2)

        bat_ok = (abs(p_bat - fix["exp_bat"]) <= 0.01)
        bowl_ok = (abs(p_bowl - fix["exp_bowl"]) <= 0.01)
        fix_ok = bat_ok and bowl_ok

        if not fix_ok:
            all_passed = False

        results.append({
            "fixture_id": fix["id"],
            "format": fix["comp"],
            "innings": fix["inn"],
            "act_bat": p_bat,
            "exp_bat": fix["exp_bat"],
            "bat_ok": bat_ok,
            "act_bowl": p_bowl,
            "exp_bowl": fix["exp_bowl"],
            "bowl_ok": bowl_ok,
            "passed": fix_ok,
        })

    return all_passed, results
