"""
Feature engineering and performance aggregation module.
Computes real cricket statistics from empirical ball-by-ball records.
"""

from .metrics import (
    compute_batter_metrics,
    compute_bowler_metrics,
    compute_player_phase_splits,
    compute_head_to_head_matchup,
    compute_team_performance_summary,
)
from .match_state import (
    reconstruct_match_states,
    calculate_ball_runs,
    identify_legal_deliveries,
    compute_innings_pressure_vectorized,
)

__all__ = [
    "compute_batter_metrics",
    "compute_bowler_metrics",
    "compute_player_phase_splits",
    "compute_head_to_head_matchup",
    "compute_team_performance_summary",
    "reconstruct_match_states",
    "calculate_ball_runs",
    "identify_legal_deliveries",
    "compute_innings_pressure_vectorized",
]
