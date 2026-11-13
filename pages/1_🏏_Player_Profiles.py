"""
SUPERR SELECTOR - Player Profiles & Tactical Breakdown
Comprehensive player analysis using empirical delivery data.
"""

from pathlib import Path
import streamlit as st
import pandas as pd

from src.config import get_raw_data_directory, COLORS
from src.data.loader import load_all_cricket_data
from src.data.preprocessor import preprocess_ball_by_ball
from src.features.metrics import (
    compute_batter_metrics,
    compute_bowler_metrics,
    compute_player_phase_splits,
)
from src.visualization.charts import (
    plot_player_radar_chart,
    plot_phase_breakdown_bar,
)
from src.utils.helpers import (
    get_player_image_path,
    render_player_avatar_html,
    format_cricket_metric,
)

st.set_page_config(page_title="Player Profiles | SUPERR SELECTOR", page_icon="🏏", layout="wide")

st.title("🏏 Player Performance & Phase Profile")
st.caption("Deep-dive tactical profiling calculated from ball-by-ball tournament records.")

# Load data
raw_dir = get_raw_data_directory()
data = load_all_cricket_data(str(raw_dir))
df_balls_raw = data["ball_by_ball"]
df_players = data["player_mappings"]

if df_balls_raw.empty:
    st.error("No ball-by-ball delivery data available.")
    st.stop()

# Preprocess deliveries
df_balls = preprocess_ball_by_ball(df_balls_raw)

# Get unique players list
if not df_players.empty:
    player_options = (
        df_players[["player_id", "player_name"]]
        .drop_duplicates()
        .sort_values("player_name")
    )
    player_dict = dict(zip(player_options["player_id"].astype(str), player_options["player_name"]))
else:
    strikers = df_balls[["striker_id", "striker_name"]].drop_duplicates()
    player_dict = dict(zip(strikers["striker_id"].astype(str), strikers["striker_name"]))

# Player Selection
selected_id = st.selectbox(
    "Select Player to Profile",
    options=list(player_dict.keys()),
    format_func=lambda pid: f"{player_dict.get(pid, 'Unknown')} (ID: {pid})",
)

player_name = player_dict.get(selected_id, "Selected Player")

# Header card with Player Photo / Avatar
header_c1, header_c2 = st.columns([1, 4])
with header_c1:
    photo_path = get_player_image_path(selected_id, player_name)
    if photo_path:
        st.image(str(photo_path), width=120)
    else:
        st.markdown(render_player_avatar_html(player_name, size_px=100), unsafe_allow_html=True)

with header_c2:
    st.subheader(player_name)
    
    # Check player styles from data
    bat_style_series = df_balls[df_balls["striker_id"] == selected_id]["batting_type"].dropna()
    bowl_style_series = df_balls[df_balls["bowler_id"] == selected_id]["bowling_type"].dropna()
    
    bat_style = bat_style_series.iloc[0] if not bat_style_series.empty else "N/A"
    bowl_style = bowl_style_series.iloc[0] if not bowl_style_series.empty else "N/A"
    
    st.markdown(f"**Batting Style:** {bat_style} | **Bowling Style:** {bowl_style}")

st.markdown("---")

# Compute Batting & Bowling Stats
df_bat = compute_batter_metrics(df_balls, min_balls=1)
df_bowl = compute_bowler_metrics(df_balls, min_balls=1)

p_bat = df_bat[df_bat["striker_id"].astype(str) == selected_id]
p_bowl = df_bowl[df_bowl["bowler_id"].astype(str) == selected_id]

# KPI Metric Cards
tab_bat, tab_bowl = st.tabs(["🏏 Batting Breakdown", "🎯 Bowling Breakdown"])

with tab_bat:
    if not p_bat.empty:
        bat_row = p_bat.iloc[0]
        k1, k2, k3, k4, k5 = st.columns(5)
        k1.metric("Total Runs", f"{int(bat_row['runs'])}")
        k2.metric("Innings", f"{int(bat_row['innings'])}")
        k3.metric("Batting Avg", format_cricket_metric(bat_row['batting_average']))
        k4.metric("Strike Rate", format_cricket_metric(bat_row['strike_rate']))
        k5.metric("Boundaries (4s / 6s)", f"{int(bat_row['fours'])} / {int(bat_row['sixes'])}")
    else:
        st.info("No recorded batting deliveries for this player.")

with tab_bowl:
    if not p_bowl.empty:
        bowl_row = p_bowl.iloc[0]
        b1, b2, b3, b4, b5 = st.columns(5)
        b1.metric("Wickets", f"{int(bowl_row['wickets'])}")
        b2.metric("Overs", str(bowl_row['overs_str']))
        b3.metric("Economy", format_cricket_metric(bowl_row['economy']))
        b4.metric("Bowling Avg", format_cricket_metric(bowl_row['bowling_average']))
        b5.metric("Dot Ball %", f"{format_cricket_metric(bowl_row['dot_ball_percent'])}%")
    else:
        st.info("No recorded bowling deliveries for this player.")

st.markdown("### ⏱️ Phase Performance & Radar Profiling")
vis_col1, vis_col2 = st.columns([1, 1])

# Phase splits
phase_data = compute_player_phase_splits(df_balls, selected_id)

with vis_col1:
    st.markdown("#### Phase Scoring Distribution")
    if not phase_data["batting"].empty:
        st.plotly_chart(plot_phase_breakdown_bar(phase_data["batting"], is_batting=True), use_container_width=True)
    elif not phase_data["bowling"].empty:
        st.plotly_chart(plot_phase_breakdown_bar(phase_data["bowling"], is_batting=False), use_container_width=True)
    else:
        st.info("Insufficient phase data for chart rendering.")

with vis_col2:
    st.markdown("#### Multi-Axis Skill Radar")
    if not p_bat.empty:
        bat_row = p_bat.iloc[0]
        radar_metrics = {
            "Strike Rate": min(100.0, (bat_row["strike_rate"] / 180.0) * 100.0),
            "Average": min(100.0, (bat_row["batting_average"] / 50.0) * 100.0),
            "Boundary %": min(100.0, bat_row["boundary_percent"]),
            "Dot Ball Resistance": max(0.0, 100.0 - bat_row["dot_ball_percent"]),
            "Inning Volume": min(100.0, (bat_row["innings"] / 20.0) * 100.0),
        }
        st.plotly_chart(plot_player_radar_chart(radar_metrics, player_name), use_container_width=True)
    elif not p_bowl.empty:
        bowl_row = p_bowl.iloc[0]
        radar_metrics = {
            "Wicket Threat": min(100.0, (bowl_row["wickets"] / 25.0) * 100.0),
            "Economy Control": max(0.0, min(100.0, (12.0 - bowl_row["economy"]) * 12.5)),
            "Dot Ball %": min(100.0, bowl_row["dot_ball_percent"]),
            "Volume (Overs)": min(100.0, (bowl_row["legal_balls"] / 240.0) * 100.0),
            "Bowling SR": max(0.0, min(100.0, (30.0 - (bowl_row["bowling_strike_rate"] or 30)) * 4.0)),
        }
        st.plotly_chart(plot_player_radar_chart(radar_metrics, player_name), use_container_width=True)
    else:
        st.info("Insufficient deliveries to generate radar profile.")

