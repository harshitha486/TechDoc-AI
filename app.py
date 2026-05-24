"""
TechDoc AI — Technical Documentation Generator
Clean, minimal Streamlit UI
"""

from __future__ import annotations

import os
import time
from pathlib import Path

import streamlit as st

# ── Env loading ──────────────────────────────────────────────────────────────
def _load_env():
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        return
    for enc in ("utf-8", "utf-16", "utf-8-sig", "latin-1"):
        try:
            from dotenv import load_dotenv
            load_dotenv(dotenv_path=str(env_path), encoding=enc, override=False)
            return
        except (UnicodeDecodeError, TypeError):
            continue

_load_env()

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TechDoc AI",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Design system — Sage & Teal ───────────────────────────────────────────────
# Primary palette:
#   bg        #f2f5f1   (lightest sage)
#   surface   #dee1dd   (sage)
#   border    #c4c9c3   (sage darker)
#   text      #1c3335   (very dark teal)
#   muted     #5e7572
#   accent    #2f575d   (teal)
#   sidebar   #2f575d bg, #dee1dd text
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, sans-serif;
    color: #1c3335;
}

.stApp { background: #f2f5f1; }

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.5rem 4rem; max-width: 1100px; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #2f575d !important;
    border-right: 1px solid #1e3f44 !important;
    padding-top: 1.5rem;
}
section[data-testid="stSidebar"] > div { padding: 0 1.2rem; }
section[data-testid="stSidebar"] * { color: #a8c4c7 !important; }
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] strong { color: #dee1dd !important; }

/* Sidebar inputs */
section[data-testid="stSidebar"] .stTextInput > div > div > input,
section[data-testid="stSidebar"] .stTextArea > div > div > textarea,
section[data-testid="stSidebar"] .stSelectbox > div > div {
    background: #234347 !important;
    border: 1px solid #1e3f44 !important;
    color: #dee1dd !important;
}
section[data-testid="stSidebar"] .stSelectbox svg { color: #a8c4c7 !important; fill: #a8c4c7 !important; }

/* ── Sidebar logo ── */
.sidebar-logo {
    display: flex; align-items: center; gap: 0.6rem;
    padding: 0.2rem 0 1.2rem;
    border-bottom: 1px solid #1e3f44;
    margin-bottom: 1.2rem;
}
.sidebar-logo-icon {
    width: 28px; height: 28px;
    background: #dee1dd;
    border-radius: 7px;
    display: flex; align-items: center; justify-content: center;
    font-size: 13px; font-weight: 700; color: #2f575d !important;
}
.sidebar-logo-text { font-size: 0.95rem; font-weight: 600; color: #dee1dd !important; }
.sidebar-logo-badge {
    font-size: 0.65rem; background: #1e3f44;
    border-radius: 4px; padding: 1px 6px;
    color: #6a9598 !important; margin-left: auto;
}

/* ── Sidebar section labels ── */
.sidebar-label {
    font-size: 0.68rem; font-weight: 600;
    letter-spacing: 0.09em; text-transform: uppercase;
    color: #6a9598 !important;
    margin: 1.2rem 0 0.45rem;
}

/* ── Main input fields ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    background: #dee1dd !important;
    border: 1px solid #c4c9c3 !important;
    border-radius: 8px !important;
    color: #1c3335 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
    transition: border-color 0.15s, box-shadow 0.15s;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #2f575d !important;
    box-shadow: 0 0 0 3px rgba(47,87,93,0.12) !important;
    outline: none !important;
}
.stTextInput > label, .stTextArea > label, .stSelectbox > label {
    font-size: 0.8rem !important; font-weight: 500 !important;
    color: #5e7572 !important; margin-bottom: 0.3rem !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid #c4c9c3;
    gap: 0; padding: 0;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important;
    color: #8aa5a3 !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    padding: 0.75rem 1.25rem !important;
    margin-bottom: -1px;
    transition: color 0.15s;
}
.stTabs [data-baseweb="tab"]:hover { color: #2f575d !important; }
.stTabs [aria-selected="true"] {
    color: #2f575d !important;
    border-bottom-color: #2f575d !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.5rem !important; }

/* ── Primary button ── */
.stButton > button {
    background: #2f575d !important;
    border: none !important;
    border-radius: 8px !important;
    color: #dee1dd !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    padding: 0.55rem 1.4rem !important;
    transition: background 0.15s, transform 0.1s;
}
.stButton > button:hover { background: #1e3f44 !important; }
.stButton > button:active { transform: scale(0.98); }
.stButton > button[kind="secondary"] {
    background: #dee1dd !important;
    border: 1px solid #c4c9c3 !important;
    color: #5e7572 !important;
}
.stButton > button[kind="secondary"]:hover {
    background: #cdd1cc !important;
    color: #1c3335 !important;
}

/* ── Download button ── */
.stDownloadButton > button {
    background: #dee1dd !important;
    border: 1px solid #c4c9c3 !important;
    border-radius: 8px !important;
    color: #2f575d !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    padding: 0.4rem 1rem !important;
    transition: all 0.15s;
}
.stDownloadButton > button:hover {
    background: #cdd1cc !important;
    border-color: #b5bbb4 !important;
    color: #1e3f44 !important;
}

/* ── Checkboxes ── */
.stCheckbox > label { font-size: 0.875rem !important; color: #5e7572 !important; }
.stCheckbox > label:hover { color: #1c3335 !important; }

/* ── Radio ── */
.stRadio > label { font-size: 0.8rem !important; color: #8aa5a3 !important; }
.stRadio [data-testid="stMarkdownContainer"] p { font-size: 0.875rem !important; color: #3d5e61; }

/* ── Progress ── */
.stProgress > div > div > div { background: #2f575d !important; border-radius: 4px !important; }
.stProgress > div > div { background: #c4c9c3 !important; border-radius: 4px !important; height: 3px !important; }

/* ── Divider ── */
hr { border-color: #c4c9c3 !important; margin: 1.5rem 0 !important; }

/* ── Alerts ── */
.stAlert { border-radius: 8px !important; font-size: 0.875rem !important; }

/* ── Expander ── */
.streamlit-expanderHeader {
    background: #dee1dd !important;
    border: 1px solid #c4c9c3 !important;
    border-radius: 8px !important;
    font-size: 0.875rem !important; font-weight: 500 !important;
    color: #5e7572 !important; padding: 0.7rem 1rem !important;
}
.streamlit-expanderContent {
    background: #e8ebe7 !important;
    border: 1px solid #c4c9c3 !important;
    border-top: none !important;
    border-radius: 0 0 8px 8px !important;
    padding: 1rem !important;
}

/* ── Code blocks ── */
code {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.8rem !important;
    background: #cdd1cc !important;
    border: 1px solid #b5bbb4;
    border-radius: 4px;
    padding: 0.15em 0.4em;
    color: #2f575d !important;
}
pre {
    background: #e8ebe7 !important;
    border: 1px solid #c4c9c3 !important;
    border-radius: 8px !important;
    padding: 1rem !important;
}
pre code { background: transparent !important; border: none !important; padding: 0 !important; }

/* ── Page header ── */
.page-header {
    display: flex; align-items: flex-start; justify-content: space-between;
    margin-bottom: 2rem; padding-bottom: 1.5rem;
    border-bottom: 1px solid #c4c9c3;
}
.page-title { font-size: 1.3rem; font-weight: 600; color: #1c3335; }
.page-subtitle { font-size: 0.85rem; color: #7a9a98; margin-top: 0.25rem; }

/* ── Section label ── */
.section-label {
    font-size: 0.72rem; font-weight: 600;
    letter-spacing: 0.07em; text-transform: uppercase;
    color: #8aa5a3; margin-bottom: 0.75rem;
}

/* ── Output card ── */
.output-card {
    background: #dee1dd;
    border: 1px solid #c4c9c3;
    border-radius: 10px;
    padding: 1.5rem; margin: 1rem 0;
}
.output-header {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 1rem; padding-bottom: 0.75rem;
    border-bottom: 1px solid #c4c9c3;
}
.output-title {
    font-size: 0.78rem; font-weight: 600;
    letter-spacing: 0.06em; text-transform: uppercase;
    color: #7a9a98;
}
.output-badge {
    font-size: 0.68rem;
    background: #e8f0f0; border: 1px solid #b0cfd2;
    border-radius: 20px; padding: 0.15em 0.7em;
    color: #2f575d;
}

/* ── Metric pill ── */
.metric-row { display: flex; gap: 0.75rem; margin: 1rem 0; }
.metric-pill {
    background: #dee1dd; border: 1px solid #c4c9c3;
    border-radius: 20px; padding: 0.3rem 0.9rem;
    font-size: 0.8rem; color: #5e7572;
}
.metric-pill span { color: #1c3335; font-weight: 600; margin-right: 0.3em; }
.metric-pill .add { color: #2e6b3e; }
.metric-pill .del { color: #8b3a3a; }

/* ── Tag strip ── */
.tag-strip { display: flex; flex-wrap: wrap; gap: 0.4rem; margin-top: 0.5rem; }
.tag {
    font-size: 0.7rem; background: #234347;
    border: 1px solid #1e3f44; border-radius: 4px;
    padding: 0.15em 0.55em; color: #a8c4c7 !important;
    font-family: 'JetBrains Mono', monospace;
}

/* ── File rows ── */
.file-row {
    display: flex; align-items: center; gap: 0.6rem;
    padding: 0.4rem 0; border-bottom: 1px solid #cdd1cc;
    font-size: 0.8rem;
}
.file-row:last-child { border-bottom: none; }
.file-status { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }
.file-name { color: #3d5e61; font-family: 'JetBrains Mono', monospace; flex: 1; }
.file-stat { font-size: 0.75rem; }
.file-stat .add { color: #2e6b3e; }
.file-stat .del { color: #8b3a3a; }

/* ── Token usage ── */
.token-row {
    display: flex; align-items: center; gap: 0.5rem;
    margin: 0.75rem 0; font-size: 0.75rem; color: #8aa5a3;
}
.token-dot { width: 5px; height: 5px; border-radius: 50%; background: #2f575d; }
.token-val { color: #5e7572; }

/* ── Spinner ── */
.stSpinner > div { border-top-color: #2f575d !important; }
</style>
""", unsafe_allow_html=True)


# ── Agent factory ─────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def get_agent(api_key: str, provider: str = "gemini"):
    from agent.doc_agent import DocAgent
    return DocAgent(api_key=api_key, provider=provider)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
      <div class="sidebar-logo-icon">◆</div>
      <span class="sidebar-logo-text">TechDoc AI</span>
      <span class="sidebar-logo-badge">beta</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="sidebar-label">Provider</p>', unsafe_allow_html=True)
    provider = st.selectbox(
        "provider", label_visibility="collapsed",
        options=["gemini", "groq", "anthropic"],
        format_func=lambda x: {
            "gemini":    "Google Gemini  ·  free",
            "groq":      "Groq / Llama 3.3  ·  free",
            "anthropic": "Anthropic Claude  ·  paid",
        }[x],
    )

    PROVIDER_INFO = {
        "gemini":    ("API Key", "AIza...",    "aistudio.google.com",    "GEMINI_API_KEY"),
        "groq":      ("API Key", "gsk_...",    "console.groq.com",       "GROQ_API_KEY"),
        "anthropic": ("API Key", "sk-ant-...", "console.anthropic.com",  "ANTHROPIC_API_KEY"),
    }
    label, placeholder, help_url, env_var = PROVIDER_INFO[provider]

    st.markdown('<p class="sidebar-label">API Key</p>', unsafe_allow_html=True)
    active_key = st.text_input(
        label, label_visibility="collapsed",
        value=os.getenv(env_var, ""),
        type="password",
        placeholder=placeholder,
        help=f"Get key at {help_url}",
    )

    st.markdown('<p class="sidebar-label">GitHub Token</p>', unsafe_allow_html=True)
    github_token = st.text_input(
        "GitHub Token", label_visibility="collapsed",
        value=os.getenv("GITHUB_TOKEN", ""),
        type="password",
        placeholder="ghp_...  (optional)",
        help="Required for private repos. github.com → Settings → Tokens",
    )

    st.markdown('<p class="sidebar-label">Settings</p>', unsafe_allow_html=True)
    doc_style = st.selectbox(
        "doc style", label_visibility="collapsed",
        options=["google", "numpy", "rst", "jsdoc", "javadoc"],
        format_func=lambda x: {
            "google": "Google style",
            "numpy":  "NumPy style",
            "rst":    "reStructuredText",
            "jsdoc":  "JSDoc",
            "javadoc":"Javadoc",
        }[x],
    )
    output_format = st.selectbox(
        "export format", label_visibility="collapsed",
        options=["Markdown", "HTML"],
    )

    st.markdown('<p class="sidebar-label">Languages</p>', unsafe_allow_html=True)
    st.markdown("""
    <div class="tag-strip">
      <span class="tag">Python</span><span class="tag">JS</span>
      <span class="tag">TS</span><span class="tag">Java</span>
      <span class="tag">Go</span><span class="tag">Rust</span>
      <span class="tag">C++</span><span class="tag">Ruby</span>
    </div>
    """, unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def validate_key() -> bool:
    if not active_key or not active_key.strip():
        st.error("Enter your API key in the sidebar to continue.")
        return False
    return True


def show_usage(usage: dict) -> None:
    if not usage:
        return
    inp  = usage.get("input_tokens", 0)
    out  = usage.get("output_tokens", 0)
    cached = usage.get("cache_read", 0)
    parts = [f"<span class='token-val'>{inp:,} in</span>",
             f"<span class='token-val'>{out:,} out</span>"]
    if cached:
        parts.append(f"<span class='token-val'>{cached:,} cached</span>")
    st.markdown(
        f"<div class='token-row'><div class='token-dot'></div>tokens · "
        + " · ".join(parts) + "</div>",
        unsafe_allow_html=True,
    )


def render_output(title: str, content: str, filename: str) -> None:
    """Render a doc output card with download button."""
    st.markdown(f"""
    <div class="output-card">
      <div class="output-header">
        <span class="output-title">{title}</span>
        <span class="output-badge">generated</span>
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(content)

    if output_format == "HTML":
        from utils.exporter import DocExporter
        data = DocExporter().to_html(content, title=title)
        fname, mime = f"{filename}.html", "text/html"
    else:
        data = content.encode("utf-8")
        fname, mime = f"{filename}.md", "text/markdown"

    st.download_button(f"Download {fname}", data=data,
                       file_name=fname, mime=mime)
    st.divider()


# ── Page header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
  <div>
    <div class="page-title">Documentation Generator</div>
    <div class="page-subtitle">Generate and update docs from code, pull requests, and deployments</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["Code → Docs", "PR Analyzer", "Deployment Docs", "API Docs"])


# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — Code → Docs
# ════════════════════════════════════════════════════════════════════════════
with tab1:
    col_left, col_right = st.columns([3, 1], gap="large")

    with col_left:
        st.markdown('<p class="section-label">Source Code</p>', unsafe_allow_html=True)
        input_mode = st.radio("input mode", ["Paste code", "Upload files"],
                               horizontal=True, label_visibility="collapsed")

        code_input = ""
        detected_lang = "python"
        filename_hint = ""

        if input_mode == "Paste code":
            code_input = st.text_area(
                "code", label_visibility="collapsed",
                height=320,
                placeholder="Paste your source code here…",
            )
        else:
            uploaded_files = st.file_uploader(
                "Upload files", label_visibility="collapsed",
                accept_multiple_files=True,
                type=["py","js","ts","jsx","tsx","java","cpp","c","go","rs","rb","php","cs","kt"],
            )
            if uploaded_files:
                from utils.file_handler import FileHandler
                fh = FileHandler()
                file_results = fh.read_multiple_files(uploaded_files)
                code_input    = fh.combine_files(file_results)
                detected_lang = file_results[0]["language"] if file_results else "python"
                filename_hint = uploaded_files[0].name if uploaded_files else ""
                st.success(f"{len(uploaded_files)} file(s) loaded — {detected_lang}")

    with col_right:
        st.markdown('<p class="section-label">Options</p>', unsafe_allow_html=True)

        if input_mode == "Paste code":
            lang_options = ["auto-detect","python","javascript","typescript",
                            "java","cpp","go","rust","ruby","php","csharp"]
            lang_choice  = st.selectbox("Language", lang_options)
            detected_lang = lang_choice if lang_choice != "auto-detect" else "auto"

        project_name  = st.text_input("Project name", placeholder="my-project")
        extra_context = st.text_area("Context", placeholder="Brief description…", height=80)

        st.markdown('<p class="section-label" style="margin-top:1rem">Generate</p>',
                    unsafe_allow_html=True)
        gen_docstrings = st.checkbox("Docstrings",   value=True)
        gen_readme     = st.checkbox("README",        value=True)
        gen_api        = st.checkbox("API Docs",      value=False)
        gen_arch       = st.checkbox("Architecture",  value=False)

    st.divider()
    run_btn = st.button("Generate documentation", type="primary")

    if run_btn:
        if not validate_key(): st.stop()
        if not code_input.strip():
            st.error("Paste or upload some source code first.")
            st.stop()

        tasks = []
        if gen_docstrings: tasks.append(("docstrings",   "Docstrings"))
        if gen_readme:     tasks.append(("readme",       "README"))
        if gen_api:        tasks.append(("api_docs",     "API Docs"))
        if gen_arch:       tasks.append(("architecture", "Architecture"))

        if not tasks:
            st.warning("Select at least one output type.")
            st.stop()

        agent   = get_agent(active_key, provider)
        context = f"Project: {project_name}. {extra_context}".strip(". ")
        results: dict[str, str] = {}
        bar     = st.progress(0, text="")

        for i, (doc_type, label) in enumerate(tasks):
            bar.progress(i / len(tasks), text=f"Generating {label}…")
            if i > 0 and provider == "gemini":
                time.sleep(10)
            try:
                results[doc_type] = agent.generate_docs(
                    code=code_input, doc_type=doc_type,
                    language=detected_lang, style=doc_style,
                    context=context, filename=filename_hint,
                )
            except Exception as exc:
                st.error(f"{label}: {exc}")

        bar.progress(1.0, text="Done")
        show_usage(agent.last_usage)
        st.divider()

        label_map = {
            "docstrings":   ("Docstrings",          "docstrings"),
            "readme":       ("README",               "README"),
            "api_docs":     ("API Reference",        "api-reference"),
            "architecture": ("Architecture Overview","architecture"),
        }
        for key, content in results.items():
            lbl, fname = label_map[key]
            render_output(lbl, content, fname)

        if len(results) > 1:
            from utils.exporter import DocExporter
            zip_data = DocExporter().to_zip({f"{k}.md": v for k, v in results.items()})
            st.download_button("Download all as ZIP", data=zip_data,
                               file_name="techdocs.zip", mime="application/zip")

        # ── Diff-aware update ─────────────────────────────────────────
        with st.expander("Update existing docs  ·  diff-aware"):
            st.caption("Paste the previous version of your code to update only what changed.")
            old_code      = st.text_area("Old code",      height=140, placeholder="Previous version…")
            existing_docs = st.text_area("Existing docs", height=140, placeholder="# My Docs…")
            upd_type      = st.selectbox("Type", ["docstrings","readme","api_docs"])
            if st.button("Update docs", type="secondary"):
                if old_code.strip() and existing_docs.strip():
                    with st.spinner("Updating…"):
                        try:
                            updated = agent.update_docs(old_code, code_input, existing_docs, upd_type)
                            render_output("Updated Documentation", updated, "updated-docs")
                            show_usage(agent.last_usage)
                        except Exception as exc:
                            st.error(str(exc))
                else:
                    st.warning("Provide both old code and existing docs.")


# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — PR Analyzer
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    col_left, col_right = st.columns([3, 1], gap="large")

    with col_left:
        st.markdown('<p class="section-label">Pull Request</p>', unsafe_allow_html=True)
        pr_mode = st.radio("pr mode", ["GitHub URL", "Paste diff"],
                           horizontal=True, label_visibility="collapsed")

        pr_diff_text = pr_title_val = pr_desc_val = ""

        if pr_mode == "GitHub URL":
            pr_url = st.text_input("url", label_visibility="collapsed",
                                   placeholder="https://github.com/owner/repo/pull/123")
            if st.button("Fetch PR", type="secondary"):
                if not pr_url.strip():
                    st.warning("Enter a GitHub PR URL.")
                else:
                    try:
                        from utils.github_client import GitHubClient
                        from parsers.pr_parser   import PRParser
                        gc = GitHubClient(token=github_token)
                        owner, repo, pr_num = gc.parse_pr_url(pr_url)
                        with st.spinner(f"Fetching #{pr_num}…"):
                            pr_data = gc.get_pr(owner, repo, pr_num)
                            pr_diff_text = gc.get_pr_diff(owner, repo, pr_num)
                            pr_files     = gc.get_pr_files(owner, repo, pr_num)
                        pr_title_val = pr_data.get("title", "")
                        pr_desc_val  = pr_data.get("body",  "") or ""
                        st.session_state.update({
                            "pr_diff": pr_diff_text, "pr_title": pr_title_val,
                            "pr_desc": pr_desc_val,  "pr_version": "Unreleased",
                        })
                        parser  = PRParser()
                        summary = parser.summarize_changes(pr_diff_text)
                        st.success(f"Fetched: {pr_title_val}")
                        st.markdown(f"""
                        <div class="metric-row">
                          <div class="metric-pill"><span>{summary['files_changed']}</span> files</div>
                          <div class="metric-pill"><span class="add">+{summary['lines_added']}</span> added</div>
                          <div class="metric-pill"><span class="del">-{summary['lines_removed']}</span> removed</div>
                        </div>""", unsafe_allow_html=True)
                        if pr_files:
                            with st.expander(f"{len(pr_files)} changed files"):
                                status_color = {"added":"#4ade80","removed":"#f87171",
                                                "modified":"#facc15","renamed":"#60a5fa"}
                                for f in pr_files[:25]:
                                    col = status_color.get(f.get("status","modified"),"#71717a")
                                    st.markdown(f"""
                                    <div class="file-row">
                                      <div class="file-status" style="background:{col}"></div>
                                      <span class="file-name">{f.get('filename','')}</span>
                                      <span class="file-stat">
                                        <span class="add">+{f.get('additions',0)}</span>
                                        <span class="del"> -{f.get('deletions',0)}</span>
                                      </span>
                                    </div>""", unsafe_allow_html=True)
                    except Exception as exc:
                        st.error(str(exc))
                        if not github_token:
                            st.info("Add a GitHub token in the sidebar for private repos.")
        else:
            pr_diff_text = st.text_area(
                "diff", label_visibility="collapsed",
                height=280,
                placeholder="diff --git a/src/auth.py b/src/auth.py\n…",
            )
            if pr_diff_text:
                st.session_state["pr_diff"] = pr_diff_text

    with col_right:
        st.markdown('<p class="section-label">Metadata</p>', unsafe_allow_html=True)
        pr_title_val = st.text_input("PR title",
                                     value=st.session_state.get("pr_title",""),
                                     placeholder="feat: add auth")
        pr_desc_val  = st.text_area("Description",
                                    value=st.session_state.get("pr_desc",""),
                                    height=90, placeholder="What does this PR do?")
        version_val  = st.text_input("Version",
                                     value=st.session_state.get("pr_version","Unreleased"),
                                     placeholder="v2.0.0")

    st.divider()
    if st.button("Generate changelog entry", type="primary"):
        if not validate_key(): st.stop()
        final_diff    = st.session_state.get("pr_diff", pr_diff_text)
        final_title   = pr_title_val
        final_desc    = pr_desc_val
        final_version = version_val or "Unreleased"
        if not final_diff.strip() and not final_title.strip():
            st.error("Provide a PR URL or paste a diff.")
            st.stop()
        agent = get_agent(active_key, provider)
        with st.spinner("Generating…"):
            try:
                changelog = agent.analyze_pr(final_diff, final_title, final_desc, final_version)
                show_usage(agent.last_usage)
                render_output("Changelog Entry", changelog, "CHANGELOG")
            except Exception as exc:
                st.error(str(exc))


# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — Deployment Docs
# ════════════════════════════════════════════════════════════════════════════
with tab3:
    col_left, col_right = st.columns([3, 1], gap="large")

    with col_left:
        st.markdown('<p class="section-label">Changes</p>', unsafe_allow_html=True)
        deployment_diff = st.text_area(
            "changes", label_visibility="collapsed",
            height=260,
            placeholder="Paste git diff, commit messages, config changes, dependency bumps…",
        )
        extra_notes = st.text_area(
            "notes", label_visibility="collapsed",
            height=90,
            placeholder="Manual steps, rollback procedure, known issues… (optional)",
        )

    with col_right:
        st.markdown('<p class="section-label">Release Info</p>', unsafe_allow_html=True)
        service_name = st.text_input("Service",     placeholder="payment-service")
        old_version  = st.text_input("From version",placeholder="v1.3.0")
        new_version  = st.text_input("To version",  placeholder="v1.4.0")

        st.markdown('<p class="section-label" style="margin-top:1rem">Outputs</p>',
                    unsafe_allow_html=True)
        gen_release  = st.checkbox("Release Notes",   value=True)
        gen_migration= st.checkbox("Migration Guide",  value=False)
        gen_breaking = st.checkbox("Breaking Changes", value=False)

    st.divider()
    if st.button("Generate release docs", type="primary"):
        if not validate_key(): st.stop()
        if not deployment_diff.strip():
            st.error("Paste deployment changes first.")
            st.stop()
        tasks = []
        if gen_release:   tasks.append("release_notes")
        if gen_migration: tasks.append("migration_guide")
        if gen_breaking:  tasks.append("breaking_changes")
        if not tasks:
            st.warning("Select at least one output type.")
            st.stop()

        agent   = get_agent(active_key, provider)
        results : dict[str, str] = {}
        bar = st.progress(0, text="")

        for i, task in enumerate(tasks):
            bar.progress(i / len(tasks), text=f"Generating {task.replace('_',' ')}…")
            if i > 0 and provider == "gemini":
                time.sleep(10)
            extra = f"Focus on: {task.replace('_',' ')}. {extra_notes}".strip()
            try:
                results[task] = agent.generate_from_deployment(
                    diff=deployment_diff,
                    service_name=service_name or "Service",
                    old_version=old_version or "previous",
                    new_version=new_version or "latest",
                    extra_notes=extra,
                )
            except Exception as exc:
                st.error(f"{task}: {exc}")

        bar.progress(1.0, text="Done")
        show_usage(agent.last_usage)
        st.divider()

        label_map = {
            "release_notes":  ("Release Notes",   "release-notes"),
            "migration_guide":("Migration Guide",  "migration-guide"),
            "breaking_changes":("Breaking Changes","breaking-changes"),
        }
        for task, content in results.items():
            lbl, fname = label_map[task]
            render_output(lbl, content, fname)

        if len(results) > 1:
            from utils.exporter import DocExporter
            zip_data = DocExporter().to_zip({f"{k}.md": v for k, v in results.items()})
            st.download_button("Download all as ZIP", data=zip_data,
                               file_name="release-docs.zip", mime="application/zip")


# ════════════════════════════════════════════════════════════════════════════
# TAB 4 — API Docs
# ════════════════════════════════════════════════════════════════════════════
with tab4:
    col_left, col_right = st.columns([3, 1], gap="large")

    with col_left:
        st.markdown('<p class="section-label">Source</p>', unsafe_allow_html=True)
        api_mode = st.radio("api mode", ["Route code", "OpenAPI JSON"],
                            horizontal=True, label_visibility="collapsed")
        api_code = ""

        if api_mode == "Route code":
            api_code = st.text_area(
                "routes", label_visibility="collapsed",
                height=300,
                placeholder="@app.route('/users', methods=['GET'])\ndef get_users(): ...",
            )
            if api_code.strip():
                from parsers.api_parser import APIParser
                api_lang = "python"
                routes = APIParser().extract_all_routes(api_code, api_lang)
                if routes:
                    st.markdown(f"""
                    <div class="metric-row">
                      <div class="metric-pill"><span>{len(routes)}</span> endpoints detected</div>
                    </div>""", unsafe_allow_html=True)
        else:
            uploaded_spec = st.file_uploader("OpenAPI JSON", type=["json"],
                                              label_visibility="collapsed")
            if uploaded_spec:
                import json
                try:
                    spec = json.loads(uploaded_spec.read().decode("utf-8"))
                    from parsers.api_parser import APIParser
                    endpoints = APIParser().parse_openapi(spec)
                    api_code  = json.dumps(spec, indent=2)[:8000]
                    st.success(f"{len(endpoints)} endpoints parsed from OpenAPI spec")
                except Exception as exc:
                    st.error(str(exc))

    with col_right:
        st.markdown('<p class="section-label">API Info</p>', unsafe_allow_html=True)
        api_service = st.text_input("Service name", placeholder="User API")
        api_base    = st.text_input("Base URL",      placeholder="https://api.example.com/v1")
        if api_mode == "Route code":
            api_framework = st.selectbox("Framework",
                                          ["Flask", "FastAPI", "Express", "Django", "Other"])

    st.divider()
    if st.button("Generate API documentation", type="primary"):
        if not validate_key(): st.stop()
        if not api_code.strip():
            st.error("Paste route code or upload an OpenAPI spec.")
            st.stop()
        agent = get_agent(active_key, provider)
        with st.spinner("Generating…"):
            try:
                api_docs = agent.generate_api_docs(
                    code=api_code,
                    service_name=api_service or "API",
                    base_url=api_base or "https://api.example.com",
                )
                show_usage(agent.last_usage)
                render_output(f"{api_service or 'API'} Reference", api_docs, "api-reference")
            except Exception as exc:
                st.error(str(exc))


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; color:#8aa5a3; font-size:0.75rem;
            margin-top:3rem; padding-top:1.5rem; border-top:1px solid #c4c9c3;">
  TechDoc AI · Gemini · Groq · Claude
</div>
""", unsafe_allow_html=True)
