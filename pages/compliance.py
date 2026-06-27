import streamlit as st

def show(user_id=1):
    st.markdown("""
    <style>
    .page-title { font-size: 2rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0; }
    .page-sub { font-size: 1rem; color: var(--text-secondary); margin-bottom: 1.5rem; }
    .c-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    .timeline-item {
        border-left: 2px solid var(--accent);
        margin-left: 20px;
        padding-left: 20px;
        position: relative;
        padding-bottom: 1.5rem;
    }
    .timeline-item::before {
        content: '';
        position: absolute;
        left: -6px;
        top: 4px;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background-color: var(--accent);
        border: 2px solid var(--bg-surface);
    }
    .timeline-title { font-weight: 700; color: var(--text-primary); font-size: 0.95rem; margin-bottom: 4px; }
    .timeline-date { font-size: 0.78rem; color: var(--accent); font-weight: 600; text-transform: uppercase; margin-bottom: 6px; }
    .timeline-desc { font-size: 0.85rem; color: var(--text-secondary); line-height: 1.4; }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<p class="page-title">Compliance & Security Dashboard</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">Understand FINELYT\'s secure infrastructure, data encryption pipeline, and regulatory compliance roadmap.</p>', unsafe_allow_html=True)
    st.divider()
    
    c_sec, c_road = st.columns([1.1, 0.9])
    
    with c_sec:
        st.markdown("<p style='font-weight:700; font-size:1.1rem; color:var(--text-primary); margin-bottom:1rem;'>Platform Security Architecture</p>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="c-card">
            <h5 style="color:var(--accent); margin:0 0 0.5rem 0;">🛡 Data Encryption Standard</h5>
            <p style="font-size:0.88rem; color:var(--text-secondary); line-height:1.5; margin:0;">
                All sensitive user transaction records, income details, and credentials are encrypted at rest using <strong>AES-256 GCM</strong>. Decryption keys are stored separately in locked environment variables.
            </p>
        </div>
        <div class="c-card">
            <h5 style="color:#3B82F6; margin:0 0 0.5rem 0;">🔑 HMAC Signed Sessions</h5>
            <p style="font-size:0.88rem; color:var(--text-secondary); line-height:1.5; margin:0;">
                To prevent session hijacking or query-parameter tampering, FINELYT tokens are cryptographically signed using <strong>HMAC-SHA256</strong> with a secure server-level private key.
            </p>
        </div>
        <div class="c-card">
            <h5 style="color:#10B981; margin:0 0 0.5rem 0;">🔐 Two-Factor Authentication (2FA)</h5>
            <p style="font-size:0.88rem; color:var(--text-secondary); line-height:1.5; margin:0;">
                User identity validation is enforced on every single sign-in flow by requesting a temporary 6-digit OTP code sent directly via SMTP secure mailing protocols.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with c_road:
        st.markdown("<p style='font-weight:700; font-size:1.1rem; color:var(--text-primary); margin-bottom:1rem;'>Compliance Roadmap</p>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="timeline-item">
            <div class="timeline-date">Phase 1: Completed</div>
            <div class="timeline-title">GDPR Data Privacy Enforcement</div>
            <div class="timeline-desc">Implemented fully sandboxed databases, end-to-end account deletion pipelines (wiping all transactions, budgets, settings, and login logs), and cookie consent.</div>
        </div>
        <div class="timeline-item">
            <div class="timeline-date">Phase 2: In Progress</div>
            <div class="timeline-title">PCI-DSS compliance</div>
            <div class="timeline-desc">Establishing secure key storage guidelines, implementing TLS 1.3 transmission for API networks, and separating card/banking indicators.</div>
        </div>
        <div class="timeline-item">
            <div class="timeline-date">Phase 3: Q3 2026</div>
            <div class="timeline-title">ISO 27001 Standards & SOC2 audit</div>
            <div class="timeline-desc">Drafting formal risk management profiles, logging internal access pipelines, and completing vulnerability pen-testing audits.</div>
        </div>
        <div class="timeline-item" style="padding-bottom:0;">
            <div class="timeline-date">Phase 4: Q4 2026</div>
            <div class="timeline-title">RBI Account Aggregator (AA) Integration</div>
            <div class="timeline-desc">Connecting RBI-approved AA frameworks to safely and programmatically retrieve structured bank balances without requesting user netbanking credentials.</div>
        </div>
        """, unsafe_allow_html=True)
