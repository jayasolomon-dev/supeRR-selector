"""
SUPERR SELECTOR - Scikit-learn Squad Selector & Player Clustering
Machine learning player clustering and balanced squad composition optimizer.
"""

from pathlib import Path
import streamlit as st
import pandas as pd

from src.config import get_raw_data_directory, TABLES_OUTPUT_DIR, COLORS
from src.data.loader import load_all_cricket_data
from src.data.preprocessor import preprocess_ball_by_ball
from src.features.metrics import compute_batter_metrics, compute_bowler_metrics
from src.models.selector import (
    cluster_player_archetypes,
    compute_composite_player_rating,
    optimize_squad_selection,
)
from src.visualization.charts import (
    plot_pca_cluster_scatter,
    plot_strike_rate_vs_average,
)

st.set_page_config(page_title="Squad Selector | SUPERR SELECTOR", page_icon="🎯", layout="wide")

st.title("🎯 SUPERR SELECTOR: ML Squad Optimizer")
st.caption("Unsupervised player archetype clustering and optimal Playing XI selection engine.")

raw_dir = get_raw_data_directory()
data = load_all_cricket_data(str(raw_dir))
df_balls_raw = data["ball_by_ball"]
df_p11 = data["playing_eleven"]

if df_balls_raw.empty:
    st.error("No ball-by-ball delivery data available.")
    st.stop()

df_balls = preprocess_ball_by_ball(df_balls_raw)

# Sidebar Constraints
st.sidebar.header("⚙️ Selection Constraints")
min_bat_balls = st.sidebar.slider("Min Batting Balls Faced", min_value=10, max_value=100, value=30, step=5)
min_bowl_balls = st.sidebar.slider("Min Bowling Balls Bowled", min_value=12, max_value=120, value=36, step=6)
n_clusters = st.sidebar.slider("Number of Player Archetypes (K-Means)", min_value=2, max_value=5, value=3)

# Compute Features
df_batters = compute_batter_metrics(df_balls, min_balls=min_bat_balls)
df_bowlers = compute_bowler_metrics(df_balls, min_balls=min_bowl_balls)

# Rename columns to standard player_id
df_batters = df_batters.rename(columns={"striker_id": "player_id"})
df_bowlers = df_bowlers.rename(columns={"bowler_id": "player_id"})

tab_clustering, tab_squad = st.tabs(["🤖 Scikit-learn Player Clustering", "🏏 Playing XI Selection Optimizer"])

with tab_clustering:
    st.subheader("Clustering Tactical Player Archetypes")
    st.markdown("""
    Unsupervised **K-Means Clustering** and **Principal Component Analysis (PCA)** 
    group players by empirical scoring patterns into tactical archetypes:
    - **Anchors / Accumulators**: High average, low dot-ball percentage, build the innings.
    - **Dynamic Stroke Makers**: Balanced strike rate and boundary frequency.
    - **Power Finishers / Boundary Hitters**: High boundary %, elevated strike rate, lower balls-per-dismissal.
    """)

    if not df_batters.empty and len(df_batters) >= n_clusters:
        df_clustered, kmeans_model, pca_model = cluster_player_archetypes(df_batters, n_clusters=n_clusters)
        
        c1, c2 = st.columns([1, 1])
        with c1:
            st.plotly_chart(plot_pca_cluster_scatter(df_clustered), use_container_width=True)
        with c2:
            st.plotly_chart(plot_strike_rate_vs_average(df_clustered), use_container_width=True)

        st.markdown("#### Clustered Batting Pool")
        cols_show = ["player_name", "archetype", "runs", "strike_rate", "batting_average", "boundary_percent", "dot_ball_percent"]
        st.dataframe(df_clustered[cols_show], use_container_width=True, hide_index=True)
    else:
        st.warning("Insufficient player pool with current minimum balls filter. Reduce the threshold in the sidebar.")

with tab_squad:
    st.subheader("Optimal Playing XI Generator")
    
    # Identify known wicketkeepers from playing_eleven table
    wk_ids = set()
    if not df_p11.empty and "is_wk" in df_p11.columns:
        wk_ids = set(df_p11[df_p11["is_wk"]]["player_id"].unique())

    # Compute ratings
    rated_batters, rated_bowlers = compute_composite_player_rating(df_batters, df_bowlers)

    col_ctrl1, col_ctrl2, col_ctrl3 = st.columns(3)
    with col_ctrl1:
        min_batters = st.number_input("Specialist Batters", min_value=3, max_value=6, value=4)
    with col_ctrl2:
        min_allrounders = st.number_input("All-Rounders", min_value=1, max_value=4, value=2)
    with col_ctrl3:
        min_bowlers = st.number_input("Specialist Bowlers", min_value=3, max_value=5, value=4)

    if st.button("🚀 Run SupeRR Selection Optimizer", type="primary"):
        with st.spinner("Solving tactical squad constraints..."):
            squad_df = optimize_squad_selection(
                df_batters_rated=rated_batters,
                df_bowlers_rated=rated_bowlers,
                wk_ids=wk_ids,
                min_batters=int(min_batters),
                min_bowlers=int(min_bowlers),
                min_allrounders=int(min_allrounders),
                target_squad_size=11,
            )

        if not squad_df.empty:
            st.success("✅ Optimal Playing XI assembled successfully!")
            
            # Display Squad Card
            display_cols = [
                "squad_role", "player_name", "batting_rating", "runs", 
                "strike_rate", "bowling_rating", "wickets", "economy", "pace_or_spin"
            ]
            clean_display = squad_df[[c for c in display_cols if c in squad_df.columns]].rename(columns={
                "squad_role": "Role",
                "player_name": "Player",
                "batting_rating": "Bat Rating",
                "runs": "Runs",
                "strike_rate": "SR",
                "bowling_rating": "Bowl Rating",
                "wickets": "Wkts",
                "economy": "Econ",
                "pace_or_spin": "Bowling Type",
            })

            st.dataframe(clean_display, use_container_width=True, hide_index=True)

            # Squad Diagnostics
            st.markdown("#### ⚖️ Squad Balance Diagnostics")
            d1, d2, d3 = st.columns(3)
            with d1:
                avg_bat = squad_df["batting_rating"].mean()
                st.metric("Avg Batting Firepower", f"{avg_bat:.1f} / 100")
            with d2:
                avg_bowl = squad_df["bowling_rating"].mean()
                st.metric("Avg Bowling Threat", f"{avg_bowl:.1f} / 100")
            with d3:
                pace_cnt = (squad_df["pace_or_spin"] == "Pace").sum()
                spin_cnt = (squad_df["pace_or_spin"] == "Spin").sum()
                st.metric("Pace vs Spin Options", f"{pace_cnt} Pace / {spin_cnt} Spin")

            # Export capability
            csv_bytes = clean_display.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Selected Squad (CSV)",
                data=csv_bytes,
                file_name="superr_selector_playing_xi.csv",
                mime="text/csv",
            )
            
            # Save copy to outputs/tables
            TABLES_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            output_path = TABLES_OUTPUT_DIR / "selected_playing_xi.csv"
            clean_display.to_csv(output_path, index=False)
            st.caption(f"Squad artifact also cached to `{output_path}`")
        else:
            st.warning("Could not assemble a complete squad under the given filters. Please relax the minimum balls constraints.")

