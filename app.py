"""
╔══════════════════════════════════════════════════════╗
║   ReAct Research Agent  ·  Streamlit Frontend        ║
║   Run: streamlit run streamlit_app.py                ║
╚══════════════════════════════════════════════════════╝
"""

import streamlit as st
import requests as req
import json
import time
from datetime import datetime

# ══════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="ReAct Research Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════
#  CUSTOM CSS — Dark editorial aesthetic
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=JetBrains+Mono:wght@300;400;500&family=Inter:wght@300;400;500;600&display=swap');

:root {
    --bg:          #0a0c0f;
    --surface:     #111418;
    --surface2:    #181c22;
    --border:      #1e2530;
    --border2:     #2a3240;
    --accent:      #3b82f6;
    --accent2:     #60a5fa;
    --accent-glow: rgba(59,130,246,0.15);
    --success:     #10b981;
    --warn:        #f59e0b;
    --danger:      #ef4444;
    --text:        #e2e8f0;
    --text-muted:  #64748b;
    --text-dim:    #94a3b8;
    --mono:        'JetBrains Mono', monospace;
    --serif:       'DM Serif Display', Georgia, serif;
    --sans:        'Inter', system-ui, sans-serif;
}

html, body, [class*="css"] {
    font-family: var(--sans) !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}
.stApp { background: var(--bg) !important; }
#MainMenu, footer, header { visibility: hidden !important; }
.block-container { padding: 1.5rem 2rem 3rem !important; max-width: 1400px !important; }

[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: var(--surface2) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: var(--sans) !important;
    font-size: 0.95rem !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-glow) !important;
    outline: none !important;
}

.stButton > button {
    background: var(--accent) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: var(--sans) !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.03em !important;
    padding: 0.6rem 1.4rem !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: var(--accent2) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(59,130,246,0.35) !important;
}

.stSelectbox > div > div,
.stNumberInput > div > div > input {
    background: var(--surface2) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
}

.streamlit-expanderHeader {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text-dim) !important;
    font-family: var(--mono) !important;
    font-size: 0.82rem !important;
}
.streamlit-expanderContent {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-top: none !important;
    border-radius: 0 0 8px 8px !important;
}

hr { border-color: var(--border) !important; margin: 1.5rem 0 !important; }

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }

.agent-header {
    display: flex; align-items: center; gap: 16px;
    padding: 2rem 0 1.5rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 2rem;
}
.agent-logo {
    width: 52px; height: 52px;
    background: linear-gradient(135deg, #1d4ed8 0%, #3b82f6 100%);
    border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.6rem;
    box-shadow: 0 8px 24px rgba(59,130,246,0.3);
    flex-shrink: 0;
}
.agent-title {
    font-family: var(--serif) !important;
    font-size: 2rem !important;
    font-weight: 400 !important;
    color: var(--text) !important;
    line-height: 1.1 !important;
    margin: 0 !important;
}
.agent-subtitle {
    font-family: var(--mono) !important;
    font-size: 0.72rem !important;
    color: var(--text-muted) !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    margin-top: 4px !important;
}
.status-badge {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 4px 12px; border-radius: 20px;
    font-family: var(--mono) !important;
    font-size: 0.72rem !important; font-weight: 500 !important;
    letter-spacing: 0.06em !important;
}
.status-online  { background: rgba(16,185,129,0.12); color: #10b981; border: 1px solid rgba(16,185,129,0.25); }
.status-offline { background: rgba(239,68,68,0.12);  color: #ef4444; border: 1px solid rgba(239,68,68,0.25); }
.status-dot { width: 6px; height: 6px; border-radius: 50%; background: currentColor; }

.answer-card {
    background: var(--surface);
    border: 1px solid var(--border2);
    border-left: 3px solid var(--accent);
    border-radius: 12px;
    padding: 1.5rem 1.75rem;
    margin: 1rem 0;
}
.answer-card h4 {
    font-family: var(--mono) !important;
    font-size: 0.7rem !important; letter-spacing: 0.12em !important;
    color: var(--accent2) !important; text-transform: uppercase !important;
    margin: 0 0 0.75rem !important;
}
.answer-card p {
    font-size: 0.975rem !important; line-height: 1.7 !important;
    color: var(--text) !important; margin: 0 !important;
}

.trace-step {
    display: flex; gap: 12px;
    padding: 10px 14px; border-radius: 8px; margin-bottom: 6px;
    background: var(--surface2); border: 1px solid var(--border);
    font-family: var(--mono) !important; font-size: 0.78rem !important;
}
.step-num   { color: var(--text-muted); min-width: 28px; font-weight: 500; }
.step-action { color: var(--accent2); font-weight: 500; min-width: 110px; }
.step-thought { color: var(--text-dim); flex: 1; }

.action-chip {
    display: inline-block; padding: 2px 8px; border-radius: 4px;
    font-family: var(--mono) !important;
    font-size: 0.7rem !important; font-weight: 500 !important;
}
.chip-search  { background: rgba(245,158,11,0.12); color: #f59e0b; }
.chip-read    { background: rgba(99,102,241,0.12);  color: #818cf8; }
.chip-summary { background: rgba(20,184,166,0.12);  color: #2dd4bf; }
.chip-final   { background: rgba(16,185,129,0.12);  color: #10b981; }
.chip-error   { background: rgba(239,68,68,0.12);   color: #f87171; }

.source-pill {
    display: inline-block; padding: 4px 10px;
    background: var(--surface2); border: 1px solid var(--border2);
    border-radius: 6px;
    font-family: var(--mono) !important; font-size: 0.72rem !important;
    color: var(--accent2) !important; margin: 3px 3px 0 0;
    word-break: break-all; text-decoration: none;
}

.metric-row { display: flex; gap: 12px; flex-wrap: wrap; margin: 0.75rem 0; }
.metric-box {
    flex: 1; min-width: 100px;
    background: var(--surface2); border: 1px solid var(--border);
    border-radius: 10px; padding: 12px 16px; text-align: center;
}
.metric-val {
    font-family: var(--mono) !important; font-size: 1.4rem !important;
    font-weight: 400 !important; color: var(--accent2) !important;
}
.metric-label {
    font-size: 0.68rem !important; color: var(--text-muted) !important;
    text-transform: uppercase !important; letter-spacing: 0.1em !important; margin-top: 2px !important;
}

.history-item {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 10px; padding: 14px 16px; margin-bottom: 10px;
}
.history-q   { font-size: 0.88rem !important; color: var(--text) !important; font-weight: 500 !important; margin-bottom: 4px !important; }
.history-meta { font-family: var(--mono) !important; font-size: 0.68rem !important; color: var(--text-muted) !important; }

.thinking-anim {
    display: flex; align-items: center; gap: 10px;
    padding: 1.2rem 1.5rem;
    background: var(--surface); border: 1px solid var(--border2);
    border-radius: 10px; margin: 1rem 0;
    font-family: var(--mono) !important; font-size: 0.82rem !important;
    color: var(--text-dim) !important;
}
.pulse-dot {
    width: 8px; height: 8px; border-radius: 50%; background: var(--accent);
    animation: pulse 1.4s ease-in-out infinite;
}
@keyframes pulse {
    0%,100% { opacity:1; transform:scale(1); }
    50%      { opacity:0.4; transform:scale(0.7); }
}
.section-label {
    font-family: var(--mono) !important;
    font-size: 0.68rem !important; letter-spacing: 0.14em !important;
    text-transform: uppercase !important; color: var(--text-muted) !important;
    margin: 1.25rem 0 0.6rem !important;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════════════════
def init_state():
    defaults = {
        "history":     [],
        "api_key":     "",
        "model":       "meta-llama/llama-3.1-8b-instruct",
        "backend":     "http://localhost:8000",
        "max_steps":   12,
        "debug":       True,
        "running":     False,
        "last_result": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# ══════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════
CHIP_MAP = {
    "search_web":        ("🔍", "chip-search",  "search_web"),
    "read_page":         ("📄", "chip-read",    "read_page"),
    "summarize":         ("✏️", "chip-summary", "summarize"),
    "final_answer":      ("✅", "chip-final",   "final_answer"),
    "parse_error":       ("⚠️", "chip-error",   "parse_error"),
    "duplicate_blocked": ("🔁", "chip-error",   "duplicate"),
}

def action_chip(name: str) -> str:
    icon, cls, label = CHIP_MAP.get(name, ("❓", "chip-error", name))
    return f'<span class="action-chip {cls}">{icon} {label}</span>'

def check_backend(url: str) -> bool:
    try:
        r = req.get(f"{url}/health", timeout=4)
        return r.status_code == 200
    except Exception:
        return False

def push_config(url: str, api_key: str, model: str):
    try:
        r = req.post(f"{url}/config", params={"api_key": api_key, "model": model}, timeout=6)
        return r.status_code == 200, r.json() if r.ok else r.text
    except Exception as e:
        return False, str(e)

def ask_agent(url: str, question: str, debug: bool = True, max_steps: int = 12):
    params = {"q": question, "debug": str(debug).lower(), "max_steps": max_steps}
    r = req.get(f"{url}/ask", params=params, timeout=180)
    r.raise_for_status()
    return r.json()

def render_trace(trace: list):
    if not trace:
        st.markdown('<p class="section-label">No trace available</p>', unsafe_allow_html=True)
        return
    for step in trace:
        stype   = step.get("type", "")
        action  = step.get("action", stype or "?")
        thought = step.get("thought", "")
        obs     = step.get("observation", "")
        args    = step.get("args", {})
        step_n  = step.get("step", "?")

        chip    = action_chip(action)
        arg_str = ""
        if args:
            first_val = next(iter(args.values()), "")
            if isinstance(first_val, str) and first_val:
                arg_str = (
                    f' — <span style="color:#94a3b8">'
                    f'{first_val[:80]}{"…" if len(first_val) > 80 else ""}</span>'
                )

        st.markdown(
            f'<div class="trace-step">'
            f'<span class="step-num">#{step_n}</span>'
            f'<span class="step-action">{chip}{arg_str}</span>'
            f'<span class="step-thought">'
            f'{thought[:120]}{"…" if len(thought) > 120 else ""}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
        if obs and obs != "✓ Done":
            with st.expander(f"Observation · step {step_n}", expanded=False):
                try:
                    st.json(json.loads(obs.rstrip("...")))
                except Exception:
                    st.code(obs, language=None)

def render_sources(sources: list):
    if not sources:
        return
    pills = " ".join(
        f'<a href="{s}" target="_blank" class="source-pill">'
        f'{s[:55]}{"…" if len(s) > 55 else ""}</a>'
        for s in sources
    )
    st.markdown(f'<div>{pills}</div>', unsafe_allow_html=True)

def render_result(result: dict, question: str):
    if "error" in result:
        st.error(f"**Agent error:** {result['error']}")
        return

    answer  = result.get("answer", "")
    sources = result.get("sources", [])
    trace   = result.get("trace", [])
    steps   = result.get("steps_taken", "?")
    warning = result.get("warning", "")

    # Metrics
    st.markdown(
        f'<div class="metric-row">'
        f'<div class="metric-box"><div class="metric-val">{steps}</div>'
        f'<div class="metric-label">Steps</div></div>'
        f'<div class="metric-box"><div class="metric-val">{len(sources)}</div>'
        f'<div class="metric-label">Sources</div></div>'
        f'<div class="metric-box"><div class="metric-val">{len(trace)}</div>'
        f'<div class="metric-label">Actions</div></div>'
        f'<div class="metric-box"><div class="metric-val">{len(answer)}</div>'
        f'<div class="metric-label">Chars</div></div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    if warning:
        st.warning(f"⚠️ {warning.replace('_', ' ').title()}")

    st.markdown('<p class="section-label">Answer</p>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="answer-card"><h4>Research Result</h4><p>{answer}</p></div>',
        unsafe_allow_html=True,
    )

    if sources:
        st.markdown('<p class="section-label">Sources consulted</p>', unsafe_allow_html=True)
        render_sources(sources)

    if trace:
        st.markdown('<p class="section-label">Reasoning trace</p>', unsafe_allow_html=True)
        render_trace(trace)

    with st.expander("📦 Raw JSON response", expanded=False):
        st.json(result)


# ══════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="padding:1.2rem 0 1rem;">
        <p style="font-family:'DM Serif Display',serif;font-size:1.15rem;margin:0;color:#e2e8f0;">
            ⚙ Configuration
        </p>
        <p style="font-family:'JetBrains Mono',monospace;font-size:0.68rem;
                  color:#475569;letter-spacing:0.1em;margin:3px 0 0;">AGENT · SETTINGS</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="section-label">Backend URL</p>', unsafe_allow_html=True)
    backend_url = st.text_input(
        "API URL", value=st.session_state.backend,
        placeholder="http://localhost:8000", label_visibility="collapsed"
    )
    st.session_state.backend = backend_url.rstrip("/")

    online = check_backend(st.session_state.backend)
    badge_cls = "status-online" if online else "status-offline"
    badge_txt = "Online" if online else "Offline"
    st.markdown(
        f'<div class="status-badge {badge_cls}">'
        f'<span class="status-dot"></span>{badge_txt}</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<p class="section-label">OpenRouter API Key</p>', unsafe_allow_html=True)
    api_key = st.text_input(
        "API Key", type="password", value=st.session_state.api_key,
        placeholder="sk-or-...", label_visibility="collapsed"
    )
    st.session_state.api_key = api_key

    st.markdown('<p class="section-label">Model</p>', unsafe_allow_html=True)
    model_options = [
        "meta-llama/llama-3.1-8b-instruct",
        "meta-llama/llama-3.1-70b-instruct",
        "mistralai/mistral-7b-instruct",
        "mistralai/mixtral-8x7b-instruct",
        "anthropic/claude-3.5-sonnet",
        "openai/gpt-4o-mini",
        "openai/gpt-4o",
    ]
    model = st.selectbox(
        "Model", options=model_options,
        index=model_options.index(st.session_state.model)
              if st.session_state.model in model_options else 0,
        label_visibility="collapsed",
    )
    st.session_state.model = model

    st.markdown('<p class="section-label">Max steps</p>', unsafe_allow_html=True)
    max_steps = st.slider(
        "Max steps", 4, 20, st.session_state.max_steps,
        label_visibility="collapsed"
    )
    st.session_state.max_steps = max_steps

    debug_mode = st.toggle("Show reasoning trace", value=st.session_state.debug)
    st.session_state.debug = debug_mode

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Apply Config", use_container_width=True):
            if not api_key:
                st.error("API key required.")
            else:
                ok, resp = push_config(st.session_state.backend, api_key, model)
                if ok:
                    st.success("Config applied ✓")
                else:
                    st.error(f"Failed: {resp}")
    with col2:
        if st.button("Recheck", use_container_width=True):
            st.rerun()

    st.divider()

    if st.session_state.history:
        st.markdown('<p class="section-label">Recent queries</p>', unsafe_allow_html=True)
        for item in reversed(st.session_state.history[-8:]):
            q_short = item["q"][:52] + ("…" if len(item["q"]) > 52 else "")
            ts      = item.get("ts", "")
            st.markdown(
                f'<div class="history-item">'
                f'<div class="history-q">{q_short}</div>'
                f'<div class="history-meta">{ts}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        if st.button("Clear history", use_container_width=True):
            st.session_state.history = []
            st.rerun()


# ══════════════════════════════════════════════════════════════
#  MAIN PANEL
# ══════════════════════════════════════════════════════════════
st.markdown("""
<div class="agent-header">
    <div class="agent-logo">🔬</div>
    <div>
        <h1 class="agent-title">ReAct Research Agent</h1>
        <p class="agent-subtitle">Autonomous · Multi-Step · Web-Grounded</p>
    </div>
</div>
""", unsafe_allow_html=True)

col_q, col_btn = st.columns([5, 1])
with col_q:
    question = st.text_input(
        "Research question",
        placeholder="e.g.  What are the latest breakthroughs in nuclear fusion energy?",
        label_visibility="collapsed",
        disabled=st.session_state.running,
    )
with col_btn:
    run_btn = st.button(
        "Research",
        use_container_width=True,
        disabled=st.session_state.running or not question.strip(),
    )

# Example prompts
examples = [
    "Latest advances in quantum computing 2025",
    "How does CRISPR gene editing work?",
    "Best open-source LLMs available today",
    "Impact of AI on the job market",
]
ex_cols = st.columns(len(examples))
for col, ex in zip(ex_cols, examples):
    with col:
        if st.button(ex, key=f"ex_{ex[:20]}", use_container_width=True,
                     disabled=st.session_state.running):
            question = ex
            run_btn  = True

st.divider()


# ══════════════════════════════════════════════════════════════
#  RUN AGENT
# ══════════════════════════════════════════════════════════════
if run_btn and question.strip():
    if not online:
        st.error("❌ Backend is offline. Start the FastAPI server and click **Recheck**.")
    elif not st.session_state.api_key:
        st.error("🔑 Enter your OpenRouter API key in the sidebar and click **Apply Config**.")
    else:
        st.session_state.running = True
        thinking_ph = st.empty()
        thinking_ph.markdown(
            '<div class="thinking-anim">'
            '<div class="pulse-dot"></div>'
            'Researching autonomously — this may take 30–90 seconds…'
            '</div>',
            unsafe_allow_html=True,
        )

        start = time.time()
        try:
            with st.spinner(""):
                result = ask_agent(
                    st.session_state.backend,
                    question.strip(),
                    debug=True,
                    max_steps=st.session_state.max_steps,
                )
        except req.exceptions.ConnectionError:
            result = {"error": "Cannot connect to backend. Is it running?"}
        except req.exceptions.Timeout:
            result = {"error": "Request timed out (>180 s). Try fewer max_steps."}
        except Exception as e:
            result = {"error": str(e)}

        elapsed = time.time() - start
        thinking_ph.empty()
        st.session_state.history.append({
            "q":      question.strip(),
            "result": result,
            "ts":     datetime.now().strftime("%H:%M · %b %d"),
        })
        st.session_state.last_result = (question.strip(), result)
        st.session_state.running     = False

        st.markdown(
            f'<p style="font-family:\'JetBrains Mono\',monospace;font-size:0.72rem;'
            f'color:#475569;margin-bottom:0.5rem;">Completed in {elapsed:.1f}s</p>',
            unsafe_allow_html=True,
        )

        if not st.session_state.debug:
            result.pop("trace", None)
        render_result(result, question.strip())

elif st.session_state.last_result:
    q, result = st.session_state.last_result
    st.markdown(
        f'<p style="font-family:\'JetBrains Mono\',monospace;font-size:0.72rem;'
        f'color:#475569;margin-bottom:1rem;">Last query: {q}</p>',
        unsafe_allow_html=True,
    )
    display_result = result if st.session_state.debug else {
        k: v for k, v in result.items() if k != "trace"
    }
    render_result(display_result, q)

else:
    st.markdown("""
    <div style="text-align:center;padding:4rem 2rem;">
        <div style="font-size:3.5rem;margin-bottom:1rem;">🔬</div>
        <p style="font-family:'DM Serif Display',serif;font-size:1.5rem;
                  color:#334155;margin:0 0 0.5rem;">
            Ask anything. The agent will figure it out.
        </p>
        <p style="font-family:'Inter',sans-serif;font-size:0.88rem;color:#475569;
                  max-width:480px;margin:0 auto;line-height:1.6;">
            Enter a question above or pick an example prompt.
            The ReAct loop searches the web, reads pages, and reasons step-by-step
            before delivering a grounded answer.
        </p>
    </div>
    """, unsafe_allow_html=True)