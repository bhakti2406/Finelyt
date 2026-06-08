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

_LOGO_FULL_RAW = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 130" width="100%" height="100%">
  <defs>
    <!-- Green to Teal gradient for the F canopy -->
    <linearGradient id="finelyt-green-teal" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#00F2A8" />
      <stop offset="100%" stop-color="#00D4FF" />
    </linearGradient>
    <!-- Blue to Teal gradient for the growth bars -->
    <linearGradient id="finelyt-blue-teal" x1="0%" y1="100%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#3B82F6" />
      <stop offset="50%" stop-color="#00D4FF" />
      <stop offset="100%" stop-color="#00F2A8" />
    </linearGradient>
    <!-- Gradient for the LYT text -->
    <linearGradient id="lyt-grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#00F2A8" />
      <stop offset="100%" stop-color="#00D4FF" />
    </linearGradient>
    <!-- Filter for soft glow effect -->
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="6" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over" />
    </filter>
  </defs>

  <!-- Group for Logo Icon -->
  <g transform="translate(15, 10)">
    <!-- 1. The F Canopy (Sweeping wing-like design with 45-degree diagonal cut at bottom) -->
    <path d="M 20 71 
             V 26 
             C 20 15, 28 12, 38 12 
             C 55 10, 75 10, 94 12 
             C 94 12, 80 22, 42 22 
             C 34 22, 30 26, 30 32 
             C 30 32, 50 32, 68 34 
             C 68 34, 52 42, 30 42 
             V 61 
             L 20 71 
             Z" 
          fill="url(#finelyt-green-teal)" />

    <!-- 2. Separate Growth Bars (Flat bottoms, rounded tops) -->
    <path d="M 20 90 V 78 A 3 3 0 0 1 26 78 V 90 Z" fill="url(#finelyt-blue-teal)" />
    <path d="M 29 90 V 66 A 3 3 0 0 1 35 66 V 90 Z" fill="url(#finelyt-blue-teal)" />

    <!-- 3. Trendline Arrow (Starts as Bar 3, turns right, dips, and shoots up-right) -->
    <path d="M 41 90 
             V 61 
             H 49 
             V 69 
             L 78 40" 
          fill="none" 
          stroke="url(#finelyt-blue-teal)" 
          stroke-width="6" 
          stroke-linecap="round" 
          stroke-linejoin="round" />
    
    <!-- Arrowhead (Solid triangle pointing up-right) -->
    <polygon points="86,32 72,34 84,46" fill="url(#finelyt-green-teal)" />
  </g>

  <!-- Group for Logo Text -->
  <g transform="translate(135, 12)">
    <!-- FINE (White text) -->
    <text x="0" y="65" 
          font-family="'Outfit', 'Inter', 'system-ui', sans-serif" 
          font-size="58" 
          font-weight="900" 
          letter-spacing="2" 
          fill="#FFFFFF">FINE</text>
    <!-- LYT (Gradient text) -->
    <text x="142" y="65" 
          font-family="'Outfit', 'Inter', 'system-ui', sans-serif" 
          font-size="58" 
          font-weight="900" 
          letter-spacing="2" 
          fill="url(#lyt-grad)" 
          filter="url(#glow)">LYT</text>
    <!-- Subheading -->
    <text x="3" y="96" 
          font-family="'Outfit', 'Inter', 'system-ui', sans-serif" 
          font-size="13.5" 
          font-weight="700" 
          letter-spacing="5.5" 
          fill="#94A3B8" 
          opacity="0.8">AI PERSONAL FINANCE COACH</text>
  </g>
</svg>"""

_LOGO_ICON_RAW = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 110 110" width="100%" height="100%">
  <defs>
    <!-- Green to Teal gradient for the F canopy -->
    <linearGradient id="finelyt-green-teal-icon" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#00F2A8" />
      <stop offset="100%" stop-color="#00D4FF" />
    </linearGradient>
    <!-- Blue to Teal gradient for the growth bars -->
    <linearGradient id="finelyt-blue-teal-icon" x1="0%" y1="100%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#3B82F6" />
      <stop offset="50%" stop-color="#00D4FF" />
      <stop offset="100%" stop-color="#00F2A8" />
    </linearGradient>
  </defs>

  <!-- Group for Logo Icon (translated to center the 74x80 icon in the 110x110 viewBox) -->
  <g transform="translate(-2, 5)">
    <!-- 1. The F Canopy -->
    <path d="M 20 71 
             V 26 
             C 20 15, 28 12, 38 12 
             C 55 10, 75 10, 94 12 
             C 94 12, 80 22, 42 22 
             C 34 22, 30 26, 30 32 
             C 30 32, 50 32, 68 34 
             C 68 34, 52 42, 30 42 
             V 61 
             L 20 71 
             Z" 
          fill="url(#finelyt-green-teal-icon)" />

    <!-- 2. Growth Bars -->
    <path d="M 20 90 V 78 A 3 3 0 0 1 26 78 V 90 Z" fill="url(#finelyt-blue-teal-icon)" />
    <path d="M 29 90 V 66 A 3 3 0 0 1 35 66 V 90 Z" fill="url(#finelyt-blue-teal-icon)" />

    <!-- 3. Trendline Arrow -->
    <path d="M 41 90 
             V 61 
             H 49 
             V 69 
             L 78 40" 
          fill="none" 
          stroke="url(#finelyt-blue-teal-icon)" 
          stroke-width="6" 
          stroke-linecap="round" 
          stroke-linejoin="round" />
    
    <!-- Arrowhead -->
    <polygon points="86,32 72,34 84,46" fill="url(#finelyt-green-teal-icon)" />
  </g>
</svg>"""

# Programmatically clean SVG strings for Streamlit compatibility (removes comments and joins into a single compact line)
def _clean_svg(svg_raw):
    clean = re.sub(r'<!--.*?-->', '', svg_raw, flags=re.DOTALL)
    return " ".join([line.strip() for line in clean.splitlines() if line.strip()])

LOGO_FULL_SVG = _clean_svg(_LOGO_FULL_RAW)
LOGO_ICON_SVG = _clean_svg(_LOGO_ICON_RAW)
