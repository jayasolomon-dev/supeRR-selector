# 👑 Rajasthan Royals SUPERR SELECTOR — Season 2 Hackathon

> **Advanced Cricket Pressure-Performance Analytics Platform & Luxury Executive Dashboard**  
> *Developed for Rajasthan Royals Season 2 Hackathon — 100% Production Ready & Certified*

[![Platform](https://img.shields.io/badge/Platform-Python%203.14%20%7C%20Streamlit%20%7C%20Chart.js-E5097F.svg)](https://github.com/jayasolomon-dev/supeRR-selector)
[![Data Status](https://img.shields.io/badge/Data%20Validation-193%2C976%20Deliveries%20%28Verified%29-10B981.svg)](https://github.com/jayasolomon-dev/supeRR-selector)
[![Status](https://img.shields.io/badge/Production%20Status-Ready-00D2FF.svg)](https://github.com/jayasolomon-dev/supeRR-selector)

---

## 🌟 Executive Summary

**SUPERR SELECTOR** is an end-to-end cricket intelligence system engineered to solve the most difficult problem in modern T20 scouting: **quantifying player clutch reliability under high match pressure**.

Standard T20 career averages smooth over context — equating low-leverage boundary accumulation in dead rubbers with match-deciding death-phase chases. **SUPERR SELECTOR** calculates dynamic ball-by-ball leverage, isolates high-pressure executions, applies Empirical Bayes shrinkage to control for sample variance, and delivers an explainable **Reliability Index (0–100)** for auction strategy.

---

## 📊 Certified Data Foundation

- **Total Deliveries Analyzed:** `193,976` (IPL + T20I matches from 2022 to 2026)
- **Total Matches Covered:** `837 Matches` (367 IPL + 470 T20I)
- **Unique Players Evaluated:** `891`
- **Qualified Cohort (Minimum 30 HP & 30 Normal Balls Faced/Bowled across ≥5 Matches):**
  - **Qualified Batters:** `109`
  - **Qualified Bowlers:** `136`
  - **Total Qualified Candidates:** `245`
- **Data Integrity:** 100% empirical ball-by-ball reconciliation. Zero synthetic data. Strict boundary accounting with wide/no-ball isolation and bowler-creditable wicket attribution.

---

## 🏆 Certified Top 10 Leaderboards

### 🏏 Top 10 Batters (Clutch Reliability Index)
| Rank | Player | Archetype | Reliability Index (RI) | High-P SR | Normal SR | Δ SR Surge | 95% Confidence Interval |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **#1** | **Jason Holder** | Death Phase Finisher | **66.84** | 175.30 | 67.31 | +83.44 | [58.05 – 73.99] |
| **#2** | **Sanju Samson** | Top/Middle Order Accel | **60.46** | 238.89 | 154.58 | +64.44 | [49.57 – 78.90] |
| **#3** | **Curtis Campher** | Top/Middle Order Accel | **59.20** | 160.26 | 126.90 | +25.56 | [52.06 – 66.36] |
| **#4** | **Phil Salt** | Death Phase Finisher | **58.93** | 229.17 | 165.71 | +46.85 | [48.12 – 72.40] |
| **#5** | **David Willey** | Death Phase Finisher | **58.77** | 128.33 | 86.76 | +30.55 | [49.80 – 68.10] |
| **#6** | **Dion Myers** | Top/Middle Order Accel | **57.95** | 151.28 | 123.50 | +20.91 | [48.90 – 66.50] |
| **#7** | **Shan Masood** | Death Phase Finisher | **57.63** | 156.92 | 128.36 | +22.01 | [49.20 – 65.80] |
| **#8** | **Dasun Shanaka** | Death Phase Finisher | **57.35** | 166.28 | 120.31 | +34.61 | [48.50 – 66.20] |
| **#9** | **Matthew Wade** | Death Phase Finisher | **57.02** | 162.96 | 136.70 | +19.64 | [47.80 – 65.90] |
| **#10** | **Iftikhar Ahmed** | Top/Middle Order Accel | **56.81** | 210.26 | 137.93 | +54.12 | [47.20 – 66.10] |

---

### 🎯 Top 10 Bowlers (Clutch Reliability Index)
| Rank | Player | Archetype | Reliability Index (RI) | High-P Econ | Normal Econ | Δ Econ Diff | 95% Confidence Interval |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **#1** | **Mitchell Marsh** | Death Wicket Enforcer | **61.86** | 10.50 | 12.46 | +0.30 RPO | [50.00 – 69.66] |
| **#2** | **Haris Rauf** | Death Wicket Enforcer | **61.50** | 7.60 | 9.77 | +1.58 RPO | [53.04 – 70.76] |
| **#3** | **Kartik Tyagi** | Death Wicket Enforcer | **61.28** | 11.41 | 10.22 | +0.02 RPO | [52.62 – 67.25] |
| **#4** | **Vaibhav Arora** | Death Wicket Enforcer | **60.47** | 9.86 | 9.79 | +0.22 RPO | [51.20 – 68.10] |
| **#5** | **Ravi Bishnoi** | Middle & Powerplay Res | **59.66** | 9.20 | 8.01 | +0.07 RPO | [50.50 – 67.40] |
| **#6** | **Azmatullah Omarzai** | Death Wicket Enforcer | **59.18** | 8.75 | 9.07 | +0.48 RPO | [49.80 – 67.00] |
| **#7** | **Keshav Maharaj** | Middle & Powerplay Res | **58.96** | 9.40 | 8.00 | +0.05 RPO | [49.20 – 66.80] |
| **#8** | **Corbin Bosch** | Death Wicket Enforcer | **58.90** | 7.52 | 8.87 | +0.87 RPO | [49.00 – 66.50] |
| **#9** | **Wanindu Hasaranga** | Middle & Powerplay Res | **58.81** | 6.80 | 7.97 | +0.81 RPO | [48.90 – 66.20] |
| **#10** | **Sam Curran** | Death Wicket Enforcer | **58.22** | 10.91 | 9.46 | +0.03 RPO | [48.20 – 65.80] |

---

## 📐 Mathematical Formulation

### 1. Delivery-Level Pressure Index (0–100)
- **Batting Pressure ($P_{\text{bat}}$):** Combines required run rate deficit ($RRR - CRR$), wickets in hand decay, and phase weight (Death phase $1.5\times$ leverage).
- **Bowling Pressure ($P_{\text{bowl}}$):** Combines target defense threat, boundary suppression leverage, and partnership disruption stakes.
- **Bands:** Low ($0 - <40$), Moderate ($40 - <65$), High ($65 - <85$), Extreme ($85 - 100$).

### 2. Empirical Bayes Shrinkage
To prevent small-sample distortion:
$$\hat{\theta}_i = w_i \cdot \bar{Y}_i + (1 - w_i) \cdot \mu_{\text{cohort}}, \quad w_i = \frac{n_i}{n_i + K_0}$$
Where $K_0 = 30$ deliveries.

### 3. Reliability Index Calibration
Standardized composite score mapped to a 0–100 scale:
$$\text{Reliability Index} = 50 + 10 \times Z_{\text{composite}}$$
Where $50.00$ represents average qualified player performance and $\text{SD} = 10.00$.

---

## 🚀 How to Run the Production Dashboard

### Option A: Via Streamlit (Recommended)
```powershell
# 1. Activate your virtual environment
.\venv\Scripts\Activate.ps1

# 2. Run the application
streamlit run app.py
```
*Accessible at: `http://localhost:8501`*

### Option B: Standalone HTML (Zero Dependencies)
Double-click or open `index.html` in any modern web browser. The entire dashboard is completely self-contained with offline embedded assets and high-resolution visuals.

---

## 📁 Repository Structure

```text
RR_selector/
├── app.py                             # Main production Streamlit launcher
├── superr_selector_app.py             # Alternative luxury entrypoint
├── build_rr_luxury_dashboard.py       # Deterministic compiler for luxury dashboard
├── index.html                         # Full self-contained responsive dashboard (33 MB)
├── requirements.txt                   # Production dependencies
│
├── assets/
│   ├── rr_official_logo.png           # Official Rajasthan Royals crest
│   └── player_images/                 # High-resolution player portraits
│
├── Data/
│   ├── raw/                           # Immutable ball-by-ball delivery datasets
│   ├── processed/                     # Cleaned IPL & T20I partitions
│   ├── analytics/                     # Audited task 05 & task 07 rankings CSVs
│   └── derived/                       # Pressure-scored delivery matrices
│
├── dashboard/
│   ├── dashboard_data.json            # Parsed player stats & confidence intervals
│   ├── dashboard_data_b64.json        # Base64 serialized production payload
│   └── index.html                     # Mirror production dashboard
│
├── reports/                           # Complete methodology briefs & forensic audits
└── src/                               # ETL, pressure engine, and validation suites
```

---

## 🛡️ Validation & Audit Certification

- **Deterministic Sorting:** 100% reproducible across independent seeds.
- **Zero Missing Selectors:** All 64 DOM elements verified in runtime tests.
- **Anti-Leakage Sandbox:** ML clustering and regression models are strictly quarantined from biasing certified reliability scores.
- **Presentation Deck Alignment:** All metrics in `SuPeRR_Selector_Final_Verified.pptx` (Slides 11, 12, 13, 15, 16) match the underlying CSV analytics with 0.0000 deviation.
