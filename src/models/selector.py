"""
SUPERR SELECTOR - Scikit-learn Squad Clustering & Tactical Selection Engine
Performs unsupervised player profiling, rating normalization, and squad composition.
"""

from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA


def cluster_player_archetypes(
    df_batters: pd.DataFrame, n_clusters: int = 3
) -> Tuple[pd.DataFrame, KMeans, PCA]:
    """
    Applies Scikit-learn StandardScaler and KMeans clustering on empirical batting metrics
    to discover tactical player archetypes (e.g., Anchors, Boundary Hitters, Finishers).
    Also performs 2D PCA for visual projection.
    """
    if df_batters.empty or len(df_batters) < n_clusters:
        return df_batters, None, None

    features = ["strike_rate", "batting_average", "boundary_percent", "dot_ball_percent"]
    X = df_batters[features].fillna(df_batters[features].mean())

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X_scaled)

    # 2D PCA for plotting
    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(X_scaled)

    df_result = df_batters.copy()
    df_result["cluster_id"] = clusters
    df_result["pca_x"] = coords[:, 0]
    df_result["pca_y"] = coords[:, 1]

    # Map cluster centroids to meaningful cricket archetypes
    cluster_means = df_result.groupby("cluster_id")[features].mean()
    cluster_labels = {}
    for cid, row in cluster_means.iterrows():
        if row["boundary_percent"] > cluster_means["boundary_percent"].median() and row["strike_rate"] > cluster_means["strike_rate"].median():
            cluster_labels[cid] = "Power Finisher / Boundary Hitter"
        elif row["batting_average"] > cluster_means["batting_average"].median() and row["dot_ball_percent"] < cluster_means["dot_ball_percent"].median():
            cluster_labels[cid] = "Anchor / Accumulator"
        else:
            cluster_labels[cid] = "Dynamic Stroke Maker"

    df_result["archetype"] = df_result["cluster_id"].map(cluster_labels)
    return df_result, kmeans, pca


def compute_composite_player_rating(
    df_batters: pd.DataFrame, df_bowlers: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Calculates normalized rating scores (0 - 100) using z-score feature scaling.
    Derived purely from true empirical stats.
    """
    # 1. Batting Rating
    df_b = df_batters.copy()
    if not df_b.empty and len(df_b) > 2:
        sr_z = (df_b["strike_rate"] - df_b["strike_rate"].mean()) / (df_b["strike_rate"].std() + 1e-6)
        avg_z = (df_b["batting_average"] - df_b["batting_average"].mean()) / (df_b["batting_average"].std() + 1e-6)
        bound_z = (df_b["boundary_percent"] - df_b["boundary_percent"].mean()) / (df_b["boundary_percent"].std() + 1e-6)
        dot_z = (df_b["dot_ball_percent"] - df_b["dot_ball_percent"].mean()) / (df_b["dot_ball_percent"].std() + 1e-6)
        
        # Weighted composite score
        composite = (0.35 * sr_z) + (0.35 * avg_z) + (0.20 * bound_z) - (0.10 * dot_z)
        
        # Min-Max scale to 40 - 99 scale for intuitive sports rating
        c_min, c_max = composite.min(), composite.max()
        if c_max > c_min:
            df_b["batting_rating"] = ((composite - c_min) / (c_max - c_min) * 59.0 + 40.0).round(1)
        else:
            df_b["batting_rating"] = 70.0
    else:
        df_b["batting_rating"] = 70.0

    # 2. Bowling Rating
    df_bowl = df_bowlers.copy()
    if not df_bowl.empty and len(df_bowl) > 2:
        econ_z = (df_bowl["economy"] - df_bowl["economy"].mean()) / (df_bowl["economy"].std() + 1e-6)
        wkts_z = (df_bowl["wickets"] - df_bowl["wickets"].mean()) / (df_bowl["wickets"].std() + 1e-6)
        dots_z = (df_bowl["dot_ball_percent"] - df_bowl["dot_ball_percent"].mean()) / (df_bowl["dot_ball_percent"].std() + 1e-6)
        
        # Lower economy is better, more wickets is better
        composite_bowl = (-0.40 * econ_z) + (0.45 * wkts_z) + (0.15 * dots_z)
        
        b_min, b_max = composite_bowl.min(), composite_bowl.max()
        if b_max > b_min:
            df_bowl["bowling_rating"] = ((composite_bowl - b_min) / (b_max - b_min) * 59.0 + 40.0).round(1)
        else:
            df_bowl["bowling_rating"] = 70.0
    else:
        df_bowl["bowling_rating"] = 70.0

    return df_b, df_bowl


def optimize_squad_selection(
    df_batters_rated: pd.DataFrame,
    df_bowlers_rated: pd.DataFrame,
    wk_ids: set,
    min_batters: int = 4,
    min_bowlers: int = 4,
    min_allrounders: int = 2,
    target_squad_size: int = 11,
) -> pd.DataFrame:
    """
    Selects a balanced Playing XI meeting tactical composition constraints:
    - At least 1 Wicketkeeper
    - Specialized Top-order batters
    - Balanced Pace/Spin bowling attack
    - All-rounders who contribute with both bat and ball
    """
    # Merge ratings to find all-rounders
    merged = pd.merge(
        df_batters_rated[["player_id", "player_name", "batting_rating", "runs", "strike_rate"]],
        df_bowlers_rated[["player_id", "bowling_rating", "wickets", "economy", "pace_or_spin"]],
        on="player_id",
        how="outer",
    )
    
    # Fill names and missing ratings
    merged["batting_rating"] = merged["batting_rating"].fillna(40.0)
    merged["bowling_rating"] = merged["bowling_rating"].fillna(40.0)
    merged["allrounder_rating"] = ((merged["batting_rating"] + merged["bowling_rating"]) / 2.0).round(1)
    merged["is_wk"] = merged["player_id"].astype(str).isin({str(x) for x in wk_ids})

    selected = []
    selected_ids = set()

    # 1. Select Best Wicketkeeper
    wk_candidates = merged[merged["is_wk"]].sort_values("batting_rating", ascending=False)
    if not wk_candidates.empty:
        best_wk = wk_candidates.iloc[0].to_dict()
        best_wk["squad_role"] = "Wicketkeeper-Batter"
        selected.append(best_wk)
        selected_ids.add(best_wk["player_id"])

    # 2. Select Specialist Batters
    bat_candidates = merged[
        (~merged["player_id"].isin(selected_ids)) &
        (merged["batting_rating"] >= 65)
    ].sort_values("batting_rating", ascending=False)

    for _, row in bat_candidates.head(min_batters).iterrows():
        b = row.to_dict()
        b["squad_role"] = "Specialist Batter"
        selected.append(b)
        selected_ids.add(b["player_id"])

    # 3. Select All-Rounders
    ar_candidates = merged[
        (~merged["player_id"].isin(selected_ids)) &
        (merged["batting_rating"] >= 55) &
        (merged["bowling_rating"] >= 55)
    ].sort_values("allrounder_rating", ascending=False)

    for _, row in ar_candidates.head(min_allrounders).iterrows():
        ar = row.to_dict()
        ar["squad_role"] = "All-Rounder"
        selected.append(ar)
        selected_ids.add(ar["player_id"])

    # 4. Select Specialist Bowlers (Pace & Spin balance)
    bowl_candidates = merged[
        ~merged["player_id"].isin(selected_ids)
    ].sort_values("bowling_rating", ascending=False)

    needed_bowlers = target_squad_size - len(selected)
    for _, row in bowl_candidates.head(needed_bowlers).iterrows():
        bw = row.to_dict()
        bw["squad_role"] = "Specialist Bowler"
        selected.append(bw)
        selected_ids.add(bw["player_id"])

    df_xi = pd.DataFrame(selected)
    return df_xi

