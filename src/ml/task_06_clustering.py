"""
Task 06 Unsupervised Clustering & Archetype Modeling Pipeline
Rajasthan Royals SupeRR Selector Season 2 Hackathon

Identifies strategic player archetypes under pressure using K-Means clustering
on standardized multi-dimensional pressure differential profiles.

Completely separates Batting and Bowling.
Trains on Qualified cohort, projects onto Provisional cohort.
"""

import os
import json
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score


def run_batting_clustering(
    input_path: str = "data/ml/task_06_batter_features.csv",
    output_path: str = "data/ml/task_06_batter_archetypes.csv",
    random_state: int = 42
) -> dict:
    """
    Fits K-Means clustering on Qualified batters and maps strategic archetypes.
    """
    df = pd.read_csv(input_path)
    q_mask = df["eligibility_tier"] == "Qualified"
    p_mask = df["eligibility_tier"] == "Provisional"
    
    arch_cols = [
        "shrunk_diff_strike_rate", "shrunk_diff_dot_pct", "shrunk_diff_dismissal_rate",
        "high_pressure_ratio", "high_balls_death_share"
    ]
    
    scaler = StandardScaler()
    X_q = scaler.fit_transform(df.loc[q_mask, arch_cols])
    
    # Grid search evaluation
    grid_eval = {}
    for k in range(2, 7):
        km_test = KMeans(n_clusters=k, n_init=20, random_state=random_state).fit(X_q)
        grid_eval[f"k_{k}"] = {
            "silhouette": round(float(silhouette_score(X_q, km_test.labels_)), 3),
            "davies_bouldin": round(float(davies_bouldin_score(X_q, km_test.labels_)), 3),
            "inertia": round(float(km_test.inertia_), 3)
        }
    
    # Optimal k=3
    k_opt = 3
    kmeans = KMeans(n_clusters=k_opt, n_init=20, random_state=random_state)
    kmeans.fit(X_q)
    q_labels = kmeans.labels_

    # Determine archetype names based on centroids
    centroids_raw = scaler.inverse_transform(kmeans.cluster_centers_)
    centroids_df = pd.DataFrame(centroids_raw, columns=arch_cols)

    archetype_map = {}
    for c_idx in range(k_opt):
        diff_sr = centroids_df.loc[c_idx, "shrunk_diff_strike_rate"]
        death_share = centroids_df.loc[c_idx, "high_balls_death_share"]
        if diff_sr < 5.0:
            archetype_map[c_idx] = "Pressure Vulnerable"
        elif death_share >= 0.50:
            archetype_map[c_idx] = "Death Phase Finisher"
        else:
            archetype_map[c_idx] = "Top/Middle Order Accelerator"

    # Assign to dataset
    df["archetype_id"] = -1
    df["archetype_name"] = "Ineligible / Unassigned"
    
    df.loc[q_mask, "archetype_id"] = q_labels
    df.loc[q_mask, "archetype_name"] = [archetype_map[l] for l in q_labels]

    # Project Provisional batters
    if p_mask.sum() > 0:
        X_p = scaler.transform(df.loc[p_mask, arch_cols].fillna(0))
        p_labels = kmeans.predict(X_p)
        df.loc[p_mask, "archetype_id"] = p_labels
        df.loc[p_mask, "archetype_name"] = [f"{archetype_map[l]} (Provisional)" for l in p_labels]

    # Export
    cols_to_export = [
        "striker_id", "striker_name", "batting_type", "eligibility_tier", "reliability_grade",
        "archetype_id", "archetype_name", "batter_reliability_index", "strike_rate_normal",
        "strike_rate_high", "shrunk_diff_strike_rate", "shrunk_diff_dot_pct",
        "shrunk_diff_dismissal_rate", "high_pressure_ratio", "high_balls_death_share"
    ]
    df[cols_to_export].to_csv(output_path, index=False)
    print(f"[Batting Clustering] Saved archetypes to {output_path}")

    # Summary
    cluster_summary = {
        "entity": "batter",
        "k_selected": k_opt,
        "grid_evaluation": grid_eval,
        "silhouette_score": grid_eval[f"k_{k_opt}"]["silhouette"],
        "davies_bouldin_index": grid_eval[f"k_{k_opt}"]["davies_bouldin"],
        "archetype_mapping": {str(k): v for k, v in archetype_map.items()},
        "qualified_distribution": df.loc[q_mask, "archetype_name"].value_counts().to_dict(),
        "provisional_distribution": df.loc[p_mask, "archetype_name"].value_counts().to_dict(),
        "centroids_raw": centroids_df.to_dict(orient="index")
    }
    return cluster_summary


def run_bowling_clustering(
    input_path: str = "data/ml/task_06_bowler_features.csv",
    output_path: str = "data/ml/task_06_bowler_archetypes.csv",
    random_state: int = 42
) -> dict:
    """
    Fits K-Means clustering on Qualified bowlers and maps strategic archetypes.
    """
    df = pd.read_csv(input_path)
    q_mask = df["eligibility_tier"] == "Qualified"
    p_mask = df["eligibility_tier"] == "Provisional"
    
    arch_cols = [
        "shrunk_diff_economy_rate", "shrunk_diff_wickets_per_over", "shrunk_diff_dot_pct",
        "high_pressure_ratio", "high_balls_death_share"
    ]
    
    scaler = StandardScaler()
    X_q = scaler.fit_transform(df.loc[q_mask, arch_cols])
    
    # Grid search evaluation
    grid_eval = {}
    for k in range(2, 7):
        km_test = KMeans(n_clusters=k, n_init=20, random_state=random_state).fit(X_q)
        grid_eval[f"k_{k}"] = {
            "silhouette": round(float(silhouette_score(X_q, km_test.labels_)), 3),
            "davies_bouldin": round(float(davies_bouldin_score(X_q, km_test.labels_)), 3),
            "inertia": round(float(km_test.inertia_), 3)
        }
    
    # Optimal k=3
    k_opt = 3
    kmeans = KMeans(n_clusters=k_opt, n_init=20, random_state=random_state)
    kmeans.fit(X_q)
    q_labels = kmeans.labels_

    # Determine archetype names based on centroids
    centroids_raw = scaler.inverse_transform(kmeans.cluster_centers_)
    centroids_df = pd.DataFrame(centroids_raw, columns=arch_cols)

    archetype_map = {}
    for c_idx in range(k_opt):
        diff_econ = centroids_df.loc[c_idx, "shrunk_diff_economy_rate"]
        death_share = centroids_df.loc[c_idx, "high_balls_death_share"]
        diff_wpo = centroids_df.loc[c_idx, "shrunk_diff_wickets_per_over"]
        
        if diff_econ > 3.0:
            archetype_map[c_idx] = "High-Pressure Conceder"
        elif death_share >= 0.60 or diff_wpo > 0.05:
            archetype_map[c_idx] = "Death Wicket Enforcer"
        else:
            archetype_map[c_idx] = "Middle & Powerplay Restrictor"

    # Assign to dataset
    df["archetype_id"] = -1
    df["archetype_name"] = "Ineligible / Unassigned"
    
    df.loc[q_mask, "archetype_id"] = q_labels
    df.loc[q_mask, "archetype_name"] = [archetype_map[l] for l in q_labels]

    # Project Provisional bowlers
    if p_mask.sum() > 0:
        X_p = scaler.transform(df.loc[p_mask, arch_cols].fillna(0))
        p_labels = kmeans.predict(X_p)
        df.loc[p_mask, "archetype_id"] = p_labels
        df.loc[p_mask, "archetype_name"] = [f"{archetype_map[l]} (Provisional)" for l in p_labels]

    # Export
    cols_to_export = [
        "bowler_id", "bowler_name", "bowling_type", "pace_or_spin", "eligibility_tier", "reliability_grade",
        "archetype_id", "archetype_name", "bowler_reliability_index", "economy_rate_normal",
        "economy_rate_high", "shrunk_diff_economy_rate", "shrunk_diff_wickets_per_over",
        "shrunk_diff_dot_pct", "high_pressure_ratio", "high_balls_death_share"
    ]
    df[cols_to_export].to_csv(output_path, index=False)
    print(f"[Bowling Clustering] Saved archetypes to {output_path}")

    # Summary
    cluster_summary = {
        "entity": "bowler",
        "k_selected": k_opt,
        "grid_evaluation": grid_eval,
        "silhouette_score": grid_eval[f"k_{k_opt}"]["silhouette"],
        "davies_bouldin_index": grid_eval[f"k_{k_opt}"]["davies_bouldin"],
        "archetype_mapping": {str(k): v for k, v in archetype_map.items()},
        "qualified_distribution": df.loc[q_mask, "archetype_name"].value_counts().to_dict(),
        "provisional_distribution": df.loc[p_mask, "archetype_name"].value_counts().to_dict(),
        "centroids_raw": centroids_df.to_dict(orient="index")
    }
    return cluster_summary


def run_clustering_pipeline():
    print("="*60)
    print("STARTING TASK 06 CLUSTERING & ARCHETYPE MODELING PIPELINE")
    print("="*60)
    
    b_summary = run_batting_clustering()
    p_summary = run_bowling_clustering()

    summary = {
        "batting_clustering": b_summary,
        "bowling_clustering": p_summary
    }

    with open("data/ml/task_06_cluster_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"[Clustering] Exported summary to data/ml/task_06_cluster_summary.json")
    print("="*60)
    print("TASK 06 CLUSTERING COMPLETE")
    print("="*60)


if __name__ == "__main__":
    run_clustering_pipeline()

