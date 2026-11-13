# Raw Data Directory (`data/raw/`)

This directory is designated for immutable, ground-truth raw datasets.

### Automatic Detection & Safety:
The **SUPERR SELECTOR** platform has built-in auto-discovery in `src/config.py`:
- If raw CSV files are placed here in `data/raw/`, they will be read directly.
- If existing tournament CSV files are located in `Data/Data Pack/`, the system automatically detects and loads them safely in read-only mode.
- Existing CSV files are **never overwritten or altered**.

