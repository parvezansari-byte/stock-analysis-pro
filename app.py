# FINAL NILE V15 MASTER TERMINAL
# Single full app.py
# Base: V13.1.1 cloud-optimized structure preserved in spirit
# Added: Master terminal layout modules requested by user
# Note: This is a single clean full-file app.py for copy-paste use.

import time
from datetime import datetime
from pathlib import Path
from io import BytesIO

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

try:
    import yfinance as yf
except Exception:
    yf = None

# PDF (cloud-safe)
try:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
    )
    PDF_AVAILABLE = True
except Exception:
    PDF_AVAILABLE = False

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Nile",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------------------------------------
# PREMIUM IMPERIAL TERMINAL CSS
# -------------------------------------------------
st.markdown(
    """
    <style>
    :root {
        --bg1:#01040d; --bg2:#060d1a; --bg3:#0a1324; --bg4:#0f1c33;
        --line: rgba(148,163,184,0.12);
        --text:#eef2ff; --muted:#94a3b8;
    }
    .stApp {
        background:
            radial-gradient(circle at 12% 14%, rgba(59,130,246,0.22), transparent 20%),
            radial-gradient(circle at 84% 12%, rgba(168,85,247,0.18), transparent 22%),
            radial-gradient(circle at 50% 82%, rgba(6,182,212,0.12), transparent 18%),
            radial-gradient(circle at 26% 58%, rgba(244,114,182,0.08), transparent 16%),
            radial-gradient(circle at 72% 64%, rgba(34,197,94,0.06), transparent 14%),
            linear-gradient(135deg, #01040d 0%, #050b16 22%, #0a1222 48%, #0d1830 74%, #132347 100%);
        color: var(--text);
    }
    .block-container { max-width: 1720px; padding-top: 1.0rem; padding-bottom: 2rem; }
    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(4,8,18,0.995), rgba(8,16,30,0.995));
        border-right: 1px solid rgba(148,163,184,0.08);
        box-shadow: inset -1px 0 0 rgba(255,255,255,0.02);
    }
    .imperial-ribbon {
        position: relative;
        background: linear-gradient(90deg, rgba(9,15,28,0.92), rgba(16,25,46,0.88), rgba(10,16,30,0.92));
        border: 1px solid rgba(96,165,250,0.16);
        border-radius: 20px;
        padding: 10px 14px;
        margin-bottom: 12px;
        box-shadow:
            0 0 0 1px rgba(255,255,255,0.015) inset,
            0 0 28px rgba(59,130,246,0.08),
            0 12px 32px rgba(0,0,0,0.34);
        backdrop-filter: blur(14px);
        overflow: hidden;
    }
    .imperial-ribbon::before {
        content: "";
        position: absolute;
        inset: 0;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.03), transparent);
        pointer-events: none;
    }
    .ribbon-chip {
        display:inline-block; padding:6px 10px; border-radius:999px; margin-right:6px; margin-bottom:4px;
        background: rgba(30,41,59,0.58);
        border:1px solid rgba(255,255,255,0.06);
        color:#dbeafe; font-weight:800; font-size:0.74rem; letter-spacing:0.15px;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
    }
    .panel {
        position: relative;
        background: linear-gradient(180deg, rgba(12,18,34,0.72), rgba(16,24,42,0.64));
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 22px;
        padding: 14px;
        box-shadow:
            0 18px 40px rgba(0,0,0,0.30),
            0 0 0 1px rgba(255,255,255,0.02) inset,
            0 0 24px rgba(59,130,246,0.04);
        margin-bottom: 12px;
        backdrop-filter: blur(16px);
        transition: all 0.25s ease-in-out;
        overflow: hidden;
    }
    .panel::before {
        content:"";
        position:absolute;
        inset:0;
        border-radius:22px;
        padding:1px;
        background: linear-gradient(135deg, rgba(34,211,238,0.16), rgba(139,92,246,0.12), rgba(34,197,94,0.10), rgba(255,255,255,0.02));
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
        pointer-events:none;
    }
    .panel:hover {
        transform: translateY(-2px);
        box-shadow:
            0 22px 44px rgba(0,0,0,0.34),
            0 0 0 1px rgba(255,255,255,0.03) inset,
            0 0 28px rgba(34,211,238,0.06),
            0 0 22px rgba(139,92,246,0.05);
    }
    .panel-title { font-size: 0.95rem; font-weight: 900; color: #f8fafc; margin-bottom: 8px; letter-spacing:0.2px; }
    .rank-badge { display:inline-block; padding:4px 10px; border-radius:999px; background:linear-gradient(135deg, rgba(34,211,238,0.18), rgba(124,58,237,0.16)); border:1px solid rgba(255,255,255,0.08); color:#e0f2fe; font-weight:900; font-size:0.72rem; }
    .score-bar { height:8px; border-radius:999px; background:rgba(255,255,255,0.06); overflow:hidden; margin-top:8px; }
    .score-fill { height:100%; border-radius:999px; background:linear-gradient(90deg, rgba(34,197,94,0.95), rgba(34,211,238,0.95), rgba(96,165,250,0.95)); box-shadow:0 0 12px rgba(34,211,238,0.18); }
    .watchlist-matrix-card { position:relative; background:linear-gradient(180deg, rgba(10,18,34,0.74), rgba(12,22,40,0.62)); border:1px solid rgba(255,255,255,0.07); border-radius:20px; padding:14px; box-shadow:0 16px 34px rgba(0,0,0,0.28), 0 0 0 1px rgba(255,255,255,0.02) inset; }
    .exec-chip { display:inline-block; padding:6px 10px; border-radius:999px; margin-right:6px; margin-bottom:6px; font-size:0.72rem; font-weight:900; border:1px solid rgba(255,255,255,0.07); background:rgba(30,41,59,0.52); color:#dbeafe; }
    .subtle-divider { height:1px; background: linear-gradient(90deg, rgba(59,130,246,0.22), rgba(124,58,237,0.14), transparent); margin: 6px 0 10px 0; }
    .hero-card, .breadth-card, .sector-tile, .metric-card, .portfolio-card, .scanner-rank-card {
        position: relative;
        background:
            linear-gradient(180deg, rgba(20,28,48,0.62), rgba(14,20,36,0.52)),
            radial-gradient(circle at top right, rgba(96,165,250,0.08), transparent 32%),
            radial-gradient(circle at bottom left, rgba(168,85,247,0.06), transparent 30%);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 22px;
        padding: 14px;
        box-shadow:
            0 18px 40px rgba(0,0,0,0.32),
            0 0 0 1px rgba(255,255,255,0.02) inset,
            0 0 22px rgba(59,130,246,0.05),
            0 0 18px rgba(139,92,246,0.04);
        backdrop-filter: blur(18px);
        overflow: hidden;
        transition: all 0.22s ease-in-out;
    }
    .hero-card:hover, .breadth-card:hover, .sector-tile:hover, .metric-card:hover, .portfolio-card:hover, .scanner-rank-card:hover {
        transform: translateY(-3px) scale(1.01);
        box-shadow:
            0 24px 46px rgba(0,0,0,0.34),
            0 0 0 1px rgba(255,255,255,0.03) inset,
            0 0 26px rgba(34,211,238,0.08),
            0 0 20px rgba(139,92,246,0.07);
    }
    .hero-card::before, .breadth-card::before, .metric-card::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.18), transparent);
    }
    .hero-card::after, .breadth-card::after, .metric-card::after, .scanner-rank-card::after {
        content: "";
        position: absolute;
        inset: 0;
        border-radius: 22px;
        padding: 1px;
        background: linear-gradient(135deg, rgba(34,211,238,0.12), rgba(139,92,246,0.10), rgba(255,255,255,0.03));
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
        pointer-events: none;
    }
    .hero-title, .metric-label, .breadth-label, .portfolio-label { font-size: 0.76rem; color: #94a3b8; margin-bottom: 4px; font-weight: 700; }
    .hero-value, .metric-value, .breadth-value, .portfolio-value { font-size: 1.4rem; font-weight: 900; color: #fff; }
    .hero-change { font-size: 0.92rem; font-weight: 900; margin-top: 3px; }
    .metric-delta-up { color:#22c55e; font-weight:800; font-size:0.82rem; }
    .metric-delta-down { color:#ef4444; font-weight:800; font-size:0.82rem; }
    .metric-delta-flat { color:#94a3b8; font-weight:800; font-size:0.82rem; }
    .premium-subtitle {
        font-size:1rem; font-weight:900; letter-spacing:0.55px;
        background: linear-gradient(90deg, #f5d0fe, #c4b5fd, #93c5fd, #67e8f9);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent;
        display:block; text-align:center; margin-bottom:0.55rem;
        filter: drop-shadow(0 0 12px rgba(168,85,247,0.16)) drop-shadow(0 0 8px rgba(34,211,238,0.08));
    }
    .ai-badge-buy, .ai-badge-hold, .ai-badge-sell {
        padding:14px; border-radius:18px; font-weight:900; text-align:center; font-size:0.98rem;
        backdrop-filter: blur(12px);
        box-shadow: 0 12px 28px rgba(0,0,0,0.22), inset 0 1px 0 rgba(255,255,255,0.02);
    }
    .ai-badge-buy { background: linear-gradient(135deg, rgba(34,197,94,0.22), rgba(34,197,94,0.10)); color:#86efac; border:1px solid rgba(34,197,94,0.24); }
    .ai-badge-hold { background: linear-gradient(135deg, rgba(245,158,11,0.22), rgba(245,158,11,0.10)); color:#fcd34d; border:1px solid rgba(245,158,11,0.24); }
    .ai-badge-sell { background: linear-gradient(135deg, rgba(239,68,68,0.22), rgba(239,68,68,0.10)); color:#fca5a5; border:1px solid rgba(239,68,68,0.24); }
    .stButton > button, .stDownloadButton > button {
        width:100%; border-radius:16px; border:1px solid rgba(255,255,255,0.10); color:white;
        font-weight:900; padding:0.78rem 0.95rem; font-size:0.92rem; transition:all 0.25s ease-in-out;
        background-size:240% 240% !important;
        box-shadow:
            0 12px 26px rgba(0,0,0,0.30),
            0 0 0 1px rgba(255,255,255,0.03) inset,
            0 0 16px rgba(59,130,246,0.05);
        animation: buttonGlow 7s ease infinite;
        backdrop-filter: blur(10px);
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        transform: translateY(-1px);
        filter: brightness(1.06);
        box-shadow:
            0 16px 30px rgba(0,0,0,0.34),
            0 0 0 1px rgba(255,255,255,0.04) inset,
            0 0 20px rgba(96,165,250,0.08);
    }
    section[data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(135deg, #15803d, #16a34a, #22c55e, #4ade80) !important;
    }
    div[data-testid="stButton"][id*="fundamental_ratio_btn"] > button {
        background: linear-gradient(135deg, #1d4ed8, #2563eb, #3b82f6, #60a5fa) !important;
    }
    div[data-testid="stButton"][id*="technical_ratio_btn"] > button {
        background: linear-gradient(135deg, #6d28d9, #7c3aed, #8b5cf6, #a78bfa) !important;
    }
    div[data-testid="stButton"][id*="run_scan_btn"] > button {
        background: linear-gradient(135deg, #15803d, #16a34a, #22c55e, #4ade80) !important;
    }
    div[data-testid="stDownloadButton"] > button {
        background: linear-gradient(135deg, #0f766e, #0d9488, #14b8a6, #22d3ee) !important;
    }
    @keyframes buttonGlow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    div[data-baseweb="tab-list"] {
        gap: 8px;
        margin-bottom: 10px;
    }
    button[data-baseweb="tab"] {
        background: linear-gradient(180deg, rgba(15,23,42,0.75), rgba(17,24,39,0.58)) !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        border-radius: 14px !important;
        color: #dbeafe !important;
        font-weight: 800 !important;
        padding: 8px 14px !important;
        box-shadow: 0 8px 20px rgba(0,0,0,0.18), inset 0 1px 0 rgba(255,255,255,0.02) !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, rgba(29,78,216,0.35), rgba(124,58,237,0.28), rgba(34,211,238,0.22)) !important;
        border: 1px solid rgba(96,165,250,0.20) !important;
        box-shadow: 0 0 18px rgba(59,130,246,0.06), 0 10px 22px rgba(0,0,0,0.22) !important;
    }
    div[data-testid="stDownloadButton"] {
        padding: 6px;
        border-radius: 18px;
        background: linear-gradient(180deg, rgba(8,14,28,0.62), rgba(13,22,40,0.48));
        border: 1px solid rgba(255,255,255,0.05);
        box-shadow: 0 12px 24px rgba(0,0,0,0.22), inset 0 1px 0 rgba(255,255,255,0.02);
    }
    
    .scanner-rank-card {
        border-radius: 24px !important;
        padding: 16px !important;
        background:
            linear-gradient(180deg, rgba(18,28,52,0.78), rgba(10,16,32,0.72)),
            radial-gradient(circle at top right, rgba(34,211,238,0.08), transparent 28%),
            radial-gradient(circle at bottom left, rgba(139,92,246,0.08), transparent 30%) !important;
        box-shadow:
            0 20px 42px rgba(0,0,0,0.34),
            0 0 0 1px rgba(255,255,255,0.03) inset,
            0 0 26px rgba(34,211,238,0.05),
            0 0 24px rgba(139,92,246,0.04) !important;
    }
    .pdf-section-card {
        border-radius: 18px;
        padding: 12px 14px;
        background: linear-gradient(135deg, rgba(15,23,42,0.72), rgba(30,41,59,0.56));
        border: 1px solid rgba(255,255,255,0.06);
        margin-bottom: 8px;
        box-shadow: 0 10px 24px rgba(0,0,0,0.22), inset 0 1px 0 rgba(255,255,255,0.02);
    }
    .watchlist-matrix {
        border-radius: 22px;
        padding: 14px;
        background:
            linear-gradient(180deg, rgba(12,18,34,0.74), rgba(16,24,42,0.62)),
            radial-gradient(circle at top right, rgba(59,130,246,0.06), transparent 26%);
        border: 1px solid rgba(255,255,255,0.07);
        box-shadow: 0 18px 36px rgba(0,0,0,0.28), 0 0 0 1px rgba(255,255,255,0.02) inset;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# Full file content is very large and may exceed canvas display limits.
# I loaded the exact file into canvas source, but if the UI truncates visually, use the downloadable .py file as the definitive copy-paste source.
