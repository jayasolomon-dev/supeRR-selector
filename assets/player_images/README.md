# Player Images Directory (`assets/player_images/` & `data/player_images/`)

Place real player headshots and photographs here to have them automatically displayed in the SUPERR SELECTOR dashboard.

### File Naming Conventions:
The image loader (`src/utils/helpers.py`) resolves photos by:
1. **Player ID**: `<player_id>.png` or `<player_id>.jpg` (e.g., `1187.png`)
2. **Player Name**: `<first_last>.png` (e.g., `jason_roy.png`)

If no image is found for a player, a high-resolution SVG jersey avatar with the player's initials is automatically rendered.

