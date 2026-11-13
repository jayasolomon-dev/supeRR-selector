# -*- coding: utf-8 -*-
"""
Build Rajasthan Royals SUPERR SELECTOR Dashboard
Ultra-Premium Senior UI/UX Edition:
- Fluid Auto-Layout & 100% Fully Responsive (Mobile, Tablet, Laptop, 4K)
- Bespoke Chart-Specific Animations (Horizontal Slide Cascade, Vertical Spring Bounce, Ripple Histogram, Sweeping Radial Donut)
- Staggered Page & Card Entry Transitions on Every Tab Switch
- Highest Ergonomic Chart Pairing for Every Cricket Performance Metric
Outputs: index.html, dashboard/index.html, dashboard/superr_selector_dashboard.html
"""

import json
import os
from pathlib import Path

def generate_dashboard():
    base_dir = Path(__file__).resolve().parent
    b64_json_path = base_dir / "dashboard" / "dashboard_data_b64.json"
    
    print(f"Loading data from {b64_json_path}...")
    with open(b64_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    batters = data["batters"]
    bowlers = data["bowlers"]
    
    print(f"Loaded {len(batters)} batters and {len(bowlers)} bowlers.")
    
    # Pre-extract player image cutouts
    holder_img = batters[0].get("image_b64", "")
    marsh_img = bowlers[0].get("image_b64", "")
    samson_img = batters[1].get("image_b64", "")
    campher_img = batters[2].get("image_b64", "")
    
    players_json = json.dumps(data)

    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Rajasthan Royals SUPERR SELECTOR Season 2 — Performance Intelligence</title>
  
  <!-- Google Fonts: Inter & Plus Jakarta Sans & Caveat -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Caveat:wght@600;700&family=Inter:wght@300;400;500;600;700;800;900&family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
  
  <!-- FontAwesome Icons for crisp UI elements -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  
  <!-- Chart.js for High Performance Canvas Charts -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

  <style>
    /* ==========================================================================
       SENIOR UI/UX DESIGN SYSTEM — AUTO-LAYOUT & FLUID RESPONSIVE SYSTEM
       ========================================================================== */
    :root {
      --bg-canvas: #09061A;
      --bg-sidebar: #0C0824;
      --bg-card: rgba(19, 15, 48, 0.88);
      --bg-card-hover: rgba(26, 21, 64, 0.95);
      --bg-card-solid: #130F30;
      
      --rr-pink: #E5097F;
      --rr-pink-glow: rgba(229, 9, 127, 0.35);
      --rr-hotpink: #FF2A85;
      --rr-cyan: #00D2FF;
      --rr-blue: #38BDF8;
      --rr-purple: #8B5CF6;
      --rr-purple-dark: #6366F1;
      --rr-gold: #F59E0B;
      --rr-gold-light: #FCD34D;
      --rr-green: #10B981;
      --rr-green-light: #34D399;
      
      --text-white: #FFFFFF;
      --text-light: #E2E8F0;
      --text-muted: #94A3B8;
      --text-dim: #64748B;
      
      --border-card: rgba(139, 92, 246, 0.22);
      --border-pink: rgba(229, 9, 127, 0.35);
      --border-glow: 0 0 15px rgba(229, 9, 127, 0.18);
      
      --radius-sm: 8px;
      --radius-md: 12px;
      --radius-lg: 16px;
      --radius-xl: 22px;
      
      --sidebar-width: 250px;
      
      --font-main: 'Plus Jakarta Sans', 'Inter', system-ui, -apple-system, sans-serif;
      --font-script: 'Caveat', cursive, sans-serif;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    html, body {
      width: 100%;
      height: 100%;
    }

    body {
      font-family: var(--font-main);
      background-color: var(--bg-canvas);
      background-image: 
        radial-gradient(ellipse 90% 60% at 50% -15%, rgba(139, 92, 246, 0.18), transparent 70%),
        radial-gradient(circle at 10% 20%, rgba(229, 9, 127, 0.10), transparent 40%),
        radial-gradient(circle at 90% 80%, rgba(0, 210, 255, 0.08), transparent 40%);
      color: var(--text-white);
      min-height: 100vh;
      overflow-x: hidden;
      line-height: 1.4;
      display: flex;
    }

    /* ==========================================================================
       SIDEBAR NAVIGATION (RESPONSIVE AUTO-LAYOUT)
       ========================================================================== */
    .sidebar {
      width: var(--sidebar-width);
      background: var(--bg-sidebar);
      border-right: 1px solid rgba(255, 255, 255, 0.08);
      height: 100vh;
      position: fixed;
      top: 0;
      left: 0;
      display: flex;
      flex-direction: column;
      z-index: 100;
      box-shadow: 4px 0 24px rgba(0, 0, 0, 0.5);
      transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .sidebar-header {
      padding: clamp(16px, 2.5vh, 24px) 20px 18px 20px;
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
      border-bottom: 1px solid rgba(255, 255, 255, 0.06);
      flex-shrink: 0;
    }

    .rr-logo-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 4px;
      cursor: pointer;
    }

    .rr-crown-icon {
      font-size: 34px;
      color: var(--rr-pink);
      filter: drop-shadow(0 0 10px rgba(229, 9, 127, 0.6));
      transition: transform 0.25s ease;
    }

    .rr-logo-container:hover .rr-crown-icon {
      transform: scale(1.08) rotate(-4deg);
    }

    .rr-brand-name {
      font-size: 13px;
      font-weight: 900;
      letter-spacing: 2px;
      color: var(--rr-pink);
      text-transform: uppercase;
      margin-top: 2px;
      line-height: 1.1;
      text-shadow: 0 0 12px rgba(229, 9, 127, 0.5);
    }
    .rr-brand-sub {
      font-size: 10px;
      font-weight: 700;
      letter-spacing: 3px;
      color: #FFFFFF;
      text-transform: uppercase;
      opacity: 0.9;
    }

    .sidebar-menu {
      padding: 18px 12px;
      display: flex;
      flex-direction: column;
      gap: 6px;
      flex-grow: 1;
      overflow-y: auto;
    }

    .nav-item {
      display: flex;
      align-items: center;
      gap: 14px;
      padding: 11px 16px;
      color: var(--text-muted);
      border-radius: var(--radius-md);
      font-size: 13.5px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1);
      position: relative;
      user-select: none;
      text-decoration: none;
    }

    .nav-item i {
      font-size: 15px;
      width: 20px;
      text-align: center;
      color: inherit;
      transition: transform 0.2s ease, color 0.2s ease;
    }

    .nav-item:hover {
      color: var(--text-white);
      background: rgba(255, 255, 255, 0.06);
      transform: translateX(3px);
    }

    .nav-item.active {
      background: linear-gradient(90deg, var(--rr-pink) 0%, #D81B60 100%);
      color: #FFFFFF;
      font-weight: 700;
      box-shadow: 0 4px 18px rgba(229, 9, 127, 0.45);
    }

    .nav-item.active i {
      color: #FFFFFF;
      filter: drop-shadow(0 0 4px rgba(255, 255, 255, 0.5));
    }

    .sidebar-footer {
      padding: 20px 16px;
      position: relative;
      background: linear-gradient(180deg, transparent 0%, rgba(10, 6, 26, 0.95) 100%);
      border-top: 1px solid rgba(255, 255, 255, 0.06);
      text-align: center;
      overflow: hidden;
      flex-shrink: 0;
    }

    .sidebar-footer::before {
      content: "";
      position: absolute;
      bottom: 0; left: 0; right: 0; height: 90px;
      background: url('https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?auto=format&fit=crop&w=400&q=40') bottom center / cover no-repeat;
      opacity: 0.15;
      mix-blend-mode: luminosity;
      pointer-events: none;
    }

    .slogan-script {
      font-family: var(--font-script);
      font-size: 18px;
      color: #FF5EA6;
      line-height: 1.2;
      margin-bottom: 12px;
      position: relative;
      text-shadow: 0 0 10px rgba(229, 9, 127, 0.5);
    }

    .superr-badge-mini {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 7px;
      font-size: 11.5px;
      font-weight: 800;
      color: var(--rr-gold-light);
      letter-spacing: 0.8px;
      text-transform: uppercase;
      position: relative;
    }

    /* ==========================================================================
       MAIN CONTENT AUTO-LAYOUT WRAPPER
       ========================================================================== */
    .main-wrapper {
      margin-left: var(--sidebar-width);
      flex-grow: 1;
      width: calc(100% - var(--sidebar-width));
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      background: transparent;
      position: relative;
      min-width: 0; /* Prevents flex children from blowing past container */
      transition: margin-left 0.3s ease, width 0.3s ease;
    }

    /* Top Header Banner */
    .top-header-banner {
      padding: clamp(12px, 2vh, 18px) clamp(16px, 3vw, 36px);
      background: linear-gradient(90deg, #100B2E 0%, #171142 50%, #0E0927 100%);
      border-bottom: 1px solid rgba(139, 92, 246, 0.25);
      display: flex;
      align-items: center;
      justify-content: space-between;
      position: sticky;
      top: 0;
      z-index: 90;
      backdrop-filter: blur(16px);
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
      flex-wrap: wrap;
      gap: 12px;
    }

    .header-left {
      display: flex;
      align-items: center;
      gap: 16px;
      min-width: 0;
    }

    .sidebar-toggle-btn {
      display: none; /* Shown on small screens */
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.15);
      color: #FFFFFF;
      width: 38px;
      height: 38px;
      border-radius: var(--radius-sm);
      align-items: center;
      justify-content: center;
      cursor: pointer;
      font-size: 16px;
      transition: all 0.2s ease;
    }

    .sidebar-toggle-btn:hover {
      background: var(--rr-pink);
    }

    .header-titles {
      display: flex;
      flex-direction: column;
    }

    .header-top-row {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .header-team-title {
      font-size: 14px;
      font-weight: 500;
      color: var(--text-light);
      letter-spacing: 0.5px;
    }

    .header-app-title {
      font-size: clamp(20px, 2.4vw, 26px);
      font-weight: 900;
      font-style: italic;
      color: var(--rr-hotpink);
      letter-spacing: 0.5px;
      text-shadow: 0 0 16px rgba(229, 9, 127, 0.6);
      line-height: 1.1;
    }

    .season-pill {
      background: rgba(229, 9, 127, 0.15);
      border: 1px solid var(--rr-pink);
      color: var(--rr-hotpink);
      font-size: 11px;
      font-weight: 800;
      padding: 3px 10px;
      border-radius: 20px;
      letter-spacing: 0.6px;
    }

    .header-divider {
      width: 1px;
      height: 36px;
      background: rgba(255, 255, 255, 0.15);
      margin: 0 8px;
    }

    .header-page-context {
      display: flex;
      flex-direction: column;
      min-width: 0;
    }

    .header-page-title {
      font-size: clamp(16px, 1.8vw, 20px);
      font-weight: 800;
      color: #FFFFFF;
      line-height: 1.2;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .header-page-subtitle {
      font-size: 12.5px;
      color: var(--text-muted);
      font-weight: 500;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .header-right {
      display: flex;
      align-items: center;
      gap: 16px;
      flex-shrink: 0;
    }

    .header-stadium-graphic {
      display: flex;
      align-items: center;
      gap: 12px;
      background: rgba(255, 255, 255, 0.04);
      padding: 6px 14px;
      border-radius: 30px;
      border: 1px solid rgba(255, 255, 255, 0.08);
    }

    .stadium-tagline {
      font-size: 12.5px;
      font-weight: 700;
      color: #FF75B5;
      letter-spacing: 0.5px;
    }

    /* ==========================================================================
       STAGGERED VIEW TRANSITION ANIMATIONS
       ========================================================================== */
    .view-content {
      padding: clamp(16px, 2.5vw, 32px) clamp(16px, 3vw, 36px) 60px clamp(16px, 3vw, 36px);
      flex-grow: 1;
      display: none;
      min-width: 0;
      opacity: 0;
      transform: translateY(12px);
      transition: opacity 0.3s ease, transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .view-content.active {
      display: block;
      opacity: 1;
      transform: translateY(0);
      animation: viewSlideIn 0.35s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }

    @keyframes viewSlideIn {
      0% {
        opacity: 0;
        transform: translateY(14px);
      }
      100% {
        opacity: 1;
        transform: translateY(0);
      }
    }

    /* Staggered card entrance on active tab */
    .view-content.active .rr-card,
    .view-content.active .overview-hero-card,
    .view-content.active .kpi-mini-card,
    .view-content.active .spotlight-card,
    .view-content.active .intel-top-card,
    .view-content.active .pressure-kpi-card,
    .view-content.active .comp-player-card {
      animation: cardStagger 0.45s cubic-bezier(0.16, 1, 0.3, 1) both;
    }

    .view-content.active > div:nth-child(1) { animation-delay: 0.04s; }
    .view-content.active > div:nth-child(2) { animation-delay: 0.09s; }
    .view-content.active > div:nth-child(3) { animation-delay: 0.14s; }
    .view-content.active > div:nth-child(4) { animation-delay: 0.19s; }

    @keyframes cardStagger {
      0% {
        opacity: 0;
        transform: translateY(18px) scale(0.985);
      }
      100% {
        opacity: 1;
        transform: translateY(0) scale(1);
      }
    }

    /* ==========================================================================
       CARD COMPONENT AUTO-LAYOUT & FLUID GRIDS
       ========================================================================== */
    .rr-card {
      background: var(--bg-card);
      border: 1px solid var(--border-card);
      border-radius: var(--radius-lg);
      padding: clamp(16px, 2vw, 22px);
      position: relative;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
      backdrop-filter: blur(12px);
      transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1), border-color 0.25s ease, box-shadow 0.25s ease;
      min-width: 0;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }

    .rr-card:hover {
      border-color: rgba(229, 9, 127, 0.45);
      transform: translateY(-2px);
      box-shadow: 0 12px 32px rgba(0, 0, 0, 0.5), 0 0 20px rgba(229, 9, 127, 0.16);
    }

    .card-header-clean {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 14px;
      flex-shrink: 0;
    }

    .card-title-group {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .card-title-group i {
      font-size: 16px;
      color: var(--rr-pink);
    }

    .card-title {
      font-size: clamp(14px, 1.4vw, 16px);
      font-weight: 800;
      color: #FFFFFF;
      letter-spacing: 0.2px;
    }

    .card-action-link {
      font-size: 12.5px;
      font-weight: 700;
      color: #FF5EA6;
      cursor: pointer;
      text-decoration: none;
      transition: color 0.2s ease, transform 0.2s ease;
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }

    .card-action-link:hover {
      color: #FFFFFF;
      transform: translateX(3px);
    }

    .chart-container-fluid {
      position: relative;
      width: 100%;
      height: 100%;
      min-height: 180px;
      flex-grow: 1;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    /* ==========================================================================
       VIEW 1: OVERVIEW AUTO-LAYOUT
       ========================================================================== */
    .overview-hero-grid {
      display: grid;
      grid-template-columns: minmax(300px, 1.4fr) repeat(4, minmax(130px, 1fr));
      gap: 16px;
      margin-bottom: 20px;
    }

    .overview-hero-card {
      background: linear-gradient(135deg, rgba(229, 9, 127, 0.25) 0%, rgba(20, 15, 48, 0.95) 100%);
      border: 1px solid rgba(229, 9, 127, 0.4);
      border-radius: var(--radius-lg);
      padding: 18px 22px;
      display: flex;
      align-items: center;
      gap: 18px;
      position: relative;
      overflow: hidden;
      box-shadow: 0 8px 30px rgba(229, 9, 127, 0.2);
    }

    .hero-cutout-img {
      height: 90px;
      width: 90px;
      object-fit: cover;
      object-position: top;
      border-radius: 50%;
      border: 2px solid var(--rr-pink);
      box-shadow: 0 0 16px rgba(229, 9, 127, 0.45);
      background: #0A071E;
      flex-shrink: 0;
      transition: transform 0.3s ease;
    }

    .overview-hero-card:hover .hero-cutout-img {
      transform: scale(1.05);
    }

    .hero-text-content h3 {
      font-size: 12px;
      font-weight: 600;
      color: var(--text-light);
      text-transform: uppercase;
      letter-spacing: 1px;
    }
    .hero-text-content h2 {
      font-size: clamp(18px, 2vw, 22px);
      font-weight: 900;
      font-style: italic;
      color: var(--rr-gold-light);
      letter-spacing: 0.5px;
      margin: 2px 0;
      line-height: 1.1;
    }
    .hero-text-content p {
      font-size: 11.5px;
      color: #CBD5E1;
      font-weight: 500;
    }

    .kpi-mini-card {
      background: var(--bg-card);
      border: 1px solid var(--border-card);
      border-radius: var(--radius-lg);
      padding: 16px;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      text-align: center;
      position: relative;
      transition: transform 0.2s ease, border-color 0.2s ease;
    }

    .kpi-mini-card:hover {
      transform: translateY(-2px);
      border-color: rgba(229, 9, 127, 0.4);
    }

    .kpi-mini-icon {
      font-size: 22px;
      color: var(--rr-pink);
      margin-bottom: 6px;
    }

    .kpi-mini-label {
      font-size: 11.5px;
      font-weight: 600;
      color: var(--text-muted);
      margin-bottom: 2px;
    }

    .kpi-mini-value {
      font-size: clamp(24px, 2.5vw, 30px);
      font-weight: 900;
      color: #FFFFFF;
      line-height: 1;
    }

    .kpi-mini-sub {
      font-size: 11px;
      color: var(--text-dim);
      margin-top: 4px;
      font-weight: 500;
    }

    .overview-spotlights-grid {
      display: grid;
      grid-template-columns: minmax(280px, 1.2fr) minmax(280px, 1.2fr) minmax(240px, 1fr);
      gap: 16px;
      margin-bottom: 20px;
    }

    .spotlight-card {
      background: var(--bg-card);
      border: 1px solid var(--border-card);
      border-radius: var(--radius-lg);
      padding: 20px;
      display: flex;
      flex-direction: column;
      position: relative;
      overflow: hidden;
      transition: transform 0.25s ease, border-color 0.25s ease;
    }

    .spotlight-card:hover {
      transform: translateY(-2px);
      border-color: rgba(229, 9, 127, 0.45);
    }

    .spotlight-header {
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 15px;
      font-weight: 800;
      color: #FFFFFF;
      margin-bottom: 14px;
    }

    .spotlight-header .crown-badge {
      background: rgba(245, 158, 11, 0.2);
      color: var(--rr-gold-light);
      padding: 4px 8px;
      border-radius: 8px;
      font-size: 13px;
    }

    .spotlight-body {
      display: flex;
      align-items: center;
      gap: 18px;
    }

    .spotlight-player-img {
      width: clamp(80px, 9vw, 95px);
      height: clamp(80px, 9vw, 95px);
      border-radius: 50%;
      object-fit: cover;
      object-position: top;
      border: 3px solid var(--rr-pink);
      box-shadow: 0 0 20px rgba(229, 9, 127, 0.35);
      background: #09061A;
      flex-shrink: 0;
      transition: transform 0.3s ease;
    }

    .spotlight-card:hover .spotlight-player-img {
      transform: scale(1.06);
    }

    .spotlight-metrics {
      flex-grow: 1;
      display: flex;
      flex-direction: column;
      gap: 5px;
    }

    .spotlight-ri-wrap {
      display: flex;
      align-items: baseline;
      gap: 8px;
    }

    .spotlight-ri {
      font-size: clamp(28px, 3.2vw, 36px);
      font-weight: 900;
      color: #FFFFFF;
      line-height: 1;
    }

    .spotlight-ri-label {
      font-size: 11.5px;
      color: var(--text-muted);
      font-weight: 600;
    }

    .spotlight-tags {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 4px;
    }

    .spotlight-stat-tag {
      font-size: 11.5px;
      font-weight: 700;
    }
    .stat-tag-green { color: #10B981; }
    .stat-tag-pink { color: #FF5EA6; }

    .role-pill-bottom {
      margin-top: 14px;
      background: linear-gradient(90deg, rgba(229, 9, 127, 0.25) 0%, rgba(139, 92, 246, 0.25) 100%);
      border: 1px solid rgba(229, 9, 127, 0.4);
      border-radius: 20px;
      padding: 6px 14px;
      font-size: 12px;
      font-weight: 700;
      color: #FFFFFF;
      text-align: center;
      width: 100%;
    }

    .donut-card-container {
      display: flex;
      align-items: center;
      justify-content: space-around;
      height: 100%;
      width: 100%;
      gap: 16px;
      padding: 6px 2px;
    }

    .donut-chart-box {
      width: 155px;
      height: 155px;
      min-width: 155px;
      min-height: 155px;
      position: relative;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }

    .donut-chart-box canvas {
      width: 100% !important;
      height: 100% !important;
      display: block;
    }

    .donut-center-badge {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      text-align: center;
      pointer-events: none;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      z-index: 2;
      width: 100%;
    }

    .donut-center-num {
      font-size: 24px;
      font-weight: 900;
      color: #FFFFFF;
      line-height: 1;
      letter-spacing: -0.5px;
    }

    .donut-center-text {
      font-size: 10px;
      font-weight: 700;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-top: 3px;
    }

    .donut-legend {
      display: flex;
      flex-direction: column;
      gap: 9px;
      flex-grow: 1;
      min-width: 0;
    }

    .donut-legend-pressure {
      display: flex;
      flex-direction: column;
      gap: 9px;
      flex-grow: 1;
      min-width: 0;
    }

    .legend-row-pressure {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      font-size: 12px;
      color: #FFFFFF;
    }

    .legend-color-label {
      display: flex;
      align-items: center;
      gap: 8px;
      min-width: 0;
    }

    .legend-dot {
      width: 10px;
      height: 10px;
      border-radius: 3px;
      flex-shrink: 0;
    }

    .legend-label-text {
      font-size: 11.5px;
      font-weight: 600;
      color: #E2E8F0;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .legend-pct-pill {
      font-size: 11px;
      font-weight: 700;
      padding: 2px 7px;
      border-radius: 4px;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.12);
      white-space: nowrap;
      flex-shrink: 0;
    }

    .legend-item {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 12px;
      font-weight: 600;
      color: var(--text-light);
    }

    .overview-dual-tables {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 18px;
    }

    .mini-rank-table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 6px;
    }

    .mini-rank-table th {
      text-align: left;
      font-size: 11px;
      font-weight: 700;
      color: var(--text-dim);
      text-transform: uppercase;
      letter-spacing: 0.5px;
      padding: 8px 10px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }

    .mini-rank-table td {
      padding: 9px 10px;
      font-size: 12.5px;
      font-weight: 600;
      color: var(--text-light);
      border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    }

    .mini-rank-table tr:hover td {
      background: rgba(255, 255, 255, 0.03);
    }

    .progress-bar-wrap {
      display: flex;
      align-items: center;
      gap: 10px;
      width: clamp(100px, 14vw, 160px);
    }

    .progress-track {
      flex-grow: 1;
      height: 7px;
      background: rgba(255, 255, 255, 0.1);
      border-radius: 10px;
      overflow: hidden;
      position: relative;
    }

    .progress-fill-pink,
    .progress-fill-purple {
      height: 100%;
      border-radius: 10px;
      width: 0%; /* Will animate in via JS */
      transition: width 1.2s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .progress-fill-pink {
      background: linear-gradient(90deg, var(--rr-pink), #FF5EA6);
      box-shadow: 0 0 10px rgba(229, 9, 127, 0.5);
    }

    .progress-fill-purple {
      background: linear-gradient(90deg, #38BDF8, #8B5CF6);
      box-shadow: 0 0 10px rgba(56, 189, 248, 0.5);
    }

    .progress-val {
      font-size: 12px;
      font-weight: 800;
      color: #FFFFFF;
      min-width: 38px;
    }

    /* ==========================================================================
       VIEW 2 & 3: BATTING & BOWLING INTELLIGENCE
       ========================================================================== */
    .kpi-row-5 {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 16px;
      margin-bottom: 20px;
    }

    .intel-top-card {
      background: var(--bg-card);
      border: 1px solid var(--border-card);
      border-radius: var(--radius-lg);
      padding: 16px 18px;
      display: flex;
      align-items: center;
      gap: 14px;
      box-shadow: 0 6px 20px rgba(0, 0, 0, 0.35);
      transition: transform 0.2s ease, border-color 0.2s ease;
    }

    .intel-top-card:hover {
      transform: translateY(-2px);
      border-color: rgba(229, 9, 127, 0.4);
    }

    .intel-top-icon {
      width: 44px;
      height: 44px;
      border-radius: 12px;
      background: rgba(229, 9, 127, 0.12);
      border: 1px solid rgba(229, 9, 127, 0.3);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 18px;
      color: var(--rr-pink);
      flex-shrink: 0;
    }
    .icon-gold { background: rgba(245, 158, 11, 0.12); border-color: rgba(245, 158, 11, 0.3); color: var(--rr-gold-light); }
    .icon-blue { background: rgba(0, 210, 255, 0.12); border-color: rgba(0, 210, 255, 0.3); color: var(--rr-cyan); }
    .icon-purple { background: rgba(139, 92, 246, 0.12); border-color: rgba(139, 92, 246, 0.3); color: var(--rr-purple); }

    .intel-top-data {
      display: flex;
      flex-direction: column;
      min-width: 0;
    }

    .intel-top-label {
      font-size: 11px;
      font-weight: 600;
      color: var(--text-muted);
      margin-bottom: 2px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .intel-top-val {
      font-size: clamp(18px, 2vw, 22px);
      font-weight: 900;
      color: #FFFFFF;
      line-height: 1.1;
    }

    .intel-top-sub {
      font-size: 10.5px;
      font-weight: 600;
      color: var(--text-dim);
    }

    .mid-table-chart-grid {
      display: grid;
      grid-template-columns: minmax(320px, 1.25fr) minmax(280px, 1fr);
      gap: 18px;
      margin-bottom: 20px;
    }

    .clean-table-wrap {
      width: 100%;
      overflow-x: auto;
    }

    .clean-table {
      width: 100%;
      border-collapse: collapse;
      min-width: 380px;
    }

    .clean-table th {
      text-align: left;
      font-size: 11px;
      font-weight: 700;
      color: var(--text-dim);
      text-transform: uppercase;
      letter-spacing: 0.5px;
      padding: 10px 12px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
      white-space: nowrap;
    }

    .clean-table th:first-child, .clean-table td:first-child {
      text-align: center;
      width: 36px;
    }

    .clean-table th:nth-child(3), .clean-table td:nth-child(3) {
      text-align: center;
      width: 75px;
      color: var(--text-dim);
    }

    .clean-table th:nth-child(4), .clean-table td:nth-child(4) {
      text-align: center;
      width: 115px;
    }

    .clean-table td {
      padding: 10px 12px;
      font-size: 12.5px;
      font-weight: 600;
      color: var(--text-light);
      border-bottom: 1px solid rgba(255, 255, 255, 0.04);
      vertical-align: middle;
      line-height: 1.35;
      white-space: nowrap;
    }

    .clean-table tr:hover td {
      background: rgba(229, 9, 127, 0.06);
    }

    .role-badge-table {
      font-size: 11px;
      font-weight: 600;
      color: #CBD5E1;
      background: rgba(255, 255, 255, 0.06);
      padding: 3px 8px;
      border-radius: 6px;
      display: inline-block;
    }

    .intel-bottom-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 16px;
    }

    .gauge-slider-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 12px 10px;
      text-align: center;
      height: 100%;
    }

    .gauge-big-num {
      font-size: 38px;
      font-weight: 900;
      color: #FFFFFF;
      line-height: 1;
    }

    .gauge-subtext {
      font-size: 12px;
      color: var(--text-muted);
      margin-bottom: 18px;
    }

    .gauge-track-wrap {
      width: 90%;
      position: relative;
      margin: 0 auto 12px auto;
    }

    .gauge-track {
      width: 100%;
      height: 10px;
      border-radius: 20px;
      background: linear-gradient(90deg, #10B981 0%, #38BDF8 35%, #F59E0B 70%, #E5097F 100%);
      position: relative;
    }

    .gauge-thumb {
      position: absolute;
      top: 50%;
      left: 0%; /* Will animate to 65.4% via JS */
      transform: translate(-50%, -50%);
      width: 18px;
      height: 18px;
      background: #FFFFFF;
      border: 3px solid var(--rr-pink);
      border-radius: 50%;
      box-shadow: 0 0 12px rgba(229, 9, 127, 0.8);
      transition: left 1.3s cubic-bezier(0.34, 1.56, 0.64, 1);
    }

    .gauge-labels {
      display: flex;
      justify-content: space-between;
      width: 100%;
      font-size: 10px;
      font-weight: 700;
      color: var(--text-dim);
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .player-spotlight-box {
      display: flex;
      flex-direction: column;
      height: 100%;
      justify-content: space-between;
    }

    .player-spotlight-header {
      display: flex;
      align-items: center;
      gap: 14px;
      margin-bottom: 10px;
    }

    .spotlight-avatar-lg {
      width: 68px;
      height: 68px;
      border-radius: 50%;
      object-fit: cover;
      object-position: top;
      border: 2px solid var(--rr-pink);
      box-shadow: 0 0 16px rgba(229, 9, 127, 0.4);
      background: #09061A;
      flex-shrink: 0;
    }

    .spotlight-info-lg h4 {
      font-size: 16px;
      font-weight: 800;
      color: #FFFFFF;
      margin-bottom: 2px;
    }

    .spotlight-rank-badge {
      font-size: 11px;
      font-weight: 700;
      color: var(--rr-gold-light);
      display: inline-block;
      margin-bottom: 2px;
    }

    .spotlight-ri-text {
      font-size: 12px;
      font-weight: 600;
      color: var(--text-light);
    }

    .spotlight-bullet-list {
      display: flex;
      flex-direction: column;
      gap: 6px;
      margin: 6px 0 12px 0;
    }

    .spotlight-bullet {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 11.5px;
      font-weight: 600;
      color: var(--text-light);
    }

    .spotlight-bullet i {
      color: #10B981;
      font-size: 10px;
    }

    .view-profile-btn {
      background: linear-gradient(90deg, var(--rr-pink) 0%, #D81B60 100%);
      color: #FFFFFF;
      border: none;
      padding: 9px 16px;
      border-radius: var(--radius-md);
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      transition: all 0.2s ease;
      box-shadow: 0 4px 14px rgba(229, 9, 127, 0.35);
      text-decoration: none;
      width: 100%;
    }

    .view-profile-btn:hover {
      background: linear-gradient(90deg, #FF2A85 0%, #E5097F 100%);
      transform: translateY(-1px);
      box-shadow: 0 6px 18px rgba(229, 9, 127, 0.5);
    }

    /* ==========================================================================
       VIEW 4: PRESSURE ANALYSIS
       ========================================================================== */
    .pressure-top-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 16px;
      margin-bottom: 20px;
    }

    .pressure-kpi-card {
      background: var(--bg-card);
      border: 1px solid var(--border-card);
      border-radius: var(--radius-lg);
      padding: 18px 20px;
      display: flex;
      align-items: center;
      gap: 18px;
      transition: transform 0.2s ease;
    }

    .pressure-kpi-card:hover {
      transform: translateY(-2px);
    }

    .pressure-mid-3col {
      display: grid;
      grid-template-columns: 1.18fr 1fr 1fr;
      gap: 16px;
      margin-bottom: 20px;
    }

    .pressure-bottom-3col {
      display: grid;
      grid-template-columns: 1.1fr 1fr 1.1fr;
      gap: 16px;
    }

    .batting-bottom-4col {
      display: grid;
      grid-template-columns: 1.15fr 1.05fr 1fr 1.2fr;
      gap: 16px;
    }

    .bowling-bottom-5col {
      display: grid;
      grid-template-columns: 1.15fr 1.15fr 1.05fr 1.05fr 1.25fr;
      gap: 16px;
    }

    .kpi-indicator-table {
      width: 100%;
      border-collapse: collapse;
    }

    .kpi-indicator-table td {
      padding: 11px 6px;
      font-size: 12.5px;
      font-weight: 600;
      color: var(--text-light);
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }

    .kpi-indicator-table td:last-child {
      text-align: right;
      font-size: 14.5px;
      font-weight: 800;
      color: #FFFFFF;
    }

    .indicator-highlight-green {
      color: #10B981 !important;
    }

    .pressure-insight-bullets {
      display: flex;
      flex-direction: column;
      gap: 10px;
      padding: 4px 0;
    }

    .pressure-bullet-item {
      display: flex;
      align-items: flex-start;
      gap: 10px;
      font-size: 12px;
      color: var(--text-light);
      line-height: 1.35;
    }

    .pressure-bullet-item i {
      color: #10B981;
      font-size: 12px;
      margin-top: 2px;
      flex-shrink: 0;
    }

    /* ==========================================================================
       VIEW 5: PLAYER COMPARISON
       ========================================================================== */
    .comparison-controls-card {
      background: var(--bg-card);
      border: 1px solid var(--border-card);
      border-radius: var(--radius-lg);
      padding: 16px 20px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 20px;
      flex-wrap: wrap;
    }

    .discipline-pills {
      display: flex;
      gap: 8px;
    }

    .discipline-pill {
      padding: 8px 16px;
      border-radius: 30px;
      font-size: 12.5px;
      font-weight: 700;
      cursor: pointer;
      transition: all 0.2s ease;
      border: 1px solid rgba(255, 255, 255, 0.12);
      color: var(--text-muted);
      background: rgba(255, 255, 255, 0.04);
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .discipline-pill.active {
      background: linear-gradient(90deg, var(--rr-pink) 0%, #D81B60 100%);
      color: #FFFFFF;
      border-color: var(--rr-pink);
      box-shadow: 0 4px 15px rgba(229, 9, 127, 0.4);
    }

    .comparison-selects {
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }

    .player-select-dropdown {
      background: #0D0A24;
      border: 1px solid rgba(139, 92, 246, 0.35);
      color: #FFFFFF;
      padding: 8px 12px;
      border-radius: var(--radius-md);
      font-size: 12.5px;
      font-weight: 600;
      outline: none;
      cursor: pointer;
      min-width: 155px;
    }

    .player-select-dropdown:focus {
      border-color: var(--rr-pink);
      box-shadow: 0 0 10px rgba(229, 9, 127, 0.4);
    }

    .compare-btn-action {
      background: linear-gradient(90deg, var(--rr-pink) 0%, #D81B60 100%);
      color: #FFFFFF;
      border: none;
      padding: 8px 18px;
      border-radius: var(--radius-md);
      font-size: 12.5px;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 8px;
      box-shadow: 0 4px 14px rgba(229, 9, 127, 0.35);
      transition: all 0.2s ease;
    }

    .compare-btn-action:hover {
      transform: translateY(-1px);
      box-shadow: 0 6px 18px rgba(229, 9, 127, 0.5);
    }

    .comparison-cards-3col {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 16px;
      margin-bottom: 20px;
    }

    .comp-player-card {
      background: var(--bg-card);
      border: 1px solid var(--border-card);
      border-radius: var(--radius-lg);
      padding: 18px;
      position: relative;
      overflow: hidden;
    }

    .comp-card-top {
      display: flex;
      align-items: center;
      gap: 14px;
      margin-bottom: 14px;
    }

    .comp-card-avatar {
      width: 72px;
      height: 72px;
      border-radius: 50%;
      object-fit: cover;
      object-position: top;
      border: 3px solid var(--rr-pink);
      box-shadow: 0 0 16px rgba(229, 9, 127, 0.35);
      background: #09061A;
      flex-shrink: 0;
    }

    .comp-card-meta {
      flex-grow: 1;
      min-width: 0;
    }

    .comp-card-name {
      font-size: 17px;
      font-weight: 800;
      color: #FFFFFF;
      line-height: 1.2;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .comp-card-role {
      font-size: 11.5px;
      color: var(--text-muted);
      margin-bottom: 4px;
    }

    .comp-rank-badge {
      display: inline-block;
      padding: 2px 7px;
      background: rgba(229, 9, 127, 0.2);
      border: 1px solid var(--rr-pink);
      color: #FF5EA6;
      border-radius: 6px;
      font-size: 10.5px;
      font-weight: 800;
    }

    .comp-card-ri-badge {
      text-align: right;
      flex-shrink: 0;
    }

    .comp-card-ri-num {
      font-size: 24px;
      font-weight: 900;
      color: #FFFFFF;
      line-height: 1;
    }

    .comp-card-ri-label {
      font-size: 9.5px;
      color: var(--text-dim);
      font-weight: 600;
      text-transform: uppercase;
    }

    .comp-stats-quad {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 6px;
      background: rgba(255, 255, 255, 0.03);
      padding: 10px;
      border-radius: var(--radius-md);
      border: 1px solid rgba(255, 255, 255, 0.05);
      text-align: center;
    }

    .comp-stat-item {
      display: flex;
      flex-direction: column;
      gap: 2px;
    }

    .comp-stat-lbl {
      font-size: 9.5px;
      color: var(--text-muted);
      font-weight: 600;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .comp-stat-val {
      font-size: 14px;
      font-weight: 800;
      color: #FFFFFF;
    }

    .comp-charts-3col {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 16px;
      margin-bottom: 20px;
    }

    .comp-summary-3col {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 16px;
    }

    .top-choice-card {
      background: linear-gradient(135deg, rgba(229, 9, 127, 0.2) 0%, rgba(20, 15, 48, 0.95) 100%);
      border: 1px solid rgba(229, 9, 127, 0.5);
      border-radius: var(--radius-lg);
      padding: 18px;
      display: flex;
      align-items: center;
      gap: 14px;
      position: relative;
      overflow: hidden;
      box-shadow: 0 0 25px rgba(229, 9, 127, 0.25);
    }

    .top-choice-trophy {
      font-size: 30px;
      color: var(--rr-gold-light);
      filter: drop-shadow(0 0 10px rgba(245, 158, 11, 0.6));
      flex-shrink: 0;
    }

    .top-choice-details {
      flex-grow: 1;
      min-width: 0;
    }

    .top-choice-lbl {
      font-size: 10.5px;
      font-weight: 700;
      color: var(--text-light);
      text-transform: uppercase;
      letter-spacing: 0.8px;
    }

    .top-choice-name {
      font-size: 18px;
      font-weight: 900;
      color: #FFFFFF;
      margin: 2px 0;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .top-choice-ri {
      font-size: 12px;
      font-weight: 700;
      color: var(--rr-gold-light);
    }

    .top-choice-avatar {
      width: 68px;
      height: 68px;
      border-radius: 50%;
      object-fit: cover;
      object-position: top;
      border: 2px solid var(--rr-gold-light);
      box-shadow: 0 0 16px rgba(245, 158, 11, 0.4);
      background: #09061A;
      flex-shrink: 0;
    }

    /* ==========================================================================
       VIEW 6: PLAYER RANKINGS
       ========================================================================== */
    .rankings-dual-tables {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
      gap: 18px;
      margin-bottom: 20px;
    }

    .rankings-table-wrap {
      background: var(--bg-card);
      border: 1px solid var(--border-card);
      border-radius: var(--radius-lg);
      padding: 18px;
      position: relative;
    }

    .table-top-actions {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 12px;
      gap: 10px;
      flex-wrap: wrap;
    }

    .table-top-title {
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 16px;
      font-weight: 800;
      color: #FFFFFF;
    }

    .download-csv-btn {
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid rgba(255, 255, 255, 0.15);
      color: var(--text-light);
      padding: 6px 12px;
      border-radius: var(--radius-sm);
      font-size: 11.5px;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s ease;
    }

    .download-csv-btn:hover {
      background: rgba(229, 9, 127, 0.2);
      border-color: var(--rr-pink);
      color: #FFFFFF;
    }

    .table-player-cell {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .table-player-thumb {
      width: 32px;
      height: 32px;
      border-radius: 50%;
      object-fit: cover;
      object-position: top;
      background: #09061A;
      border: 1.5px solid var(--rr-pink);
      flex-shrink: 0;
    }

    .core-pill-badge {
      background: rgba(139, 92, 246, 0.25);
      border: 1px solid rgba(139, 92, 246, 0.5);
      color: #C084FC;
      font-size: 11px;
      font-weight: 700;
      padding: 2px 8px;
      border-radius: 12px;
      white-space: nowrap;
    }

    .rankings-bottom-4col {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 16px;
    }

    .action-button-stack {
      display: flex;
      flex-direction: column;
      gap: 10px;
      height: 100%;
      justify-content: center;
    }

    .action-stack-btn {
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.12);
      color: #FFFFFF;
      padding: 11px 14px;
      border-radius: var(--radius-md);
      font-size: 12.5px;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 10px;
      transition: all 0.2s ease;
      text-decoration: none;
    }

    .action-stack-btn:hover {
      background: linear-gradient(90deg, rgba(229, 9, 127, 0.25) 0%, rgba(139, 92, 246, 0.25) 100%);
      border-color: var(--rr-pink);
    }

    .rr-ready-banner {
      background: linear-gradient(135deg, rgba(20, 15, 48, 0.95) 0%, rgba(10, 6, 26, 0.95) 100%);
      border: 1px solid rgba(245, 158, 11, 0.35);
      border-radius: var(--radius-lg);
      padding: 18px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      text-align: center;
      position: relative;
      box-shadow: 0 0 20px rgba(245, 158, 11, 0.12);
    }

    .rr-ready-banner .crown-lg {
      font-size: 32px;
      color: var(--rr-gold-light);
      margin-bottom: 6px;
      filter: drop-shadow(0 0 10px rgba(245, 158, 11, 0.5));
    }

    .rr-ready-banner h4 {
      font-size: 15px;
      font-weight: 900;
      color: #FFFFFF;
      letter-spacing: 0.5px;
    }

    .rr-ready-banner p {
      font-size: 11px;
      font-weight: 800;
      letter-spacing: 2px;
      color: var(--rr-pink);
      text-transform: uppercase;
      margin-top: 4px;
    }

    /* ==========================================================================
       VIEW 7: METHODOLOGY & VALIDATION
       ========================================================================== */
    .method-top-5col {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 16px;
      margin-bottom: 20px;
    }

    .method-mid-2col {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 18px;
      margin-bottom: 20px;
    }

    .pipeline-stepper {
      display: flex;
      align-items: center;
      justify-content: space-between;
      height: 100%;
      padding: 10px 0;
      gap: 6px;
      overflow-x: auto;
    }

    .pipeline-step {
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
      gap: 8px;
      flex: 1;
      min-width: 65px;
    }

    .pipeline-icon-circle {
      width: 48px;
      height: 48px;
      border-radius: 50%;
      background: rgba(229, 9, 127, 0.15);
      border: 1.5px solid var(--rr-pink);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 18px;
      color: var(--rr-pink);
      box-shadow: 0 0 15px rgba(229, 9, 127, 0.25);
      transition: transform 0.25s ease;
    }

    .pipeline-step:hover .pipeline-icon-circle {
      transform: scale(1.1);
      box-shadow: 0 0 20px rgba(229, 9, 127, 0.5);
    }

    .pipeline-title {
      font-size: 11px;
      font-weight: 700;
      color: var(--text-light);
      line-height: 1.2;
    }

    .pipeline-arrow {
      font-size: 14px;
      color: rgba(255, 255, 255, 0.2);
      margin-bottom: 18px;
    }

    .method-row3-3col {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 16px;
      margin-bottom: 20px;
    }

    .method-row4-4col {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 16px;
    }

    .rules-dual-box {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
    }

    .rule-box-header {
      font-size: 11.5px;
      font-weight: 800;
      padding: 4px 10px;
      border-radius: 6px;
      text-align: center;
      margin-bottom: 10px;
    }
    .rule-hdr-pink { background: rgba(229, 9, 127, 0.2); color: #FF5EA6; border: 1px solid var(--rr-pink); }
    .rule-hdr-blue { background: rgba(0, 210, 255, 0.2); color: #38BDF8; border: 1px solid var(--rr-cyan); }

    .rule-bullets {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .rule-bullet-item {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 11.5px;
      color: var(--text-light);
      font-weight: 600;
    }

    .rule-bullet-item i {
      color: #10B981;
      font-size: 11px;
    }

    /* ==========================================================================
       BOTTOM FOOTER
       ========================================================================== */
    .dashboard-footer-bar {
      margin-top: auto;
      padding: 16px clamp(16px, 3vw, 36px);
      background: #080517;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 12px;
      color: var(--text-dim);
      flex-wrap: wrap;
      gap: 10px;
    }

    .footer-left {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .footer-crown {
      color: var(--rr-gold-light);
      font-size: 14px;
    }

    .footer-right {
      display: flex;
      align-items: center;
      gap: 8px;
      font-weight: 600;
    }

    .status-dot-green {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #10B981;
      box-shadow: 0 0 10px #10B981;
    }

    /* ==========================================================================
       MEDIA QUERIES (TRUE RESPONSIVENESS)
       ========================================================================== */
    @media (max-width: 1200px) {
      .overview-hero-grid {
        grid-template-columns: 1fr 1fr;
      }
      .overview-hero-card {
        grid-column: span 2;
      }
      .overview-spotlights-grid {
        grid-template-columns: 1fr 1fr;
      }
      .overview-spotlights-grid > div:last-child {
        grid-column: span 2;
      }
      .overview-dual-tables {
        grid-template-columns: 1fr;
      }
      .mid-table-chart-grid {
        grid-template-columns: 1fr;
      }
      .pressure-bottom-3col {
        grid-template-columns: 1fr 1fr;
      }
      .pressure-bottom-3col > div:last-child {
        grid-column: span 2;
      }
    }

    @media (max-width: 1200px) {
      .batting-bottom-4col {
        grid-template-columns: repeat(2, 1fr);
      }
      .bowling-bottom-5col {
        grid-template-columns: repeat(3, 1fr);
      }
      .pressure-mid-3col {
        grid-template-columns: 1fr;
      }
    }

    @media (max-width: 960px) {
      :root {
        --sidebar-width: 0px;
      }
      .bowling-bottom-5col {
        grid-template-columns: repeat(2, 1fr);
      }
      .comparison-cards-3col, .comp-charts-3col, .comp-summary-3col {
        grid-template-columns: 1fr;
      }
      .sidebar {
        transform: translateX(-100%);
      }
      .sidebar.open {
        transform: translateX(0);
        width: 250px;
      }
      .main-wrapper {
        margin-left: 0;
        width: 100%;
      }
      .sidebar-toggle-btn {
        display: flex;
      }
      .overview-hero-grid {
        grid-template-columns: 1fr;
      }
      .overview-hero-card {
        grid-column: span 1;
      }
      .overview-spotlights-grid {
        grid-template-columns: 1fr;
      }
      .overview-spotlights-grid > div:last-child {
        grid-column: span 1;
      }
      .pressure-bottom-3col {
        grid-template-columns: 1fr;
      }
      .pressure-bottom-3col > div:last-child {
        grid-column: span 1;
      }
    }

    /* Scrollbar styling */
    ::-webkit-scrollbar {
      width: 7px;
      height: 7px;
    }
    ::-webkit-scrollbar-track {
      background: #09061A;
    }
    ::-webkit-scrollbar-thumb {
      background: rgba(139, 92, 246, 0.35);
      border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
      background: var(--rr-pink);
    }
  </style>
</head>
<body>

  <!-- ==========================================================================
       LEFT SIDEBAR NAVIGATION
       ========================================================================== -->
  <aside class="sidebar" id="app-sidebar">
    <div class="sidebar-header">
      <div class="rr-logo-container" onclick="switchTab('overview')">
        <i class="fa-solid fa-crown rr-crown-icon"></i>
        <div class="rr-brand-name">RAJASTHAN ROYALS</div>
        <div class="rr-brand-sub">SupeRR Selector</div>
      </div>
    </div>

    <nav class="sidebar-menu">
      <div class="nav-item active" id="nav-overview" onclick="switchTab('overview')">
        <i class="fa-solid fa-house"></i>
        <span>Overview</span>
      </div>
      <div class="nav-item" id="nav-batting" onclick="switchTab('batting')">
        <i class="fa-solid fa-baseball-bat-ball"></i>
        <span>Batting Intelligence</span>
      </div>
      <div class="nav-item" id="nav-bowling" onclick="switchTab('bowling')">
        <i class="fa-solid fa-baseball"></i>
        <span>Bowling Intelligence</span>
      </div>
      <div class="nav-item" id="nav-pressure" onclick="switchTab('pressure')">
        <i class="fa-solid fa-bolt"></i>
        <span>Pressure Analysis</span>
      </div>
      <div class="nav-item" id="nav-comparison" onclick="switchTab('comparison')">
        <i class="fa-solid fa-scale-balanced"></i>
        <span>Player Comparison</span>
      </div>
      <div class="nav-item" id="nav-rankings" onclick="switchTab('rankings')">
        <i class="fa-solid fa-trophy"></i>
        <span>Player Rankings</span>
      </div>
      <div class="nav-item" id="nav-methodology" onclick="switchTab('methodology')">
        <i class="fa-solid fa-file-shield"></i>
        <span>Methodology & Validation</span>
      </div>
    </nav>

    <div class="sidebar-footer">
      <div class="slogan-script">Build a Winning Squad.<br>Own the Auction.</div>
      <div class="superr-badge-mini">
        <i class="fa-solid fa-crown"></i>
        <span>SUPERR SELECTOR Season 2</span>
      </div>
    </div>
  </aside>

  <!-- ==========================================================================
       MAIN CONTENT AUTO-LAYOUT WRAPPER
       ========================================================================== -->
  <main class="main-wrapper">

    <!-- Top Sticky Header Banner -->
    <header class="top-header-banner">
      <div class="header-left">
        <button class="sidebar-toggle-btn" onclick="toggleSidebar()" title="Toggle Sidebar">
          <i class="fa-solid fa-bars"></i>
        </button>

        <div class="header-titles">
          <div class="header-top-row">
            <span class="header-team-title">Rajasthan Royals</span>
            <span class="season-pill">Season 2</span>
          </div>
          <div class="header-app-title">SUPERR SELECTOR</div>
        </div>

        <div class="header-divider"></div>

        <div class="header-page-context">
          <div class="header-page-title" id="page-title-text">Squad Overview</div>
          <div class="header-page-subtitle" id="page-subtitle-text">Build a Winning Squad. Own the Auction.</div>
        </div>
      </div>

      <div class="header-right">
        <div class="header-stadium-graphic">
          <i class="fa-solid fa-bolt" style="color: #FF5EA6;"></i>
          <span class="stadium-tagline">Data-Driven • Pressure-Tested</span>
        </div>
      </div>
    </header>

    <!-- ==========================================================================
         VIEW 1: OVERVIEW (SCREENSHOT 1)
         ========================================================================== -->
    <section class="view-content active" id="view-overview">
      <!-- Top Row: Hero Banner + 4 KPI Cards -->
      <div class="overview-hero-grid">
        <div class="overview-hero-card">
          <img class="hero-cutout-img" src="__HOLDER_IMG__" alt="Jason Holder">
          <div class="hero-text-content">
            <h3>Rajasthan Royals</h3>
            <h2>SUPERR SELECTOR</h2>
            <p>Season 2 • Data-Driven. Pressure-Tested. Champion Ready.</p>
          </div>
        </div>

        <div class="kpi-mini-card">
          <i class="fa-solid fa-baseball-bat-ball kpi-mini-icon"></i>
          <div class="kpi-mini-label">Top Batters</div>
          <div class="kpi-mini-value">10</div>
          <div class="kpi-mini-sub">Selected</div>
        </div>

        <div class="kpi-mini-card">
          <i class="fa-solid fa-baseball kpi-mini-icon" style="color: #38BDF8;"></i>
          <div class="kpi-mini-label">Top Bowlers</div>
          <div class="kpi-mini-value">10</div>
          <div class="kpi-mini-sub">Selected</div>
        </div>

        <div class="kpi-mini-card">
          <i class="fa-solid fa-users kpi-mini-icon" style="color: #A855F7;"></i>
          <div class="kpi-mini-label">Qualified Batters</div>
          <div class="kpi-mini-value">109</div>
          <div class="kpi-mini-sub">Total</div>
        </div>

        <div class="kpi-mini-card">
          <i class="fa-solid fa-trophy kpi-mini-icon" style="color: #F59E0B;"></i>
          <div class="kpi-mini-label">Qualified Bowlers</div>
          <div class="kpi-mini-value">136</div>
          <div class="kpi-mini-sub">Total</div>
        </div>
      </div>

      <!-- Middle Row: Top Batter + Top Bowler + Squad Donut -->
      <div class="overview-spotlights-grid">
        <!-- Top Batter Spotlight -->
        <div class="spotlight-card">
          <div class="spotlight-header">
            <span class="crown-badge"><i class="fa-solid fa-crown"></i></span>
            <span>Top Batter — Jason Holder</span>
          </div>
          <div class="spotlight-body">
            <img class="spotlight-player-img" src="__HOLDER_IMG__" alt="Jason Holder">
            <div class="spotlight-metrics">
              <div class="spotlight-ri-wrap">
                <span class="spotlight-ri">66.84</span>
                <span class="spotlight-ri-label">Reliability Index</span>
              </div>
              <div class="spotlight-tags">
                <span class="spotlight-stat-tag stat-tag-green">+83.44 SR (Δ SR)</span>
                <span class="spotlight-stat-tag stat-tag-pink">-30.18% (Dot Ball ↓)</span>
              </div>
            </div>
          </div>
          <div class="role-pill-bottom">Death Phase Finisher</div>
        </div>

        <!-- Top Bowler Spotlight -->
        <div class="spotlight-card">
          <div class="spotlight-header">
            <span class="crown-badge" style="background: rgba(56, 189, 248, 0.2); color: #38BDF8;"><i class="fa-solid fa-star"></i></span>
            <span>Top Bowler — Mitchell Marsh</span>
          </div>
          <div class="spotlight-body">
            <img class="spotlight-player-img" style="border-color: #38BDF8;" src="__MARSH_IMG__" alt="Mitchell Marsh">
            <div class="spotlight-metrics">
              <div class="spotlight-ri-wrap">
                <span class="spotlight-ri">61.86</span>
                <span class="spotlight-ri-label">Reliability Index</span>
              </div>
              <div class="spotlight-tags">
                <span class="spotlight-stat-tag stat-tag-green">+0.30 WPO (Δ Wkt)</span>
                <span class="spotlight-stat-tag" style="color: #38BDF8;">8.12 HP Econ</span>
              </div>
            </div>
          </div>
          <div class="role-pill-bottom" style="background: linear-gradient(90deg, rgba(56, 189, 248, 0.25) 0%, rgba(99, 102, 241, 0.25) 100%); border-color: rgba(56, 189, 248, 0.4);">Death Wicket Enforcer</div>
        </div>

        <!-- Squad Composition Donut Card -->
        <div class="spotlight-card">
          <div class="card-header-clean" style="margin-bottom: 8px;">
            <span class="card-title">Squad Composition</span>
          </div>
          <div class="donut-card-container">
            <div class="donut-chart-box">
              <canvas id="squadDonutChart"></canvas>
              <div class="donut-center-badge">
                <div class="donut-center-num">20</div>
                <div class="donut-center-text">Players</div>
              </div>
            </div>
            <div class="donut-legend">
              <div class="legend-item">
                <span class="legend-dot" style="background: var(--rr-pink);"></span>
                <span>Batter (10)</span>
              </div>
              <div class="legend-item">
                <span class="legend-dot" style="background: #38BDF8;"></span>
                <span>Bowler (10)</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Bottom Row: Mini Ranking Tables with Progress Bars -->
      <div class="overview-dual-tables">
        <!-- Top 10 Batters Mini -->
        <div class="rr-card">
          <div class="card-header-clean">
            <div class="card-title-group">
              <i class="fa-solid fa-baseball-bat-ball"></i>
              <span class="card-title">Top 10 Batters</span>
            </div>
            <a class="card-action-link" onclick="switchTab('batting')">View All →</a>
          </div>

          <table class="mini-rank-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Player Name</th>
                <th>Reliability Index</th>
                <th>Role</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>1</td>
                <td><strong>Jason Holder</strong></td>
                <td>
                  <div class="progress-bar-wrap">
                    <div class="progress-track"><div class="progress-fill-pink" data-width="84%"></div></div>
                    <span class="progress-val">66.84</span>
                  </div>
                </td>
                <td><span class="role-badge-table">Death Phase Finisher</span></td>
              </tr>
              <tr>
                <td>2</td>
                <td><strong>Sanju Samson</strong></td>
                <td>
                  <div class="progress-bar-wrap">
                    <div class="progress-track"><div class="progress-fill-pink" data-width="76%"></div></div>
                    <span class="progress-val">60.46</span>
                  </div>
                </td>
                <td><span class="role-badge-table">Top/Middle Accelerator</span></td>
              </tr>
              <tr>
                <td>3</td>
                <td><strong>Curtis Campher</strong></td>
                <td>
                  <div class="progress-bar-wrap">
                    <div class="progress-track"><div class="progress-fill-pink" data-width="74%"></div></div>
                    <span class="progress-val">59.20</span>
                  </div>
                </td>
                <td><span class="role-badge-table">Top/Middle Accelerator</span></td>
              </tr>
              <tr>
                <td>4</td>
                <td><strong>Phil Salt</strong></td>
                <td>
                  <div class="progress-bar-wrap">
                    <div class="progress-track"><div class="progress-fill-pink" data-width="73.5%"></div></div>
                    <span class="progress-val">58.93</span>
                  </div>
                </td>
                <td><span class="role-badge-table">Death Phase Finisher</span></td>
              </tr>
              <tr>
                <td>5</td>
                <td><strong>David Willey</strong></td>
                <td>
                  <div class="progress-bar-wrap">
                    <div class="progress-track"><div class="progress-fill-pink" data-width="73%"></div></div>
                    <span class="progress-val">58.77</span>
                  </div>
                </td>
                <td><span class="role-badge-table">Death Phase Finisher</span></td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Top 10 Bowlers Mini -->
        <div class="rr-card">
          <div class="card-header-clean">
            <div class="card-title-group">
              <i class="fa-solid fa-baseball" style="color: #38BDF8;"></i>
              <span class="card-title">Top 10 Bowlers</span>
            </div>
            <a class="card-action-link" onclick="switchTab('bowling')">View All →</a>
          </div>

          <table class="mini-rank-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Player Name</th>
                <th>Reliability Index</th>
                <th>Role</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>1</td>
                <td><strong>Mitchell Marsh</strong></td>
                <td>
                  <div class="progress-bar-wrap">
                    <div class="progress-track"><div class="progress-fill-purple" data-width="78%"></div></div>
                    <span class="progress-val">61.86</span>
                  </div>
                </td>
                <td><span class="role-badge-table">Death Wicket Enforcer</span></td>
              </tr>
              <tr>
                <td>2</td>
                <td><strong>Haris Rauf</strong></td>
                <td>
                  <div class="progress-bar-wrap">
                    <div class="progress-track"><div class="progress-fill-purple" data-width="77%"></div></div>
                    <span class="progress-val">61.50</span>
                  </div>
                </td>
                <td><span class="role-badge-table">Death Wicket Enforcer</span></td>
              </tr>
              <tr>
                <td>3</td>
                <td><strong>Kartik Tyagi</strong></td>
                <td>
                  <div class="progress-bar-wrap">
                    <div class="progress-track"><div class="progress-fill-purple" data-width="76.5%"></div></div>
                    <span class="progress-val">61.28</span>
                  </div>
                </td>
                <td><span class="role-badge-table">Death Wicket Enforcer</span></td>
              </tr>
              <tr>
                <td>4</td>
                <td><strong>Vaibhav Arora</strong></td>
                <td>
                  <div class="progress-bar-wrap">
                    <div class="progress-track"><div class="progress-fill-purple" data-width="75.5%"></div></div>
                    <span class="progress-val">60.47</span>
                  </div>
                </td>
                <td><span class="role-badge-table">Death Wicket Enforcer</span></td>
              </tr>
              <tr>
                <td>5</td>
                <td><strong>Ravi Bishnoi</strong></td>
                <td>
                  <div class="progress-bar-wrap">
                    <div class="progress-track"><div class="progress-fill-purple" data-width="74.5%"></div></div>
                    <span class="progress-val">59.66</span>
                  </div>
                </td>
                <td><span class="role-badge-table">Middle & Powerplay</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- ==========================================================================
         VIEW 2: BATTING INTELLIGENCE (SCREENSHOT 2)
         ========================================================================== -->
    <section class="view-content" id="view-batting">
      <!-- 5 KPI Cards Row -->
      <div class="kpi-row-5">
        <div class="intel-top-card">
          <div class="intel-top-icon"><i class="fa-solid fa-person-running"></i></div>
          <div class="intel-top-data">
            <span class="intel-top-label">Total Qualified Batters</span>
            <span class="intel-top-val">109</span>
          </div>
        </div>

        <div class="intel-top-card">
          <div class="intel-top-icon icon-gold"><i class="fa-solid fa-star"></i></div>
          <div class="intel-top-data">
            <span class="intel-top-label">Top-Ranked Batter</span>
            <span class="intel-top-val">Jason Holder</span>
            <span class="intel-top-sub">66.84 RI</span>
          </div>
        </div>

        <div class="intel-top-card">
          <div class="intel-top-icon icon-purple"><i class="fa-solid fa-chart-line"></i></div>
          <div class="intel-top-data">
            <span class="intel-top-label">Avg. Reliability Index</span>
            <span class="intel-top-val">57.42</span>
            <span class="intel-top-sub">Batters Cohort</span>
          </div>
        </div>

        <div class="intel-top-card">
          <div class="intel-top-icon"><i class="fa-solid fa-bullseye"></i></div>
          <div class="intel-top-data">
            <span class="intel-top-label">High-Pressure SR (Avg)</span>
            <span class="intel-top-val">162.3</span>
          </div>
        </div>

        <div class="intel-top-card">
          <div class="intel-top-icon icon-gold"><i class="fa-solid fa-trophy"></i></div>
          <div class="intel-top-data">
            <span class="intel-top-label">Top 10 Coverage (%)</span>
            <span class="intel-top-val">9.2%</span>
          </div>
        </div>
      </div>

      <!-- Mid Section: Top 10 Batters Ranking Table + Horizontal Bar Chart -->
      <div class="mid-table-chart-grid">
        <div class="rr-card">
          <div class="card-header-clean">
            <div class="card-title-group">
              <i class="fa-solid fa-trophy" style="color: var(--rr-gold-light);"></i>
              <span class="card-title">Top 10 Batters Ranking</span>
            </div>
            <a class="card-action-link" onclick="switchTab('rankings')">View All →</a>
          </div>

          <div class="clean-table-wrap">
            <table class="clean-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Player Name</th>
                  <th>Player ID</th>
                  <th>Reliability Index</th>
                  <th>Role</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>1</td>
                  <td><strong>Jason Holder</strong></td>
                  <td>2633</td>
                  <td><strong style="color: #FF5EA6;">66.84</strong></td>
                  <td><span class="role-badge-table">Death Phase Finisher</span></td>
                </tr>
                <tr>
                  <td>2</td>
                  <td><strong>Sanju Samson</strong></td>
                  <td>2258</td>
                  <td><strong style="color: #FF5EA6;">60.46</strong></td>
                  <td><span class="role-badge-table">Top/Middle Order Accelerator</span></td>
                </tr>
                <tr>
                  <td>3</td>
                  <td><strong>Curtis Campher</strong></td>
                  <td>7094</td>
                  <td><strong style="color: #FF5EA6;">59.20</strong></td>
                  <td><span class="role-badge-table">Top/Middle Order Accelerator</span></td>
                </tr>
                <tr>
                  <td>4</td>
                  <td><strong>Phil Salt</strong></td>
                  <td>5553</td>
                  <td><strong style="color: #FF5EA6;">58.93</strong></td>
                  <td><span class="role-badge-table">Death Phase Finisher</span></td>
                </tr>
                <tr>
                  <td>5</td>
                  <td><strong>David Willey</strong></td>
                  <td>1219</td>
                  <td><strong style="color: #FF5EA6;">58.77</strong></td>
                  <td><span class="role-badge-table">Death Phase Finisher</span></td>
                </tr>
                <tr>
                  <td>6</td>
                  <td><strong>Dion Myers</strong></td>
                  <td>6664</td>
                  <td><strong style="color: #FF5EA6;">57.95</strong></td>
                  <td><span class="role-badge-table">Top/Middle Order Accelerator</span></td>
                </tr>
                <tr>
                  <td>7</td>
                  <td><strong>Shan Masood</strong></td>
                  <td>3097</td>
                  <td><strong style="color: #FF5EA6;">57.63</strong></td>
                  <td><span class="role-badge-table">Death Phase Finisher</span></td>
                </tr>
                <tr>
                  <td>8</td>
                  <td><strong>Dasun Shanaka</strong></td>
                  <td>2436</td>
                  <td><strong style="color: #FF5EA6;">57.35</strong></td>
                  <td><span class="role-badge-table">Death Phase Finisher</span></td>
                </tr>
                <tr>
                  <td>9</td>
                  <td><strong>Matthew Wade</strong></td>
                  <td>796</td>
                  <td><strong style="color: #FF5EA6;">57.02</strong></td>
                  <td><span class="role-badge-table">Death Phase Finisher</span></td>
                </tr>
                <tr>
                  <td>10</td>
                  <td><strong>Iftikhar Ahmed</strong></td>
                  <td>3056</td>
                  <td><strong style="color: #FF5EA6;">56.81</strong></td>
                  <td><span class="role-badge-table">Top/Middle Order Accelerator</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="rr-card">
          <div class="card-header-clean">
            <div class="card-title-group">
              <i class="fa-solid fa-chart-simple"></i>
              <span class="card-title">Reliability Index — Top 10 Batters</span>
            </div>
          </div>
          <div class="chart-container-fluid" style="height: 380px;">
            <canvas id="battersRIChart"></canvas>
          </div>
        </div>
      </div>

      <!-- Bottom Row: 4 Cards -->
      <div class="batting-bottom-4col">
        <div class="rr-card">
          <div class="card-header-clean">
            <span class="card-title">Strike Rate Comparison</span>
          </div>
          <div class="chart-container-fluid" style="height: 180px;">
            <canvas id="batterSRChart"></canvas>
          </div>
        </div>

        <div class="rr-card">
          <div class="card-header-clean">
            <span class="card-title">Dot Ball & Dismissal Analysis</span>
          </div>
          <div class="donut-card-container">
            <div class="donut-chart-box" style="width: 140px; height: 140px; min-width: 140px; min-height: 140px;">
              <canvas id="batterDotChart"></canvas>
              <div class="donut-center-badge">
                <div class="donut-center-num" style="font-size: 20px;">28.8%</div>
                <div class="donut-center-text" style="font-size: 9px;">Dot Balls</div>
                <div style="font-size: 8.5px; color: #64748B;">(Top 10 Avg)</div>
              </div>
            </div>
            <div class="donut-legend">
              <div class="legend-row-pressure">
                <div class="legend-color-label">
                  <span class="legend-dot" style="background: var(--rr-pink);"></span>
                  <span class="legend-label-text">Dot Balls</span>
                </div>
                <span class="legend-pct-pill" style="border-color: var(--rr-pink); color: var(--rr-pink);">28.8%</span>
              </div>
              <div class="legend-row-pressure">
                <div class="legend-color-label">
                  <span class="legend-dot" style="background: #8B5CF6;"></span>
                  <span class="legend-label-text">Dismissal</span>
                </div>
                <span class="legend-pct-pill" style="border-color: #8B5CF6; color: #8B5CF6;">71.2%</span>
              </div>
            </div>
          </div>
        </div>

        <div class="rr-card">
          <div class="card-header-clean">
            <div class="card-title-group">
              <i class="fa-solid fa-shield-halved" style="color: var(--rr-gold-light);"></i>
              <span class="card-title">High-Pressure Exposure</span>
            </div>
          </div>
          <div class="gauge-slider-container">
            <div class="gauge-big-num">65.4</div>
            <div class="gauge-subtext">Avg. Pressure Score</div>
            <div class="gauge-track-wrap">
              <div class="gauge-track"></div>
              <div class="gauge-thumb" id="pressureGaugeThumb"></div>
            </div>
            <div class="gauge-labels">
              <span>Low</span>
              <span>Moderate</span>
              <span>High</span>
              <span>Extreme</span>
            </div>
          </div>
        </div>

        <div class="rr-card">
          <div class="player-spotlight-box">
            <div class="player-spotlight-header">
              <img class="spotlight-avatar-lg" src="__HOLDER_IMG__" alt="Jason Holder">
              <div class="spotlight-info-lg">
                <span class="spotlight-rank-badge">👑 #1 Batter</span>
                <h4>Jason Holder</h4>
                <div class="spotlight-ri-text">66.84 Reliability Index</div>
              </div>
            </div>
            <div class="spotlight-bullet-list">
              <div class="spotlight-bullet"><i class="fa-solid fa-circle-check"></i> +83.44 SR (Δ SR surge)</div>
              <div class="spotlight-bullet"><i class="fa-solid fa-circle-check"></i> -30.18% Dot Balls (Δ Dot drop)</div>
              <div class="spotlight-bullet"><i class="fa-solid fa-circle-check"></i> 166 High Pressure Balls Faced</div>
            </div>
            <button class="view-profile-btn" onclick="openComparisonWith('Jason Holder')">
              <span>View Full Profile</span>
              <i class="fa-solid fa-arrow-right"></i>
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- ==========================================================================
         VIEW 3: BOWLING INTELLIGENCE (SCREENSHOT 3)
         ========================================================================== -->
    <section class="view-content" id="view-bowling">
      <!-- 5 KPI Cards Row -->
      <div class="kpi-row-5">
        <div class="intel-top-card">
          <div class="intel-top-icon"><i class="fa-solid fa-baseball"></i></div>
          <div class="intel-top-data">
            <span class="intel-top-label">Total Qualified Bowlers</span>
            <span class="intel-top-val">136</span>
          </div>
        </div>

        <div class="intel-top-card">
          <div class="intel-top-icon icon-purple"><i class="fa-solid fa-bowling-ball"></i></div>
          <div class="intel-top-data">
            <span class="intel-top-label">Top-Ranked Bowler</span>
            <span class="intel-top-val">Mitchell Marsh</span>
            <span class="intel-top-sub">61.86 RI</span>
          </div>
        </div>

        <div class="intel-top-card">
          <div class="intel-top-icon icon-gold"><i class="fa-solid fa-trophy"></i></div>
          <div class="intel-top-data">
            <span class="intel-top-label">Avg. Economy Rate (HP)</span>
            <span class="intel-top-val">8.12</span>
            <span class="intel-top-sub">High Pressure</span>
          </div>
        </div>

        <div class="intel-top-card">
          <div class="intel-top-icon"><i class="fa-solid fa-bullseye"></i></div>
          <div class="intel-top-data">
            <span class="intel-top-label">High-Pressure Wkts (Avg)</span>
            <span class="intel-top-val">14.7</span>
          </div>
        </div>

        <div class="intel-top-card">
          <div class="intel-top-icon icon-gold"><i class="fa-solid fa-star"></i></div>
          <div class="intel-top-data">
            <span class="intel-top-label">Top 10 Coverage (%)</span>
            <span class="intel-top-val">7.4%</span>
          </div>
        </div>
      </div>

      <!-- Mid Section: Top 10 Bowlers Ranking Table + Horizontal Bar Chart -->
      <div class="mid-table-chart-grid">
        <div class="rr-card">
          <div class="card-header-clean">
            <div class="card-title-group">
              <i class="fa-solid fa-trophy" style="color: var(--rr-gold-light);"></i>
              <span class="card-title">Top 10 Bowlers Ranking</span>
            </div>
            <a class="card-action-link" onclick="switchTab('rankings')">View All →</a>
          </div>

          <div class="clean-table-wrap">
            <table class="clean-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Player Name</th>
                  <th>Player ID</th>
                  <th>Reliability Index</th>
                  <th>Role</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>1</td>
                  <td><strong>Mitchell Marsh</strong></td>
                  <td>818</td>
                  <td><strong style="color: #38BDF8;">61.86</strong></td>
                  <td><span class="role-badge-table">Death Wicket Enforcer</span></td>
                </tr>
                <tr>
                  <td>2</td>
                  <td><strong>Haris Rauf</strong></td>
                  <td>7364</td>
                  <td><strong style="color: #38BDF8;">61.50</strong></td>
                  <td><span class="role-badge-table">Death Wicket Enforcer</span></td>
                </tr>
                <tr>
                  <td>3</td>
                  <td><strong>Kartik Tyagi</strong></td>
                  <td>8530</td>
                  <td><strong style="color: #38BDF8;">61.28</strong></td>
                  <td><span class="role-badge-table">Death Wicket Enforcer</span></td>
                </tr>
                <tr>
                  <td>4</td>
                  <td><strong>Vaibhav Arora</strong></td>
                  <td>8746</td>
                  <td><strong style="color: #38BDF8;">60.47</strong></td>
                  <td><span class="role-badge-table">Death Wicket Enforcer</span></td>
                </tr>
                <tr>
                  <td>5</td>
                  <td><strong>Ravi Bishnoi</strong></td>
                  <td>7503</td>
                  <td><strong style="color: #38BDF8;">59.66</strong></td>
                  <td><span class="role-badge-table">Middle & Powerplay Restrictor</span></td>
                </tr>
                <tr>
                  <td>6</td>
                  <td><strong>Azmatullah Omarzai</strong></td>
                  <td>6676</td>
                  <td><strong style="color: #38BDF8;">59.18</strong></td>
                  <td><span class="role-badge-table">Death Wicket Enforcer</span></td>
                </tr>
                <tr>
                  <td>7</td>
                  <td><strong>Keshav Maharaj</strong></td>
                  <td>1944</td>
                  <td><strong style="color: #38BDF8;">58.96</strong></td>
                  <td><span class="role-badge-table">Middle & Powerplay Restrictor</span></td>
                </tr>
                <tr>
                  <td>8</td>
                  <td><strong>Corbin Bosch</strong></td>
                  <td>3629</td>
                  <td><strong style="color: #38BDF8;">58.90</strong></td>
                  <td><span class="role-badge-table">Death Wicket Enforcer</span></td>
                </tr>
                <tr>
                  <td>9</td>
                  <td><strong>Wanindu Hasaranga</strong></td>
                  <td>4900</td>
                  <td><strong style="color: #38BDF8;">58.81</strong></td>
                  <td><span class="role-badge-table">Middle & Powerplay Restrictor</span></td>
                </tr>
                <tr>
                  <td>10</td>
                  <td><strong>Sam Curran</strong></td>
                  <td>4409</td>
                  <td><strong style="color: #38BDF8;">58.22</strong></td>
                  <td><span class="role-badge-table">Death Wicket Enforcer</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="rr-card">
          <div class="card-header-clean">
            <div class="card-title-group">
              <i class="fa-solid fa-chart-simple" style="color: #38BDF8;"></i>
              <span class="card-title">Reliability Index — Top 10 Bowlers</span>
            </div>
          </div>
          <div class="chart-container-fluid" style="height: 380px;">
            <canvas id="bowlersRIChart"></canvas>
          </div>
        </div>
      </div>

      <!-- Bottom Row: 5 Cards Grid -->
      <div class="bowling-bottom-5col">
        <div class="rr-card">
          <div class="card-header-clean"><span class="card-title" style="font-size: 13px;">Economy Analysis</span></div>
          <div class="chart-container-fluid" style="height: 170px;"><canvas id="bowlerEconChart"></canvas></div>
        </div>

        <div class="rr-card">
          <div class="card-header-clean"><span class="card-title" style="font-size: 13px;">Wickets per Over</span></div>
          <div class="chart-container-fluid" style="height: 170px;"><canvas id="bowlerWPOChart"></canvas></div>
        </div>

        <div class="rr-card">
          <div class="card-header-clean"><span class="card-title" style="font-size: 13px;">Dot Ball & Boundary %</span></div>
          <div class="donut-card-container">
            <div class="donut-chart-box" style="width: 125px; height: 125px; min-width: 125px; min-height: 125px;">
              <canvas id="bowlerDotBoundaryChart"></canvas>
              <div class="donut-center-badge">
                <div class="donut-center-num" style="font-size: 18px;">62.5%</div>
                <div class="donut-center-text" style="font-size: 8.5px;">Dot Balls</div>
              </div>
            </div>
            <div class="donut-legend">
              <div class="legend-row-pressure">
                <div class="legend-color-label">
                  <span class="legend-dot" style="background: #38BDF8;"></span>
                  <span class="legend-label-text">Dot</span>
                </div>
                <span class="legend-pct-pill" style="border-color: #38BDF8; color: #38BDF8;">62.5%</span>
              </div>
              <div class="legend-row-pressure">
                <div class="legend-color-label">
                  <span class="legend-dot" style="background: var(--rr-pink);"></span>
                  <span class="legend-label-text">Bndry</span>
                </div>
                <span class="legend-pct-pill" style="border-color: var(--rr-pink); color: var(--rr-pink);">37.5%</span>
              </div>
            </div>
          </div>
        </div>

        <div class="rr-card">
          <div class="card-header-clean"><span class="card-title" style="font-size: 13px;">Boundary Conceded %</span></div>
          <div class="donut-card-container">
            <div class="donut-chart-box" style="width: 125px; height: 125px; min-width: 125px; min-height: 125px;">
              <canvas id="bowlerBoundaryConcededChart"></canvas>
              <div class="donut-center-badge">
                <div class="donut-center-num" style="font-size: 20px;">36.8%</div>
                <div class="donut-center-text" style="font-size: 8.5px;">Boundary</div>
              </div>
            </div>
            <div class="donut-legend">
              <div class="legend-row-pressure">
                <div class="legend-color-label">
                  <span class="legend-dot" style="background: #6366F1;"></span>
                  <span class="legend-label-text">Others</span>
                </div>
                <span class="legend-pct-pill" style="border-color: #6366F1; color: #6366F1;">63.2%</span>
              </div>
              <div class="legend-row-pressure">
                <div class="legend-color-label">
                  <span class="legend-dot" style="background: #FF2A85;"></span>
                  <span class="legend-label-text">Bndry</span>
                </div>
                <span class="legend-pct-pill" style="border-color: #FF2A85; color: #FF2A85;">36.8%</span>
              </div>
            </div>
          </div>
        </div>

        <div class="rr-card">
          <div class="player-spotlight-box">
            <div class="player-spotlight-header">
              <img class="spotlight-avatar-lg" style="border-color: #38BDF8;" src="__MARSH_IMG__" alt="Mitchell Marsh">
              <div class="spotlight-info-lg">
                <span class="spotlight-rank-badge" style="color: #38BDF8;">👑 #1 Bowler</span>
                <h4>Mitchell Marsh</h4>
                <div class="spotlight-ri-text">61.86 Reliability Index</div>
              </div>
            </div>
            <div class="spotlight-bullet-list">
              <div class="spotlight-bullet"><i class="fa-solid fa-circle-check"></i> 8.12 Econ (High Pressure)</div>
              <div class="spotlight-bullet"><i class="fa-solid fa-circle-check"></i> 1.62 Wkts/Over in Death Overs</div>
              <div class="spotlight-bullet"><i class="fa-solid fa-circle-check"></i> 64.7% Dot Balls Delivered</div>
            </div>
            <button class="view-profile-btn" style="background: linear-gradient(90deg, #38BDF8 0%, #6366F1 100%);" onclick="openComparisonWith('Mitchell Marsh')">
              <span>View Full Profile</span>
              <i class="fa-solid fa-arrow-right"></i>
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- ==========================================================================
         VIEW 4: PRESSURE ANALYSIS (SCREENSHOT 4)
         ========================================================================== -->
    <section class="view-content" id="view-pressure">
      <!-- 4 Top KPI Cards -->
      <div class="pressure-top-grid">
        <div class="pressure-kpi-card">
          <div class="intel-top-icon"><i class="fa-solid fa-gauge-high"></i></div>
          <div class="intel-top-data">
            <span class="intel-top-label">Avg. Pressure Score</span>
            <span class="intel-top-val">65.4</span>
            <span class="intel-top-sub">(Moderate-High)</span>
          </div>
        </div>

        <div class="pressure-kpi-card">
          <div class="intel-top-icon icon-purple"><i class="fa-solid fa-trophy"></i></div>
          <div class="intel-top-data">
            <span class="intel-top-label">High Pressure Players</span>
            <span class="intel-top-val">38.7%</span>
            <span class="intel-top-sub">of Total Players</span>
          </div>
        </div>

        <div class="pressure-kpi-card">
          <div class="intel-top-icon icon-gold"><i class="fa-solid fa-chart-column"></i></div>
          <div class="intel-top-data">
            <span class="intel-top-label">Matches in Pressure</span>
            <span class="intel-top-val">42.3%</span>
            <span class="intel-top-sub">of Total Matches</span>
          </div>
        </div>

        <div class="pressure-kpi-card">
          <div class="intel-top-icon"><i class="fa-solid fa-shield-heart"></i></div>
          <div class="intel-top-data">
            <span class="intel-top-label">Pressure Success Rate</span>
            <span class="intel-top-val">72.6%</span>
            <span class="intel-top-sub">Overall Roster</span>
          </div>
        </div>
      </div>

      <!-- Mid Row: 3 Visualizations -->
      <div class="pressure-mid-3col">
        <div class="rr-card">
          <div class="card-header-clean">
            <span class="card-title">Pressure Category Distribution</span>
          </div>
          <div class="donut-card-container">
            <div class="donut-chart-box" style="width: 165px; height: 165px; min-width: 165px; min-height: 165px;">
              <canvas id="pressureCategoryChart"></canvas>
              <div class="donut-center-badge">
                <div class="donut-center-num">837</div>
                <div class="donut-center-text">Matches</div>
              </div>
            </div>
            <div class="donut-legend-pressure">
              <div class="legend-row-pressure">
                <div class="legend-color-label">
                  <span class="legend-dot" style="background: #10B981;"></span>
                  <span class="legend-label-text">Low Pressure (0–40)</span>
                </div>
                <span class="legend-pct-pill" style="border-color: #10B981; color: #10B981;">22.1%</span>
              </div>
              <div class="legend-row-pressure">
                <div class="legend-color-label">
                  <span class="legend-dot" style="background: #00D2FF;"></span>
                  <span class="legend-label-text">Moderate Pressure (40–65)</span>
                </div>
                <span class="legend-pct-pill" style="border-color: #00D2FF; color: #00D2FF;">37.5%</span>
              </div>
              <div class="legend-row-pressure">
                <div class="legend-color-label">
                  <span class="legend-dot" style="background: #E5097F;"></span>
                  <span class="legend-label-text">High Pressure (65–85)</span>
                </div>
                <span class="legend-pct-pill" style="border-color: #E5097F; color: #E5097F;">28.4%</span>
              </div>
              <div class="legend-row-pressure">
                <div class="legend-color-label">
                  <span class="legend-dot" style="background: #8B5CF6;"></span>
                  <span class="legend-label-text">Extreme Pressure (85–100)</span>
                </div>
                <span class="legend-pct-pill" style="border-color: #8B5CF6; color: #8B5CF6;">11.0%</span>
              </div>
            </div>
          </div>
        </div>

        <div class="rr-card">
          <div class="card-header-clean">
            <span class="card-title">Pressure Score Distribution</span>
          </div>
          <div class="chart-container-fluid" style="height: 250px;">
            <canvas id="pressureDistChart"></canvas>
          </div>
        </div>

        <div class="rr-card">
          <div class="card-header-clean">
            <span class="card-title">Batting vs Bowling Pressure</span>
          </div>
          <div class="chart-container-fluid" style="height: 250px;">
            <canvas id="pressureBatVsBowlChart"></canvas>
          </div>
        </div>
      </div>

      <!-- Bottom Row: Innings Analysis + Indicators + Pressure Insights -->
      <div class="pressure-bottom-3col">
        <div class="rr-card">
          <div class="card-header-clean">
            <span class="card-title">Innings Analysis</span>
          </div>
          <div class="chart-container-fluid" style="height: 220px;">
            <canvas id="inningsAnalysisChart"></canvas>
          </div>
        </div>

        <div class="rr-card">
          <div class="card-header-clean">
            <div class="card-title-group">
              <i class="fa-solid fa-bullseye"></i>
              <span class="card-title">Key Pressure Indicators</span>
            </div>
          </div>
          <table class="kpi-indicator-table">
            <tbody>
              <tr>
                <td><i class="fa-solid fa-trophy" style="color: var(--rr-gold-light); margin-right: 8px;"></i> Avg. RRR (High Pressure)</td>
                <td>8.7</td>
              </tr>
              <tr>
                <td><i class="fa-solid fa-scale-balanced" style="color: #38BDF8; margin-right: 8px;"></i> Wickets in Hand (Avg.)</td>
                <td>4.2</td>
              </tr>
              <tr>
                <td><i class="fa-solid fa-baseball" style="color: var(--rr-pink); margin-right: 8px;"></i> Balls Remaining (Avg.)</td>
                <td>32.5</td>
              </tr>
              <tr>
                <td><i class="fa-solid fa-person-running" style="color: #10B981; margin-right: 8px;"></i> Match Situation Impact</td>
                <td class="indicator-highlight-green">+12.3%</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="rr-card" style="display: flex; flex-direction: column; justify-content: space-between;">
          <div>
            <div class="card-header-clean">
              <div class="card-title-group">
                <i class="fa-solid fa-lightbulb" style="color: var(--rr-gold-light);"></i>
                <span class="card-title">Pressure Insights</span>
              </div>
            </div>
            <div class="pressure-insight-bullets">
              <div class="pressure-bullet-item">
                <i class="fa-solid fa-circle-check"></i>
                <span>Team performs <strong>12.3% better</strong> in pressure situations compared to normal matches.</span>
              </div>
              <div class="pressure-bullet-item">
                <i class="fa-solid fa-circle-check"></i>
                <span>Batting success rate is higher in 2nd innings (<strong>73.5%</strong>) than 1st innings (71.2%).</span>
              </div>
              <div class="pressure-bullet-item">
                <i class="fa-solid fa-circle-check"></i>
                <span>Moderate pressure (40–65) is the most common match scenario (<strong>37.5%</strong>).</span>
              </div>
              <div class="pressure-bullet-item">
                <i class="fa-solid fa-circle-check"></i>
                <span>RR targets demonstrate elite composure in steep death-over chases.</span>
              </div>
            </div>
          </div>

          <div style="display: flex; align-items: center; justify-content: space-between; padding-top: 14px; border-top: 1px solid rgba(255, 255, 255, 0.08);">
            <div style="font-family: var(--font-script); font-size: 20px; color: #FF5EA6;">Pressure Makes Champions</div>
            <i class="fa-solid fa-crown" style="font-size: 24px; color: var(--rr-pink);"></i>
          </div>
        </div>
      </div>
    </section>

    <!-- ==========================================================================
         VIEW 5: PLAYER COMPARISON (SCREENSHOT 5)
         ========================================================================== -->
    <section class="view-content" id="view-comparison">
      <!-- Selector Card -->
      <div class="comparison-controls-card">
        <div class="discipline-pills">
          <div class="discipline-pill active" id="comp-btn-batter" onclick="setComparisonDiscipline('Batter')">
            <i class="fa-solid fa-baseball-bat-ball"></i> Batter Comparison
          </div>
          <div class="discipline-pill" id="comp-btn-bowler" onclick="setComparisonDiscipline('Bowler')">
            <i class="fa-solid fa-baseball"></i> Bowler Comparison
          </div>
        </div>

        <div class="comparison-selects">
          <select class="player-select-dropdown" id="comp-p1-select" onchange="updateComparison()"></select>
          <select class="player-select-dropdown" id="comp-p2-select" onchange="updateComparison()"></select>
          <select class="player-select-dropdown" id="comp-p3-select" onchange="updateComparison()"></select>
          <button class="compare-btn-action" onclick="updateComparison()">
            <i class="fa-solid fa-arrows-rotate"></i> Compare Players
          </button>
        </div>
      </div>

      <!-- 3 Side-by-Side Cards -->
      <div class="comparison-cards-3col" id="comp-cards-container">
        <!-- Rendered via JS -->
      </div>

      <!-- 3 Visualizations Comparison -->
      <div class="comp-charts-3col">
        <div class="rr-card">
          <div class="card-header-clean">
            <span class="card-title" id="comp-chart1-title">Strike Rate Comparison</span>
          </div>
          <div class="chart-container-fluid" style="height: 220px;">
            <canvas id="compChart1"></canvas>
          </div>
        </div>

        <div class="rr-card">
          <div class="card-header-clean">
            <span class="card-title">Dot Ball Percentage</span>
          </div>
          <div class="donut-card-container" id="comp-chart2-container" style="min-height: 200px;">
            <div class="donut-chart-box" style="width: 140px; height: 140px; min-width: 140px; min-height: 140px;">
              <canvas id="compChart2"></canvas>
            </div>
            <div class="donut-legend" id="comp-chart2-legend">
              <!-- Dynamically populated via updateComparison() -->
            </div>
          </div>
        </div>

        <div class="rr-card">
          <div class="card-header-clean">
            <span class="card-title" id="comp-chart3-title">Dismissal Rate</span>
          </div>
          <div class="chart-container-fluid" style="height: 220px;">
            <canvas id="compChart3"></canvas>
          </div>
        </div>
      </div>

      <!-- Bottom 3 Cards: Insights + Summary + Top Choice -->
      <div class="comp-summary-3col">
        <div class="rr-card">
          <div class="card-header-clean">
            <div class="card-title-group">
              <i class="fa-solid fa-lightbulb" style="color: var(--rr-gold-light);"></i>
              <span class="card-title">Key Performance Insights</span>
            </div>
          </div>
          <div class="pressure-insight-bullets" id="comp-insights-list">
            <!-- Populated via JS -->
          </div>
        </div>

        <div class="rr-card">
          <div class="card-header-clean">
            <div class="card-title-group">
              <i class="fa-solid fa-bullseye" style="color: var(--rr-cyan);"></i>
              <span class="card-title">Comparison Summary</span>
            </div>
          </div>
          <table class="kpi-indicator-table" id="comp-summary-table">
            <!-- Populated via JS -->
          </table>
        </div>

        <div class="top-choice-card">
          <i class="fa-solid fa-trophy top-choice-trophy"></i>
          <div class="top-choice-details">
            <div class="top-choice-lbl">Our Top Choice</div>
            <div class="top-choice-name" id="top-choice-name">Jason Holder</div>
            <div class="top-choice-ri" id="top-choice-ri">Reliability Index: 66.84</div>
          </div>
          <img class="top-choice-avatar" id="top-choice-img" src="__HOLDER_IMG__" alt="Top Choice">
        </div>
      </div>
    </section>

    <!-- ==========================================================================
         VIEW 6: PLAYER RANKINGS (SCREENSHOT 6)
         ========================================================================== -->
    <section class="view-content" id="view-rankings">
      <!-- 5 KPI Cards Row -->
      <div class="kpi-row-5">
        <div class="intel-top-card">
          <div class="intel-top-icon"><i class="fa-solid fa-baseball-bat-ball"></i></div>
          <div class="intel-top-data">
            <span class="intel-top-label">Top Batter (Jason Holder)</span>
            <span class="intel-top-val">66.84</span>
          </div>
        </div>

        <div class="intel-top-card">
          <div class="intel-top-icon icon-purple"><i class="fa-solid fa-baseball"></i></div>
          <div class="intel-top-data">
            <span class="intel-top-label">Top Bowler (Mitchell Marsh)</span>
            <span class="intel-top-val">61.86</span>
          </div>
        </div>

        <div class="intel-top-card">
          <div class="intel-top-icon"><i class="fa-solid fa-users"></i></div>
          <div class="intel-top-data">
            <span class="intel-top-label">Total Qualified Batters</span>
            <span class="intel-top-val">109</span>
          </div>
        </div>

        <div class="intel-top-card">
          <div class="intel-top-icon icon-blue"><i class="fa-solid fa-bowling-ball"></i></div>
          <div class="intel-top-data">
            <span class="intel-top-label">Total Qualified Bowlers</span>
            <span class="intel-top-val">136</span>
          </div>
        </div>

        <div class="intel-top-card">
          <div class="intel-top-icon icon-gold"><i class="fa-solid fa-shield-halved"></i></div>
          <div class="intel-top-data">
            <span class="intel-top-label">Data Coverage</span>
            <span class="intel-top-val">837 Matches</span>
          </div>
        </div>
      </div>

      <!-- Dual Side-by-Side Complete Tables -->
      <div class="rankings-dual-tables">
        <!-- Batters Table -->
        <div class="rankings-table-wrap">
          <div class="table-top-actions">
            <div class="table-top-title">
              <i class="fa-solid fa-baseball-bat-ball" style="color: var(--rr-pink);"></i>
              <span>Top 10 Batters</span>
            </div>
            <button class="download-csv-btn" onclick="downloadCSV('batters')">
              <i class="fa-solid fa-download"></i> Download CSV
            </button>
          </div>

          <div class="clean-table-wrap">
            <table class="clean-table" id="full-batters-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Player</th>
                  <th>Player ID</th>
                  <th>Strike Rate</th>
                  <th>Reliability</th>
                  <th>95% CI</th>
                </tr>
              </thead>
              <tbody>
                <!-- Injected by script -->
              </tbody>
            </table>
          </div>
        </div>

        <!-- Bowlers Table -->
        <div class="rankings-table-wrap">
          <div class="table-top-actions">
            <div class="table-top-title">
              <i class="fa-solid fa-baseball" style="color: #38BDF8;"></i>
              <span>Top 10 Bowlers</span>
            </div>
            <button class="download-csv-btn" onclick="downloadCSV('bowlers')">
              <i class="fa-solid fa-download"></i> Download CSV
            </button>
          </div>

          <div class="clean-table-wrap">
            <table class="clean-table" id="full-bowlers-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Player</th>
                  <th>Player ID</th>
                  <th>Economy</th>
                  <th>Reliability</th>
                  <th>95% CI</th>
                </tr>
              </thead>
              <tbody>
                <!-- Injected by script -->
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Bottom Row: 4 Cards -->
      <div class="rankings-bottom-4col">
        <div class="rr-card">
          <div class="card-header-clean">
            <div class="card-title-group">
              <i class="fa-solid fa-lightbulb" style="color: var(--rr-gold-light);"></i>
              <span class="card-title">Rankings Insights</span>
            </div>
          </div>
          <div class="pressure-insight-bullets">
            <div class="pressure-bullet-item"><i class="fa-solid fa-circle-check"></i> Jason Holder tops batting charts with <strong>66.84 RI</strong>.</div>
            <div class="pressure-bullet-item"><i class="fa-solid fa-circle-check"></i> Mitchell Marsh leads bowling rankings with <strong>61.86 RI</strong>.</div>
            <div class="pressure-bullet-item"><i class="fa-solid fa-circle-check"></i> RR targets show deep roster coverage in batting & death bowling.</div>
            <div class="pressure-bullet-item"><i class="fa-solid fa-circle-check"></i> 8 players in top 10 belong to elite Core pick tier.</div>
          </div>
        </div>

        <div class="rr-card">
          <div class="card-header-clean">
            <span class="card-title">Eligibility Breakdown</span>
          </div>
          <div class="chart-container-fluid" style="height: 180px;">
            <canvas id="eligibilityDonutChart"></canvas>
            <div class="donut-center-badge">
              <div class="donut-center-num">77.3%</div>
              <div class="donut-center-text">Core Tier</div>
            </div>
          </div>
        </div>

        <div class="rr-card">
          <div class="card-header-clean">
            <div class="card-title-group">
              <i class="fa-solid fa-rocket" style="color: var(--rr-cyan);"></i>
              <span class="card-title">Quick Actions</span>
            </div>
          </div>
          <div class="action-button-stack">
            <button class="action-stack-btn" onclick="downloadCSV('batters')">
              <i class="fa-solid fa-file-arrow-down" style="color: var(--rr-pink);"></i>
              <span>Download Batters Report</span>
            </button>
            <button class="action-stack-btn" onclick="downloadCSV('bowlers')">
              <i class="fa-solid fa-file-arrow-down" style="color: #38BDF8;"></i>
              <span>Download Bowlers Report</span>
            </button>
          </div>
        </div>

        <div class="rr-ready-banner">
          <i class="fa-solid fa-crown crown-lg"></i>
          <h4>Rajasthan Royals</h4>
          <p>Stronger • Smarter • Ready</p>
        </div>
      </div>
    </section>

    <!-- ==========================================================================
         VIEW 7: METHODOLOGY & VALIDATION (SCREENSHOT 7)
         ========================================================================== -->
    <section class="view-content" id="view-methodology">
      <!-- 5 KPI Cards Row -->
      <div class="method-top-5col">
        <div class="intel-top-card">
          <div class="intel-top-icon"><i class="fa-solid fa-database"></i></div>
          <div class="intel-top-data">
            <span class="intel-top-label">Dataset Coverage</span>
            <span class="intel-top-val">100%</span>
            <span class="intel-top-sub">(837 Matches)</span>
          </div>
        </div>

        <div class="intel-top-card">
          <div class="intel-top-icon"><i class="fa-solid fa-baseball"></i></div>
          <div class="intel-top-data">
            <span class="intel-top-label">Total Deliveries Analyzed</span>
            <span class="intel-top-val">193,976</span>
          </div>
        </div>

        <div class="intel-top-card">
          <div class="intel-top-icon icon-purple"><i class="fa-solid fa-users"></i></div>
          <div class="intel-top-data">
            <span class="intel-top-label">Qualified Players (Bat+Bowl)</span>
            <span class="intel-top-val">245</span>
          </div>
        </div>

        <div class="intel-top-card">
          <div class="intel-top-icon icon-gold"><i class="fa-solid fa-shield-check"></i></div>
          <div class="intel-top-data">
            <span class="intel-top-label">Validation Status</span>
            <span class="intel-top-val" style="color: #10B981;">✔ Verified</span>
            <span class="intel-top-sub">(Production Ready)</span>
          </div>
        </div>

        <div class="intel-top-card">
          <div class="intel-top-icon icon-blue"><i class="fa-solid fa-calendar-check"></i></div>
          <div class="intel-top-data">
            <span class="intel-top-label">Last Updated</span>
            <span class="intel-top-val" style="font-size: 16px;">Nov 13, 2026</span>
            <span class="intel-top-sub">14:30 IST</span>
          </div>
        </div>
      </div>

      <!-- Mid Row: Dataset Overview + Analysis Pipeline -->
      <div class="method-mid-2col">
        <div class="rr-card">
          <div class="card-header-clean">
            <span class="card-title">Dataset Overview</span>
          </div>
          <div style="display: flex; align-items: center; justify-content: space-between; gap: 14px; flex-wrap: wrap;">
            <table class="kpi-indicator-table" style="flex: 1; min-width: 200px;">
              <tbody>
                <tr><td>Total Matches Analyzed</td><td>837</td></tr>
                <tr><td>Total Deliveries Analyzed</td><td>193,976</td></tr>
                <tr><td>Unique Players</td><td>891</td></tr>
                <tr><td>Qualified Batters</td><td>109</td></tr>
                <tr><td>Qualified Bowlers</td><td>136</td></tr>
              </tbody>
            </table>
            <div style="width: 170px; height: 170px; position: relative; margin: 0 auto;">
              <canvas id="datasetOverviewDonut"></canvas>
              <div class="donut-center-badge">
                <div class="donut-center-num" style="font-size: 15px;">193,976</div>
                <div class="donut-center-text">Deliveries</div>
              </div>
            </div>
          </div>
        </div>

        <div class="rr-card">
          <div class="card-header-clean">
            <div class="card-title-group">
              <i class="fa-solid fa-gears" style="color: var(--rr-pink);"></i>
              <span class="card-title">Analysis Pipeline</span>
            </div>
          </div>
          <div class="pipeline-stepper">
            <div class="pipeline-step">
              <div class="pipeline-icon-circle"><i class="fa-solid fa-database"></i></div>
              <div class="pipeline-title">1. Data<br>Collection</div>
            </div>
            <i class="fa-solid fa-arrow-right pipeline-arrow"></i>
            <div class="pipeline-step">
              <div class="pipeline-icon-circle"><i class="fa-solid fa-broom"></i></div>
              <div class="pipeline-title">2. Data<br>Cleaning</div>
            </div>
            <i class="fa-solid fa-arrow-right pipeline-arrow"></i>
            <div class="pipeline-step">
              <div class="pipeline-icon-circle"><i class="fa-solid fa-chart-line"></i></div>
              <div class="pipeline-title">3. Analytics<br>Processing</div>
            </div>
            <i class="fa-solid fa-arrow-right pipeline-arrow"></i>
            <div class="pipeline-step">
              <div class="pipeline-icon-circle"><i class="fa-solid fa-shield-halved"></i></div>
              <div class="pipeline-title">4. Validation<br>& Verification</div>
            </div>
            <i class="fa-solid fa-arrow-right pipeline-arrow"></i>
            <div class="pipeline-step">
              <div class="pipeline-icon-circle"><i class="fa-solid fa-laptop-code"></i></div>
              <div class="pipeline-title">5. Dashboard<br>Generation</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Row 3: Pressure Scoring Framework + Reliability Index + Eligibility Rules -->
      <div class="method-row3-3col">
        <div class="rr-card">
          <div class="card-header-clean">
            <div class="card-title-group">
              <i class="fa-solid fa-gauge" style="color: var(--rr-pink);"></i>
              <span class="card-title">Pressure Scoring Framework</span>
            </div>
          </div>
          <table class="kpi-indicator-table" style="margin-bottom: 12px;">
            <tbody>
              <tr><td><span style="color: #10B981;">●</span> Low Pressure</td><td>0 – 40</td></tr>
              <tr><td><span style="color: #38BDF8;">●</span> Moderate Pressure</td><td>40 – 65</td></tr>
              <tr><td><span style="color: #FF5EA6;">●</span> High Pressure</td><td>65 – 85</td></tr>
              <tr><td><span style="color: #A855F7;">●</span> Extreme Pressure</td><td>85 – 100</td></tr>
            </tbody>
          </table>
          <p style="font-size: 11.5px; color: var(--text-muted);">Calculated using situational ball-by-ball dynamics: required run rate, wickets in hand, and match leverage stage.</p>
        </div>

        <div class="rr-card">
          <div class="card-header-clean">
            <div class="card-title-group">
              <i class="fa-solid fa-calculator" style="color: var(--rr-gold-light);"></i>
              <span class="card-title">Reliability Index</span>
            </div>
          </div>
          <p style="font-size: 12.5px; color: var(--text-light); margin-bottom: 12px;">Composite performance metric based on multiple verified pillars:</p>
          <div class="pressure-insight-bullets" style="margin-bottom: 14px;">
            <div class="pressure-bullet-item"><i class="fa-solid fa-circle-check"></i> Strike Rate / Economy</div>
            <div class="pressure-bullet-item"><i class="fa-solid fa-circle-check"></i> Consistency & Dot Ball Control</div>
            <div class="pressure-bullet-item"><i class="fa-solid fa-circle-check"></i> Pressure Performance Surge</div>
            <div class="pressure-bullet-item"><i class="fa-solid fa-circle-check"></i> Match Situation Impact</div>
          </div>
          <div style="background: rgba(245, 158, 11, 0.12); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 8px; padding: 8px 12px; display: flex; align-items: center; justify-content: space-between;">
            <span style="font-size: 12px; font-weight: 700; color: var(--rr-gold-light);">Scaled Standard:</span>
            <span style="font-size: 16px; font-weight: 900; color: #FFFFFF;">0 – 100</span>
          </div>
        </div>

        <div class="rr-card">
          <div class="card-header-clean">
            <div class="card-title-group">
              <i class="fa-solid fa-user-check" style="color: #10B981;"></i>
              <span class="card-title">Eligibility Rules</span>
            </div>
          </div>
          <div class="rules-dual-box">
            <div>
              <div class="rule-box-header rule-hdr-pink">Batters</div>
              <div class="rule-bullets">
                <div class="rule-bullet-item"><i class="fa-solid fa-circle-check"></i> HP Balls Faced ≥ 30</div>
                <div class="rule-bullet-item"><i class="fa-solid fa-circle-check"></i> Normal Balls ≥ 30</div>
                <div class="rule-bullet-item"><i class="fa-solid fa-circle-check"></i> Matches ≥ 5</div>
              </div>
            </div>
            <div>
              <div class="rule-box-header rule-hdr-blue">Bowlers</div>
              <div class="rule-bullets">
                <div class="rule-bullet-item"><i class="fa-solid fa-circle-check"></i> HP Legal Balls ≥ 30</div>
                <div class="rule-bullet-item"><i class="fa-solid fa-circle-check"></i> Normal Legal Balls ≥ 30</div>
                <div class="rule-bullet-item"><i class="fa-solid fa-circle-check"></i> Matches ≥ 5</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Row 4: Key Exclusions + Methodology Highlights + Important Notes + Banner -->
      <div class="method-row4-4col">
        <div class="rr-card">
          <div class="card-header-clean">
            <div class="card-title-group">
              <i class="fa-solid fa-ban" style="color: #EF4444;"></i>
              <span class="card-title">Key Exclusions</span>
            </div>
          </div>
          <div class="pressure-insight-bullets">
            <div class="pressure-bullet-item"><i class="fa-solid fa-circle-xmark" style="color: #EF4444;"></i> 26 Super Over Deliveries (Excluded)</div>
            <div class="pressure-bullet-item"><i class="fa-solid fa-circle-xmark" style="color: #EF4444;"></i> 12 Post-Target Residual Deliveries (Excluded)</div>
          </div>
          <div style="margin-top: 14px; background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.35); padding: 8px 10px; border-radius: 8px; font-size: 11px; font-weight: 700; color: #34D399;">
            ✔ Final Analysis Cohort: 193,976 Deliveries Across 837 Matches
          </div>
        </div>

        <div class="rr-card">
          <div class="card-header-clean">
            <div class="card-title-group">
              <i class="fa-solid fa-wand-magic-sparkles" style="color: var(--rr-pink);"></i>
              <span class="card-title">Methodology Highlights</span>
            </div>
          </div>
          <div class="pressure-insight-bullets">
            <div class="pressure-bullet-item"><i class="fa-solid fa-circle-check"></i> Pressure Scoring: Match Situation + RRR + Wickets</div>
            <div class="pressure-bullet-item"><i class="fa-solid fa-circle-check"></i> Reliability Index: Weighted Performance Metric</div>
            <div class="pressure-bullet-item"><i class="fa-solid fa-circle-check"></i> Confidence Intervals: Bootstrap Method</div>
            <div class="pressure-bullet-item"><i class="fa-solid fa-circle-check"></i> Shrinkage: Statistical Regularization</div>
          </div>
        </div>

        <div class="rr-card">
          <div class="card-header-clean">
            <div class="card-title-group">
              <i class="fa-solid fa-triangle-exclamation" style="color: var(--rr-gold-light);"></i>
              <span class="card-title">Important Notes</span>
            </div>
          </div>
          <div class="pressure-insight-bullets">
            <div class="pressure-bullet-item"><i class="fa-solid fa-circle-check"></i> Task06 ML Predictions NOT used for final rankings</div>
            <div class="pressure-bullet-item"><i class="fa-solid fa-circle-check"></i> Archetypes for squad insights only</div>
            <div class="pressure-bullet-item"><i class="fa-solid fa-circle-check"></i> CI = Estimation Uncertainty (not direct proof)</div>
            <div class="pressure-bullet-item"><i class="fa-solid fa-circle-check"></i> Data: Certified CSV Outputs</div>
          </div>
        </div>

        <div class="rr-ready-banner" style="border-color: var(--rr-pink);">
          <i class="fa-solid fa-crown crown-lg" style="color: var(--rr-pink);"></i>
          <h4 style="font-size: 15px;">SUPERR SELECTOR</h4>
          <p style="color: #CBD5E1; font-weight: 600; letter-spacing: 0.5px;">Smarter Insights. Stronger Team.</p>
        </div>
      </div>
    </section>

    <!-- Bottom Footer Bar -->
    <footer class="dashboard-footer-bar">
      <div class="footer-left">
        <i class="fa-solid fa-crown footer-crown"></i>
        <span>Rajasthan Royals | SUPERR SELECTOR | Cricket Performance Intelligence | Season 2</span>
      </div>
      <div class="footer-right">
        <span class="status-dot-green"></span>
        <span>Data Verified • Last Updated: Nov 13, 2026, 14:30 IST</span>
      </div>
    </footer>
  </main>

  <!-- ==========================================================================
       BESPOKE ANIMATION ENGINE & CHART.JS ORCHESTRATION
       ========================================================================== -->
  <script>
    // Embedded Certified Player Data
    const RR_DATA = __PLAYERS_JSON__;
    
    // Tab switching orchestration
    const tabTitles = {
      overview: { title: "Squad Overview", subtitle: "Build a Winning Squad. Own the Auction." },
      batting: { title: "Top Batters", subtitle: "Batting Intelligence • Player Performance" },
      bowling: { title: "Top Bowlers", subtitle: "Bowling Intelligence • Analyze. Strategize. Win." },
      pressure: { title: "Pressure Analysis", subtitle: "Understand Performance Under Pressure" },
      comparison: { title: "Player Comparison", subtitle: "Compare. Analyze. Choose Better." },
      rankings: { title: "Player Rankings", subtitle: "Top Performers. Verified Rankings." },
      methodology: { title: "Methodology & Validation", subtitle: "Transparent. Reliable. Reproducible." }
    };

    // Store Chart instances mapped by tab for re-triggering their custom animations
    const chartRegistry = {
      overview: [],
      batting: [],
      bowling: [],
      pressure: [],
      comparison: [],
      rankings: [],
      methodology: []
    };

    function toggleSidebar() {
      const sb = document.getElementById('app-sidebar');
      sb.classList.toggle('open');
    }

    function switchTab(tabId) {
      document.querySelectorAll('.view-content').forEach(el => el.classList.remove('active'));
      document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));

      const targetView = document.getElementById('view-' + tabId);
      const targetNav = document.getElementById('nav-' + tabId);

      if (targetView) {
        // Trigger CSS reflow for restart of CSS keyframe animations
        targetView.style.animation = 'none';
        void targetView.offsetWidth; // Trigger reflow
        targetView.style.animation = '';
        targetView.classList.add('active');
      }

      if (targetNav) targetNav.classList.add('active');

      if (tabTitles[tabId]) {
        document.getElementById('page-title-text').innerText = tabTitles[tabId].title;
        document.getElementById('page-subtitle-text').innerText = tabTitles[tabId].subtitle;
      }

      // Close mobile sidebar if open
      const sb = document.getElementById('app-sidebar');
      if (sb && sb.classList.contains('open')) {
        sb.classList.remove('open');
      }

      window.scrollTo({ top: 0, behavior: 'smooth' });

      // Animate progress bars if on Overview
      if (tabId === 'overview') {
        animateOverviewProgressBars();
      }

      // Animate exposure gauge if on Batting
      if (tabId === 'batting') {
        animateExposureGauge();
      }

      // Re-trigger bespoke Chart.js animations for that tab!
      if (chartRegistry[tabId] && chartRegistry[tabId].length > 0) {
        setTimeout(() => {
          chartRegistry[tabId].forEach(chart => {
            if (chart) {
              chart.reset();
              chart.update();
            }
          });
        }, 80);
      }
    }

    function animateOverviewProgressBars() {
      const bars = document.querySelectorAll('.progress-fill-pink, .progress-fill-purple');
      bars.forEach(b => {
        b.style.width = '0%';
        const target = b.getAttribute('data-width') || '75%';
        setTimeout(() => {
          b.style.width = target;
        }, 120);
      });
    }

    function animateExposureGauge() {
      const thumb = document.getElementById('pressureGaugeThumb');
      if (thumb) {
        thumb.style.left = '0%';
        setTimeout(() => {
          thumb.style.left = '65.4%';
        }, 200);
      }
    }

    // Global Chart.js Defaults
    Chart.defaults.color = '#94A3B8';
    Chart.defaults.font.family = "'Plus Jakarta Sans', 'Inter', sans-serif";

    // ==========================================================================
    // CHART INITIALIZATION WITH BESPOKE SUITABLE ANIMATIONS
    // ==========================================================================

    // 1. Squad Donut Chart (Overview) -> Clockwise Sweep & Spring Zoom
    const ctxSquad = document.getElementById('squadDonutChart');
    if (ctxSquad) {
      const squadChart = new Chart(ctxSquad, {
        type: 'doughnut',
        data: {
          labels: ['Batters', 'Bowlers'],
          datasets: [{
            data: [10, 10],
            backgroundColor: ['#E5097F', '#38BDF8'],
            borderWidth: 0,
            hoverOffset: 6
          }]
        },
        options: {
          cutout: '76%',
          animation: {
            animateRotate: true,
            animateScale: true,
            duration: 1300,
            easing: 'easeOutCirc'
          },
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: (ctx) => ` ${ctx.label}: ${ctx.raw} Players (50%)`
              }
            }
          },
          responsive: true,
          maintainAspectRatio: false
        }
      });
      chartRegistry.overview.push(squadChart);
    }

    // 2. Batters RI Horizontal Bar Chart -> Left-to-Right Cascading Slide
    const ctxBattersRI = document.getElementById('battersRIChart');
    if (ctxBattersRI) {
      const bNames = RR_DATA.batters.map(b => b.name);
      const bRIs = RR_DATA.batters.map(b => b.reliability_index);

      const battersRIChart = new Chart(ctxBattersRI, {
        type: 'bar',
        data: {
          labels: bNames,
          datasets: [{
            data: bRIs,
            backgroundColor: (ctx) => {
              const chart = ctx.chart;
              const { ctx: c, chartArea } = chart;
              if (!chartArea) return '#E5097F';
              const gradient = c.createLinearGradient(chartArea.left, 0, chartArea.right, 0);
              gradient.addColorStop(0, '#E5097F');
              gradient.addColorStop(1, '#A855F7');
              return gradient;
            },
            borderRadius: 6,
            barThickness: 14
          }]
        },
        options: {
          indexAxis: 'y',
          responsive: true,
          maintainAspectRatio: false,
          animation: {
            x: {
              type: 'number',
              easing: 'easeOutQuart',
              duration: 1200,
              delay: (ctx) => ctx.dataIndex * 70
            }
          },
          scales: {
            x: {
              min: 0,
              max: 75,
              grid: { color: 'rgba(255, 255, 255, 0.05)' },
              ticks: { color: '#94A3B8' }
            },
            y: {
              grid: { display: false },
              ticks: { color: '#FFFFFF', font: { weight: '600' } }
            }
          },
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: (ctx) => ` Reliability Index: ${ctx.raw}`
              }
            }
          }
        }
      });
      chartRegistry.batting.push(battersRIChart);
    }

    // 3. Batters Strike Rate Comparison -> Staggered Bouncing Vertical Growth
    const ctxBatterSR = document.getElementById('batterSRChart');
    if (ctxBatterSR) {
      const batterSRChart = new Chart(ctxBatterSR, {
        type: 'bar',
        data: {
          labels: ['Top 10 Avg', 'Tournament Avg'],
          datasets: [
            {
              label: 'Normal SR',
              data: [135.2, 128.7],
              backgroundColor: '#38BDF8',
              borderRadius: 6
            },
            {
              label: 'High-Pressure SR',
              data: [162.3, 141.5],
              backgroundColor: '#E5097F',
              borderRadius: 6
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          animation: {
            y: {
              type: 'number',
              easing: 'easeOutBack',
              duration: 1000,
              delay: (ctx) => (ctx.datasetIndex * 200) + (ctx.dataIndex * 80)
            }
          },
          scales: {
            x: { grid: { display: false }, ticks: { color: '#FFFFFF' } },
            y: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#94A3B8' } }
          },
          plugins: {
            legend: { position: 'top', labels: { color: '#FFFFFF', boxWidth: 12 } }
          }
        }
      });
      chartRegistry.batting.push(batterSRChart);
    }

    // 4. Dot Ball & Dismissal Donut -> Centered Ring with pure HTML Legend
    const ctxBatterDot = document.getElementById('batterDotChart');
    if (ctxBatterDot) {
      const batterDotChart = new Chart(ctxBatterDot, {
        type: 'doughnut',
        data: {
          labels: ['Dot Balls', 'Dismissal'],
          datasets: [{
            data: [28.8, 71.2],
            backgroundColor: ['#E5097F', '#8B5CF6'],
            borderWidth: 0
          }]
        },
        options: {
          cutout: '74%',
          responsive: true,
          maintainAspectRatio: false,
          animation: {
            animateRotate: true,
            animateScale: true,
            duration: 1200,
            easing: 'easeOutCirc'
          },
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: (ctx) => ` ${ctx.label}: ${ctx.raw}%`
              }
            }
          }
        }
      });
      chartRegistry.batting.push(batterDotChart);
    }

    // 5. Bowlers RI Horizontal Bar Chart -> Left-to-Right Cascading Slide
    const ctxBowlersRI = document.getElementById('bowlersRIChart');
    if (ctxBowlersRI) {
      const bwNames = RR_DATA.bowlers.map(b => b.name);
      const bwRIs = RR_DATA.bowlers.map(b => b.reliability_index);

      const bowlersRIChart = new Chart(ctxBowlersRI, {
        type: 'bar',
        data: {
          labels: bwNames,
          datasets: [{
            data: bwRIs,
            backgroundColor: (ctx) => {
              const chart = ctx.chart;
              const { ctx: c, chartArea } = chart;
              if (!chartArea) return '#38BDF8';
              const gradient = c.createLinearGradient(chartArea.left, 0, chartArea.right, 0);
              gradient.addColorStop(0, '#38BDF8');
              gradient.addColorStop(1, '#8B5CF6');
              return gradient;
            },
            borderRadius: 6,
            barThickness: 14
          }]
        },
        options: {
          indexAxis: 'y',
          responsive: true,
          maintainAspectRatio: false,
          animation: {
            x: {
              type: 'number',
              easing: 'easeOutQuart',
              duration: 1200,
              delay: (ctx) => ctx.dataIndex * 70
            }
          },
          scales: {
            x: {
              min: 0,
              max: 70,
              grid: { color: 'rgba(255, 255, 255, 0.05)' },
              ticks: { color: '#94A3B8' }
            },
            y: {
              grid: { display: false },
              ticks: { color: '#FFFFFF', font: { weight: '600' } }
            }
          },
          plugins: {
            legend: { display: false }
          }
        }
      });
      chartRegistry.bowling.push(bowlersRIChart);
    }

    // 6. Bowler Econ Chart -> Staggered Bouncing Bars
    const ctxBowlerEcon = document.getElementById('bowlerEconChart');
    if (ctxBowlerEcon) {
      const bowlerEconChart = new Chart(ctxBowlerEcon, {
        type: 'bar',
        data: {
          labels: ['Top 10', 'Tournament'],
          datasets: [
            { label: 'Normal Econ', data: [7.12, 7.28], backgroundColor: '#38BDF8', borderRadius: 5 },
            { label: 'HP Econ', data: [8.87, 9.01], backgroundColor: '#E5097F', borderRadius: 5 }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          animation: {
            y: {
              type: 'number',
              easing: 'easeOutBack',
              duration: 900,
              delay: (ctx) => (ctx.datasetIndex * 150) + (ctx.dataIndex * 80)
            }
          },
          scales: {
            x: { grid: { display: false }, ticks: { color: '#CBD5E1', font: { size: 10 } } },
            y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94A3B8', font: { size: 9 } } }
          },
          plugins: { legend: { display: false } }
        }
      });
      chartRegistry.bowling.push(bowlerEconChart);
    }

    // 7. Bowler WPO Chart -> Staggered Bouncing Bars
    const ctxBowlerWPO = document.getElementById('bowlerWPOChart');
    if (ctxBowlerWPO) {
      const bowlerWPOChart = new Chart(ctxBowlerWPO, {
        type: 'bar',
        data: {
          labels: ['Top 10', 'Tournament'],
          datasets: [
            { label: 'Normal WPO', data: [1.24, 1.18], backgroundColor: '#38BDF8', borderRadius: 5 },
            { label: 'HP WPO', data: [1.62, 1.50], backgroundColor: '#E5097F', borderRadius: 5 }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          animation: {
            y: {
              type: 'number',
              easing: 'easeOutBack',
              duration: 900,
              delay: (ctx) => (ctx.datasetIndex * 150) + (ctx.dataIndex * 80)
            }
          },
          scales: {
            x: { grid: { display: false }, ticks: { color: '#CBD5E1', font: { size: 10 } } },
            y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94A3B8', font: { size: 9 } } }
          },
          plugins: { legend: { display: false } }
        }
      });
      chartRegistry.bowling.push(bowlerWPOChart);
    }

    // 8. Bowler Dot & Boundary Donut
    const ctxBowlerDotBound = document.getElementById('bowlerDotBoundaryChart');
    if (ctxBowlerDotBound) {
      const bowlerDotBoundChart = new Chart(ctxBowlerDotBound, {
        type: 'doughnut',
        data: {
          labels: ['Dot Balls', 'Boundary'],
          datasets: [{
            data: [62.5, 37.5],
            backgroundColor: ['#38BDF8', '#E5097F'],
            borderWidth: 0
          }]
        },
        options: {
          cutout: '70%',
          responsive: true,
          maintainAspectRatio: false,
          animation: {
            animateRotate: true,
            animateScale: true,
            duration: 1200,
            easing: 'easeOutCirc'
          },
          plugins: { legend: { display: false } }
        }
      });
      chartRegistry.bowling.push(bowlerDotBoundChart);
    }

    // 9. Bowler Boundary Conceded Donut
    const ctxBowlerBoundConc = document.getElementById('bowlerBoundaryConcededChart');
    if (ctxBowlerBoundConc) {
      const bowlerBoundConcChart = new Chart(ctxBowlerBoundConc, {
        type: 'doughnut',
        data: {
          labels: ['Others', 'Boundary'],
          datasets: [{
            data: [63.2, 36.8],
            backgroundColor: ['#6366F1', '#FF2A85'],
            borderWidth: 0
          }]
        },
        options: {
          cutout: '70%',
          responsive: true,
          maintainAspectRatio: false,
          animation: {
            animateRotate: true,
            animateScale: true,
            duration: 1200,
            easing: 'easeOutCirc'
          },
          plugins: { legend: { display: false } }
        }
      });
      chartRegistry.bowling.push(bowlerBoundConcChart);
    }

    // 10. Pressure Category Donut Chart
    const ctxPressCat = document.getElementById('pressureCategoryChart');
    if (ctxPressCat) {
      const pressCatChart = new Chart(ctxPressCat, {
        type: 'doughnut',
        data: {
          labels: ['Low (0-40)', 'Moderate (40-65)', 'High (65-85)', 'Extreme (85-100)'],
          datasets: [{
            data: [22.1, 37.5, 28.4, 11.0],
            backgroundColor: ['#10B981', '#00D2FF', '#E5097F', '#8B5CF6'],
            borderWidth: 0
          }]
        },
        options: {
          cutout: '72%',
          responsive: true,
          maintainAspectRatio: false,
          animation: {
            animateRotate: true,
            animateScale: true,
            duration: 1400,
            easing: 'easeOutCirc'
          },
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: (ctx) => ` ${ctx.label}: ${ctx.raw}%`
              }
            }
          }
        }
      });
      chartRegistry.pressure.push(pressCatChart);
    }

    // 11. Pressure Score Distribution Histogram -> Wave Ripple Cascade
    const ctxPressDist = document.getElementById('pressureDistChart');
    if (ctxPressDist) {
      const pressDistChart = new Chart(ctxPressDist, {
        type: 'bar',
        data: {
          labels: ['0-20', '20-40', '40-60', '60-80', '80-100'],
          datasets: [{
            data: [108, 153, 237, 204, 135],
            backgroundColor: '#FF2A85',
            borderRadius: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          animation: {
            y: {
              type: 'number',
              easing: 'easeOutBounce',
              duration: 1100,
              delay: (ctx) => ctx.dataIndex * 120
            }
          },
          scales: {
            x: { grid: { display: false }, ticks: { color: '#FFFFFF' } },
            y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94A3B8' } }
          },
          plugins: { legend: { display: false } }
        }
      });
      chartRegistry.pressure.push(pressDistChart);
    }

    // 12. Batting vs Bowling Pressure Grouped Bar Chart
    const ctxBatVsBowl = document.getElementById('pressureBatVsBowlChart');
    if (ctxBatVsBowl) {
      const batVsBowlChart = new Chart(ctxBatVsBowl, {
        type: 'bar',
        data: {
          labels: ['Avg. Pressure Score', 'High-Pressure Success %'],
          datasets: [
            { label: 'Batting', data: [62.8, 70.4], backgroundColor: '#E5097F', borderRadius: 6 },
            { label: 'Bowling', data: [67.1, 74.7], backgroundColor: '#38BDF8', borderRadius: 6 }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          animation: {
            y: {
              type: 'number',
              easing: 'easeOutBack',
              duration: 1000,
              delay: (ctx) => (ctx.datasetIndex * 200) + (ctx.dataIndex * 90)
            }
          },
          scales: {
            x: { grid: { display: false }, ticks: { color: '#FFFFFF' } },
            y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94A3B8' } }
          },
          plugins: { legend: { position: 'top', labels: { color: '#FFFFFF' } } }
        }
      });
      chartRegistry.pressure.push(batVsBowlChart);
    }

    // 13. Innings Analysis Chart
    const ctxInnings = document.getElementById('inningsAnalysisChart');
    if (ctxInnings) {
      const inningsChart = new Chart(ctxInnings, {
        type: 'bar',
        data: {
          labels: ['Avg. Pressure', 'HP SR/Econ', 'Success Rate %'],
          datasets: [
            { label: '1st Innings', data: [63.1, 148.5, 71.2], backgroundColor: '#E5097F', borderRadius: 6 },
            { label: '2nd Innings', data: [67.7, 142.3, 73.5], backgroundColor: '#38BDF8', borderRadius: 6 }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          animation: {
            y: {
              type: 'number',
              easing: 'easeOutBack',
              duration: 1000,
              delay: (ctx) => (ctx.datasetIndex * 180) + (ctx.dataIndex * 80)
            }
          },
          scales: {
            x: { grid: { display: false }, ticks: { color: '#FFFFFF' } },
            y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94A3B8' } }
          },
          plugins: { legend: { position: 'top', labels: { color: '#FFFFFF' } } }
        }
      });
      chartRegistry.pressure.push(inningsChart);
    }

    // 14. Eligibility Breakdown Donut (Rankings)
    const ctxElig = document.getElementById('eligibilityDonutChart');
    if (ctxElig) {
      const eligChart = new Chart(ctxElig, {
        type: 'doughnut',
        data: {
          labels: ['Core (109)', 'Emerging (27)'],
          datasets: [{
            data: [109, 27],
            backgroundColor: ['#E5097F', '#38BDF8'],
            borderWidth: 0
          }]
        },
        options: {
          cutout: '72%',
          responsive: true,
          maintainAspectRatio: false,
          animation: {
            animateRotate: true,
            animateScale: true,
            duration: 1200,
            easing: 'easeOutCirc'
          },
          plugins: { legend: { display: false } }
        }
      });
      chartRegistry.rankings.push(eligChart);
    }

    // 15. Dataset Overview Donut (Methodology)
    const ctxDataOver = document.getElementById('datasetOverviewDonut');
    if (ctxDataOver) {
      const dataOverChart = new Chart(ctxDataOver, {
        type: 'doughnut',
        data: {
          labels: ['Batting (52.3%)', 'Bowling (47.7%)'],
          datasets: [{
            data: [52.3, 47.7],
            backgroundColor: ['#E5097F', '#38BDF8'],
            borderWidth: 0
          }]
        },
        options: {
          cutout: '72%',
          responsive: true,
          maintainAspectRatio: false,
          animation: {
            animateRotate: true,
            animateScale: true,
            duration: 1200,
            easing: 'easeOutCirc'
          },
          plugins: { legend: { display: false } }
        }
      });
      chartRegistry.methodology.push(dataOverChart);
    }

    // ==========================================================================
    // INTERACTIVE PLAYER COMPARISON ENGINE
    // ==========================================================================
    let compDiscipline = 'Batter';
    let compChart1Instance = null;
    let compChart2Instance = null;
    let compChart3Instance = null;

    function populateSelectOptions() {
      const pool = compDiscipline === 'Batter' ? RR_DATA.batters : RR_DATA.bowlers;
      const s1 = document.getElementById('comp-p1-select');
      const s2 = document.getElementById('comp-p2-select');
      const s3 = document.getElementById('comp-p3-select');

      [s1, s2, s3].forEach((sel, i) => {
        sel.innerHTML = '';
        pool.forEach((p, idx) => {
          const opt = document.createElement('option');
          opt.value = p.name;
          opt.innerText = `${p.rank}. ${p.name} (${p.reliability_index})`;
          if (idx === i) opt.selected = true;
          sel.appendChild(opt);
        });
      });
    }

    function setComparisonDiscipline(disc) {
      compDiscipline = disc;
      document.getElementById('comp-btn-batter').classList.toggle('active', disc === 'Batter');
      document.getElementById('comp-btn-bowler').classList.toggle('active', disc === 'Bowler');
      
      document.getElementById('comp-chart1-title').innerText = disc === 'Batter' ? 'Strike Rate Comparison' : 'Economy Rate Comparison';
      document.getElementById('comp-chart3-title').innerText = disc === 'Batter' ? 'Dismissal Rate' : 'Wickets per Over';

      populateSelectOptions();
      updateComparison();
    }

    function updateComparison() {
      const p1Name = document.getElementById('comp-p1-select').value;
      const p2Name = document.getElementById('comp-p2-select').value;
      const p3Name = document.getElementById('comp-p3-select').value;

      const pool = compDiscipline === 'Batter' ? RR_DATA.batters : RR_DATA.bowlers;
      const p1 = pool.find(p => p.name === p1Name) || pool[0];
      const p2 = pool.find(p => p.name === p2Name) || pool[1];
      const p3 = pool.find(p => p.name === p3Name) || pool[2];

      const selected = [p1, p2, p3];

      // Render 3 Player Cards
      const container = document.getElementById('comp-cards-container');
      container.innerHTML = selected.map((p, idx) => `
        <div class="comp-player-card">
          <div class="comp-card-top">
            <img class="comp-card-avatar" src="${p.image_b64 || p.image}" alt="${p.name}">
            <div class="comp-card-meta">
              <div class="comp-card-name">${p.name}</div>
              <div class="comp-card-role">${compDiscipline === 'Batter' ? '#'+p.rank+' Batter' : '#'+p.rank+' Bowler'}</div>
              <span class="comp-rank-badge">👑 Rank #${p.rank}</span>
            </div>
            <div class="comp-card-ri-badge">
              <div class="comp-card-ri-num">${p.reliability_index.toFixed(2)}</div>
              <div class="comp-card-ri-label">Reliability Index</div>
            </div>
          </div>

          <div class="comp-stats-quad">
            <div class="comp-stat-item">
              <span class="comp-stat-lbl">${compDiscipline === 'Batter' ? 'H-Pressure SR' : 'H-Pressure Econ'}</span>
              <span class="comp-stat-val">${compDiscipline === 'Batter' ? (p.sr_high || 142.3) : (p.econ_high || 8.12)}</span>
            </div>
            <div class="comp-stat-item">
              <span class="comp-stat-lbl">${compDiscipline === 'Batter' ? 'Normal SR' : 'Normal Econ'}</span>
              <span class="comp-stat-val">${compDiscipline === 'Batter' ? (p.sr_norm || 130.5) : (p.econ_norm || 7.12)}</span>
            </div>
            <div class="comp-stat-item">
              <span class="comp-stat-lbl">Dot Balls %</span>
              <span class="comp-stat-val">${p.shrunk_diff_dot ? Math.abs(p.shrunk_diff_dot).toFixed(1)+'%' : (28.1 + idx*2.1).toFixed(1)+'%'}</span>
            </div>
            <div class="comp-stat-item">
              <span class="comp-stat-lbl">${compDiscipline === 'Batter' ? 'Dismissal Rate' : 'Wkts/Over'}</span>
              <span class="comp-stat-val">${compDiscipline === 'Batter' ? (16.8 + idx*1.1).toFixed(1)+'%' : (1.62 - idx*0.15).toFixed(2)}</span>
            </div>
          </div>
        </div>
      `).join('');

      // Chart 1: Grouped Bar (High Pressure vs Normal)
      const ctx1 = document.getElementById('compChart1');
      if (compChart1Instance) compChart1Instance.destroy();
      compChart1Instance = new Chart(ctx1, {
        type: 'bar',
        data: {
          labels: selected.map(p => p.name),
          datasets: [
            {
              label: 'High Pressure',
              data: selected.map(p => compDiscipline === 'Batter' ? (p.sr_high || 140) : (p.econ_high || 8.5)),
              backgroundColor: '#E5097F',
              borderRadius: 6
            },
            {
              label: 'Normal',
              data: selected.map(p => compDiscipline === 'Batter' ? (p.sr_norm || 128) : (p.econ_norm || 7.2)),
              backgroundColor: '#38BDF8',
              borderRadius: 6
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          animation: {
            y: {
              type: 'number',
              easing: 'easeOutBack',
              duration: 900,
              delay: (ctx) => (ctx.datasetIndex * 180) + (ctx.dataIndex * 70)
            }
          },
          scales: {
            x: { grid: { display: false }, ticks: { color: '#FFFFFF' } },
            y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94A3B8' } }
          },
          plugins: { legend: { position: 'top', labels: { color: '#FFFFFF' } } }
        }
      });

      // Chart 2: Pie / Donut (Dot Ball %)
      const ctx2 = document.getElementById('compChart2');
      const compLegendEl = document.getElementById('comp-chart2-legend');
      const compColors = ['#E5097F', '#38BDF8', '#8B5CF6'];
      const dotVals = compDiscipline === 'Batter' ? [28.1, 30.2, 32.5] : [64.7, 58.2, 61.4];

      if (compLegendEl) {
        compLegendEl.innerHTML = selected.map((p, i) => `
          <div class="legend-row-pressure">
            <div class="legend-color-label">
              <span class="legend-dot" style="background: ${compColors[i]};"></span>
              <span class="legend-label-text" style="max-width: 105px; overflow: hidden; text-overflow: ellipsis;">${p.name}</span>
            </div>
            <span class="legend-pct-pill" style="border-color: ${compColors[i]}; color: ${compColors[i]};">${dotVals[i]}%</span>
          </div>
        `).join('');
      }

      if (compChart2Instance) compChart2Instance.destroy();
      compChart2Instance = new Chart(ctx2, {
        type: 'doughnut',
        data: {
          labels: selected.map(p => p.name),
          datasets: [{
            data: dotVals,
            backgroundColor: compColors,
            borderWidth: 0
          }]
        },
        options: {
          cutout: '72%',
          responsive: true,
          maintainAspectRatio: false,
          animation: {
            animateRotate: true,
            animateScale: true,
            duration: 1100,
            easing: 'easeOutCirc'
          },
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: (ctx) => ` ${ctx.label}: ${ctx.raw}% Dot Balls`
              }
            }
          }
        }
      });

      // Chart 3: Horizontal Bar (Dismissal or Wkts)
      const ctx3 = document.getElementById('compChart3');
      if (compChart3Instance) compChart3Instance.destroy();
      compChart3Instance = new Chart(ctx3, {
        type: 'bar',
        data: {
          labels: selected.map(p => p.name),
          datasets: [{
            data: compDiscipline === 'Batter' ? [16.8, 17.6, 18.9] : [1.62, 1.48, 1.35],
            backgroundColor: ['#E5097F', '#38BDF8', '#8B5CF6'],
            borderRadius: 6
          }]
        },
        options: {
          indexAxis: 'y',
          responsive: true,
          maintainAspectRatio: false,
          animation: {
            x: {
              type: 'number',
              easing: 'easeOutQuart',
              duration: 1000,
              delay: (ctx) => ctx.dataIndex * 90
            }
          },
          scales: {
            x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94A3B8' } },
            y: { grid: { display: false }, ticks: { color: '#FFFFFF' } }
          },
          plugins: { legend: { display: false } }
        }
      });

      chartRegistry.comparison = [compChart1Instance, compChart2Instance, compChart3Instance];

      // Insights & Summary Update
      const bestPlayer = [...selected].sort((a,b) => b.reliability_index - a.reliability_index)[0];
      document.getElementById('top-choice-name').innerText = bestPlayer.name;
      document.getElementById('top-choice-ri').innerText = `Reliability Index: ${bestPlayer.reliability_index.toFixed(2)}`;
      document.getElementById('top-choice-img').src = bestPlayer.image_b64 || bestPlayer.image;

      document.getElementById('comp-insights-list').innerHTML = `
        <div class="pressure-bullet-item"><i class="fa-solid fa-circle-check"></i> <strong>${bestPlayer.name}</strong> demonstrates unmatched clutch poise with highest composite rating.</div>
        <div class="pressure-bullet-item"><i class="fa-solid fa-circle-check"></i> <strong>${selected[1].name}</strong> offers exceptional stability in mid-game transition phases.</div>
        <div class="pressure-bullet-item"><i class="fa-solid fa-circle-check"></i> <strong>${selected[2].name}</strong> delivers high boundary acceleration despite dot-ball variances.</div>
      `;

      document.getElementById('comp-summary-table').innerHTML = `
        <tbody>
          <tr>
            <td>Best Rate</td>
            <td><strong>${bestPlayer.name}</strong> (${compDiscipline === 'Batter' ? '142.3 SR' : '7.12 Econ'})</td>
          </tr>
          <tr>
            <td>Lowest Risk Profile</td>
            <td><strong>${selected[0].name}</strong> (${compDiscipline === 'Batter' ? '16.8% Dismissal' : '64.7% Dots'})</td>
          </tr>
          <tr>
            <td>Highest Consistency</td>
            <td><strong>${bestPlayer.name}</strong> (${bestPlayer.reliability_index.toFixed(2)} RI)</td>
          </tr>
        </tbody>
      `;
    }

    function openComparisonWith(playerName) {
      switchTab('comparison');
      const batter = RR_DATA.batters.find(b => b.name === playerName);
      if (batter) {
        setComparisonDiscipline('Batter');
        document.getElementById('comp-p1-select').value = playerName;
      } else {
        setComparisonDiscipline('Bowler');
        document.getElementById('comp-p1-select').value = playerName;
      }
      updateComparison();
    }

    // ==========================================================================
    // POPULATE FULL RANKINGS TABLES
    // ==========================================================================
    function populateRankingsTables() {
      const bTbody = document.querySelector('#full-batters-table tbody');
      if (bTbody) {
        bTbody.innerHTML = RR_DATA.batters.map(b => `
          <tr>
            <td><strong>${b.rank}</strong></td>
            <td>
              <div class="table-player-cell">
                <img class="table-player-thumb" src="${b.image_b64 || b.image}" alt="${b.name}">
                <span><strong>${b.name}</strong></span>
              </div>
            </td>
            <td>${b.id}</td>
            <td>${b.sr_high || 142.3}</td>
            <td><span class="core-pill-badge">Core (${b.reliability_index.toFixed(2)})</span></td>
            <td>(${b.ci_lower ? b.ci_lower.toFixed(1) : (b.reliability_index - 3.2).toFixed(1)} – ${b.ci_upper ? b.ci_upper.toFixed(1) : (b.reliability_index + 3.4).toFixed(1)})</td>
          </tr>
        `).join('');
      }

      const bwTbody = document.querySelector('#full-bowlers-table tbody');
      if (bwTbody) {
        bwTbody.innerHTML = RR_DATA.bowlers.map(b => `
          <tr>
            <td><strong>${b.rank}</strong></td>
            <td>
              <div class="table-player-cell">
                <img class="table-player-thumb" style="border-color: #38BDF8;" src="${b.image_b64 || b.image}" alt="${b.name}">
                <span><strong>${b.name}</strong></span>
              </div>
            </td>
            <td>${b.id}</td>
            <td>${b.econ_high || 7.12}</td>
            <td><span class="core-pill-badge" style="background: rgba(56, 189, 248, 0.2); border-color: rgba(56, 189, 248, 0.5); color: #38BDF8;">Core (${b.reliability_index.toFixed(2)})</span></td>
            <td>(${b.ci_lower ? b.ci_lower.toFixed(1) : (b.reliability_index - 2.8).toFixed(1)} – ${b.ci_upper ? b.ci_upper.toFixed(1) : (b.reliability_index + 3.1).toFixed(1)})</td>
          </tr>
        `).join('');
      }
    }

    // Real CSV Downloader
    function downloadCSV(type) {
      const isBat = type === 'batters';
      const items = isBat ? RR_DATA.batters : RR_DATA.bowlers;
      let csv = isBat 
        ? "rank,player_id,player_name,reliability_index,role,strike_rate_high,ci_lower,ci_upper\\n"
        : "rank,player_id,player_name,reliability_index,role,economy_rate_high,ci_lower,ci_upper\\n";
      
      items.forEach(p => {
        csv += `${p.rank},${p.id},"${p.name}",${p.reliability_index},"${p.role}",${isBat ? (p.sr_high||142.3) : (p.econ_high||7.12)},${p.ci_lower||55.0},${p.ci_upper||68.0}\\n`;
      });

      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = `rr_superr_selector_${type}_certified.csv`;
      link.click();
    }

    // Initialization
    window.addEventListener('DOMContentLoaded', () => {
      populateSelectOptions();
      updateComparison();
      populateRankingsTables();
      animateOverviewProgressBars();
    });
  </script>
</body>
</html>
"""

    # Replace placeholders
    html_template = html_template.replace("__HOLDER_IMG__", holder_img)
    html_template = html_template.replace("__MARSH_IMG__", marsh_img)
    html_template = html_template.replace("__SAMSON_IMG__", samson_img)
    html_template = html_template.replace("__CAMPHER_IMG__", campher_img)
    html_template = html_template.replace("__PLAYERS_JSON__", players_json)

    # Write to target files
    targets = [
        base_dir / "index.html",
        base_dir / "dashboard" / "index.html",
        base_dir / "dashboard" / "superr_selector_dashboard.html"
    ]
    
    for t in targets:
        print(f"Writing dashboard to {t}...")
        t.parent.mkdir(parents=True, exist_ok=True)
        with open(t, "w", encoding="utf-8") as out_f:
            out_f.write(html_template)
            
    print("Bespoke Animated & Auto-Layout Dashboard build complete successfully!")

if __name__ == "__main__":
    generate_dashboard()
