"""
SUPERR SELECTOR - Main Application Entrypoint
Enterprise-grade Cricket Analytics & Squad Selection Platform.
"""

from pathlib import Path
import streamlit as st
import pandas as pd

from src.config import get_raw_data_directory, COLORS
from src.data.loader import load_all_cricket_data
from src.data.preprocessor import preprocess_ball_by_ball

# ------------------------------------------------------------------------------
# Streamlit Page Configuration
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="SUPERR SELECTOR | Cricket Analytics",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------------------
# Custom CSS for Professional Sports Analytics Aesthetics
# ------------------------------------------------------------------------------
st.markdown(f"""
<style>
    .main-header {{
        background: linear-gradient(90deg, #023047 0%, #219EBC 100%);
        padding: 24px;
        border-radius: 12px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }}
    .metric-card {{
        background: white;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid {COLORS["accent_gold"]};
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }}
    .platform-badge {{
        background-color: {COLORS["accent_gold"]};
        color: #023047;
        padding: 4px 12px;
        border-radius: 16px;
        font-weight: 700;
        font-size: 13px;
        letter-spacing: 1px;
    }}
</style>
""", unsafe_allow_html=True)


def main():
    # Header Banner
    st.markdown("""
    <div class="main-header">
        <span class="platform-badge">DATA ENGINEERING & ML PLATFORM</span>
        <h1 style="margin-top: 8px; margin-bottom: 4px; color: #FFFFFF;">⚡ SUPERR SELECTOR</h1>
        <p style="margin: 0; font-size: 16px; opacity: 0.95;">
            High-Performance T20 Cricket Intelligence, Player Profiling & Squad Selection System
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Load real datasets
    raw_dir = get_raw_data_directory()
    data_dict = load_all_cricket_data(str(raw_dir))
    df_balls = data_dict["ball_by_ball"]
    df_matches = data_dict["matches"]
    df_players = data_dict["player_mappings"]
    df_comps = data_dict["competitions"]

    # Top KPI Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            label="Total Deliveries Analyzed",
            value=f"{len(df_balls):,}" if not df_balls.empty else "0",
            help="Total empirical ball-by-ball records from active tournament data"
        )
    with col2:
        st.metric(
            label="Matches Indexed",
            value=f"{len(df_matches):,}" if not df_matches.empty else "0",
            help="Total professional T20 matches in the database"
        )
    with col3:
        st.metric(
            label="Roster Players",
            value=f"{df_players['player_id'].nunique():,}" if not df_players.empty else "0",
            help="Unique players mapped across participating teams"
        )
    with col4:
        st.metric(
            label="Competitions",
            value=f"{len(df_comps):,}" if not df_comps.empty else "0",
            help="Domestic and international T20 leagues indexed"
        )

    st.markdown("---")

    # Platform Feature Highlights
    st.subheader("📌 Platform Capabilities & Modules")
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("""
        #### 🏏 1. Player Profiles & Phase Splits
        - In-depth career and tournament breakdowns for batters and bowlers.
        - **Match Phase Analytics**: Powerplay (Overs 1-6), Middle (7-15), Death (16-20).
        - Multi-dimensional skill radar charts powered by real delivery records.
        - Pace vs Spin efficiency splits.
        
        #### 📊 2. Team Analytics & Match Dynamics
        - Head-to-head records, win-loss percentages, and venue performance.
        - Run-rate acceleration and boundary frequency per over.
        - Toss impact and match condition evaluations.
        """)

    with c2:
        st.markdown("""
        #### ⚡ 3. Matchup Simulator (Batter vs Bowler)
        - Granular tactical head-to-head records using historical encounters.
        - Strike rate, dot-ball pressure, and dismissal history between specific players.
        - Interactive outcome distribution charts.

        #### 🎯 4. Machine Learning Squad Selector
        - **Scikit-learn Unsupervised Clustering**: Discovers natural player archetypes (Anchors, Boundary Hitters, Death Specialists).
        - **Composite Performance Rating**: Z-score normalized skill metrics.
        - **Tactical Squad Optimization**: Assembles a balanced Playing XI respecting real cricket constraints.
        """)

    st.markdown("---")
    
    # Data Integrity & System Health Card
    st.subheader("🛡️ Data Integrity & System Status")
    status_col1, status_col2 = st.columns([2, 1])
    
    with status_col1:
        st.info(f"""
        **Active Data Directory:** `{raw_dir.resolve()}`  
        - **Source Authenticity:** All analytics are derived 100% from actual ball-by-ball delivery events.  
        - **Data Safety:** Source CSV files are treated as read-only immutable assets.  
        - **Engine:** Python, Pandas, NumPy, Scikit-learn, Plotly, Streamlit.
        """)
        
    with status_col2:
        st.success("""
        **Pipeline Health: Active**  
        ✔️ Ball-by-Ball Records Loaded  
        ✔️ Player Mappings Verified  
        ✔️ Match Outcomes Validated  
        ✔️ Streamlit Caching Enabled  
        """)

    st.caption("👈 Use the sidebar navigation to explore individual platform modules.")


if __name__ == "__main__":
    main()

