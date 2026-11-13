"""
SUPERR SELECTOR - T20 Match-State & Pressure Detection Engine
Reconstructs cumulative match context before every delivery without future-data leakage.
Handles wides, no-balls, byes, leg-byes, wickets, innings breaks, and DLS shortened matches.
"""

from typing import Dict, Optional, Tuple, Union
import numpy as np
import pandas as pd


# ------------------------------------------------------------------------------
# Core Cricket Constants
# ------------------------------------------------------------------------------
STANDARD_T20_LEGAL_BALLS = 120       # 20 overs * 6 balls
STANDARD_T20_PAR_RUN_RATE = 8.5      # Median empirical T20 scoring rate
MAX_PRESSURE_SCORE = 100.0
MIN_PRESSURE_SCORE = 0.0


def _clean_id(val) -> str:
    """Safely converts an ID to a clean string without float '.0' suffix."""
    s = str(val).strip()
    if s.endswith(".0"):
        s = s[:-2]
    return s


def calculate_ball_runs(df: pd.DataFrame) -> pd.Series:
    """
    Computes total runs produced on a delivery: bat runs + penalty extra + overthrow extra.
    Formula: runs + extras1_runs + extras_2_runs
    """
    runs = pd.to_numeric(df.get("runs", 0), errors="coerce").fillna(0).astype(int)
    ext1 = pd.to_numeric(df.get("extras1_runs", 0), errors="coerce").fillna(0).astype(int)
    ext2 = pd.to_numeric(df.get("extras_2_runs", 0), errors="coerce").fillna(0).astype(int)
    return runs + ext1 + ext2


def identify_legal_deliveries(extras_series: pd.Series) -> pd.Series:
    """
    Identifies legal deliveries in cricket:
    - Wides & No-balls (Overstep & other): ILLEGAL deliveries (legal ball count does NOT increment).
    - Byes, Leg-byes, Penalty, and regular deliveries: LEGAL deliveries.
    """
    clean_extras = extras_series.astype(str).str.strip().str.lower()
    return ~clean_extras.isin(["wide", "overstep", "other"])


def compute_required_run_rate_and_chase_state(
    innings: Union[int, np.ndarray, pd.Series],
    legal_balls_remaining_before: Union[int, float, np.ndarray, pd.Series],
    required_runs_before: Union[int, float, np.ndarray, pd.Series],
) -> Tuple[Union[float, np.ndarray], Union[bool, np.ndarray]]:
    """
    Production calculation of Required Run Rate (RRR) and impossible chase state before a delivery.

    Rules:
    - Innings 1: RRR is strictly NaN, impossible_chase_state is False.
    - Innings 2:
      * When legal_balls_remaining_before > 0:
        RRR = round((required_runs_before / legal_balls_remaining_before) * 6.0, 2)
      * When legal_balls_remaining_before <= 0 or NaN:
        RRR is strictly NaN (undefined / infinite rate; not silently assigned 36.0).
      * impossible_chase_state = True strictly when:
        innings == 2 AND legal_balls_remaining_before == 0 AND required_runs_before > 0
    """
    is_scalar = (
        np.isscalar(innings)
        and np.isscalar(legal_balls_remaining_before)
        and np.isscalar(required_runs_before)
    )

    inn_arr = np.asarray(innings)
    balls_arr = np.asarray(legal_balls_remaining_before, dtype=float)
    req_arr = np.asarray(required_runs_before, dtype=float)

    is_inn2 = (inn_arr == 2)
    valid_balls = (balls_arr > 0) & (~np.isnan(balls_arr))
    safe_balls_rem = np.where(valid_balls, balls_arr, 1.0)
    rrr_calc = np.round((req_arr / safe_balls_rem) * 6.0, 2)

    rrr = np.where(is_inn2 & valid_balls, rrr_calc, np.nan)
    imp = is_inn2 & (balls_arr == 0) & (req_arr > 0)

    if is_scalar:
        return (float(rrr) if not np.isnan(rrr) else np.nan), bool(imp)
    return rrr, imp


def compute_innings_pressure_vectorized(
    innings_num: int,
    crr: np.ndarray,
    rrr: np.ndarray,
    wickets_before: np.ndarray,
    legal_balls_bowled: np.ndarray,
    legal_balls_remaining: np.ndarray,
    total_legal_balls: np.ndarray,
    required_runs: np.ndarray,
) -> np.ndarray:
    """
    Vectorized calculation of reproducible, bounded pressure score [0.0, 100.0].
    Strictly depends on match state prior to the current delivery.
    """
    n = len(wickets_before)
    pressure = np.zeros(n, dtype=np.float64)

    # Safe fractions
    total_b = np.where(total_legal_balls > 0, total_legal_balls, STANDARD_T20_LEGAL_BALLS)
    f_bowled = np.clip(legal_balls_bowled / total_b, 0.0, 1.0)

    if innings_num == 1:
        # ----------------------------------------------------------------------
        # Innings 1: Target Setting (CRR vs Par 8.5 & Resource Depletion)
        # ----------------------------------------------------------------------
        # Pace deficit
        deficit = STANDARD_T20_PAR_RUN_RATE - crr
        # For early balls (< 12 balls), damp the pace variance
        early_mask = legal_balls_bowled < 12
        p_pace = np.where(early_mask, 45.0, np.clip(50.0 + deficit * 4.5, 15.0, 85.0))

        # Expected wickets at current fraction of innings (par ~6.5 wickets by 20th over)
        expected_wkts = 6.5 * (f_bowled ** 0.85)
        wkt_diff = wickets_before - expected_wkts
        w_adj = wkt_diff * 6.5

        # Death overs urgency bump (+5 in final 5 overs)
        death_bump = np.where(f_bowled >= 0.75, 5.0, 0.0)

        pressure = np.clip(p_pace + w_adj + death_bump, MIN_PRESSURE_SCORE, MAX_PRESSURE_SCORE)

    else:
        # ----------------------------------------------------------------------
        # Innings 2: Run Chase (Required Run Rate, Wickets, & Urgency)
        # ----------------------------------------------------------------------
        # Base RRR sigmoid centered at 8.5 RPO
        # S(x) = 100 / (1 + exp(-0.45 * (RRR - 8.5)))
        safe_rrr = np.nan_to_num(rrr, nan=STANDARD_T20_PAR_RUN_RATE)
        p_base = 100.0 / (1.0 + np.exp(-0.45 * (safe_rrr - STANDARD_T20_PAR_RUN_RATE)))

        # Wicket depletion multiplier (0.80 at 0 wickets up to 1.40 at 9 wickets)
        safe_wkts = np.clip(wickets_before, 0, 10)
        w_mult = 0.80 + 0.60 * ((safe_wkts / 10.0) ** 1.25)

        # Urgency multiplier: late in chase, high RRR creates exponential stress
        rrr_diff = safe_rrr - STANDARD_T20_PAR_RUN_RATE
        u_mult = np.where(
            safe_rrr > STANDARD_T20_PAR_RUN_RATE,
            1.0 + 0.35 * f_bowled * np.clip(rrr_diff / STANDARD_T20_PAR_RUN_RATE, 0.0, 2.0),
            1.0 - 0.20 * f_bowled * np.clip(-rrr_diff / STANDARD_T20_PAR_RUN_RATE, 0.0, 1.0)
        )

        composite = p_base * w_mult * u_mult

        # Edge cases: Target reached
        target_reached = required_runs <= 0
        composite = np.where(target_reached, 0.0, composite)

        pressure = np.clip(composite, MIN_PRESSURE_SCORE, MAX_PRESSURE_SCORE)

    return np.round(pressure, 2)


def reconstruct_match_states(
    df_balls: pd.DataFrame,
    df_matches: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """
    Reconstructs complete prior match states for all deliveries:
    - score_before: batting team score prior to this ball
    - wickets_before: wickets lost prior to this ball
    - legal_balls_bowled_before: legal deliveries bowled prior to this ball
    - legal_balls_remaining_before: legal deliveries remaining in innings
    - target: innings 2 target (from Innings 1 score + 1, or DLS revised_target)
    - required_runs_before: runs needed to win prior to this ball (Innings 2)
    - required_run_rate_before: RRR prior to this ball (Innings 2)
    - current_run_rate_before: CRR prior to this ball
    - pressure_score_before: reproducible continuous pressure index [0, 100]
    
    GUARANTEE: No future-data leakage. All '_before' fields depend strictly on balls 0 to t-1.
    """
    if df_balls.empty:
        return df_balls

    df = df_balls.copy()

    # 1. Ensure Chronological Sequence
    sort_cols = [c for c in ["match_id", "innings", "innings_ball_num", "overid", "over_ball_num"] if c in df.columns]
    df = df.sort_values(sort_cols).reset_index(drop=True)

    # 2. Extract Event Flags on Delivery
    df["ball_total_runs"] = calculate_ball_runs(df)
    df["is_legal_delivery"] = identify_legal_deliveries(df.get("extras_type", pd.Series(index=df.index)))
    
    is_wkt_series = df.get("is_wicket", pd.Series(False, index=df.index))
    if is_wkt_series.dtype != bool:
        df["is_wicket_delivery"] = (
            is_wkt_series.astype(str).str.strip().str.lower().isin(["true", "1", "t", "yes"])
        )
    else:
        df["is_wicket_delivery"] = is_wkt_series

    # 3. Match Context & Revised Overs/Targets
    matches_info: Dict[str, Dict] = {}
    if df_matches is not None and not df_matches.empty:
        for _, row in df_matches.iterrows():
            mid = _clean_id(row["match_id"])
            rev_inn1 = row.get("first_inn_revised_overs")
            rev_inn2 = row.get("second_inn_revised_overs")
            rev_target = row.get("revised_target")
            
            matches_info[mid] = {
                "rev_inn1_balls": int(float(rev_inn1)) if pd.notnull(rev_inn1) and float(rev_inn1) > 0 else None,
                "rev_inn2_balls": int(float(rev_inn2)) if pd.notnull(rev_inn2) and float(rev_inn2) > 0 else None,
                "rev_target": int(float(rev_target)) if pd.notnull(rev_target) and float(rev_target) > 0 else None,
            }

    # 4. Group by Match & Innings for Prior State Cumsums
    grp = df.groupby(["match_id", "innings"], observed=True)

    # State before ball = cumulative sum up to this ball minus this ball's contribution
    df["score_before"] = grp["ball_total_runs"].cumsum() - df["ball_total_runs"]
    df["wickets_before"] = grp["is_wicket_delivery"].cumsum() - df["is_wicket_delivery"]
    df["legal_balls_bowled_before"] = grp["is_legal_delivery"].cumsum() - df["is_legal_delivery"]

    # 5. Innings 1 Final Scores for Target Resolution
    inn1_mask = df["innings"] == 1
    inn1_totals = {}
    if inn1_mask.any():
        for mid, sub_grp in df[inn1_mask].groupby("match_id", observed=True):
            inn1_totals[_clean_id(mid)] = int(sub_grp["ball_total_runs"].sum())

    # 6. Allocate Total Legal Balls & Target per Match & Innings
    def get_max_balls(row) -> int:
        mid = _clean_id(row["match_id"])
        inn = int(row["innings"])
        m_info = matches_info.get(mid, {})
        
        if inn == 1:
            return m_info.get("rev_inn1_balls") or STANDARD_T20_LEGAL_BALLS
        else:
            return m_info.get("rev_inn2_balls") or m_info.get("rev_inn1_balls") or STANDARD_T20_LEGAL_BALLS

    def get_target(row) -> Union[float, int]:
        inn = int(row["innings"])
        if inn != 2:
            return np.nan
        mid = _clean_id(row["match_id"])
        m_info = matches_info.get(mid, {})
        rev_t = m_info.get("rev_target")
        if rev_t is not None:
            return rev_t
        # Standard: Innings 1 final score + 1
        inn1_score = inn1_totals.get(mid, 0)
        return int(inn1_score) + 1

    df["total_legal_balls"] = df.apply(get_max_balls, axis=1)
    df["target"] = df.apply(get_target, axis=1)

    # 7. Legal Balls Remaining Before Delivery
    df["legal_balls_remaining_before"] = np.maximum(
        0, df["total_legal_balls"] - df["legal_balls_bowled_before"]
    )

    # 8. Current Run Rate Before Delivery (Safe division: NaN before first legal ball)
    balls_bowled = df["legal_balls_bowled_before"].values
    scores_before = df["score_before"].values
    safe_balls_bowled = np.where(balls_bowled > 0, balls_bowled, 1)
    df["current_run_rate_before"] = np.where(
        balls_bowled > 0,
        np.round((scores_before / safe_balls_bowled) * 6.0, 2),
        np.nan
    )

    # 9. Required Runs & Required Run Rate Before Delivery (Innings 2)
    inn2_mask = df["innings"] == 2
    targets = df["target"].values
    req_runs = np.where(
        inn2_mask,
        np.maximum(0, targets - scores_before),
        np.nan
    )
    df["required_runs_before"] = req_runs

    df["required_run_rate_before"], df["impossible_chase_state"] = compute_required_run_rate_and_chase_state(
        innings=df["innings"],
        legal_balls_remaining_before=df["legal_balls_remaining_before"],
        required_runs_before=df["required_runs_before"],
    )

    # 10. Pressure Score Computation (Vectorized per innings)
    df["pressure_score_before"] = 0.0

    # Innings 1 pressure
    if inn1_mask.any():
        sub_inn1 = df[inn1_mask]
        p_inn1 = compute_innings_pressure_vectorized(
            innings_num=1,
            crr=sub_inn1["current_run_rate_before"].values,
            rrr=np.zeros(len(sub_inn1)),
            wickets_before=sub_inn1["wickets_before"].values,
            legal_balls_bowled=sub_inn1["legal_balls_bowled_before"].values,
            legal_balls_remaining=sub_inn1["legal_balls_remaining_before"].values,
            total_legal_balls=sub_inn1["total_legal_balls"].values,
            required_runs=np.zeros(len(sub_inn1)),
        )
        df.loc[inn1_mask, "pressure_score_before"] = p_inn1

    # Innings 2 pressure
    if inn2_mask.any():
        sub_inn2 = df[inn2_mask]
        p_inn2 = compute_innings_pressure_vectorized(
            innings_num=2,
            crr=sub_inn2["current_run_rate_before"].values,
            rrr=sub_inn2["required_run_rate_before"].values,
            wickets_before=sub_inn2["wickets_before"].values,
            legal_balls_bowled=sub_inn2["legal_balls_bowled_before"].values,
            legal_balls_remaining=sub_inn2["legal_balls_remaining_before"].values,
            total_legal_balls=sub_inn2["total_legal_balls"].values,
            required_runs=sub_inn2["required_runs_before"].values,
        )
        df.loc[inn2_mask, "pressure_score_before"] = p_inn2

    return df
