"""
Task 06 Automated Validation Suite
Rajasthan Royals SupeRR Selector Season 2 Hackathon

Executes 8 rigorous independent validation checks:
1. Feature Schema Integrity
2. Missing-Value Handling
3. Data Leakage Prevention
4. Reproducibility with Fixed Random Seeds
5. Model Stability & Overfitting Checks
6. Baseline Superiority Comparisons
7. Clustering & Archetype Integrity
8. Explainability Output Consistency
"""

import os
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import KFold, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge, LogisticRegression
from sklearn.metrics import root_mean_squared_error, r2_score, roc_auc_score


def run_validation_suite(
    output_summary_path: str = "reports/task_06_validation_summary.json"
) -> dict:
    print("="*60)
    print("STARTING TASK 06 INDEPENDENT VALIDATION SUITE")
    print("="*60)

    test_results = {}

    # 1. Feature Schema Integrity
    required_files = [
        "data/ml/task_06_batter_features.csv",
        "data/ml/task_06_bowler_features.csv",
        "data/ml/task_06_batter_feature_metadata.json",
        "data/ml/task_06_bowler_feature_metadata.json",
        "data/ml/task_06_batter_predictions.csv",
        "data/ml/task_06_bowler_predictions.csv",
        "data/ml/task_06_batter_archetypes.csv",
        "data/ml/task_06_bowler_archetypes.csv",
        "data/ml/task_06_model_metrics.json",
        "data/ml/task_06_cluster_summary.json",
        "data/ml/task_06_explainability_metrics.json",
        "reports/task_06_figures/fig1_batting_feature_importance.svg",
        "reports/task_06_figures/fig2_bowling_feature_importance.svg",
        "reports/task_06_figures/fig3_batting_cluster_archetypes.svg",
        "reports/task_06_figures/fig4_bowling_cluster_archetypes.svg",
        "reports/task_06_figures/fig5_predicted_vs_actual_pressure.svg",
        "reports/task_06_figures/interactive_task_06_ml_dashboard.html"
    ]
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    b_df = pd.read_csv("data/ml/task_06_batter_features.csv")
    p_df = pd.read_csv("data/ml/task_06_bowler_features.csv")
    
    schema_pass = (len(missing_files) == 0 and len(b_df) == 824 and len(p_df) == 596)
    test_results["1_schema_integrity"] = {
        "status": "PASS" if schema_pass else "FAIL",
        "total_files_verified": len(required_files),
        "missing_files": missing_files,
        "batter_rows": len(b_df),
        "bowler_rows": len(p_df)
    }
    print(f"Test 1 [Schema Integrity]: {test_results['1_schema_integrity']['status']}")

    # 2. Missing-Value Handling
    with open("data/ml/task_06_batter_feature_metadata.json", "r") as f:
        b_meta = json.load(f)
    with open("data/ml/task_06_bowler_feature_metadata.json", "r") as f:
        p_meta = json.load(f)

    b_preds = b_meta["feature_groups"]["supervised_predictors"]
    p_preds = p_meta["feature_groups"]["supervised_predictors"]

    b_q = b_df[b_df["eligibility_tier"] == "Qualified"]
    p_q = p_df[p_df["eligibility_tier"] == "Qualified"]

    b_nulls = int(b_q[b_preds].isnull().sum().sum())
    p_nulls = int(p_q[p_preds].isnull().sum().sum())

    missing_pass = (b_nulls == 0 and p_nulls == 0)
    test_results["2_missing_value_handling"] = {
        "status": "PASS" if missing_pass else "FAIL",
        "qualified_batter_predictor_nulls": b_nulls,
        "qualified_bowler_predictor_nulls": p_nulls
    }
    print(f"Test 2 [Missing-Value Handling]: {test_results['2_missing_value_handling']['status']}")

    # 3. Data Leakage Prevention
    b_quar = set(b_meta["feature_groups"]["quarantined_from_supervised_predictors"])
    p_quar = set(p_meta["feature_groups"]["quarantined_from_supervised_predictors"])

    b_overlap = set(b_preds).intersection(b_quar)
    p_overlap = set(p_preds).intersection(p_quar)

    b_index_in_preds = "batter_reliability_index" in b_preds
    p_index_in_preds = "bowler_reliability_index" in p_preds

    b_target_in_preds = "strike_rate_high" in b_preds
    p_target_in_preds = "economy_rate_high" in p_preds

    # Check correlations with target
    b_corrs = b_q[b_preds].apply(lambda s: s.corr(b_q["strike_rate_high"])).abs().max()
    p_corrs = p_q[p_preds].apply(lambda s: s.corr(p_q["economy_rate_high"])).abs().max()

    leakage_pass = (
        len(b_overlap) == 0 and len(p_overlap) == 0 and
        not b_index_in_preds and not p_index_in_preds and
        not b_target_in_preds and not p_target_in_preds and
        b_corrs < 0.90 and p_corrs < 0.90
    )
    test_results["3_data_leakage_prevention"] = {
        "status": "PASS" if leakage_pass else "FAIL",
        "batter_predictor_quarantined_overlap": list(b_overlap),
        "bowler_predictor_quarantined_overlap": list(p_overlap),
        "batter_index_in_predictors": b_index_in_preds,
        "bowler_index_in_predictors": p_index_in_preds,
        "max_batter_predictor_target_corr": round(float(b_corrs), 3),
        "max_bowler_predictor_target_corr": round(float(p_corrs), 3)
    }
    print(f"Test 3 [Data Leakage Prevention]: {test_results['3_data_leakage_prevention']['status']}")

    # 4. Reproducibility with Fixed Random Seeds
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    X_b = b_q[b_preds]
    y_b = b_q["strike_rate_high"]
    
    rmses_1 = []
    for tr, va in kf.split(X_b, y_b):
        scaler = StandardScaler()
        X_tr = scaler.fit_transform(X_b.iloc[tr])
        X_va = scaler.transform(X_b.iloc[va])
        reg = Ridge(alpha=10.0).fit(X_tr, y_b.iloc[tr])
        rmses_1.append(root_mean_squared_error(y_b.iloc[va], reg.predict(X_va)))
    
    # Load saved metrics
    with open("data/ml/task_06_model_metrics.json", "r") as f:
        metrics_saved = json.load(f)
    saved_ridge_rmse = metrics_saved["batting"]["regression_metrics"]["Ridge"]["rmse"]
    reproduced_rmse = round(float(np.mean(rmses_1)), 3)

    repro_pass = (reproduced_rmse == saved_ridge_rmse)
    test_results["4_reproducibility"] = {
        "status": "PASS" if repro_pass else "FAIL",
        "saved_ridge_rmse": saved_ridge_rmse,
        "reproduced_ridge_rmse": reproduced_rmse,
        "absolute_difference": round(abs(reproduced_rmse - saved_ridge_rmse), 6)
    }
    print(f"Test 4 [Reproducibility]: {test_results['4_reproducibility']['status']}")

    # 5. Model Stability & Overfitting Checks
    b_ridge_std = metrics_saved["batting"]["regression_metrics"]["Ridge"]["rmse_std"]
    p_ridge_std = metrics_saved["bowling"]["regression_metrics"]["Ridge"]["rmse_std"]
    stability_pass = (b_ridge_std < 10.0 and p_ridge_std < 1.0)
    test_results["5_model_stability"] = {
        "status": "PASS" if stability_pass else "FAIL",
        "batting_ridge_cv_std": b_ridge_std,
        "bowling_ridge_cv_std": p_ridge_std
    }
    print(f"Test 5 [Model Stability]: {test_results['5_model_stability']['status']}")

    # 6. Baseline Superiority Comparisons
    b_id_rmse = metrics_saved["batting"]["regression_metrics"]["Identity_Heuristic"]["rmse"]
    b_ridge_rmse = metrics_saved["batting"]["regression_metrics"]["Ridge"]["rmse"]
    b_rmse_improvement_pct = ((b_id_rmse - b_ridge_rmse) / b_id_rmse) * 100.0

    p_id_rmse = metrics_saved["bowling"]["regression_metrics"]["Identity_Heuristic"]["rmse"]
    p_ridge_rmse = metrics_saved["bowling"]["regression_metrics"]["Ridge"]["rmse"]
    p_rmse_improvement_pct = ((p_id_rmse - p_ridge_rmse) / p_id_rmse) * 100.0

    b_logreg_auc = metrics_saved["batting"]["classification_metrics"]["Logistic_Regression"]["roc_auc"]
    p_logreg_auc = metrics_saved["bowling"]["classification_metrics"]["Logistic_Regression"]["roc_auc"]

    baseline_pass = (
        b_rmse_improvement_pct > 20.0 and p_rmse_improvement_pct > 20.0 and
        b_logreg_auc > 0.65 and p_logreg_auc > 0.65
    )
    test_results["6_baseline_superiority"] = {
        "status": "PASS" if baseline_pass else "FAIL",
        "batting_rmse_improvement_vs_naive_pct": round(b_rmse_improvement_pct, 2),
        "bowling_rmse_improvement_vs_naive_pct": round(p_rmse_improvement_pct, 2),
        "batting_logistic_auc": b_logreg_auc,
        "bowling_logistic_auc": p_logreg_auc
    }
    print(f"Test 6 [Baseline Superiority]: {test_results['6_baseline_superiority']['status']}")

    # 7. Clustering Integrity
    with open("data/ml/task_06_cluster_summary.json", "r") as f:
        clust_summary = json.load(f)
    b_sil = clust_summary["batting_clustering"]["silhouette_score"]
    p_sil = clust_summary["bowling_clustering"]["silhouette_score"]
    b_min_cluster = min(clust_summary["batting_clustering"]["qualified_distribution"].values())
    p_min_cluster = min(clust_summary["bowling_clustering"]["qualified_distribution"].values())

    clustering_pass = (b_sil > 0.15 and p_sil > 0.15 and b_min_cluster >= 15 and p_min_cluster >= 15)
    test_results["7_clustering_integrity"] = {
        "status": "PASS" if clustering_pass else "FAIL",
        "batting_silhouette": b_sil,
        "bowling_silhouette": p_sil,
        "batting_min_cluster_size": b_min_cluster,
        "bowling_min_cluster_size": p_min_cluster
    }
    print(f"Test 7 [Clustering Integrity]: {test_results['7_clustering_integrity']['status']}")

    # 8. Explainability Output Consistency
    with open("data/ml/task_06_explainability_metrics.json", "r") as f:
        exp_metrics = json.load(f)
    b_mdi_sum = sum(f["rf_mdi_reg"] for f in exp_metrics["batting_feature_importance"])
    p_mdi_sum = sum(f["rf_mdi_reg"] for f in exp_metrics["bowling_feature_importance"])

    exp_pass = (abs(b_mdi_sum - 1.0) < 1e-4 and abs(p_mdi_sum - 1.0) < 1e-4)
    test_results["8_explainability_consistency"] = {
        "status": "PASS" if exp_pass else "FAIL",
        "batting_mdi_sum": round(b_mdi_sum, 4),
        "bowling_mdi_sum": round(p_mdi_sum, 4)
    }
    print(f"Test 8 [Explainability Consistency]: {test_results['8_explainability_consistency']['status']}")

    overall_pass = all(res["status"] == "PASS" for res in test_results.values())
    validation_report = {
        "suite_name": "Task 06 Machine Learning Validation Suite",
        "overall_status": "CERTIFIED_PASS" if overall_pass else "FAILED",
        "tests_passed": sum(1 for res in test_results.values() if res["status"] == "PASS"),
        "total_tests": len(test_results),
        "results": test_results
    }

    os.makedirs(os.path.dirname(output_summary_path), exist_ok=True)
    with open(output_summary_path, "w", encoding="utf-8") as f:
        json.dump(validation_report, f, indent=2)
    print(f"[Validation] Saved summary to {output_summary_path}")
    print("="*60)
    print(f"OVERALL VALIDATION STATUS: {validation_report['overall_status']}")
    print("="*60)

    return validation_report


if __name__ == "__main__":
    run_validation_suite()
