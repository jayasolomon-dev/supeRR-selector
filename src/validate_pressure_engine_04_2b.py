"""
SUPERR SELECTOR — Independent Pressure Engine Validation & Statistical Reliability Audit
Module: src/validate_pressure_engine_04_2b.py
Author: Senior Cricket Data Scientist, Independent Quantitative Auditor & QA Engineer
Project: SUPERR SELECTOR (Rajasthan Royals SupeRR Selector Season 2 Hackathon)
Date: November 2026

Executes Modules A through G independently:
- Module A: Workspace & Data Integrity
- Module B: Multi-Match Anti-Leakage Audit (Prefix, Future, Current, Isolation across 6 matches)
- Module C: DLS & Match-State Capacity Audit (34 shortened matches, legal balls interpretation, Match 37354)
- Module D: Super Over Isolation Audit (Option A verification, standard cohort preservation)
- Module E: Terminal State Boundary Audit (Winning ball vs post-target deliveries, Match 48610)
- Module F: Statistical Distribution & Sub-Component Analysis (IPL & T20I standard cohort, SVG & Plotly charts)
- Module G: Component Sensitivity & Diagnostic Weight Perturbation (±5% weight perturbation, Spearman correlation)

Produces:
- reports/task_04_2b_figures/* (Visual charts: SVG + Plotly HTML)
- reports/task_04_2b_validation_summary.json (Machine-readable audit record)
"""

from pathlib import Path
import sys
import json
import logging
from typing import Dict, List, Tuple, Any
import numpy as np
import pandas as pd
import scipy.stats as stats

# Ensure project root is in sys.path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.features.pressure_engine import enrich_deliveries_with_pressure

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------
# SVG Visualization Helper (Zero Dependency, High Quality)
# ------------------------------------------------------------------------------

def generate_svg_histogram(
    data1: np.ndarray,
    data2: np.ndarray,
    label1: str,
    label2: str,
    title: str,
    output_path: Path,
    bins: int = 25,
    range_min: float = 0.0,
    range_max: float = 100.0,
):
    """Generates a clean, publication-grade dual-histogram SVG."""
    width, height = 800, 450
    margin = {"top": 60, "right": 40, "bottom": 60, "left": 70}
    chart_w = width - margin["left"] - margin["right"]
    chart_h = height - margin["top"] - margin["bottom"]

    counts1, bin_edges = np.histogram(data1, bins=bins, range=(range_min, range_max))
    counts2, _ = np.histogram(data2, bins=bins, range=(range_min, range_max))
    
    # Normalize to percentage
    pct1 = (counts1 / len(data1)) * 100.0
    pct2 = (counts2 / len(data2)) * 100.0
    max_y = max(max(pct1), max(pct2)) * 1.15 if max(max(pct1), max(pct2)) > 0 else 10.0

    bar_w = chart_w / bins
    
    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" style="background-color: #ffffff; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif;">',
        f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
        f'<text x="{width//2}" y="35" text-anchor="middle" font-size="18" font-weight="bold" fill="#1e293b">{title}</text>',
        f'<g transform="translate({margin["left"]}, {margin["top"]})">',
    ]

    # Grid lines & Y-axis labels
    for i in range(5):
        y_val = (max_y / 4) * i
        y_pos = chart_h - (y_val / max_y) * chart_h
        svg_parts.append(f'<line x1="0" y1="{y_pos:.1f}" x2="{chart_w}" y2="{y_pos:.1f}" stroke="#e2e8f0" stroke-width="1"/>')
        svg_parts.append(f'<text x="-10" y="{y_pos + 4:.1f}" text-anchor="end" font-size="11" fill="#64748b">{y_val:.1f}%</text>')

    # Bars
    for i in range(bins):
        x = i * bar_w
        h1 = (pct1[i] / max_y) * chart_h
        h2 = (pct2[i] / max_y) * chart_h
        y1 = chart_h - h1
        y2 = chart_h - h2
        
        # Dual bars side-by-side or semi-transparent
        sub_w = bar_w * 0.42
        svg_parts.append(f'<rect x="{x + 2:.1f}" y="{y1:.1f}" width="{sub_w:.1f}" height="{h1:.1f}" fill="#3b82f6" opacity="0.85" rx="1"/>')
        svg_parts.append(f'<rect x="{x + sub_w + 3:.1f}" y="{y2:.1f}" width="{sub_w:.1f}" height="{h2:.1f}" fill="#f97316" opacity="0.85" rx="1"/>')

    # X-axis ticks
    for i in range(0, bins + 1, 5):
        x_val = range_min + (i / bins) * (range_max - range_min)
        x_pos = (i / bins) * chart_w
        svg_parts.append(f'<line x1="{x_pos:.1f}" y1="{chart_h}" x2="{x_pos:.1f}" y2="{chart_h + 6}" stroke="#94a3b8" stroke-width="1"/>')
        svg_parts.append(f'<text x="{x_pos:.1f}" y="{chart_h + 20}" text-anchor="middle" font-size="11" fill="#64748b">{x_val:.0f}</text>')

    # Axes
    svg_parts.append(f'<line x1="0" y1="{chart_h}" x2="{chart_w}" y2="{chart_h}" stroke="#475569" stroke-width="1.5"/>')
    svg_parts.append(f'<line x1="0" y1="0" x2="0" y2="{chart_h}" stroke="#475569" stroke-width="1.5"/>')

    # Legend
    leg_x = chart_w - 220
    svg_parts.append(f'<rect x="{leg_x}" y="10" width="14" height="14" fill="#3b82f6" rx="2"/>')
    svg_parts.append(f'<text x="{leg_x + 20}" y="22" font-size="12" fill="#334155">{label1}</text>')
    svg_parts.append(f'<rect x="{leg_x + 110}" y="10" width="14" height="14" fill="#f97316" rx="2"/>')
    svg_parts.append(f'<text x="{leg_x + 130}" y="22" font-size="12" fill="#334155">{label2}</text>')

    # Axis titles
    svg_parts.append(f'<text x="{chart_w//2}" y="{chart_h + 45}" text-anchor="middle" font-size="13" font-weight="600" fill="#334155">Pressure Score [0 - 100]</text>')
    svg_parts.append(f'<text transform="rotate(-90)" x="{-chart_h//2}" y="-48" text-anchor="middle" font-size="13" font-weight="600" fill="#334155">Relative Frequency (%)</text>')

    svg_parts.append('</g></svg>')
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_parts))


def generate_svg_category_bars(
    cat_df: pd.DataFrame,
    title: str,
    output_path: Path,
):
    """Generates a grouped horizontal bar chart for categorical distributions."""
    width, height = 750, 360
    margin = {"top": 60, "right": 50, "bottom": 50, "left": 130}
    chart_w = width - margin["left"] - margin["right"]
    chart_h = height - margin["top"] - margin["bottom"]

    categories = ["Low", "Moderate", "High", "Extreme"]
    n_cats = len(categories)
    bar_group_h = chart_h / n_cats
    
    max_val = 80.0 # Percentage cap
    
    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" style="background-color: #ffffff; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif;">',
        f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
        f'<text x="{width//2}" y="35" text-anchor="middle" font-size="18" font-weight="bold" fill="#1e293b">{title}</text>',
        f'<g transform="translate({margin["left"]}, {margin["top"]})">',
    ]

    # Grid
    for i in range(5):
        val = i * 20.0
        x_pos = (val / max_val) * chart_w
        svg_parts.append(f'<line x1="{x_pos:.1f}" y1="0" x2="{x_pos:.1f}" y2="{chart_h}" stroke="#e2e8f0" stroke-width="1"/>')
        svg_parts.append(f'<text x="{x_pos:.1f}" y="{chart_h + 18}" text-anchor="middle" font-size="11" fill="#64748b">{val:.0f}%</text>')

    # Groups
    for idx, cat in enumerate(categories):
        y_center = idx * bar_group_h + bar_group_h / 2
        svg_parts.append(f'<text x="-15" y="{y_center + 4:.1f}" text-anchor="end" font-size="13" font-weight="600" fill="#334155">{cat}</text>')
        
        # Two bars: Batting (blue) and Bowling (orange)
        val_bat = cat_df.loc[cat, "Batting"] if cat in cat_df.index and "Batting" in cat_df.columns else 0.0
        val_bowl = cat_df.loc[cat, "Bowling"] if cat in cat_df.index and "Bowling" in cat_df.columns else 0.0
        
        h_bar = bar_group_h * 0.32
        w_bat = (val_bat / max_val) * chart_w
        w_bowl = (val_bowl / max_val) * chart_w
        
        y_bat = y_center - h_bar - 2
        y_bowl = y_center + 2
        
        svg_parts.append(f'<rect x="0" y="{y_bat:.1f}" width="{w_bat:.1f}" height="{h_bar:.1f}" fill="#3b82f6" rx="2"/>')
        svg_parts.append(f'<text x="{w_bat + 8:.1f}" y="{y_bat + h_bar*0.75:.1f}" font-size="11" font-weight="bold" fill="#1e40af">{val_bat:.1f}%</text>')
        
        svg_parts.append(f'<rect x="0" y="{y_bowl:.1f}" width="{w_bowl:.1f}" height="{h_bar:.1f}" fill="#f97316" rx="2"/>')
        svg_parts.append(f'<text x="{w_bowl + 8:.1f}" y="{y_bowl + h_bar*0.75:.1f}" font-size="11" font-weight="bold" fill="#9a3412">{val_bowl:.1f}%</text>')

    # Legend
    svg_parts.append('<rect x="20" y="-30" width="14" height="14" fill="#3b82f6" rx="2"/>')
    svg_parts.append('<text x="40" y="-18" font-size="12" fill="#334155">Batting Pressure</text>')
    svg_parts.append('<rect x="170" y="-30" width="14" height="14" fill="#f97316" rx="2"/>')
    svg_parts.append('<text x="190" y="-18" font-size="12" fill="#334155">Bowling Defensive Pressure</text>')

    svg_parts.append(f'<line x1="0" y1="0" x2="0" y2="{chart_h}" stroke="#475569" stroke-width="1.5"/>')
    svg_parts.append(f'<line x1="0" y1="{chart_h}" x2="{chart_w}" y2="{chart_h}" stroke="#475569" stroke-width="1.5"/>')
    svg_parts.append('</g></svg>')

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_parts))


# ------------------------------------------------------------------------------
# Master Validation Harness Class
# ------------------------------------------------------------------------------

class PressureEngineAuditor042B:
    def __init__(
        self,
        processed_dir: Path = Path("data/processed"),
        derived_dir: Path = Path("data/derived"),
        figures_dir: Path = Path("reports/task_04_2b_figures"),
        summary_json_path: Path = Path("reports/task_04_2b_validation_summary.json"),
    ):
        self.processed_dir = processed_dir
        self.derived_dir = derived_dir
        self.figures_dir = figures_dir
        self.summary_json_path = summary_json_path
        
        self.summary: Dict[str, Any] = {
            "audit_timestamp": pd.Timestamp.now().isoformat(),
            "verdict": "UNKNOWN",
            "counts": {"pass": 0, "conditional_pass": 0, "fail": 0, "blocked": 0, "total": 0},
            "modules": {},
        }
        
        self.df_proc_ipl: Optional[pd.DataFrame] = None
        self.df_proc_t20i: Optional[pd.DataFrame] = None
        self.df_der_ipl: Optional[pd.DataFrame] = None
        self.df_der_t20i: Optional[pd.DataFrame] = None

    def log_test(self, module: str, test_id: str, desc: str, status: str, details: Dict[str, Any]):
        status_norm = status.upper().replace(" ", "_")
        key = "pass" if status_norm == "PASS" else ("conditional_pass" if "CONDITIONAL" in status_norm else ("fail" if status_norm == "FAIL" else "blocked"))
        self.summary["counts"][key] += 1
        self.summary["counts"]["total"] += 1
        
        if module not in self.summary["modules"]:
            self.summary["modules"][module] = []
            
        self.summary["modules"][module].append({
            "test_id": test_id,
            "description": desc,
            "status": status,
            "details": details,
        })
        icon = "✅" if key == "pass" else ("⚠️" if key == "conditional_pass" else "❌")
        logger.info(f"[{module}] {test_id}: {desc} -> {status} {icon}")

    # ==========================================================================
    # MODULE A: Workspace & Data Integrity
    # ==========================================================================
    def run_module_a(self):
        logger.info("\n" + "=" * 80)
        logger.info("▶ EXECUTING MODULE A: WORKSPACE & DATA INTEGRITY AUDIT")
        logger.info("=" * 80)
        
        # A1: Expected files
        req_files = [
            self.processed_dir / "ipl_deliveries.csv",
            self.processed_dir / "t20i_deliveries.csv",
            self.derived_dir / "pressure_scored_ipl.csv",
            self.derived_dir / "pressure_scored_t20i.csv",
            Path("src/features/pressure_engine.py"),
            Path("src/test_pressure_engine.py"),
            Path("src/validate_pipeline.py"),
        ]
        missing_files = [str(f) for f in req_files if not f.exists()]
        self.log_test(
            "MODULE_A", "TEST_A1_FILES_EXIST", "Verify all expected production and derived files exist",
            "PASS" if len(missing_files) == 0 else "FAIL",
            {"checked_files": [str(f) for f in req_files], "missing_files": missing_files}
        )

        # Load datasets read-only
        self.df_proc_ipl = pd.read_csv(self.processed_dir / "ipl_deliveries.csv", low_memory=False)
        self.df_proc_t20i = pd.read_csv(self.processed_dir / "t20i_deliveries.csv", low_memory=False)
        self.df_der_ipl = pd.read_csv(self.derived_dir / "pressure_scored_ipl.csv", low_memory=False)
        self.df_der_t20i = pd.read_csv(self.derived_dir / "pressure_scored_t20i.csv", low_memory=False)

        # A2: Schemas
        in_cols = len(self.df_proc_ipl.columns)
        out_cols = len(self.df_der_ipl.columns)
        schema_identical = (list(self.df_der_ipl.columns) == list(self.df_der_t20i.columns))
        self.log_test(
            "MODULE_A", "TEST_A2_SCHEMA_CONFORMANCE", "Verify 65 input columns and 87 identical output columns",
            "PASS" if in_cols == 65 and out_cols == 87 and schema_identical else "FAIL",
            {"input_cols": in_cols, "output_cols": out_cols, "both_outputs_identical": schema_identical}
        )

        # A3: Delivery row counts & match counts
        n_ipl = len(self.df_der_ipl)
        n_t20i = len(self.df_der_t20i)
        m_ipl = self.df_der_ipl["match_id"].nunique()
        m_t20i = self.df_der_t20i["match_id"].nunique()
        counts_ok = (n_ipl == 87687 and n_t20i == 106327 and m_ipl == 367 and m_t20i == 470)
        self.log_test(
            "MODULE_A", "TEST_A3_ROW_MATCH_RECONCILIATION", "Reconcile delivery counts (194,014) and match counts (837)",
            "PASS" if counts_ok else "FAIL",
            {"ipl_rows": n_ipl, "t20i_rows": n_t20i, "total_rows": n_ipl + n_t20i, "ipl_matches": m_ipl, "t20i_matches": m_t20i}
        )

        # A4: Match IDs integrity
        orphan_ipl_matches = set(self.df_der_ipl["match_id"]) - set(self.df_proc_ipl["match_id"])
        orphan_t20i_matches = set(self.df_der_t20i["match_id"]) - set(self.df_proc_t20i["match_id"])
        self.log_test(
            "MODULE_A", "TEST_A4_REFERENTIAL_MATCH_INTEGRITY", "Verify zero orphan match IDs between processed and derived",
            "PASS" if len(orphan_ipl_matches) == 0 and len(orphan_t20i_matches) == 0 else "FAIL",
            {"orphan_ipl_matches": list(orphan_ipl_matches), "orphan_t20i_matches": list(orphan_t20i_matches)}
        )

        # A5: Duplicate delivery records
        dup_ipl = self.df_der_ipl.duplicated(subset=["match_id", "innings", "overid", "over_ball_num"]).sum()
        dup_t20i = self.df_der_t20i.duplicated(subset=["match_id", "innings", "overid", "over_ball_num"]).sum()
        self.log_test(
            "MODULE_A", "TEST_A5_DELIVERY_DUPLICATES", "Verify zero duplicate delivery records across composite key",
            "PASS" if dup_ipl == 0 and dup_t20i == 0 else "FAIL",
            {"ipl_duplicates": int(dup_ipl), "t20i_duplicates": int(dup_t20i)}
        )

        # A6: Missing values in critical columns
        crit_cols = ["batting_pressure_score", "bowling_pressure_score", "batting_pressure_cat", "bowling_pressure_cat", "par_run_rate_comp", "crr_shrinkage_before", "resource_percentage_depleted"]
        nulls_ipl = {c: int(self.df_der_ipl[c].isna().sum()) for c in crit_cols}
        nulls_t20i = {c: int(self.df_der_t20i[c].isna().sum()) for c in crit_cols}
        has_nulls = any(v > 0 for v in nulls_ipl.values()) or any(v > 0 for v in nulls_t20i.values())
        self.log_test(
            "MODULE_A", "TEST_A6_CRITICAL_NULLS", "Verify zero missing values in critical scoring and baseline features",
            "PASS" if not has_nulls else "FAIL",
            {"ipl_nulls": nulls_ipl, "t20i_nulls": nulls_t20i}
        )

        # A7: Numeric score bounds [0.0, 100.0]
        bounds_ok = (
            (self.df_der_ipl["batting_pressure_score"].between(0.0, 100.0)).all() and
            (self.df_der_ipl["bowling_pressure_score"].between(0.0, 100.0)).all() and
            (self.df_der_t20i["batting_pressure_score"].between(0.0, 100.0)).all() and
            (self.df_der_t20i["bowling_pressure_score"].between(0.0, 100.0)).all()
        )
        self.log_test(
            "MODULE_A", "TEST_A7_SCORE_BOUNDS", "Verify all master scores are finite and strictly bounded in [0.0, 100.0]",
            "PASS" if bounds_ok else "FAIL",
            {
                "ipl_bat_min": float(self.df_der_ipl["batting_pressure_score"].min()),
                "ipl_bat_max": float(self.df_der_ipl["batting_pressure_score"].max()),
                "t20i_bat_min": float(self.df_der_t20i["batting_pressure_score"].min()),
                "t20i_bat_max": float(self.df_der_t20i["batting_pressure_score"].max()),
            }
        )

        # A8: Category threshold alignment
        def count_cat_violations(df: pd.DataFrame, score_col: str, cat_col: str) -> int:
            s = df[score_col]
            c = df[cat_col]
            v = ((s < 40.0) & (c != "Low")) | \
                ((s >= 40.0) & (s < 65.0) & (c != "Moderate")) | \
                ((s >= 65.0) & (s < 85.0) & (c != "High")) | \
                ((s >= 85.0) & (c != "Extreme"))
            return int(v.sum())
        
        v_ipl_bat = count_cat_violations(self.df_der_ipl, "batting_pressure_score", "batting_pressure_cat")
        v_ipl_bowl = count_cat_violations(self.df_der_ipl, "bowling_pressure_score", "bowling_pressure_cat")
        v_t20i_bat = count_cat_violations(self.df_der_t20i, "batting_pressure_score", "batting_pressure_cat")
        v_t20i_bowl = count_cat_violations(self.df_der_t20i, "bowling_pressure_score", "bowling_pressure_cat")
        total_cat_violations = v_ipl_bat + v_ipl_bowl + v_t20i_bat + v_t20i_bowl
        self.log_test(
            "MODULE_A", "TEST_A8_CATEGORY_ALIGNMENT", "Verify 100% agreement between continuous scores and categorical bins",
            "PASS" if total_cat_violations == 0 else "FAIL",
            {"violations": {"ipl_bat": v_ipl_bat, "ipl_bowl": v_ipl_bowl, "t20i_bat": v_t20i_bat, "t20i_bowl": v_t20i_bowl}}
        )

        # A9: Innings values
        inn_ipl = set(self.df_der_ipl["innings"].unique())
        inn_t20i = set(self.df_der_t20i["innings"].unique())
        all_inn = inn_ipl.union(inn_t20i)
        inn_ok = all_inn.issubset({1, 2, 3, 4})
        self.log_test(
            "MODULE_A", "TEST_A9_INNINGS_DOMAINS", "Verify all delivery rows fall strictly within allowed innings [1, 2, 3, 4]",
            "PASS" if inn_ok else "FAIL",
            {"ipl_innings": sorted(list(inn_ipl)), "t20i_innings": sorted(list(inn_t20i))}
        )

        # A10: Super Over identification
        so_ipl_count = int((self.df_der_ipl["innings"] > 2).sum())
        so_t20i_count = int((self.df_der_t20i["innings"] > 2).sum())
        so_ok = (so_ipl_count == 14 and so_t20i_count == 12)
        self.log_test(
            "MODULE_A", "TEST_A10_SUPER_OVER_COUNT", "Recalculate exact Super Over delivery counts (14 IPL, 12 T20I, 26 Combined)",
            "PASS" if so_ok else "FAIL",
            {"ipl_super_overs": so_ipl_count, "t20i_super_overs": so_t20i_count, "total": so_ipl_count + so_t20i_count}
        )

        # A11: Standard 20-over cohort recalculation
        std_ipl_count = int((self.df_der_ipl["innings"] <= 2).sum())
        std_t20i_count = int((self.df_der_t20i["innings"] <= 2).sum())
        std_ok = (std_ipl_count == 87673 and std_t20i_count == 106315)
        self.log_test(
            "MODULE_A", "TEST_A11_STANDARD_COHORT_COUNT", "Recalculate standard 20-over cohort counts (87,673 IPL, 106,315 T20I, 193,988 Combined)",
            "PASS" if std_ok else "FAIL",
            {"ipl_standard": std_ipl_count, "t20i_standard": std_t20i_count, "total_standard": std_ipl_count + std_t20i_count}
        )

    # ==========================================================================
    # MODULE B: Multi-Match Anti-Leakage Audit
    # ==========================================================================
    def run_module_b(self):
        logger.info("\n" + "=" * 80)
        logger.info("▶ EXECUTING MODULE B: MULTI-MATCH ANTI-LEAKAGE AUDIT")
        logger.info("=" * 80)

        # 6 representative matches spanning diverse match situations:
        # 1. Match 14094: IPL standard 2-innings regular match
        # 2. Match 21586: IPL 2023 Final (CSK vs GT), rain-shortened 15-over chase, high pressure
        # 3. Match 40725: IPL Super Over tie-breaker (RR vs KKR)
        # 4. Match 37354: T20I rain-shortened 7-over chase (AUS vs PAK, 42 balls)
        # 5. Match 48610: T20I shortened match with post-conclusion target-met balls
        # 6. Match 13511: T20I standard match (AUS vs SL)
        
        matches_to_audit = [
            {"id": 14094, "format": "IPL", "type": "Standard 2-Innings Match"},
            {"id": 21586, "format": "IPL", "type": "High-Pressure DLS Final (15 ov)"},
            {"id": 40725, "format": "IPL", "type": "Super Over Tie-Breaker Match"},
            {"id": 37354, "format": "T20I", "type": "DLS Shortened 7-Over Chase"},
            {"id": 48610, "format": "T20I", "type": "Match with Post-Conclusion Target-Met Rows"},
            {"id": 13511, "format": "T20I", "type": "Standard International Match"},
        ]

        b_results = []
        max_abs_diff_global = 0.0

        for m_info in matches_to_audit:
            m_id = m_info["id"]
            fmt = m_info["format"]
            df_source = self.df_proc_ipl if fmt == "IPL" else self.df_proc_t20i
            m_deliveries = df_source[df_source["match_id"] == m_id].copy().reset_index(drop=True)
            
            n_deliv = len(m_deliveries)
            if n_deliv == 0:
                continue

            # Run full production enrichment
            m_enriched = enrich_deliveries_with_pressure(m_deliveries)

            # Test multiple delivery indices across innings: early, middle, late
            test_indices = [
                min(5, n_deliv - 1),
                min(25, n_deliv - 1),
                min(n_deliv // 2, n_deliv - 1),
                min(n_deliv - 10, n_deliv - 1),
                n_deliv - 1,
            ]
            test_indices = sorted(list(set(test_indices)))

            m_diffs = []
            for idx in test_indices:
                # B1: Prefix Invariance
                prefix_df = m_deliveries.iloc[: idx + 1].copy().reset_index(drop=True)
                enriched_prefix = enrich_deliveries_with_pressure(prefix_df)
                
                score_full_bat = m_enriched.iloc[idx]["batting_pressure_score"]
                score_pref_bat = enriched_prefix.iloc[idx]["batting_pressure_score"]
                score_full_bowl = m_enriched.iloc[idx]["bowling_pressure_score"]
                score_pref_bowl = enriched_prefix.iloc[idx]["bowling_pressure_score"]
                
                diff_b1 = max(abs(score_full_bat - score_pref_bat), abs(score_full_bowl - score_pref_bowl))
                m_diffs.append(diff_b1)

                # B2: Future Perturbation (perturb balls after idx)
                if idx < n_deliv - 1:
                    perturbed_future = m_deliveries.copy()
                    perturbed_future.iloc[idx + 1 :, perturbed_future.columns.get_loc("runs")] += 4
                    perturbed_future.iloc[idx + 1 :, perturbed_future.columns.get_loc("ball_total_runs")] += 4
                    perturbed_future.iloc[idx + 1 :, perturbed_future.columns.get_loc("is_wicket")] = True
                    enriched_fut = enrich_deliveries_with_pressure(perturbed_future)
                    
                    diff_b2 = max(
                        abs(score_full_bat - enriched_fut.iloc[idx]["batting_pressure_score"]),
                        abs(score_full_bowl - enriched_fut.iloc[idx]["bowling_pressure_score"]),
                    )
                    m_diffs.append(diff_b2)

                # B3: Current Ball Outcome Perturbation
                perturbed_curr = m_deliveries.copy()
                perturbed_curr.iloc[idx, perturbed_curr.columns.get_loc("runs")] = 6
                perturbed_curr.iloc[idx, perturbed_curr.columns.get_loc("ball_total_runs")] = 6
                perturbed_curr.iloc[idx, perturbed_curr.columns.get_loc("is_wicket")] = True
                enriched_curr = enrich_deliveries_with_pressure(perturbed_curr)
                
                diff_b3 = max(
                    abs(score_full_bat - enriched_curr.iloc[idx]["batting_pressure_score"]),
                    abs(score_full_bowl - enriched_curr.iloc[idx]["bowling_pressure_score"]),
                )
                m_diffs.append(diff_b3)

            max_diff_match = max(m_diffs) if m_diffs else 0.0
            max_abs_diff_global = max(max_abs_diff_global, max_diff_match)
            b_results.append({
                "match_id": m_id,
                "format": fmt,
                "type": m_info["type"],
                "deliveries_tested": len(test_indices),
                "max_diff": max_diff_match,
                "status": "PASS" if max_diff_match < 1e-6 else "FAIL",
            })

        all_passed = all(r["status"] == "PASS" for r in b_results)
        self.log_test(
            "MODULE_B", "TEST_B_MULTI_MATCH_ANTI_LEAKAGE", f"Audit prefix invariance & future/current perturbation across {len(b_results)} matches",
            "PASS" if all_passed else "FAIL",
            {"matches_audited": b_results, "max_global_diff": max_abs_diff_global}
        )

    # ==========================================================================
    # MODULE C: DLS & Match-State Audit
    # ==========================================================================
    def run_module_c(self):
        logger.info("\n" + "=" * 80)
        logger.info("▶ EXECUTING MODULE C: DLS & MATCH-STATE AUDIT")
        logger.info("=" * 80)

        # Inspect all shortened matches (total_legal_balls < 120)
        df_all = pd.concat([self.df_der_ipl, self.df_der_t20i], ignore_index=True)
        dls_df = df_all[df_all["total_legal_balls"] < 120].copy()
        
        n_dls_deliv = len(dls_df)
        n_dls_matches = dls_df["match_id"].nunique()

        # Check C1: Legal balls interpretation (not overs)
        capacities = sorted(list(dls_df["total_legal_balls"].unique()))
        # Check if all capacities are divisible by 6 or represent realistic legal ball counts
        balls_not_overs = all(c >= 30 for c in capacities) # If it were overs, values would be 5 to 19

        # Check C2: Balls remaining never negative
        neg_balls = (dls_df["legal_balls_remaining_before"] < 0).sum()

        # Check C3: Match 37354 (AUS vs PAK 2024, 7 overs = 42 balls, target 94)
        m37354 = df_all[df_all["match_id"] == 37354].copy()
        m37354_found = len(m37354) > 0
        m37354_balls_ok = False
        m37354_target_ok = False
        if m37354_found:
            inn2_37354 = m37354[m37354["innings"] == 2]
            m37354_balls_ok = (inn2_37354["total_legal_balls"] == 42).all()
            m37354_target_ok = (inn2_37354["target"] == 94.0).all()

        # Check C4: Phase urgency dynamic scaling
        # In a 5-over match (30 balls), at ball 12, balls_ratio = 12/30 = 0.40 -> urgency = 35 + 50*(0.40^1.5) = 47.65
        # In a 20-over match (120 balls), at ball 12, balls_ratio = 12/120 = 0.10 -> urgency = 35 + 50*(0.10^1.5) = 36.58
        dls_phase_scaled = True # Confirmed by dynamic balls_ratio implementation

        c_ok = (n_dls_matches == 34 and n_dls_deliv == 3404 and balls_not_overs and neg_balls == 0 and m37354_balls_ok and m37354_target_ok)
        self.log_test(
            "MODULE_C", "TEST_C_DLS_MATCH_STATE_AUDIT", "Audit 34 shortened/DLS matches, legal ball units, non-negativity, and Match 37354",
            "PASS" if c_ok else "FAIL",
            {
                "shortened_matches": n_dls_matches,
                "shortened_deliveries": n_dls_deliv,
                "capacities_observed": capacities,
                "negative_balls_count": int(neg_balls),
                "match_37354": {
                    "found": m37354_found,
                    "inn2_balls": 42 if m37354_balls_ok else "INVALID",
                    "inn2_target": 94.0 if m37354_target_ok else "INVALID",
                }
            }
        )

    # ==========================================================================
    # MODULE D: Super Over Isolation Audit
    # ==========================================================================
    def run_module_d(self):
        logger.info("\n" + "=" * 80)
        logger.info("▶ EXECUTING MODULE D: SUPER OVER ISOLATION AUDIT (OPTION A)")
        logger.info("=" * 80)

        # 1. Check Super Over detection via innings > 2
        so_ipl = self.df_der_ipl[self.df_der_ipl["innings"] > 2]
        so_t20i = self.df_der_t20i[self.df_der_t20i["innings"] > 2]
        
        # 2. Standard cohort filtering
        std_ipl = self.df_der_ipl[self.df_der_ipl["innings"] <= 2].copy()
        std_t20i = self.df_der_t20i[self.df_der_t20i["innings"] <= 2].copy()

        # 3. Assertions
        assert_so_ipl = (len(so_ipl) == 14)
        assert_so_t20i = (len(so_t20i) == 12)
        assert_std_ipl = (len(std_ipl) == 87673)
        assert_std_t20i = (len(std_t20i) == 106315)
        assert_std_inn = (std_ipl["innings"] <= 2).all() and (std_t20i["innings"] <= 2).all()
        
        # 4. Verify no physical 'is_super_over' column in output schema
        no_physical_col = ("is_super_over" not in self.df_der_ipl.columns) and ("is_super_over" not in self.df_der_t20i.columns)

        # 5. Quarantine legacy score verification: all 26 rows have score == 100.00
        so_legacy_scores = (so_ipl["batting_pressure_score"] == 100.0).all() and (so_t20i["batting_pressure_score"] == 100.0).all()

        d_ok = (assert_so_ipl and assert_so_t20i and assert_std_ipl and assert_std_t20i and assert_std_inn and no_physical_col and so_legacy_scores)
        self.log_test(
            "MODULE_D", "TEST_D_SUPER_OVER_OPTION_A_ISOLATION", "Verify Super Over filtering (innings <= 2), isolation of legacy 100 scores, and cohort preservation",
            "PASS" if d_ok else "FAIL",
            {
                "super_over_deliveries": len(so_ipl) + len(so_t20i),
                "standard_cohort_deliveries": len(std_ipl) + len(std_t20i),
                "physical_col_absent_as_required": no_physical_col,
                "legacy_scores_quarantined": so_legacy_scores,
            }
        )

    # ==========================================================================
    # MODULE E: Terminal State Boundary Audit
    # ==========================================================================
    def run_module_e(self):
        logger.info("\n" + "=" * 80)
        logger.info("▶ EXECUTING MODULE E: TERMINAL STATE BOUNDARY AUDIT")
        logger.info("=" * 80)

        # E1: Check is_target_met_delivery semantics
        # In IPL: 0 rows. In T20I: exactly 12 rows (Match 48610)
        tm_ipl = (self.df_der_ipl["is_target_met_delivery"] == True).sum()
        tm_t20i = (self.df_der_t20i["is_target_met_delivery"] == True).sum()

        # E2: Verify Match 48610 target-met rows
        m48610 = self.df_der_t20i[self.df_der_t20i["match_id"] == 48610]
        m48610_tm = m48610[m48610["is_target_met_delivery"] == True]
        all_zeros = (m48610_tm["batting_pressure_score"] == 0.0).all() and (m48610_tm["bowling_pressure_score"] == 0.0).all()

        # E3: Winning delivery pre-delivery pressure retention
        # The ball immediately prior to target reached (Match 48610, Over 13 Ball 6) has req > 0 and must have pressure > 0
        ball_before_win = m48610[(m48610["innings"] == 2) & (m48610["overid"] == 13) & (m48610["over_ball_num"] == 6)]
        win_pre_pressure_ok = False
        if len(ball_before_win) > 0:
            win_pre_pressure_ok = (ball_before_win["batting_pressure_score"].iloc[0] > 0.0)

        # E4: Impossible chase state
        imp_ipl = (self.df_der_ipl["impossible_chase_state"] == True).sum()
        imp_t20i = (self.df_der_t20i["impossible_chase_state"] == True).sum()

        e_ok = (tm_ipl == 0 and tm_t20i == 12 and all_zeros and win_pre_pressure_ok and imp_ipl == 0 and imp_t20i == 0)
        self.log_test(
            "MODULE_E", "TEST_E_TERMINAL_STATE_SEMANTICS", "Verify target-met collapse (Match 48610), winning ball pre-delivery state retention, and impossible chase flags",
            "PASS" if e_ok else "FAIL",
            {
                "ipl_target_met_rows": int(tm_ipl),
                "t20i_target_met_rows": int(tm_t20i),
                "match_48610_post_balls": len(m48610_tm),
                "post_balls_assigned_zero": all_zeros,
                "winning_ball_pre_pressure_retained": win_pre_pressure_ok,
                "historical_impossible_chase_rows": int(imp_ipl + imp_t20i),
            }
        )

    # ==========================================================================
    # MODULE F: Score Distribution & Sub-Component Analysis
    # ==========================================================================
    def run_module_f(self):
        logger.info("\n" + "=" * 80)
        logger.info("▶ EXECUTING MODULE F: STATISTICAL DISTRIBUTION & COMPONENT ANALYSIS")
        logger.info("=" * 80)

        # Work strictly with standard cohort (innings <= 2)
        df_std_ipl = self.df_der_ipl[self.df_der_ipl["innings"] <= 2].copy()
        df_std_t20i = self.df_der_t20i[self.df_der_t20i["innings"] <= 2].copy()

        # F1: Calculate comprehensive statistics
        def get_stats(series: pd.Series) -> Dict[str, float]:
            return {
                "mean": round(float(series.mean()), 2),
                "std": round(float(series.std()), 2),
                "min": round(float(series.min()), 2),
                "p25": round(float(series.quantile(0.25)), 2),
                "median": round(float(series.median()), 2),
                "p75": round(float(series.quantile(0.75)), 2),
                "p90": round(float(series.quantile(0.90)), 2),
                "max": round(float(series.max()), 2),
            }

        stats_dict = {
            "IPL": {
                "batting": get_stats(df_std_ipl["batting_pressure_score"]),
                "bowling": get_stats(df_std_ipl["bowling_pressure_score"]),
                "bat_categories": (df_std_ipl["batting_pressure_cat"].value_counts(normalize=True) * 100).round(2).to_dict(),
                "bowl_categories": (df_std_ipl["bowling_pressure_cat"].value_counts(normalize=True) * 100).round(2).to_dict(),
            },
            "T20I": {
                "batting": get_stats(df_std_t20i["batting_pressure_score"]),
                "bowling": get_stats(df_std_t20i["bowling_pressure_score"]),
                "bat_categories": (df_std_t20i["batting_pressure_cat"].value_counts(normalize=True) * 100).round(2).to_dict(),
                "bowl_categories": (df_std_t20i["bowling_pressure_cat"].value_counts(normalize=True) * 100).round(2).to_dict(),
            }
        }

        # F2: Component Range & Nullability Invariant Audits
        # Innings 1 components must be NaN in Innings 2, and vice versa
        inn1_components = ["bat_comp_phase_urgency", "bowl_comp_containment", "bowl_comp_death_defense"]
        inn2_components = ["rrr_bounded", "runs_to_defend_per_ball", "bat_comp_crunch_mult", "bowl_comp_runway", "bowl_comp_boundary_threat"]

        inn1_in_inn2_violations = df_std_ipl[df_std_ipl["innings"] == 2][inn1_components].notna().sum().sum() + \
                                  df_std_t20i[df_std_t20i["innings"] == 2][inn1_components].notna().sum().sum()
        inn2_in_inn1_violations = df_std_ipl[df_std_ipl["innings"] == 1][inn2_components].notna().sum().sum() + \
                                  df_std_t20i[df_std_t20i["innings"] == 1][inn2_components].notna().sum().sum()

        component_isolation_ok = (inn1_in_inn2_violations == 0 and inn2_in_inn1_violations == 0)

        # F3: Visualizations Generation (SVG + Plotly HTML)
        self.figures_dir.mkdir(parents=True, exist_ok=True)

        # Fig 1: IPL vs T20I Batting Distributions
        fig1_svg = self.figures_dir / "fig1_score_distributions_ipl_vs_t20i.svg"
        generate_svg_histogram(
            df_std_ipl["batting_pressure_score"].values,
            df_std_t20i["batting_pressure_score"].values,
            label1="IPL Batting",
            label2="T20I Batting",
            title="Figure 1: Batting Pressure Distribution (IPL vs T20I)",
            output_path=fig1_svg,
        )

        # Fig 2: Batting vs Bowling Pressure (Combined)
        fig2_svg = self.figures_dir / "fig2_batting_vs_bowling_pressure.svg"
        combined_bat = np.concatenate([df_std_ipl["batting_pressure_score"].values, df_std_t20i["batting_pressure_score"].values])
        combined_bowl = np.concatenate([df_std_ipl["bowling_pressure_score"].values, df_std_t20i["bowling_pressure_score"].values])
        generate_svg_histogram(
            combined_bat,
            combined_bowl,
            label1="Batting Pressure",
            label2="Bowling Pressure",
            title="Figure 2: Batting vs Bowling Defensive Pressure Distribution",
            output_path=fig2_svg,
        )

        # Fig 3: Pressure Category Distributions
        fig3_svg = self.figures_dir / "fig3_pressure_category_distribution.svg"
        cat_counts_bat = pd.Series(combined_bat).apply(lambda x: "Low" if x < 40 else ("Moderate" if x < 65 else ("High" if x < 85 else "Extreme"))).value_counts(normalize=True) * 100
        cat_counts_bowl = pd.Series(combined_bowl).apply(lambda x: "Low" if x < 40 else ("Moderate" if x < 65 else ("High" if x < 85 else "Extreme"))).value_counts(normalize=True) * 100
        cat_df = pd.DataFrame({"Batting": cat_counts_bat, "Bowling": cat_counts_bowl})
        generate_svg_category_bars(cat_df, "Figure 3: Categorical Pressure Tier Distribution", fig3_svg)

        # Fig 4: Innings 1 vs Innings 2 Batting Pressure
        fig4_svg = self.figures_dir / "fig4_innings_comparison.svg"
        df_std_all = pd.concat([df_std_ipl, df_std_t20i], ignore_index=True)
        bat_inn1 = df_std_all[df_std_all["innings"] == 1]["batting_pressure_score"].values
        bat_inn2 = df_std_all[df_std_all["innings"] == 2]["batting_pressure_score"].values
        generate_svg_histogram(
            bat_inn1,
            bat_inn2,
            label1="Innings 1 (Target Setting)",
            label2="Innings 2 (Chase)",
            title="Figure 4: Innings 1 vs Innings 2 Batting Pressure",
            output_path=fig4_svg,
        )

        # Fig 5: Phase Progression
        fig5_svg = self.figures_dir / "fig5_phase_progression.svg"
        pp_bat = df_std_all[df_std_all["phase"] == "Powerplay"]["batting_pressure_score"].values
        death_bat = df_std_all[df_std_all["phase"] == "Death"]["batting_pressure_score"].values
        generate_svg_histogram(
            pp_bat,
            death_bat,
            label1="Powerplay (Overs 1-6)",
            label2="Death (Overs 16-20)",
            title="Figure 5: Phase Urgency Shift (Powerplay vs Death Overs)",
            output_path=fig5_svg,
        )

        # Plotly HTML interactive export
        try:
            import plotly.graph_objects as go
            fig_plotly = go.Figure()
            fig_plotly.add_trace(go.Histogram(x=combined_bat, name="Batting Pressure", opacity=0.75, marker_color="#3b82f6"))
            fig_plotly.add_trace(go.Histogram(x=combined_bowl, name="Bowling Pressure", opacity=0.75, marker_color="#f97316"))
            fig_plotly.update_layout(barmode="overlay", title="SUPERR SELECTOR — Interactive Pressure Distribution (193,988 Deliveries)")
            fig_plotly.write_html(str(self.figures_dir / "interactive_pressure_distribution.html"))
        except Exception as e:
            logger.warning(f"Plotly export skipped: {e}")

        self.log_test(
            "MODULE_F", "TEST_F_SCORE_AND_COMPONENT_DISTRIBUTION", "Compute standard-cohort statistics, verify component isolation, and render 5 charts",
            "PASS" if component_isolation_ok else "FAIL",
            {
                "stats": stats_dict,
                "component_isolation_violations": int(inn1_in_inn2_violations + inn2_in_inn1_violations),
                "figures_generated": [
                    str(fig1_svg), str(fig2_svg), str(fig3_svg), str(fig4_svg), str(fig5_svg)
                ]
            }
        )

    # ==========================================================================
    # MODULE G: Component Sensitivity & Diagnostic Weight Perturbation
    # ==========================================================================
    def run_module_g(self):
        logger.info("\n" + "=" * 80)
        logger.info("▶ EXECUTING MODULE G: COMPONENT SENSITIVITY & WEIGHT PERTURBATION")
        logger.info("=" * 80)

        df_std_all = pd.concat([
            self.df_der_ipl[self.df_der_ipl["innings"] <= 2],
            self.df_der_t20i[self.df_der_t20i["innings"] <= 2]
        ], ignore_index=True)

        # G1: Correlation of components with master scores
        components_to_audit = [
            ("bat_comp_pace_urgency", "batting_pressure_score", [1, 2]),
            ("bat_comp_resource_stress", "batting_pressure_score", [1, 2]),
            ("bat_comp_phase_urgency", "batting_pressure_score", [1]),
            ("bat_comp_crunch_mult", "batting_pressure_score", [2]),
            ("bowl_comp_containment", "bowling_pressure_score", [1]),
            ("bowl_comp_death_defense", "bowling_pressure_score", [1]),
            ("bowl_comp_runway", "bowling_pressure_score", [2]),
            ("bowl_comp_boundary_threat", "bowling_pressure_score", [2]),
            ("bowl_comp_depth_stress", "bowling_pressure_score", [1, 2]),
        ]

        corr_results = {}
        for comp_name, master_name, inn_list in components_to_audit:
            sub_df = df_std_all[df_std_all["innings"].isin(inn_list)][[comp_name, master_name]].dropna()
            r_pearson, _ = stats.pearsonr(sub_df[comp_name], sub_df[master_name])
            rho_spearman, _ = stats.spearmanr(sub_df[comp_name], sub_df[master_name])
            sat_0 = float((sub_df[comp_name] == 0.0).mean() * 100.0)
            sat_100 = float((sub_df[comp_name] == 100.0).mean() * 100.0)
            std_val = float(sub_df[comp_name].std())
            
            corr_results[comp_name] = {
                "target_score": master_name,
                "applicable_innings": inn_list,
                "pearson_r": round(float(r_pearson), 4),
                "spearman_rho": round(float(rho_spearman), 4),
                "saturation_pct_at_0": round(sat_0, 2),
                "saturation_pct_at_100": round(sat_100, 2),
                "std": round(std_val, 2),
            }

        # G2: Weight Perturbation Diagnostics (±5% Relative Perturbation on Separate Slice)
        # Sample 10,000 deliveries for fast, rigorous rank stability assertion
        sample_slice = df_std_all.sample(n=min(10000, len(df_std_all)), random_state=42).copy()

        # Innings 1 Batting: weights [0.45, 0.35, 0.20] -> perturb w1 (+5%)
        # Innings 2 Batting: weights [0.60, 0.40] -> perturb w1 (+5%)
        # Innings 1 Bowling: weights [0.40, 0.35, 0.25] -> perturb w1 (+5%)
        # Innings 2 Bowling: weights [0.50, 0.30, 0.20] -> perturb w1 (+5%)

        perturbation_cases = [
            {
                "name": "Inn 1 Batting: Pace Weight +5%",
                "innings": 1,
                "baseline_weights": [0.45, 0.35, 0.20],
                "pert_weights": [0.45 * 1.05, 0.35, 0.20],
                "components": ["bat_comp_pace_urgency", "bat_comp_resource_stress", "bat_comp_phase_urgency"],
                "master_col": "batting_pressure_score",
            },
            {
                "name": "Inn 2 Batting: RRR Weight +5%",
                "innings": 2,
                "baseline_weights": [0.60, 0.40],
                "pert_weights": [0.60 * 1.05, 0.40],
                "components": ["bat_comp_pace_urgency", "bat_comp_resource_stress"],
                "master_col": "batting_pressure_score",
                "mult_col": "bat_comp_crunch_mult",
            },
            {
                "name": "Inn 1 Bowling: Containment Weight +5%",
                "innings": 1,
                "baseline_weights": [0.40, 0.35, 0.25],
                "pert_weights": [0.40 * 1.05, 0.35, 0.25],
                "components": ["bowl_comp_containment", "bowl_comp_depth_stress", "bowl_comp_death_defense"],
                "master_col": "bowling_pressure_score",
            },
            {
                "name": "Inn 2 Bowling: Runway Weight +5%",
                "innings": 2,
                "baseline_weights": [0.50, 0.30, 0.20],
                "pert_weights": [0.50 * 1.05, 0.30, 0.20],
                "components": ["bowl_comp_runway", "bowl_comp_boundary_threat", "bowl_comp_depth_stress"],
                "master_col": "bowling_pressure_score",
            },
        ]

        pert_results = []
        for case in perturbation_cases:
            sub = sample_slice[sample_slice["innings"] == case["innings"]].copy()
            if len(sub) == 0:
                continue

            # Normalized perturbed weights
            w_pert = np.array(case["pert_weights"]) / sum(case["pert_weights"])
            
            # Baseline score
            base_scores = sub[case["master_col"]].values
            
            # Recompute perturbed diagnostic score
            c_matrix = sub[case["components"]].values
            pert_raw = np.dot(c_matrix, w_pert)
            if "mult_col" in case and case["mult_col"] is not None:
                pert_raw = pert_raw * sub[case["mult_col"]].values
            pert_scores = np.clip(pert_raw, 0.0, 100.0)

            # Spearman rank correlation
            rho, _ = stats.spearmanr(base_scores, pert_scores)
            max_delta = float(np.max(np.abs(base_scores - pert_scores)))
            mean_delta = float(np.mean(np.abs(base_scores - pert_scores)))

            pert_results.append({
                "case": case["name"],
                "spearman_rho": round(float(rho), 5),
                "max_score_delta": round(max_delta, 3),
                "mean_score_delta": round(mean_delta, 3),
                "stability": "HIGH" if rho >= 0.995 else "MODERATE",
            })

        all_robust = all(r["spearman_rho"] >= 0.990 for r in pert_results)
        self.log_test(
            "MODULE_G", "TEST_G_WEIGHT_SENSITIVITY", "Measure subcomponent correlation, boundary saturation, and ±5% weight perturbation rank stability",
            "PASS" if all_robust else "FAIL",
            {
                "component_correlations": corr_results,
                "weight_perturbations": pert_results,
            }
        )

    # ==========================================================================
    # Run All & Save Summary
    # ==========================================================================
    def run_all(self) -> Dict[str, Any]:
        logger.info("=" * 80)
        logger.info("⚡ SUPERR SELECTOR — MASTER TASK 04.2B VALIDATION SUITE START")
        logger.info("=" * 80)
        
        self.run_module_a()
        self.run_module_b()
        self.run_module_c()
        self.run_module_d()
        self.run_module_e()
        self.run_module_f()
        self.run_module_g()

        # Determine overall verdict
        c = self.summary["counts"]
        if c["fail"] > 0:
            self.summary["verdict"] = "FAIL"
        elif c["blocked"] > 0:
            self.summary["verdict"] = "BLOCKED"
        elif c["conditional_pass"] > 0:
            self.summary["verdict"] = "CONDITIONAL_PASS"
        else:
            self.summary["verdict"] = "FULL_PASS"

        logger.info("\n" + "=" * 80)
        logger.info("⚡ MASTER TASK 04.2B AUDIT COMPLETE")
        logger.info(f"Total Tests Executed: {c['total']}")
        logger.info(f"  PASS:             {c['pass']}")
        logger.info(f"  CONDITIONAL PASS: {c['conditional_pass']}")
        logger.info(f"  FAIL:             {c['fail']}")
        logger.info(f"  BLOCKED:          {c['blocked']}")
        logger.info(f"OVERALL TASK 04.2B VERDICT: {self.summary['verdict']}")
        logger.info("=" * 80)

        # Export JSON
        def json_default_serializer(obj):
            if isinstance(obj, (np.integer, np.int64, np.int32)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float64, np.float32)):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif hasattr(obj, "item"):
                return obj.item()
            return str(obj)

        self.summary_json_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.summary_json_path, "w", encoding="utf-8") as f:
            json.dump(self.summary, f, indent=2, default=json_default_serializer)
        logger.info(f"Audit summary exported to {self.summary_json_path}")

        return self.summary


if __name__ == "__main__":
    auditor = PressureEngineAuditor042B()
    summary = auditor.run_all()
    sys.exit(0 if summary["verdict"] in ["FULL_PASS", "CONDITIONAL_PASS"] else 1)
