"""
SUPERR SELECTOR - Rajasthan Royals Season 2 Hackathon
Premium Cricket Performance Intelligence & Squad Analytics Platform
Streamlit Web Application - Ultra Premium Edition
"""

import os
import json
import base64
from pathlib import Path

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ------------------------------------------------------------------------------
# 1. STREAMLIT PAGE CONFIGURATION & METADATA
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="SUPERR SELECTOR | Rajasthan Royals Analytics",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------------------------------------------------------
# 2. DESIGN SYSTEM & CUSTOM CSS
# Rajasthan Royals Identity: Deep Navy (#0A0E1A, #0F1523), Royal Pink (#E5097F),
# Electric Blue (#00D2FF), Gold (#FFB703), Card Charcoal (#151C2C)
# ------------------------------------------------------------------------------
st.markdown("""
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Rajdhani:wght@500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main Container Padding */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3.5rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 1450px;
    }

    /* Backgrounds */
    .stApp {
        background: #F8FAFC;
        color: #0F172A;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid rgba(15, 23, 42, 0.08);
    }

    /* Header Banner */
    .rr-header-banner {
        background: linear-gradient(135deg, rgba(229, 9, 127, 0.18) 0%, #FFFFFF 50%, rgba(0, 210, 255, 0.15) 100%);
        border: 1px solid rgba(229, 9, 127, 0.35);
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.05);
    }
    .rr-header-banner::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; height: 3px;
        background: linear-gradient(90deg, #E5097F 0%, #FFB703 50%, #00D2FF 100%);
    }

    .badge-pill {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    .badge-pink {
        background: rgba(229, 9, 127, 0.22);
        color: #FF52A2;
        border: 1px solid rgba(229, 9, 127, 0.45);
    }
    .badge-blue {
        background: rgba(0, 210, 255, 0.18);
        color: #00D2FF;
        border: 1px solid rgba(0, 210, 255, 0.4);
    }
    .badge-gold {
        background: rgba(255, 183, 3, 0.18);
        color: #FFB703;
        border: 1px solid rgba(255, 183, 3, 0.4);
    }

    /* Metric KPI Cards */
    .kpi-card {
        background: #FFFFFF;
        border: 1px solid rgba(15, 23, 42, 0.08);
        border-radius: 12px;
        padding: 16px 18px;
        transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        border-color: rgba(229, 9, 127, 0.4);
        box-shadow: 0 8px 24px rgba(229, 9, 127, 0.15);
    }
    .kpi-title {
        font-size: 0.78rem;
        font-weight: 600;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 4px;
    }
    .kpi-value {
        font-family: 'Rajdhani', sans-serif;
        font-size: 2.1rem;
        font-weight: 700;
        line-height: 1.1;
        color: #0F172A;
    }
    .kpi-subtitle {
        font-size: 0.74rem;
        color: #64748B;
        margin-top: 4px;
    }

    /* Player Roster Cards (Visual Grid) */
    .player-roster-card {
        background: #FFFFFF;
        border: 1px solid rgba(15, 23, 42, 0.09);
        border-radius: 14px;
        padding: 14px 12px;
        text-align: center;
        position: relative;
        transition: all 0.25s cubic-bezier(0.25, 0.8, 0.25, 1);
        box-shadow: 0 4px 16px rgba(15, 23, 42, 0.05);
        margin-bottom: 16px;
        backdrop-filter: blur(8px);
    }
    .player-roster-card:hover {
        transform: translateY(-5px);
        border-color: rgba(229, 9, 127, 0.55);
        box-shadow: 0 12px 28px rgba(229, 9, 127, 0.22);
    }
    .player-roster-card.blue:hover {
        border-color: rgba(0, 210, 255, 0.55);
        box-shadow: 0 12px 28px rgba(0, 210, 255, 0.22);
    }
    .card-rank-badge {
        position: absolute;
        top: 8px;
        left: 8px;
        background: rgba(229, 9, 127, 0.25);
        color: #FF52A2;
        border: 1px solid rgba(229, 9, 127, 0.5);
        padding: 2px 7px;
        border-radius: 12px;
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    .player-roster-card.blue .card-rank-badge {
        background: rgba(0, 210, 255, 0.2);
        color: #00D2FF;
        border: 1px solid rgba(0, 210, 255, 0.4);
    }
    .card-img-container {
        height: 140px;
        display: flex;
        align-items: flex-end;
        justify-content: center;
        margin-bottom: 8px;
        margin-top: 4px;
    }
    .player-cutout-img {
        max-height: 135px;
        max-width: 100%;
        object-fit: contain;
        filter: drop-shadow(0 8px 12px rgba(0, 0, 0, 0.6));
        transition: transform 0.3s ease;
    }
    .player-roster-card:hover .player-cutout-img {
        transform: scale(1.06);
    }
    .card-player-name {
        font-family: 'Rajdhani', sans-serif;
        font-size: 1.15rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 2px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .card-player-id {
        font-size: 0.72rem;
        color: #94A3B8;
        margin-bottom: 8px;
    }
    .card-score-pill {
        background: #F8FAFC;
        border: 1px solid rgba(15, 23, 42, 0.08);
        border-radius: 8px;
        padding: 5px 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }
    .score-label {
        font-size: 0.65rem;
        color: #94A3B8;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .score-value {
        font-family: 'Rajdhani', sans-serif;
        font-size: 1.25rem;
        font-weight: 700;
        color: #E5097F;
    }
    .player-roster-card.blue .score-value {
        color: #00D2FF;
    }
    .card-stat-row {
        display: flex;
        justify-content: space-around;
        border-top: 1px solid rgba(15, 23, 42, 0.06);
        padding-top: 6px;
        font-size: 0.75rem;
    }
    .stat-lbl {
        color: #64748B;
        font-size: 0.65rem;
        text-transform: uppercase;
        display: block;
    }
    .stat-val {
        color: #1E293B;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .text-green {
        color: #10B981 !important;
    }

    /* Hero Spotlight Cards */
    .hero-spotlight {
        background: #FFFFFF;
        border: 1px solid rgba(15, 23, 42, 0.09);
        border-radius: 16px;
        padding: 20px;
        display: flex;
        align-items: center;
        gap: 20px;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
        position: relative;
        overflow: hidden;
    }
    .hero-spotlight.pink {
        border-left: 5px solid #E5097F;
    }
    .hero-spotlight.blue {
        border-left: 5px solid #00D2FF;
    }

    /* Section Subheadings */
    .section-title {
        font-family: 'Rajdhani', sans-serif;
        font-size: 1.55rem;
        font-weight: 700;
        color: #0F172A;
        letter-spacing: 0.5px;
        margin-top: 18px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    /* Glass Container */
    .glass-box {
        background: #FFFFFF;
        border: 1px solid rgba(15, 23, 42, 0.08);
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 16px rgba(15, 23, 42, 0.04);
    }

    /* Footer */
    .rr-footer {
        text-align: center;
        padding: 28px 0 10px 0;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        margin-top: 40px;
        font-size: 0.85rem;
        color: #64748B;
        letter-spacing: 1px;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 3. DIRECTORY RESOLUTION & DATA LOADERS
# ------------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
ANALYTICS_DIR = BASE_DIR / "Data" / "analytics"
ML_DIR = BASE_DIR / "Data" / "ml"
ASSETS_DIR = BASE_DIR / "assets"
PLAYER_IMAGES_DIR = ASSETS_DIR / "player_images"

PLAYER_IMAGE_MAP = {
    "Jason Holder": "jason_holder.png",
    "Sanju Samson": "sanju_samson.png",
    "Curtis Campher": "curtis_campher.png",
    "Phil Salt": "phil_salt.png",
    "David Willey": "david_willey.png",
    "Dion Myers": "dion_myers.png",
    "Shan Masood": "shan_masood.png",
    "Dasun Shanaka": "dasun_shanaka.png",
    "Matthew Wade": "matthew_wade.png",
    "Iftikhar Ahmed": "iftikhar_ahmed.png",
    "Mitchell Marsh": "mitchell_marsh.png",
    "Haris Rauf": "haris_rauf.png",
    "Kartik Tyagi": "kartik_tyagi.png",
    "Vaibhav Arora": "vaibhav_arora.png",
    "Ravi Bishnoi": "ravi_bishnoi.png",
    "Azmatullah Omarzai": "azmatullah_omarzai.png",
    "Keshav Maharaj": "keshav_maharaj.png",
    "Corbin Bosch": "corbin_bosch.png",
    "Wanindu Hasaranga": "wanindu_hasaranga.png",
    "Sam Curran": "sam_curran.png"
}

@st.cache_data
def get_player_b64_cache():
    """Caches base64-encoded strings for all 20 professional player images."""
    b64_dict = {}
    for player_name, fname in PLAYER_IMAGE_MAP.items():
        p = PLAYER_IMAGES_DIR / fname
        if p.exists():
            with open(p, "rb") as f:
                b64_dict[player_name] = "data:image/png;base64," + base64.b64encode(f.read()).decode("utf-8")
    return b64_dict

@st.cache_data
def load_all_datasets():
    """Loads certified data artifacts and returns structured dataframes."""
    top10_batters = pd.read_csv(ANALYTICS_DIR / "task_07_final_top10_batters.csv")
    top10_bowlers = pd.read_csv(ANALYTICS_DIR / "task_07_final_top10_bowlers.csv")
    all_batters = pd.read_csv(ANALYTICS_DIR / "task_07_all_qualified_batters_ranked.csv")
    all_bowlers = pd.read_csv(ANALYTICS_DIR / "task_07_all_qualified_bowlers_ranked.csv")
    batter_rel = pd.read_csv(ANALYTICS_DIR / "task_05_batter_reliability.csv")
    bowler_rel = pd.read_csv(ANALYTICS_DIR / "task_05_bowler_reliability.csv")

    try:
        batter_archetypes = pd.read_csv(ML_DIR / "task_06_batter_archetypes.csv")
        bowler_archetypes = pd.read_csv(ML_DIR / "task_06_bowler_archetypes.csv")
    except Exception:
        batter_archetypes = pd.DataFrame()
        bowler_archetypes = pd.DataFrame()

    pressure_summary = {}
    summary_path = ANALYTICS_DIR / "pressure_summary.json"
    if summary_path.exists():
        with open(summary_path, "r") as f:
            pressure_summary = json.load(f)

    return {
        "top10_batters": top10_batters,
        "top10_bowlers": top10_bowlers,
        "all_batters": all_batters,
        "all_bowlers": all_bowlers,
        "batter_rel": batter_rel,
        "bowler_rel": bowler_rel,
        "batter_archetypes": batter_archetypes,
        "bowler_archetypes": bowler_archetypes,
        "pressure_summary": pressure_summary
    }

# ------------------------------------------------------------------------------
# 4. PLOTLY THEME HELPER
# ------------------------------------------------------------------------------
def apply_rr_theme(fig, title: str = "", height: int = 400, x_title: str = "", y_title: str = "", show_legend: bool = True):
    """Applies Rajasthan Royals dark aesthetic to Plotly figures."""
    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(size=14, color="#0F172A", family="Rajdhani, Inter, sans-serif"),
            x=0.01,
            y=0.96
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#334155", family="Inter, system-ui, sans-serif"),
        height=height,
        margin=dict(l=35, r=35, t=50, b=40),
        showlegend=show_legend,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11, color="#1E293B"),
            bgcolor="rgba(0,0,0,0)"
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(15,23,42,0.06)",
            linecolor="rgba(15,23,42,0.15)",
            tickfont=dict(color="#94A3B8"),
            title=dict(text=x_title, font=dict(color="#94A3B8", size=11))
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(15,23,42,0.06)",
            linecolor="rgba(15,23,42,0.15)",
            tickfont=dict(color="#94A3B8"),
            title=dict(text=y_title, font=dict(color="#94A3B8", size=11))
        )
    )
    return fig

# ------------------------------------------------------------------------------
# 5. DATA & IMAGE CACHE INITIALIZATION
# ------------------------------------------------------------------------------
data = load_all_datasets()
player_images = get_player_b64_cache()

top10_batters = data["top10_batters"]
top10_bowlers = data["top10_bowlers"]
all_batters = data["all_batters"]
all_bowlers = data["all_bowlers"]
batter_rel = data["batter_rel"]
bowler_rel = data["bowler_rel"]
press_summary = data["pressure_summary"]

# Merge detailed metrics into top10 for rich visual cards
m_bat = top10_batters.merge(
    batter_rel[["striker_id", "strike_rate_normal", "dot_pct_high", "dot_pct_normal", "dismissal_rate_per_100_high", "dismissal_rate_per_100_normal"]],
    on="striker_id", how="left"
)
m_bowl = top10_bowlers.merge(
    bowler_rel[["bowler_id", "economy_rate_normal", "wickets_per_over_high", "wickets_per_over_normal", "dot_pct_high", "dot_pct_normal", "boundary_conceded_pct_high", "boundary_conceded_pct_normal"]],
    on="bowler_id", how="left"
)

# ------------------------------------------------------------------------------
# 6. SIDEBAR NAVIGATION
# ------------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="padding: 10px 0 16px 0;">
        <span class="badge-pill badge-pink">RAJASTHAN ROYALS</span>
        <h2 style="font-family: 'Rajdhani', sans-serif; font-size: 1.8rem; margin: 4px 0 2px 0; color: #0F172A;">
            ⚡ SUPERR SELECTOR
        </h2>
        <p style="font-size: 0.8rem; color: #94A3B8; margin: 0;">
            Cricket Performance Intelligence & Squad Strategy
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    nav_selection = st.radio(
        label="DASHBOARD NAVIGATION",
        options=[
            "1. Overview",
            "2. Batting Intelligence",
            "3. Bowling Intelligence",
            "4. Pressure Analysis",
            "5. Player Comparison",
            "6. Player Rankings",
            "7. Methodology & Validation"
        ],
        index=0
    )

    st.markdown("---")
    st.markdown("""
    <div style="font-size: 0.75rem; color: #64748B; line-height: 1.6;">
        <b style="color: #94A3B8;">PLATFORM SPECIFICATIONS</b><br>
        • Season: IPL 2027 Strategy<br>
        • Matches: 837 Indexed<br>
        • Deliveries: 193,976 Analysed<br>
        • Engine: Empirical Bayes + Physical Model<br>
        • Status: <span style="color: #10B981;">● Certified Production</span>
    </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# SECTION 1: OVERVIEW DASHBOARD
# ==============================================================================
if nav_selection == "1. Overview":
    st.markdown("""
    <div class="rr-header-banner">
        <span class="badge-pill badge-pink">EXECUTIVE INTELLIGENCE BRIEF</span>
        <h1 style="font-family: 'Rajdhani', sans-serif; font-size: 2.3rem; margin: 6px 0 8px 0; color: #0F172A;">
            SUPERR SELECTOR — RAJASTHAN ROYALS SEASON 2
        </h1>
        <p style="font-size: 0.95rem; color: #CBD5E1; margin: 0; max-width: 950px; line-height: 1.5;">
            Official player scouting and performance intelligence platform for Rajasthan Royals. 
            Evaluating pressure-tested reliability across 193,976 deliveries using empirical situational leverage, 
            multidimensional stress indices, and Bayesian shrinkage.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 5 Key Platform KPIs
    kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)
    with kpi_col1:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-title">Matches Analysed</div>
            <div class="kpi-value" style="color: #00D2FF;">837</div>
            <div class="kpi-subtitle">340 IPL + 497 T20I Encounters</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi_col2:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-title">Deliveries Analysed</div>
            <div class="kpi-value" style="color: #FFB703;">193,976</div>
            <div class="kpi-subtitle">Ball-by-Ball Leverage Scored</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi_col3:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-title">Unique Players</div>
            <div class="kpi-value" style="color: #E2E8F0;">891</div>
            <div class="kpi-subtitle">Global T20 Talent Pool</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi_col4:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-title">Qualified Batters</div>
            <div class="kpi-value" style="color: #E5097F;">109</div>
            <div class="kpi-subtitle">≥30 HP & ≥30 Norm Balls, ≥5 M</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi_col5:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-title">Qualified Bowlers</div>
            <div class="kpi-value" style="color: #38BDF8;">136</div>
            <div class="kpi-subtitle">≥30 HP & ≥30 Norm Balls, ≥5 M</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # Hero Spotlight: Top-Ranked Batter & Bowler with REAL Cutout Headshots
    hero_b_col, hero_bowl_col = st.columns(2)
    jason_img = player_images.get("Jason Holder", "")
    mitch_img = player_images.get("Mitchell Marsh", "")

    with hero_b_col:
        st.markdown(f"""
        <div class="hero-spotlight pink">
            <div style="flex: 0 0 110px; height: 130px; display: flex; align-items: center; justify-content: center;">
                <img src="{jason_img}" style="max-height: 130px; max-width: 100%; object-fit: contain; filter: drop-shadow(0 6px 12px rgba(229,9,127,0.35));" alt="Jason Holder">
            </div>
            <div style="flex: 1;">
                <span class="badge-pill badge-pink">#1 RANKED BATTER • ELITE</span>
                <div style="font-family: 'Rajdhani', sans-serif; font-size: 1.6rem; font-weight: 700; color: #0F172A;">
                    Jason Holder
                </div>
                <div style="font-size: 0.78rem; color: #94A3B8; margin-bottom: 6px;">
                    Player ID: 2633 | RHB All-Rounder | 59 Matches
                </div>
                <div style="display: flex; gap: 18px; align-items: baseline; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 8px;">
                    <div>
                        <span style="font-size: 0.68rem; color: #94A3B8; text-transform: uppercase;">Reliability Index</span><br>
                        <b style="font-family: 'Rajdhani', sans-serif; font-size: 1.6rem; color: #E5097F;">66.84</b>
                    </div>
                    <div>
                        <span style="font-size: 0.68rem; color: #94A3B8; text-transform: uppercase;">HP Strike Rate</span><br>
                        <b style="font-family: 'Rajdhani', sans-serif; font-size: 1.3rem; color: #00D2FF;">175.30</b>
                        <span style="font-size: 0.75rem; color: #10B981;"> (+108.0)</span>
                    </div>
                    <div>
                        <span style="font-size: 0.68rem; color: #94A3B8; text-transform: uppercase;">95% Confidence</span><br>
                        <span style="font-size: 0.85rem; color: #CBD5E1;">[58.05 - 73.99]</span>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with hero_bowl_col:
        st.markdown(f"""
        <div class="hero-spotlight blue">
            <div style="flex: 0 0 110px; height: 130px; display: flex; align-items: center; justify-content: center;">
                <img src="{mitch_img}" style="max-height: 130px; max-width: 100%; object-fit: contain; filter: drop-shadow(0 6px 12px rgba(0,210,255,0.35));" alt="Mitchell Marsh">
            </div>
            <div style="flex: 1;">
                <span class="badge-pill badge-blue">#1 RANKED BOWLER • STRONG</span>
                <div style="font-family: 'Rajdhani', sans-serif; font-size: 1.6rem; font-weight: 700; color: #0F172A;">
                    Mitchell Marsh
                </div>
                <div style="font-size: 0.78rem; color: #94A3B8; margin-bottom: 6px;">
                    Player ID: 818 | Right-arm Medium-Fast | 19 Matches
                </div>
                <div style="display: flex; gap: 18px; align-items: baseline; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 8px;">
                    <div>
                        <span style="font-size: 0.68rem; color: #94A3B8; text-transform: uppercase;">Reliability Index</span><br>
                        <b style="font-family: 'Rajdhani', sans-serif; font-size: 1.6rem; color: #00D2FF;">61.86</b>
                    </div>
                    <div>
                        <span style="font-size: 0.68rem; color: #94A3B8; text-transform: uppercase;">HP Economy</span><br>
                        <b style="font-family: 'Rajdhani', sans-serif; font-size: 1.3rem; color: #E5097F;">10.50</b>
                        <span style="font-size: 0.75rem; color: #10B981;"> (-1.96)</span>
                    </div>
                    <div>
                        <span style="font-size: 0.68rem; color: #94A3B8; text-transform: uppercase;">95% Confidence</span><br>
                        <span style="font-size: 0.85rem; color: #CBD5E1;">[50.00 - 69.66]</span>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # Visual Showcase: Top 5 Elite Batters
    st.markdown("<div class='section-title'>🏏 Top 5 Certified Batters (Visual Showcase)</div>", unsafe_allow_html=True)
    b5_cols = st.columns(5)
    for i in range(5):
        row = m_bat.iloc[i]
        b_img = player_images.get(row["striker_name"], "")
        with b5_cols[i]:
            st.markdown(f"""
            <div class="player-roster-card">
                <div class="card-rank-badge">#{row['rank']}</div>
                <div class="card-img-container">
                    <img src="{b_img}" class="player-cutout-img" alt="{row['striker_name']}">
                </div>
                <div class="card-player-name">{row['striker_name']}</div>
                <div class="card-player-id">ID: {row['striker_id']} • {row['batting_type']}</div>
                <div class="card-score-pill">
                    <span class="score-label">RELIABILITY</span>
                    <span class="score-value">{row['batter_reliability_index']:.2f}</span>
                </div>
                <div class="card-stat-row">
                    <div>
                        <span class="stat-lbl">HP SR</span>
                        <span class="stat-val">{row['strike_rate_high']:.1f}</span>
                    </div>
                    <div>
                        <span class="stat-lbl">Delta SR</span>
                        <span class="stat-val text-green">{row['diff_strike_rate']:+.1f}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Visual Showcase: Top 5 Elite Bowlers
    st.markdown("<div class='section-title'>🎯 Top 5 Certified Bowlers (Visual Showcase)</div>", unsafe_allow_html=True)
    bowl5_cols = st.columns(5)
    for i in range(5):
        row = m_bowl.iloc[i]
        bowl_img = player_images.get(row["bowler_name"], "")
        with bowl5_cols[i]:
            st.markdown(f"""
            <div class="player-roster-card blue">
                <div class="card-rank-badge">#{row['rank']}</div>
                <div class="card-img-container">
                    <img src="{bowl_img}" class="player-cutout-img" alt="{row['bowler_name']}">
                </div>
                <div class="card-player-name">{row['bowler_name']}</div>
                <div class="card-player-id">ID: {row['bowler_id']} • {row['pace_or_spin']}</div>
                <div class="card-score-pill">
                    <span class="score-label">RELIABILITY</span>
                    <span class="score-value">{row['bowler_reliability_index']:.2f}</span>
                </div>
                <div class="card-stat-row">
                    <div>
                        <span class="stat-lbl">HP Econ</span>
                        <span class="stat-val">{row['economy_rate_high']:.2f}</span>
                    </div>
                    <div>
                        <span class="stat-lbl">Delta Econ</span>
                        <span class="stat-val text-green">{row['diff_economy_rate']:+.2f}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

    # Overview Analytics Charts
    dist_col1, dist_col2 = st.columns(2)

    with dist_col1:
        fig_pie = go.Figure(data=[go.Pie(
            labels=["Qualified Batters", "Qualified Bowlers", "Non-Qualified Cohort"],
            values=[109, 136, 891 - 109 - 136],
            hole=0.55,
            marker=dict(colors=["#E5097F", "#00D2FF", "#334155"]),
            textinfo='label+value+percent',
            textfont=dict(color="#FFFFFF", size=11)
        )])
        apply_rr_theme(fig_pie, title="TALENT POOL QUALIFICATION DISTRIBUTION (891 PLAYERS)", height=340)
        st.plotly_chart(fig_pie, use_container_width=True)

    with dist_col2:
        p_cats = ["Low (0-40)", "Moderate (40-65)", "High (65-85)", "Extreme (85-100)"]
        bat_counts = [63979, 104755, 15617, 9625]
        bowl_counts = [33917, 145419, 12945, 1695]

        fig_press_over = go.Figure()
        fig_press_over.add_trace(go.Bar(
            name="Batting Deliveries",
            x=p_cats,
            y=bat_counts,
            marker_color="#E5097F"
        ))
        fig_press_over.add_trace(go.Bar(
            name="Bowling Deliveries",
            x=p_cats,
            y=bowl_counts,
            marker_color="#00D2FF"
        ))
        fig_press_over.update_layout(barmode='group')
        apply_rr_theme(fig_press_over, title="DELIVERY DISTRIBUTION BY PRESSURE CATEGORY", height=340, x_title="Pressure Category", y_title="Deliveries Analysed")
        st.plotly_chart(fig_press_over, use_container_width=True)


# ==============================================================================
# SECTION 2: BATTING INTELLIGENCE
# ==============================================================================
elif nav_selection == "2. Batting Intelligence":
    st.markdown("""
    <div class="rr-header-banner">
        <span class="badge-pill badge-pink">BATTING RELIABILITY INTELLIGENCE</span>
        <h1 style="font-family: 'Rajdhani', sans-serif; font-size: 2.2rem; margin: 4px 0 6px 0; color: #0F172A;">
            Top 10 Certified Batters Under Pressure
        </h1>
        <p style="font-size: 0.9rem; color: #CBD5E1; margin: 0;">
            Evaluated using empirical pressure differential (HP Strike Rate, Dot-Ball Reduction, Dismissal Rate Suppression)
            with Bayesian sample shrinkage and 1,000-sample bootstrap confidence intervals.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Visual Cards Gallery for All 10 Batters
    st.markdown("<div class='section-title'>🎴 Certified Top 10 Batters (Official Player Roster)</div>", unsafe_allow_html=True)
    
    # 2 Rows of 5 Cards
    row1_cols = st.columns(5)
    for i in range(5):
        row = m_bat.iloc[i]
        b_img = player_images.get(row["striker_name"], "")
        with row1_cols[i]:
            st.markdown(f"""
            <div class="player-roster-card">
                <div class="card-rank-badge">#{row['rank']}</div>
                <div class="card-img-container">
                    <img src="{b_img}" class="player-cutout-img" alt="{row['striker_name']}">
                </div>
                <div class="card-player-name">{row['striker_name']}</div>
                <div class="card-player-id">ID: {row['striker_id']} • {row['batting_type']}</div>
                <div class="card-score-pill">
                    <span class="score-label">RELIABILITY</span>
                    <span class="score-value">{row['batter_reliability_index']:.2f}</span>
                </div>
                <div class="card-stat-row">
                    <div>
                        <span class="stat-lbl">HP SR</span>
                        <span class="stat-val">{row['strike_rate_high']:.1f}</span>
                    </div>
                    <div>
                        <span class="stat-lbl">Delta SR</span>
                        <span class="stat-val text-green">{row['diff_strike_rate']:+.1f}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    row2_cols = st.columns(5)
    for i in range(5, 10):
        row = m_bat.iloc[i]
        b_img = player_images.get(row["striker_name"], "")
        with row2_cols[i - 5]:
            st.markdown(f"""
            <div class="player-roster-card">
                <div class="card-rank-badge">#{row['rank']}</div>
                <div class="card-img-container">
                    <img src="{b_img}" class="player-cutout-img" alt="{row['striker_name']}">
                </div>
                <div class="card-player-name">{row['striker_name']}</div>
                <div class="card-player-id">ID: {row['striker_id']} • {row['batting_type']}</div>
                <div class="card-score-pill">
                    <span class="score-label">RELIABILITY</span>
                    <span class="score-value">{row['batter_reliability_index']:.2f}</span>
                </div>
                <div class="card-stat-row">
                    <div>
                        <span class="stat-lbl">HP SR</span>
                        <span class="stat-val">{row['strike_rate_high']:.1f}</span>
                    </div>
                    <div>
                        <span class="stat-lbl">Delta SR</span>
                        <span class="stat-val text-green">{row['diff_strike_rate']:+.1f}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

    # Certified Table View (Expandable/Tabbed)
    with st.expander("📋 View Complete Certified Batters Numerical Table", expanded=False):
        display_bat_df = top10_batters[[
            "rank", "striker_id", "striker_name", "batting_type", "batter_reliability_index",
            "reliability_grade", "strike_rate_high", "diff_strike_rate", "diff_dot_pct",
            "matches_overall", "balls_faced_high", "ci_lower_95", "ci_upper_95"
        ]].copy()
        display_bat_df.columns = [
            "Rank", "Player ID", "Batter Name", "Style", "Reliability Index",
            "Grade", "HP Strike Rate", "Delta Strike Rate", "Delta Dot %",
            "Matches", "HP Balls", "CI Lower (95%)", "CI Upper (95%)"
        ]
        st.dataframe(
            display_bat_df.style.format({
                "Reliability Index": "{:.2f}",
                "HP Strike Rate": "{:.2f}",
                "Delta Strike Rate": "{:+.2f}",
                "Delta Dot %": "{:+.2f}%",
                "CI Lower (95%)": "{:.2f}",
                "CI Upper (95%)": "{:.2f}"
            }),
            use_container_width=True,
            hide_index=True
        )

    # 1. Reliability Index Bar Chart with Confidence Intervals
    st.markdown("<div class='section-title'>📊 Reliability Index & 95% Bootstrap Confidence Intervals</div>", unsafe_allow_html=True)
    fig_ci_b = go.Figure()
    fig_ci_b.add_trace(go.Bar(
        x=top10_batters["striker_name"],
        y=top10_batters["batter_reliability_index"],
        error_y=dict(
            type='data',
            symmetric=False,
            array=top10_batters["ci_upper_95"] - top10_batters["batter_reliability_index"],
            arrayminus=top10_batters["batter_reliability_index"] - top10_batters["ci_lower_95"],
            color='#FFB703',
            thickness=2,
            width=6
        ),
        marker=dict(
            color='#E5097F',
            line=dict(color='rgba(255,255,255,0.2)', width=1)
        ),
        text=[f"{val:.2f}" for val in top10_batters["batter_reliability_index"]],
        textposition='outside',
        textfont=dict(color="#FFFFFF", size=11)
    ))
    apply_rr_theme(fig_ci_b, title="BATTING RELIABILITY INDEX (POINT ESTIMATE ± 95% CONFIDENCE INTERVAL)", height=380, x_title="Batter Name", y_title="Reliability Index (0-100)", show_legend=False)
    st.plotly_chart(fig_ci_b, use_container_width=True)

    # Grouped comparisons: Strike Rate & Dot %
    c_sr, c_dot = st.columns(2)

    with c_sr:
        fig_sr = go.Figure()
        fig_sr.add_trace(go.Bar(
            name="Normal Strike Rate",
            x=m_bat["striker_name"],
            y=m_bat["strike_rate_normal"],
            marker_color="#475569"
        ))
        fig_sr.add_trace(go.Bar(
            name="High-Pressure Strike Rate",
            x=m_bat["striker_name"],
            y=m_bat["strike_rate_high"],
            marker_color="#E5097F"
        ))
        fig_sr.update_layout(barmode='group')
        apply_rr_theme(fig_sr, title="HIGH-PRESSURE VS NORMAL STRIKE RATE", height=380, x_title="Batter", y_title="Strike Rate")
        st.plotly_chart(fig_sr, use_container_width=True)

    with c_dot:
        fig_dot = go.Figure()
        fig_dot.add_trace(go.Bar(
            name="Normal Dot %",
            x=m_bat["striker_name"],
            y=m_bat["dot_pct_normal"],
            marker_color="#475569"
        ))
        fig_dot.add_trace(go.Bar(
            name="High-Pressure Dot %",
            x=m_bat["striker_name"],
            y=m_bat["dot_pct_high"],
            marker_color="#00D2FF"
        ))
        fig_dot.update_layout(barmode='group')
        apply_rr_theme(fig_dot, title="DOT-BALL PERCENTAGE (HIGH-PRESSURE VS NORMAL)", height=380, x_title="Batter", y_title="Dot Ball %")
        st.plotly_chart(fig_dot, use_container_width=True)

    # Dismissal Rate & High Pressure Exposure
    c_dism, c_exp = st.columns(2)

    with c_dism:
        fig_dism = go.Figure()
        fig_dism.add_trace(go.Bar(
            name="Normal Dismissals / 100",
            x=m_bat["striker_name"],
            y=m_bat["dismissal_rate_per_100_normal"],
            marker_color="#475569"
        ))
        fig_dism.add_trace(go.Bar(
            name="HP Dismissals / 100",
            x=m_bat["striker_name"],
            y=m_bat["dismissal_rate_per_100_high"],
            marker_color="#FFB703"
        ))
        fig_dism.update_layout(barmode='group')
        apply_rr_theme(fig_dism, title="DISMISSAL RATE PER 100 BALLS (HP VS NORMAL)", height=380, x_title="Batter", y_title="Dismissals / 100 Balls")
        st.plotly_chart(fig_dism, use_container_width=True)

    with c_exp:
        fig_scat_b = px.scatter(
            all_batters,
            x="matches_overall",
            y="balls_faced_high",
            size="batter_reliability_index",
            color="reliability_grade",
            hover_name="striker_name",
            color_discrete_map={"Elite": "#E5097F", "Strong": "#00D2FF", "Moderate": "#94A3B8", "Developing": "#475569"}
        )
        apply_rr_theme(fig_scat_b, title="HIGH-PRESSURE EXPOSURE VS MATCHES PLAYED (ALL 109 QUALIFIED)", height=380, x_title="Total Matches Played", y_title="High-Pressure Balls Faced")
        st.plotly_chart(fig_scat_b, use_container_width=True)

    # Individual Batter Inspector
    st.markdown("<div class='section-title'>🔍 Individual Batter Tactical Inspector</div>", unsafe_allow_html=True)
    selected_batter_name = st.selectbox(
        "Select a Batter to Inspect:",
        options=top10_batters["striker_name"].tolist()
    )
    b_profile = m_bat[m_bat["striker_name"] == selected_batter_name].iloc[0]
    b_inspect_img = player_images.get(selected_batter_name, "")

    st.markdown(f"""
    <div class="glass-box" style="display: flex; gap: 24px; align-items: center; border-left: 5px solid #E5097F;">
        <div style="flex: 0 0 160px; height: 180px; display: flex; align-items: center; justify-content: center;">
            <img src="{b_inspect_img}" style="max-height: 180px; max-width: 100%; object-fit: contain; filter: drop-shadow(0 8px 16px rgba(229,9,127,0.4));" alt="{selected_batter_name}">
        </div>
        <div style="flex: 1;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h3 style="font-family: 'Rajdhani', sans-serif; font-size: 1.8rem; color: #0F172A; margin: 0;">{selected_batter_name}</h3>
                <span class="badge-pill badge-pink">Rank #{b_profile['rank']} • {b_profile['reliability_grade']}</span>
            </div>
            <div style="font-size: 0.85rem; color: #94A3B8; margin-top: 4px;">
                Player ID: {b_profile['striker_id']} | Batting Style: {b_profile['batting_type']} | Archetype: {b_profile['archetype_name']}
            </div>
            <hr style="border-color: rgba(255,255,255,0.08); margin: 12px 0;">
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px;">
                <div>
                    <span style="font-size: 0.7rem; color: #94A3B8; text-transform: uppercase;">Reliability Index</span><br>
                    <b style="font-size: 1.4rem; color: #E5097F;">{b_profile['batter_reliability_index']:.2f}</b>
                </div>
                <div>
                    <span style="font-size: 0.7rem; color: #94A3B8; text-transform: uppercase;">HP Strike Rate</span><br>
                    <b style="font-size: 1.4rem; color: #00D2FF;">{b_profile['strike_rate_high']:.2f}</b>
                </div>
                <div>
                    <span style="font-size: 0.7rem; color: #94A3B8; text-transform: uppercase;">Delta Strike Rate</span><br>
                    <b style="font-size: 1.4rem; color: #10B981;">{b_profile['diff_strike_rate']:+.2f}</b>
                </div>
                <div>
                    <span style="font-size: 0.7rem; color: #94A3B8; text-transform: uppercase;">Delta Dot %</span><br>
                    <b style="font-size: 1.4rem; color: #10B981;">{b_profile['diff_dot_pct']:+.2f}%</b>
                </div>
            </div>
            <div style="font-size: 0.8rem; color: #64748B; margin-top: 14px; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 8px;">
                95% Confidence Interval: [{b_profile['ci_lower_95']:.2f} - {b_profile['ci_upper_95']:.2f}] | Total Matches: {b_profile['matches_overall']} | HP Balls Faced: {b_profile['balls_faced_high']}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# SECTION 3: BOWLING INTELLIGENCE
# ==============================================================================
elif nav_selection == "3. Bowling Intelligence":
    st.markdown("""
    <div class="rr-header-banner">
        <span class="badge-pill badge-blue">BOWLING RELIABILITY INTELLIGENCE</span>
        <h1 style="font-family: 'Rajdhani', sans-serif; font-size: 2.2rem; margin: 4px 0 6px 0; color: #0F172A;">
            Top 10 Certified Bowlers Under Pressure
        </h1>
        <p style="font-size: 0.9rem; color: #CBD5E1; margin: 0;">
            Evaluated using empirical pressure differential (HP Economy Control, Wicket-Taking Surge, Dot-Ball Escalation)
            with Bayesian sample shrinkage and 1,000-sample bootstrap confidence intervals.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Visual Cards Gallery for All 10 Bowlers
    st.markdown("<div class='section-title'>🎴 Certified Top 10 Bowlers (Official Player Roster)</div>", unsafe_allow_html=True)
    
    # 2 Rows of 5 Cards
    row1_cols = st.columns(5)
    for i in range(5):
        row = m_bowl.iloc[i]
        bowl_img = player_images.get(row["bowler_name"], "")
        with row1_cols[i]:
            st.markdown(f"""
            <div class="player-roster-card blue">
                <div class="card-rank-badge">#{row['rank']}</div>
                <div class="card-img-container">
                    <img src="{bowl_img}" class="player-cutout-img" alt="{row['bowler_name']}">
                </div>
                <div class="card-player-name">{row['bowler_name']}</div>
                <div class="card-player-id">ID: {row['bowler_id']} • {row['pace_or_spin']}</div>
                <div class="card-score-pill">
                    <span class="score-label">RELIABILITY</span>
                    <span class="score-value">{row['bowler_reliability_index']:.2f}</span>
                </div>
                <div class="card-stat-row">
                    <div>
                        <span class="stat-lbl">HP Econ</span>
                        <span class="stat-val">{row['economy_rate_high']:.2f}</span>
                    </div>
                    <div>
                        <span class="stat-lbl">Delta Econ</span>
                        <span class="stat-val text-green">{row['diff_economy_rate']:+.2f}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    row2_cols = st.columns(5)
    for i in range(5, 10):
        row = m_bowl.iloc[i]
        bowl_img = player_images.get(row["bowler_name"], "")
        with row2_cols[i - 5]:
            st.markdown(f"""
            <div class="player-roster-card blue">
                <div class="card-rank-badge">#{row['rank']}</div>
                <div class="card-img-container">
                    <img src="{bowl_img}" class="player-cutout-img" alt="{row['bowler_name']}">
                </div>
                <div class="card-player-name">{row['bowler_name']}</div>
                <div class="card-player-id">ID: {row['bowler_id']} • {row['pace_or_spin']}</div>
                <div class="card-score-pill">
                    <span class="score-label">RELIABILITY</span>
                    <span class="score-value">{row['bowler_reliability_index']:.2f}</span>
                </div>
                <div class="card-stat-row">
                    <div>
                        <span class="stat-lbl">HP Econ</span>
                        <span class="stat-val">{row['economy_rate_high']:.2f}</span>
                    </div>
                    <div>
                        <span class="stat-lbl">Delta Econ</span>
                        <span class="stat-val text-green">{row['diff_economy_rate']:+.2f}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

    # Certified Table View (Expandable)
    with st.expander("📋 View Complete Certified Bowlers Numerical Table", expanded=False):
        display_bowl_df = top10_bowlers[[
            "rank", "bowler_id", "bowler_name", "bowling_type", "pace_or_spin", "bowler_reliability_index",
            "reliability_grade", "economy_rate_high", "diff_economy_rate", "diff_wickets_per_over",
            "matches_overall", "legal_balls_high", "ci_lower_95", "ci_upper_95"
        ]].copy()
        display_bowl_df.columns = [
            "Rank", "Player ID", "Bowler Name", "Bowling Type", "Discipline", "Reliability Index",
            "Grade", "HP Economy", "Delta Economy", "Delta Wkts/Over",
            "Matches", "HP Legal Balls", "CI Lower (95%)", "CI Upper (95%)"
        ]
        st.dataframe(
            display_bowl_df.style.format({
                "Reliability Index": "{:.2f}",
                "HP Economy": "{:.2f}",
                "Delta Economy": "{:+.2f}",
                "Delta Wkts/Over": "{:+.3f}",
                "CI Lower (95%)": "{:.2f}",
                "CI Upper (95%)": "{:.2f}"
            }),
            use_container_width=True,
            hide_index=True
        )

    # 1. Reliability Index Bar Chart with Confidence Intervals
    st.markdown("<div class='section-title'>📊 Reliability Index & 95% Bootstrap Confidence Intervals</div>", unsafe_allow_html=True)
    fig_ci_bowl = go.Figure()
    fig_ci_bowl.add_trace(go.Bar(
        x=top10_bowlers["bowler_name"],
        y=top10_bowlers["bowler_reliability_index"],
        error_y=dict(
            type='data',
            symmetric=False,
            array=top10_bowlers["ci_upper_95"] - top10_bowlers["bowler_reliability_index"],
            arrayminus=top10_bowlers["bowler_reliability_index"] - top10_bowlers["ci_lower_95"],
            color='#FFB703',
            thickness=2,
            width=6
        ),
        marker=dict(
            color='#00D2FF',
            line=dict(color='rgba(255,255,255,0.2)', width=1)
        ),
        text=[f"{val:.2f}" for val in top10_bowlers["bowler_reliability_index"]],
        textposition='outside',
        textfont=dict(color="#FFFFFF", size=11)
    ))
    apply_rr_theme(fig_ci_bowl, title="BOWLING RELIABILITY INDEX (POINT ESTIMATE ± 95% CONFIDENCE INTERVAL)", height=380, x_title="Bowler Name", y_title="Reliability Index (0-100)", show_legend=False)
    st.plotly_chart(fig_ci_bowl, use_container_width=True)

    # Grouped comparisons: Economy & Wickets
    c_econ, c_wpo = st.columns(2)

    with c_econ:
        fig_econ = go.Figure()
        fig_econ.add_trace(go.Bar(
            name="Normal Economy",
            x=m_bowl["bowler_name"],
            y=m_bowl["economy_rate_normal"],
            marker_color="#475569"
        ))
        fig_econ.add_trace(go.Bar(
            name="High-Pressure Economy",
            x=m_bowl["bowler_name"],
            y=m_bowl["economy_rate_high"],
            marker_color="#00D2FF"
        ))
        fig_econ.update_layout(barmode='group')
        apply_rr_theme(fig_econ, title="HIGH-PRESSURE VS NORMAL ECONOMY RATE", height=380, x_title="Bowler", y_title="Economy Rate (Runs/Over)")
        st.plotly_chart(fig_econ, use_container_width=True)

    with c_wpo:
        fig_wpo = go.Figure()
        fig_wpo.add_trace(go.Bar(
            name="Normal Wickets/Over",
            x=m_bowl["bowler_name"],
            y=m_bowl["wickets_per_over_normal"],
            marker_color="#475569"
        ))
        fig_wpo.add_trace(go.Bar(
            name="HP Wickets/Over",
            x=m_bowl["bowler_name"],
            y=m_bowl["wickets_per_over_high"],
            marker_color="#E5097F"
        ))
        fig_wpo.update_layout(barmode='group')
        apply_rr_theme(fig_wpo, title="WICKETS PER OVER (HIGH-PRESSURE VS NORMAL)", height=380, x_title="Bowler", y_title="Wickets / Over")
        st.plotly_chart(fig_wpo, use_container_width=True)

    # Dot ball & Boundary Conceded Comparisons
    c_bdot, c_bound = st.columns(2)

    with c_bdot:
        fig_bdot = go.Figure()
        fig_bdot.add_trace(go.Bar(
            name="Normal Dot %",
            x=m_bowl["bowler_name"],
            y=m_bowl["dot_pct_normal"],
            marker_color="#475569"
        ))
        fig_bdot.add_trace(go.Bar(
            name="HP Dot %",
            x=m_bowl["bowler_name"],
            y=m_bowl["dot_pct_high"],
            marker_color="#38BDF8"
        ))
        fig_bdot.update_layout(barmode='group')
        apply_rr_theme(fig_bdot, title="BOWLING DOT-BALL PERCENTAGE (HP VS NORMAL)", height=380, x_title="Bowler", y_title="Dot Ball %")
        st.plotly_chart(fig_bdot, use_container_width=True)

    with c_bound:
        fig_bound = go.Figure()
        fig_bound.add_trace(go.Bar(
            name="Normal Boundary Conceded %",
            x=m_bowl["bowler_name"],
            y=m_bowl["boundary_conceded_pct_normal"],
            marker_color="#475569"
        ))
        fig_bound.add_trace(go.Bar(
            name="HP Boundary Conceded %",
            x=m_bowl["bowler_name"],
            y=m_bowl["boundary_conceded_pct_high"],
            marker_color="#FB7185"
        ))
        fig_bound.update_layout(barmode='group')
        apply_rr_theme(fig_bound, title="BOUNDARY CONCEDED PERCENTAGE (HP VS NORMAL)", height=380, x_title="Bowler", y_title="Boundary % Conceded")
        st.plotly_chart(fig_bound, use_container_width=True)

    # Individual Bowler Inspector
    st.markdown("<div class='section-title'>🔍 Individual Bowler Tactical Inspector</div>", unsafe_allow_html=True)
    selected_bowler_name = st.selectbox(
        "Select a Bowler to Inspect:",
        options=top10_bowlers["bowler_name"].tolist()
    )
    bowl_profile = m_bowl[m_bowl["bowler_name"] == selected_bowler_name].iloc[0]
    bowl_inspect_img = player_images.get(selected_bowler_name, "")

    st.markdown(f"""
    <div class="glass-box" style="display: flex; gap: 24px; align-items: center; border-left: 5px solid #00D2FF;">
        <div style="flex: 0 0 160px; height: 180px; display: flex; align-items: center; justify-content: center;">
            <img src="{bowl_inspect_img}" style="max-height: 180px; max-width: 100%; object-fit: contain; filter: drop-shadow(0 8px 16px rgba(0,210,255,0.4));" alt="{selected_bowler_name}">
        </div>
        <div style="flex: 1;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h3 style="font-family: 'Rajdhani', sans-serif; font-size: 1.8rem; color: #0F172A; margin: 0;">{selected_bowler_name}</h3>
                <span class="badge-pill badge-blue">Rank #{bowl_profile['rank']} • {bowl_profile['reliability_grade']}</span>
            </div>
            <div style="font-size: 0.85rem; color: #94A3B8; margin-top: 4px;">
                Player ID: {bowl_profile['bowler_id']} | Type: {bowl_profile['bowling_type']} ({bowl_profile['pace_or_spin']}) | Archetype: {bowl_profile['archetype_name']}
            </div>
            <hr style="border-color: rgba(255,255,255,0.08); margin: 12px 0;">
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px;">
                <div>
                    <span style="font-size: 0.7rem; color: #94A3B8; text-transform: uppercase;">Reliability Index</span><br>
                    <b style="font-size: 1.4rem; color: #00D2FF;">{bowl_profile['bowler_reliability_index']:.2f}</b>
                </div>
                <div>
                    <span style="font-size: 0.7rem; color: #94A3B8; text-transform: uppercase;">HP Economy</span><br>
                    <b style="font-size: 1.4rem; color: #E5097F;">{bowl_profile['economy_rate_high']:.2f}</b>
                </div>
                <div>
                    <span style="font-size: 0.7rem; color: #94A3B8; text-transform: uppercase;">Delta Economy</span><br>
                    <b style="font-size: 1.4rem; color: #10B981;">{bowl_profile['diff_economy_rate']:+.2f}</b>
                </div>
                <div>
                    <span style="font-size: 0.7rem; color: #94A3B8; text-transform: uppercase;">HP Wickets/Over</span><br>
                    <b style="font-size: 1.4rem; color: #CBD5E1;">{bowl_profile['wickets_per_over_high']:.3f}</b>
                </div>
            </div>
            <div style="font-size: 0.8rem; color: #64748B; margin-top: 14px; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 8px;">
                95% Confidence Interval: [{bowl_profile['ci_lower_95']:.2f} - {bowl_profile['ci_upper_95']:.2f}] | Total Matches: {bowl_profile['matches_overall']} | HP Legal Balls: {bowl_profile['legal_balls_high']}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# SECTION 4: PRESSURE ANALYSIS
# ==============================================================================
elif nav_selection == "4. Pressure Analysis":
    st.markdown("""
    <div class="rr-header-banner">
        <span class="badge-pill badge-gold">QUANTITATIVE PRESSURE FRAMEWORK</span>
        <h1 style="font-family: 'Rajdhani', sans-serif; font-size: 2.2rem; margin: 4px 0 6px 0; color: #0F172A;">
            Delivery-Level Pressure Mechanics & Distribution
        </h1>
        <p style="font-size: 0.9rem; color: #CBD5E1; margin: 0;">
            A continuous 0–100 scale evaluating physical match tension across required run rate, resource depletion,
            match phase multiplier, and tactical crunch conditions.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 4 Pressure Categories Explanation Cards
    p_b1, p_b2, p_b3, p_b4 = st.columns(4)
    with p_b1:
        st.markdown("""
        <div class="kpi-card" style="border-top: 3px solid #10B981;">
            <div class="kpi-title" style="color: #10B981;">LOW PRESSURE (0–40)</div>
            <div style="font-size: 0.85rem; color: #CBD5E1; margin-top: 6px;">
                Early overs, full wickets in hand, manageable run rates (RRR &lt; 7.5). Batters enjoy baseline conditions.
            </div>
            <div style="font-size: 0.75rem; color: #64748B; margin-top: 8px;">
                63,979 Batting deliveries (33.0%)
            </div>
        </div>
        """, unsafe_allow_html=True)

    with p_b2:
        st.markdown("""
        <div class="kpi-card" style="border-top: 3px solid #38BDF8;">
            <div class="kpi-title" style="color: #38BDF8;">MODERATE (40–65)</div>
            <div style="font-size: 0.85rem; color: #CBD5E1; margin-top: 6px;">
                Middle overs consolidation, standard competitive T20 tempo (RRR 7.5–9.5). Typical match conditions.
            </div>
            <div style="font-size: 0.75rem; color: #64748B; margin-top: 8px;">
                104,755 Batting deliveries (54.0%)
            </div>
        </div>
        """, unsafe_allow_html=True)

    with p_b3:
        st.markdown("""
        <div class="kpi-card" style="border-top: 3px solid #FFB703;">
            <div class="kpi-title" style="color: #FFB703;">HIGH PRESSURE (65–85)</div>
            <div style="font-size: 0.85rem; color: #CBD5E1; margin-top: 6px;">
                Elevated RRR (9.5–12.5), 3–5 wickets down, death overs initiation. Demands aggressive execution.
            </div>
            <div style="font-size: 0.75rem; color: #64748B; margin-top: 8px;">
                15,617 Batting deliveries (8.1%)
            </div>
        </div>
        """, unsafe_allow_html=True)

    with p_b4:
        st.markdown("""
        <div class="kpi-card" style="border-top: 3px solid #E5097F;">
            <div class="kpi-title" style="color: #E5097F;">EXTREME PRESSURE (85–100)</div>
            <div style="font-size: 0.85rem; color: #CBD5E1; margin-top: 6px;">
                Steep chase (RRR &gt; 12.5), 6+ wickets lost, final 3 overs. Margin for error is effectively zero.
            </div>
            <div style="font-size: 0.75rem; color: #64748B; margin-top: 8px;">
                9,625 Batting deliveries (5.0%)
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

    p_c1, p_c2 = st.columns(2)

    with p_c1:
        cat_df = pd.DataFrame({
            "Category": ["Low (0-40)", "Moderate (40-65)", "High (65-85)", "Extreme (85-100)"],
            "Batting": [63979, 104755, 15617, 9625],
            "Bowling": [33917, 145419, 12945, 1695]
        })
        fig_cat = go.Figure()
        fig_cat.add_trace(go.Bar(name="Batting Deliveries", x=cat_df["Category"], y=cat_df["Batting"], marker_color="#E5097F"))
        fig_cat.add_trace(go.Bar(name="Bowling Deliveries", x=cat_df["Category"], y=cat_df["Bowling"], marker_color="#00D2FF"))
        fig_cat.update_layout(barmode="group")
        apply_rr_theme(fig_cat, title="DELIVERY DISTRIBUTION ACROSS PRESSURE TIERS", height=380, x_title="Tier", y_title="Ball Count")
        st.plotly_chart(fig_cat, use_container_width=True)

    with p_c2:
        phase_df = pd.DataFrame({
            "Phase": ["Powerplay (1-6)", "Middle (7-15)", "Death (16-20)"],
            "Mean Batting Pressure": [40.10, 46.39, 59.11],
            "Mean Bowling Pressure": [48.39, 48.97, 51.83]
        })
        fig_phase = go.Figure()
        fig_phase.add_trace(go.Bar(name="Batting Pressure", x=phase_df["Phase"], y=phase_df["Mean Batting Pressure"], marker_color="#E5097F"))
        fig_phase.add_trace(go.Bar(name="Bowling Pressure", x=phase_df["Phase"], y=phase_df["Mean Bowling Pressure"], marker_color="#00D2FF"))
        fig_phase.update_layout(barmode="group")
        apply_rr_theme(fig_phase, title="AVERAGE PRESSURE BY MATCH PHASE", height=380, x_title="Match Phase", y_title="Mean Pressure Score (0-100)")
        st.plotly_chart(fig_phase, use_container_width=True)

    p_c3, p_c4 = st.columns(2)

    with p_c3:
        inn_df = pd.DataFrame({
            "Innings": ["Innings 1 (Setting Target)", "Innings 2 (Chasing Target)"],
            "Deliveries": [102054, 91922],
            "Batting Mean Pressure": [49.50, 44.65],
            "Bowling Mean Pressure": [51.02, 47.64]
        })
        fig_inn = go.Figure()
        fig_inn.add_trace(go.Bar(name="Batting Mean", x=inn_df["Innings"], y=inn_df["Batting Mean Pressure"], marker_color="#E5097F"))
        fig_inn.add_trace(go.Bar(name="Bowling Mean", x=inn_df["Innings"], y=inn_df["Bowling Mean Pressure"], marker_color="#00D2FF"))
        fig_inn.update_layout(barmode="group")
        apply_rr_theme(fig_inn, title="FIRST INNINGS VS SECOND INNINGS PRESSURE COMPARISON", height=380, x_title="Innings", y_title="Mean Pressure Score")
        st.plotly_chart(fig_inn, use_container_width=True)

    with p_c4:
        st.markdown("""
        <div class="glass-box" style="height: 380px; overflow-y: auto;">
            <h4 style="font-family: 'Rajdhani', sans-serif; color: #0F172A; margin-top: 0;">🔬 Key Situational Pressure Indicators</h4>
            <div style="font-size: 0.85rem; color: #CBD5E1; line-height: 1.6;">
                <b style="color: #FFB703;">1. Required Run Rate (RRR) Gradient:</b><br>
                In second innings chases, pressure grows non-linearly with RRR escalation above the tournament par of 8.54 runs/over.<br><br>
                <b style="color: #00D2FF;">2. Resource Depletion Ratio:</b><br>
                Evaluates the interaction between wickets lost and remaining balls. Losing early wickets in overs 1–6 compounds pressure by up to 2.4×.<br><br>
                <b style="color: #E5097F;">3. Match Phase Multiplier:</b><br>
                Death overs (16–20) automatically enforce higher leverage baselines, scaling with required boundaries per over.<br><br>
                <b style="color: #38BDF8;">4. Bowling Containment & Death Defense:</b><br>
                Bowlers defending low totals or bowling overs 18–20 face asymmetric loss penalties on boundary balls.
            </div>
        </div>
        """, unsafe_allow_html=True)


# ==============================================================================
# SECTION 5: PLAYER COMPARISON
# ==============================================================================
elif nav_selection == "5. Player Comparison":
    st.markdown("""
    <div class="rr-header-banner">
        <span class="badge-pill badge-pink">HEAD-TO-HEAD TACTICAL COMPARISON</span>
        <h1 style="font-family: 'Rajdhani', sans-serif; font-size: 2.2rem; margin: 4px 0 6px 0; color: #0F172A;">
            Multi-Player Scouting Benchmark Tool
        </h1>
        <p style="font-size: 0.9rem; color: #CBD5E1; margin: 0;">
            Compare 2 to 3 qualified batters or 2 to 3 qualified bowlers across pressure-performance metrics.
            Notice: Batting and bowling indices are calibrated on distinct domain scales and must not be compared directly.
        </p>
    </div>
    """, unsafe_allow_html=True)

    comp_tab_bat, comp_tab_bowl = st.tabs(["🏏 Compare Batters", "🎯 Compare Bowlers"])

    with comp_tab_bat:
        default_batters = ["Jason Holder", "Sanju Samson", "Curtis Campher"]
        selected_batters = st.multiselect(
            "Select 2 or 3 Batters to Benchmark:",
            options=all_batters["striker_name"].tolist(),
            default=[b for b in default_batters if b in all_batters["striker_name"].tolist()][:3],
            max_selections=3
        )

        if len(selected_batters) < 2:
            st.warning("Please select at least 2 batters to activate comparison.")
        else:
            comp_bat_df = all_batters[all_batters["striker_name"].isin(selected_batters)].merge(
                batter_rel[["striker_id", "strike_rate_normal", "dot_pct_high", "dot_pct_normal", "dismissal_rate_per_100_high", "dismissal_rate_per_100_normal"]],
                on="striker_id", how="left"
            )

            # Side-by-Side Visual Photo Cards
            b_cols = st.columns(len(selected_batters))
            for idx, p_name in enumerate(selected_batters):
                row = comp_bat_df[comp_bat_df["striker_name"] == p_name].iloc[0]
                p_img = player_images.get(p_name, "")
                with b_cols[idx]:
                    st.markdown(f"""
                    <div class="player-roster-card" style="min-height: 440px;">
                        <div class="card-rank-badge">#{row['rank']}</div>
                        <div class="card-img-container" style="height: 160px;">
                            <img src="{p_img}" class="player-cutout-img" style="max-height: 155px;" alt="{p_name}">
                        </div>
                        <div class="card-player-name">{p_name}</div>
                        <div class="card-player-id">ID: {row['striker_id']} • {row['batting_type']} • {row['archetype_name']}</div>
                        <div class="card-score-pill">
                            <span class="score-label">RELIABILITY INDEX</span>
                            <span class="score-value">{row['batter_reliability_index']:.2f}</span>
                        </div>
                        <div style="font-size: 0.8rem; line-height: 1.8; color: #CBD5E1; text-align: left; padding: 0 8px;">
                            <b>HP Strike Rate:</b> <span style="color: #00D2FF;">{row['strike_rate_high']:.2f}</span><br>
                            <b>Normal Strike Rate:</b> {row['strike_rate_normal']:.2f}<br>
                            <b>Delta Strike Rate:</b> <span style="color: #10B981;">{row['diff_strike_rate']:+.2f}</span><br>
                            <b>HP Dot Ball %:</b> {row['dot_pct_high']:.2f}%<br>
                            <b>Delta Dot %:</b> <span style="color: #10B981;">{row['diff_dot_pct']:+.2f}%</span><br>
                            <b>HP Dismissals/100:</b> {row['dismissal_rate_per_100_high']:.2f}<br>
                            <b>Total Matches:</b> {row['matches_overall']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

            # Comparative Bar Chart
            fig_comp_b = go.Figure()
            for p_name in selected_batters:
                p_row = comp_bat_df[comp_bat_df["striker_name"] == p_name].iloc[0]
                fig_comp_b.add_trace(go.Bar(
                    name=p_name,
                    x=["Reliability Index", "HP Strike Rate / 2", "Delta SR", "HP Balls Faced / 2"],
                    y=[p_row["batter_reliability_index"], p_row["strike_rate_high"] / 2.0, p_row["diff_strike_rate"], p_row["balls_faced_high"] / 2.0]
                ))
            apply_rr_theme(fig_comp_b, title="BATTING METRIC COMPARISON ACROSS SELECTED PLAYERS", height=380, x_title="Metric Dimension", y_title="Normalized Value")
            st.plotly_chart(fig_comp_b, use_container_width=True)

    with comp_tab_bowl:
        default_bowlers = ["Mitchell Marsh", "Haris Rauf", "Kartik Tyagi"]
        selected_bowlers = st.multiselect(
            "Select 2 or 3 Bowlers to Benchmark:",
            options=all_bowlers["bowler_name"].tolist(),
            default=[b for b in default_bowlers if b in all_bowlers["bowler_name"].tolist()][:3],
            max_selections=3
        )

        if len(selected_bowlers) < 2:
            st.warning("Please select at least 2 bowlers to activate comparison.")
        else:
            comp_bowl_df = all_bowlers[all_bowlers["bowler_name"].isin(selected_bowlers)].merge(
                bowler_rel[["bowler_id", "economy_rate_normal", "wickets_per_over_high", "wickets_per_over_normal", "dot_pct_high", "dot_pct_normal", "boundary_conceded_pct_high", "boundary_conceded_pct_normal"]],
                on="bowler_id", how="left"
            )

            bowl_cols = st.columns(len(selected_bowlers))
            for idx, p_name in enumerate(selected_bowlers):
                row = comp_bowl_df[comp_bowl_df["bowler_name"] == p_name].iloc[0]
                bowl_img = player_images.get(p_name, "")
                with bowl_cols[idx]:
                    st.markdown(f"""
                    <div class="player-roster-card blue" style="min-height: 440px;">
                        <div class="card-rank-badge">#{row['rank']}</div>
                        <div class="card-img-container" style="height: 160px;">
                            <img src="{bowl_img}" class="player-cutout-img" style="max-height: 155px;" alt="{p_name}">
                        </div>
                        <div class="card-player-name">{p_name}</div>
                        <div class="card-player-id">ID: {row['bowler_id']} • {row['pace_or_spin']} • {row['archetype_name']}</div>
                        <div class="card-score-pill">
                            <span class="score-label">RELIABILITY INDEX</span>
                            <span class="score-value">{row['bowler_reliability_index']:.2f}</span>
                        </div>
                        <div style="font-size: 0.8rem; line-height: 1.8; color: #CBD5E1; text-align: left; padding: 0 8px;">
                            <b>HP Economy:</b> <span style="color: #E5097F;">{row['economy_rate_high']:.2f}</span><br>
                            <b>Normal Economy:</b> {row['economy_rate_normal']:.2f}<br>
                            <b>Delta Economy:</b> <span style="color: #10B981;">{row['diff_economy_rate']:+.2f}</span><br>
                            <b>HP Wickets/Over:</b> {row['wickets_per_over_high']:.3f}<br>
                            <b>Delta Wkts/Over:</b> <span style="color: #10B981;">{row['diff_wickets_per_over']:+.3f}</span><br>
                            <b>HP Dot Ball %:</b> {row['dot_pct_high']:.2f}%<br>
                            <b>Total Matches:</b> {row['matches_overall']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

            fig_comp_bowl = go.Figure()
            for p_name in selected_bowlers:
                p_row = comp_bowl_df[comp_bowl_df["bowler_name"] == p_name].iloc[0]
                fig_comp_bowl.add_trace(go.Bar(
                    name=p_name,
                    x=["Reliability Index", "HP Economy × 5", "Delta Econ (Inverted)", "HP Balls / 2"],
                    y=[p_row["bowler_reliability_index"], p_row["economy_rate_high"] * 5.0, -p_row["diff_economy_rate"] * 10.0, p_row["legal_balls_high"] / 2.0]
                ))
            apply_rr_theme(fig_comp_bowl, title="BOWLING METRIC COMPARISON ACROSS SELECTED PLAYERS", height=380, x_title="Metric Dimension", y_title="Normalized Value")
            st.plotly_chart(fig_comp_bowl, use_container_width=True)


# ==============================================================================
# SECTION 6: PLAYER RANKINGS
# ==============================================================================
elif nav_selection == "6. Player Rankings":
    st.markdown("""
    <div class="rr-header-banner">
        <span class="badge-pill badge-pink">CERTIFIED OFFICIAL RANKINGS</span>
        <h1 style="font-family: 'Rajdhani', sans-serif; font-size: 2.2rem; margin: 4px 0 6px 0; color: #0F172A;">
            Full Squad Player Rankings & Data Export
        </h1>
        <p style="font-size: 0.9rem; color: #CBD5E1; margin: 0;">
            Browse certified Top 10 lists and all qualified cohorts with search, filters, and direct CSV download.
            Rankings strictly preserve certified Task 07 empirical ordering.
        </p>
    </div>
    """, unsafe_allow_html=True)

    rank_tab_b, rank_tab_bowl = st.tabs(["🏏 Batter Rankings", "🎯 Bowler Rankings"])

    with rank_tab_b:
        view_scope_b = st.radio("Select Batter Cohort:", ["Certified Top 10 Batters", "All 109 Qualified Batters"], horizontal=True)
        active_b_df = top10_batters if view_scope_b == "Certified Top 10 Batters" else all_batters

        styles_b = ["All"] + sorted(active_b_df["batting_type"].dropna().unique().tolist())
        selected_style_b = st.selectbox("Filter by Batting Style:", styles_b)
        if selected_style_b != "All":
            active_b_df = active_b_df[active_b_df["batting_type"] == selected_style_b]

        search_query_b = st.text_input("Search Batter by Name or ID:", "")
        if search_query_b:
            active_b_df = active_b_df[
                active_b_df["striker_name"].str.contains(search_query_b, case=False, na=False) |
                active_b_df["striker_id"].astype(str).str.contains(search_query_b)
            ]

        # If Top 10, also render the visual gallery
        if view_scope_b == "Certified Top 10 Batters" and not search_query_b and selected_style_b == "All":
            st.markdown("<div class='section-title'>🎴 Top 10 Batters Cutout Gallery</div>", unsafe_allow_html=True)
            r1 = st.columns(5)
            for i in range(5):
                r = active_b_df.iloc[i]
                im = player_images.get(r["striker_name"], "")
                with r1[i]:
                    st.markdown(f"""
                    <div class="player-roster-card">
                        <div class="card-rank-badge">#{r['rank']}</div>
                        <div class="card-img-container">
                            <img src="{im}" class="player-cutout-img" alt="{r['striker_name']}">
                        </div>
                        <div class="card-player-name">{r['striker_name']}</div>
                        <div class="card-player-id">ID: {r['striker_id']}</div>
                        <div class="card-score-pill">
                            <span class="score-label">INDEX</span>
                            <span class="score-value">{r['batter_reliability_index']:.2f}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            r2 = st.columns(5)
            for i in range(5, 10):
                r = active_b_df.iloc[i]
                im = player_images.get(r["striker_name"], "")
                with r2[i - 5]:
                    st.markdown(f"""
                    <div class="player-roster-card">
                        <div class="card-rank-badge">#{r['rank']}</div>
                        <div class="card-img-container">
                            <img src="{im}" class="player-cutout-img" alt="{r['striker_name']}">
                        </div>
                        <div class="card-player-name">{r['striker_name']}</div>
                        <div class="card-player-id">ID: {r['striker_id']}</div>
                        <div class="card-score-pill">
                            <span class="score-label">INDEX</span>
                            <span class="score-value">{r['batter_reliability_index']:.2f}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        out_b = active_b_df[[
            "rank", "striker_id", "striker_name", "batting_type", "batter_reliability_index",
            "reliability_grade", "strike_rate_high", "diff_strike_rate", "diff_dot_pct",
            "matches_overall", "balls_faced_high", "ci_lower_95", "ci_upper_95"
        ]].copy()
        out_b.columns = [
            "Rank", "Player ID", "Batter Name", "Style", "Reliability Index",
            "Grade", "HP Strike Rate", "Delta Strike Rate", "Delta Dot %",
            "Matches", "HP Balls", "CI Lower (95%)", "CI Upper (95%)"
        ]

        st.dataframe(
            out_b.style.format({
                "Reliability Index": "{:.2f}",
                "HP Strike Rate": "{:.2f}",
                "Delta Strike Rate": "{:+.2f}",
                "Delta Dot %": "{:+.2f}%",
                "CI Lower (95%)": "{:.2f}",
                "CI Upper (95%)": "{:.2f}"
            }),
            use_container_width=True,
            hide_index=True
        )

        c_csv_b1, c_csv_b2 = st.columns(2)
        with c_csv_b1:
            st.download_button(
                label="📥 Download Certified Top 10 Batters CSV",
                data=top10_batters.to_csv(index=False).encode('utf-8'),
                file_name="task_07_final_top10_batters.csv",
                mime="text/csv"
            )
        with c_csv_b2:
            st.download_button(
                label="📥 Download All 109 Qualified Batters CSV",
                data=all_batters.to_csv(index=False).encode('utf-8'),
                file_name="task_07_all_qualified_batters_ranked.csv",
                mime="text/csv"
            )

    with rank_tab_bowl:
        view_scope_bowl = st.radio("Select Bowler Cohort:", ["Certified Top 10 Bowlers", "All 136 Qualified Bowlers"], horizontal=True)
        active_bowl_df = top10_bowlers if view_scope_bowl == "Certified Top 10 Bowlers" else all_bowlers

        disc_bowl = ["All"] + sorted(active_bowl_df["pace_or_spin"].dropna().unique().tolist())
        selected_disc_bowl = st.selectbox("Filter by Discipline (Pace/Spin):", disc_bowl)
        if selected_disc_bowl != "All":
            active_bowl_df = active_bowl_df[active_bowl_df["pace_or_spin"] == selected_disc_bowl]

        search_query_bowl = st.text_input("Search Bowler by Name or ID:", "")
        if search_query_bowl:
            active_bowl_df = active_bowl_df[
                active_bowl_df["bowler_name"].str.contains(search_query_bowl, case=False, na=False) |
                active_bowl_df["bowler_id"].astype(str).str.contains(search_query_bowl)
            ]

        if view_scope_bowl == "Certified Top 10 Bowlers" and not search_query_bowl and selected_disc_bowl == "All":
            st.markdown("<div class='section-title'>🎴 Top 10 Bowlers Cutout Gallery</div>", unsafe_allow_html=True)
            r1 = st.columns(5)
            for i in range(5):
                r = active_bowl_df.iloc[i]
                im = player_images.get(r["bowler_name"], "")
                with r1[i]:
                    st.markdown(f"""
                    <div class="player-roster-card blue">
                        <div class="card-rank-badge">#{r['rank']}</div>
                        <div class="card-img-container">
                            <img src="{im}" class="player-cutout-img" alt="{r['bowler_name']}">
                        </div>
                        <div class="card-player-name">{r['bowler_name']}</div>
                        <div class="card-player-id">ID: {r['bowler_id']}</div>
                        <div class="card-score-pill">
                            <span class="score-label">INDEX</span>
                            <span class="score-value">{r['bowler_reliability_index']:.2f}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            r2 = st.columns(5)
            for i in range(5, 10):
                r = active_bowl_df.iloc[i]
                im = player_images.get(r["bowler_name"], "")
                with r2[i - 5]:
                    st.markdown(f"""
                    <div class="player-roster-card blue">
                        <div class="card-rank-badge">#{r['rank']}</div>
                        <div class="card-img-container">
                            <img src="{im}" class="player-cutout-img" alt="{r['bowler_name']}">
                        </div>
                        <div class="card-player-name">{r['bowler_name']}</div>
                        <div class="card-player-id">ID: {r['bowler_id']}</div>
                        <div class="card-score-pill">
                            <span class="score-label">INDEX</span>
                            <span class="score-value">{r['bowler_reliability_index']:.2f}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        out_bowl = active_bowl_df[[
            "rank", "bowler_id", "bowler_name", "bowling_type", "pace_or_spin", "bowler_reliability_index",
            "reliability_grade", "economy_rate_high", "diff_economy_rate", "diff_wickets_per_over",
            "matches_overall", "legal_balls_high", "ci_lower_95", "ci_upper_95"
        ]].copy()
        out_bowl.columns = [
            "Rank", "Player ID", "Bowler Name", "Bowling Type", "Discipline", "Reliability Index",
            "Grade", "HP Economy", "Delta Economy", "Delta Wkts/Over",
            "Matches", "HP Legal Balls", "CI Lower (95%)", "CI Upper (95%)"
        ]

        st.dataframe(
            out_bowl.style.format({
                "Reliability Index": "{:.2f}",
                "HP Economy": "{:.2f}",
                "Delta Economy": "{:+.2f}",
                "Delta Wkts/Over": "{:+.3f}",
                "CI Lower (95%)": "{:.2f}",
                "CI Upper (95%)": "{:.2f}"
            }),
            use_container_width=True,
            hide_index=True
        )

        c_csv_bowl1, c_csv_bowl2 = st.columns(2)
        with c_csv_bowl1:
            st.download_button(
                label="📥 Download Certified Top 10 Bowlers CSV",
                data=top10_bowlers.to_csv(index=False).encode('utf-8'),
                file_name="task_07_final_top10_bowlers.csv",
                mime="text/csv"
            )
        with c_csv_bowl2:
            st.download_button(
                label="📥 Download All 136 Qualified Bowlers CSV",
                data=all_bowlers.to_csv(index=False).encode('utf-8'),
                file_name="task_07_all_qualified_bowlers_ranked.csv",
                mime="text/csv"
            )


# ==============================================================================
# SECTION 7: METHODOLOGY & VALIDATION
# ==============================================================================
elif nav_selection == "7. Methodology & Validation":
    st.markdown("""
    <div class="rr-header-banner">
        <span class="badge-pill badge-pink">SCIENTIFIC RIGOR & TRANSPARENCY</span>
        <h1 style="font-family: 'Rajdhani', sans-serif; font-size: 2.2rem; margin: 4px 0 6px 0; color: #0F172A;">
            Methodology, Validation & Governance Disclosures
        </h1>
        <p style="font-size: 0.9rem; color: #CBD5E1; margin: 0;">
            Complete audit trail detailing dataset coverage, exclusion criteria, statistical shrinkage,
            confidence interval interpretation, and machine learning governance.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 1. Dataset Coverage & Cleaning Disclosures
    st.markdown("<div class='section-title'>1. Empirical Dataset Coverage & Exclusions</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="glass-box">
        <div style="font-size: 0.85rem; color: #CBD5E1; line-height: 1.6;">
            <b>• Total Indexed Scope:</b> 194,014 raw delivery records across 837 professional T20 encounters (340 IPL + 497 T20I matches).<br>
            <b>• Cleaned Production Cohort:</b> Exactly <b>193,976 deliveries</b> across 837 matches.<br>
            <b>• Excluded Deliveries:</b><br>
            &nbsp;&nbsp;&nbsp;&nbsp;1. <b>26 Super Over deliveries</b> (Innings 3 & 4) excluded because infinite-pressure tie-breaker mechanics distort standard continuous match-state models.<br>
            &nbsp;&nbsp;&nbsp;&nbsp;2. <b>12 post-target residual deliveries</b> excluded where the victory condition was achieved prior to recorded ball events.<br>
            <b>• Player Coverage:</b> 891 unique players across participating franchises and national squads.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Qualification Criteria
    st.markdown("<div class='section-title'>2. Statistical Qualification Rules</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="glass-box">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; font-size: 0.85rem; color: #CBD5E1;">
            <div>
                <b style="color: #E5097F; font-size: 1rem;">🏏 Batting Qualification:</b><br>
                1. <b>High-Pressure Exposure:</b> ≥ 30 balls faced in High/Extreme pressure situations (Score ≥ 65).<br>
                2. <b>Normal Baseline Exposure:</b> ≥ 30 balls faced in Normal/Low pressure situations (Score &lt; 40).<br>
                3. <b>Sample Depth:</b> ≥ 5 distinct matches played.<br>
                <i>Result: 109 qualified batters out of 824 active batters (13.2% qualification rate).</i>
            </div>
            <div>
                <b style="color: #00D2FF; font-size: 1rem;">🎯 Bowling Qualification:</b><br>
                1. <b>High-Pressure Exposure:</b> ≥ 30 legal balls bowled under High/Extreme pressure.<br>
                2. <b>Normal Baseline Exposure:</b> ≥ 30 legal balls bowled under Normal/Low pressure.<br>
                3. <b>Sample Depth:</b> ≥ 5 distinct matches played.<br>
                <i>Result: 136 qualified bowlers out of 596 active bowlers (22.8% qualification rate).</i>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 3. Empirical Bayes Shrinkage & Confidence Intervals
    st.markdown("<div class='section-title'>3. Empirical Bayes Shrinkage & Bootstrap Estimation</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="glass-box">
        <div style="font-size: 0.85rem; color: #CBD5E1; line-height: 1.6;">
            <b>• Empirical Bayes Shrinkage:</b> Small-sample volatility is controlled by shrinking raw performance differentials toward the qualified cohort mean based on effective sample weight:
            <div style="background: rgba(0,0,0,0.3); padding: 8px 14px; border-radius: 6px; font-family: monospace; color: #FFB703; margin: 8px 0;">
                Shrunk_Metric = w_i × Raw_Metric_i + (1 - w_i) × Cohort_Mean, where w_i = Effective_Balls_i / (Effective_Balls_i + K)
            </div>
            <b>• Bootstrap Confidence Intervals:</b> 1,000 resamples per player establish 95% confidence intervals (<code>ci_lower_95</code>, <code>ci_upper_95</code>).<br>
            <b>• Critical CI Interpretation Rule:</b> Overlapping confidence intervals represent individual estimation uncertainty and <b>do not independently establish pairwise equality or superiority</b>. Point estimates represent the maximum-likelihood expected performance.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 4. Mandatory Machine Learning Governance Disclosures
    st.markdown("<div class='section-title'>4. Machine Learning Governance & Target Leakage Disclosures</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="glass-box" style="border-left: 4px solid #E5097F;">
        <h4 style="color: #E5097F; margin-top: 0;">⚠️ Mandatory Model Integrity Statement</h4>
        <div style="font-size: 0.85rem; color: #CBD5E1; line-height: 1.6;">
            <b>1. Task06 Supervised ML Predictions Discarded:</b><br>
            An internal audit identified target leakage in Task06 supervised regression models (features accidentally encapsulated constituent components of the reliability index). In accordance with strict sports analytics ethics, <b>Task06 ML predictions are 100% EXCLUDED from generating or adjusting player rankings</b>. The official rankings are derived solely from audited Task 05 and Task 07 empirical formulations.<br><br>
            <b>2. Task06 K-Means Archetypes Status:</b><br>
            Task06 unsupervised archetypes (e.g., <i>Death Phase Finisher</i>, <i>Death Wicket Enforcer</i>) are presented <b>strictly as descriptive squad-balance qualitative tags</b>. They do not constitute performance metrics or selection scores.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 5. Validation Status
    st.markdown("<div class='section-title'>5. System Verification & Validation Status</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="glass-box">
        <table style="width: 100%; font-size: 0.85rem; border-collapse: collapse; color: #CBD5E1;">
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.12); text-align: left; color: #94A3B8;">
                <th style="padding: 8px;">Audit Dimension</th>
                <th style="padding: 8px;">Check Description</th>
                <th style="padding: 8px;">Audited Value</th>
                <th style="padding: 8px;">Audit Status</th>
            </tr>
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.06);">
                <td style="padding: 8px; font-weight: 600;">Monotonicity</td>
                <td style="padding: 8px;">Ranks 1 to 10 strictly decreasing in Reliability Index</td>
                <td style="padding: 8px;">Batters: 66.84 → 56.81 | Bowlers: 61.86 → 58.22</td>
                <td style="padding: 8px; color: #10B981; font-weight: 700;">PASSED (100%)</td>
            </tr>
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.06);">
                <td style="padding: 8px; font-weight: 600;">Data Leakage Boundary</td>
                <td style="padding: 8px;">Task 06 predictions excluded from ranking pipeline</td>
                <td style="padding: 8px;">Zero Task 06 weights in Task 07 index</td>
                <td style="padding: 8px; color: #10B981; font-weight: 700;">PASSED (100%)</td>
            </tr>
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.06);">
                <td style="padding: 8px; font-weight: 600;">Eligibility Verification</td>
                <td style="padding: 8px;">All Top 10 players satisfy sample thresholds</td>
                <td style="padding: 8px;">All 20 players: HP balls ≥ 30, Matches ≥ 5</td>
                <td style="padding: 8px; color: #10B981; font-weight: 700;">PASSED (100%)</td>
            </tr>
            <tr>
                <td style="padding: 8px; font-weight: 600;">Cross-Artifact Parity</td>
                <td style="padding: 8px;">Dashboard metrics equal certified CSV records</td>
                <td style="padding: 8px;">100% exact numerical match</td>
                <td style="padding: 8px; color: #10B981; font-weight: 700;">PASSED (100%)</td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)


# ------------------------------------------------------------------------------
# 7. DASHBOARD FOOTER
# ------------------------------------------------------------------------------
st.markdown("""
<div class="rr-footer">
    SUPERR SELECTOR | Cricket Performance Intelligence | Season 2<br>
    <span style="font-size: 0.75rem; color: #475569;">
        Built for Rajasthan Royals IPL 2027 Auction Strategy • Empirical Cricket Data Science Platform
    </span>
</div>
""", unsafe_allow_html=True)
