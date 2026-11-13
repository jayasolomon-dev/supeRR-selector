"""
SUPERR SELECTOR - Rajasthan Royals Season 2 Hackathon
Premium Cricket Performance Intelligence & Squad Analytics Platform
Main Streamlit Application Entrypoint — Ultra Premium Executive Edition
"""

import os
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

# Base Directory & Logo Path
base_dir = Path(__file__).resolve().parent
logo_icon_path = base_dir / "assets" / "rr_official_logo.png"

# Page Configuration with Official RR Crest Favicon
st.set_page_config(
    page_title="Rajasthan Royals SUPERR SELECTOR Season 2",
    page_icon=str(logo_icon_path) if logo_icon_path.exists() else "👑",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Fullscreen CSS to eliminate Streamlit chrome & padding
st.markdown("""
<style>
    /* Hide Streamlit Header, Footer, and Sidebar */
    #MainMenu {visibility: hidden;}
    header[data-testid="stHeader"] {display: none !important;}
    footer {visibility: hidden !important;}
    [data-testid="stSidebar"] {display: none !important;}
    [data-testid="collapsedControl"] {display: none !important;}
    
    /* Seamless Edge-to-Edge Container */
    .block-container {
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
        width: 100% !important;
        overflow: hidden !important;
    }
    
    .stApp {
        background-color: #09061A !important;
    }

    iframe {
        width: 100vw !important;
        height: 100vh !important;
        min-height: 100vh !important;
        border: none !important;
        display: block !important;
    }
</style>
""", unsafe_allow_html=True)

# Load the certified dark luxury dashboard
html_file = base_dir / "index.html"
if not html_file.exists():
    html_file = base_dir / "dashboard" / "index.html"

if html_file.exists():
    html_code = html_file.read_text(encoding="utf-8")
    components.html(html_code, height=1080, scrolling=True)
else:
    st.error("Certified Dashboard HTML not found. Please run build_rr_luxury_dashboard.py")
