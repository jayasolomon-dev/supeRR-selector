"""
SUPERR SELECTOR - Matchup Simulator
Granular head-to-head tactical intelligence between batters and bowlers.
"""

import streamlit as st
import pandas as pd

from src.config import get_raw_data_directory, COLORS
from src.data.loader import load_all_cricket_data
from src.data.preprocessor import preprocess_ball_by_ball
from src.features.metrics import (
    compute_head_to_head_matchup,
    compute_batter_metrics,
    compute_bowler_metrics,
)
from src.visualization.charts import plot_head_to_head_breakdown
from src.utils.helpers import render_player_avatar_html, format_cricket_metric

st.set_page_config(page_title="Matchup Simulator | SUPERR SELECTOR", page_icon="⚡", layout="wide")

st.title("⚡ Head-to-Head Matchup Simulator")
st.caption("Tactical batter vs bowler confrontations extracted from empirical ball-by-ball deliveries.")

raw_dir = get_raw_data_directory()
data = load_all_cricket_data(str(raw_dir))
df_balls_raw = data["ball_by_ball"]

if df_balls_raw.empty:
    st.error("No delivery data available.")
    st.stop()

df_balls = preprocess_ball_by_ball(df_balls_raw)

# Extract Batter and Bowler options
batters = (
    df_balls[["striker_id", "striker_name"]]
    .drop_duplicates()
    .sort_values("striker_name")
)
bowlers = (
    df_balls[["bowler_id", "bowler_name"]]
    .drop_duplicates()
    .sort_values("bowler_name")
)

batter_dict = dict(zip(batters["striker_id"].astype(str), batters["striker_name"]))
bowler_dict = dict(zip(bowlers["bowler_id"].astype(str), bowlers["bowler_name"]))

col_b, col_w = st.columns(2)

with col_b:
    st.markdown("### 🏏 Select Batter")
    sel_batter_id = st.selectbox(
        "Batter",
        options=list(batter_dict.keys()),
        format_func=lambda pid: batter_dict[pid],
        key="sel_batter",
    )
    batter_name = batter_dict[sel_batter_id]

with col_w:
    st.markdown("### 🎯 Select Bowler")
    sel_bowler_id = st.selectbox(
        "Bowler",
        options=list(bowler_dict.keys()),
        format_func=lambda pid: bowler_dict[pid],
        key="sel_bowler",
    )
    bowler_name = bowler_dict[sel_bowler_id]

st.markdown("---")

# Compute Head to Head
matchup = compute_head_to_head_matchup(df_balls, sel_batter_id, sel_bowler_id)

st.subheader(f"⚔️ {batter_name} vs {bowler_name}")

if matchup["has_data"]:
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric("Balls Faced", matchup["balls_faced"])
    m2.metric("Runs Scored", matchup["runs_scored"])
    m3.metric("Dismissals", matchup["dismissals"])
    m4.metric("Strike Rate", format_cricket_metric(matchup["strike_rate"]))
    m5.metric("Dot Balls", matchup["dots"])
    m6.metric("Boundaries (4s / 6s)", f"{matchup['fours']} / {matchup['sixes']}")

    chart_col, table_col = st.columns([1, 1])
    with chart_col:
        st.plotly_chart(plot_head_to_head_breakdown(matchup), use_container_width=True)
    with table_col:
        st.markdown("#### Historical Delivery Log")
        deliv_df = matchup["deliveries"][
            ["overid", "over_ball_num", "runs", "is_four", "is_six", "is_bowler_wicket", "dismissal_type", "phase"]
        ].rename(columns={
            "overid": "Over",
            "over_ball_num": "Ball",
            "runs": "Runs",
            "is_four": "4",
            "is_six": "6",
            "is_bowler_wicket": "Out",
            "dismissal_type": "Dismissal",
            "phase": "Phase",
        })
        st.dataframe(deliv_df, use_container_width=True, hide_index=True)
else:
    st.warning(f"No direct deliveries recorded between {batter_name} and {bowler_name} in this tournament dataset.")
    st.info("Comparing career baseline efficiency between the two players:")
    
    b_stats = compute_batter_metrics(df_balls, min_balls=1)
    w_stats = compute_bowler_metrics(df_balls, min_balls=1)
    
    b_row = b_stats[b_stats["striker_id"].astype(str) == sel_batter_id]
    w_row = w_stats[w_stats["bowler_id"].astype(str) == sel_bowler_id]
    
    comp1, comp2 = st.columns(2)
    with comp1:
        st.markdown(f"**{batter_name} Career Baseline:**")
        if not b_row.empty:
            st.write(f"- Total Runs: {b_row.iloc[0]['runs']}")
            st.write(f"- Strike Rate: {b_row.iloc[0]['strike_rate']}")
            st.write(f"- Boundary %: {b_row.iloc[0]['boundary_percent']}%")
    with comp2:
        st.markdown(f"**{bowler_name} Career Baseline:**")
        if not w_row.empty:
            st.write(f"- Total Wickets: {w_row.iloc[0]['wickets']}")
            st.write(f"- Economy Rate: {w_row.iloc[0]['economy']}")
            st.write(f"- Dot Ball %: {w_row.iloc[0]['dot_ball_percent']}%")

