"""
Task 06 Feature Engineering Pipeline: Batting
Rajasthan Royals SupeRR Selector Season 2 Hackathon

Extracts, engineers, validates, and tags batting features for Machine Learning modeling.
Maintains strict separation between:
1. PREDICTORS (Baseline / Normal match condition features & player traits)
2. TARGETS (High-pressure outcomes: strike_rate_high, above-median binary flags)
3. QUARANTINED (Differentials, shrinkage metrics, reliability index - excluded from predictors to prevent leakage)
4. ARCHETYPES (Multi-dimensional profile features for unsupervised clustering)
"""

import os
import json
import numpy as np
import pandas as pd


def engineer_batting_features(
    input_path: str = "data/analytics/task_05_batter_reliability.csv",
    output_path: str = "data/ml/task_06_batter_features.csv",
    metadata_path: str = "data/ml/task_06_batter_feature_metadata.json"
) -> pd.DataFrame:
    """
    Builds the batting feature matrix and metadata dictionary.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    df = pd.read_csv(input_path)
    print(f"[Batting Features] Loaded {len(df)} records from {input_path}")

    # 1. Identifiers
    feat = pd.DataFrame()
    feat["striker_id"] = df["striker_id"]
    feat["striker_name"] = df["striker_name"]
    feat["batting_type"] = df["batting_type"]
    feat["eligibility_tier"] = df["eligibility_tier"]
    feat["reliability_grade"] = df["reliability_grade"]

    # 2. Player Traits & Demographics
    feat["batting_hand_LHB"] = (df["batting_type"].str.contains("Left|LHB", case=False, na=False)).astype(int)

    # 3. Baseline Normal-Condition Predictor Features (Pre-pressure Performance)
    feat["balls_faced_normal"] = df["balls_faced_normal"].fillna(0)
    feat["strike_rate_normal"] = df["strike_rate_normal"]
    feat["dot_pct_normal"] = df["dot_pct_normal"]
    feat["boundary_ball_pct_normal"] = df["boundary_ball_pct_normal"]
    feat["dismissal_rate_per_100_normal"] = df["dismissal_rate_per_100_normal"]
    feat["matches_normal"] = df["matches_normal"].fillna(0)

    # Engineered Baseline Metrics
    sixes_norm = df["sixes_normal"].fillna(0)
    fours_norm = df["fours_normal"].fillna(0)
    feat["six_ratio_normal"] = np.where(
        (fours_norm + sixes_norm) > 0,
        sixes_norm / (fours_norm + sixes_norm),
        0.0
    )
    
    runs_norm = df["runs_normal"].fillna(0)
    boundary_runs_norm = df["boundary_runs_normal"].fillna(0)
    running_runs = runs_norm - boundary_runs_norm
    running_balls = feat["balls_faced_normal"] - (fours_norm + sixes_norm)
    feat["running_strike_rate_normal"] = np.where(
        running_balls > 0,
        (running_runs / running_balls) * 100.0,
        0.0
    )

    # 4. Career Aggregates & Exposure Predictors
    feat["balls_faced_overall"] = df["balls_faced_overall"]
    feat["strike_rate_overall"] = df["strike_rate_overall"]
    feat["dot_pct_overall"] = df["dot_pct_overall"]
    feat["boundary_ball_pct_overall"] = df["boundary_ball_pct_overall"]
    feat["dismissal_rate_per_100_overall"] = df["dismissal_rate_per_100_overall"]
    
    # Competition split (IPL exposure ratio)
    feat["ipl_ball_share"] = np.where(
        df["balls_faced_overall"] > 0,
        df["balls_faced_ipl"] / df["balls_faced_overall"],
        0.0
    )

    # 5. High-Pressure Exposure & Phase Profile (Descriptive context)
    feat["balls_faced_high"] = df["balls_faced_high"].fillna(0)
    feat["high_pressure_ratio"] = np.where(
        df["balls_faced_overall"] > 0,
        df["balls_faced_high"] / df["balls_faced_overall"],
        0.0
    )
    
    bf_high = feat["balls_faced_high"]
    feat["high_balls_pp_share"] = np.where(bf_high > 0, df["high_balls_pp"] / bf_high, 0.0)
    feat["high_balls_mid_share"] = np.where(bf_high > 0, df["high_balls_mid"] / bf_high, 0.0)
    feat["high_balls_death_share"] = np.where(bf_high > 0, df["high_balls_death"] / bf_high, 0.0)

    # 6. High-Pressure Target Outcomes (Supervised Learning Targets)
    feat["strike_rate_high"] = df["strike_rate_high"]
    feat["dot_pct_high"] = df["dot_pct_high"]
    feat["boundary_ball_pct_high"] = df["boundary_ball_pct_high"]
    feat["dismissal_rate_per_100_high"] = df["dismissal_rate_per_100_high"]

    # Target Formulation:
    q_mask = df["eligibility_tier"] == "Qualified"
    median_sr_high_q = df.loc[q_mask, "strike_rate_high"].median()
    feat["target_above_median_sr_high"] = np.where(
        df["strike_rate_high"].notna(),
        (df["strike_rate_high"] >= median_sr_high_q).astype(int),
        np.nan
    )
    feat["target_high_pressure_outperformer"] = np.where(
        (df["strike_rate_high"].notna()) & (df["strike_rate_normal"].notna()),
        (df["strike_rate_high"] > df["strike_rate_normal"]).astype(int),
        np.nan
    )

    # 7. Quarantined Differential & Shrinkage Features (Strictly EXCLUDED from supervised predictors)
    feat["diff_strike_rate"] = df["diff_strike_rate"]
    feat["diff_dot_pct"] = df["diff_dot_pct"]
    feat["diff_dismissal_rate_per_100"] = df["diff_dismissal_rate_per_100"]
    feat["rel_diff_strike_rate"] = df["rel_diff_strike_rate"]
    feat["shrinkage_weight"] = df["shrinkage_weight"]
    feat["shrunk_diff_strike_rate"] = df["shrunk_diff_strike_rate"]
    feat["shrunk_diff_dot_pct"] = df["shrunk_diff_dot_pct"]
    feat["shrunk_diff_dismissal_rate"] = df["shrunk_diff_dismissal_rate"]
    feat["raw_composite_z"] = df["raw_composite_z"]
    feat["batter_reliability_index"] = df["batter_reliability_index"]
    feat["ci_lower_95"] = df["ci_lower_95"]
    feat["ci_upper_95"] = df["ci_upper_95"]
    feat["ci_std_error"] = df["ci_std_error"]
    feat["ci_width_95"] = df["ci_upper_95"] - df["ci_lower_95"]

    # Save to disk
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    feat.to_csv(output_path, index=False)
    print(f"[Batting Features] Successfully saved {feat.shape[0]} rows, {feat.shape[1]} columns to {output_path}")

    # Build and save metadata
    supervised_predictors = [
        "strike_rate_normal", "dot_pct_normal", "boundary_ball_pct_normal",
        "dismissal_rate_per_100_normal", "balls_faced_normal",
        "six_ratio_normal", "running_strike_rate_normal",
        "strike_rate_overall", "dot_pct_overall", "boundary_ball_pct_overall",
        "dismissal_rate_per_100_overall", "balls_faced_overall", "ipl_ball_share",
        "batting_hand_LHB"
    ]

    metadata = {
        "entity": "batter",
        "total_records": len(feat),
        "qualified_records": int((feat["eligibility_tier"] == "Qualified").sum()),
        "provisional_records": int((feat["eligibility_tier"] == "Provisional").sum()),
        "ineligible_records": int((feat["eligibility_tier"] == "Ineligible").sum()),
        "feature_groups": {
            "identifiers": [
                "striker_id", "striker_name", "batting_type", "eligibility_tier", "reliability_grade"
            ],
            "supervised_predictors": supervised_predictors,
            "supervised_targets": {
                "regression_primary": "strike_rate_high",
                "regression_secondary": ["dot_pct_high", "boundary_ball_pct_high", "dismissal_rate_per_100_high"],
                "classification_primary": "target_above_median_sr_high",
                "classification_secondary": "target_high_pressure_outperformer",
                "median_threshold_qualified": float(median_sr_high_q)
            },
            "unsupervised_archetype_features": [
                "shrunk_diff_strike_rate", "shrunk_diff_dot_pct", "shrunk_diff_dismissal_rate",
                "high_pressure_ratio", "high_balls_death_share"
            ],
            "quarantined_from_supervised_predictors": [
                "diff_strike_rate", "diff_dot_pct", "diff_dismissal_rate_per_100", "rel_diff_strike_rate",
                "shrinkage_weight", "shrunk_diff_strike_rate", "shrunk_diff_dot_pct", "shrunk_diff_dismissal_rate",
                "raw_composite_z", "batter_reliability_index", "ci_lower_95", "ci_upper_95",
                "ci_std_error", "ci_width_95", "balls_faced_high", "strike_rate_high",
                "dot_pct_high", "boundary_ball_pct_high", "dismissal_rate_per_100_high"
            ]
        }
    }
    
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"[Batting Features] Metadata written to {metadata_path}")
    
    return feat


if __name__ == "__main__":
    engineer_batting_features()
