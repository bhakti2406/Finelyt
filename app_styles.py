# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL DESIGN SYSTEM — Finelyt
# ─────────────────────────────────────────────────────────────────────────────

GLOBAL_CSS = """
<div class="fintech-bg">
    <div class="glow-orb orb-1"></div>
    <div class="glow-orb orb-2"></div>
    <div class="glow-orb orb-3"></div>
    <div class="glow-orb orb-4"></div>
    <div class="particles-layer"></div>
    <div class="fintech-wave"></div>
</div>
<style>
/* ── FONTS ─────────────────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

/* ── FINTECH ANIMATED BACKGROUND ── */
.fintech-bg {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    z-index: -9999;
    background-color: #0B0F1A;
    overflow: hidden;
    pointer-events: none;
}

/* Moving Grid Lines & Scanning Streak */
.fintech-bg::before {
    content: '';
    position: absolute;
    inset: 0;
    background-image: 
        linear-gradient(to right, rgba(0, 242, 168, 0.015) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(0, 242, 168, 0.015) 1px, transparent 1px);
    background-size: 60px 60px;
    mask-image: radial-gradient(circle at 50% 50%, #000 60%, transparent 100%);
    -webkit-mask-image: radial-gradient(circle at 50% 50%, #000 60%, transparent 100%);
    pointer-events: none;
    animation: grid-drift 20s linear infinite;
}

@keyframes grid-drift {
    0% { background-position: 0 0; }
    100% { background-position: 60px 60px; }
}

/* Light streak scanner line */
.fintech-bg::after {
    content: '';
    position: absolute;
    top: -50%;
    left: 0;
    width: 100%;
    height: 200%;
    background: linear-gradient(to bottom, 
        transparent 45%, 
        rgba(0, 212, 255, 0.02) 48%, 
        rgba(0, 242, 168, 0.06) 50%, 
        rgba(0, 212, 255, 0.02) 52%, 
        transparent 55%);
    pointer-events: none;
    animation: scan-line 12s cubic-bezier(0.4, 0, 0.2, 1) infinite;
}

@keyframes scan-line {
    0% { transform: translateY(-30%); }
    100% { transform: translateY(30%); }
}

/* Premium Glowing Mesh Orbs */
.glow-orb {
    position: absolute;
    border-radius: 50%;
    filter: blur(130px);
    mix-blend-mode: screen;
    pointer-events: none;
    opacity: 0.65;
}
/* Orb-1: Green */
.orb-1 {
    top: -10%;
    left: -10%;
    width: 55vw;
    height: 55vw;
    background: radial-gradient(circle, rgba(0, 242, 168, 0.12), transparent 70%);
    animation: float-orb-1 25s ease-in-out infinite alternate;
}
/* Orb-2: Teal/Blue */
.orb-2 {
    bottom: -15%;
    right: -10%;
    width: 65vw;
    height: 65vw;
    background: radial-gradient(circle, rgba(0, 212, 255, 0.1), transparent 70%);
    animation: float-orb-2 30s ease-in-out infinite alternate;
}
/* Orb-3: Purple */
.orb-3 {
    top: 25%;
    left: 20%;
    width: 45vw;
    height: 45vw;
    background: radial-gradient(circle, rgba(139, 92, 246, 0.06), transparent 70%);
    animation: float-orb-3 20s ease-in-out infinite alternate;
}
/* Orb-4: Blue */
.orb-4 {
    bottom: 30%;
    right: 25%;
    width: 40vw;
    height: 40vw;
    background: radial-gradient(circle, rgba(99, 102, 241, 0.05), transparent 70%);
    animation: float-orb-4 22s ease-in-out infinite alternate;
}

@keyframes float-orb-1 {
    0% { transform: translate(0, 0) scale(1); }
    100% { transform: translate(12vw, 12vh) scale(1.15); }
}
@keyframes float-orb-2 {
    0% { transform: translate(0, 0) scale(1.1); }
    100% { transform: translate(-15vw, -12vh) scale(0.9); }
}
@keyframes float-orb-3 {
    0% { transform: translate(0, 0) scale(0.9); }
    100% { transform: translate(8vw, -10vh) scale(1.1); }
}
@keyframes float-orb-4 {
    0% { transform: translate(0, 0) scale(1.05); }
    100% { transform: translate(-10vw, 8vh) scale(0.95); }
}

/* Wireframe wave wave elements */
.fintech-wave {
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 25vh;
    opacity: 0.08;
    background-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1440 320' fill='none'%3E%3Cpath d='M0,192L48,197.3C96,203,192,213,288,208C384,203,480,181,576,181.3C672,181,768,203,864,197.3C960,192,1056,160,1152,144C1248,128,1344,128,1392,128L1440,128L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z' fill='%2300D4FF'/%3E%3C/svg%3E");
    background-size: 1440px 100%;
    background-repeat: repeat-x;
    animation: wave-slide 40s linear infinite;
    mask-image: linear-gradient(to top, rgba(0,0,0,1), rgba(0,0,0,0));
    -webkit-mask-image: linear-gradient(to top, rgba(0,0,0,1), rgba(0,0,0,0));
}

@keyframes wave-slide {
    0% { background-position-x: 0; }
    100% { background-position-x: 1440px; }
}

/* Floating particles CSS */
.particles-layer {
    position: absolute;
    inset: 0;
    opacity: 0.18;
    background-image: 
        radial-gradient(circle, rgba(0, 242, 168, 0.3) 1px, transparent 1px),
        radial-gradient(circle, rgba(0, 212, 255, 0.3) 1.5px, transparent 1.5px);
    background-size: 180px 180px, 240px 240px;
    background-position: 0 0, 90px 120px;
    animation: particles-drift 35s linear infinite;
}

@keyframes particles-drift {
    0% { transform: translateY(0) rotate(0deg); }
    100% { transform: translateY(-180px) rotate(5deg); }
}

/* ── DESIGN TOKENS ─────────────────────────────────────────────────────────── */
:root {
    --bg-base:        #0B0F1A; /* Deep Fintech Navy base */
    --bg-surface:     #0F1426; /* Darker navy/slate surface */
    --bg-elevated:    #181E36; /* Slate elevated background */
    --bg-card:        #111830; /* Premium navy card background */
    --bg-card-hover:  #192245; /* Slightly lighter navy hover card */

    --border:         #1E274A; /* Slate border */
    --border-light:   #2E3D75; /* Light border */
    --border-focus:   #00F2A8; /* Fintech green */

    --accent:         #00F2A8; /* Fintech green */
    --accent-dim:     #00F2A815; /* Transparent green */
    --accent-glow:    #00F2A808;
    --accent-hover:   #00C88C; /* Rich green hover */

    --danger:         #EF4444; /* Fintech red */
    --danger-dim:     #EF444415;
    --warning:        #F59E0B;
    --warning-dim:    #F59E0B15;
    --info:           #00D4FF;
    --info-dim:       #00D4FF15;
    --purple:         #8B5CF6;
    --purple-dim:     #8B5CF615;

    --text-primary:   #F8FAFC; /* Off-white */
    --text-secondary: #94A3B8; /* Slate gray */
    --text-muted:     #64748B; /* Darker slate gray */
    --text-accent:    #00F2A8;

    --radius-sm:   8px;
    --radius-md:   12px;
    --radius-lg:   16px;
    --radius-xl:   20px;
    --radius-full: 999px;

    --shadow-sm:  0 1px 3px rgba(0,0,0,0.5);
    --shadow-md:  0 4px 12px rgba(0,0,0,0.4);
    --shadow-lg:  0 10px 25px rgba(0,0,0,0.5);
    --shadow-glow: 0 0 15px rgba(0,242,168,0.1);

    --transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    --font: 'Inter', sans-serif;
    --font-mono: 'JetBrains Mono', monospace;
}

/* ── GLOBAL RESET ───────────────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }

body {
    background-color: var(--bg-base) !important;
}

html, body, [data-testid="stAppViewContainer"] {
    background-color: transparent !important;
    color: var(--text-primary) !important;
    font-family: var(--font) !important;
    font-size: 15px;
    line-height: 1.6;
    -webkit-font-smoothing: antialiased;
}

/* ── HIDE STREAMLIT CHROME ──────────────────────────────────────────────────── */
#MainMenu, footer, header { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
.stDeployButton { display: none !important; }

/* ── MAIN CONTENT AREA ──────────────────────────────────────────────────────── */
[data-testid="stMain"] {
    background: transparent !important;
}
.main .block-container {
    padding: 2.5rem 3rem 4rem !important;
    max-width: 1200px !important;
    animation: contentFadeIn 0.8s cubic-bezier(0.16, 1, 0.3, 1) both;
}

@keyframes contentFadeIn {
    0% {
        opacity: 0;
        transform: translateY(16px);
    }
    100% {
        opacity: 1;
        transform: translateY(0);
    }
}

/* ── SIDEBAR ────────────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--bg-surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 1.5rem 1rem !important;
}
[data-testid="stSidebarNavItems"] {
    gap: 2px !important;
}

/* Hide Streamlit radio button circles */
[data-testid="stSidebar"] .stRadio div[data-baseweb="radio"] {
    display: none !important;
}

/* Sidebar radio buttons styled as clean modern nav list */
[data-testid="stSidebar"] .stRadio > div {
    gap: 4px !important;
}
[data-testid="stSidebar"] .stRadio label {
    background: transparent !important;
    border: 1px solid transparent !important;
    border-radius: var(--radius-sm) !important;
    padding: 10px 14px !important;
    color: var(--text-secondary) !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    cursor: pointer !important;
    transition: var(--transition) !important;
    width: 100% !important;
    display: flex !important;
    align-items: center !important;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: var(--bg-elevated) !important;
    color: var(--text-primary) !important;
    border-color: var(--border) !important;
}

/* Selected navigation tab styling using CSS has */
[data-testid="stSidebar"] .stRadio [data-testid="stRadioButton"]:has(input:checked) label {
    background: var(--accent-dim) !important;
    color: var(--accent) !important;
    font-weight: 600 !important;
    border-color: rgba(16,185,129,0.3) !important;
}

/* ── TYPOGRAPHY ─────────────────────────────────────────────────────────────── */
h1, h2, h3, h4, h5, h6 {
    font-family: var(--font) !important;
    color: var(--text-primary) !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
    line-height: 1.2 !important;
}
h1 { font-size: 2.2rem !important; }
h2 { font-size: 1.6rem !important; }
h3 { font-size: 1.2rem !important; }
p  { color: var(--text-secondary); line-height: 1.7; }

/* ── FINTECH GLOW EFFECTS ───────────────────────────────────────────────────── */
.fc-glow-emerald {
    color: #10B981 !important;
    text-shadow: 0 0 10px rgba(16, 185, 129, 0.6), 0 0 20px rgba(16, 185, 129, 0.3) !important;
}
.fc-glow-blue {
    color: #3B82F6 !important;
    text-shadow: 0 0 10px rgba(59, 130, 246, 0.6), 0 0 20px rgba(59, 130, 246, 0.3) !important;
}
.fc-glow-purple {
    color: #8B5CF6 !important;
    text-shadow: 0 0 10px rgba(139, 92, 246, 0.6), 0 0 20px rgba(139, 92, 246, 0.3) !important;
}
.fc-logo-glow {
    color: #10B981 !important;
    font-weight: 800;
    text-shadow: 0 0 15px rgba(16, 185, 129, 0.7), 0 0 30px rgba(16, 185, 129, 0.3) !important;
}
.fc-gradient-glow {
    filter: drop-shadow(0 0 15px rgba(16, 185, 129, 0.45));
}
.fc-metric-value-glow {
    text-shadow: 0 0 10px rgba(16, 185, 129, 0.2) !important;
}
.nw-num {
    text-shadow: 0 0 15px currentColor !important;
}
[data-testid="stMetricValue"] > div {
    text-shadow: 0 0 10px rgba(16, 185, 129, 0.2) !important;
}

/* ── PAGE HEADERS ───────────────────────────────────────────────────────────── */
.fc-page-header {
    margin-bottom: 2rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid var(--border);
}
.fc-page-title, .page-title {
    font-size: 2.1rem !important;
    font-weight: 800 !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.03em !important;
    line-height: 1.1 !important;
    margin-bottom: 4px !important;
    text-shadow: 0 0 15px rgba(248, 250, 252, 0.12), 0 0 30px rgba(248, 250, 252, 0.05) !important;
}
.fc-page-sub, .page-sub {
    font-size: 0.92rem !important;
    color: var(--text-secondary) !important;
    font-weight: 400 !important;
    margin-bottom: 1.5rem !important;
}

/* ── SECTION LABELS ─────────────────────────────────────────────────────────── */
.fc-section-label {
    font-size: 0.7rem;
    font-weight: 700;
    color: var(--accent);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 0.8rem;
    display: flex;
    align-items: center;
    gap: 6px;
}
.fc-section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
}

/* ── METRIC / KPI CARDS ─────────────────────────────────────────────────────── */
.fc-metric {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.4rem 1.6rem;
    transition: var(--transition);
    position: relative;
    overflow: hidden;
    box-shadow: var(--shadow-sm);
}
.fc-metric::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent), transparent);
    opacity: 0;
    transition: var(--transition);
}
.fc-metric:hover {
    border-color: var(--accent) !important;
    background: var(--bg-card-hover) !important;
    transform: translateY(-4px) !important;
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.5), 0 0 20px rgba(16, 185, 129, 0.15) !important;
}
.fc-metric:hover::before { opacity: 1; }
.fc-metric-label {
    font-size: 0.72rem;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 8px;
}
.fc-metric-value {
    font-size: 1.8rem;
    font-weight: 800;
    color: var(--text-primary);
    letter-spacing: -0.03em;
    line-height: 1;
    font-family: var(--font-mono);
}
.fc-metric-delta {
    font-size: 0.78rem;
    color: var(--text-muted);
    margin-top: 6px;
    display: flex;
    align-items: center;
    gap: 4px;
}

/* ── CONTENT CARDS ──────────────────────────────────────────────────────────── */
.fc-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.4rem 1.6rem;
    margin-bottom: 0.75rem;
    transition: var(--transition);
    box-shadow: var(--shadow-sm);
}
.fc-card:hover {
    border-color: var(--accent) !important;
    background: var(--bg-card-hover) !important;
    transform: translateY(-4px) !important;
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.5), 0 0 20px rgba(16, 185, 129, 0.15) !important;
}
.fc-card-danger {
    background: #191215;
    border-color: var(--danger);
    border-left: 4px solid var(--danger);
}
.fc-card-success {
    background: #0D1B18;
    border-color: var(--accent);
    border-left: 4px solid var(--accent);
}
.fc-card-warning {
    background: #1B1812;
    border-color: var(--warning);
    border-left: 4px solid var(--warning);
}

/* ── BADGES ─────────────────────────────────────────────────────────────────── */
.fc-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 3px 10px;
    border-radius: var(--radius-full);
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.fc-badge-green {
    background: var(--accent-dim);
    border: 1px solid var(--accent);
    color: var(--accent);
}
.fc-badge-red {
    background: var(--danger-dim);
    border: 1px solid var(--danger);
    color: var(--danger);
}
.fc-badge-yellow {
    background: var(--warning-dim);
    border: 1px solid var(--warning);
    color: var(--warning);
}
.fc-badge-blue {
    background: var(--info-dim);
    border: 1px solid var(--info);
    color: var(--info);
}
.fc-badge-purple {
    background: var(--purple-dim);
    border: 1px solid var(--purple);
    color: var(--purple);
}

/* ── PROGRESS BARS ──────────────────────────────────────────────────────────── */
.fc-progress-wrap {
    background: var(--bg-base);
    border-radius: var(--radius-full);
    height: 6px;
    overflow: hidden;
}
.fc-progress-bar {
    height: 100%;
    border-radius: var(--radius-full);
    transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}
.fc-progress-green  { background: var(--accent); }
.fc-progress-yellow { background: var(--warning); }
.fc-progress-red    { background: var(--danger); }

/* ── DIVIDERS ───────────────────────────────────────────────────────────────── */
hr, [data-testid="stDivider"] > hr {
    border: none !important;
    border-top: 1px solid var(--border) !important;
    margin: 1.5rem 0 !important;
}

/* ── STREAMLIT BUTTONS ──────────────────────────────────────────────────────── */
.stButton > button {
    background: var(--bg-elevated) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-light) !important;
    border-radius: var(--radius-sm) !important;
    font-family: var(--font) !important;
    font-size: 0.87rem !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.1rem !important;
    transition: var(--transition) !important;
    letter-spacing: 0.01em !important;
}
.stButton > button:hover {
    background: var(--bg-card-hover) !important;
    border-color: var(--accent) !important;
    color: var(--accent) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 0 15px rgba(16, 185, 129, 0.3) !important;
}
.stButton > button[kind="primary"] {
    background: var(--accent) !important;
    color: #0A0F1D !important;
    border-color: var(--accent) !important;
    font-weight: 700 !important;
}
.stButton > button[kind="primary"]:hover {
    background: var(--accent-hover) !important;
    border-color: var(--accent-hover) !important;
    color: #0A0F1D !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 0 20px rgba(16, 185, 129, 0.5) !important;
}

/* ── STREAMLIT INPUTS ───────────────────────────────────────────────────────── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > div {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border-light) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-primary) !important;
    font-family: var(--font) !important;
    font-size: 0.9rem !important;
    transition: var(--transition) !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.15), 0 0 10px rgba(16, 185, 129, 0.2) !important;
    outline: none !important;
}
.stTextInput label, .stNumberInput label,
.stTextArea label, .stSelectbox label,
.stDateInput label, .stRadio label {
    color: var(--text-secondary) !important;
    font-size: 0.83rem !important;
    font-weight: 500 !important;
    font-family: var(--font) !important;
}

/* ── TABS ───────────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-surface) !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 0 !important;
    padding: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text-muted) !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    font-family: var(--font) !important;
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    padding: 0.75rem 1.2rem !important;
    transition: var(--transition) !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: var(--text-primary) !important;
    background: var(--bg-elevated) !important;
}
.stTabs [aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom-color: var(--accent) !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab-panel"] {
    background: transparent !important;
    padding: 1.5rem 0 !important;
}

/* ── METRICS (st.metric) ────────────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-lg) !important;
    padding: 1.2rem 1.4rem !important;
    transition: var(--transition) !important;
    box-shadow: var(--shadow-sm);
}
[data-testid="stMetric"]:hover {
    border-color: var(--accent) !important;
    transform: translateY(-4px) !important;
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.5), 0 0 20px rgba(16, 185, 129, 0.15) !important;
}
[data-testid="stMetricLabel"] > div {
    color: var(--text-muted) !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    font-family: var(--font) !important;
}
[data-testid="stMetricValue"] > div {
    color: var(--text-primary) !important;
    font-size: 1.7rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.03em !important;
    font-family: var(--font-mono) !important;
}
[data-testid="stMetricDelta"] > div {
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    font-family: var(--font) !important;
}

/* ── DATAFRAME ──────────────────────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    overflow: hidden !important;
}
.dvn-scroller { background: var(--bg-card) !important; }

/* ── ALERTS & MESSAGES ──────────────────────────────────────────────────────── */
[data-testid="stAlert"] {
    border-radius: var(--radius-md) !important;
    border: 1px solid !important;
    font-family: var(--font) !important;
    font-size: 0.88rem !important;
}
[data-testid="stAlert"][data-type="success"] {
    background: #0D1B18 !important;
    border-color: var(--accent) !important;
    color: var(--accent) !important;
}
[data-testid="stAlert"][data-type="error"] {
    background: #191215 !important;
    border-color: var(--danger) !important;
    color: var(--danger) !important;
}
[data-testid="stAlert"][data-type="warning"] {
    background: #1B1812 !important;
    border-color: var(--warning) !important;
    color: var(--warning) !important;
}
[data-testid="stAlert"][data-type="info"] {
    background: #10162A !important;
    border-color: var(--info) !important;
    color: var(--info) !important;
}

/* ── EXPANDER ───────────────────────────────────────────────────────────────── */
[data-testid="stExpander"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    overflow: hidden !important;
}
[data-testid="stExpander"] summary {
    font-family: var(--font) !important;
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    color: var(--text-secondary) !important;
    padding: 0.8rem 1rem !important;
    background: var(--bg-card) !important;
}
[data-testid="stExpander"] summary:hover {
    color: var(--text-primary) !important;
    background: var(--bg-card-hover) !important;
}

/* ── SELECTBOX DROPDOWN ─────────────────────────────────────────────────────── */
[data-baseweb="popover"] {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border-light) !important;
    border-radius: var(--radius-md) !important;
    box-shadow: var(--shadow-lg) !important;
}
[role="option"] {
    background: transparent !important;
    color: var(--text-secondary) !important;
    font-family: var(--font) !important;
    font-size: 0.88rem !important;
    transition: var(--transition) !important;
}
[role="option"]:hover {
    background: var(--bg-card) !important;
    color: var(--text-primary) !important;
}
[aria-selected="true"][role="option"] {
    background: var(--accent-dim) !important;
    color: var(--accent) !important;
}

/* ── DATE INPUT ─────────────────────────────────────────────────────────────── */
[data-testid="stDateInput"] input {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border-light) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-primary) !important;
    font-family: var(--font) !important;
}

/* ── DOWNLOAD BUTTON ────────────────────────────────────────────────────────── */
[data-testid="stDownloadButton"] > button {
    background: var(--bg-elevated) !important;
    color: var(--text-secondary) !important;
    border: 1px solid var(--border-light) !important;
    border-radius: var(--radius-sm) !important;
    font-family: var(--font) !important;
    font-size: 0.84rem !important;
    font-weight: 600 !important;
    transition: var(--transition) !important;
}
[data-testid="stDownloadButton"] > button:hover {
    color: var(--accent) !important;
    border-color: var(--accent) !important;
}

/* ── SPINNER ────────────────────────────────────────────────────────────────── */
[data-testid="stSpinner"] {
    color: var(--accent) !important;
}

/* ── SCROLLBAR ──────────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-base); }
::-webkit-scrollbar-thumb {
    background: var(--border-light);
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

/* ── SIDEBAR LOGO AREA ──────────────────────────────────────────────────────── */
.fc-sidebar-logo {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 0.5rem 0.5rem 1.5rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1rem;
}
.fc-sidebar-logo-icon {
    width: 32px; height: 32px;
    background: var(--accent);
    border-radius: 8px;
    display: flex; align-items: center;
    justify-content: center;
    font-size: 1rem;
}
.fc-sidebar-logo-text {
    font-size: 1rem;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.02em;
}
.fc-sidebar-logo-sub {
    font-size: 0.72rem;
    color: var(--text-muted);
    font-weight: 400;
}

/* ── EMPTY STATE ────────────────────────────────────────────────────────────── */
.fc-empty {
    background: var(--bg-card);
    border: 1px dashed var(--border-light);
    border-radius: var(--radius-xl);
    padding: 4rem 2rem;
    text-align: center;
}
.fc-empty-icon { font-size: 2.5rem; margin-bottom: 1rem; }
.fc-empty-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 0.5rem;
}
.fc-empty-sub {
    font-size: 0.88rem;
    color: var(--text-muted);
    max-width: 300px;
    margin: 0 auto;
}

/* ── TABLE ROWS ─────────────────────────────────────────────────────────────── */
.fc-table-header {
    font-size: 0.7rem;
    font-weight: 700;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 0.4rem;
}
.fc-row-div {
    border-bottom: 1px solid var(--border);
    margin: 0.3rem 0;
    opacity: 0.5;
}

/* ── TOOLTIP / HINT BOX ─────────────────────────────────────────────────────── */
.fc-hint {
    background: var(--accent-glow);
    border-left: 3px solid var(--accent);
    border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
    padding: 0.6rem 0.9rem;
    color: var(--text-secondary);
    font-size: 0.83rem;
    margin: 0.5rem 0 1rem;
    line-height: 1.5;
}
.fc-warn {
    background: var(--warning-dim);
    border-left: 3px solid var(--warning);
    border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
    padding: 0.6rem 0.9rem;
    color: var(--warning);
    font-size: 0.83rem;
    margin: 0.5rem 0 0.8rem;
}
.fc-danger {
    background: var(--danger-dim);
    border-left: 3px solid var(--danger);
    border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
    padding: 0.6rem 0.9rem;
    color: var(--danger);
    font-size: 0.83rem;
    margin: 0.5rem 0 0.8rem;
}

/* ── TOP HORIZONTAL NAVIGATION ──────────────────────────────────────────────── */
div.st-key-top_navigation {
    background: rgba(15, 22, 45, 0.4) !important;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 24px !important;
    padding: 4px 8px !important;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37), 0 0 15px rgba(0, 242, 168, 0.03) !important;
    margin-bottom: 0 !important;
    width: 100% !important;
    overflow: hidden !important;
}

div.st-key-top_navigation div[role="radiogroup"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    gap: 6px !important;
    background: transparent !important;
    border: none !important;
    padding: 2px 4px !important;
    box-shadow: none !important;
    justify-content: flex-start !important;
    align-items: center !important;
    width: 100% !important;
    overflow-x: auto !important;
    -webkit-overflow-scrolling: touch !important;
}

div.st-key-top_navigation div[role="radiogroup"]::-webkit-scrollbar {
    display: none !important;
    width: 0 !important;
    height: 0 !important;
}

div.st-key-top_navigation div[role="radiogroup"] div[data-testid="stRadioButton"] {
    display: inline-block !important;
    margin: 0 !important;
    flex-shrink: 0 !important;
}

/* Hide Streamlit's main navigation widget label */
div.st-key-top_navigation > label {
    display: none !important;
}

/* Hide native Streamlit radio selection markers */
div.st-key-top_navigation div[role="radiogroup"] label [data-testid="stRadioButtonMarker"],
div.st-key-top_navigation div[role="radiogroup"] label > div:first-child {
    display: none !important;
}

/* Style only the radio option labels inside the radiogroup */
div.st-key-top_navigation div[role="radiogroup"] label {
    display: inline-flex !important;
    flex-direction: row !important;
    align-items: center !important;
    justify-content: center !important;
    background: transparent !important;
    border: 1px solid transparent !important;
    border-radius: 20px !important;
    padding: 6px 14px !important;
    height: 30px !important;
    color: var(--text-secondary) !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    cursor: pointer !important;
    transition: all 300ms cubic-bezier(0.4, 0, 0.2, 1) !important;
    margin: 0 !important;
    box-shadow: none !important;
    backdrop-filter: none !important;
    -webkit-backdrop-filter: none !important;
    text-align: center !important;
    position: relative !important;
    overflow: hidden !important;
    white-space: nowrap !important;
    gap: 5px !important;
    flex-shrink: 0 !important;
}

/* Hover state: Lift, Glow, Background Highlight */
div.st-key-top_navigation div[role="radiogroup"] label:hover {
    background: rgba(255, 255, 255, 0.05) !important;
    border-color: rgba(0, 212, 255, 0.2) !important;
    color: var(--text-primary) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 12px rgba(0, 212, 255, 0.15) !important;
}

/* Active state: Green-to-Teal gradient, soft glow, slight elevation, smooth transition */
div.st-key-top_navigation div[role="radiogroup"] label:has(input:checked),
div.st-key-top_navigation div[role="radiogroup"] [data-testid="stRadioButton"][data-checked="true"] label,
div.st-key-top_navigation div[role="radiogroup"] [data-testid="stRadioButton"] label[data-checked="true"],
div.st-key-top_navigation div[role="radiogroup"] [aria-checked="true"] label {
    background: linear-gradient(135deg, #00F2A8, #00D4FF) !important;
    border-color: transparent !important;
    color: #0B0F1A !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 12px rgba(0, 242, 168, 0.35) !important;
    transform: translateY(-1px) !important;
}

/* Active hover state */
div.st-key-top_navigation div[role="radiogroup"] label:has(input:checked):hover,
div.st-key-top_navigation div[role="radiogroup"] [aria-checked="true"] label:hover {
    background: linear-gradient(135deg, #00F2A8, #00D4FF) !important;
    color: #0B0F1A !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 16px rgba(0, 242, 168, 0.45) !important;
}

/* Click / Tactile feedback */
div.st-key-top_navigation div[role="radiogroup"] label:active {
    transform: translateY(-1px) scale(0.97) !important;
    transition: all 0.05s ease !important;
}

/* Add icons via mask-image in ::before */
div.st-key-top_navigation div[role="radiogroup"] label::before {
    content: '';
    display: inline-block;
    width: 12px;
    height: 12px;
    flex-shrink: 0;
    margin-bottom: 0 !important;
    margin-right: 2px !important;
    background-color: var(--text-secondary);
    -webkit-mask-size: contain;
    mask-size: contain;
    -webkit-mask-repeat: no-repeat;
    mask-repeat: no-repeat;
    -webkit-mask-position: center;
    mask-position: center;
    transition: all 300ms cubic-bezier(0.4, 0, 0.2, 1) !important;
}

div.st-key-top_navigation div[role="radiogroup"] label:has(input:checked)::before,
div.st-key-top_navigation div[role="radiogroup"] [data-testid="stRadioButton"][data-checked="true"] label::before,
div.st-key-top_navigation div[role="radiogroup"] [data-testid="stRadioButton"] label[data-checked="true"]::before,
div.st-key-top_navigation div[role="radiogroup"] [aria-checked="true"] label::before {
    background-color: #0B0F1A !important;
}

div.st-key-top_navigation div[role="radiogroup"] label:hover::before {
    background-color: var(--text-primary) !important;
}

/* Specific Icons via nth-child */
/* Order: 1=Dashboard, 2=Add Expense, 3=Income, 4=Anomalies, 5=AI Coach, 6=Budgets, 7=Reports, 8=Splits, 9=Savings, 10=Guilt-Free, 11=Streaks, 12=Bill Calendar, 13=Net Worth, 14=Summary, 15=Settings */

/* 1 — Dashboard */
div.st-key-top_navigation div[role="radiogroup"] [data-testid="stRadioButton"]:nth-child(1) label::before {
    -webkit-mask-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='3' y='3' width='7' height='9'/%3E%3Crect x='14' y='3' width='7' height='5'/%3E%3Crect x='14' y='12' width='7' height='9'/%3E%3Crect x='3' y='16' width='7' height='5'/%3E%3C/svg%3E");
    mask-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='3' y='3' width='7' height='9'/%3E%3Crect x='14' y='3' width='7' height='5'/%3E%3Crect x='14' y='12' width='7' height='9'/%3E%3Crect x='3' y='16' width='7' height='5'/%3E%3C/svg%3E");
}
/* 2 — Add Expense */
div.st-key-top_navigation div[role="radiogroup"] [data-testid="stRadioButton"]:nth-child(2) label::before {
    -webkit-mask-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='12' cy='12' r='10'/%3E%3Cline x1='12' y1='8' x2='12' y2='16'/%3E%3Cline x1='8' y1='12' x2='16' y2='12'/%3E%3C/svg%3E");
    mask-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='12' cy='12' r='10'/%3E%3Cline x1='12' y1='8' x2='12' y2='16'/%3E%3Cline x1='8' y1='12' x2='16' y2='12'/%3E%3C/svg%3E");
}
/* 3 — Income */
div.st-key-top_navigation div[role="radiogroup"] [data-testid="stRadioButton"]:nth-child(3) label::before {
    -webkit-mask-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='12' cy='12' r='10'/%3E%3Cpolyline points='8 12 12 16 16 12'/%3E%3Cline x1='12' y1='8' x2='12' y2='16'/%3E%3C/svg%3E");
    mask-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='12' cy='12' r='10'/%3E%3Cpolyline points='8 12 12 16 16 12'/%3E%3Cline x1='12' y1='8' x2='12' y2='16'/%3E%3C/svg%3E");
}
/* 4 — Anomalies */
div.st-key-top_navigation div[role="radiogroup"] [data-testid="stRadioButton"]:nth-child(4) label::before {
    -webkit-mask-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z'/%3E%3Cline x1='12' y1='9' x2='12' y2='13'/%3E%3Cline x1='12' y1='17' x2='12.01' y2='17'/%3E%3C/svg%3E");
    mask-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z'/%3E%3Cline x1='12' y1='9' x2='12' y2='13'/%3E%3Cline x1='12' y1='17' x2='12.01' y2='17'/%3E%3C/svg%3E");
}
/* 5 — AI Coach */
div.st-key-top_navigation div[role="radiogroup"] [data-testid="stRadioButton"]:nth-child(5) label::before {
    -webkit-mask-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z'/%3E%3C/svg%3E");
    mask-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z'/%3E%3C/svg%3E");
}
/* 6 — Budgets */
div.st-key-top_navigation div[role="radiogroup"] [data-testid="stRadioButton"]:nth-child(6) label::before {
    -webkit-mask-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M21.21 15.89A10 10 0 1 1 8 2.83'/%3E%3Cpath d='M22 12A10 10 0 0 0 12 2v10z'/%3E%3C/svg%3E");
    mask-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M21.21 15.89A10 10 0 1 1 8 2.83'/%3E%3Cpath d='M22 12A10 10 0 0 0 12 2v10z'/%3E%3C/svg%3E");
}
/* 7 — Reports */
div.st-key-top_navigation div[role="radiogroup"] [data-testid="stRadioButton"]:nth-child(7) label::before {
    -webkit-mask-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cline x1='18' y1='20' x2='18' y2='10'/%3E%3Cline x1='12' y1='20' x2='12' y2='4'/%3E%3Cline x1='6' y1='20' x2='6' y2='14'/%3E%3C/svg%3E");
    mask-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cline x1='18' y1='20' x2='18' y2='10'/%3E%3Cline x1='12' y1='20' x2='12' y2='4'/%3E%3Cline x1='6' y1='20' x2='6' y2='14'/%3E%3C/svg%3E");
}
/* 8 — Splits */
div.st-key-top_navigation div[role="radiogroup"] [data-testid="stRadioButton"]:nth-child(8) label::before {
    -webkit-mask-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='18' cy='18' r='3'/%3E%3Ccircle cx='6' cy='6' r='3'/%3E%3Cpath d='M13 6h3a2 2 0 0 1 2 2v7'/%3E%3Cpath d='M11 18H8a2 2 0 0 1-2-2V9'/%3E%3C/svg%3E");
    mask-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='18' cy='18' r='3'/%3E%3Ccircle cx='6' cy='6' r='3'/%3E%3Cpath d='M13 6h3a2 2 0 0 1 2 2v7'/%3E%3Cpath d='M11 18H8a2 2 0 0 1-2-2V9'/%3E%3C/svg%3E");
}
/* 9 — Savings */
div.st-key-top_navigation div[role="radiogroup"] [data-testid="stRadioButton"]:nth-child(9) label::before {
    -webkit-mask-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M19 5c-1.5 0-2.8 1.4-3 2-2.5-1.7-5.5-1.9-8-.5a5.5 5.5 0 0 0-3.5 4.9c-.3.4-.5.8-.5 1.3A3.5 3.5 0 0 0 7.5 16h6.8c.9 0 1.7-.3 2.5-.8 1.7-.5 3-1.8 3.5-3.2A4.2 4.2 0 0 0 20 10V5Z'/%3E%3Cpath d='M2 9v1c0 1.1.9 2 2 2h1'/%3E%3Cpath d='M16 11h.01'/%3E%3Cpath d='M18 14v5a2 2 0 0 1-2 2H12v-4'/%3E%3Cpath d='M12 17v4H8v-4'/%3E%3Cpath d='M10 5h4V3h-4z'/%3E%3C/svg%3E");
    mask-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M19 5c-1.5 0-2.8 1.4-3 2-2.5-1.7-5.5-1.9-8-.5a5.5 5.5 0 0 0-3.5 4.9c-.3.4-.5.8-.5 1.3A3.5 3.5 0 0 0 7.5 16h6.8c.9 0 1.7-.3 2.5-.8 1.7-.5 3-1.8 3.5-3.2A4.2 4.2 0 0 0 20 10V5Z'/%3E%3Cpath d='M2 9v1c0 1.1.9 2 2 2h1'/%3E%3Cpath d='M16 11h.01'/%3E%3Cpath d='M18 14v5a2 2 0 0 1-2 2H12v-4'/%3E%3Cpath d='M12 17v4H8v-4'/%3E%3Cpath d='M10 5h4V3h-4z'/%3E%3C/svg%3E");
}
/* 10 — Guilt-Free */
div.st-key-top_navigation div[role="radiogroup"] [data-testid="stRadioButton"]:nth-child(10) label::before {
    -webkit-mask-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z'/%3E%3C/svg%3E");
    mask-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z'/%3E%3C/svg%3E");
}
/* 11 — Streaks */
div.st-key-top_navigation div[role="radiogroup"] [data-testid="stRadioButton"]:nth-child(11) label::before {
    -webkit-mask-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z'/%3E%3C/svg%3E");
    mask-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z'/%3E%3C/svg%3E");
}
/* 12 — Bill Calendar */
div.st-key-top_navigation div[role="radiogroup"] [data-testid="stRadioButton"]:nth-child(12) label::before {
    -webkit-mask-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='3' y='4' width='18' height='18' rx='2' ry='2'/%3E%3Cline x1='16' y1='2' x2='16' y2='6'/%3E%3Cline x1='8' y1='2' x2='8' y2='6'/%3E%3Cline x1='3' y1='10' x2='21' y2='10'/%3E%3C/svg%3E");
    mask-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='3' y='4' width='18' height='18' rx='2' ry='2'/%3E%3Cline x1='16' y1='2' x2='16' y2='6'/%3E%3Cline x1='8' y1='2' x2='8' y2='6'/%3E%3Cline x1='3' y1='10' x2='21' y2='10'/%3E%3C/svg%3E");
}
/* 13 — Net Worth */
div.st-key-top_navigation div[role="radiogroup"] [data-testid="stRadioButton"]:nth-child(13) label::before {
    -webkit-mask-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='23 6 13.5 15.5 8.5 10.5 1 18'/%3E%3Cpolyline points='17 6 23 6 23 12'/%3E%3C/svg%3E");
    mask-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='23 6 13.5 15.5 8.5 10.5 1 18'/%3E%3Cpolyline points='17 6 23 6 23 12'/%3E%3C/svg%3E");
}
/* 14 — Summary */
div.st-key-top_navigation div[role="radiogroup"] [data-testid="stRadioButton"]:nth-child(14) label::before {
    -webkit-mask-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z'/%3E%3Cpolyline points='14 2 14 8 20 8'/%3E%3Cline x1='16' y1='13' x2='8' y2='13'/%3E%3Cline x1='16' y1='17' x2='8' y2='17'/%3E%3Cpolyline points='10 9 9 9 8 9'/%3E%3C/svg%3E");
    mask-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z'/%3E%3Cpolyline points='14 2 14 8 20 8'/%3E%3Cline x1='16' y1='13' x2='8' y2='13'/%3E%3Cline x1='16' y1='17' x2='8' y2='17'/%3E%3Cpolyline points='10 9 9 9 8 9'/%3E%3C/svg%3E");
}
/* 15 — Settings */
div.st-key-top_navigation div[role="radiogroup"] [data-testid="stRadioButton"]:nth-child(15) label::before {
    -webkit-mask-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='12' cy='12' r='3'/%3E%3Cpath d='M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z'/%3E%3C/svg%3E");
    mask-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='12' cy='12' r='3'/%3E%3Cpath d='M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z'/%3E%3C/svg%3E");
}

/* Tablet responsiveness: Compact size, tight padding */
@media (min-width: 768px) and (max-width: 1200px) {
    div.st-key-top_navigation {
        border-radius: 20px !important;
        padding: 3px 6px !important;
    }
    div.st-key-top_navigation div[role="radiogroup"] label {
        padding: 5px 8px !important;
        font-size: 0.72rem !important;
        gap: 3px !important;
    }
    div.st-key-top_navigation div[role="radiogroup"] label::before {
        width: 10px;
        height: 10px;
        margin-right: 1px !important;
    }
}

/* Mobile responsiveness: Horizontally scrollable navbar */
@media (max-width: 767px) {
    div.st-key-top_navigation {
        border-radius: 16px !important;
        padding: 4px 6px !important;
    }
    div.st-key-top_navigation div[role="radiogroup"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        overflow-x: auto !important;
        justify-content: flex-start !important;
        gap: 6px !important;
        padding: 2px !important;
        -webkit-overflow-scrolling: touch !important;
    }
    div.st-key-top_navigation div[role="radiogroup"]::-webkit-scrollbar {
        display: none !important;
    }
    div.st-key-top_navigation div[role="radiogroup"] label {
        flex: 0 0 auto !important;
        padding: 5px 8px !important;
        font-size: 0.7rem !important;
        gap: 3px !important;
    }
    div.st-key-top_navigation div[role="radiogroup"] label::before {
        width: 10px;
        height: 10px;
        margin-right: 1px !important;
    }
}


/* ── FORM SECTIONS ──────────────────────────────────────────────────────────── */
.fc-form-section {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
}
.fc-form-section-title {
    font-size: 0.85rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 1rem;
    padding-bottom: 0.6rem;
    border-bottom: 1px solid var(--border);
}

/* ── HERO CARD ──────────────────────────────────────────────────────────────── */
.fc-hero {
    background: linear-gradient(135deg, var(--bg-card) 0%,
                var(--bg-surface) 100%);
    border: 1px solid var(--border);
    border-radius: var(--radius-xl);
    padding: 2.5rem;
    text-align: center;
    position: relative;
    overflow: hidden;
    margin-bottom: 1.5rem;
}
.fc-hero::before {
    content: '';
    position: absolute;
    top: 0; left: 50%;
    transform: translateX(-50%);
    width: 60%;
    height: 1px;
    background: linear-gradient(90deg,
        transparent, var(--accent), transparent);
}
.fc-hero-label {
    font-size: 0.72rem;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.15em;
    margin-bottom: 0.8rem;
}
.fc-hero-value {
    font-size: 3.5rem;
    font-weight: 900;
    letter-spacing: -0.04em;
    line-height: 1;
    margin: 0.4rem 0;
    font-family: var(--font-mono);
    text-shadow: 0 0 15px rgba(16, 185, 129, 0.3) !important;
}
.fc-hero-sub {
    font-size: 0.92rem;
    color: var(--text-muted);
    margin-top: 0.6rem;
}

/* ── ANIMATIONS ─────────────────────────────────────────────────────────────── */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes pulse-glow {
    0%, 100% { box-shadow: 0 0 0 0 rgba(16,185,129,0); }
    50%       { box-shadow: 0 0 12px 3px rgba(16,185,129,0.15); }
}
.fc-animate { animation: fadeInUp 0.4s ease both; }
.fc-pulse   { animation: pulse-glow 2s ease infinite; }

/* ── RESPONSIVE ─────────────────────────────────────────────────────────────── */
@media (max-width: 768px) {
    .main .block-container {
        padding: 1.5rem 1.5rem 3rem !important;
    }
    .fc-hero-value { font-size: 2.2rem; }
    .fc-metric-value { font-size: 1.4rem; }
}

/* ── RADIO BUTTONS ──────────────────────────────────────────────────────────── */
.stRadio [data-testid="stRadioButton"] {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border-light) !important;
    border-radius: var(--radius-sm) !important;
    padding: 0.4rem 0.9rem !important;
    transition: var(--transition) !important;
    color: var(--text-secondary) !important;
    font-family: var(--font) !important;
    font-size: 0.87rem !important;
    font-weight: 500 !important;
}
.stRadio [data-testid="stRadioButton"]:hover {
    border-color: var(--accent) !important;
    color: var(--text-primary) !important;
}
[data-baseweb="radio"][aria-checked="true"] + div {
    color: var(--accent) !important;
}

/* ── MULTISELECT ────────────────────────────────────────────────────────────── */
[data-baseweb="tag"] {
    background: var(--accent-dim) !important;
    border: 1px solid var(--accent) !important;
    border-radius: var(--radius-full) !important;
    color: var(--accent) !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
}

/* ── CHECKBOX ───────────────────────────────────────────────────────────────── */
[data-testid="stCheckbox"] label {
    color: var(--text-secondary) !important;
    font-family: var(--font) !important;
    font-size: 0.88rem !important;
}

/* ── PLOTLY CHARTS ──────────────────────────────────────────────────────────── */
.js-plotly-plot .plotly {
    font-family: var(--font) !important;
}

/* ── SIDEBAR HIDING ─────────────────────────────────────────────────────────── */
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] {
    display: none !important;
}

}
/* 14 — Summary */
div.st-key-top_navigation div[role="radiogroup"] [data-testid="stRadioButton"]:nth-child(14) label::before {
    -webkit-mask-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z'/%3E%3Cpolyline points='14 2 14 8 20 8'/%3E%3Cline x1='16' y1='13' x2='8' y2='13'/%3E%3Cline x1='16' y1='17' x2='8' y2='17'/%3E%3Cpolyline points='10 9 9 9 8 9'/%3E%3C/svg%3E");
    mask-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z'/%3E%3Cpolyline points='14 2 14 8 20 8'/%3E%3Cline x1='16' y1='13' x2='8' y2='13'/%3E%3Cline x1='16' y1='17' x2='8' y2='17'/%3E%3Cpolyline points='10 9 9 9 8 9'/%3E%3C/svg%3E");
}
/* 15 — Settings */
div.st-key-top_navigation div[role="radiogroup"] [data-testid="stRadioButton"]:nth-child(15) label::before {
    -webkit-mask-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='12' cy='12' r='3'/%3E%3Cpath d='M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z'/%3E%3C/svg%3E");
    mask-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='12' cy='12' r='3'/%3E%3Cpath d='M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z'/%3E%3C/svg%3E");
}

/* Tablet responsiveness: Compact size, tight padding */
@media (min-width: 768px) and (max-width: 1200px) {
    div.st-key-top_navigation {
        border-radius: 20px !important;
        padding: 3px 6px !important;
    }
    div.st-key-top_navigation div[role="radiogroup"] label {
        padding: 5px 8px !important;
        font-size: 0.72rem !important;
        gap: 3px !important;
    }
    div.st-key-top_navigation div[role="radiogroup"] label::before {
        width: 10px;
        height: 10px;
        margin-right: 1px !important;
    }
}

/* Mobile responsiveness: Horizontally scrollable navbar */
@media (max-width: 767px) {
    div.st-key-top_navigation {
        border-radius: 16px !important;
        padding: 4px 6px !important;
    }
    div.st-key-top_navigation div[role="radiogroup"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        overflow-x: auto !important;
        justify-content: flex-start !important;
        gap: 6px !important;
        padding: 2px !important;
        -webkit-overflow-scrolling: touch !important;
    }
    div.st-key-top_navigation div[role="radiogroup"]::-webkit-scrollbar {
        display: none !important;
    }
    div.st-key-top_navigation div[role="radiogroup"] label {
        flex: 0 0 auto !important;
        padding: 5px 8px !important;
        font-size: 0.7rem !important;
        gap: 3px !important;
    }
    div.st-key-top_navigation div[role="radiogroup"] label::before {
        width: 10px;
        height: 10px;
        margin-right: 1px !important;
    }
}

/* ── STICKY GLASSMORPHIC HEADER & ANIMATED LOGO ───────────────────────────── */
div.st-key-global_header {
    position: sticky !important;
    top: 0 !important;
    z-index: 999 !important;
    background: rgba(13, 18, 36, 0.65) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border-bottom: 1px solid var(--border) !important;
    padding: 1rem 3rem !important;
    margin-left: -3rem !important;
    margin-right: -3rem !important;
    margin-top: -2.5rem !important;
    margin-bottom: 2rem !important;
}

.fc-logo-container {
    display: flex;
    align-items: center;
    gap: 12px;
}

.fc-logo-container svg path[fill*="green-teal"] {
    filter: drop-shadow(0 0 10px rgba(0, 242, 168, 0.8)) !important;
}

.fc-logo-glowing {
    font-family: var(--font) !important;
    font-size: 1.5rem !important;
    font-weight: 900 !important;
    letter-spacing: -0.03em !important;
    text-transform: uppercase;
    background: linear-gradient(135deg, #00F2A8, #00D4FF, #6366F1, #00F2A8);
    background-size: 300% auto;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    display: inline-block;
    position: relative;
    animation: shine 6s linear infinite;
    filter: drop-shadow(0 0 8px rgba(0, 242, 168, 0.4));
}

@keyframes shine {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* Style selectbox inside sticky header */
div.st-key-global_header div[data-testid="stSelectbox"] > div > div {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border-light) !important;
    border-radius: var(--radius-sm) !important;
    height: 38px !important;
    display: flex !important;
    align-items: center !important;
}

div.st-key-global_header div[data-testid="stSelectbox"] div[role="combobox"] {
    padding-top: 0 !important;
    padding-bottom: 0 !important;
    height: 36px !important;
    line-height: 36px !important;
    display: inline-flex !important;
    align-items: center !important;
}

/* Style alerts, profile, and logout buttons inside sticky header */
div.st-key-alerts_button button, div.st-key-alerts_button_unread button, div.st-key-profile_button button, div.st-key-logout_button button {
    height: 38px !important;
    font-size: 0.82rem !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 4px !important;
    padding: 0 !important;
    width: 100% !important;
}

div.st-key-alerts_button button::before, div.st-key-alerts_button_unread button::before {
    content: '';
    display: inline-block;
    width: 24px !important;
    height: 24px !important;
    min-width: 24px !important;
    min-height: 24px !important;
    flex-shrink: 0 !important;
    background-color: var(--text-secondary);
    -webkit-mask: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9'/%3E%3Cpath d='M13.73 21a2 2 0 0 1-3.46 0'/%3E%3C/svg%3E") no-repeat center;
    mask: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9'/%3E%3Cpath d='M13.73 21a2 2 0 0 1-3.46 0'/%3E%3C/svg%3E") no-repeat center;
    -webkit-mask-size: contain;
    mask-size: contain;
}

div.st-key-alerts_button_unread button::after {
    content: '';
    position: absolute;
    top: 5px;
    right: calc(50% - 10px);
    width: 8px;
    height: 8px;
    background-color: #00F2A8;
    border-radius: 50%;
    box-shadow: 0 0 8px #00F2A8;
}

div.st-key-profile_button button {
    background: rgba(255, 255, 255, 0.03) !important;
    border: 1px solid var(--border-light) !important;
    color: var(--text-secondary) !important;
    border-radius: var(--radius-sm) !important;
    transition: var(--transition) !important;
}

div.st-key-profile_button button:hover {
    background: rgba(0, 242, 168, 0.05) !important;
    border-color: var(--accent) !important;
    color: var(--accent) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 0 15px rgba(0, 242, 168, 0.15) !important;
}

div.st-key-profile_button button::before {
    content: '';
    display: inline-block;
    width: 24px !important;
    height: 24px !important;
    min-width: 24px !important;
    min-height: 24px !important;
    flex-shrink: 0 !important;
    background-color: var(--text-secondary);
    -webkit-mask: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2'/%3E%3Ccircle cx='12' cy='7' r='4'/%3E%3C/svg%3E") no-repeat center;
    mask: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2'/%3E%3Ccircle cx='12' cy='7' r='4'/%3E%3C/svg%3E") no-repeat center;
    -webkit-mask-size: contain;
    mask-size: contain;
    transition: var(--transition);
}

div.st-key-profile_button button:hover::before {
    background-color: var(--accent) !important;
}

div.st-key-logout_button button {
    background: transparent !important;
    border: 1px solid var(--danger) !important;
    color: var(--danger) !important;
    transition: var(--transition) !important;
}

div.st-key-logout_button button:hover {
    background: var(--danger-dim) !important;
    box-shadow: 0 0 15px rgba(239, 68, 68, 0.35) !important;
    transform: translateY(-2px) !important;
}

div.st-key-logout_button button::before {
    content: '';
    display: inline-block;
    width: 24px !important;
    height: 24px !important;
    min-width: 24px !important;
    min-height: 24px !important;
    flex-shrink: 0 !important;
    background-color: var(--danger);
    -webkit-mask: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4'/%3E%3Cpolyline points='16 17 21 12 16 7'/%3E%3Cline x1='21' y1='12' x2='9' y2='12'/%3E%3C/svg%3E") no-repeat center;
    mask: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4'/%3E%3Cpolyline points='16 17 21 12 16 7'/%3E%3Cline x1='21' y1='12' x2='9' y2='12'/%3E%3C/svg%3E") no-repeat center;
    -webkit-mask-size: contain;
    mask-size: contain;
}

/* Glassmorphic Login Panel */
div.st-key-login_panel {
    background: rgba(15, 22, 45, 0.45) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-lg) !important;
    padding: 2rem 2.2rem !important;
    box-shadow: var(--shadow-lg), 0 0 40px rgba(0, 0, 0, 0.25) !important;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
}

/* Premium tab selection pill selector override */
div.st-key-login_panel .stTabs [data-baseweb="tab-list"] {
    background: rgba(11, 15, 26, 0.6) !important;
    border-radius: 999px !important;
    padding: 4px !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    margin-bottom: 1rem !important;
    display: flex !important;
    justify-content: space-between !important;
}
div.st-key-login_panel .stTabs [data-baseweb="tab"] {
    color: #8B8FA8 !important;
    border-radius: 999px !important;
    padding: 8px 24px !important;
    font-weight: 700 !important;
    background: transparent !important;
    border: none !important;
    transition: var(--transition) !important;
    flex-grow: 1 !important;
    text-align: center !important;
}
div.st-key-login_panel .stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #00F2A8, #00D4FF) !important;
    color: #0B0F1A !important;
    box-shadow: 0 4px 15px rgba(0, 242, 168, 0.25) !important;
}

/* Custom premium input focus states inside the login panel */
div.st-key-login_panel div[data-testid="stTextInput"] input {
    background: rgba(26, 29, 39, 0.6) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    color: #FFFFFF !important;
    border-radius: 8px !important;
    padding: 10px 14px !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
div.st-key-login_panel div[data-testid="stTextInput"] input:focus {
    border-color: #00D4FF !important;
    box-shadow: 0 0 15px rgba(0, 212, 255, 0.25) !important;
}

/* Inline warning errors style */
.field-error-msg {
    color: #EF4444;
    font-size: 0.76rem;
    margin-top: 4px;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 4px;
    animation: fadeIn 0.2s ease;
}

/* Gradient fintech buttons in login panel */
div.st-key-login_panel button[type="submit"], div.st-key-login_panel button[kind="primary"] {
    background: linear-gradient(135deg, #00F2A8, #00D4FF) !important;
    color: #0B0F1A !important;
    border: none !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    border-radius: var(--radius-md) !important;
    box-shadow: 0 4px 15px rgba(0, 242, 168, 0.3) !important;
    transition: var(--transition) !important;
    height: 44px !important;
}

div.st-key-login_panel button[type="submit"]:hover, div.st-key-login_panel button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(0, 242, 168, 0.5), 0 0 15px rgba(0, 242, 168, 0.2) !important;
    color: #0B0F1A !important;
}

/* Password checklist styles */
.validation-check {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 6px;
    font-size: 0.78rem;
    font-weight: 500;
    transition: color 0.3s ease;
}
.validation-check.valid {
    color: #00F2A8 !important;
}
.validation-check.invalid {
    color: #EF4444 !important;
}
.validation-check::before {
    content: '';
    display: inline-block;
    width: 14px;
    height: 14px;
    border-radius: 50%;
    background-size: 60% 60%;
    background-repeat: no-repeat;
    background-position: center;
    transition: all 0.3s ease;
    flex-shrink: 0;
}
.validation-check.valid::before {
    background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%230B0F1A' stroke-width='4' stroke-linecap='round' stroke-linejoin='round'><polyline points='20 6 9 17 4 12'/></svg>");
    background-color: #00F2A8;
    box-shadow: 0 0 8px rgba(0, 242, 168, 0.4);
}
.validation-check.invalid::before {
    background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23FFFFFF' stroke-width='4' stroke-linecap='round' stroke-linejoin='round'><line x1='18' y1='6' x2='6' y2='18'/><line x1='6' y1='6' x2='18' y2='18'/></svg>");
    background-color: #EF4444;
}

/* Lockout state container */
.lockout-panel {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 1.5rem 1rem;
    animation: fadeIn 0.4s ease;
}
.lockout-shield-icon {
    width: 56px;
    height: 56px;
    background-color: #EF4444;
    -webkit-mask: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z'/%3E%3C/svg%3E") no-repeat center;
    mask: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z'/%3E%3C/svg%3E") no-repeat center;
    -webkit-mask-size: contain;
    mask-size: contain;
    filter: drop-shadow(0 0 15px rgba(239, 68, 68, 0.4));
    margin-bottom: 1.2rem;
}
.lockout-timer {
    font-size: 2.2rem;
    font-weight: 800;
    font-family: var(--font-mono) !important;
    color: #FFB347;
    margin: 0.8rem 0;
    text-shadow: 0 0 10px rgba(255, 179, 71, 0.3);
}

/* 2FA Panel styling */
.otp-badge {
    display: inline-block;
    background: rgba(0, 212, 255, 0.1);
    border: 1px solid rgba(0, 212, 255, 0.2);
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 0.8rem;
    color: #00D4FF;
    margin-bottom: 1.2rem;
    font-weight: 600;
}

/* Feature grid for Login page */
.login-feature-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-bottom: 2.5rem;
}
.login-feature-card {
    display: flex;
    align-items: center;
    gap: 12px;
    background: rgba(17, 24, 48, 0.4) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md);
    padding: 14px 16px;
    transition: var(--transition);
}
.login-feature-card:hover {
    background: var(--bg-card-hover) !important;
    border-color: var(--accent) !important;
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 242, 168, 0.06);
}
.feature-icon {
    width: 20px;
    height: 20px;
    background-color: var(--accent);
    -webkit-mask-size: contain;
    mask-size: contain;
    -webkit-mask-repeat: no-repeat;
    mask-repeat: no-repeat;
    -webkit-mask-position: center;
    mask-position: center;
}
.dashboard-icon {
    -webkit-mask-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='3' y='3' width='7' height='9'/%3E%3Crect x='14' y='3' width='7' height='5'/%3E%3Crect x='14' y='12' width='7' height='9'/%3E%3Crect x='3' y='16' width='7' height='5'/%3E%3C/svg%3E");
}
.anomaly-icon {
    -webkit-mask-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z'/%3E%3Cline x1='12' y1='9' x2='12' y2='13'/%3E%3Cline x1='12' y1='17' x2='12.01' y2='17'/%3E%3C/svg%3E");
}
.budget-icon {
    -webkit-mask-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M21.21 15.89A10 10 0 1 1 8 2.83'/%3E%3Cpath d='M22 12A10 10 0 0 0 12 2v10z'/%3E%3C/svg%3E");
}
.coach-icon {
    -webkit-mask-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z'/%3E%3C/svg%3E");
}
.health-icon {
    -webkit-mask-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='22 12 18 12 15 21 9 3 6 12 2 12'/%3E%3C/svg%3E");
}
.reports-icon {
    -webkit-mask-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z'/%3E%3Cpolyline points='14 2 14 8 20 8'/%3E%3Cline x1='16' y1='13' x2='8' y2='13'/%3E%3Cline x1='16' y1='17' x2='8' y2='17'/%3E%3Cpolyline points='10 9 9 9 8 9'/%3E%3C/svg%3E");
}
.feature-label {
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--text-primary);
}

/* Trust container for Login page */
.login-trust-container {
    display: flex;
    gap: 2.2rem;
    margin-top: 2.5rem;
}
.login-trust-badge {
    display: flex;
    align-items: center;
    gap: 8px;
}
.login-trust-badge span {
    font-size: 0.8rem;
    font-weight: 500;
    color: var(--text-secondary);
}
.trust-icon {
    width: 16px;
    height: 16px;
    background-color: var(--text-muted);
    -webkit-mask-size: contain;
    mask-size: contain;
    -webkit-mask-repeat: no-repeat;
    mask-repeat: no-repeat;
    transition: var(--transition);
}
.login-trust-badge:hover .trust-icon {
    background-color: var(--accent);
}
.shield-icon {
    -webkit-mask-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z'/%3E%3C/svg%3E");
}
.lock-icon {
    -webkit-mask-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='3' y='11' width='18' height='11' rx='2' ry='2'/%3E%3Cpath d='M7 11V7a5 5 0 0 1 10 0v4'/%3E%3C/svg%3E");
}
.sparkles-icon {
    -webkit-mask-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z'/%3E%3C/svg%3E");
}
</style>

"""


import re

_LOGO_FULL_RAW = """<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 520 130' width='100%' height='100%'>
  <defs>
    <linearGradient id='lyt-grad' x1='0%' y1='0%' x2='100%' y2='0%'>
      <stop offset='0%' stop-color='#00F2A8' />
      <stop offset='100%' stop-color='#00D4FF' />
    </linearGradient>
    <filter id='glow-logo'>
      <feGaussianBlur stdDeviation='4' result='blur' />
      <feComposite in='SourceGraphic' in2='blur' operator='over' />
    </filter>
  </defs>
  <image href='data:image/png;base64,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'
         x='4' y='3' width='118' height='124'
         preserveAspectRatio='xMidYMid meet' />
  <text x='138' y='72'
        font-family="'Outfit','Inter','system-ui',sans-serif"
        font-size='58' font-weight='900' letter-spacing='2'
        fill='#FFFFFF'>FINE</text>
  <text x='280' y='72'
        font-family="'Outfit','Inter','system-ui',sans-serif"
        font-size='58' font-weight='900' letter-spacing='2'
        fill='url(#lyt-grad)' filter='url(#glow-logo)'>LYT</text>
  <text x='140' y='103'
        font-family="'Outfit','Inter','system-ui',sans-serif"
        font-size='13.5' font-weight='700' letter-spacing='5.5'
        fill='#94A3B8' opacity='0.8'>AI PERSONAL FINANCE COACH</text>
</svg>"""

_LOGO_ICON_RAW = """<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 110 110' width='100%' height='100%'>
  <image href='data:image/png;base64,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'
         x='5' y='5' width='100' height='100'
         preserveAspectRatio='xMidYMid meet' />
</svg>"""

# Programmatically clean SVG strings for Streamlit compatibility (removes comments and joins into a single compact line)
def _clean_svg(svg_raw):
    clean = re.sub(r'<!--.*?-->', '', svg_raw, flags=re.DOTALL)
    return " ".join([line.strip() for line in clean.splitlines() if line.strip()])

LOGO_FULL_SVG = _clean_svg(_LOGO_FULL_RAW)
LOGO_ICON_SVG = _clean_svg(_LOGO_ICON_RAW)
