"""SangamAI Visual Identity — v2  ·  «Forge» theme

Design direction: Industrial warmth meets editorial refinement.
───────────────────────────────────────────────────────────────
● Palette: Charcoal-black canvas (#09090b), warm graphite surfaces (#151518),
  burnt-orange accent (#E8532E) dominates, bone-white text (#F0ECE5).
● Fonts: "Playfair Display" (serif display) + "Outfit" (geometric body) +
  "Fira Code" (mono). A striking serif/geometric contrast.
● Texture: subtle dot-grid pattern overlay, warm diagonal streak.
● Cards: frosted warm-glass, orange border glow.
"""

import streamlit as st

# ── colour tokens ─────────────────────────────────────────────────────
BG_VOID       = "#09090b"
BG_SURFACE    = "#151518"
BG_CARD       = "rgba(21, 21, 24, 0.72)"
BORDER_WARM   = "rgba(232, 83, 46, 0.15)"
ACCENT        = "#E8532E"      # burnt orange — the hero
ACCENT_GLOW   = "#FF7043"      # lighter orange for hovers
ACCENT_DIM    = "#B33D1F"      # deeper ember for gradients
TEXT_PRIMARY   = "#F0ECE5"      # warm bone-white
TEXT_MUTED     = "#7C7C85"
TEXT_DIM       = "#38383F"


def inject_theme() -> None:
    """Call once at the top of every page."""

    st.markdown(
        f"""
        <!-- Google Fonts -->
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400..900;1,400..900&family=Outfit:wght@200..700&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">

        <style>
        /* ═══════════════════════════════════════════════════════════
           0. ROOT & CANVAS
           ═══════════════════════════════════════════════════════════ */
        :root {{
            --bg-void:      {BG_VOID};
            --bg-surface:   {BG_SURFACE};
            --bg-card:      {BG_CARD};
            --border-warm:  {BORDER_WARM};
            --accent:       {ACCENT};
            --accent-glow:  {ACCENT_GLOW};
            --accent-dim:   {ACCENT_DIM};
            --text:         {TEXT_PRIMARY};
            --text-muted:   {TEXT_MUTED};
            --text-dim:     {TEXT_DIM};
            --font-display: 'Playfair Display', Georgia, serif;
            --font-body:    'Outfit', sans-serif;
            --font-mono:    'Fira Code', monospace;
        }}

        .stApp, .stApp > header,
        [data-testid="stAppViewContainer"],
        [data-testid="stHeader"] {{
            background: var(--bg-void) !important;
        }}

        /* dot-grid texture */
        .stApp::before {{
            content: "";
            position: fixed; inset: 0; z-index: 0;
            pointer-events: none; opacity: 0.028;
            background-image: radial-gradient(circle, var(--text-dim) 1px, transparent 1px);
            background-size: 24px 24px;
        }}

        /* warm diagonal streak — top-left */
        .stApp::after {{
            content: "";
            position: fixed;
            top: -80px; left: -160px;
            width: 420px; height: 2px;
            background: linear-gradient(90deg, transparent, var(--accent), transparent);
            transform: rotate(-32deg);
            pointer-events: none; z-index: 1; opacity: 0.30;
        }}

        /* ═══════════════════════════════════════════════════════════
           1. TYPOGRAPHY
           ═══════════════════════════════════════════════════════════ */
        html, body, [class*="css"] {{
            font-family: var(--font-body) !important;
            color: var(--text) !important;
        }}
        h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{
            font-family: var(--font-display) !important;
            color: var(--text) !important;
            letter-spacing: -0.01em;
        }}
        h1 {{ font-size: 2.6rem !important; font-weight: 700 !important; }}
        h2 {{ font-size: 1.55rem !important; font-weight: 600 !important; }}
        code, pre, .stCodeBlock {{ font-family: var(--font-mono) !important; }}
        p, li, span, label, .stMarkdown p {{
            color: var(--text) !important;
            line-height: 1.65;
        }}

        /* ═══════════════════════════════════════════════════════════
           2. SIDEBAR
           ═══════════════════════════════════════════════════════════ */
        [data-testid="stSidebar"] {{
            background: linear-gradient(175deg, #111113 0%, #0c0c0e 100%) !important;
            border-right: 1px solid var(--border-warm) !important;
        }}
        [data-testid="stSidebar"] * {{ color: var(--text) !important; }}
        [data-testid="stSidebar"] .stDivider {{ border-color: var(--text-dim) !important; }}

        /* ═══════════════════════════════════════════════════════════
           3. INPUTS
           ═══════════════════════════════════════════════════════════ */
        .stTextInput > div > div,
        .stSelectbox > div > div {{
            background: rgba(21, 21, 24, 0.55) !important;
            border: 1px solid var(--text-dim) !important;
            border-radius: 8px !important;
            color: var(--text) !important;
            backdrop-filter: blur(6px);
            transition: border-color 0.25s ease, box-shadow 0.25s ease;
        }}
        .stTextInput > div > div:focus-within,
        .stSelectbox > div > div:focus-within {{
            border-color: var(--accent) !important;
            box-shadow: 0 0 0 2px rgba(232, 83, 46, 0.18) !important;
        }}
        .stTextInput input, .stSelectbox select {{ color: var(--text) !important; }}
        .stTextInput input {{
            padding: 0.6rem 0.75rem !important;
            font-size: 0.95rem !important;
            line-height: 1.5 !important;
        }}
        .stTextInput input::placeholder {{ color: var(--text-muted) !important; }}

        /* ═══════════════════════════════════════════════════════════
           4. BUTTONS
           ═══════════════════════════════════════════════════════════ */
        .stButton > button[kind="primary"],
        .stButton > button {{
            background: linear-gradient(135deg, var(--accent), var(--accent-dim)) !important;
            color: {TEXT_PRIMARY} !important;
            border: none !important;
            border-radius: 8px !important;
            font-family: var(--font-body) !important;
            font-weight: 600 !important;
            padding: 0.55rem 1.5rem !important;
            letter-spacing: 0.02em;
            transition: transform 0.15s ease, box-shadow 0.25s ease;
        }}
        .stButton > button:hover {{
            transform: translateY(-1px);
            box-shadow: 0 6px 24px rgba(232, 83, 46, 0.30) !important;
            background: linear-gradient(135deg, var(--accent-glow), var(--accent)) !important;
        }}
        .stButton > button:active {{ transform: translateY(0); }}

        /* ═══════════════════════════════════════════════════════════
           5. TABS
           ═══════════════════════════════════════════════════════════ */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 0;
            background: transparent !important;
            border-bottom: 1px solid var(--text-dim) !important;
        }}
        .stTabs [data-baseweb="tab"] {{
            font-family: var(--font-body) !important;
            font-weight: 500;
            color: var(--text-muted) !important;
            background: transparent !important;
            border-radius: 0 !important;
            padding: 0.7rem 1.6rem !important;
            border-bottom: 2px solid transparent !important;
            transition: color 0.2s ease, border-color 0.2s ease;
        }}
        .stTabs [data-baseweb="tab"][aria-selected="true"] {{
            color: var(--accent) !important;
            border-bottom: 2px solid var(--accent) !important;
        }}
        .stTabs [data-baseweb="tab-highlight"] {{
            background-color: var(--accent) !important;
        }}
        .stTabs [data-baseweb="tab-panel"] {{ padding-top: 1.5rem; }}

        /* ═══════════════════════════════════════════════════════════
           6. CHAT MESSAGES
           ═══════════════════════════════════════════════════════════ */
        [data-testid="stChatMessage"] {{
            background: var(--bg-card) !important;
            border: 1px solid var(--border-warm) !important;
            border-radius: 12px !important;
            padding: 1rem 1.25rem !important;
            backdrop-filter: blur(10px);
            margin-bottom: 0.8rem !important;
        }}

        /* ═══════════════════════════════════════════════════════════
           6b. CHAT INPUT — proper border, padding, focus
           ═══════════════════════════════════════════════════════════ */
        [data-testid="stChatInput"] {{
            background: rgba(21, 21, 24, 0.65) !important;
            border: 1px solid var(--text-dim) !important;
            border-radius: 10px !important;
            padding: 0.35rem 0.5rem !important;
            transition: border-color 0.25s ease, box-shadow 0.25s ease;
        }}
        [data-testid="stChatInput"]:focus-within {{
            border-color: var(--accent) !important;
            box-shadow: 0 0 0 2px rgba(232, 83, 46, 0.15) !important;
        }}
        [data-testid="stChatInput"] textarea {{
            background: transparent !important;
            border: none !important;
            color: var(--text) !important;
            padding: 0.6rem 0.75rem !important;
            font-family: var(--font-body) !important;
            font-size: 0.95rem !important;
            line-height: 1.5 !important;
        }}
        [data-testid="stChatInput"] textarea::placeholder {{
            color: var(--text-muted) !important;
        }}
        /* send button inside chat input */
        [data-testid="stChatInput"] button {{
            background: var(--accent) !important;
            border: none !important;
            border-radius: 6px !important;
            color: var(--text) !important;
        }}
        [data-testid="stChatInput"] button:hover {{
            background: var(--accent-glow) !important;
        }}

        /* ═══════════════════════════════════════════════════════════
           7. ALERTS
           ═══════════════════════════════════════════════════════════ */
        .stAlert {{
            background: rgba(21, 21, 24, 0.55) !important;
            border-radius: 10px !important;
            backdrop-filter: blur(8px);
        }}
        .stSuccess {{ border-left: 3px solid var(--accent) !important; }}
        .stWarning {{ border-left: 3px solid #D4A017 !important; }}

        /* ═══════════════════════════════════════════════════════════
           8. EXPANDER
           ═══════════════════════════════════════════════════════════ */
        .streamlit-expanderHeader {{
            font-family: var(--font-body) !important;
            font-weight: 500;
            color: var(--text-muted) !important;
            background: transparent !important;
        }}
        .streamlit-expanderContent {{
            background: rgba(21, 21, 24, 0.45) !important;
            border: 1px solid var(--border-warm) !important;
            border-radius: 0 0 10px 10px !important;
        }}

        /* ═══════════════════════════════════════════════════════════
           9. FILE UPLOADER
           ═══════════════════════════════════════════════════════════ */
        [data-testid="stFileUploader"] {{ background: transparent !important; }}
        [data-testid="stFileUploader"] section {{
            background: rgba(21, 21, 24, 0.35) !important;
            border: 1px dashed var(--text-dim) !important;
            border-radius: 10px !important;
            padding: 2rem !important;
            transition: border-color 0.25s ease;
        }}
        [data-testid="stFileUploader"] section:hover {{
            border-color: var(--accent) !important;
        }}

        /* ═══════════════════════════════════════════════════════════
           10. SPINNER
           ═══════════════════════════════════════════════════════════ */
        .stSpinner > div {{ border-top-color: var(--accent) !important; }}

        /* ═══════════════════════════════════════════════════════════
           11. SCROLLBAR
           ═══════════════════════════════════════════════════════════ */
        ::-webkit-scrollbar {{ width: 5px; height: 5px; }}
        ::-webkit-scrollbar-track {{ background: var(--bg-void); }}
        ::-webkit-scrollbar-thumb {{
            background: var(--text-dim);
            border-radius: 4px;
        }}
        ::-webkit-scrollbar-thumb:hover {{ background: var(--text-muted); }}

        /* firefox */
        * {{
            scrollbar-width: thin;
            scrollbar-color: var(--text-dim) var(--bg-void);
        }}

        /* ═══════════════════════════════════════════════════════════
           12. DIVIDERS
           ═══════════════════════════════════════════════════════════ */
        hr, .stDivider {{ border-color: var(--text-dim) !important; opacity: 0.5; }}

        /* ═══════════════════════════════════════════════════════════
           13. CAPTIONS
           ═══════════════════════════════════════════════════════════ */
        .stCaption, small, .stMarkdown small {{
            color: var(--text-muted) !important;
            font-size: 0.82rem !important;
        }}

        /* ═══════════════════════════════════════════════════════════
           14. DROPDOWN
           ═══════════════════════════════════════════════════════════ */
        [data-baseweb="popover"] {{
            background: var(--bg-surface) !important;
            border: 1px solid var(--border-warm) !important;
            border-radius: 8px !important;
        }}
        [data-baseweb="popover"] li {{
            color: var(--text) !important;
            background: transparent !important;
        }}
        [data-baseweb="popover"] li:hover {{
            background: rgba(232, 83, 46, 0.10) !important;
        }}

        /* ═══════════════════════════════════════════════════════════
           15. UTILITY CLASSES
           ═══════════════════════════════════════════════════════════ */
        .omni-hero {{
            text-align: center;
            padding: 3rem 0 1.5rem;
        }}
        .omni-hero h1 {{
            font-family: var(--font-display) !important;
            font-size: 3.2rem !important;
            background: linear-gradient(135deg, var(--accent) 0%, #F4A261 60%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.3rem !important;
        }}
        .omni-hero .tagline {{
            color: var(--text-muted);
            font-size: 1.05rem;
            font-weight: 300;
            letter-spacing: 0.04em;
        }}
        .omni-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-warm);
            border-radius: 14px;
            padding: 1.8rem 2rem;
            backdrop-filter: blur(12px);
            margin-bottom: 1rem;
        }}
        .omni-label {{
            color: var(--text-muted);
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            font-family: var(--font-body);
            font-weight: 500;
            margin-bottom: 0.35rem;
        }}
        .omni-divider {{
            height: 1px;
            background: linear-gradient(90deg, transparent, var(--border-warm), transparent);
            border: none;
            margin: 1.5rem 0;
        }}
        .omni-glow-text {{
            color: var(--accent) !important;
            text-shadow: 0 0 20px rgba(232, 83, 46, 0.25);
        }}

        /* ═══════════════════════════════════════════════════════════
           16. CREATIVE LOADING PIPELINE
           ═══════════════════════════════════════════════════════════ */
        .pipeline-container {{
            display: flex;
            flex-direction: column;
            gap: 0;
            padding: 1rem 0;
        }}
        .pipeline-step {{
            display: flex;
            align-items: center;
            gap: 0.9rem;
            padding: 0.65rem 1rem;
            border-left: 2px solid var(--text-dim);
            position: relative;
            transition: all 0.4s ease;
        }}
        .pipeline-step.active {{
            border-left-color: var(--accent);
        }}
        .pipeline-step.done {{
            border-left-color: var(--accent);
            opacity: 0.55;
        }}
        .pipeline-step .dot {{
            width: 10px; height: 10px;
            border-radius: 50%;
            background: var(--text-dim);
            flex-shrink: 0;
            transition: all 0.3s ease;
        }}
        .pipeline-step.active .dot {{
            background: var(--accent);
            box-shadow: 0 0 10px rgba(232, 83, 46, 0.5);
            animation: pulse-dot 1.2s ease-in-out infinite;
        }}
        .pipeline-step.done .dot {{
            background: var(--accent);
        }}
        .pipeline-step .step-label {{
            font-family: var(--font-body);
            font-size: 0.88rem;
            font-weight: 400;
            color: var(--text-dim);
            transition: color 0.3s ease;
        }}
        .pipeline-step.active .step-label {{
            color: var(--text);
            font-weight: 500;
        }}
        .pipeline-step.done .step-label {{
            color: var(--text-muted);
        }}
        .pipeline-step .step-icon {{
            font-size: 0.85rem;
            opacity: 0;
            transition: opacity 0.3s ease;
        }}
        .pipeline-step.done .step-icon {{
            opacity: 1;
        }}

        @keyframes pulse-dot {{
            0%, 100% {{ transform: scale(1); opacity: 1; }}
            50% {{ transform: scale(1.5); opacity: 0.7; }}
        }}

        /* ═══════════════════════════════════════════════════════════
           17. USERNAME BADGE
           ═══════════════════════════════════════════════════════════ */
        .username-badge {{
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            margin: 0.6rem 0 0.85rem;
            padding: 0.35rem 0.75rem;
            background: rgba(232, 83, 46, 0.10);
            border: 1px solid rgba(232, 83, 46, 0.20);
            border-radius: 6px;
            font-family: var(--font-body);
            font-size: 0.88rem;
            font-weight: 500;
            color: var(--accent-glow);
        }}
        .username-badge .uname {{
            color: var(--text);
        }}
        .username-hint {{
            display: inline-block;
            margin: 0.5rem 0 0.7rem;
            padding: 0.4rem 0.75rem;
            background: rgba(232, 83, 46, 0.08);
            border: 1px dashed rgba(232, 83, 46, 0.25);
            border-radius: 6px;
            font-size: 0.78rem;
            color: var(--accent-glow);
            font-family: var(--font-body);
            animation: hint-fade 2s ease-in-out infinite;
        }}
        @keyframes hint-fade {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.55; }}
        }}

        /* ═══════════════════════════════════════════════════════════
           18. PROFILE INFO GRID
           ═══════════════════════════════════════════════════════════ */
        .profile-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.2rem;
            margin-bottom: 1.2rem;
        }}
        .profile-field {{
            padding: 0;
        }}
        .profile-field .field-label {{
            color: var(--text-muted);
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            font-family: var(--font-body);
            font-weight: 500;
            margin-bottom: 0.3rem;
        }}
        .profile-field .field-value {{
            color: var(--text);
            font-size: 0.95rem;
            font-family: var(--font-body);
            word-break: break-all;
        }}
        .profile-field .field-value.mono {{
            font-family: var(--font-mono);
            font-size: 0.82rem;
            color: var(--text-muted);
        }}

        /* ═══════════════════════════════════════════════════════════
           19. LOGIN TRANSITION LOADER
           ═══════════════════════════════════════════════════════════ */
        .login-loader-overlay {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 60vh;
            gap: 1.5rem;
        }}
        .login-loader-overlay h2 {{
            font-family: var(--font-display) !important;
            font-size: 2.4rem !important;
            background: linear-gradient(135deg, var(--accent) 0%, #F4A261 60%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0 !important;
        }}
        .login-loader-bar {{
            width: 180px;
            height: 3px;
            background: var(--text-dim);
            border-radius: 3px;
            overflow: hidden;
            position: relative;
        }}
        .login-loader-bar::after {{
            content: "";
            position: absolute;
            top: 0; left: -60%;
            width: 60%; height: 100%;
            background: linear-gradient(90deg, transparent, var(--accent), transparent);
            border-radius: 3px;
            animation: loader-slide 1.2s ease-in-out infinite;
        }}
        @keyframes loader-slide {{
            0%   {{ left: -60%; }}
            100% {{ left: 100%; }}
        }}
        .login-loader-text {{
            font-family: var(--font-body);
            font-size: 0.85rem;
            color: var(--text-muted);
            letter-spacing: 0.06em;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
