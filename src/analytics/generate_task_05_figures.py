"""
SUPERR SELECTOR - Master Task 05 Visualizations Engine
Generates publication-quality vector SVG charts and interactive Plotly visualization.
"""

import os
import sys
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FIGURES_DIR = os.path.join(ROOT_DIR, "reports", "task_05_figures")
os.makedirs(FIGURES_DIR, exist_ok=True)

BATTER_REL_PATH = os.path.join(ROOT_DIR, "data", "analytics", "task_05_batter_reliability.csv")
BOWLER_REL_PATH = os.path.join(ROOT_DIR, "data", "analytics", "task_05_bowler_reliability.csv")

bat = pd.read_csv(BATTER_REL_PATH)
bowl = pd.read_csv(BOWLER_REL_PATH)

qual_bat = bat[bat["eligibility_tier"] == "Qualified"].copy()
qual_bowl = bowl[bowl["eligibility_tier"] == "Qualified"].copy()


def save_svg(content: str, filename: str):
    path = os.path.join(FIGURES_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Saved: {path}")


# ==============================================================================
# Figure 1: Pressure vs Normal Performance (Scatter SVG)
# ==============================================================================
def generate_fig1_svg():
    w, h = 950, 480
    svg = [
        f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" style="background:#ffffff; font-family:system-ui, -apple-system, sans-serif;">',
        f'<text x="{w/2}" y="32" text-anchor="middle" font-size="18" font-weight="bold" fill="#1e293b">Figure 1: High Pressure vs Normal Pressure Performance (Qualified Players)</text>',
        f'<text x="{w/2}" y="52" text-anchor="middle" font-size="12" fill="#64748b">Comparison of Batting Strike Rate (Left) and Bowling Economy Rate (Right) against Parity Baselines</text>'
    ]

    # Panel 1: Batting SR (x: normal, y: high)
    # Range: [80, 240]
    p1_x, p1_y, p1_w, p1_h = 70, 80, 380, 330
    svg.append(f'<rect x="{p1_x}" y="{p1_y}" width="{p1_w}" height="{p1_h}" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1"/>')
    svg.append(f'<text x="{p1_x + p1_w/2}" y="{p1_y - 10}" text-anchor="middle" font-size="13" font-weight="600" fill="#0f172a">Batting Strike Rate (N = {len(qual_bat)})</text>')
    
    # Grid & Parity Line
    min_sr, max_sr = 70.0, 250.0
    def scale_sr_x(val): return p1_x + (val - min_sr) / (max_sr - min_sr) * p1_w
    def scale_sr_y(val): return p1_y + p1_h - (val - min_sr) / (max_sr - min_sr) * p1_h

    # Parity line
    svg.append(f'<line x1="{scale_sr_x(80)}" y1="{scale_sr_y(80)}" x2="{scale_sr_x(240)}" y2="{scale_sr_y(240)}" stroke="#94a3b8" stroke-dasharray="4,4" stroke-width="1.5"/>')
    svg.append(f'<text x="{scale_sr_x(230)}" y="{scale_sr_y(225)}" font-size="10" fill="#64748b">Parity</text>')

    for sr_tick in [100, 150, 200]:
        x_pos = scale_sr_x(sr_tick)
        y_pos = scale_sr_y(sr_tick)
        svg.append(f'<line x1="{x_pos}" y1="{p1_y}" x2="{x_pos}" y2="{p1_y + p1_h}" stroke="#e2e8f0" stroke-width="1"/>')
        svg.append(f'<line x1="{p1_x}" y1="{y_pos}" x2="{p1_x + p1_w}" y2="{y_pos}" stroke="#e2e8f0" stroke-width="1"/>')
        svg.append(f'<text x="{x_pos}" y="{p1_y + p1_h + 18}" text-anchor="middle" font-size="10" fill="#64748b">{sr_tick}</text>')
        svg.append(f'<text x="{p1_x - 10}" y="{y_pos + 4}" text-anchor="end" font-size="10" fill="#64748b">{sr_tick}</text>')

    # Dots
    for _, r in qual_bat.iterrows():
        cx = scale_sr_x(r["strike_rate_normal"])
        cy = scale_sr_y(r["strike_rate_high"])
        rad = max(3.0, min(8.0, np.sqrt(r["effective_balls"]) * 0.6))
        svg.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{rad:.1f}" fill="#2563eb" fill-opacity="0.6" stroke="#1d4ed8" stroke-width="1"/>')

    svg.append(f'<text x="{p1_x + p1_w/2}" y="{p1_y + p1_h + 38}" text-anchor="middle" font-size="11" font-weight="500" fill="#334155">Normal Pressure Strike Rate (P &lt; 40)</text>')
    svg.append(f'<text x="{p1_x - 38}" y="{p1_y + p1_h/2}" text-anchor="middle" transform="rotate(-90 {p1_x - 38} {p1_y + p1_h/2})" font-size="11" font-weight="500" fill="#334155">High Pressure Strike Rate (P &ge; 65)</text>')

    # Panel 2: Bowling Econ (x: normal, y: high)
    # Range: [4.0, 16.0]
    p2_x, p2_y, p2_w, p2_h = 510, 80, 380, 330
    svg.append(f'<rect x="{p2_x}" y="{p2_y}" width="{p2_w}" height="{p2_h}" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1"/>')
    svg.append(f'<text x="{p2_x + p2_w/2}" y="{p2_y - 10}" text-anchor="middle" font-size="13" font-weight="600" fill="#0f172a">Bowling Economy Rate (N = {len(qual_bowl)})</text>')

    min_ec, max_ec = 4.0, 16.0
    def scale_ec_x(val): return p2_x + (val - min_ec) / (max_ec - min_ec) * p2_w
    def scale_ec_y(val): return p2_y + p2_h - (val - min_ec) / (max_ec - min_ec) * p2_h

    # Parity line
    svg.append(f'<line x1="{scale_ec_x(5.0)}" y1="{scale_ec_y(5.0)}" x2="{scale_ec_x(15.0)}" y2="{scale_ec_y(15.0)}" stroke="#94a3b8" stroke-dasharray="4,4" stroke-width="1.5"/>')
    svg.append(f'<text x="{scale_ec_x(14.0)}" y="{scale_ec_y(13.5)}" font-size="10" fill="#64748b">Parity</text>')

    for ec_tick in [6.0, 9.0, 12.0, 15.0]:
        x_pos = scale_ec_x(ec_tick)
        y_pos = scale_ec_y(ec_tick)
        svg.append(f'<line x1="{x_pos}" y1="{p2_y}" x2="{x_pos}" y2="{p2_y + p2_h}" stroke="#e2e8f0" stroke-width="1"/>')
        svg.append(f'<line x1="{p2_x}" y1="{y_pos}" x2="{p2_x + p2_w}" y2="{y_pos}" stroke="#e2e8f0" stroke-width="1"/>')
        svg.append(f'<text x="{x_pos}" y="{p2_y + p2_h + 18}" text-anchor="middle" font-size="10" fill="#64748b">{ec_tick:.0f}</text>')
        svg.append(f'<text x="{p2_x - 10}" y="{y_pos + 4}" text-anchor="end" font-size="10" fill="#64748b">{ec_tick:.0f}</text>')

    # Dots
    for _, r in qual_bowl.iterrows():
        cx = scale_ec_x(r["economy_rate_normal"])
        cy = scale_ec_y(r["economy_rate_high"])
        rad = max(3.0, min(8.0, np.sqrt(r["effective_balls"]) * 0.6))
        svg.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{rad:.1f}" fill="#ea580c" fill-opacity="0.6" stroke="#c2410c" stroke-width="1"/>')

    svg.append(f'<text x="{p2_x + p2_w/2}" y="{p2_y + p2_h + 38}" text-anchor="middle" font-size="11" font-weight="500" fill="#334155">Normal Pressure Economy Rate (P &lt; 40)</text>')
    svg.append(f'<text x="{p2_x - 38}" y="{p2_y + p2_h/2}" text-anchor="middle" transform="rotate(-90 {p2_x - 38} {p2_y + p2_h/2})" font-size="11" font-weight="500" fill="#334155">High Pressure Economy Rate (P &ge; 65)</text>')

    svg.append(f'<text x="{w/2}" y="{h - 10}" text-anchor="middle" font-size="10" fill="#94a3b8">Note: Bubble size indicates harmonic effective sample size (credibility). Deliveries from standard cohort (innings &le; 2).</text>')
    svg.append('</svg>')
    save_svg("\n".join(svg), "fig1_pressure_vs_normal_performance.svg")


# ==============================================================================
# Figure 2: Sample Size & Eligibility Gate Distribution SVG
# ==============================================================================
def generate_fig2_svg():
    w, h = 950, 460
    svg = [
        f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" style="background:#ffffff; font-family:system-ui, -apple-system, sans-serif;">',
        f'<text x="{w/2}" y="32" text-anchor="middle" font-size="18" font-weight="bold" fill="#1e293b">Figure 2: Player Sample Size Distribution and Eligibility Threshold Gates</text>',
        f'<text x="{w/2}" y="52" text-anchor="middle" font-size="12" fill="#64748b">Distribution of High-Pressure Exposure showing Qualified (>=30 balls), Provisional (15-29), and Ineligible (&lt;15)</text>'
    ]

    p1_x, p1_y, p1_w, p1_h = 70, 80, 380, 310
    svg.append(f'<rect x="{p1_x}" y="{p1_y}" width="{p1_w}" height="{p1_h}" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1"/>')
    svg.append(f'<text x="{p1_x + p1_w/2}" y="{p1_y - 10}" text-anchor="middle" font-size="13" font-weight="600" fill="#0f172a">Batter High-Pressure Exposure (N = {len(bat)})</text>')

    # Bins for batters: 0-14 (inelig), 15-29 (prov), 30-59, 60-99, 100-149, 150+
    b_counts = [
        (bat["balls_faced_high"] < 15).sum(),
        ((bat["balls_faced_high"] >= 15) & (bat["balls_faced_high"] < 30)).sum(),
        ((bat["balls_faced_high"] >= 30) & (bat["balls_faced_high"] < 60)).sum(),
        ((bat["balls_faced_high"] >= 60) & (bat["balls_faced_high"] < 100)).sum(),
        ((bat["balls_faced_high"] >= 100) & (bat["balls_faced_high"] < 150)).sum(),
        (bat["balls_faced_high"] >= 150).sum(),
    ]
    labels = ["<15 (Inelig)", "15-29 (Prov)", "30-59", "60-99", "100-149", "150+"]
    colors = ["#cbd5e1", "#fdba74", "#38bdf8", "#0284c7", "#0369a1", "#075985"]

    bar_w = p1_w / len(b_counts) - 10
    max_c = 600.0
    for i, (cnt, lbl, col) in enumerate(zip(b_counts, labels, colors)):
        bx = p1_x + 5 + i * (p1_w / len(b_counts))
        bh = cnt / max_c * p1_h
        by = p1_y + p1_h - bh
        svg.append(f'<rect x="{bx}" y="{by}" width="{bar_w}" height="{bh}" fill="{col}" stroke="#64748b" stroke-width="1"/>')
        svg.append(f'<text x="{bx + bar_w/2}" y="{by - 6}" text-anchor="middle" font-size="11" font-weight="600" fill="#334155">{cnt}</text>')
        svg.append(f'<text x="{bx + bar_w/2}" y="{p1_y + p1_h + 18}" text-anchor="middle" font-size="9" fill="#475569">{lbl}</text>')

    # Panel 2: Bowlers
    p2_x, p2_y, p2_w, p2_h = 510, 80, 380, 310
    svg.append(f'<rect x="{p2_x}" y="{p2_y}" width="{p2_w}" height="{p2_h}" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1"/>')
    svg.append(f'<text x="{p2_x + p2_w/2}" y="{p2_y - 10}" text-anchor="middle" font-size="13" font-weight="600" fill="#0f172a">Bowler High-Pressure Exposure (N = {len(bowl)})</text>')

    bw_counts = [
        (bowl["legal_balls_high"] < 15).sum(),
        ((bowl["legal_balls_high"] >= 15) & (bowl["legal_balls_high"] < 30)).sum(),
        ((bowl["legal_balls_high"] >= 30) & (bowl["legal_balls_high"] < 60)).sum(),
        ((bowl["legal_balls_high"] >= 60) & (bowl["legal_balls_high"] < 100)).sum(),
        ((bowl["legal_balls_high"] >= 100) & (bowl["legal_balls_high"] < 150)).sum(),
        (bowl["legal_balls_high"] >= 150).sum(),
    ]
    colors_bw = ["#cbd5e1", "#fdba74", "#fb923c", "#f97316", "#ea580c", "#c2410c"]

    bar_w2 = p2_w / len(bw_counts) - 10
    max_c2 = 400.0
    for i, (cnt, lbl, col) in enumerate(zip(bw_counts, labels, colors_bw)):
        bx = p2_x + 5 + i * (p2_w / len(bw_counts))
        bh = cnt / max_c2 * p2_h
        by = p2_y + p2_h - bh
        svg.append(f'<rect x="{bx}" y="{by}" width="{bar_w2}" height="{bh}" fill="{col}" stroke="#64748b" stroke-width="1"/>')
        svg.append(f'<text x="{bx + bar_w2/2}" y="{by - 6}" text-anchor="middle" font-size="11" font-weight="600" fill="#334155">{cnt}</text>')
        svg.append(f'<text x="{bx + bar_w2/2}" y="{p2_y + p2_h + 18}" text-anchor="middle" font-size="9" fill="#475569">{lbl}</text>')

    svg.append(f'<text x="{w/2}" y="{h - 10}" text-anchor="middle" font-size="10" fill="#94a3b8">Threshold Gates: Qualified &ge; 30 balls; Provisional &ge; 15 balls. Low-sample outliers prevented from contaminating rankings.</text>')
    svg.append('</svg>')
    save_svg("\n".join(svg), "fig2_sample_size_distribution.svg")


# ==============================================================================
# Figure 3: Raw vs Shrunk Empirical Bayes Estimates SVG
# ==============================================================================
def generate_fig3_svg():
    w, h = 950, 480
    svg = [
        f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" style="background:#ffffff; font-family:system-ui, -apple-system, sans-serif;">',
        f'<text x="{w/2}" y="32" text-anchor="middle" font-size="18" font-weight="bold" fill="#1e293b">Figure 3: Empirical Bayes Shrinkage Effect (Raw vs Shrunk Differentials)</text>',
        f'<text x="{w/2}" y="52" text-anchor="middle" font-size="12" fill="#64748b">Partial pooling shrinks noisy small-sample estimates toward the population prior</text>'
    ]

    p1_x, p1_y, p1_w, p1_h = 70, 80, 380, 330
    svg.append(f'<rect x="{p1_x}" y="{p1_y}" width="{p1_w}" height="{p1_h}" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1"/>')
    svg.append(f'<text x="{p1_x + p1_w/2}" y="{p1_y - 10}" text-anchor="middle" font-size="13" font-weight="600" fill="#0f172a">Batter &Delta; Strike Rate Shrinkage (N = {len(qual_bat)})</text>')

    # Range: Raw diff [-50, 110], Shrunk diff [-10, 80]
    min_x, max_x = -50.0, 120.0
    min_y, max_y = -20.0, 90.0
    def scale_x1(v): return p1_x + (v - min_x) / (max_x - min_x) * p1_w
    def scale_y1(v): return p1_y + p1_h - (v - min_y) / (max_y - min_y) * p1_h

    # Prior baseline horizontal line (+18.64)
    svg.append(f'<line x1="{p1_x}" y1="{scale_y1(18.64)}" x2="{p1_x + p1_w}" y2="{scale_y1(18.64)}" stroke="#e11d48" stroke-dasharray="3,3" stroke-width="1.5"/>')
    svg.append(f'<text x="{p1_x + 10}" y="{scale_y1(18.64) - 5}" font-size="10" font-weight="600" fill="#e11d48">Prior Mean: +18.6 RPO</text>')

    for vx in [-30, 0, 30, 60, 90]:
        xp = scale_x1(vx)
        svg.append(f'<line x1="{xp}" y1="{p1_y}" x2="{xp}" y2="{p1_y + p1_h}" stroke="#e2e8f0" stroke-width="1"/>')
        svg.append(f'<text x="{xp}" y="{p1_y + p1_h + 18}" text-anchor="middle" font-size="10" fill="#64748b">{vx}</text>')
    for vy in [0, 20, 40, 60, 80]:
        yp = scale_y1(vy)
        svg.append(f'<line x1="{p1_x}" y1="{yp}" x2="{p1_x + p1_w}" y2="{yp}" stroke="#e2e8f0" stroke-width="1"/>')
        svg.append(f'<text x="{p1_x - 10}" y="{yp + 4}" text-anchor="end" font-size="10" fill="#64748b">{vy}</text>')

    for _, r in qual_bat.iterrows():
        cx = scale_x1(r["diff_strike_rate"])
        cy = scale_y1(r["shrunk_diff_strike_rate"])
        w_val = r["shrinkage_weight"]
        # color interpolate from grey (low w) to blue (high w)
        svg.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="4.5" fill="#2563eb" fill-opacity="{max(0.3, w_val):.2f}" stroke="#1e40af" stroke-width="0.8"/>')

    svg.append(f'<text x="{p1_x + p1_w/2}" y="{p1_y + p1_h + 38}" text-anchor="middle" font-size="11" font-weight="500" fill="#334155">Observed Raw &Delta; Strike Rate (High - Normal)</text>')
    svg.append(f'<text x="{p1_x - 38}" y="{p1_y + p1_h/2}" text-anchor="middle" transform="rotate(-90 {p1_x - 38} {p1_y + p1_h/2})" font-size="11" font-weight="500" fill="#334155">EB Shrunk &Delta; Strike Rate</text>')

    # Panel 2: Bowlers
    p2_x, p2_y, p2_w, p2_h = 510, 80, 380, 330
    svg.append(f'<rect x="{p2_x}" y="{p2_y}" width="{p2_w}" height="{p2_h}" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1"/>')
    svg.append(f'<text x="{p2_x + p2_w/2}" y="{p2_y - 10}" text-anchor="middle" font-size="13" font-weight="600" fill="#0f172a">Bowler &Delta; Economy Rate Shrinkage (N = {len(qual_bowl)})</text>')

    # Range: Raw diff [-5.0, 9.0], Shrunk diff [-3.0, 7.0]
    min_x2, max_x2 = -6.0, 10.0
    min_y2, max_y2 = -4.0, 8.0
    def scale_x2(v): return p2_x + (v - min_x2) / (max_x2 - min_x2) * p2_w
    def scale_y2(v): return p2_y + p2_h - (v - min_y2) / (max_y2 - min_y2) * p2_h

    # Prior baseline horizontal line (+2.95)
    svg.append(f'<line x1="{p2_x}" y1="{scale_y2(2.95)}" x2="{p2_x + p2_w}" y2="{scale_y2(2.95)}" stroke="#e11d48" stroke-dasharray="3,3" stroke-width="1.5"/>')
    svg.append(f'<text x="{p2_x + 10}" y="{scale_y2(2.95) - 5}" font-size="10" font-weight="600" fill="#e11d48">Prior Mean: +2.95 RPO</text>')

    for vx in [-3, 0, 3, 6, 9]:
        xp = scale_x2(vx)
        svg.append(f'<line x1="{xp}" y1="{p2_y}" x2="{xp}" y2="{p2_y + p2_h}" stroke="#e2e8f0" stroke-width="1"/>')
        svg.append(f'<text x="{xp}" y="{p2_y + p2_h + 18}" text-anchor="middle" font-size="10" fill="#64748b">{vx}</text>')
    for vy in [-2, 0, 2, 4, 6]:
        yp = scale_y2(vy)
        svg.append(f'<line x1="{p2_x}" y1="{yp}" x2="{p2_x + p2_w}" y2="{yp}" stroke="#e2e8f0" stroke-width="1"/>')
        svg.append(f'<text x="{p2_x - 10}" y="{yp + 4}" text-anchor="end" font-size="10" fill="#64748b">{vy}</text>')

    for _, r in qual_bowl.iterrows():
        cx = scale_x2(r["diff_economy_rate"])
        cy = scale_y2(r["shrunk_diff_economy_rate"])
        w_val = r["shrinkage_weight"]
        svg.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="4.5" fill="#ea580c" fill-opacity="{max(0.3, w_val):.2f}" stroke="#9a3412" stroke-width="0.8"/>')

    svg.append(f'<text x="{p2_x + p2_w/2}" y="{p2_y + p2_h + 38}" text-anchor="middle" font-size="11" font-weight="500" fill="#334155">Observed Raw &Delta; Economy Rate (High - Normal)</text>')
    svg.append(f'<text x="{p2_x - 38}" y="{p2_y + p2_h/2}" text-anchor="middle" transform="rotate(-90 {p2_x - 38} {p2_y + p2_h/2})" font-size="11" font-weight="500" fill="#334155">EB Shrunk &Delta; Economy Rate</text>')

    svg.append(f'<text x="{w/2}" y="{h - 10}" text-anchor="middle" font-size="10" fill="#94a3b8">Note: Opacity corresponds to shrinkage weight w_i. Larger samples experience less shrinkage, retaining raw variance.</text>')
    svg.append('</svg>')
    save_svg("\n".join(svg), "fig3_raw_vs_shrunk_estimates.svg")


# ==============================================================================
# Figure 4: Top Qualified Players with 95% Confidence Intervals SVG
# ==============================================================================
def generate_fig4_svg():
    w, h = 950, 520
    svg = [
        f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" style="background:#ffffff; font-family:system-ui, -apple-system, sans-serif;">',
        f'<text x="{w/2}" y="30" text-anchor="middle" font-size="18" font-weight="bold" fill="#1e293b">Figure 4: Top Qualified Players with 95% Match-Cluster Bootstrap Intervals</text>',
        f'<text x="{w/2}" y="48" text-anchor="middle" font-size="12" fill="#64748b">Reliability Index point estimates with honest uncertainty intervals derived from 500 match cluster resamples</text>'
    ]

    # Panel 1: Top 10 Qualified Batters
    top_bat = qual_bat.sort_values(by="batter_reliability_index", ascending=False).head(10).reset_index(drop=True)
    p1_x, p1_y, p1_w, p1_h = 160, 75, 290, 380

    svg.append(f'<text x="{p1_x + p1_w/2}" y="{p1_y - 8}" text-anchor="middle" font-size="13" font-weight="600" fill="#0f172a">Top 10 Qualified Batters</text>')
    min_sc, max_sc = 35.0, 85.0
    def scale_sc1(v): return p1_x + (v - min_sc) / (max_sc - min_sc) * p1_w

    # Baseline 50.0
    svg.append(f'<line x1="{scale_sc1(50.0)}" y1="{p1_y}" x2="{scale_sc1(50.0)}" y2="{p1_y + p1_h}" stroke="#94a3b8" stroke-dasharray="3,3" stroke-width="1.5"/>')
    svg.append(f'<text x="{scale_sc1(50.0)}" y="{p1_y + p1_h + 16}" text-anchor="middle" font-size="10" fill="#64748b">50.0</text>')

    row_h = p1_h / len(top_bat)
    for i, r in top_bat.iterrows():
        ry = p1_y + i * row_h + row_h / 2
        name = r["striker_name"]
        score = r["batter_reliability_index"]
        lo = r["ci_lower_95"]
        hi = r["ci_upper_95"]

        svg.append(f'<text x="{p1_x - 12}" y="{ry + 4}" text-anchor="end" font-size="11" fill="#1e293b">{name}</text>')
        # Error bar
        svg.append(f'<line x1="{scale_sc1(lo):.1f}" y1="{ry}" x2="{scale_sc1(hi):.1f}" y2="{ry}" stroke="#93c5fd" stroke-width="3"/>')
        svg.append(f'<line x1="{scale_sc1(lo):.1f}" y1="{ry - 4}" x2="{scale_sc1(lo):.1f}" y2="{ry + 4}" stroke="#60a5fa" stroke-width="1.5"/>')
        svg.append(f'<line x1="{scale_sc1(hi):.1f}" y1="{ry - 4}" x2="{scale_sc1(hi):.1f}" y2="{ry + 4}" stroke="#60a5fa" stroke-width="1.5"/>')
        # Point estimate
        svg.append(f'<circle cx="{scale_sc1(score):.1f}" cy="{ry}" r="4.5" fill="#2563eb" stroke="#1e40af" stroke-width="1"/>')
        svg.append(f'<text x="{scale_sc1(hi) + 8}" y="{ry + 3}" font-size="9" fill="#64748b">{score:.1f}</text>')

    # Panel 2: Top 10 Qualified Bowlers
    top_bowl = qual_bowl.sort_values(by="bowler_reliability_index", ascending=False).head(10).reset_index(drop=True)
    p2_x, p2_y, p2_w, p2_h = 630, 75, 290, 380

    svg.append(f'<text x="{p2_x + p2_w/2}" y="{p2_y - 8}" text-anchor="middle" font-size="13" font-weight="600" fill="#0f172a">Top 10 Qualified Bowlers</text>')
    def scale_sc2(v): return p2_x + (v - min_sc) / (max_sc - min_sc) * p2_w

    svg.append(f'<line x1="{scale_sc2(50.0)}" y1="{p2_y}" x2="{scale_sc2(50.0)}" y2="{p2_y + p2_h}" stroke="#94a3b8" stroke-dasharray="3,3" stroke-width="1.5"/>')
    svg.append(f'<text x="{scale_sc2(50.0)}" y="{p2_y + p2_h + 16}" text-anchor="middle" font-size="10" fill="#64748b">50.0</text>')

    for i, r in top_bowl.iterrows():
        ry = p2_y + i * row_h + row_h / 2
        name = r["bowler_name"]
        score = r["bowler_reliability_index"]
        lo = r["ci_lower_95"]
        hi = r["ci_upper_95"]

        svg.append(f'<text x="{p2_x - 12}" y="{ry + 4}" text-anchor="end" font-size="11" fill="#1e293b">{name}</text>')
        # Error bar
        svg.append(f'<line x1="{scale_sc2(lo):.1f}" y1="{ry}" x2="{scale_sc2(hi):.1f}" y2="{ry}" stroke="#fdba74" stroke-width="3"/>')
        svg.append(f'<line x1="{scale_sc2(lo):.1f}" y1="{ry - 4}" x2="{scale_sc2(lo):.1f}" y2="{ry + 4}" stroke="#fb923c" stroke-width="1.5"/>')
        svg.append(f'<line x1="{scale_sc2(hi):.1f}" y1="{ry - 4}" x2="{scale_sc2(hi):.1f}" y2="{ry + 4}" stroke="#fb923c" stroke-width="1.5"/>')
        # Point estimate
        svg.append(f'<circle cx="{scale_sc2(score):.1f}" cy="{ry}" r="4.5" fill="#ea580c" stroke="#c2410c" stroke-width="1"/>')
        svg.append(f'<text x="{scale_sc2(hi) + 8}" y="{ry + 3}" font-size="9" fill="#64748b">{score:.1f}</text>')

    svg.append(f'<text x="{w/2}" y="{h - 10}" text-anchor="middle" font-size="10" fill="#94a3b8">Note: Width of intervals reflects match-level volatility and sample density. Top performers are not final top-10 selections.</text>')
    svg.append('</svg>')
    save_svg("\n".join(svg), "fig4_confidence_interval_comparisons.svg")


# ==============================================================================
# Figure 5: Reliability Index by Eligibility Tier SVG
# ==============================================================================
def generate_fig5_svg():
    w, h = 800, 380
    svg = [
        f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" style="background:#ffffff; font-family:system-ui, -apple-system, sans-serif;">',
        f'<text x="{w/2}" y="30" text-anchor="middle" font-size="18" font-weight="bold" fill="#1e293b">Figure 5: Player Reliability Index Distribution across Eligibility Tiers</text>',
        f'<text x="{w/2}" y="48" text-anchor="middle" font-size="12" fill="#64748b">Comparison of Score Variance: Qualified (full variance) vs Provisional (shrunk) vs Ineligible (clamped to 50.0)</text>'
    ]

    tiers = [
        ("Qualified (Bat)", qual_bat["batter_reliability_index"], "#2563eb"),
        ("Provisional (Bat)", bat[bat["eligibility_tier"] == "Provisional"]["batter_reliability_index"], "#60a5fa"),
        ("Qualified (Bowl)", qual_bowl["bowler_reliability_index"], "#ea580c"),
        ("Provisional (Bowl)", bowl[bowl["eligibility_tier"] == "Provisional"]["bowler_reliability_index"], "#fb923c"),
        ("Ineligible (All)", pd.Series([50.0] * 100), "#94a3b8"),
    ]

    p_x, p_y, p_w, p_h = 160, 75, 580, 260
    svg.append(f'<rect x="{p_x}" y="{p_y}" width="{p_w}" height="{p_h}" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1"/>')

    min_v, max_v = 30.0, 75.0
    def scale_v(v): return p_x + (v - min_v) / (max_v - min_v) * p_w

    for v_tick in [35, 40, 45, 50, 55, 60, 65, 70]:
        xp = scale_v(v_tick)
        svg.append(f'<line x1="{xp}" y1="{p_y}" x2="{xp}" y2="{p_y + p_h}" stroke="#e2e8f0" stroke-width="1"/>')
        svg.append(f'<text x="{xp}" y="{p_y + p_h + 18}" text-anchor="middle" font-size="10" fill="#64748b">{v_tick}</text>')

    row_h = p_h / len(tiers)
    for i, (name, s, col) in enumerate(tiers):
        ry = p_y + i * row_h + row_h / 2
        p25, p50, p75 = s.quantile(0.25), s.median(), s.quantile(0.75)
        pmin, pmax = s.min(), s.max()

        svg.append(f'<text x="{p_x - 12}" y="{ry + 4}" text-anchor="end" font-size="11" font-weight="500" fill="#1e293b">{name}</text>')
        # Whisker
        svg.append(f'<line x1="{scale_v(pmin):.1f}" y1="{ry}" x2="{scale_v(pmax):.1f}" y2="{ry}" stroke="#64748b" stroke-width="1.5"/>')
        # Box
        bx1 = scale_v(p25)
        bx2 = scale_v(p75)
        svg.append(f'<rect x="{bx1:.1f}" y="{ry - 10}" width="{max(2, bx2 - bx1):.1f}" height="20" fill="{col}" fill-opacity="0.75" stroke="{col}" stroke-width="1.5"/>')
        # Median line
        svg.append(f'<line x1="{scale_v(p50):.1f}" y1="{ry - 10}" x2="{scale_v(p50):.1f}" y2="{ry + 10}" stroke="#0f172a" stroke-width="2"/>')

    svg.append(f'<text x="{w/2}" y="{h - 10}" text-anchor="middle" font-size="10" fill="#94a3b8">Ineligible players lack statistical power and are clamped strictly to neutral baseline 50.0.</text>')
    svg.append('</svg>')
    save_svg("\n".join(svg), "fig5_reliability_index_by_tier.svg")


# ==============================================================================
# Interactive Plotly Dashboard
# ==============================================================================
def generate_plotly_dashboard():
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Batters: High vs Normal Strike Rate",
            "Bowlers: High vs Normal Economy Rate",
            "Top Qualified Batters (Reliability Index)",
            "Top Qualified Bowlers (Reliability Index)"
        )
    )

    # Subplot 1: Batters Scatter
    fig.add_trace(
        go.Scatter(
            x=qual_bat["strike_rate_normal"],
            y=qual_bat["strike_rate_high"],
            mode="markers",
            text=qual_bat["striker_name"],
            marker=dict(size=qual_bat["effective_balls"] * 0.4, color="#2563eb", opacity=0.7),
            name="Batters"
        ),
        row=1, col=1
    )

    # Subplot 2: Bowlers Scatter
    fig.add_trace(
        go.Scatter(
            x=qual_bowl["economy_rate_normal"],
            y=qual_bowl["economy_rate_high"],
            mode="markers",
            text=qual_bowl["bowler_name"],
            marker=dict(size=qual_bowl["effective_balls"] * 0.4, color="#ea580c", opacity=0.7),
            name="Bowlers"
        ),
        row=1, col=2
    )

    # Subplot 3: Top Batters Bar
    top_b = qual_bat.sort_values(by="batter_reliability_index", ascending=False).head(10)
    fig.add_trace(
        go.Bar(
            x=top_b["batter_reliability_index"],
            y=top_b["striker_name"],
            orientation="h",
            marker=dict(color="#2563eb"),
            name="Top Batters"
        ),
        row=2, col=1
    )

    # Subplot 4: Top Bowlers Bar
    top_bw = qual_bowl.sort_values(by="bowler_reliability_index", ascending=False).head(10)
    fig.add_trace(
        go.Bar(
            x=top_bw["bowler_reliability_index"],
            y=top_bw["bowler_name"],
            orientation="h",
            marker=dict(color="#ea580c"),
            name="Top Bowlers"
        ),
        row=2, col=2
    )

    fig.update_layout(
        title_text="SUPERR SELECTOR — Master Task 05 Interactive Player Reliability Analytics Dashboard",
        height=850,
        showlegend=False
    )

    html_path = os.path.join(FIGURES_DIR, "interactive_player_reliability.html")
    fig.write_html(html_path)
    print(f"Saved interactive HTML dashboard: {html_path}")


if __name__ == "__main__":
    generate_fig1_svg()
    generate_fig2_svg()
    generate_fig3_svg()
    generate_fig4_svg()
    generate_fig5_svg()
    generate_plotly_dashboard()
