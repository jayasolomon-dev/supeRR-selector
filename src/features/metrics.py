"""
SUPERR SELECTOR - Empirical Cricket Feature Engineering
Calculates ground-truth metrics directly from ball-by-ball delivery records.
NO mock or synthetic statistics are generated.
"""

from typing import Dict, Optional, Tuple
import pandas as pd
import numpy as np

try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False


def _cache_decorator(func):
    if HAS_STREAMLIT:
        return st.cache_data(show_spinner="Calculating empirical cricket statistics...")(func)
    return func


@_cache_decorator
def compute_batter_metrics(df_balls: pd.DataFrame, min_balls: int = 20) -> pd.DataFrame:
    """
    Computes comprehensive batting metrics for all batters in the dataset.
    Filtered by minimum balls faced for statistical relevance.
    """
    if df_balls.empty:
        return pd.DataFrame()

    # Pre-aggregations
    grouped = df_balls.groupby(["striker_id", "striker_name"], observed=True)

    # Core stats
    total_runs = grouped["runs"].sum()
    balls_faced = grouped["is_batter_ball"].sum()
    fours = grouped["is_four"].sum()
    sixes = grouped["is_six"].sum()
    dots = grouped["is_dot_ball"].sum()
    innings = grouped.apply(lambda x: len(x[["match_id", "innings"]].drop_duplicates()), include_groups=False)

    # Dismissals: where striker was the dismissed player
    dismissals = df_balls[df_balls["is_wicket"]].groupby("dismissed_player_id")["match_id"].count()
    
    # Styles
    batting_style = grouped["batting_type"].first()

    stats = pd.DataFrame({
        "striker_id": [idx[0] for idx in grouped.groups.keys()],
        "player_name": [idx[1] for idx in grouped.groups.keys()],
        "innings": innings.values,
        "runs": total_runs.values,
        "balls_faced": balls_faced.values,
        "fours": fours.values,
        "sixes": sixes.values,
        "dot_balls": dots.values,
        "batting_style": batting_style.values,
    }).set_index("striker_id")

    # Map dismissals
    stats["dismissals"] = stats.index.map(dismissals).fillna(0).astype(int)
    
    # Filter by minimum balls
    stats = stats[stats["balls_faced"] >= min_balls].copy()
    if stats.empty:
        return stats

    # Derived Rate Metrics
    stats["strike_rate"] = np.where(
        stats["balls_faced"] > 0,
        (stats["runs"] / stats["balls_faced"]) * 100.0,
        0.0
    ).round(2)

    stats["batting_average"] = np.where(
        stats["dismissals"] > 0,
        stats["runs"] / stats["dismissals"],
        stats["runs"]  # If never dismissed, career runs
    ).round(2)

    boundary_runs = (stats["fours"] * 4) + (stats["sixes"] * 6)
    stats["boundary_percent"] = np.where(
        stats["runs"] > 0,
        (boundary_runs / stats["runs"]) * 100.0,
        0.0
    ).round(2)

    stats["dot_ball_percent"] = np.where(
        stats["balls_faced"] > 0,
        (stats["dot_balls"] / stats["balls_faced"]) * 100.0,
        0.0
    ).round(2)

    return stats.sort_values("runs", ascending=False).reset_index()


@_cache_decorator
def compute_bowler_metrics(df_balls: pd.DataFrame, min_balls: int = 24) -> pd.DataFrame:
    """
    Computes comprehensive bowling metrics for all bowlers in the dataset.
    Filtered by minimum legal deliveries bowled.
    """
    if df_balls.empty:
        return pd.DataFrame()

    grouped = df_balls.groupby(["bowler_id", "bowler_name"], observed=True)

    legal_balls = grouped["is_legal_ball"].sum()
    runs_conceded = grouped["bowler_runs"].sum()
    wickets = grouped["is_bowler_wicket"].sum()
    dots = grouped["is_dot_ball"].sum()
    matches = grouped["match_id"].nunique()
    bowling_style = grouped["bowling_type"].first()
    pace_spin = grouped["pace_or_spin"].first()

    stats = pd.DataFrame({
        "bowler_id": [idx[0] for idx in grouped.groups.keys()],
        "player_name": [idx[1] for idx in grouped.groups.keys()],
        "matches": matches.values,
        "legal_balls": legal_balls.values,
        "runs_conceded": runs_conceded.values,
        "wickets": wickets.values,
        "dot_balls": dots.values,
        "bowling_style": bowling_style.values,
        "pace_or_spin": pace_spin.values,
    }).set_index("bowler_id")

    # Filter
    stats = stats[stats["legal_balls"] >= min_balls].copy()
    if stats.empty:
        return stats

    # Overs calculation
    complete_overs = stats["legal_balls"] // 6
    remaining_balls = stats["legal_balls"] % 6
    stats["overs_str"] = complete_overs.astype(str) + "." + remaining_balls.astype(str)
    overs_exact = stats["legal_balls"] / 6.0

    # Economy, Average, Strike Rate
    stats["economy"] = np.where(
        overs_exact > 0,
        stats["runs_conceded"] / overs_exact,
        0.0
    ).round(2)

    stats["bowling_average"] = np.where(
        stats["wickets"] > 0,
        stats["runs_conceded"] / stats["wickets"],
        np.nan
    ).round(2)

    stats["bowling_strike_rate"] = np.where(
        stats["wickets"] > 0,
        stats["legal_balls"] / stats["wickets"],
        np.nan
    ).round(2)

    stats["dot_ball_percent"] = np.where(
        stats["legal_balls"] > 0,
        (stats["dot_balls"] / stats["legal_balls"]) * 100.0,
        0.0
    ).round(2)

    return stats.sort_values("wickets", ascending=False).reset_index()


def compute_player_phase_splits(df_balls: pd.DataFrame, player_id: str) -> Dict[str, pd.DataFrame]:
    """
    Computes split metrics across Powerplay, Middle, and Death phases for a given player.
    Returns both batting and bowling phase tables.
    """
    player_id = str(player_id)
    
    # Batting splits
    batting_mask = df_balls["striker_id"].astype(str) == player_id
    df_bat = df_balls[batting_mask]
    bat_splits = pd.DataFrame()
    if not df_bat.empty:
        bat_grp = df_bat.groupby("phase", observed=True)
        bat_splits = pd.DataFrame({
            "phase": [idx for idx in bat_grp.groups.keys()],
            "runs": bat_grp["runs"].sum().values,
            "balls": bat_grp["is_batter_ball"].sum().values,
            "fours": bat_grp["is_four"].sum().values,
            "sixes": bat_grp["is_six"].sum().values,
            "dots": bat_grp["is_dot_ball"].sum().values,
        })
        bat_splits["strike_rate"] = np.where(
            bat_splits["balls"] > 0,
            (bat_splits["runs"] / bat_splits["balls"]) * 100.0,
            0.0
        ).round(2)

    # Bowling splits
    bowling_mask = df_balls["bowler_id"].astype(str) == player_id
    df_bowl = df_balls[bowling_mask]
    bowl_splits = pd.DataFrame()
    if not df_bowl.empty:
        bowl_grp = df_bowl.groupby("phase", observed=True)
        bowl_splits = pd.DataFrame({
            "phase": [idx for idx in bowl_grp.groups.keys()],
            "legal_balls": bowl_grp["is_legal_ball"].sum().values,
            "runs_conceded": bowl_grp["bowler_runs"].sum().values,
            "wickets": bowl_grp["is_bowler_wicket"].sum().values,
            "dots": bowl_grp["is_dot_ball"].sum().values,
        })
        overs_float = bowl_splits["legal_balls"] / 6.0
        bowl_splits["economy"] = np.where(
            overs_float > 0,
            bowl_splits["runs_conceded"] / overs_float,
            0.0
        ).round(2)

    return {"batting": bat_splits, "bowling": bowl_splits}


def compute_head_to_head_matchup(
    df_balls: pd.DataFrame, striker_id: str, bowler_id: str
) -> Dict[str, any]:
    """
    Extracts real empirical encounter statistics between a specific batter and bowler.
    """
    mask = (
        (df_balls["striker_id"].astype(str) == str(striker_id)) &
        (df_balls["bowler_id"].astype(str) == str(bowler_id))
    )
    encounters = df_balls[mask]
    if encounters.empty:
        return {
            "has_data": False,
            "balls_faced": 0,
            "runs_scored": 0,
            "dismissals": 0,
            "strike_rate": 0.0,
            "dots": 0,
            "fours": 0,
            "sixes": 0,
        }

    runs = encounters["runs"].sum()
    balls = encounters["is_batter_ball"].sum()
    dismissals = encounters["is_bowler_wicket"].sum()
    fours = encounters["is_four"].sum()
    sixes = encounters["is_six"].sum()
    dots = encounters["is_dot_ball"].sum()
    sr = round((runs / balls * 100.0), 2) if balls > 0 else 0.0

    return {
        "has_data": True,
        "balls_faced": int(balls),
        "runs_scored": int(runs),
        "dismissals": int(dismissals),
        "strike_rate": sr,
        "dots": int(dots),
        "fours": int(fours),
        "sixes": int(sixes),
        "deliveries": encounters,
    }


def compute_team_performance_summary(
    df_matches: pd.DataFrame, df_balls: pd.DataFrame
) -> pd.DataFrame:
    """
    Computes team-level win rates, toss outcomes, and average totals.
    """
    if df_matches.empty:
        return pd.DataFrame()

    teams_set = set(df_matches["home_team"].dropna()).union(set(df_matches["away_team"].dropna()))
    records = []

    for team in sorted(teams_set):
        t_matches = df_matches[(df_matches["home_team"] == team) | (df_matches["away_team"] == team)]
        total_played = len(t_matches)
        if total_played == 0:
            continue
        wins = len(df_matches[df_matches["result"].str.contains(team, case=False, na=False)])
        toss_wins = len(t_matches[t_matches["home_team"] == team][t_matches["toss_win_team_id"] == t_matches["home_team_id"]])
        
        records.append({
            "team_name": team,
            "matches_played": total_played,
            "wins": wins,
            "win_rate_percent": round((wins / total_played) * 100.0, 1),
        })

    return pd.DataFrame(records).sort_values("win_rate_percent", ascending=False)

