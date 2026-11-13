"""
SUPERR SELECTOR - Plotly Interactive Visualizations
Publication-ready interactive cricket analytics charts with a modern aesthetic.
"""

from typing import Dict, List, Optional
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from src.config import COLORS, PLOTLY_TEMPLATE


def plot_player_radar_chart(
    metrics_dict: Dict[str, float], player_name: str
) -> go.Figure:
    """
    Renders an interactive 5-axis radar chart displaying a player's multi-dimensional profile.
    All attributes are 0-100 normalized scores derived from empirical data.
    """
    categories = list(metrics_dict.keys())
    values = list(metrics_dict.values())
    
    # Close the radar polygon
    categories.append(categories[0])
    values.append(values[0])

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill="toself",
        fillcolor="rgba(33, 158, 188, 0.35)",
        line=dict(color=COLORS["accent_blue"], width=2.5),
        name=player_name,
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=10, color="#666"),
                gridcolor="#E0E0E0",
            ),
            angularaxis=dict(
                tickfont=dict(size=11, color="#222", face="bold" if hasattr(dict, "face") else None),
                gridcolor="#E0E0E0",
            )
        ),
        showlegend=False,
        title=dict(
            text=f"Tactical Profile: {player_name}",
            font=dict(size=15, color=COLORS["dark_blue"]),
            x=0.5,
        ),
        margin=dict(l=40, r=40, t=50, b=40),
        template=PLOTLY_TEMPLATE,
    )
    return fig


def plot_phase_breakdown_bar(df_phase: pd.DataFrame, is_batting: bool = True) -> go.Figure:
    """
    Generates a grouped bar chart displaying metrics across Powerplay, Middle, and Death phases.
    """
    if df_phase.empty:
        fig = go.Figure()
        fig.add_annotation(text="No phase data recorded for this player", showarrow=False)
        return fig

    fig = go.Figure()
    if is_batting:
        fig.add_trace(go.Bar(
            x=df_phase["phase"],
            y=df_phase["runs"],
            name="Runs Scored",
            marker_color=COLORS["dark_blue"],
            text=df_phase["runs"],
            textposition="auto",
        ))
        fig.add_trace(go.Bar(
            x=df_phase["phase"],
            y=df_phase["strike_rate"],
            name="Strike Rate",
            marker_color=COLORS["accent_gold"],
            text=df_phase["strike_rate"],
            textposition="auto",
        ))
        title_text = "Phase Analysis: Runs Scored & Strike Rate"
    else:
        fig.add_trace(go.Bar(
            x=df_phase["phase"],
            y=df_phase["wickets"],
            name="Wickets Taken",
            marker_color=COLORS["accent_red"],
            text=df_phase["wickets"],
            textposition="auto",
        ))
        fig.add_trace(go.Bar(
            x=df_phase["phase"],
            y=df_phase["economy"],
            name="Economy Rate",
            marker_color=COLORS["accent_blue"],
            text=df_phase["economy"],
            textposition="auto",
        ))
        title_text = "Phase Analysis: Wickets & Economy Rate"

    fig.update_layout(
        barmode="group",
        title=dict(text=title_text, font=dict(size=14, color=COLORS["dark_blue"])),
        xaxis_title="Match Phase",
        yaxis_title="Metric Value",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=30, r=30, t=60, b=30),
        template=PLOTLY_TEMPLATE,
    )
    return fig


def plot_pca_cluster_scatter(df_clustered: pd.DataFrame) -> go.Figure:
    """
    Visualizes Scikit-learn PCA dimensions and player clusters.
    """
    if "pca_x" not in df_clustered.columns or df_clustered.empty:
        return go.Figure()

    fig = px.scatter(
        df_clustered,
        x="pca_x",
        y="pca_y",
        color="archetype",
        hover_name="player_name",
        hover_data={
            "runs": True,
            "strike_rate": True,
            "batting_average": True,
            "boundary_percent": True,
            "pca_x": False,
            "pca_y": False,
        },
        title="Scikit-learn Player Archetype Clustering (PCA Projection)",
        labels={"pca_x": "Principal Component 1 (Aggression & Boundaries)", "pca_y": "Principal Component 2 (Consistency & Average)"},
        color_discrete_sequence=[COLORS["dark_blue"], COLORS["accent_gold"], COLORS["accent_blue"]],
        template=PLOTLY_TEMPLATE,
    )
    fig.update_traces(marker=dict(size=9, opacity=0.85, line=dict(width=1, color="DarkSlateGrey")))
    fig.update_layout(margin=dict(l=30, r=30, t=50, b=30))
    return fig


def plot_strike_rate_vs_average(df_batters: pd.DataFrame) -> go.Figure:
    """
    Interactive scatter chart comparing Strike Rate against Batting Average with quadrant benchmarks.
    """
    if df_batters.empty:
        return go.Figure()

    mean_sr = df_batters["strike_rate"].median()
    mean_avg = df_batters["batting_average"].median()

    fig = px.scatter(
        df_batters,
        x="strike_rate",
        y="batting_average",
        size="runs",
        color="boundary_percent",
        hover_name="player_name",
        hover_data={"strike_rate": ":.1f", "batting_average": ":.1f", "runs": True, "balls_faced": True},
        title="T20 Batting Efficiency: Strike Rate vs Batting Average",
        labels={"strike_rate": "Batting Strike Rate", "batting_average": "Batting Average", "boundary_percent": "Boundary %"},
        color_continuous_scale="Viridis",
        template=PLOTLY_TEMPLATE,
    )

    # Reference lines for median quadrant splitting
    fig.add_vline(x=mean_sr, line_dash="dash", line_color="gray", annotation_text=f"Median SR ({mean_sr:.1f})")
    fig.add_hline(y=mean_avg, line_dash="dash", line_color="gray", annotation_text=f"Median Avg ({mean_avg:.1f})")
    fig.update_layout(margin=dict(l=30, r=30, t=50, b=30))
    return fig


def plot_head_to_head_breakdown(matchup_dict: Dict) -> go.Figure:
    """
    Creates an outcome breakdown donut chart for batter vs bowler confrontations.
    """
    if not matchup_dict.get("has_data", False):
        fig = go.Figure()
        fig.add_annotation(text="No historical deliveries between these two players", showarrow=False)
        return fig

    dots = matchup_dict["dots"]
    fours = matchup_dict["fours"]
    sixes = matchup_dict["sixes"]
    dismissals = matchup_dict["dismissals"]
    total_balls = matchup_dict["balls_faced"]
    singles_twos = max(0, total_balls - dots - fours - sixes)

    labels = ["Dot Balls", "Singles / Running", "Fours (4s)", "Sixes (6s)", "Dismissals"]
    values = [dots, singles_twos, fours, sixes, dismissals]
    colors = ["#CED4DA", "#4D908E", "#F9C74F", "#F94144", "#577590"]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.45,
        marker=dict(colors=colors),
        textinfo="label+value",
    )])

    fig.update_layout(
        title=dict(text=f"Delivery Outcome Distribution ({total_balls} balls)", font=dict(size=14)),
        margin=dict(l=20, r=20, t=40, b=20),
        template=PLOTLY_TEMPLATE,
    )
    return fig


def plot_team_runrate_by_over(df_overs: pd.DataFrame, team_name: str) -> go.Figure:
    """
    Renders run rate progression by over number.
    """
    if df_overs.empty:
        return go.Figure()

    fig = px.bar(
        df_overs,
        x="overid",
        y="runs",
        color="phase",
        title=f"Scoring Velocity by Over: {team_name}",
        labels={"overid": "Over Number (1 - 20)", "runs": "Total Runs Scored", "phase": "Phase"},
        color_discrete_map={
            "Powerplay": COLORS["accent_gold"],
            "Middle": COLORS["accent_blue"],
            "Death": COLORS["accent_red"],
        },
        template=PLOTLY_TEMPLATE,
    )
    fig.update_layout(xaxis=dict(tickmode="linear", tick0=1, dtick=1), margin=dict(l=30, r=30, t=50, b=30))
    return fig

