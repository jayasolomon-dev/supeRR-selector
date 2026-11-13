# 🏏 SUPERR SELECTOR

> **Advanced Cricket Pressure-Performance Analytics Platform**  
> *Developed for Hackathons on Windows 11 with Google Antigravity IDE*

---

## 🌟 Project Overview

**SUPERR SELECTOR** is a data-driven cricket analytics platform focused on quantifying **player performance under pressure** in high-stakes T20 cricket. 

### Data Scope
- **Target Competitions:** **IPL (Indian Premier League)** and **T20I (ICC Men's International T20s)**.
- **Data Integrity:** **100% empirical data.** No fake statistics, synthetic player rankings, or generated match records are used. All calculations are grounded in official ball-by-ball delivery events.

---

## 📂 Project Structure

The project has been organized with clear separation of concerns:

```text
SupeRR_Selector/
│
├── data/
│   ├── raw/                 # Official immutable raw datasets (CSVs)
│   ├── external/            # Benchmark rankings, venue & atmospheric metadata
│   └── processed/           # Cleaned feature matrices and verified subsets
│
├── src/                     # Core Python source code (ETL, features, models)
│
├── dashboard/               # Streamlit interactive UI
│   ├── pages/               # Multi-page views (Player Profiles, Matchups, Squad Selection)
│   └── components/          # Reusable UI widgets, KPI cards, and custom filters
│
├── assets/
│   ├── player_images/       # Player photos mapped by player_id
│   └── team_logos/          # Official franchise and national team badges
│
├── outputs/
│   ├── charts/              # Saved Plotly visual exports (PNG / HTML)
│   ├── data_audit/          # Data audit reports and foreign key validation sheets
│   ├── models/              # Saved model weights (.pkl / .joblib)
│   └── tables/              # Exported CSV data tables and squad sheets
│
├── reports/                 # Project documentation, methodology briefs & presentations
│
├── requirements.txt         # Pinned Python package dependencies
├── .gitignore               # Excludes virtual environments and temporary cache files
└── README.md                # Beginner-friendly setup manual (this file)
```

---

## 💻 Beginner-Friendly Windows 11 Setup Guide

Follow these exact steps in your Windows 11 environment.

### Step 1: Open PowerShell or Windows Terminal
1. Press `Win + X` on your keyboard.
2. Click on **Terminal** (or search for **PowerShell** in the Start Menu).
3. Navigate into your project folder:
   ```powershell
   cd D:\SupeRR_Selector
   ```

### Step 2: Verify Python and Pip
Confirm your Python environment is ready:
```powershell
python --version
pip --version
```
*(Your system has Python 3.14.4 and Pip 26.3 verified and operational).*

### Step 3: Create an Isolated Virtual Environment
A virtual environment ensures your hackathon packages don't conflict with other software on your PC:
```powershell
python -m venv venv
```
This creates a new folder named `venv/` containing an isolated copy of Python.

### Step 4: Activate the Virtual Environment
To activate the virtual environment in PowerShell, run:
```powershell
.\venv\Scripts\Activate.ps1
```

> ⚠️ **Common Windows 11 PowerShell Execution Policy Fix:**  
> If PowerShell shows an error in red text saying *`"running scripts is disabled on this system"`*, don't worry! This is a standard Windows security default. Run this single command to allow script execution for your current window:
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
> .\venv\Scripts\Activate.ps1
> ```
> *(Once activated, your terminal prompt will display `(venv)` at the beginning of the line).*

*(If using Command Prompt `cmd.exe` instead of PowerShell, simply run: `venv\Scripts\activate.bat`)*

### Step 5: Install Project Dependencies
Upgrade pip and install all required libraries from `requirements.txt`:
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## 📊 Supplied Datasets Verified in `Data/Data Pack/`

All six required CSV files are verified in read-only mode:
1. **`ball_by_ball.csv`** (39.17 MB) — 200,999 delivery records.
2. **`matches.csv`** (0.12 MB) — 883 match results and conditions.
3. **`competitions.csv`** (0.01 MB) — 141 tournaments (134 T20I, 5 IPL, 2 other).
4. **`teams.csv`** (0.01 MB) — 38 unique competing teams.
5. **`playing_eleven.csv`** (0.92 MB) — 28,381 match day squad appearances.
6. **`competition_team_player_mapping.csv`** (0.44 MB) — 6,413 player registry mappings.

---

## 🗺️ Next Steps Roadmap

1. **Step 1 Completed:** Workspace inspected, Python/pip verified, datasets verified, folder structure created, requirements & documentation established.
2. **Step 2 (Next):** Filter and validate the dataset specifically for IPL and T20I matches.
3. **Step 3:** Feature engineering for Pressure Index and clutch performance metrics.
4. **Step 4:** Machine learning algorithms (Scikit-learn clustering & optional gradient boosting).
5. **Step 5:** Interactive Streamlit dashboard in `dashboard/`.
