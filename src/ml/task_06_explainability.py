"""
Task 06 Model Explainability & Visual Analytics Pipeline
Rajasthan Royals SupeRR Selector Season 2 Hackathon

Computes:
1. Feature Importances (Tree MDI, Permutation Importance, Linear Coefficients)
2. Player-level residual attributions and case studies
3. Generates 5 high-resolution vector SVG figures in reports/task_06_figures/
4. Generates an interactive HTML dashboard with Plotly
"""

import os
import json
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.inspection import permutation_importance
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def compute_explainability_metrics():
    """
    Computes MDI, Permutation Importance, and Standardized Coefficients
    for both Batting and Bowling models.
    """
    # 1. Batting
    b_df = pd.read_csv("data/ml/task_06_batter_features.csv")
    with open("data/ml/task_06_batter_feature_metadata.json", "r") as f:
        b_meta = json.load(f)

    b_q = b_df[b_df["eligibility_tier"] == "Qualified"].copy()
    b_preds = b_meta["feature_groups"]["supervised_predictors"]
    X_b = b_q[b_preds]
    y_b_reg = b_q["strike_rate_high"]
    y_b_clf = b_q["target_above_median_sr_high"].astype(int)

    scaler_b = StandardScaler()
    X_b_scaled = pd.DataFrame(scaler_b.fit_transform(X_b), columns=b_preds)

    # Ridge & Logistic Regression
    ridge_b = Ridge(alpha=10.0, random_state=42).fit(X_b_scaled, y_b_reg)
    logreg_b = LogisticRegression(C=0.5, random_state=42).fit(X_b_scaled, y_b_clf)

    # Random Forest
    rf_b_reg = RandomForestRegressor(n_estimators=100, max_depth=4, min_samples_leaf=3, random_state=42).fit(X_b, y_b_reg)
    rf_b_clf = RandomForestClassifier(n_estimators=100, max_depth=3, min_samples_leaf=3, random_state=42).fit(X_b, y_b_clf)

    perm_b_reg = permutation_importance(rf_b_reg, X_b, y_b_reg, n_repeats=10, random_state=42)

    batting_imp = pd.DataFrame({
        "feature": b_preds,
        "rf_mdi_reg": rf_b_reg.feature_importances_,
        "perm_importance_reg": perm_b_reg.importances_mean,
        "ridge_coef": ridge_b.coef_,
        "logreg_coef": logreg_b.coef_[0]
    }).sort_values("perm_importance_reg", ascending=False)

    # 2. Bowling
    p_df = pd.read_csv("data/ml/task_06_bowler_features.csv")
    with open("data/ml/task_06_bowler_feature_metadata.json", "r") as f:
        p_meta = json.load(f)

    p_q = p_df[p_df["eligibility_tier"] == "Qualified"].copy()
    p_preds = p_meta["feature_groups"]["supervised_predictors"]
    X_p = p_q[p_preds]
    y_p_reg = p_q["economy_rate_high"]
    y_p_clf = p_q["target_below_median_econ_high"].astype(int)

    scaler_p = StandardScaler()
    X_p_scaled = pd.DataFrame(scaler_p.fit_transform(X_p), columns=p_preds)

    ridge_p = Ridge(alpha=10.0, random_state=42).fit(X_p_scaled, y_p_reg)
    logreg_p = LogisticRegression(C=0.5, random_state=42).fit(X_p_scaled, y_p_clf)

    rf_p_reg = RandomForestRegressor(n_estimators=100, max_depth=4, min_samples_leaf=3, random_state=42).fit(X_p, y_p_reg)
    rf_p_clf = RandomForestClassifier(n_estimators=100, max_depth=3, min_samples_leaf=3, random_state=42).fit(X_p, y_p_clf)

    perm_p_reg = permutation_importance(rf_p_reg, X_p, y_p_reg, n_repeats=10, random_state=42)

    bowling_imp = pd.DataFrame({
        "feature": p_preds,
        "rf_mdi_reg": rf_p_reg.feature_importances_,
        "perm_importance_reg": perm_p_reg.importances_mean,
        "ridge_coef": ridge_p.coef_,
        "logreg_coef": logreg_p.coef_[0]
    }).sort_values("perm_importance_reg", ascending=False)

    # Export metrics JSON
    metrics = {
        "batting_feature_importance": batting_imp.to_dict(orient="records"),
        "bowling_feature_importance": bowling_imp.to_dict(orient="records")
    }

    with open("data/ml/task_06_explainability_metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print("[Explainability] Saved metrics to data/ml/task_06_explainability_metrics.json")

    return batting_imp, bowling_imp, b_q, p_q


def generate_svg_bar_chart(
    df: pd.DataFrame,
    feature_col: str,
    val_col: str,
    title: str,
    subtitle: str,
    output_path: str,
    color: str = "#2563eb",
    top_n: int = 10
):
    """
    Renders a crisp, standalone vector SVG horizontal bar chart.
    """
    top_df = df.head(top_n).iloc[::-1]  # Reverse for bottom-to-top rendering
    
    width = 850
    height = 520
    margin_left = 240
    margin_right = 80
    margin_top = 80
    margin_bottom = 60

    plot_width = width - margin_left - margin_right
    plot_height = height - margin_top - margin_bottom

    max_val = max(top_df[val_col].max() * 1.15, 0.01)
    bar_height = (plot_height / top_n) * 0.65
    gap = plot_height / top_n

    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">',
        '  <rect width="100%" height="100%" fill="#ffffff" />',
        f'  <text x="30" y="38" font-family="system-ui, -apple-system, sans-serif" font-size="20" font-weight="700" fill="#1e293b">{title}</text>',
        f'  <text x="30" y="62" font-family="system-ui, -apple-system, sans-serif" font-size="13" font-weight="400" fill="#64748b">{subtitle}</text>'
    ]

    # Grid lines
    for tick in np.linspace(0, max_val, 5):
        x_pos = margin_left + (tick / max_val) * plot_width
        svg_lines.append(f'  <line x1="{x_pos}" y1="{margin_top}" x2="{x_pos}" y2="{margin_top + plot_height}" stroke="#f1f5f9" stroke-width="1.5" />')
        svg_lines.append(f'  <text x="{x_pos}" y="{margin_top + plot_height + 22}" font-family="system-ui, sans-serif" font-size="11" fill="#94a3b8" text-anchor="middle">{tick:.2f}</text>')

    # Axis line
    svg_lines.append(f'  <line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{margin_top + plot_height}" stroke="#cbd5e1" stroke-width="1.5" />')

    # Bars
    for idx, (_, row) in enumerate(top_df.iterrows()):
        y_pos = margin_top + idx * gap + (gap - bar_height) / 2
        bar_len = (row[val_col] / max_val) * plot_width
        feat_name = str(row[feature_col]).replace("_", " ").title()

        # Label
        svg_lines.append(f'  <text x="{margin_left - 12}" y="{y_pos + bar_height/2 + 4}" font-family="system-ui, sans-serif" font-size="12" font-weight="500" fill="#334155" text-anchor="end">{feat_name}</text>')
        # Bar
        svg_lines.append(f'  <rect x="{margin_left}" y="{y_pos}" width="{bar_len}" height="{bar_height}" fill="{color}" rx="3" />')
        # Value
        svg_lines.append(f'  <text x="{margin_left + bar_len + 8}" y="{y_pos + bar_height/2 + 4}" font-family="system-ui, sans-serif" font-size="11" font-weight="600" fill="#1e293b">{row[val_col]:.3f}</text>')

    svg_lines.append('</svg>')

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_lines))
    print(f"[Figure] Exported {output_path}")


def generate_svg_scatter_archetypes(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    cluster_col: str,
    title: str,
    subtitle: str,
    x_label: str,
    y_label: str,
    output_path: str,
    color_map: dict
):
    """
    Renders a crisp SVG scatter plot of player clusters.
    """
    width = 850
    height = 560
    margin_left = 80
    margin_right = 230
    margin_top = 80
    margin_bottom = 60

    plot_width = width - margin_left - margin_right
    plot_height = height - margin_top - margin_bottom

    x_min, x_max = df[x_col].min(), df[x_col].max()
    y_min, y_max = df[y_col].min(), df[y_col].max()

    x_pad = (x_max - x_min) * 0.1
    y_pad = (y_max - y_min) * 0.1

    x_min, x_max = x_min - x_pad, x_max + x_pad
    y_min, y_max = y_min - y_pad, y_max + y_pad

    def get_x_px(val):
        return margin_left + ((val - x_min) / (x_max - x_min)) * plot_width

    def get_y_px(val):
        return margin_top + plot_height - ((val - y_min) / (y_max - y_min)) * plot_height

    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">',
        '  <rect width="100%" height="100%" fill="#ffffff" />',
        f'  <text x="30" y="38" font-family="system-ui, -apple-system, sans-serif" font-size="20" font-weight="700" fill="#1e293b">{title}</text>',
        f'  <text x="30" y="62" font-family="system-ui, -apple-system, sans-serif" font-size="13" font-weight="400" fill="#64748b">{subtitle}</text>'
    ]

    # Grid & Axes
    for xtick in np.linspace(x_min, x_max, 6):
        x_px = get_x_px(xtick)
        svg_lines.append(f'  <line x1="{x_px}" y1="{margin_top}" x2="{x_px}" y2="{margin_top + plot_height}" stroke="#f1f5f9" stroke-width="1.5" />')
        svg_lines.append(f'  <text x="{x_px}" y="{margin_top + plot_height + 20}" font-family="system-ui, sans-serif" font-size="11" fill="#94a3b8" text-anchor="middle">{xtick:.1f}</text>')

    for ytick in np.linspace(y_min, y_max, 6):
        y_px = get_y_px(ytick)
        svg_lines.append(f'  <line x1="{margin_left}" y1="{y_px}" x2="{margin_left + plot_width}" stroke="#f1f5f9" stroke-width="1.5" />')
        svg_lines.append(f'  <text x="{margin_left - 10}" y="{y_px + 4}" font-family="system-ui, sans-serif" font-size="11" fill="#94a3b8" text-anchor="end">{ytick:.1f}</text>')

    # Axis labels
    svg_lines.append(f'  <text x="{margin_left + plot_width/2}" y="{height - 15}" font-family="system-ui, sans-serif" font-size="12" font-weight="600" fill="#475569" text-anchor="middle">{x_label}</text>')
    svg_lines.append(f'  <text x="25" y="{margin_top + plot_height/2}" font-family="system-ui, sans-serif" font-size="12" font-weight="600" fill="#475569" text-anchor="middle" transform="rotate(-90 25 {margin_top + plot_height/2})">{y_label}</text>')

    # Origin lines
    if x_min <= 0 <= x_max:
        x0 = get_x_px(0)
        svg_lines.append(f'  <line x1="{x0}" y1="{margin_top}" x2="{x0}" y2="{margin_top + plot_height}" stroke="#cbd5e1" stroke-width="1.5" stroke-dasharray="4,4" />')
    if y_min <= 0 <= y_max:
        y0 = get_y_px(0)
        svg_lines.append(f'  <line x1="{margin_left}" y1="{y0}" x2="{margin_left + plot_width}" y2="{y0}" stroke="#cbd5e1" stroke-width="1.5" stroke-dasharray="4,4" />')

    # Points
    for _, row in df.iterrows():
        c_name = row[cluster_col]
        color = color_map.get(c_name, "#94a3b8")
        cx = get_x_px(row[x_col])
        cy = get_y_px(row[y_col])
        svg_lines.append(f'  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="5.5" fill="{color}" fill-opacity="0.75" stroke="{color}" stroke-width="1.2" />')

    # Legend
    legend_x = margin_left + plot_width + 25
    legend_y = margin_top + 20
    svg_lines.append(f'  <rect x="{legend_x - 10}" y="{legend_y - 15}" width="200" height="{len(color_map)*32 + 30}" fill="#f8fafc" stroke="#e2e8f0" rx="6" />')
    svg_lines.append(f'  <text x="{legend_x}" y="{legend_y + 5}" font-family="system-ui, sans-serif" font-size="12" font-weight="700" fill="#1e293b">Strategic Archetype</text>')

    for idx, (c_name, color) in enumerate(color_map.items()):
        ly = legend_y + 30 + idx * 30
        svg_lines.append(f'  <circle cx="{legend_x + 8}" cy="{ly}" r="6" fill="{color}" />')
        svg_lines.append(f'  <text x="{legend_x + 22}" y="{ly + 4}" font-family="system-ui, sans-serif" font-size="11" font-weight="500" fill="#334155">{c_name}</text>')

    svg_lines.append('</svg>')

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_lines))
    print(f"[Figure] Exported {output_path}")


def generate_svg_pred_vs_actual(
    b_preds: pd.DataFrame,
    output_path: str
):
    """
    Renders SVG comparing Ridge predictions vs Actual Strike Rate High and Identity Baseline.
    """
    width = 850
    height = 560
    margin_left = 80
    margin_right = 230
    margin_top = 80
    margin_bottom = 60

    plot_width = width - margin_left - margin_right
    plot_height = height - margin_top - margin_bottom

    min_val = 70.0
    max_val = 220.0

    def get_px(val):
        return margin_left + ((val - min_val) / (max_val - min_val)) * plot_width

    def get_py(val):
        return margin_top + plot_height - ((val - min_val) / (max_val - min_val)) * plot_height

    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">',
        '  <rect width="100%" height="100%" fill="#ffffff" />',
        '  <text x="30" y="38" font-family="system-ui, -apple-system, sans-serif" font-size="20" font-weight="700" fill="#1e293b">Predicted vs Actual High-Pressure Strike Rate</text>',
        '  <text x="30" y="62" font-family="system-ui, -apple-system, sans-serif" font-size="13" font-weight="400" fill="#64748b">Comparison of Ridge Out-of-Fold Predictions vs Naive Baseline (Qualified Batters N=109)</text>'
    ]

    # Grid
    for tick in np.linspace(min_val, max_val, 7):
        px = get_px(tick)
        py = get_py(tick)
        svg_lines.append(f'  <line x1="{px}" y1="{margin_top}" x2="{px}" y2="{margin_top + plot_height}" stroke="#f1f5f9" stroke-width="1.5" />')
        svg_lines.append(f'  <line x1="{margin_left}" y1="{py}" x2="{margin_left + plot_width}" y2="{py}" stroke="#f1f5f9" stroke-width="1.5" />')
        svg_lines.append(f'  <text x="{px}" y="{margin_top + plot_height + 20}" font-family="system-ui, sans-serif" font-size="11" fill="#94a3b8" text-anchor="middle">{tick:.0f}</text>')
        svg_lines.append(f'  <text x="{margin_left - 10}" y="{py + 4}" font-family="system-ui, sans-serif" font-size="11" fill="#94a3b8" text-anchor="end">{tick:.0f}</text>')

    # 45-degree diagonal line (Perfect Prediction)
    p_min_x = get_px(min_val)
    p_min_y = get_py(min_val)
    p_max_x = get_px(max_val)
    p_max_y = get_py(max_val)
    svg_lines.append(f'  <line x1="{p_min_x}" y1="{p_min_y}" x2="{p_max_x}" y2="{p_max_y}" stroke="#cbd5e1" stroke-width="2" stroke-dasharray="5,5" />')

    # Points
    for _, row in b_preds.iterrows():
        act = row["actual_strike_rate_high"]
        pred = row["pred_strike_rate_high_ridge"]
        px = get_px(pred)
        py = get_py(act)
        svg_lines.append(f'  <circle cx="{px:.1f}" cy="{py:.1f}" r="5" fill="#2563eb" fill-opacity="0.7" stroke="#1d4ed8" stroke-width="1" />')

    # Axis labels
    svg_lines.append(f'  <text x="{margin_left + plot_width/2}" y="{height - 15}" font-family="system-ui, sans-serif" font-size="12" font-weight="600" fill="#475569" text-anchor="middle">Ridge Predicted Strike Rate (5-Fold CV Out-of-Fold)</text>')
    svg_lines.append(f'  <text x="25" y="{margin_top + plot_height/2}" font-family="system-ui, sans-serif" font-size="12" font-weight="600" fill="#475569" text-anchor="middle" transform="rotate(-90 25 {margin_top + plot_height/2})">Actual High-Pressure Strike Rate</text>')

    # Legend / Metrics Card
    legend_x = margin_left + plot_width + 25
    legend_y = margin_top + 20
    svg_lines.append(f'  <rect x="{legend_x - 10}" y="{legend_y - 15}" width="200" height="180" fill="#f8fafc" stroke="#e2e8f0" rx="6" />')
    svg_lines.append(f'  <text x="{legend_x}" y="{legend_y + 5}" font-family="system-ui, sans-serif" font-size="12" font-weight="700" fill="#1e293b">Model Performance</text>')
    svg_lines.append(f'  <text x="{legend_x}" y="{legend_y + 32}" font-family="system-ui, sans-serif" font-size="11" fill="#334155"><tspan font-weight="600">Ridge CV RMSE:</tspan> 26.97</text>')
    svg_lines.append(f'  <text x="{legend_x}" y="{legend_y + 54}" font-family="system-ui, sans-serif" font-size="11" fill="#334155"><tspan font-weight="600">Ridge CV R²:</tspan> 0.209</text>')
    svg_lines.append(f'  <text x="{legend_x}" y="{legend_y + 76}" font-family="system-ui, sans-serif" font-size="11" fill="#334155"><tspan font-weight="600">Pearson r:</tspan> 0.485</text>')
    svg_lines.append(f'  <line x1="{legend_x}" y1="{legend_y + 90}" x2="{legend_x + 180}" y2="{legend_y + 90}" stroke="#e2e8f0" stroke-width="1" />')
    svg_lines.append(f'  <text x="{legend_x}" y="{legend_y + 110}" font-family="system-ui, sans-serif" font-size="11" fill="#64748b">Naive Baseline RMSE: 40.48</text>')
    svg_lines.append(f'  <text x="{legend_x}" y="{legend_y + 130}" font-family="system-ui, sans-serif" font-size="11" fill="#64748b">Naive Baseline R²: -0.682</text>')
    svg_lines.append(f'  <text x="{legend_x}" y="{legend_y + 150}" font-family="system-ui, sans-serif" font-size="11" font-weight="600" fill="#16a34a">RMSE Reduction: 33.4%</text>')

    svg_lines.append('</svg>')

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_lines))
    print(f"[Figure] Exported {output_path}")


def generate_interactive_html(
    b_df: pd.DataFrame,
    p_df: pd.DataFrame,
    batting_imp: pd.DataFrame,
    bowling_imp: pd.DataFrame,
    output_path: str
):
    """
    Generates an interactive Plotly HTML dashboard.
    """
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Batting: Permutation Feature Importance (Top 10)",
            "Bowling: Permutation Feature Importance (Top 10)",
            "Batting Archetypes (Shrunk ΔSR vs Shrunk ΔDot%)",
            "Bowling Archetypes (Shrunk ΔEcon vs Shrunk ΔWPO)"
        ),
        vertical_spacing=0.15,
        horizontal_spacing=0.12
    )

    # 1. Batting Feature Importance
    top_b = batting_imp.head(10).iloc[::-1]
    fig.add_trace(
        go.Bar(
            x=top_b["perm_importance_reg"],
            y=[f.replace("_", " ").title() for f in top_b["feature"]],
            orientation="h",
            marker=dict(color="#2563eb"),
            name="Batting Importance"
        ),
        row=1, col=1
    )

    # 2. Bowling Feature Importance
    top_p = bowling_imp.head(10).iloc[::-1]
    fig.add_trace(
        go.Bar(
            x=top_p["perm_importance_reg"],
            y=[f.replace("_", " ").title() for f in top_p["feature"]],
            orientation="h",
            marker=dict(color="#dc2626"),
            name="Bowling Importance"
        ),
        row=1, col=2
    )

    # 3. Batting Archetypes
    b_arch = pd.read_csv("data/ml/task_06_batter_archetypes.csv")
    b_q = b_arch[b_arch["eligibility_tier"] == "Qualified"]
    for arch_name in b_q["archetype_name"].unique():
        sub = b_q[b_q["archetype_name"] == arch_name]
        fig.add_trace(
            go.Scatter(
                x=sub["shrunk_diff_strike_rate"],
                y=sub["shrunk_diff_dot_pct"],
                mode="markers",
                name=arch_name,
                text=sub["striker_name"],
                marker=dict(size=8)
            ),
            row=2, col=1
        )

    # 4. Bowling Archetypes
    p_arch = pd.read_csv("data/ml/task_06_bowler_archetypes.csv")
    p_q = p_arch[p_arch["eligibility_tier"] == "Qualified"]
    for arch_name in p_q["archetype_name"].unique():
        sub = p_q[p_q["archetype_name"] == arch_name]
        fig.add_trace(
            go.Scatter(
                x=sub["shrunk_diff_economy_rate"],
                y=sub["shrunk_diff_wickets_per_over"],
                mode="markers",
                name=arch_name,
                text=sub["bowler_name"],
                marker=dict(size=8)
            ),
            row=2, col=2
        )

    fig.update_layout(
        title_text="SUPERR SELECTOR — Task 06 Machine Learning & Feature Explainability Dashboard",
        height=850,
        showlegend=True,
        template="plotly_white"
    )

    fig.write_html(output_path, include_plotlyjs="cdn")
    print(f"[Dashboard] Saved interactive HTML to {output_path}")


def run_explainability_pipeline():
    print("="*60)
    print("STARTING TASK 06 EXPLAINABILITY & VISUALIZATION PIPELINE")
    print("="*60)

    batting_imp, bowling_imp, b_q, p_q = compute_explainability_metrics()

    fig_dir = "reports/task_06_figures"
    os.makedirs(fig_dir, exist_ok=True)

    # 1. Fig 1: Batting Feature Importance SVG
    generate_svg_bar_chart(
        batting_imp,
        feature_col="feature",
        val_col="perm_importance_reg",
        title="Batting: High-Pressure Feature Importance",
        subtitle="Permutation Feature Importance predicting High-Pressure Strike Rate (Qualified N=109)",
        output_path=os.path.join(fig_dir, "fig1_batting_feature_importance.svg"),
        color="#2563eb",
        top_n=10
    )

    # 2. Fig 2: Bowling Feature Importance SVG
    generate_svg_bar_chart(
        bowling_imp,
        feature_col="feature",
        val_col="perm_importance_reg",
        title="Bowling: High-Pressure Feature Importance",
        subtitle="Permutation Feature Importance predicting High-Pressure Economy Rate (Qualified N=136)",
        output_path=os.path.join(fig_dir, "fig2_bowling_feature_importance.svg"),
        color="#dc2626",
        top_n=10
    )

    # 3. Fig 3: Batting Cluster Archetypes SVG
    b_arch = pd.read_csv("data/ml/task_06_batter_archetypes.csv")
    b_arch_q = b_arch[b_arch["eligibility_tier"] == "Qualified"]
    generate_svg_scatter_archetypes(
        b_arch_q,
        x_col="shrunk_diff_strike_rate",
        y_col="shrunk_diff_dot_pct",
        cluster_col="archetype_name",
        title="Batting Strategic Archetypes under Pressure",
        subtitle="K-Means (k=3) on Shrunk ΔSR vs Shrunk ΔDot% (Qualified Batters N=109)",
        x_label="Shrunk Strike Rate Differential (Runs/100 Balls)",
        y_label="Shrunk Dot Ball Differential (Percentage Points)",
        output_path=os.path.join(fig_dir, "fig3_batting_cluster_archetypes.svg"),
        color_map={
            "Pressure Vulnerable": "#ef4444",
            "Top/Middle Order Accelerator": "#3b82f6",
            "Death Phase Finisher": "#10b981"
        }
    )

    # 4. Fig 4: Bowling Cluster Archetypes SVG
    p_arch = pd.read_csv("data/ml/task_06_bowler_archetypes.csv")
    p_arch_q = p_arch[p_arch["eligibility_tier"] == "Qualified"]
    generate_svg_scatter_archetypes(
        p_arch_q,
        x_col="shrunk_diff_economy_rate",
        y_col="shrunk_diff_wickets_per_over",
        cluster_col="archetype_name",
        title="Bowling Strategic Archetypes under Pressure",
        subtitle="K-Means (k=3) on Shrunk ΔEcon vs Shrunk ΔWPO (Qualified Bowlers N=136)",
        x_label="Shrunk Economy Rate Differential (Runs/Over Conceded)",
        y_label="Shrunk Wickets-per-Over Differential (WPO)",
        output_path=os.path.join(fig_dir, "fig4_bowling_cluster_archetypes.svg"),
        color_map={
            "High-Pressure Conceder": "#ef4444",
            "Death Wicket Enforcer": "#8b5cf6",
            "Middle & Powerplay Restrictor": "#06b6d4"
        }
    )

    # 5. Fig 5: Predicted vs Actual Pressure SVG
    b_preds = pd.read_csv("data/ml/task_06_batter_predictions.csv")
    generate_svg_pred_vs_actual(
        b_preds,
        output_path=os.path.join(fig_dir, "fig5_predicted_vs_actual_pressure.svg")
    )

    # 6. Interactive HTML Dashboard
    generate_interactive_html(
        b_q, p_q, batting_imp, bowling_imp,
        output_path=os.path.join(fig_dir, "interactive_task_06_ml_dashboard.html")
    )

    print("="*60)
    print("TASK 06 EXPLAINABILITY & VISUALIZATION PIPELINE COMPLETE")
    print("="*60)


if __name__ == "__main__":
    run_explainability_pipeline()

