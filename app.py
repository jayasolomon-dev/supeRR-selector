"""
SUPERR SELECTOR - Rajasthan Royals Season 2 Hackathon
Premium Cricket Performance Intelligence & Squad Analytics Platform
Main Streamlit Application Entrypoint
"""

from pathlib import Path
import runpy

app_path = Path(__file__).resolve().parent / "superr_selector_app.py"
runpy.run_path(str(app_path), run_name="__main__")
