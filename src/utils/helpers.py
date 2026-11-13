"""
SUPERR SELECTOR - Utility Helpers
Handles player headshot discovery across image directories and visual formatting.
"""

from pathlib import Path
from typing import Optional
import re

from src.config import PLAYER_IMAGES_DIR, DATA_PLAYER_IMAGES_DIR


def get_player_image_path(player_id: str, player_name: Optional[str] = None) -> Optional[Path]:
    """
    Searches assets/player_images and data/player_images for a matching player photo.
    Supports formats: .png, .jpg, .jpeg, .webp
    Matches against: player_id, clean_player_name
    """
    search_dirs = [PLAYER_IMAGES_DIR, DATA_PLAYER_IMAGES_DIR]
    extensions = [".png", ".jpg", ".jpeg", ".webp"]
    
    clean_id = str(player_id).strip()
    name_slug = ""
    if player_name:
        name_slug = re.sub(r"[^\w\s-]", "", player_name).strip().replace(" ", "_").lower()

    for directory in search_dirs:
        if not directory.exists():
            continue
            
        # 1. Check by player ID
        for ext in extensions:
            target = directory / f"{clean_id}{ext}"
            if target.exists():
                return target
                
        # 2. Check by name slug
        if name_slug:
            for ext in extensions:
                target = directory / f"{name_slug}{ext}"
                if target.exists():
                    return target
                    
    return None


def render_player_avatar_html(player_name: str, size_px: int = 64) -> str:
    """
    Renders an inline SVG cricket jersey badge with player initials when no photo exists.
    """
    parts = player_name.strip().split()
    if len(parts) >= 2:
        initials = f"{parts[0][0]}{parts[-1][0]}".upper()
    elif len(parts) == 1 and len(parts[0]) > 0:
        initials = parts[0][:2].upper()
    else:
        initials = "CR"

    return f"""
    <div style="
        width: {size_px}px;
        height: {size_px}px;
        border-radius: 50%;
        background: linear-gradient(135deg, #023047, #219EBC);
        color: #FFB703;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: bold;
        font-size: {int(size_px * 0.38)}px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
        border: 2px solid #FFB703;
    ">
        {initials}
    </div>
    """


def format_cricket_metric(value: float, decimals: int = 2, fallback: str = "N/A") -> str:
    """Safely formats numeric cricket metrics handling NaNs."""
    if value is None or (isinstance(value, float) and (value != value or value == float("inf"))):
        return fallback
    return f"{value:.{decimals}f}"

