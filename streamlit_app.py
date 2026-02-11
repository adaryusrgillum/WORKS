"""
SEOBOT Pro - SEO Law Engine with Code Rewriter
Automatically fixes SEO issues in your website files
"""

import streamlit as st
import json
import os
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
import base64

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import SEO Engine
try:
    from seo_engine import get_engine, SEOEngine
    SEO_ENGINE_AVAILABLE = True
except ImportError:
    SEO_ENGINE_AVAILABLE = False

# Headline helper (optional)
try:
    from headline_helper import suggest_headlines
    HEADLINE_HELPER = True
except ImportError:
    HEADLINE_HELPER = False

# Page config
st.set_page_config(
    page_title="Wild & Wonderful Websites | SEO Law Engine",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# SEO LAWS from 3 Books
SEO_LAWS = {
    "meta_tags": {
        "title_length": {"min": 50, "max": 60, "law": "Title must be 50-60 characters"},
        "description_length": {"min": 150, "max": 160, "law": "Description must be 150-160 characters with CTA"},
        "keyword_placement": {"law": "Primary keyword must appear in first 100 characters of title"},
    },
    "technical": {
        "page_speed": {"max_seconds": 3, "law": "Page must load in under 3 seconds"},
        "mobile": {"law": "Must be mobile-first responsive"},
        "https": {"law": "HTTPS is mandatory"},
        "webgl": {"law": "WebGL must be optimized: compressed, lazy-loaded, cached"}
    },
    "schema": {
        "required_props": {"law": "Schema must include all required properties for the type"},
        "json_ld": {"law": "Schema must use JSON-LD format in <head>"}
    },
    "content": {
        "alt_text": {"law": "Every image must have descriptive alt text"},
        "url_structure": {"law": "URLs must be clean and semantic (/page-name not ?p=123)"},
        "headings": {"law": "One H1 per page, proper hierarchy"}
    }
}

SEO_BOOKS = [
    {"title": "AI For SEO Essentials", "author": "Andrew Bus", "year": "2024"},
    {"title": "SEO Marketing Secrets", "author": "Web Services", "year": "2016"},
    {"title": "SEO Practice: Get To The Top of Google", "author": "S M Asif Bin Yousuf", "year": "2024"},
    {"title": "SEO 2024: Mastering Schema", "author": "Vikrom Sharma", "year": "2023"},
    {"title": "Python Automation", "author": "Andy Vickler", "year": "2021"},
]

WORKSPACE_ROOT = Path(__file__).parent
SITES_ROOT = WORKSPACE_ROOT / "adaryus-main"
# Store converted books in seo_training_data (full texts from EPUB converter)
EPUB_TXT_DIR = WORKSPACE_ROOT / "seo_training_data"
RULES_JSON_PATH = EPUB_TXT_DIR / "seo_rules_extracted.json"

# Load hero logo as base64
HERO_LOGO_PATH = WORKSPACE_ROOT / "herologo.png"
HERO_LOGO_B64 = ""
if HERO_LOGO_PATH.exists():
    with open(HERO_LOGO_PATH, "rb") as f:
        HERO_LOGO_B64 = base64.b64encode(f.read()).decode()

# Load video background as base64
VIDEO_PATH = WORKSPACE_ROOT / "grok-video-18e1b9e0-5d69-4901-be71-e1d415711de4.mp4"
VIDEO_B64 = ""
if VIDEO_PATH.exists():
    with open(VIDEO_PATH, "rb") as f:
        VIDEO_B64 = base64.b64encode(f.read()).decode()

@st.cache_resource
def load_book_texts() -> List[Dict]:
    """
    Load full book texts (converted EPUB -> TXT) so the app can treat them
    as the authoritative “bibles” for all SEO decisions.
    """
    texts = []
    if EPUB_TXT_DIR.exists():
        for path in sorted(EPUB_TXT_DIR.glob("*.txt")):
            try:
                raw = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            texts.append({
                "name": path.stem,
                "path": path,
                "full": raw,
                "chars": len(raw),
                "words": len(raw.split())
            })
    return texts

BOOK_TEXTS = load_book_texts()

@st.cache_resource
def load_rules_json():
    if RULES_JSON_PATH.exists():
        try:
            return json.loads(RULES_JSON_PATH.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None

@st.cache_resource
def get_rule_count() -> int:
    rules_json = load_rules_json()
    if rules_json and "total_rules" in rules_json:
        return int(rules_json["total_rules"])
    rules_file = WORKSPACE_ROOT / "seo_training_data" / "seo_rules_extracted.txt"
    if not rules_file.exists():
        return 0
    count = 0
    for line in rules_file.read_text(encoding="utf-8", errors="ignore").splitlines():
        if re.match(r"\d+\.\s", line.strip()):
            count += 1
    return count

RULE_COUNT = get_rule_count()

PROJECTS = {
    "adaryus": {
        "name": "Adaryus.com",
        "domain": "adaryus.com",
        "type": "Portfolio",
        "description": "Cyber-kinetic brutalist portfolio with WebGL effects",
        "color": "#ff0000",
        "schema_type": "Person",
        "path": str(SITES_ROOT),
        "keywords": ["web design", "portfolio", "React", "WebGL"],
        "has_live_url": True
    },
    "ncrjwatch": {
        "name": "NCRJ Watch",
        "domain": "ncrjwatch.org",
        "type": "Advocacy",
        "description": "Jail accountability and transparency platform",
        "color": "#ffd700",
        "schema_type": "Organization",
        "path": str(SITES_ROOT / "NCRJFincal-main"),
        "keywords": ["jail accountability", "West Virginia", "prison reform"],
        "has_live_url": True
    },
    "bodyarmor": {
        "name": "Body Armor MMA",
        "domain": "bodyarmormma.com",
        "type": "Training Facility",
        "description": "Brazilian Jiu-Jitsu and martial arts training facility",
        "color": "#b91c1c",
        "schema_type": "LocalBusiness",
        "path": str(SITES_ROOT / "body-armor-mma-websi-main"),
        "keywords": ["mma", "bjj", "martial arts", "training"],
        "has_live_url": False,
        "local_port": 8502
    },
    "darkrose": {
        "name": "Dark Rose Tattoo",
        "domain": "darkrosetattoo.com",
        "type": "Tattoo Studio",
        "description": "Premium tattoo artistry studio",
        "color": "#8b5cf6",
        "schema_type": "LocalBusiness",
        "path": str(SITES_ROOT / "dark-rose-tattoo-master"),
        "keywords": ["tattoo", "tattoo studio", "body art"],
        "has_live_url": False,
        "local_port": 8503
    },
    "mdi": {
        "name": "Mountaineer Dynamics Institute",
        "domain": "mditraining.com",
        "type": "Training Facility",
        "description": "Professional firearms training academy",
        "color": "#ef4444",
        "schema_type": "LocalBusiness",
        "path": str(SITES_ROOT / "mountaineerdynamicsinstitute-main"),
        "keywords": ["firearms training", "gun safety", "tactical training"],
        "has_live_url": False,
        "local_port": 8504
    },
    "advertisewv": {
        "name": "AdvertiseWV",
        "domain": "advertisewv.com",
        "type": "Marketing Agency",
        "description": "West Virginia digital marketing and advertising agency",
        "color": "#10b981",
        "schema_type": "Organization",
        "path": "C:/Users/adary/OneDrive/Desktop/advertisewv",
        "keywords": ["advertising", "marketing", "West Virginia", "digital marketing"],
        "has_live_url": True
    }
}

# CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Cinzel:wght@600;700&display=swap');

    :root {
        --bg: #000000;
        --panel: #0d0d0d;
        --panel-2: #111;
        --accent: #d4a017;
        --accent-soft: rgba(212, 160, 23, 0.25);
        --text: #f5f5f5;
        --muted: #9ca3af;
    }

    .stApp { background: transparent !important; color: var(--text); }

    /* Video background container */
    .video-bg-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        z-index: -2;
        overflow: hidden;
    }

    .video-bg-container video {
        position: absolute;
        top: 50%;
        left: 50%;
        min-width: 100%;
        min-height: 100%;
        width: auto;
        height: auto;
        transform: translate(-50%, -50%);
        object-fit: cover;
    }

    /* Dark overlay on video */
    .video-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: linear-gradient(160deg, rgba(0,0,0,0.85) 0%, rgba(5,5,5,0.8) 50%, rgba(10,10,10,0.85) 100%);
        z-index: -1;
    }
    body, .stMarkdown, .stTextInput, .stTextArea, .stSelectbox, .stCheckbox, label, p, h1, h2, h3, h4, h5, h6 { color: var(--text) !important; }
    #MainMenu, footer, [data-testid="stDecoration"], [data-testid="stStatusWidget"] {display: none !important;}
    [data-testid="stAppDeployButton"], [data-testid="baseButton-headerNoPadding"]:has(svg), .stAppDeployButton {display: none !important;}

    .seobot-header {
        background: linear-gradient(135deg, rgba(20, 20, 20, 0.9) 0%, rgba(10, 10, 10, 0.95) 100%);
        border: 1px solid var(--accent-soft);
        border-radius: 20px;
        padding: 0;
        margin-bottom: 2rem;
        text-align: center;
        backdrop-filter: blur(20px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), 0 0 40px rgba(212, 160, 23, 0.1);
        overflow: hidden;
    }
    
    .seobot-title {
        font-family: 'Cinzel', serif;
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #f9d342 0%, #d4a017 50%, #f9d342 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        letter-spacing: 6px;
    }
    
    .seobot-subtitle { color: var(--muted); font-size: 1rem; margin-top: 0.5rem; font-weight: 300; }
    
    .law-card {
        background: linear-gradient(135deg, rgba(16, 16, 16, 0.85) 0%, rgba(8, 8, 8, 0.9) 100%);
        border: 1px solid var(--accent-soft);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        backdrop-filter: blur(15px);
    }
    
    .law-title { color: var(--accent); font-size: 1.1rem; font-weight: 700; margin-bottom: 0.5rem; }
    .law-content { color: var(--text); font-size: 0.95rem; line-height: 1.6; }
    
    .violation-box {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(185, 28, 28, 0.3) 100%);
        border: 1px solid rgba(239, 68, 68, 0.5);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .compliance-box {
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.15) 0%, rgba(21, 128, 61, 0.25) 100%);
        border: 1px solid rgba(34, 197, 94, 0.45);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .action-card {
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.18) 0%, rgba(20, 20, 20, 0.5) 100%);
        border: 1px solid rgba(37, 99, 235, 0.35);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .action-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 40px rgba(37, 99, 235, 0.2);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255, 255, 255, 0.04);
        border-radius: 16px;
        padding: 6px;
        border: 1px solid rgba(212, 160, 23, 0.3);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        color: var(--muted);
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(212, 160, 23, 0.3) 0%, rgba(212, 160, 23, 0.15) 100%) !important;
        color: var(--accent) !important;
        border: 1px solid rgba(212, 160, 23, 0.4) !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #d4a017 0%, #b8860b 100%) !important;
        color: #000 !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.875rem 1.75rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(212, 160, 23, 0.4) !important;
    }
    
    .stTextInput > div > div, .stTextArea > div > div, .stSelectbox > div > div {
        background: rgba(20, 20, 20, 0.85) !important;
        border: 1px solid rgba(212, 160, 23, 0.35) !important;
        border-radius: 12px !important;
        color: var(--text) !important;
    }
    
    .code-block {
        background: rgba(0, 0, 0, 0.9);
        border: 1px solid rgba(212, 160, 23, 0.35);
        border-radius: 12px;
        padding: 1rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        overflow-x: auto;
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #000 0%, #0c0c0c 100%) !important;
        border-right: 1px solid rgba(212, 160, 23, 0.2);
    }

    /* Yellow hamburger menu button - hide chevron, show hamburger */
    [data-testid="collapsedControl"] svg,
    [data-testid="stSidebarCollapsedControl"] svg,
    [data-testid="baseButton-headerNoPadding"] svg {
        display: none !important;
    }
    [data-testid="collapsedControl"]::before,
    [data-testid="stSidebarCollapsedControl"]::before,
    [data-testid="baseButton-headerNoPadding"]::before {
        content: "☰";
        font-size: 1.5rem;
        color: #f4d03f !important;
        display: block;
    }
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="baseButton-headerNoPadding"] {
        color: #f4d03f !important;
    }
    button[kind="header"], button[kind="headerNoPadding"] {
        color: #f4d03f !important;
    }
</style>
""", unsafe_allow_html=True)

# Video background
if VIDEO_B64:
    st.markdown(f"""
    <div class="video-bg-container">
        <video id="bg-video" autoplay loop playsinline>
            <source src="data:video/mp4;base64,{VIDEO_B64}" type="video/mp4">
        </video>
    </div>
    <div class="video-overlay"></div>
    <button id="sound-toggle" onclick="toggleSound()" style="
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 9999;
        background: rgba(212, 160, 23, 0.9);
        border: none;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        cursor: pointer;
        font-size: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        transition: transform 0.2s;
    ">🔇</button>
    <script>
        const video = document.getElementById('bg-video');
        const btn = document.getElementById('sound-toggle');

        // Try to play with audio
        video.muted = false;
        video.play().catch(() => {{
            // Browser blocked autoplay with sound, start muted
            video.muted = true;
            video.play();
        }});

        function toggleSound() {{
            video.muted = !video.muted;
            btn.textContent = video.muted ? '🔇' : '🔊';
        }}

        // Update button on page load
        setTimeout(() => {{
            btn.textContent = video.muted ? '🔇' : '🔊';
        }}, 500);
    </script>
    """, unsafe_allow_html=True)

# Header with hero logo - full height
logo_html = f'<img src="data:image/png;base64,{HERO_LOGO_B64}" alt="Wild & Wonderful Websites" style="height: 100%; width: auto; border-radius: 8px; object-fit: contain;">' if HERO_LOGO_B64 else ''

st.markdown(f"""
<div class="seobot-header" style="padding: 0; overflow: hidden;">
    <div style="display: flex; justify-content: center; align-items: stretch; height: 220px;">
        <div style="display: flex; align-items: center; padding: 0; margin: 0;">
            {logo_html}
        </div>
        <div style="display: flex; flex-direction: column; justify-content: center; text-align: left; padding-left: 2rem;">
            <div style="font-family: 'Cinzel', serif; font-size: 2.4rem; font-weight: 700; background: linear-gradient(135deg, #d4a017 0%, #f4d03f 50%, #d4a017 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: 4px;">WILD &amp;</div>
            <div style="font-family: 'Cinzel', serif; font-size: 2.4rem; font-weight: 700; background: linear-gradient(135deg, #d4a017 0%, #f4d03f 50%, #d4a017 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: 4px;">WONDERFUL</div>
            <div style="font-family: 'Cinzel', serif; font-size: 2.4rem; font-weight: 700; background: linear-gradient(135deg, #d4a017 0%, #f4d03f 50%, #d4a017 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: 4px;">WEBSITES</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown(f"<div style='color: #f4d03f; font-size: 2.5rem; font-weight: 800; text-align: center;'>{len(SEO_BOOKS)}</div>", unsafe_allow_html=True)
    st.markdown("<div style='color: #64748b; text-align: center; font-size: 0.85rem;'>Sacred Texts</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    for book in SEO_BOOKS:
        st.markdown(f"<div style='color: #f4d03f; font-size: 0.9rem; font-weight: 600;'>{book['title']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='color: #64748b; font-size: 0.75rem;'>{book['author']} • {book['year']}</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### 🎯 Select Project")
    selected_project = st.selectbox(
        "Select project",
        list(PROJECTS.keys()),
        format_func=lambda x: PROJECTS[x]['name'],
        label_visibility="collapsed"
    )
    proj = PROJECTS[selected_project]
    
    st.markdown(f"""
    <div class="law-card" style="margin-top: 1rem;">
        <div style="color: {proj['color']}; font-size: 1.2rem; font-weight: 700;">{proj['name']}</div>
        <div style="color: #94a3b8; font-size: 0.85rem;">{proj['type']}</div>
        <div style="color: #64748b; font-size: 0.8rem; margin-top: 8px;">{proj['description']}</div>
        {'<div style="color: #22c55e; font-size: 0.75rem; margin-top: 8px;">✓ Local files found</div>' if proj.get('path') and Path(proj['path']).exists() else '<div style="color: #ef4444; font-size: 0.75rem; margin-top: 8px;">✖️ No local path</div>'}
    </div>
    """, unsafe_allow_html=True)

# Import Site Scanner (fallback to inline scanner if unavailable)
try:
    from site_scanner import SiteScanner
    SCANNER_AVAILABLE = True
except ImportError:
    SCANNER_AVAILABLE = False
    SiteScanner = None

# Import Lead Capture module
try:
    from lead_capture import (
        SmartFillExtractor, RAGReportGenerator, LeadDatabase,
        SEO_CHALLENGES, create_lead_from_scan, scan_url_with_fallback,
        SELENIUM_AVAILABLE
    )
    LEAD_CAPTURE_AVAILABLE = True
except ImportError:
    LEAD_CAPTURE_AVAILABLE = False
    SELENIUM_AVAILABLE = False

# Main Tabs
grid_tab, audit_tab, knowledge_tab, lead_gen_tab = st.tabs([
    "🌐 Live Preview", "🔍 FREE WEBSITE AUDIT", "📚 Books", "🎯 Get Free SEO Report"
])

# TAB 0: LIVE PREVIEW GRID - All sites at once
with grid_tab:
    st.markdown("""
    <div class="law-card">
        <div class="law-title">🌐 LIVE PREVIEW GRID</div>
        <div class="law-content">
            View all 6 portfolio sites simultaneously. Click any site to open in new tab.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # macOS-style window preview CSS with responsive scaling
    st.markdown("""
    <style>
        .mac-window {
            background: #1e1e1e;
            border-radius: 10px;
            overflow: hidden;
            margin-bottom: 0.5rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        }
        .mac-titlebar {
            background: linear-gradient(180deg, #3c3c3c 0%, #2a2a2a 100%);
            padding: 6px 10px;
            display: flex;
            align-items: center;
            gap: 8px;
            border-bottom: 1px solid #1a1a1a;
        }
        .mac-buttons {
            display: flex;
            gap: 5px;
        }
        .mac-btn {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            border: none;
        }
        .mac-close { background: #ff5f57; }
        .mac-minimize { background: #ffbd2e; }
        .mac-maximize { background: #28ca41; }
        .mac-title {
            flex: 1;
            text-align: center;
            color: #999;
            font-size: 0.7rem;
            font-weight: 500;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .mac-content {
            position: relative;
            overflow: hidden;
            background: #0a0a0a;
        }
        .mac-content iframe {
            width: 200%;
            height: 200%;
            border: 0;
            display: block;
            transform: scale(0.5);
            transform-origin: top left;
        }
        /* Hide scrollbars */
        .mac-content::-webkit-scrollbar { display: none; }
        .mac-content { -ms-overflow-style: none; scrollbar-width: none; }
    </style>
    """, unsafe_allow_html=True)

    def render_preview_card(project, height=320):
        # Determine URL
        if project.get('has_live_url', True):
            url = f"https://{project['domain']}"
            link_text = project['domain']
        else:
            local_port = project.get('local_port')
            if local_port:
                url = f"http://localhost:{local_port}"
                link_text = f"localhost:{local_port}"
            else:
                url = None
                link_text = None

        if url:
            # macOS-style window with scaled iframe for responsiveness
            # iframe is 200% size and scaled to 50% for crisp rendering
            mac_window_html = f"""
            <div class="mac-window">
                <div class="mac-titlebar">
                    <div class="mac-buttons">
                        <div class="mac-btn mac-close"></div>
                        <div class="mac-btn mac-minimize"></div>
                        <div class="mac-btn mac-maximize"></div>
                    </div>
                    <div class="mac-title">{project['name']}</div>
                </div>
                <div class="mac-content" style="height: {height}px;">
                    <iframe
                        src="{url}"
                        title="{project['name']} preview"
                        style="width: 200%; height: {height * 2}px;"
                        loading="lazy"
                        scrolling="no"
                    ></iframe>
                </div>
            </div>
            <a href="{url}" target="_blank" style="display: block; text-align: center; color: #666; font-size: 0.65rem; padding: 2px; text-decoration: none;">{link_text} ↗</a>
            """
            st.markdown(mac_window_html, unsafe_allow_html=True)
        else:
            # Show macOS-style card for local-only projects without server
            local_path = Path(project.get('path', ''))
            index_exists = (local_path / "index.html").exists()

            mac_placeholder_html = f"""
            <div class="mac-window">
                <div class="mac-titlebar">
                    <div class="mac-buttons">
                        <div class="mac-btn mac-close"></div>
                        <div class="mac-btn mac-minimize"></div>
                        <div class="mac-btn mac-maximize"></div>
                    </div>
                    <div class="mac-title">{project['name']}</div>
                </div>
                <div class="mac-content" style="height: {height}px; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); display: flex; flex-direction: column; justify-content: center; align-items: center;">
                    <div style="color: {project['color']}; font-size: 2rem; margin-bottom: 0.5rem;">📁</div>
                    <div style="color: #f4d03f; font-size: 0.9rem; font-weight: 700;">{project['name']}</div>
                    <div style="color: {'#22c55e' if index_exists else '#ef4444'}; font-size: 0.6rem; margin-top: 0.25rem;">{'✓ Local files' if index_exists else '✖️ No server'}</div>
                </div>
            </div>
            """
            st.markdown(mac_placeholder_html, unsafe_allow_html=True)

    project_list = list(PROJECTS.items())
    columns_per_row = 3

    for row_start in range(0, len(project_list), columns_per_row):
        row_items = project_list[row_start:row_start + columns_per_row]
        row_cols = st.columns(columns_per_row)
        for col_index in range(columns_per_row):
            if col_index >= len(row_items):
                continue
            _, project = row_items[col_index]
            with row_cols[col_index]:
                render_preview_card(project)

    st.markdown("---")

    # Quick SEO Audit summary
    st.markdown("### Quick SEO Audit")
    st.markdown("""
    <div style="background: rgba(30, 58, 95, 0.4); border: 1px solid rgba(212, 160, 23, 0.2); border-radius: 12px; padding: 1rem; margin-bottom: 0.75rem;">
        <div style="color: #f4d03f; font-weight: 700; margin-bottom: 0.5rem;">Optimize Page Speed</div>
        <div style="color: #cbd5e1; font-size: 0.9rem;">Compress WebGL assets, enable browser caching, and use lazy loading to ensure load time under 3 seconds.</div>
    </div>
    <div style="background: rgba(30, 58, 95, 0.4); border: 1px solid rgba(212, 160, 23, 0.2); border-radius: 12px; padding: 1rem; margin-bottom: 0.75rem;">
        <div style="color: #f4d03f; font-weight: 700; margin-bottom: 0.5rem;">Implement Proper Meta Tags</div>
        <div style="color: #cbd5e1; font-size: 0.9rem;">Create unique, keyword-rich titles (50-60 chars) and descriptions (150-160 chars) with clear CTAs for all pages.</div>
    </div>
    <div style="background: rgba(30, 58, 95, 0.4); border: 1px solid rgba(212, 160, 23, 0.2); border-radius: 12px; padding: 1rem; margin-bottom: 0.75rem;">
        <div style="color: #f4d03f; font-weight: 700; margin-bottom: 0.5rem;">Add Schema Markup</div>
        <div style="color: #cbd5e1; font-size: 0.9rem;">Use Organization/Article schema for portfolio pages, including logo, author, datePublished, and image metadata.</div>
    </div>
    <div style="background: rgba(30, 58, 95, 0.4); border: 1px solid rgba(212, 160, 23, 0.2); border-radius: 12px; padding: 1rem; margin-bottom: 0.75rem;">
        <div style="color: #f4d03f; font-weight: 700; margin-bottom: 0.5rem;">Ensure Mobile-First Responsiveness</div>
        <div style="color: #cbd5e1; font-size: 0.9rem;">Validate mobile usability via Google's Mobile-Friendly Test and optimize WebGL performance for smaller screens.</div>
    </div>
    <div style="background: rgba(30, 58, 95, 0.4); border: 1px solid rgba(212, 160, 23, 0.2); border-radius: 12px; padding: 1rem; margin-bottom: 0.75rem;">
        <div style="color: #f4d03f; font-weight: 700; margin-bottom: 0.5rem;">Improve Image Alt Text & Clean URLs</div>
        <div style="color: #cbd5e1; font-size: 0.9rem;">Add descriptive alt text to all images and use clean, semantic URLs (e.g., /project-name instead of ?p=123).</div>
    </div>
    """, unsafe_allow_html=True)

    st.info("👆 Use the tabs above to implement these fixes with the Code Rewriter, WebGL Optimizer, Meta Generator, and Schema Builder tools.")

# TAB: FREE WEBSITE AUDIT - All tools combined
with audit_tab:
    st.markdown(f"""
    <div class="law-card">
        <div class="law-title">🔍 FREE WEBSITE AUDIT</div>
        <div class="law-content">
            Complete SEO toolkit powered by 5 books ({RULE_COUNT} extracted rules). Audit your site, generate meta tags, schema markup, and performance optimizations.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Section selector
    audit_section = st.radio(
        "Select Tool",
        ["⚙️ SEO Audit", "🏷️ Meta Generator", "✨ Schema Builder", "🎮 WebGL Optimizer", "✏️ Code Rewriter"],
        horizontal=True,
        label_visibility="collapsed"
    )

    st.markdown("---")

    # ═══════════════════════════════════════════════════════════════════════════════
    # SECTION: SEO AUDIT
    # ═══════════════════════════════════════════════════════════════════════════════
    if audit_section == "⚙️ SEO Audit":
        # Determine URL based on project
        if proj.get('local_port'):
            default_url = f"http://localhost:{proj['local_port']}"
        else:
            default_url = f"https://{proj['domain']}"

        audit_url = st.text_input("Website URL to Audit", default_url, key="audit_url_input")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            check_meta = st.checkbox("Meta Tags", value=True)
        with col2:
            check_speed = st.checkbox("Page Speed", value=True)
        with col3:
            check_schema = st.checkbox("Schema", value=True)
        with col4:
            check_mobile = st.checkbox("Mobile", value=True)

        if st.button("🔍 Run Full Audit", key="run_audit_btn"):
            with st.spinner(f"Fetching page and auditing against {RULE_COUNT} SEO rules..."):
                try:
                    # Fetch the page HTML
                    response = requests.get(audit_url, timeout=10, headers={'User-Agent': 'SEOBOT/1.0'})
                    html_content = response.text

                    # Run SEO Engine analysis
                    if SEO_ENGINE_AVAILABLE:
                        engine = get_engine()
                        analysis = engine.analyze_html(html_content, audit_url)

                        # Display score
                        score = analysis['overall_score']
                        score_color = "#22c55e" if score >= 80 else "#f59e0b" if score >= 60 else "#ef4444"

                        st.markdown(f"""
                        <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, rgba(30, 58, 95, 0.6) 0%, rgba(15, 29, 50, 0.8) 100%); border-radius: 16px; border: 2px solid {score_color}; margin-bottom: 1rem;">
                            <div style="font-size: 3rem; font-weight: 800; color: {score_color};">{score}</div>
                            <div style="color: #94a3b8; font-size: 0.9rem;">SEO Score (out of 100)</div>
                        </div>
                        """, unsafe_allow_html=True)

                        # Category scores
                        col1, col2, col3, col4 = st.columns(4)
                        for i, (cat, cat_score) in enumerate(analysis['scores'].items()):
                            with [col1, col2, col3, col4][i % 4]:
                                st.metric(cat.replace('_', ' ').title(), f"{cat_score}%")

                        # Issues summary
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Total Issues", len(analysis['issues']))
                        col2.metric("Critical", analysis['critical'], delta=None if analysis['critical'] == 0 else f"-{analysis['critical']}")
                        col3.metric("Warnings", analysis['warning'])

                        st.markdown("---")
                        st.markdown("### 📋 Detailed Findings")

                        # Group issues by category
                        issues_by_cat = {}
                        for issue in analysis['issues']:
                            cat = issue.category
                            if cat not in issues_by_cat:
                                issues_by_cat[cat] = []
                            issues_by_cat[cat].append(issue)

                        for category, issues in issues_by_cat.items():
                            critical_count = len([i for i in issues if i.severity == "critical"])
                            icon = "🔴" if critical_count > 0 else "🟡"
                            with st.expander(f"{icon} {category} - {len(issues)} issues"):
                                for issue in issues:
                                    sev_color = "#ef4444" if issue.severity == "critical" else "#f59e0b"
                                    st.markdown(f"""
                                    <div style="background: rgba(15, 29, 50, 0.6); padding: 0.75rem; border-radius: 8px; margin-bottom: 0.5rem; border-left: 3px solid {sev_color};">
                                        <div style="color: {sev_color}; font-weight: 700; font-size: 0.9rem;">{issue.title}</div>
                                        <div style="color: #94a3b8; font-size: 0.8rem; margin: 0.25rem 0;">{issue.description}</div>
                                        <div style="color: #86efac; font-size: 0.8rem;">✓ Fix: {issue.fix}</div>
                                        <div style="color: #64748b; font-size: 0.7rem; font-style: italic; margin-top: 0.25rem;">📚 {issue.law_reference}</div>
                                    </div>
                                    """, unsafe_allow_html=True)

                                # Generate fix code button
                                if st.button(f"Generate Fix Code for {category}", key=f"fix_{category}"):
                                    st.markdown("**Generated Fix Code:**")
                                    for issue in issues:
                                        fix_code = engine.gen_fix(issue, proj)
                                        st.code(fix_code, language="html")

                        # Store analysis in session for code rewriter
                        st.session_state['last_audit'] = analysis
                        st.session_state['last_audit_html'] = html_content

                    else:
                        st.error("SEO Engine not available. Check seo_engine.py")

                except requests.exceptions.RequestException as e:
                    st.error(f"Could not fetch URL: {e}")
                except Exception as e:
                    st.error(f"Audit error: {e}")

    # ═══════════════════════════════════════════════════════════════════════════════
    # SECTION: META GENERATOR
    # ═══════════════════════════════════════════════════════════════════════════════
    elif audit_section == "🏷️ Meta Generator":
        col1, col2 = st.columns(2)
        with col1:
            meta_title = st.text_input("Page Title", f"{proj['name']} - Professional {proj['type']} Services | WV", key="meta_title")
            meta_desc = st.text_area("Meta Description", f"Professional {proj['type']} services in West Virginia. {proj['description']} Contact us today for a free consultation!", height=100, key="meta_desc")
        with col2:
            meta_url = st.text_input("Page URL", f"https://{proj['domain']}", key="meta_url")
            meta_keywords = st.text_input("Keywords (comma separated)", ", ".join(proj['keywords']), key="meta_keywords")

        # Headline suggestions (small local model)
        if HEADLINE_HELPER:
            st.markdown("#### Headline Suggestions (5-book tuned)")
            hl_topic = st.text_input("What's the page about?", proj["description"], key="headline_topic")
            if st.button("Suggest Headlines", key="btn_suggest_headlines"):
                headlines = suggest_headlines(hl_topic, n=5)
                choice = st.radio("Pick a headline to apply", headlines, index=0, key="headline_pick")
                if st.button("Use Selected Headline", key="btn_use_headline"):
                    st.session_state.meta_title = choice
                    meta_title = choice

        # Real-time validation
        title_len = len(meta_title)
        desc_len = len(meta_desc)

        col1, col2 = st.columns(2)
        with col1:
            if 50 <= title_len <= 60:
                st.success(f"✔️ Title: {title_len}/60 characters")
            else:
                st.error(f"⚠️ Title: {title_len}/60 characters - {'Too short!' if title_len < 50 else 'Too long!'}")
        with col2:
            if 150 <= desc_len <= 160:
                st.success(f"✔️ Description: {desc_len}/160 characters")
            else:
                st.error(f"⚠️ Description: {desc_len}/160 characters - {'Too short!' if desc_len < 150 else 'Too long!'}")

        if st.button("Generate Complete Meta Tags"):
            meta_code = f"""<!-- SEO LAW COMPLIANT META TAGS -->
<!-- Following: AI For SEO Essentials, SEO Marketing Secrets, SEO Practice -->

<title>{meta_title}</title>
<meta name="title" content="{meta_title}">
<meta name="description" content="{meta_desc}">
<meta name="keywords" content="{meta_keywords}">
<meta name="robots" content="index, follow">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta charset="UTF-8">
<link rel="canonical" href="{meta_url}">

<!-- Open Graph / Facebook -->
<meta property="og:type" content="website">
<meta property="og:url" content="{meta_url}">
<meta property="og:title" content="{meta_title}">
<meta property="og:description" content="{meta_desc}">
<meta property="og:image" content="{meta_url}/og-image.jpg">
<meta property="og:site_name" content="{proj['name']}">

<!-- Twitter -->
<meta property="twitter:card" content="summary_large_image">
<meta property="twitter:url" content="{meta_url}">
<meta property="twitter:title" content="{meta_title}">
<meta property="twitter:description" content="{meta_desc}">
<meta property="twitter:image" content="{meta_url}/twitter-image.jpg">

<!-- Compliance Check -->
<!-- Title: {title_len}/60 chars {'✔️' if 50 <= title_len <= 60 else '✖'} -->
<!-- Description: {desc_len}/160 chars {'✔️' if 150 <= desc_len <= 160 else '✖'} -->"""

            st.code(meta_code, language="html")

            # Google Preview
            st.markdown("### Google Search Preview")
            st.markdown(f"""
            <div style="background: white; padding: 20px; border-radius: 12px; max-width: 650px; font-family: Arial, sans-serif; margin-top: 1rem;">
                <div style="color: #202124; font-size: 14px;">{meta_url}</div>
                <div style="color: #1a0dab; font-size: 20px; padding: 4px 0;">{meta_title[:60]}{'...' if len(meta_title) > 60 else ''}</div>
                <div style="color: #4d5156; font-size: 14px;">{meta_desc[:160]}{'...' if len(meta_desc) > 160 else ''}</div>
            </div>
            """, unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════════════════════
    # SECTION: SCHEMA BUILDER
    # ═══════════════════════════════════════════════════════════════════════════════
    elif audit_section == "✨ Schema Builder":
        schema_type = st.selectbox("Schema Type",
            ["Organization", "Person", "LocalBusiness", "WebSite", "Article", "Product"],
            index=["Organization", "Person", "LocalBusiness", "WebSite", "Article", "Product"].index(proj['schema_type'])
        )

        col1, col2 = st.columns(2)
        with col1:
            schema_name = st.text_input("Name", proj['name'])
            schema_url = st.text_input("Website URL", f"https://{proj['domain']}")
            schema_logo = st.text_input("Logo URL", f"https://{proj['domain']}/logo.png")
        with col2:
            schema_desc = st.text_area("Description", proj['description'], height=100)
            if schema_type in ['Person', 'Organization']:
                schema_social = st.text_area("Social Profile URLs (one per line)",
                    "https://twitter.com/adaryus\nhttps://linkedin.com/in/adaryus", height=80)

        if st.button("Generate Schema Markup"):
            schema = {
                "@context": "https://schema.org",
                "@type": schema_type,
                "name": schema_name,
                "url": schema_url,
                "description": schema_desc
            }

            if schema_type == "Organization":
                schema["@id"] = f"{schema_url}#organization"
                schema["logo"] = schema_logo
                schema["sameAs"] = [url.strip() for url in schema_social.split('\n') if url.strip()]
                schema["contactPoint"] = {
                    "@type": "ContactPoint",
                    "contactType": "customer service",
                    "availableLanguage": ["English"]
                }

            elif schema_type == "Person":
                schema["@id"] = f"{schema_url}#person"
                schema["jobTitle"] = "Web Designer & Developer"
                schema["sameAs"] = [url.strip() for url in schema_social.split('\n') if url.strip()]
                schema["worksFor"] = {"@type": "Organization", "name": schema_name}

            elif schema_type == "LocalBusiness":
                schema["@id"] = f"{schema_url}#business"
                schema["image"] = schema_logo
                schema["address"] = {
                    "@type": "PostalAddress",
                    "addressRegion": "WV",
                    "addressCountry": "US"
                }
                schema["geo"] = {"@type": "GeoCoordinates", "latitude": "", "longitude": ""}
                schema["openingHours"] = ["Mo-Fr 09:00-17:00"]
                schema["priceRange"] = "$$"

            elif schema_type == "WebSite":
                schema["@id"] = f"{schema_url}#website"
                schema["publisher"] = {"@type": "Organization", "name": schema_name, "url": schema_url}
                schema["potentialAction"] = {
                    "@type": "SearchAction",
                    "target": {"@type": "EntryPoint", "urlTemplate": f"{schema_url}/search?q={{search_term_string}}"},
                    "query-input": "required name=search_term_string"
                }

            elif schema_type == "Article":
                schema["author"] = {"@type": "Person", "name": "Adaryus"}
                schema["datePublished"] = datetime.now().isoformat()
                schema["dateModified"] = datetime.now().isoformat()
                schema["image"] = schema_logo

            schema_json = json.dumps(schema, indent=2)

            st.code(f'<script type="application/ld+json">\n{schema_json}\n</script>', language="html")

            st.markdown("""
            <div class="compliance-box">
                <div style="color: #86efac; font-weight: 700;">✔️ Schema follows SEO Law requirements</div>
                <div style="color: #86efac; font-size: 0.85rem; margin-top: 8px;">
                    Include this in your &lt;head&gt; section before any CSS/JS
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════════════════════
    # SECTION: WEBGL OPTIMIZER
    # ═══════════════════════════════════════════════════════════════════════════════
    elif audit_section == "🎮 WebGL Optimizer":
        st.markdown("### Optimization Code Generator")

        opt_type = st.selectbox("Optimization Type", [
            "WebGL Lazy Loader (Intersection Observer)",
            "Texture Compression Utility",
            "Service Worker for Caching",
            "Performance CSS",
            "Complete .htaccess Config"
        ])

        if opt_type == "WebGL Lazy Loader (Intersection Observer)":
            code = """// WebGL Lazy Loader - Load only when visible
class WebGLLazyLoader {
    constructor(canvasId, initFunction) {
        this.canvas = document.getElementById(canvasId);
        this.initFunction = initFunction;
        this.observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !this.loaded) {
                    this.loaded = true;
                    this.initFunction(this.canvas);
                    console.log('WebGL initialized on viewport entry');
                }
            });
        }, { threshold: 0.1 });

        this.observer.observe(this.canvas);
    }
}

// Usage:
// const loader = new WebGLLazyLoader('webgl-canvas', (canvas) => {
//     // Your Three.js init code here
// });"""

        elif opt_type == "Texture Compression Utility":
            code = """// Texture Compression - Resize before GPU upload
async function compressTexture(image, maxSize = 2048) {
    return new Promise((resolve) => {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');

        let { width, height } = image;

        // Resize if too large
        if (width > maxSize || height > maxSize) {
            const ratio = Math.min(maxSize / width, maxSize / height);
            width *= ratio;
            height *= ratio;
        }

        canvas.width = width;
        canvas.height = height;
        ctx.drawImage(image, 0, 0, width, height);

        // Convert to WebP if supported (smaller size)
        canvas.toBlob((blob) => {
            resolve(blob);
        }, 'image/webp', 0.85);
    });
}

// Usage in Three.js:
// const texture = new THREE.TextureLoader().load(url);
// texture.minFilter = THREE.LinearFilter; // Better performance"""

        elif opt_type == "Service Worker for Caching":
            code = """// service-worker.js - Browser Caching
const CACHE_NAME = 'site-cache-v1';
const STATIC_ASSETS = [
    '/',
    '/index.html',
    '/styles.css',
    '/main.js',
    '/og-image.jpg'
];

// Install: Cache static assets
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(STATIC_ASSETS))
            .then(() => self.skipWaiting())
    );
});

// Fetch: Serve from cache or network
self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                // Return cached or fetch new
                if (response) {
                    return response;
                }
                return fetch(event.request).then(response => {
                    // Cache new requests
                    if (response.status === 200) {
                        const clone = response.clone();
                        caches.open(CACHE_NAME).then(cache => {
                            cache.put(event.request, clone);
                        });
                    }
                    return response;
                });
            })
    );
});

// Register in your main JS:
// if ('serviceWorker' in navigator) {
//     navigator.serviceWorker.register('/service-worker.js');
// }"""

        elif opt_type == "Performance CSS":
            code = """/* Performance Optimizations CSS */

/* GPU acceleration for WebGL canvas */
canvas.webgl {
    will-change: transform;
    transform: translateZ(0);
    contain: layout style paint;
}

/* Lazy loading fade-in */
img[loading="lazy"] {
    opacity: 0;
    transition: opacity 0.3s ease;
}
img[loading="lazy"].loaded {
    opacity: 1;
}

/* Reduce motion for accessibility */
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        transition-duration: 0.01ms !important;
    }
}

/* Mobile WebGL optimization */
@media (pointer: coarse) {
    canvas.webgl {
        image-rendering: optimizeSpeed;
    }
}"""

        else:  # .htaccess
            code = """# .htaccess - Browser Caching & Compression
# Place this in your web root

# Enable compression
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/plain text/html text/xml text/css
    AddOutputFilterByType DEFLATE application/xml application/xhtml+xml
    AddOutputFilterByType DEFLATE application/rss+xml application/javascript
    AddOutputFilterByType DEFLATE application/x-javascript
</IfModule>

# Browser caching
<IfModule mod_expires.c>
    ExpiresActive On

    # Images
    ExpiresByType image/jpeg "access plus 1 year"
    ExpiresByType image/gif "access plus 1 year"
    ExpiresByType image/png "access plus 1 year"
    ExpiresByType image/webp "access plus 1 year"
    ExpiresByType image/svg+xml "access plus 1 year"

    # CSS & JS
    ExpiresByType text/css "access plus 1 month"
    ExpiresByType application/javascript "access plus 1 month"

    # Fonts
    ExpiresByType font/woff2 "access plus 1 year"

    # Default
    ExpiresDefault "access plus 2 days"
</IfModule>

# Security headers
<IfModule mod_headers.c>
    Header set X-Content-Type-Options "nosniff"
    Header set X-Frame-Options "SAMEORIGIN"
    Header set X-XSS-Protection "1; mode=block"
</IfModule>"""

        st.code(code, language="javascript" if "JavaScript" in opt_type or "Loader" in opt_type or "Worker" in opt_type else "css" if "CSS" in opt_type else "apache")

        st.download_button(
            label=f"Download {opt_type.split('(')[0].strip()}",
            data=code,
            file_name=f"{'webgl-optimizer.js' if 'Loader' in opt_type else 'texture-compress.js' if 'Texture' in opt_type else 'service-worker.js' if 'Worker' in opt_type else 'performance.css' if 'CSS' in opt_type else '.htaccess'}",
            mime="text/plain"
        )

    # ═══════════════════════════════════════════════════════════════════════════════
    # SECTION: CODE REWRITER
    # ═══════════════════════════════════════════════════════════════════════════════
    elif audit_section == "✏️ Code Rewriter":
        if proj.get('path') and Path(proj['path']).exists():
            st.success(f"Project files found at: {proj['path']}")

            col1, col2 = st.columns(2)
            with col1:
                fix_meta = st.checkbox("Fix Meta Tags", value=True, help="Titles 50-60 chars, descriptions 150-160 chars")
                fix_schema = st.checkbox("Add Schema Markup", value=True, help="JSON-LD structured data")
                fix_og = st.checkbox("Add Open Graph", value=True, help="Facebook/LinkedIn sharing")
            with col2:
                fix_twitter = st.checkbox("Add Twitter Cards", value=True, help="Twitter sharing cards")
                fix_alt = st.checkbox("Fix Image Alt Text", value=True, help="Descriptive alt text for accessibility")
                fix_canonical = st.checkbox("Add Canonical URLs", value=True, help="Prevent duplicate content")

            if st.button("Rewrite All Files", type="primary"):
                with st.spinner("Creating backup and rewriting files..."):
                    try:
                        from code_rewriter import SEOCodeRewriter

                        rewriter = SEOCodeRewriter(proj['path'])
                        backup_path = rewriter.create_backup()

                        st.info(f"Backup created at: {backup_path}")

                        # Scan and rewrite
                        results = rewriter.scan_and_rewrite_project(proj)

                        st.success("Rewrite complete!")

                        # Show results
                        for result in results[:5]:  # Show first 5
                            if result['success']:
                                with st.expander(f"✓ {Path(result['file']).name}"):
                                    for change in result['changes']:
                                        st.markdown(f"<div style='color: #86efac; font-size: 0.85rem;'>• {change}</div>", unsafe_allow_html=True)
                            elif result['error']:
                                st.error(f"✖️ {result['file']}: {result['error']}")

                        if len(results) > 5:
                            st.markdown(f"<div style='color: #64748b; text-align: center;'>... and {len(results) - 5} more files</div>", unsafe_allow_html=True)

                    except Exception as e:
                        st.error(f"Error: {e}")
                        st.info("Make sure code_rewriter.py is in the same directory")
        else:
            st.error("No local project files found")
            st.info("This project doesn't have a local path configured. Switch to a project with local files (Adaryus or NCRJ Watch).")

            # Show manual code generation instead
            st.markdown("### Manual Code Generation")
            st.markdown("Generate SEO-compliant code snippets to manually add to your site:")

            page_name = st.text_input("Page Name", "home")
            page_title = st.text_input("Page Title", f"{proj['name']} - Professional {proj['type']} Services")
            page_desc = st.text_area("Page Description", f"Professional {proj['type']} services. {proj['description']}", height=80)

            if st.button("Generate Complete Head Section"):
                # Validate lengths
                title_ok = 50 <= len(page_title) <= 60
                desc_ok = 150 <= len(page_desc) <= 160

                if not title_ok:
                    st.warning(f"Title is {len(page_title)} chars. Should be 50-60.")
                if not desc_ok:
                    st.warning(f"Description is {len(page_desc)} chars. Should be 150-160.")

                code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <!-- Primary Meta Tags -->
    <title>{page_title}</title>
    <meta name="title" content="{page_title}">
    <meta name="description" content="{page_desc}">
    <meta name="robots" content="index, follow">
    <link rel="canonical" href="https://{proj['domain']}/{page_name}">

    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://{proj['domain']}/{page_name}">
    <meta property="og:title" content="{page_title}">
    <meta property="og:description" content="{page_desc}">
    <meta property="og:image" content="https://{proj['domain']}/og-image.jpg">

    <!-- Twitter -->
    <meta property="twitter:card" content="summary_large_image">
    <meta property="twitter:url" content="https://{proj['domain']}/{page_name}">
    <meta property="twitter:title" content="{page_title}">
    <meta property="twitter:description" content="{page_desc}">
    <meta property="twitter:image" content="https://{proj['domain']}/twitter-image.jpg">

    <!-- Schema.org -->
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "{proj['schema_type']}",
        "name": "{proj['name']}",
        "url": "https://{proj['domain']}",
        "description": "{proj['description']}"
    }}
    </script>
</head>"""

                st.code(code, language="html")

# TAB 6: BOOK KNOWLEDGE
with knowledge_tab:
    st.markdown("""
    <div class="law-card">
        <div class="law-title">📚 Book Knowledge</div>
        <div class="law-content">
            Full texts of all 5 EPUBs (now bibles for the sites). Search any phrase and reuse passages directly.
        </div>
    </div>
    """, unsafe_allow_html=True)

    rules_json = load_rules_json()

    if not BOOK_TEXTS:
        st.error("No TXT files found in seo_training_data. Run the EPUB conversion first (epub_converter.py).")
    else:
        total_chars = sum(b["chars"] for b in BOOK_TEXTS)
        total_words = sum(b["words"] for b in BOOK_TEXTS)
        c1, c2, c3 = st.columns(3)
        c1.metric("Books", len(BOOK_TEXTS))
        c2.metric("Total chars", f"{total_chars:,}")
        c3.metric("Total words", f"{total_words:,}")

        if rules_json:
            st.markdown("#### Rule Corpus (JSON)")
            cat_cols = st.columns(3)
            categories = list(rules_json.get("categories", {}).items())
            for idx, (cat, items) in enumerate(categories):
                col = cat_cols[idx % 3]
                col.metric(cat.replace("_", " ").title(), len(items))
            st.download_button("📥 Download rules JSON", data=json.dumps(rules_json, ensure_ascii=False, indent=2), file_name="seo_rules_extracted.json")

        query = st.text_input("Search across ALL books (full text)", "")
        limit = st.slider("Results to show", 1, 15, 6)

        # Book chooser for full reading/download
        with st.expander("Open a full book", expanded=False):
            book_names = [b["name"] for b in BOOK_TEXTS]
            sel = st.selectbox("Select book", book_names, label_visibility="collapsed")
            chosen = next(b for b in BOOK_TEXTS if b["name"] == sel)
            st.download_button(f"📥 Download {sel}.txt", data=chosen["full"], file_name=f"{sel}.txt")
            st.text_area("Full text (read-only)", chosen["full"], height=240)

        if query.strip():
            q = query.lower()
            hits = []
            for book in BOOK_TEXTS:
                # find all occurrences
                pos = book["full"].lower().find(q)
                while pos != -1 and len(hits) < limit:
                    window_chars = 480
                    start = max(0, pos - 140)
                    end = min(len(book["full"]), pos + window_chars)
                    excerpt = book["full"][start:end]
                    hits.append((book, excerpt))
                    pos = book["full"].lower().find(q, pos + 1)

            if not hits:
                st.info("No matches found across the full texts.")
            else:
                st.markdown("### Matches")
                for book, excerpt in hits[:limit]:
                    st.markdown(f"**{book['name']}** ({book['words']:,} words)")
                    st.code(excerpt.strip() + " ...", language="text")
        else:
            st.markdown("### Quick excerpts (first 1,200 chars per book)")
            for book in BOOK_TEXTS[:limit]:
                st.markdown(f"**{book['name']}** ({book['words']:,} words)")
                st.code(book["full"][:1200].strip() + " ...", language="text")

# TAB 7: LEAD GENERATION - Get Free SEO Report
with lead_gen_tab:
    st.markdown("""
    <div class="law-card">
        <div class="law-title">🎯 Get Your Free SEO Report</div>
        <div class="law-content">
            Enter your website URL to get a comprehensive SEO audit powered by AI and our 5-book knowledge base ({} rules).
        </div>
    </div>
    """.format(RULE_COUNT), unsafe_allow_html=True)

    if not LEAD_CAPTURE_AVAILABLE:
        st.error("Lead capture module not available. Check lead_capture.py")
    else:
        # Initialize session state for wizard
        if 'lead_step' not in st.session_state:
            st.session_state.lead_step = 1
        if 'lead_data' not in st.session_state:
            st.session_state.lead_data = {}
        if 'lead_audit' not in st.session_state:
            st.session_state.lead_audit = None
        if 'lead_html' not in st.session_state:
            st.session_state.lead_html = ""
        if 'lead_extracted' not in st.session_state:
            st.session_state.lead_extracted = {}

        # Progress indicator
        steps = ["URL Input", "Preview", "Smart Fill", "Contact Info", "Full Report"]
        step_cols = st.columns(5)
        for i, (col, step_name) in enumerate(zip(step_cols, steps), 1):
            with col:
                if i < st.session_state.lead_step:
                    st.markdown(f"<div style='text-align: center; color: #22c55e;'>✓ {step_name}</div>", unsafe_allow_html=True)
                elif i == st.session_state.lead_step:
                    st.markdown(f"<div style='text-align: center; color: #f4d03f; font-weight: bold;'>● {step_name}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='text-align: center; color: #64748b;'>○ {step_name}</div>", unsafe_allow_html=True)

        st.markdown("---")

        # ═══════════════════════════════════════════════════════════════════
        # STEP 1: URL INPUT
        # ═══════════════════════════════════════════════════════════════════
        if st.session_state.lead_step == 1:
            st.markdown("### Step 1: Enter Your Website URL")

            # Show scanning method indicator
            if SELENIUM_AVAILABLE:
                st.markdown("""
                <div style="background: rgba(34, 197, 94, 0.1); padding: 0.5rem 1rem; border-radius: 8px; border-left: 3px solid #22c55e; margin-bottom: 1rem;">
                    <span style="color: #22c55e;">✓ Selenium Browser</span>
                    <span style="color: #94a3b8; font-size: 0.85rem;"> - Full JavaScript rendering enabled</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background: rgba(245, 158, 11, 0.1); padding: 0.5rem 1rem; border-radius: 8px; border-left: 3px solid #f59e0b; margin-bottom: 1rem;">
                    <span style="color: #f59e0b;">⚠ Basic Mode</span>
                    <span style="color: #94a3b8; font-size: 0.85rem;"> - Some dynamic sites may not scan fully</span>
                </div>
                """, unsafe_allow_html=True)

            lead_url = st.text_input(
                "Website URL",
                placeholder="https://yourbusiness.com",
                key="lead_url_input",
                help="Enter your full website URL including https://"
            )

            col1, col2 = st.columns([3, 1])
            with col2:
                scan_btn = st.button("🔍 Scan Website", type="primary", use_container_width=True)

            if scan_btn and lead_url:
                # Validate URL
                if not lead_url.startswith(("http://", "https://")):
                    lead_url = "https://" + lead_url

                # Show progress
                progress_text = st.empty()
                progress_bar = st.progress(0)

                try:
                    progress_text.text("🚀 Launching browser...")
                    progress_bar.progress(10)

                    # Use Selenium scanner with fallback
                    progress_text.text("🌐 Loading page with JavaScript rendering...")
                    progress_bar.progress(30)

                    html, page_data = scan_url_with_fallback(lead_url, use_selenium=SELENIUM_AVAILABLE)

                    if not html:
                        st.error(f"Could not fetch URL: {page_data.get('status', 'Unknown error')}")
                    else:
                        progress_text.text("🔍 Analyzing SEO...")
                        progress_bar.progress(60)

                        st.session_state.lead_html = html

                        # Run SEO analysis
                        if SEO_ENGINE_AVAILABLE:
                            engine = get_engine()
                            audit = engine.analyze_html(html, lead_url)
                            st.session_state.lead_audit = audit

                            progress_text.text("📊 Extracting business info...")
                            progress_bar.progress(80)

                            # Extract business info using page_data from Selenium
                            extractor = SmartFillExtractor()
                            extracted = extractor.extract_business_info(page_data, html)

                            st.session_state.lead_extracted = extracted
                            st.session_state.lead_data["url"] = lead_url
                            st.session_state.lead_data["page_data"] = page_data
                            st.session_state.lead_data["scan_method"] = page_data.get("scan_method", "unknown")

                            progress_text.text("✅ Scan complete!")
                            progress_bar.progress(100)

                            # Show scan method used
                            scan_method = page_data.get("scan_method", "unknown")
                            if scan_method == "selenium":
                                st.success(f"✓ Scanned with Selenium (full JS rendering) in {page_data.get('load_time', '?')}s")
                            else:
                                st.info(f"Scanned with {scan_method}")

                            # Move to next step
                            st.session_state.lead_step = 2
                            st.rerun()
                        else:
                            st.error("SEO Engine not available")

                except Exception as e:
                    st.error(f"Error scanning: {e}")
                    import traceback
                    st.code(traceback.format_exc())

        # ═══════════════════════════════════════════════════════════════════
        # STEP 2: PREVIEW (Teaser)
        # ═══════════════════════════════════════════════════════════════════
        elif st.session_state.lead_step == 2:
            st.markdown("### Step 2: Your SEO Score Preview")

            audit = st.session_state.lead_audit
            if audit:
                score = audit['overall_score']
                score_color = "#22c55e" if score >= 80 else "#f59e0b" if score >= 60 else "#ef4444"

                # Large score display
                st.markdown(f"""
                <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, rgba(30, 58, 95, 0.6) 0%, rgba(15, 29, 50, 0.8) 100%); border-radius: 20px; border: 3px solid {score_color}; margin-bottom: 1.5rem;">
                    <div style="font-size: 5rem; font-weight: 800; color: {score_color}; line-height: 1;">{score}</div>
                    <div style="color: #94a3b8; font-size: 1.1rem; margin-top: 0.5rem;">SEO Score (out of 100)</div>
                    <div style="color: #64748b; font-size: 0.9rem; margin-top: 0.25rem;">{st.session_state.lead_data.get('url', '')}</div>
                </div>
                """, unsafe_allow_html=True)

                # Top 3 critical issues (teaser)
                st.markdown("#### Top Issues Found")
                critical_issues = [i for i in audit['issues'] if i.severity == "critical"][:3]
                if not critical_issues:
                    critical_issues = audit['issues'][:3]

                for i, issue in enumerate(critical_issues, 1):
                    sev_color = "#ef4444" if issue.severity == "critical" else "#f59e0b"
                    st.markdown(f"""
                    <div style="background: rgba(15, 29, 50, 0.6); padding: 1rem; border-radius: 12px; margin-bottom: 0.75rem; border-left: 4px solid {sev_color};">
                        <div style="color: {sev_color}; font-weight: 700;">{i}. {issue.title}</div>
                        <div style="color: #94a3b8; font-size: 0.9rem; margin-top: 0.25rem;">{issue.description}</div>
                        <div style="color: #64748b; font-size: 0.8rem; font-style: italic; margin-top: 0.25rem;">📚 {issue.law_reference}</div>
                    </div>
                    """, unsafe_allow_html=True)

                # Blurred teaser of more content
                if len(audit['issues']) > 3:
                    st.markdown(f"""
                    <div style="position: relative; margin: 1.5rem 0;">
                        <div style="background: rgba(20, 20, 20, 0.9); padding: 1.5rem; border-radius: 12px; filter: blur(4px); opacity: 0.6;">
                            <div style="color: #f4d03f; font-weight: 700;">+ {len(audit['issues']) - 3} More Issues</div>
                            <div style="color: #94a3b8; margin-top: 0.5rem;">Detailed recommendations and code fixes...</div>
                            <div style="color: #94a3b8; margin-top: 0.25rem;">AI-powered suggestions from our 5-book knowledge base...</div>
                        </div>
                        <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: linear-gradient(135deg, #d4a017 0%, #b8860b 100%); color: #000; padding: 0.75rem 1.5rem; border-radius: 8px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;">
                            🔓 Unlock Full Report
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                # Issue summary
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Issues", len(audit['issues']))
                col2.metric("Critical", audit['critical'])
                col3.metric("Warnings", audit['warning'])

                st.markdown("---")

                # Navigation
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("← Start Over"):
                        st.session_state.lead_step = 1
                        st.rerun()
                with col2:
                    if st.button("Continue to Get Full Report →", type="primary"):
                        st.session_state.lead_step = 3
                        st.rerun()

        # ═══════════════════════════════════════════════════════════════════
        # STEP 3: SMART FILL REVIEW
        # ═══════════════════════════════════════════════════════════════════
        elif st.session_state.lead_step == 3:
            st.markdown("### Step 3: We Found Your Business Info")
            st.markdown("Review the information we extracted from your website. You can edit anything that's incorrect.")

            extracted = st.session_state.lead_extracted

            # Show what we found
            col1, col2 = st.columns(2)
            with col1:
                business_name = st.text_input(
                    "Business Name",
                    value=extracted.get("business_name", ""),
                    key="smart_fill_name"
                )
                email = st.text_input(
                    "Email Address",
                    value=extracted.get("email", ""),
                    key="smart_fill_email"
                )
            with col2:
                phone = st.text_input(
                    "Phone Number",
                    value=extracted.get("phone", ""),
                    key="smart_fill_phone"
                )
                address = st.text_input(
                    "Address",
                    value=extracted.get("address", ""),
                    key="smart_fill_address"
                )

            # Store edited values
            st.session_state.lead_data["business_name"] = business_name
            st.session_state.lead_data["email"] = email
            st.session_state.lead_data["phone"] = phone
            st.session_state.lead_data["address"] = address

            # Show extraction sources
            with st.expander("How we found this info"):
                st.markdown("""
                We extracted your business information from:
                - **Schema.org markup** (structured data in your HTML)
                - **Open Graph tags** (og:site_name, etc.)
                - **Meta tags** (title, description)
                - **Contact links** (mailto:, tel:)
                - **Footer content** (common location for contact info)

                *If any information is missing or incorrect, please update it in the fields above.*
                """)

            st.markdown("---")

            # Navigation
            col1, col2 = st.columns(2)
            with col1:
                if st.button("← Back to Preview"):
                    st.session_state.lead_step = 2
                    st.rerun()
            with col2:
                if st.button("Continue →", type="primary"):
                    st.session_state.lead_step = 4
                    st.rerun()

        # ═══════════════════════════════════════════════════════════════════
        # STEP 4: LEAD CAPTURE FORM
        # ═══════════════════════════════════════════════════════════════════
        elif st.session_state.lead_step == 4:
            st.markdown("### Step 4: Complete Your Information")
            st.markdown("Just a few more details to unlock your complete SEO report with AI-powered recommendations.")

            with st.form("lead_capture_form"):
                col1, col2 = st.columns(2)
                with col1:
                    final_business_name = st.text_input(
                        "Business Name *",
                        value=st.session_state.lead_data.get("business_name", ""),
                        key="form_business_name"
                    )
                    final_email = st.text_input(
                        "Email Address *",
                        value=st.session_state.lead_data.get("email", ""),
                        key="form_email"
                    )
                with col2:
                    final_phone = st.text_input(
                        "Phone Number (optional)",
                        value=st.session_state.lead_data.get("phone", ""),
                        key="form_phone"
                    )
                    challenge = st.selectbox(
                        "What's your biggest SEO challenge? *",
                        SEO_CHALLENGES,
                        key="form_challenge"
                    )

                st.markdown("---")

                # Privacy notice
                st.markdown("""
                <div style="color: #64748b; font-size: 0.8rem;">
                    🔒 Your information is secure and will only be used to send you your SEO report and follow-up recommendations.
                </div>
                """, unsafe_allow_html=True)

                submitted = st.form_submit_button("🚀 Get My Full Report", type="primary", use_container_width=True)

                if submitted:
                    # Validation
                    errors = []
                    if not final_business_name.strip():
                        errors.append("Business name is required")
                    if not final_email.strip():
                        errors.append("Email address is required")
                    elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', final_email):
                        errors.append("Please enter a valid email address")
                    if challenge == "":
                        errors.append("Please select your SEO challenge")

                    if errors:
                        for error in errors:
                            st.error(error)
                    else:
                        # Save lead to database
                        try:
                            db = LeadDatabase().connect()
                            audit = st.session_state.lead_audit

                            lead_dict = {
                                "url": st.session_state.lead_data.get("url", ""),
                                "initial_score": audit['overall_score'] if audit else 0,
                                "extracted_business_name": st.session_state.lead_extracted.get("business_name", ""),
                                "extracted_email": st.session_state.lead_extracted.get("email", ""),
                                "extracted_phone": st.session_state.lead_extracted.get("phone", ""),
                                "extracted_address": st.session_state.lead_extracted.get("address", ""),
                                "business_name": final_business_name,
                                "contact_email": final_email,
                                "contact_phone": final_phone,
                                "seo_challenge": challenge,
                                "full_audit_json": json.dumps([{
                                    "title": i.title,
                                    "severity": i.severity,
                                    "category": i.category,
                                    "description": i.description,
                                    "fix": i.fix,
                                    "law_reference": i.law_reference
                                } for i in audit['issues']] if audit else []),
                                "report_generated": True
                            }

                            lead_id = db.save_lead(lead_dict)
                            st.session_state.lead_data["lead_id"] = lead_id
                            db.close()

                            st.session_state.lead_step = 5
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error saving: {e}")

            # Back button (outside form)
            if st.button("← Back"):
                st.session_state.lead_step = 3
                st.rerun()

        # ═══════════════════════════════════════════════════════════════════
        # STEP 5: FULL REPORT
        # ═══════════════════════════════════════════════════════════════════
        elif st.session_state.lead_step == 5:
            st.markdown("### 🎉 Your Complete SEO Report")

            audit = st.session_state.lead_audit
            page_data = st.session_state.lead_data.get("page_data", {})

            if audit:
                score = audit['overall_score']
                score_color = "#22c55e" if score >= 80 else "#f59e0b" if score >= 60 else "#ef4444"

                # Header with score
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, rgba(30, 58, 95, 0.6) 0%, rgba(15, 29, 50, 0.8) 100%); padding: 1.5rem; border-radius: 16px; border: 2px solid {score_color}; margin-bottom: 1.5rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="color: #f4d03f; font-size: 1.5rem; font-weight: 700;">{st.session_state.lead_data.get('business_name', 'Your Business')}</div>
                            <div style="color: #94a3b8; font-size: 0.9rem;">{st.session_state.lead_data.get('url', '')}</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 3rem; font-weight: 800; color: {score_color};">{score}</div>
                            <div style="color: #94a3b8; font-size: 0.8rem;">SEO Score</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Category scores
                st.markdown("#### Category Breakdown")
                score_cols = st.columns(4)
                for i, (cat, cat_score) in enumerate(audit['scores'].items()):
                    with score_cols[i % 4]:
                        cat_color = "#22c55e" if cat_score >= 80 else "#f59e0b" if cat_score >= 60 else "#ef4444"
                        st.markdown(f"""
                        <div style="background: rgba(20, 20, 20, 0.6); padding: 1rem; border-radius: 12px; text-align: center; border: 1px solid {cat_color}40;">
                            <div style="color: {cat_color}; font-size: 1.8rem; font-weight: 700;">{cat_score}%</div>
                            <div style="color: #94a3b8; font-size: 0.8rem;">{cat.replace('_', ' ').title()}</div>
                        </div>
                        """, unsafe_allow_html=True)

                st.markdown("---")

                # Generate RAG recommendations
                st.markdown("#### AI-Powered Recommendations")
                st.markdown(f"<div style='color: #64748b; font-size: 0.85rem; margin-bottom: 1rem;'>Powered by our {RULE_COUNT}-rule knowledge base from 5 SEO books</div>", unsafe_allow_html=True)

                rag_gen = RAGReportGenerator()
                recommendations = rag_gen.generate_recommendations(audit, page_data)

                for rec in recommendations.get("recommendations", []):
                    sev_color = "#ef4444" if rec["severity"] == "critical" else "#f59e0b"
                    with st.expander(f"{'🔴' if rec['severity'] == 'critical' else '🟡'} {rec['issue']} ({rec['category']})"):
                        st.markdown(f"""
                        <div style="color: #94a3b8; margin-bottom: 0.75rem;">{rec['description']}</div>
                        """, unsafe_allow_html=True)

                        # AI Recommendation
                        st.markdown("**AI Recommendation:**")
                        st.markdown(f"<div style='background: rgba(34, 197, 94, 0.1); padding: 0.75rem; border-radius: 8px; border-left: 3px solid #22c55e; color: #86efac;'>{rec['ai_recommendation']}</div>", unsafe_allow_html=True)

                        # Book citations
                        if rec.get("book_citations"):
                            st.markdown("**Book Citations:**")
                            for cite in rec["book_citations"]:
                                st.markdown(f"""
                                <div style="background: rgba(244, 208, 63, 0.1); padding: 0.5rem; border-radius: 6px; margin-bottom: 0.5rem; border-left: 2px solid #f4d03f;">
                                    <div style="color: #f4d03f; font-size: 0.8rem; font-weight: 600;">📚 {cite['book_title']}</div>
                                    <div style="color: #94a3b8; font-size: 0.8rem; margin-top: 0.25rem;">{cite['content']}</div>
                                </div>
                                """, unsafe_allow_html=True)

                        # Code fix
                        if rec.get("code_fix"):
                            st.markdown("**Code Fix:**")
                            st.code(rec["code_fix"], language="html")

                st.markdown("---")

                # Export options
                st.markdown("#### Download Your Report")
                col1, col2, col3 = st.columns(3)

                with col1:
                    # JSON export
                    report_json = json.dumps({
                        "business": st.session_state.lead_data.get("business_name", ""),
                        "url": st.session_state.lead_data.get("url", ""),
                        "score": audit['overall_score'],
                        "category_scores": audit['scores'],
                        "issues": [{
                            "title": i.title,
                            "severity": i.severity,
                            "category": i.category,
                            "description": i.description,
                            "fix": i.fix
                        } for i in audit['issues']],
                        "recommendations": recommendations.get("recommendations", []),
                        "generated_at": datetime.now().isoformat()
                    }, indent=2)
                    st.download_button(
                        "📄 Download JSON",
                        data=report_json,
                        file_name=f"seo_report_{st.session_state.lead_data.get('business_name', 'report').replace(' ', '_')}.json",
                        mime="application/json"
                    )

                with col2:
                    # CSV export (simplified)
                    csv_data = "Category,Issue,Severity,Fix\n"
                    for i in audit['issues']:
                        csv_data += f'"{i.category}","{i.title}","{i.severity}","{i.fix}"\n'
                    st.download_button(
                        "📊 Download CSV",
                        data=csv_data,
                        file_name=f"seo_issues_{st.session_state.lead_data.get('business_name', 'report').replace(' ', '_')}.csv",
                        mime="text/csv"
                    )

                with col3:
                    if st.button("🔄 Scan Another Site"):
                        # Reset state
                        st.session_state.lead_step = 1
                        st.session_state.lead_data = {}
                        st.session_state.lead_audit = None
                        st.session_state.lead_html = ""
                        st.session_state.lead_extracted = {}
                        st.rerun()

                # Follow-up CTA
                st.markdown("---")
                st.markdown("""
                <div style="background: linear-gradient(135deg, rgba(212, 160, 23, 0.2) 0%, rgba(184, 134, 11, 0.3) 100%); padding: 1.5rem; border-radius: 16px; text-align: center; border: 1px solid rgba(212, 160, 23, 0.4);">
                    <div style="color: #f4d03f; font-size: 1.3rem; font-weight: 700;">Need Help Implementing These Fixes?</div>
                    <div style="color: #94a3b8; margin-top: 0.5rem;">Our team at Wild & Wonderful Websites can help you implement all these SEO improvements.</div>
                    <div style="margin-top: 1rem;">
                        <a href="mailto:contact@wildandwonderfulwebsites.com" style="background: linear-gradient(135deg, #d4a017 0%, #b8860b 100%); color: #000; padding: 0.75rem 1.5rem; border-radius: 8px; text-decoration: none; font-weight: 700; text-transform: uppercase;">Contact Us</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 0.85rem; padding: 1rem;">
    <p>🌐 Wild & Wonderful Websites - West Virginia</p>
    <p style="font-size: 0.75rem; margin-top: 8px;">
        Founded by Adaryus Gillum
    </p>
</div>
""", unsafe_allow_html=True)




