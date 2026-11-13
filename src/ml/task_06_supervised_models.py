"""
Task 06 Supervised Machine Learning Pipeline
Rajasthan Royals SupeRR Selector Season 2 Hackathon

Trains and evaluates supervised regression and classification models to predict
high-pressure performance from baseline pre-pressure characteristics.

Separates Batting and Bowling into completely independent pipelines.
Strictly avoids data leakage:
- No reliability indices or composite z-scores in predictor sets.
- No differential metrics in predictor sets.
- 5-Fold Cross Validation with fixed random state (seed 42).
- Comparison against Dummy Mean/Prior and Identity Heuristic baselines.
"""

import os
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import KFold, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, RandomForestClassifier, GradientBoostingClassifier
from sklearn.dummy import DummyRegressor, DummyClassifier
from sklearn.metrics import (
    root_mean_squared_error, mean_absolute_error, r2_score,
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
)


def train_evaluate_regression(
    X: pd.DataFrame,
    y: pd.Series,
    y_normal: pd.Series,
    cv_splits: int = 5,
    random_state: int = 42
) -> tuple[dict, pd.DataFrame]:
    """
    Evaluates regression models using K-Fold Cross Validation.
    Returns metrics dict and out-of-fold predictions DataFrame.
    """
    kf = KFold(n_splits=cv_splits, shuffle=True, random_state=random_state)
    
    # Baseline: Identity Heuristic (predicting normal condition metric)
    rmse_id = float(root_mean_squared_error(y, y_normal))
    mae_id = float(mean_absolute_error(y, y_normal))
    r2_id = float(r2_score(y, y_normal))
    corr_id = float(np.corrcoef(y, y_normal)[0, 1])

    models = {
        "Dummy_Mean": DummyRegressor(strategy="mean"),
        "Ridge": Ridge(alpha=10.0),
        "Random_Forest": RandomForestRegressor(n_estimators=100, max_depth=4, min_samples_leaf=3, random_state=random_state),
        "Gradient_Boosting": GradientBoostingRegressor(n_estimators=100, learning_rate=0.05, max_depth=3, min_samples_leaf=3, random_state=random_state)
    }

    oof_preds = {name: np.zeros(len(y)) for name in models}
    metrics = {
        "Identity_Heuristic": {
            "rmse": round(rmse_id, 3),
            "mae": round(mae_id, 3),
            "r2": round(r2_id, 3),
            "pearson_r": round(corr_id, 3)
        }
    }

    for name, model in models.items():
        fold_rmses, fold_maes, fold_r2s = [], [], []
        
        for train_idx, val_idx in kf.split(X, y):
            X_tr, y_tr = X.iloc[train_idx], y.iloc[train_idx]
            X_va, y_va = X.iloc[val_idx], y.iloc[val_idx]
            
            if name == "Ridge":
                scaler = StandardScaler()
                X_tr = scaler.fit_transform(X_tr)
                X_va = scaler.transform(X_va)
                model.fit(X_tr, y_tr)
                preds = model.predict(X_va)
            else:
                model.fit(X_tr, y_tr)
                preds = model.predict(X_va)
            
            oof_preds[name][val_idx] = preds
            fold_rmses.append(root_mean_squared_error(y_va, preds))
            fold_maes.append(mean_absolute_error(y_va, preds))
            fold_r2s.append(r2_score(y_va, preds))
        
        corr = float(np.corrcoef(y, oof_preds[name])[0, 1])
        metrics[name] = {
            "rmse": round(float(np.mean(fold_rmses)), 3),
            "rmse_std": round(float(np.std(fold_rmses)), 3),
            "mae": round(float(np.mean(fold_maes)), 3),
            "mae_std": round(float(np.std(fold_maes)), 3),
            "r2": round(float(np.mean(fold_r2s)), 3),
            "r2_std": round(float(np.std(fold_r2s)), 3),
            "pearson_r": round(corr, 3)
        }

    oof_df = pd.DataFrame(oof_preds, index=X.index)
    oof_df["actual"] = y
    oof_df["identity_baseline"] = y_normal

    return metrics, oof_df


def train_evaluate_classification(
    X: pd.DataFrame,
    y: pd.Series,
    cv_splits: int = 5,
    random_state: int = 42
) -> tuple[dict, pd.DataFrame]:
    """
    Evaluates classification models using Stratified K-Fold Cross Validation.
    Returns metrics dict and out-of-fold probability predictions DataFrame.
    """
    skf = StratifiedKFold(n_splits=cv_splits, shuffle=True, random_state=random_state)

    models = {
        "Dummy_Prior": DummyClassifier(strategy="prior"),
        "Logistic_Regression": LogisticRegression(C=0.5, max_iter=1000, random_state=random_state),
        "Random_Forest": RandomForestClassifier(n_estimators=100, max_depth=3, min_samples_leaf=3, random_state=random_state),
        "Gradient_Boosting": GradientBoostingClassifier(n_estimators=100, learning_rate=0.03, max_depth=2, min_samples_leaf=4, random_state=random_state)
    }

    oof_probs = {name: np.zeros(len(y)) for name in models}
    oof_preds = {name: np.zeros(len(y), dtype=int) for name in models}
    metrics = {}

    for name, model in models.items():
        fold_accs, fold_precs, fold_recalls, fold_f1s, fold_aucs = [], [], [], [], []
        
        for train_idx, val_idx in skf.split(X, y):
            X_tr, y_tr = X.iloc[train_idx], y.iloc[train_idx]
            X_va, y_va = X.iloc[val_idx], y.iloc[val_idx]
            
            if name == "Logistic_Regression":
                scaler = StandardScaler()
                X_tr = scaler.fit_transform(X_tr)
                X_va = scaler.transform(X_va)
                model.fit(X_tr, y_tr)
                probs = model.predict_proba(X_va)[:, 1]
                preds = model.predict(X_va)
            else:
                model.fit(X_tr, y_tr)
                probs = model.predict_proba(X_va)[:, 1]
                preds = model.predict(X_va)
            
            oof_probs[name][val_idx] = probs
            oof_preds[name][val_idx] = preds
            
            fold_accs.append(accuracy_score(y_va, preds))
            fold_precs.append(precision_score(y_va, preds, zero_division=0))
            fold_recalls.append(recall_score(y_va, preds, zero_division=0))
            fold_f1s.append(f1_score(y_va, preds, zero_division=0))
            fold_aucs.append(roc_auc_score(y_va, probs))
        
        metrics[name] = {
            "accuracy": round(float(np.mean(fold_accs)), 3),
            "precision": round(float(np.mean(fold_precs)), 3),
            "recall": round(float(np.mean(fold_recalls)), 3),
            "f1": round(float(np.mean(fold_f1s)), 3),
            "roc_auc": round(float(np.mean(fold_aucs)), 3)
        }

    oof_df = pd.DataFrame({f"{name}_prob": oof_probs[name] for name in models}, index=X.index)
    for name in models:
        oof_df[f"{name}_pred"] = oof_preds[name]
    oof_df["actual"] = y

    return metrics, oof_df


def run_supervised_pipeline():
    """
    Executes supervised training and evaluation for both Batting and Bowling cohorts.
    """
    print("="*60)
    print("STARTING TASK 06 SUPERVISED MACHINE LEARNING PIPELINE")
    print("="*60)

    # 1. Load Batting Data
    b_df = pd.read_csv("data/ml/task_06_batter_features.csv")
    with open("data/ml/task_06_batter_feature_metadata.json", "r") as f:
        b_meta = json.load(f)

    b_q = b_df[b_df["eligibility_tier"] == "Qualified"].copy()
    b_preds = b_meta["feature_groups"]["supervised_predictors"]
    X_b = b_q[b_preds]
    y_b_reg = b_q["strike_rate_high"]
    y_b_norm = b_q["strike_rate_normal"]
    y_b_clf = b_q["target_above_median_sr_high"].astype(int)

    print(f"\n[Batting] Training Cohort: N = {len(b_q)} Qualified Batters")
    print(f"[Batting] Predictor Count: {len(b_preds)} baseline features")

    b_reg_metrics, b_reg_oof = train_evaluate_regression(X_b, y_b_reg, y_b_norm)
    b_clf_metrics, b_clf_oof = train_evaluate_classification(X_b, y_b_clf)

    # Merge batting predictions
    b_pred_full = b_q[["striker_id", "striker_name", "batting_type", "batter_reliability_index", "reliability_grade"]].copy()
    b_pred_full["actual_strike_rate_high"] = y_b_reg
    b_pred_full["baseline_strike_rate_normal"] = y_b_norm
    b_pred_full["pred_strike_rate_high_ridge"] = b_reg_oof["Ridge"]
    b_pred_full["pred_strike_rate_high_rf"] = b_reg_oof["Random_Forest"]
    b_pred_full["pred_prob_above_median_logreg"] = b_clf_oof["Logistic_Regression_prob"]
    b_pred_full["pred_prob_above_median_rf"] = b_clf_oof["Random_Forest_prob"]
    b_pred_full["residual_ridge"] = b_pred_full["actual_strike_rate_high"] - b_pred_full["pred_strike_rate_high_ridge"]

    b_pred_full.to_csv("data/ml/task_06_batter_predictions.csv", index=False)
    print(f"[Batting] Saved predictions to data/ml/task_06_batter_predictions.csv")

    # 2. Load Bowling Data
    p_df = pd.read_csv("data/ml/task_06_bowler_features.csv")
    with open("data/ml/task_06_bowler_feature_metadata.json", "r") as f:
        p_meta = json.load(f)

    p_q = p_df[p_df["eligibility_tier"] == "Qualified"].copy()
    p_preds = p_meta["feature_groups"]["supervised_predictors"]
    X_p = p_q[p_preds]
    y_p_reg = p_q["economy_rate_high"]
    y_p_norm = p_q["economy_rate_normal"]
    y_p_clf = p_q["target_below_median_econ_high"].astype(int)

    print(f"\n[Bowling] Training Cohort: N = {len(p_q)} Qualified Bowlers")
    print(f"[Bowling] Predictor Count: {len(p_preds)} baseline features")

    p_reg_metrics, p_reg_oof = train_evaluate_regression(X_p, y_p_reg, y_p_norm)
    p_clf_metrics, p_clf_oof = train_evaluate_classification(X_p, y_p_clf)

    # Merge bowling predictions
    p_pred_full = p_q[["bowler_id", "bowler_name", "bowling_type", "pace_or_spin", "bowler_reliability_index", "reliability_grade"]].copy()
    p_pred_full["actual_economy_rate_high"] = y_p_reg
    p_pred_full["baseline_economy_rate_normal"] = y_p_norm
    p_pred_full["pred_economy_rate_high_ridge"] = p_reg_oof["Ridge"]
    p_pred_full["pred_economy_rate_high_rf"] = p_reg_oof["Random_Forest"]
    p_pred_full["pred_prob_below_median_logreg"] = p_clf_oof["Logistic_Regression_prob"]
    p_pred_full["pred_prob_below_median_rf"] = p_clf_oof["Random_Forest_prob"]
    p_pred_full["residual_ridge"] = p_pred_full["actual_economy_rate_high"] - p_pred_full["pred_economy_rate_high_ridge"]

    p_pred_full.to_csv("data/ml/task_06_bowler_predictions.csv", index=False)
    print(f"[Bowling] Saved predictions to data/ml/task_06_bowler_predictions.csv")

    # Combine all metrics
    all_metrics = {
        "batting": {
            "sample_size": len(b_q),
            "regression_target": "strike_rate_high",
            "regression_metrics": b_reg_metrics,
            "classification_target": "target_above_median_sr_high",
            "classification_metrics": b_clf_metrics
        },
        "bowling": {
            "sample_size": len(p_q),
            "regression_target": "economy_rate_high",
            "regression_metrics": p_reg_metrics,
            "classification_target": "target_below_median_econ_high",
            "classification_metrics": p_clf_metrics
        }
    }

    with open("data/ml/task_06_model_metrics.json", "w", encoding="utf-8") as f:
        json.dump(all_metrics, f, indent=2)
    print(f"[Metrics] Saved all evaluation metrics to data/ml/task_06_model_metrics.json")
    print("="*60)
    print("TASK 06 SUPERVISED PIPELINE COMPLETE")
    print("="*60)


if __name__ == "__main__":
    run_supervised_pipeline()

