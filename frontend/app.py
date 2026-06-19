import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd
from io import BytesIO

API_URL = st.secrets.get("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Xeno Validator",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---- Global CSS ----
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg: #F7F7F5;
    --surface: #FFFFFF;
    --sidebar-bg: #111111;
    --accent: #E63946;
    --accent-dim: #7a1f26;
    --text-primary: #0F0F0F;
    --text-secondary: #555555;
    --text-muted: #999999;
    --text-faint: #BBBBBB;
    --border: #E2E2E0;
    --border-dark: #1F1F1F;
    --pass: #2A7A2A;
    --fail: #E63946;
    --row-alt: #F3F3F1;
    --font-sans: 'Inter', 'Helvetica Neue', Arial, sans-serif;
    --font-mono: 'JetBrains Mono', 'Fira Mono', 'Courier New', monospace;
}

/* Reset & Base */
html, body, [class*="css"] {
    font-family: var(--font-sans) !important;
    background-color: var(--bg) !important;
}

#MainMenu, footer, header, .stDeployButton { visibility: hidden; display: none; }
.block-container { padding: 0 !important; max-width: 100% !important; }
.stApp { background-color: var(--bg) !important; }

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: var(--sidebar-bg) !important;
    border-right: 1px solid var(--border-dark) !important;
    padding: 0 !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 28px 20px 20px 20px !important;
}
[data-testid="stSidebar"] * {
    color: #CCCCCC !important;
    font-family: var(--font-sans) !important;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stNumberInput label,
[data-testid="stSidebar"] .stCheckbox label {
    font-size: 9px !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: #666666 !important;
    font-weight: 500 !important;
    margin-bottom: 4px !important;
}
[data-testid="stSidebar"] .stSelectbox > div > div {
    background-color: #1A1A1A !important;
    border: 1px solid #2A2A2A !important;
    border-radius: 0 !important;
    color: #CCCCCC !important;
    font-size: 12px !important;
    font-family: var(--font-mono) !important;
}
[data-testid="stSidebar"] .stNumberInput > div > div > input {
    background-color: #1A1A1A !important;
    border: 1px solid #2A2A2A !important;
    border-radius: 0 !important;
    color: #CCCCCC !important;
    font-size: 12px !important;
    font-family: var(--font-mono) !important;
}
[data-testid="stSidebar"] .stCheckbox > label {
    font-size: 11px !important;
    letter-spacing: 0.04em !important;
    text-transform: none !important;
    color: #AAAAAA !important;
}
[data-testid="stSidebar"] hr {
    border-color: var(--border-dark) !important;
    margin: 16px 0 !important;
}

/* Main content */
.main-wrapper {
    padding: 0;
    min-height: 100vh;
}

/* Top bar */
.top-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 18px 36px 17px 36px;
    border-bottom: 1px solid var(--border);
    background: var(--surface);
    position: sticky;
    top: 0;
    z-index: 100;
}
.top-bar-title {
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.04em;
    color: var(--text-primary);
    text-transform: uppercase;
}
.api-status {
    display: flex;
    align-items: center;
    gap: 7px;
    font-family: var(--font-mono);
    font-size: 9px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
.api-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
}
.api-dot.online { background: #2A7A2A; }
.api-dot.offline { background: var(--accent); }
.api-status.online { color: #2A7A2A; }
.api-status.offline { color: var(--accent); }

/* Page content padding */
.page-content {
    padding: 36px 36px 60px 36px;
}

/* Section labels */
.section-label {
    font-size: 9px;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 14px;
    margin-top: 0;
}

/* File drop zone */
.drop-hint {
    border: 1px dashed #C8C8C4;
    background: var(--surface);
    padding: 48px 36px;
    text-align: center;
    margin-bottom: 24px;
}
.drop-hint p {
    font-size: 12px;
    color: var(--text-muted);
    margin: 0;
    letter-spacing: 0.02em;
}

/* Hide default file uploader label and style the widget */
[data-testid="stFileUploader"] {
    background: var(--surface) !important;
    border: 1px dashed #C8C8C4 !important;
    border-radius: 0 !important;
    padding: 0 !important;
}
[data-testid="stFileUploader"] label { display: none !important; }
[data-testid="stFileUploader"] > div {
    padding: 40px 36px !important;
    text-align: center !important;
}
[data-testid="stFileUploader"] small {
    font-family: var(--font-mono) !important;
    font-size: 10px !important;
    color: var(--text-muted) !important;
}
[data-testid="stFileUploader"] svg { display: none !important; }

/* Data preview table */
.preview-meta {
    font-family: var(--font-mono);
    font-size: 10px;
    color: var(--text-muted);
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 10px;
}
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: 0 !important;
}
[data-testid="stDataFrame"] th {
    font-family: var(--font-sans) !important;
    font-size: 9px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    color: var(--text-muted) !important;
    font-weight: 500 !important;
    background: var(--row-alt) !important;
}
[data-testid="stDataFrame"] td {
    font-family: var(--font-mono) !important;
    font-size: 11px !important;
    color: var(--text-primary) !important;
}

/* Run button */
.stButton > button {
    width: 100% !important;
    background: var(--text-primary) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 0 !important;
    font-family: var(--font-sans) !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    padding: 14px 24px !important;
    cursor: pointer !important;
    transition: background 0.15s ease !important;
    margin-top: 20px !important;
}
.stButton > button:hover {
    background: #333333 !important;
}
.stButton > button:active {
    background: var(--accent) !important;
}

/* Stat bar */
.stat-bar {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    border: 1px solid var(--border);
    background: var(--surface);
    margin-bottom: 32px;
}
.stat-item {
    padding: 24px 28px;
    border-right: 1px solid var(--border);
}
.stat-item:last-child { border-right: none; }
.stat-number {
    font-size: 32px;
    font-weight: 700;
    color: var(--text-primary);
    font-family: var(--font-sans);
    line-height: 1;
    margin-bottom: 6px;
}
.stat-number.accent { color: var(--accent); }
.stat-number.pass { color: var(--pass); }
.stat-label {
    font-size: 9px;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-muted);
}

/* Validator results table */
.validator-table {
    width: 100%;
    border-collapse: collapse;
    border: 1px solid var(--border);
    background: var(--surface);
    margin-bottom: 24px;
}
.validator-table th {
    font-size: 9px;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-muted);
    padding: 10px 16px;
    text-align: left;
    background: var(--row-alt);
    border-bottom: 1px solid var(--border);
}
.validator-table th:last-child { text-align: right; }
.validator-table td {
    padding: 13px 16px;
    font-size: 12px;
    color: var(--text-primary);
    border-bottom: 1px solid var(--border);
    vertical-align: middle;
}
.validator-table td:last-child {
    text-align: right;
    font-family: var(--font-mono);
    font-size: 11px;
    color: var(--text-muted);
}
.validator-table tr:last-child td { border-bottom: none; }
.status-pass {
    font-family: var(--font-mono);
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 0.08em;
    color: var(--pass);
}
.status-fail {
    font-family: var(--font-mono);
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 0.08em;
    color: var(--fail);
}
.worker-name {
    font-size: 12px;
    font-weight: 500;
    color: var(--text-primary);
}

/* Error detail tables */
.error-section {
    margin-bottom: 16px;
    border: 1px solid var(--border);
    background: var(--surface);
}
.error-section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 11px 16px;
    background: var(--row-alt);
    border-bottom: 1px solid var(--border);
    cursor: pointer;
}
.error-section-title {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text-primary);
}
.error-count-badge {
    font-family: var(--font-mono);
    font-size: 10px;
    color: var(--accent);
}
.error-table {
    width: 100%;
    border-collapse: collapse;
}
.error-table th {
    font-size: 9px;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-muted);
    padding: 8px 16px;
    text-align: left;
    border-bottom: 1px solid var(--border);
    background: var(--surface);
}
.error-table td {
    padding: 9px 16px;
    font-family: var(--font-mono);
    font-size: 11px;
    color: var(--text-primary);
    border-bottom: 1px solid var(--border);
}
.error-table tr:last-child td { border-bottom: none; }
.error-table tr:nth-child(even) td { background: #FAFAF8; }
.error-reason { color: var(--text-secondary) !important; font-size: 10px !important; }

/* Output files section */
.output-files {
    background: var(--surface);
    border: 1px solid var(--border);
}
.output-file-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 13px 16px;
    border-bottom: 1px solid var(--border);
}
.output-file-row:last-child { border-bottom: none; }
.output-filename {
    font-family: var(--font-mono);
    font-size: 11px;
    color: var(--text-primary);
}
.output-meta {
    font-family: var(--font-mono);
    font-size: 10px;
    color: var(--text-muted);
}

/* Download buttons inside output section */
.stDownloadButton > button {
    background: transparent !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 0 !important;
    font-family: var(--font-mono) !important;
    font-size: 10px !important;
    font-weight: 400 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    padding: 6px 14px !important;
    margin-top: 0 !important;
}
.stDownloadButton > button:hover {
    background: var(--text-primary) !important;
    color: #FFFFFF !important;
    border-color: var(--text-primary) !important;
}

/* Divider */
.section-divider {
    height: 1px;
    background: var(--border);
    margin: 32px 0;
}

/* Empty state */
.empty-state {
    padding: 60px 36px;
    text-align: center;
}
.empty-state-title {
    font-size: 13px;
    font-weight: 500;
    color: var(--text-primary);
    margin-bottom: 8px;
}
.empty-state-sub {
    font-size: 11px;
    color: var(--text-muted);
    font-family: var(--font-mono);
    line-height: 1.8;
}

/* Processing status */
.processing-bar {
    background: var(--surface);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    padding: 14px 18px;
    margin-bottom: 16px;
    font-size: 11px;
    color: var(--text-secondary);
    font-family: var(--font-mono);
    letter-spacing: 0.04em;
}

/* Error alert */
.error-alert {
    background: #FFF5F5;
    border: 1px solid #FFCCCC;
    border-left: 3px solid var(--accent);
    padding: 14px 18px;
    font-size: 11px;
    color: #7A1F1F;
    font-family: var(--font-mono);
}

/* Spinner override */
.stSpinner > div {
    border-top-color: var(--accent) !important;
}

/* Expander styling */
.streamlit-expanderHeader {
    background: #0F0F0F !important;
    border: 2px solid #0F0F0F !important;
    border-radius: 0 !important;
    font-size: 12px !important;
    font-weight: 700 !important;
    font-family: var(--font-sans) !important;
    color: #FFFFFF !important;
    padding: 14px 16px !important;
    cursor: pointer !important;
    margin-bottom: 8px !important;
}
.streamlit-expanderHeader svg {
    fill: #FFFFFF !important;
    opacity: 1 !important;
    visibility: visible !important;
    display: inline-block !important;
}
[data-testid="stExpander"] {
    border: none !important;
}
[data-testid="stExpander"] details {
    border: none !important;
}
[data-testid="stExpander"] details summary {
    opacity: 1 !important;
    background: #0F0F0F !important;
    border: 2px solid #0F0F0F !important;
    border-radius: 0 !important;
    font-size: 12px !important;
    font-weight: 700 !important;
    color: #FFFFFF !important;
    padding: 14px 16px !important;
    list-style: none !important;
    display: flex !important;
    align-items: center !important;
    cursor: pointer !important;
}
[data-testid="stExpander"] details summary::-webkit-details-marker {
    display: none !important;
}
[data-testid="stExpander"] details summary::marker {
    display: none !important;
}
[data-testid="stExpander"] details summary svg {
    fill: #FFFFFF !important;
    opacity: 1 !important;
    visibility: visible !important;
    display: inline-block !important;
    width: 16px !important;
    height: 16px !important;
    margin-right: 8px !important;
    flex-shrink: 0 !important;
}
[data-testid="stExpander"] details[open] summary svg {
    transform: rotate(90deg) !important;
}
/* Force visibility on all possible selectors */
[data-testid="stExpander"] svg,
[data-testid="stExpander"] summary svg,
.streamlit-expanderHeader svg,
details summary svg {
    opacity: 1 !important;
    visibility: visible !important;
    display: inline-block !important;
}
</style>
""", unsafe_allow_html=True)


# ---- API Health Check ----
def check_api():
    try:
        r = requests.get(f"{API_URL}/health", timeout=3)
        return r.ok
    except Exception:
        return False


def get_countries():
    try:
        r = requests.get(f"{API_URL}/config/countries", timeout=5)
        return r.json() if r.ok else {}
    except Exception:
        return {"IN": {"name": "India", "digits": 10},
                "SG": {"name": "Singapore", "digits": 8},
                "US": {"name": "United States", "digits": 10},
                "GB": {"name": "United Kingdom", "digits": 10}}


# ---- Sidebar ----
with st.sidebar:
    st.markdown("""
        <div style="margin-bottom:6px;">
            <span style="font-family:'JetBrains Mono',monospace; font-size:11px;
                font-weight:700; letter-spacing:0.2em; color:#E63946;
                text-transform:uppercase;">XENO VALIDATOR</span>
        </div>
        <div style="font-family:'JetBrains Mono',monospace; font-size:10px;
            color:#444444; margin-bottom:24px; letter-spacing:0.04em;">
            v1.0 / Transaction Validator
        </div>
        <hr style="border:none; border-top:1px solid #1F1F1F; margin-bottom:20px;"/>
        <div style="font-size:9px; letter-spacing:0.14em; text-transform:uppercase;
            color:#444444; font-weight:600; margin-bottom:14px;">Configuration</div>
    """, unsafe_allow_html=True)

    countries = get_countries()
    country_options = {f"{code} — {info['name']}": code for code, info in countries.items()}
    selected_label = st.selectbox("Country (Phone Validation)", list(country_options.keys()))
    country_code = country_options[selected_label]

    date_format = st.selectbox(
        "Expected Date Format",
        ["%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d", "%d-%b-%Y"]
    )

    chunk_size_input = st.number_input("Chunk Size (Rows)", min_value=100, max_value=10000, value=1000, step=100)
    split_output = st.checkbox("Split output file", value=False)
    chunk_size = chunk_size_input if split_output else 1000

    st.markdown("""
        <hr style="border:none; border-top:1px solid #1F1F1F; margin:20px 0 16px 0;"/>
        <div style="font-size:9px; letter-spacing:0.14em; text-transform:uppercase;
            color:#444444; font-weight:600; margin-bottom:8px;">Valid Payment Modes</div>
        <div style="font-family:'JetBrains Mono',monospace; font-size:9px;
            color:#555555; line-height:1.9;">
            credit_card, debit_card, upi,<br>
            net_banking, cash, wallet, emi
        </div>
    """, unsafe_allow_html=True)


# ---- Top Bar ----
api_online = check_api()
status_class = "online" if api_online else "offline"
status_dot = "online" if api_online else "offline"
status_text = "API Connected" if api_online else "API Offline"

st.markdown(f"""
<div class="top-bar">
    <span class="top-bar-title">Upload</span>
    <div class="api-status {status_class}">
        <div class="api-dot {status_dot}"></div>
        {status_text}
    </div>
</div>
""", unsafe_allow_html=True)


# ---- Main Content ----
st.markdown('<div class="page-content">', unsafe_allow_html=True)

st.markdown('<p class="section-label">Transaction File</p>', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Select CSV file",
    type=["csv"],
    label_visibility="collapsed"
)

if uploaded_file:
    preview_df = pd.read_csv(uploaded_file)
    uploaded_file.seek(0)

    st.markdown(f"""
        <div class="preview-meta" style="margin-top:20px;">
            {len(preview_df):,} rows &nbsp;&middot;&nbsp;
            {len(preview_df.columns)} columns &nbsp;&middot;&nbsp;
            {uploaded_file.name}
        </div>
    """, unsafe_allow_html=True)

    st.dataframe(preview_df.head(10), use_container_width=True)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # Initialize session state for validation results
    if "validation_data" not in st.session_state:
        st.session_state.validation_data = None

    # Create button row - centered with clear button on the side if results exist
    if st.session_state.validation_data is not None:
        btn_col1, btn_col2, btn_col3 = st.columns([2, 3, 2])
        with btn_col1:
            if st.button("CLEAR RESULTS", use_container_width=True):
                st.session_state.validation_data = None
                st.session_state.cached_files = None
                st.session_state.cache_key = None
                st.rerun()
        with btn_col2:
            run_validation = st.button("RUN VALIDATION", use_container_width=True)
        with btn_col3:
            st.write("")  # Empty column for balance
    else:
        # Center the validation button when no results
        btn_col1, btn_col2, btn_col3 = st.columns([2, 3, 2])
        with btn_col1:
            st.write("")
        with btn_col2:
            run_validation = st.button("RUN VALIDATION", use_container_width=True)
        with btn_col3:
            st.write("")

    if run_validation:
        with st.spinner("Processing..."):
            try:
                response = requests.post(
                    f"{API_URL}/validate",
                    files={"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")},
                    data={
                        "country_code": country_code,
                        "date_format": date_format,
                        "chunk_size": chunk_size,
                        "split_output": str(split_output).lower()
                    },
                    timeout=60
                )

                if response.ok:
                    # Store validation results in session state
                    st.session_state.validation_data = response.json()
                else:
                    detail = response.json().get("detail", "Unknown error")
                    st.markdown(f'<div class="error-alert">Error: {detail}</div>', unsafe_allow_html=True)
                    st.session_state.validation_data = None

            except requests.exceptions.ConnectionError:
                st.markdown(
                    '<div class="error-alert">Cannot connect to backend. Ensure the API server is running on port 8000.</div>',
                    unsafe_allow_html=True
                )
                st.session_state.validation_data = None
            except Exception as e:
                st.markdown(f'<div class="error-alert">Unexpected error: {str(e)}</div>', unsafe_allow_html=True)
                st.session_state.validation_data = None

    # Display validation results if available
    if st.session_state.validation_data is not None:
        try:
            data = st.session_state.validation_data
            total = data["file_stats"]["row_count"]
            valid = data["clean_summary"]["valid_rows"]
            invalid = data["clean_summary"]["invalid_rows"]
            chunks = data["split_summary"]["chunks_created"]

            # ---- Stat Bar ----
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
            st.markdown('<p class="section-label">Summary</p>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="stat-bar">
                <div class="stat-item">
                    <div class="stat-number">{total:,}</div>
                    <div class="stat-label">Total Rows</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number pass">{valid:,}</div>
                    <div class="stat-label">Valid Rows</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number accent">{invalid:,}</div>
                    <div class="stat-label">Invalid Rows</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{chunks}</div>
                    <div class="stat-label">Chunks</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # ---- Validator Table ----
            st.markdown('<p class="section-label" style="margin-top:32px;">Validators</p>', unsafe_allow_html=True)

            rows_html = ""
            for s in data["validation_summaries"]:
                status_html = (
                    '<span class="status-pass">PASS</span>'
                    if s["is_valid"] else
                    '<span class="status-fail">FAIL</span>'
                )
                rows_html += f"""
                <tr>
                    <td><span class="worker-name">{s['worker']}</span></td>
                    <td>{status_html}</td>
                    <td>{s['error_count']}</td>
                </tr>"""

            st.markdown(f"""
            <table class="validator-table">
                <thead>
                    <tr>
                        <th>Validator</th>
                        <th>Status</th>
                        <th>Errors</th>
                    </tr>
                </thead>
                <tbody>{rows_html}</tbody>
            </table>
            """, unsafe_allow_html=True)

            # ---- Error Details ----
            has_errors = any(s["error_count"] > 0 for s in data["validation_summaries"])
            if has_errors:
                st.markdown('<p class="section-label" style="margin-top:32px;">Error Detail</p>', unsafe_allow_html=True)

                for s in data["validation_summaries"]:
                    if s["error_count"] == 0:
                        continue
                    
                    # Create more descriptive label
                    worker_name = s['worker'].replace('Worker', '')
                    issue_text = "issue" if s["error_count"] == 1 else "issues"
                    expander_label = f"▸ {worker_name} Validation — {s['error_count']} {issue_text} detected — Click to view details"
                    
                    with st.expander(expander_label, expanded=False):
                        if s["errors"]:
                            err_rows = ""
                            for e in s["errors"]:
                                err_rows += f"""
                                <tr>
                                    <td>{e.get('row', '-')}</td>
                                    <td>{e.get('column', '-')}</td>
                                    <td>{e.get('value', '-')}</td>
                                    <td class="error-reason">{e.get('reason', '-')}</td>
                                </tr>"""
                            st.markdown(f"""
                            <table class="error-table">
                                <thead>
                                    <tr>
                                        <th>Row</th>
                                        <th>Column</th>
                                        <th>Value</th>
                                        <th>Reason</th>
                                    </tr>
                                </thead>
                                <tbody>{err_rows}</tbody>
                            </table>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(
                                '<p style="font-size:11px;color:#999;font-family:monospace;padding:12px 0;">No issues detected.</p>',
                                unsafe_allow_html=True
                            )

            # ---- Download Options ----
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
            st.markdown('<p class="section-label">Download Options</p>', unsafe_allow_html=True)
            
            # Get report URLs if available
            report_urls = data.get("report_urls", {})
            
            if report_urls:
                # Initialize session state for previews
                if "show_validation_preview" not in st.session_state:
                    st.session_state.show_validation_preview = False
                if "show_failed_preview" not in st.session_state:
                    st.session_state.show_failed_preview = False
                if "show_cleaned_preview" not in st.session_state:
                    st.session_state.show_cleaned_preview = False
                
                # Fetch all files once (only if not already cached with this session)
                cache_key = f"files_{data.get('file_stats', {}).get('row_count', 0)}"
                if "cached_files" not in st.session_state or st.session_state.get("cache_key") != cache_key:
                    validation_resp = requests.get(f"{API_URL}{report_urls['validation_report']}", timeout=30)
                    failed_resp = requests.get(f"{API_URL}{report_urls['failed_records']}", timeout=30)
                    cleaned_resp = requests.get(f"{API_URL}{report_urls['cleaned_data']}", timeout=30)
                    
                    st.session_state.cached_files = {
                        "validation": validation_resp.content if validation_resp.ok else None,
                        "failed": failed_resp.content if failed_resp.ok else None,
                        "cleaned": cleaned_resp.content if cleaned_resp.ok else None
                    }
                    st.session_state.cache_key = cache_key
                
                # Use cached file contents
                validation_content = st.session_state.cached_files.get("validation")
                failed_content = st.session_state.cached_files.get("failed")
                cleaned_content = st.session_state.cached_files.get("cleaned")
                
                # Create three columns for download options
                col1, col2, col3 = st.columns(3)
                
                # 1. Validation Report (all records with status)
                with col1:
                    st.markdown("""
                    <div style="margin-bottom: 8px;">
                        <div style="font-size: 11px; font-weight: 600; color: #0F0F0F; margin-bottom: 4px;">Validation Report</div>
                        <div style="font-size: 10px; color: #999; font-family: monospace;">All records + status + errors</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    btn_col1, btn_col2 = st.columns([1, 1])
                    with btn_col1:
                        if validation_content:
                            st.download_button(
                                label="Download",
                                data=validation_content,
                                file_name="validation_report.csv",
                                mime="text/csv",
                                key="dl_validation_report",
                                use_container_width=True
                            )
                    with btn_col2:
                        if st.button("Preview", key="preview_validation", use_container_width=True):
                            st.session_state.show_validation_preview = not st.session_state.show_validation_preview
                
                # 2. Failed Records
                with col2:
                    st.markdown("""
                    <div style="margin-bottom: 8px;">
                        <div style="font-size: 11px; font-weight: 600; color: #0F0F0F; margin-bottom: 4px;">Failed Records</div>
                        <div style="font-size: 10px; color: #999; font-family: monospace;">Only invalid records + reasons</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    btn_col1, btn_col2 = st.columns([1, 1])
                    with btn_col1:
                        if failed_content:
                            st.download_button(
                                label="Download",
                                data=failed_content,
                                file_name="failed_records.csv",
                                mime="text/csv",
                                key="dl_failed_records",
                                use_container_width=True
                            )
                    with btn_col2:
                        if st.button("Preview", key="preview_failed", use_container_width=True):
                            st.session_state.show_failed_preview = not st.session_state.show_failed_preview
                
                # 3. Cleaned CSV
                with col3:
                    st.markdown("""
                    <div style="margin-bottom: 8px;">
                        <div style="font-size: 11px; font-weight: 600; color: #0F0F0F; margin-bottom: 4px;">Clean Data</div>
                        <div style="font-size: 10px; color: #999; font-family: monospace;">Only valid records (clean)</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    btn_col1, btn_col2 = st.columns([1, 1])
                    with btn_col1:
                        if cleaned_content:
                            st.download_button(
                                label="Download",
                                data=cleaned_content,
                                file_name="cleaned_data.csv",
                                mime="text/csv",
                                key="dl_cleaned_data",
                                use_container_width=True
                            )
                    with btn_col2:
                        if st.button("Preview", key="preview_cleaned", use_container_width=True):
                            st.session_state.show_cleaned_preview = not st.session_state.show_cleaned_preview
                
                # Show previews based on session state
                if st.session_state.show_validation_preview and validation_content:
                    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
                    st.markdown('<p class="section-label">Validation Report Preview</p>', unsafe_allow_html=True)
                    validation_df = pd.read_csv(BytesIO(validation_content))
                    st.markdown(f"""
                    <div style="color: #0F0F0F; font-size: 12px; margin: 1rem 0;">
                        {len(validation_df)} rows × {len(validation_df.columns)} columns (showing first 10 rows)
                    </div>
                    """, unsafe_allow_html=True)
                    st.dataframe(validation_df.head(10), use_container_width=True)
                
                if st.session_state.show_failed_preview and failed_content:
                    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
                    st.markdown('<p class="section-label">Failed Records Preview</p>', unsafe_allow_html=True)
                    failed_df = pd.read_csv(BytesIO(failed_content))
                    st.markdown(f"""
                    <div style="color: #0F0F0F; font-size: 12px; margin: 1rem 0;">
                        {len(failed_df)} rows × {len(failed_df.columns)} columns (showing first 10 rows)
                    </div>
                    """, unsafe_allow_html=True)
                    st.dataframe(failed_df.head(10), use_container_width=True)
                
                if st.session_state.show_cleaned_preview and cleaned_content:
                    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
                    st.markdown('<p class="section-label">Clean Data Preview</p>', unsafe_allow_html=True)
                    cleaned_df = pd.read_csv(BytesIO(cleaned_content))
                    st.markdown(f"""
                    <div style="color: #0F0F0F; font-size: 12px; margin: 1rem 0;">
                        {len(cleaned_df)} rows × {len(cleaned_df.columns)} columns (showing first 10 rows)
                    </div>
                    """, unsafe_allow_html=True)
                    st.dataframe(cleaned_df.head(10), use_container_width=True)

        except requests.exceptions.ConnectionError:
            st.markdown(
                '<div class="error-alert">Cannot connect to backend. Ensure the API server is running on port 8000.</div>',
                unsafe_allow_html=True
            )
        except Exception as e:
            st.markdown(f'<div class="error-alert">Unexpected error: {str(e)}</div>', unsafe_allow_html=True)

else:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-state-title">Select a transaction file to begin.</div>
        <div class="empty-state-sub" style="margin-top:16px;">
            Expected columns: order_id &nbsp;&middot;&nbsp; product_id &nbsp;&middot;&nbsp;
            payment_mode &nbsp;&middot;&nbsp; phone<br>
            order_date &nbsp;&middot;&nbsp; amount &nbsp;&middot;&nbsp; email
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)