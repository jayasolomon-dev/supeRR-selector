"""
SUPERR SELECTOR - Team Analytics & Match Dynamics
Team-level win metrics, phase control, and scoring acceleration.
"""

import streamlit as st
import pandas as pd

from src.config import get_raw_data_directory, COLORS
from src.data.loader import load_all_cricket_data
from src.data.preprocessor import preprocess_ball_by_ball
from src.features.metrics import compute_team_performance_summary
from src.visualization.charts import plot_team_runrate_by_over

st.set_page_config(page_title="Team Analysis | SUPERR SELECTOR", page_icon="📊", layout="wide")

st.title("📊 Team Performance & Match Dynamics")
st.caption("Aggregated match outcomes, scoring rates, and tactical phase metrics.")

raw_dir = get_raw_data_directory()
data = load_all_cricket_data(str(raw_dir))
df_matches = data["matches"]
df_balls_raw = data["ball_by_ball"]

if df_matches.empty:
    st.error("No match records found.")
    st.stop()

df_balls = preprocess_ball_by_ball(df_balls_raw)

# Team Standings / Win Rate Summary
st.subheader("🏆 Team Standings & Win Rates")
summary_df = compute_team_performance_summary(df_matches, df_balls)
st.dataframe(
    summary_df.rename(columns={
        "team_name": "Team",
        "matches_played": "Matches",
        "wins": "Wins",
        "win_rate_percent": "Win %",
    }),
    use_container_width=True,
    hide_index=True,
)

st.markdown("---")

# Deep-dive on individual team
st.subheader("🔍 Deep-Dive: Team Scoring Patterns")
teams_list = sorted(summary_df["team_name"].unique()) if not summary_df.empty else []

if teams_list:
    selected_team = st.selectbox("Select Team to Inspect", options=teams_list)
    
    # Filter deliveries where this team was batting
    # Find team_ids associated with this team name
    team_matches = df_matches[(df_matches["home_team"] == selected_team) | (df_matches["away_team"] == selected_team)]
    home_ids = team_matches[team_matches["home_team"] == selected_team]["home_team_id"].unique()
    away_ids = team_matches[team_matches["away_team"] == selected_team]["away_team_id"].unique()
    target_team_ids = set(home_ids).union(set(away_ids))
    
    team_balls = df_balls[df_balls["batting_team_id"].isin(target_team_ids)]
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown(f"#### Scoring Velocity by Over: {selected_team}")
        if not team_balls.empty:
            over_runs = (
                team_balls.groupby(["overid", "phase"], observed=True)["runs"]
                .sum()
                .reset_index()
                .sort_values("overid")
            )
            st.plotly_chart(plot_team_runrate_by_over(over_runs, selected_team), use_container_width=True)
        else:
            st.info("No delivery records found for this team.")
            
    with col2:
        st.markdown(f"#### Leading Run Contributors: {selected_team}")
        if not team_balls.empty:
            top_batters = (
                team_balls.groupby("striker_name")["runs"]
                .sum()
                .reset_index()
                .sort_values("runs", ascending=False)
                .head(10)
            )
            st.dataframe(
                top_batters.rename(columns={"striker_name": "Batter", "runs": "Total Runs"}),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No batting records available.")

