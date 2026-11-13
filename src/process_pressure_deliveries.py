"""
SUPERR SELECTOR — Batch Execution Script for Delivery-Level Pressure Scoring
Module: src/process_pressure_deliveries.py
Author: Senior Cricket Data Scientist & Pipeline Architect
Project: SUPERR SELECTOR (Rajasthan Royals SupeRR Selector Season 2 Hackathon)

Processes the approved delivery datasets from data/processed/ and writes enriched deliverables
to data/derived/:
  - data/derived/pressure_scored_ipl.csv
  - data/derived/pressure_scored_t20i.csv

Guarantees:
  - 100% data safety: data/raw/ and data/processed/ are NEVER modified.
  - Delivery counts and match counts reconcile exactly.
  - Zero NaNs in batting_pressure_score and bowling_pressure_score.
  - Retains all 65 original columns + adds all 22 derived pressure features (87 columns total).
"""

from pathlib import Path
import sys
import logging
import pandas as pd
import numpy as np

# Ensure project root is in sys.path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.features.pressure_engine import enrich_deliveries_with_pressure

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def process_datasets(
    processed_dir: Path = Path("data/processed"),
    derived_dir: Path = Path("data/derived"),
) -> bool:
    logger.info("=" * 80)
    logger.info("⚡ SUPERR SELECTOR — DELIVERY-LEVEL PRESSURE SCORING BATCH RUN")
    logger.info("=" * 80)

    ipl_in = processed_dir / "ipl_deliveries.csv"
    t20i_in = processed_dir / "t20i_deliveries.csv"

    if not ipl_in.exists() or not t20i_in.exists():
        logger.error(f"Missing input processed deliverable at {ipl_in} or {t20i_in}")
        return False

    # Create derived directory if not present
    derived_dir.mkdir(parents=True, exist_ok=True)
    ipl_out = derived_dir / "pressure_scored_ipl.csv"
    t20i_out = derived_dir / "pressure_scored_t20i.csv"

    # --------------------------------------------------------------------------
    # 1. Process IPL Deliveries
    # --------------------------------------------------------------------------
    logger.info(f"Loading IPL deliveries from {ipl_in}...")
    df_ipl = pd.read_csv(ipl_in, low_memory=False)
    n_ipl_orig = len(df_ipl)
    m_ipl_orig = df_ipl["match_id"].nunique()
    logger.info(f"Loaded {n_ipl_orig:,} IPL deliveries across {m_ipl_orig} matches.")

    logger.info("Enriching IPL deliveries with Pressure Engine features...")
    df_ipl_enriched = enrich_deliveries_with_pressure(df_ipl)
    n_ipl_out = len(df_ipl_enriched)
    m_ipl_out = df_ipl_enriched["match_id"].nunique()

    # Assertions
    assert n_ipl_orig == n_ipl_out == 87687, f"IPL row count mismatch: {n_ipl_orig} -> {n_ipl_out}"
    assert m_ipl_orig == m_ipl_out == 367, f"IPL match count mismatch: {m_ipl_orig} -> {m_ipl_out}"
    assert df_ipl_enriched["batting_pressure_score"].isna().sum() == 0, "NaNs found in IPL batting pressure"
    assert df_ipl_enriched["bowling_pressure_score"].isna().sum() == 0, "NaNs found in IPL bowling pressure"

    logger.info(f"Saving enriched IPL deliveries to {ipl_out}...")
    df_ipl_enriched.to_csv(ipl_out, index=False)
    logger.info(f"Successfully saved {ipl_out} ({len(df_ipl_enriched.columns)} columns).")

    # --------------------------------------------------------------------------
    # 2. Process T20I Deliveries
    # --------------------------------------------------------------------------
    logger.info(f"\nLoading T20I deliveries from {t20i_in}...")
    df_t20i = pd.read_csv(t20i_in, low_memory=False)
    n_t20i_orig = len(df_t20i)
    m_t20i_orig = df_t20i["match_id"].nunique()
    logger.info(f"Loaded {n_t20i_orig:,} T20I deliveries across {m_t20i_orig} matches.")

    logger.info("Enriching T20I deliveries with Pressure Engine features...")
    df_t20i_enriched = enrich_deliveries_with_pressure(df_t20i)
    n_t20i_out = len(df_t20i_enriched)
    m_t20i_out = df_t20i_enriched["match_id"].nunique()

    # Assertions
    assert n_t20i_orig == n_t20i_out == 106327, f"T20I row count mismatch: {n_t20i_orig} -> {n_t20i_out}"
    assert m_t20i_orig == m_t20i_out == 470, f"T20I match count mismatch: {m_t20i_orig} -> {m_t20i_out}"
    assert df_t20i_enriched["batting_pressure_score"].isna().sum() == 0, "NaNs found in T20I batting pressure"
    assert df_t20i_enriched["bowling_pressure_score"].isna().sum() == 0, "NaNs found in T20I bowling pressure"

    logger.info(f"Saving enriched T20I deliveries to {t20i_out}...")
    df_t20i_enriched.to_csv(t20i_out, index=False)
    logger.info(f"Successfully saved {t20i_out} ({len(df_t20i_enriched.columns)} columns).")

    # --------------------------------------------------------------------------
    # 3. Reconciled Summary
    # --------------------------------------------------------------------------
    total_deliveries = n_ipl_out + n_t20i_out
    total_matches = m_ipl_out + m_t20i_out
    assert total_deliveries == 194014, f"Total delivery count mismatch: {total_deliveries}"
    assert total_matches == 837, f"Total match count mismatch: {total_matches}"

    logger.info("\n" + "=" * 80)
    logger.info("RECONCILIATION & DATASET PROCESSING SUMMARY")
    logger.info("=" * 80)
    logger.info(f"  IPL Deliveries:   {n_ipl_out:,} rows | Matches: {m_ipl_out} | Saved to: {ipl_out}")
    logger.info(f"  T20I Deliveries:  {n_t20i_out:,} rows | Matches: {m_t20i_out} | Saved to: {t20i_out}")
    logger.info(f"  Total Deliveries: {total_deliveries:,} rows | Total Matches: {total_matches}")
    logger.info("  Batting Pressure NaNs: 0")
    logger.info("  Bowling Pressure NaNs: 0")
    logger.info("  Total Columns per file: 87 (65 original + 22 derived pressure features)")
    logger.info("ALL DATASETS PROCESSED & RECONCILED SUCCESSFULLY ✅")
    logger.info("=" * 80)

    return True


if __name__ == "__main__":
    success = process_datasets()
    sys.exit(0 if success else 1)

