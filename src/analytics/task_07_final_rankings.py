"""
Task 07: Final Player Ranking & Official Top-10 Selection Engine
Rajasthan Royals SupeRR Selector Season 2 Hackathon

This module implements the certified Master Task 07 ranking execution pipeline.
It generates the official Top-10 Most Reliable Batters and Bowlers based strictly on:
1. Certified Task 05 Empirical Bayes Reliability Indices (descending).
2. Approved deterministic tie-breaking sequence (differentials and absolute pressure rates).
3. Strict filtering for Qualified players only (109 batters, 136 bowlers).
4. Descriptive integration of Task 06 tactical archetypes (quarantine of supervised predictions).

Author: Lead Quantitative Cricket Analyst, Rajasthan Royals Roster Architecture
Date: November 13, 2026
"""

import os
import sys
import logging
import pandas as pd
import numpy as np

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s [%(name)s]: %(message)s"
)
logger = logging.getLogger("Task07FinalRankings")

# Project Directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ANALYTICS_DIR = os.path.join(BASE_DIR, "data", "analytics")
ML_DIR = os.path.join(BASE_DIR, "data", "ml")

# Certified Input File Paths
BATTER_RELIABILITY_PATH = os.path.join(ANALYTICS_DIR, "task_05_batter_reliability.csv")
BOWLER_RELIABILITY_PATH = os.path.join(ANALYTICS_DIR, "task_05_bowler_reliability.csv")
BATTER_ARCHETYPES_PATH = os.path.join(ML_DIR, "task_06_batter_archetypes.csv")
BOWLER_ARCHETYPES_PATH = os.path.join(ML_DIR, "task_06_bowler_archetypes.csv")

# Output File Paths
TOP10_BATTERS_PATH = os.path.join(ANALYTICS_DIR, "task_07_final_top10_batters.csv")
TOP10_BOWLERS_PATH = os.path.join(ANALYTICS_DIR, "task_07_final_top10_bowlers.csv")
ALL_QUALIFIED_BATTERS_PATH = os.path.join(ANALYTICS_DIR, "task_07_all_qualified_batters_ranked.csv")
ALL_QUALIFIED_BOWLERS_PATH = os.path.join(ANALYTICS_DIR, "task_07_all_qualified_bowlers_ranked.csv")


def load_and_validate_inputs():
    """Loads certified Task 05 reliability files and Task 06 descriptive archetypes."""
    logger.info("Loading certified Task 05 reliability outputs...")
    
    if not os.path.exists(BATTER_RELIABILITY_PATH):
        raise FileNotFoundError(f"Missing certified batter reliability: {BATTER_RELIABILITY_PATH}")
    if not os.path.exists(BOWLER_RELIABILITY_PATH):
        raise FileNotFoundError(f"Missing certified bowler reliability: {BOWLER_RELIABILITY_PATH}")
        
    bat_rel = pd.read_csv(BATTER_RELIABILITY_PATH)
    bowl_rel = pd.read_csv(BOWLER_RELIABILITY_PATH)
    
    logger.info(f"Loaded {len(bat_rel)} batter records and {len(bowl_rel)} bowler records.")
    
    # Verify expected populations
    assert len(bat_rel) == 824, f"Expected 824 batters, found {len(bat_rel)}"
    assert len(bowl_rel) == 596, f"Expected 596 bowlers, found {len(bowl_rel)}"
    
    # Load descriptive archetypes
    logger.info("Loading Task 06 tactical archetypes (descriptive only)...")
    bat_arc = pd.read_csv(BATTER_ARCHETYPES_PATH)[["striker_id", "archetype_id", "archetype_name"]]
    bowl_arc = pd.read_csv(BOWLER_ARCHETYPES_PATH)[["bowler_id", "archetype_id", "archetype_name"]]
    
    return bat_rel, bowl_rel, bat_arc, bowl_arc


def rank_batters(bat_rel: pd.DataFrame, bat_arc: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Ranks qualified batters using certified reliability index and approved deterministic tie-breakers.
    
    Primary Sort: batter_reliability_index [DESC]
    Tie-Breaker 1: shrunk_diff_strike_rate [DESC]
    Tie-Breaker 2: shrunk_diff_dot_pct [ASC]
    Tie-Breaker 3: strike_rate_high [DESC]
    """
    logger.info("Ranking Qualified Batters...")
    
    # Filter strictly for Qualified players
    qual_bat = bat_rel[bat_rel["eligibility_tier"] == "Qualified"].copy()
    assert len(qual_bat) == 109, f"Expected 109 qualified batters, found {len(qual_bat)}"
    
    # Merge descriptive archetypes
    qual_bat = qual_bat.merge(bat_arc, on="striker_id", how="left")
    
    # Deterministic multi-tier sort
    # Note: higher reliability index is better; higher shrunk diff SR is better; lower shrunk diff dot% is better; higher strike_rate_high is better
    sorted_bat = qual_bat.sort_values(
        by=[
            "batter_reliability_index",
            "shrunk_diff_strike_rate",
            "shrunk_diff_dot_pct",
            "strike_rate_high"
        ],
        ascending=[False, False, True, False]
    ).reset_index(drop=True)
    
    # Assign continuous 1-based ranks
    sorted_bat.insert(0, "rank", range(1, len(sorted_bat) + 1))
    
    # Define canonical column order
    cols = [
        "rank",
        "striker_id",
        "striker_name",
        "batting_type",
        "eligibility_tier",
        "batter_reliability_index",
        "raw_composite_z",
        "reliability_grade",
        "archetype_id",
        "archetype_name",
        "balls_faced_high",
        "balls_faced_normal",
        "effective_balls",
        "matches_overall",
        "strike_rate_high",
        "diff_strike_rate",
        "diff_dot_pct",
        "diff_dismissal_rate_per_100",
        "shrunk_diff_strike_rate",
        "shrunk_diff_dot_pct",
        "shrunk_diff_dismissal_rate",
        "shrunk_strike_rate_high",
        "ci_lower_95",
        "ci_upper_95",
        "ci_std_error"
    ]
    
    ranked_all = sorted_bat[cols].copy()
    top10 = ranked_all.head(10).copy()
    
    logger.info("Successfully ranked 109 qualified batters and selected Top 10.")
    return ranked_all, top10


def rank_bowlers(bowl_rel: pd.DataFrame, bowl_arc: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Ranks qualified bowlers using certified reliability index and approved deterministic tie-breakers.
    
    Primary Sort: bowler_reliability_index [DESC]
    Tie-Breaker 1: shrunk_diff_economy_rate [ASC] (lower economy diff under pressure is superior)
    Tie-Breaker 2: shrunk_diff_wickets_per_over [DESC] (higher wicket rate diff under pressure is superior)
    Tie-Breaker 3: economy_rate_high [ASC] (lower absolute economy under pressure is superior)
    """
    logger.info("Ranking Qualified Bowlers...")
    
    # Filter strictly for Qualified players
    qual_bowl = bowl_rel[bowl_rel["eligibility_tier"] == "Qualified"].copy()
    assert len(qual_bowl) == 136, f"Expected 136 qualified bowlers, found {len(qual_bowl)}"
    
    # Merge descriptive archetypes
    qual_bowl = qual_bowl.merge(bowl_arc, on="bowler_id", how="left")
    
    # Deterministic multi-tier sort
    # Note: higher reliability index is better; lower shrunk diff econ is better; higher shrunk diff wkt is better; lower economy_rate_high is better
    sorted_bowl = qual_bowl.sort_values(
        by=[
            "bowler_reliability_index",
            "shrunk_diff_economy_rate",
            "shrunk_diff_wickets_per_over",
            "economy_rate_high"
        ],
        ascending=[False, True, False, True]
    ).reset_index(drop=True)
    
    # Assign continuous 1-based ranks
    sorted_bowl.insert(0, "rank", range(1, len(sorted_bowl) + 1))
    
    # Define canonical column order
    cols = [
        "rank",
        "bowler_id",
        "bowler_name",
        "bowling_type",
        "pace_or_spin",
        "eligibility_tier",
        "bowler_reliability_index",
        "raw_composite_z",
        "reliability_grade",
        "archetype_id",
        "archetype_name",
        "legal_balls_high",
        "legal_balls_normal",
        "effective_balls",
        "matches_overall",
        "economy_rate_high",
        "diff_economy_rate",
        "diff_wickets_per_over",
        "diff_dot_pct",
        "shrunk_diff_economy_rate",
        "shrunk_diff_wickets_per_over",
        "shrunk_diff_dot_pct",
        "shrunk_economy_rate_high",
        "ci_lower_95",
        "ci_upper_95",
        "ci_std_error"
    ]
    
    ranked_all = sorted_bowl[cols].copy()
    top10 = ranked_all.head(10).copy()
    
    logger.info("Successfully ranked 136 qualified bowlers and selected Top 10.")
    return ranked_all, top10


def export_rankings(bat_all: pd.DataFrame, bat_top10: pd.DataFrame, bowl_all: pd.DataFrame, bowl_top10: pd.DataFrame):
    """Exports official ranked CSV datasets."""
    logger.info("Exporting Task 07 ranking CSVs...")
    
    bat_top10.to_csv(TOP10_BATTERS_PATH, index=False)
    bowl_top10.to_csv(TOP10_BOWLERS_PATH, index=False)
    bat_all.to_csv(ALL_QUALIFIED_BATTERS_PATH, index=False)
    bowl_all.to_csv(ALL_QUALIFIED_BOWLERS_PATH, index=False)
    
    logger.info(f"Saved: {TOP10_BATTERS_PATH} ({len(bat_top10)} rows)")
    logger.info(f"Saved: {TOP10_BOWLERS_PATH} ({len(bowl_top10)} rows)")
    logger.info(f"Saved: {ALL_QUALIFIED_BATTERS_PATH} ({len(bat_all)} rows)")
    logger.info(f"Saved: {ALL_QUALIFIED_BOWLERS_PATH} ({len(bowl_all)} rows)")


def validate_rankings(bat_all: pd.DataFrame, bat_top10: pd.DataFrame, bowl_all: pd.DataFrame, bowl_top10: pd.DataFrame):
    """Performs rigorous post-execution validation checks."""
    logger.info("Executing comprehensive validation assertions...")
    
    # Check 1: Record counts
    assert len(bat_top10) == 10, f"Expected 10 top batters, found {len(bat_top10)}"
    assert len(bowl_top10) == 10, f"Expected 10 top bowlers, found {len(bowl_top10)}"
    assert len(bat_all) == 109, f"Expected 109 qualified batters, found {len(bat_all)}"
    assert len(bowl_all) == 136, f"Expected 136 qualified bowlers, found {len(bowl_all)}"
    
    # Check 2: Continuous ranks 1 to N
    assert list(bat_top10["rank"]) == list(range(1, 11)), "Batters top 10 ranks non-continuous"
    assert list(bowl_top10["rank"]) == list(range(1, 11)), "Bowlers top 10 ranks non-continuous"
    assert list(bat_all["rank"]) == list(range(1, 110)), "Batters all ranks non-continuous"
    assert list(bowl_all["rank"]) == list(range(1, 137)), "Bowlers all ranks non-continuous"
    
    # Check 3: Unique IDs
    assert bat_top10["striker_id"].nunique() == 10, "Duplicate IDs in top 10 batters"
    assert bowl_top10["bowler_id"].nunique() == 10, "Duplicate IDs in top 10 bowlers"
    assert bat_all["striker_id"].nunique() == 109, "Duplicate IDs in all qualified batters"
    assert bowl_all["bowler_id"].nunique() == 136, "Duplicate IDs in all qualified bowlers"
    
    # Check 4: Qualified tiers only
    assert (bat_top10["eligibility_tier"] == "Qualified").all(), "Non-qualified batter found in top 10"
    assert (bowl_top10["eligibility_tier"] == "Qualified").all(), "Non-qualified bowler found in top 10"
    
    # Check 5: Top 10 matches first 10 rows of all qualified
    pd.testing.assert_frame_equal(bat_top10, bat_all.head(10))
    pd.testing.assert_frame_equal(bowl_top10, bowl_all.head(10))
    
    # Check 6: Monotonically non-increasing reliability indices
    assert bat_all["batter_reliability_index"].is_monotonic_decreasing, "Batter index not monotonic decreasing"
    assert bowl_all["bowler_reliability_index"].is_monotonic_decreasing, "Bowler index not monotonic decreasing"
    
    logger.info("ALL VALIDATION ASSERTIONS PASSED WITH ZERO VIOLATIONS.")


def main():
    logger.info("=== STARTING MASTER TASK 07 FINAL RANKING EXECUTION ===")
    bat_rel, bowl_rel, bat_arc, bowl_arc = load_and_validate_inputs()
    
    bat_all, bat_top10 = rank_batters(bat_rel, bat_arc)
    bowl_all, bowl_top10 = rank_bowlers(bowl_rel, bowl_arc)
    
    export_rankings(bat_all, bat_top10, bowl_all, bowl_top10)
    validate_rankings(bat_all, bat_top10, bowl_all, bowl_top10)
    
    print("\n" + "=" * 90)
    print("OFFICIAL TOP 10 MOST RELIABLE BATTERS (Rajasthan Royals SupeRR Selector Season 2)")
    print("=" * 90)
    for _, r in bat_top10.iterrows():
        print(f"Rank {r['rank']:2d} | ID: {r['striker_id']:5d} | {r['striker_name']:<22} | "
              f"Index: {r['batter_reliability_index']:5.2f} | Raw Z: {r['raw_composite_z']:+5.3f} | "
              f"Archetype: {r['archetype_name']:<28} | CI: [{r['ci_lower_95']:.2f}, {r['ci_upper_95']:.2f}]")
              
    print("\n" + "=" * 90)
    print("OFFICIAL TOP 10 MOST RELIABLE BOWLERS (Rajasthan Royals SupeRR Selector Season 2)")
    print("=" * 90)
    for _, r in bowl_top10.iterrows():
        print(f"Rank {r['rank']:2d} | ID: {r['bowler_id']:5d} | {r['bowler_name']:<22} | "
              f"Index: {r['bowler_reliability_index']:5.2f} | Raw Z: {r['raw_composite_z']:+5.3f} | "
              f"Archetype: {r['archetype_name']:<28} | CI: [{r['ci_lower_95']:.2f}, {r['ci_upper_95']:.2f}]")
    print("=" * 90 + "\n")
    logger.info("=== MASTER TASK 07 RANKING EXECUTION COMPLETE ===")


if __name__ == "__main__":
    main()

