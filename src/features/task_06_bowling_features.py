"""
Task 06 Feature Engineering Pipeline: Bowling
Rajasthan Royals SupeRR Selector Season 2 Hackathon

Extracts, engineers, validates, and tags bowling features for Machine Learning modeling.
Maintains strict separation between:
1. PREDICTORS (Baseline / Normal match condition features & player traits)
2. TARGETS (High-pressure outcomes: economy_rate_high, below-median binary flags)
3. QUARANTINED (Differentials, shrinkage metrics, reliability index - excluded from predictors to prevent leakage)
4. ARCHETYPES (Multi-dimensional profile features for unsupervised clustering)
"""

import os
import json
import numpy as np
import pandas as pd


def engineer_bowling_features(
    input_path: str = "data/analytics/task_05_bowler_reliability.csv",
    output_path: str = "data/ml/task_06_bowler_features.csv",
    metadata_path: str = "data/ml/task_06_bowler_feature_metadata.json"
) -> pd.DataFrame:
    """
    Builds the bowling feature matrix and metadata dictionary.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    df = pd.read_csv(input_path)
    print(f"[Bowling Features] Loaded {len(df)} records from {input_path}")

    # 1. Identifiers
    feat = pd.DataFrame()
    feat["bowler_id"] = df["bowler_id"]
    feat["bowler_name"] = df["bowler_name"]
    feat["bowling_type"] = df["bowling_type"]
    feat["pace_or_spin"] = df["pace_or_spin"]
    feat["eligibility_tier"] = df["eligibility_tier"]
    feat["reliability_grade"] = df["reliability_grade"]

    # 2. Player Traits & Demographics
    feat["is_spin"] = (df["pace_or_spin"].str.lower() == "spin").astype(int)
    feat["bowling_arm_left"] = (df["bowling_type"].str.contains("Left|slow left", case=False, na=False)).astype(int)

    # 3. Baseline Normal-Condition Predictor Features (Pre-pressure Performance)
    feat["legal_balls_normal"] = df["legal_balls_normal"].fillna(0)
    feat["economy_rate_normal"] = df["economy_rate_normal"]
    feat["wickets_per_over_normal"] = df["wickets_per_over_normal"]
    feat["dot_pct_normal"] = df["dot_pct_normal"]
    feat["boundary_conceded_pct_normal"] = df["boundary_conceded_pct_normal"]
    feat["matches_normal"] = df["matches_normal"].fillna(0)

    # Disciplined Extras / Control Rate
    wides_norm = df["wides_normal"].fillna(0)
    noballs_norm = df["noballs_normal"].fillna(0)
    feat["extras_per_legal_ball_normal"] = np.where(
        feat["legal_balls_normal"] > 0,
        (wides_norm + noballs_norm) / feat["legal_balls_normal"],
        0.0
    )
    
    # Boundary distribution conceded
    fours_c_norm = df["fours_conceded_normal"].fillna(0)
    sixes_c_norm = df["sixes_conceded_normal"].fillna(0)
    feat["six_conceded_ratio_normal"] = np.where(
        (fours_c_norm + sixes_c_norm) > 0,
        sixes_c_norm / (fours_c_norm + sixes_c_norm),
        0.0
    )

    # Imputed bowling strike rate for zero wickets (avoiding inf/nan)
    wickets_norm = df["wickets_normal"].fillna(0)
    feat["bowling_strike_rate_normal_clean"] = np.where(
        wickets_norm > 0,
        feat["legal_balls_normal"] / wickets_norm,
        120.0
    )
    feat["zero_wickets_normal_flag"] = (wickets_norm == 0).astype(int)

    # 4. Career Aggregates & Exposure Predictors
    feat["legal_balls_overall"] = df["legal_balls_overall"]
    feat["economy_rate_overall"] = df["economy_rate_overall"]
    feat["wickets_per_over_overall"] = df["wickets_per_over_overall"]
    feat["dot_pct_overall"] = df["dot_pct_overall"]
    feat["boundary_conceded_pct_overall"] = df["boundary_conceded_pct_overall"]
    
    # Competition split (IPL exposure ratio)
    feat["ipl_ball_share"] = np.where(
        df["legal_balls_overall"] > 0,
        df["legal_balls_ipl"] / df["legal_balls_overall"],
        0.0
    )

    # 5. High-Pressure Exposure & Phase Profile (Descriptive context)
    feat["legal_balls_high"] = df["legal_balls_high"].fillna(0)
    feat["high_pressure_ratio"] = np.where(
        df["legal_balls_overall"] > 0,
        df["legal_balls_high"] / df["legal_balls_overall"],
        0.0
    )
    
    lb_high = feat["legal_balls_high"]
    feat["high_balls_pp_share"] = np.where(lb_high > 0, df["high_balls_pp"] / lb_high, 0.0)
    feat["high_balls_mid_share"] = np.where(lb_high > 0, df["high_balls_mid"] / lb_high, 0.0)
    feat["high_balls_death_share"] = np.where(lb_high > 0, df["high_balls_death"] / lb_high, 0.0)

    # 6. High-Pressure Target Outcomes (Supervised Learning Targets)
    feat["economy_rate_high"] = df["economy_rate_high"]
    feat["wickets_per_over_high"] = df["wickets_per_over_high"]
    feat["dot_pct_high"] = df["dot_pct_high"]
    feat["boundary_conceded_pct_high"] = df["boundary_conceded_pct_high"]
    
    wickets_high = df["wickets_high"].fillna(0)
    feat["bowling_strike_rate_high_clean"] = np.where(
        wickets_high > 0,
        df["legal_balls_high"] / wickets_high,
        120.0
    )

    # Target Formulation:
    q_mask = df["eligibility_tier"] == "Qualified"
    median_econ_high_q = df.loc[q_mask, "economy_rate_high"].median()
    feat["target_below_median_econ_high"] = np.where(
        df["economy_rate_high"].notna(),
        (df["economy_rate_high"] <= median_econ_high_q).astype(int),
        np.nan
    )
    feat["target_high_pressure_outperformer"] = np.where(
        (df["economy_rate_high"].notna()) & (df["economy_rate_normal"].notna()),
        (df["economy_rate_high"] < df["economy_rate_normal"]).astype(int),
        np.nan
    )

    # 7. Quarantined Differential & Shrinkage Features (Strictly EXCLUDED from supervised predictors)
    feat["diff_economy_rate"] = df["diff_economy_rate"]
    feat["diff_wickets_per_over"] = df["diff_wickets_per_over"]
    feat["diff_dot_pct"] = df["diff_dot_pct"]
    feat["diff_boundary_conceded_pct"] = df["diff_boundary_conceded_pct"]
    feat["rel_diff_economy_rate"] = df["rel_diff_economy_rate"]
    feat["shrinkage_weight"] = df["shrinkage_weight"]
    feat["shrunk_diff_economy_rate"] = df["shrunk_diff_economy_rate"]
    feat["shrunk_diff_wickets_per_over"] = df["shrunk_diff_wickets_per_over"]
    feat["shrunk_diff_dot_pct"] = df["shrunk_diff_dot_pct"]
    feat["raw_composite_z"] = df["raw_composite_z"]
    feat["bowler_reliability_index"] = df["bowler_reliability_index"]
    feat["ci_lower_95"] = df["ci_lower_95"]
    feat["ci_upper_95"] = df["ci_upper_95"]
    feat["ci_std_error"] = df["ci_std_error"]
    feat["ci_width_95"] = df["ci_upper_95"] - df["ci_lower_95"]

    # Save to disk
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    feat.to_csv(output_path, index=False)
    print(f"[Bowling Features] Successfully saved {feat.shape[0]} rows, {feat.shape[1]} columns to {output_path}")

    # Build and save metadata
    supervised_predictors = [
        "economy_rate_normal", "wickets_per_over_normal", "dot_pct_normal",
        "boundary_conceded_pct_normal", "legal_balls_normal",
        "extras_per_legal_ball_normal", "six_conceded_ratio_normal",
        "bowling_strike_rate_normal_clean", "zero_wickets_normal_flag",
        "economy_rate_overall", "wickets_per_over_overall",
        "dot_pct_overall", "boundary_conceded_pct_overall", "legal_balls_overall",
        "ipl_ball_share", "is_spin", "bowling_arm_left"
    ]

    metadata = {
        "entity": "bowler",
        "total_records": len(feat),
        "qualified_records": int((feat["eligibility_tier"] == "Qualified").sum()),
        "provisional_records": int((feat["eligibility_tier"] == "Provisional").sum()),
        "ineligible_records": int((feat["eligibility_tier"] == "Ineligible").sum()),
        "feature_groups": {
            "identifiers": [
                "bowler_id", "bowler_name", "bowling_type", "pace_or_spin", "eligibility_tier", "reliability_grade"
            ],
            "supervised_predictors": supervised_predictors,
            "supervised_targets": {
                "regression_primary": "economy_rate_high",
                "regression_secondary": ["wickets_per_over_high", "dot_pct_high", "boundary_conceded_pct_high"],
                "classification_primary": "target_below_median_econ_high",
                "classification_secondary": "target_high_pressure_outperformer",
                "median_threshold_qualified": float(median_econ_high_q)
            },
            "unsupervised_archetype_features": [
                "shrunk_diff_economy_rate", "shrunk_diff_wickets_per_over", "shrunk_diff_dot_pct",
                "high_pressure_ratio", "high_balls_death_share"
            ],
            "quarantined_from_supervised_predictors": [
                "diff_economy_rate", "diff_wickets_per_over", "diff_dot_pct", "diff_boundary_conceded_pct",
                "rel_diff_economy_rate", "shrinkage_weight", "shrunk_diff_economy_rate",
                "shrunk_diff_wickets_per_over", "shrunk_diff_dot_pct", "raw_composite_z",
                "bowler_reliability_index", "ci_lower_95", "ci_upper_95", "ci_std_error",
                "ci_width_95", "legal_balls_high", "economy_rate_high", "wickets_per_over_high",
                "dot_pct_high", "boundary_conceded_pct_high", "bowling_strike_rate_high_clean"
            ]
        }
    }
    
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"[Bowling Features] Metadata written to {metadata_path}")
    
    return feat


if __name__ == "__main__":
    engineer_bowling_features()
