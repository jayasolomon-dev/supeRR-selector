"""
Machine learning and tactical squad selection algorithms.
Utilizes Scikit-learn clustering and standardized rating models.
"""

from .selector import (
    cluster_player_archetypes,
    compute_composite_player_rating,
    optimize_squad_selection,
)

__all__ = [
    "cluster_player_archetypes",
    "compute_composite_player_rating",
    "optimize_squad_selection",
]

