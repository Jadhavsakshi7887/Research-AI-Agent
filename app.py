"""
╔══════════════════════════════════════════════════════════════╗
║   ReAct Research Agent  — fully self-contained single file   ║
║   Run:  streamlit run app.py                                 ║
╚══════════════════════════════════════════════════════════════╝

No FastAPI. No separate server.
The entire ReAct loop + tools run directly inside Streamlit.
"""

# ══════════════════════════════════════════════════════════════
#  IMPORTS
# ══════════════════════════════════════════════════════════════
import streamlit as st
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import json
import re
import os
import time
import logging
from datetime import datetime
from urllib.parse import quote_plus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════
#  PAGE CONFIG  (must be first Streamlit call)
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="ReAct Research Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ══════════════════════════════════════════════════════════════
#  CSS — dark editorial aesthetic
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

.stSelectbox > div > div {
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

/* ── Live step card ── */
.live-step {
    display: flex; align-items: flex-start; gap: 14px;
    padding: 12px 16px; border-radius: 10px; margin-bottom: 8px;
    background: var(--surface2); border: 1px solid var(--border2);
    animation: fadeIn 0.3s ease;
}
@keyframes fadeIn { from { opacity:0; transform:translateY(6px); } to { opacity:1; transform:translateY(0); } }
.live-step-icon { font-size: 1.1rem; margin-top: 1px; flex-shrink: 0; }
.live-step-body { flex: 1; }
.live-step-action {
    font-family: var(--mono) !important; font-size: 0.72rem !important;
    font-weight: 600 !important; letter-spacing: 0.08em !important;
    text-transform: uppercase !important; margin-bottom: 3px !important;
}
.live-step-thought {
    font-size: 0.875rem !important; color: var(--text-dim) !important;
    line-height: 1.5 !important;
}
.live-step-obs {
    font-family: var(--mono) !important; font-size: 0.73rem !important;
    color: var(--text-muted) !important; margin-top: 4px !important;
    padding: 4px 8px; background: var(--surface); border-radius: 4px;
    border-left: 2px solid var(--border2);
}

/* ── Action colours ── */
.col-search  { color: #f59e0b; }
.col-read    { color: #818cf8; }
.col-summary { color: #2dd4bf; }
.col-final   { color: #10b981; }
.col-error   { color: #f87171; }
.col-default { color: var(--accent2); }

/* ── Answer card ── */
.answer-card {
    background: var(--surface);
    border: 1px solid var(--border2);
    border-left: 3px solid var(--accent);
    border-radius: 12px;
    padding: 1.5rem 1.75rem;
    margin: 1rem 0;
}
.answer-card h4 {
    font-family: var(--mono) !important; font-size: 0.7rem !important;
    letter-spacing: 0.12em !important; color: var(--accent2) !important;
    text-transform: uppercase !important; margin: 0 0 0.75rem !important;
}
.answer-card p {
    font-size: 0.975rem !important; line-height: 1.75 !important;
    color: var(--text) !important; margin: 0 !important;
    white-space: pre-wrap !important;
}

/* ── Metrics ── */
.metric-row { display: flex; gap: 12px; flex-wrap: wrap; margin: 0.75rem 0; }
.metric-box {
    flex: 1; min-width: 90px;
    background: var(--surface2); border: 1px solid var(--border);
    border-radius: 10px; padding: 12px 16px; text-align: center;
}
.metric-val {
    font-family: var(--mono) !important; font-size: 1.4rem !important;
    font-weight: 400 !important; color: var(--accent2) !important;
}
.metric-label {
    font-size: 0.68rem !important; color: var(--text-muted) !important;
    text-transform: uppercase !important; letter-spacing: 0.1em !important;
    margin-top: 2px !important;
}

/* ── Source pills ── */
.source-pill {
    display: inline-block; padding: 4px 10px;
    background: var(--surface2); border: 1px solid var(--border2);
    border-radius: 6px; font-family: var(--mono) !important;
    font-size: 0.72rem !important; color: var(--accent2) !important;
    margin: 3px 3px 0 0; word-break: break-all; text-decoration: none;
}

/* ── History ── */
.history-item {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 10px; padding: 12px 14px; margin-bottom: 8px;
}
.history-q   { font-size: 0.875rem !important; color: var(--text) !important; font-weight: 500 !important; margin-bottom: 3px !important; }
.history-meta { font-family: var(--mono) !important; font-size: 0.68rem !important; color: var(--text-muted) !important; }

/* ── Section label ── */
.section-label {
    font-family: var(--mono) !important; font-size: 0.68rem !important;
    letter-spacing: 0.14em !important; text-transform: uppercase !important;
    color: var(--text-muted) !important; margin: 1.25rem 0 0.6rem !important;
}

/* ── Agent header ── */
.agent-header {
    display: flex; align-items: center; gap: 16px;
    padding: 2rem 0 1.5rem; border-bottom: 1px solid var(--border);
    margin-bottom: 2rem;
}
.agent-logo {
    width: 52px; height: 52px;
    background: linear-gradient(135deg, #1d4ed8 0%, #3b82f6 100%);
    border-radius: 14px; display: flex; align-items: center;
    justify-content: center; font-size: 1.6rem;
    box-shadow: 0 8px 24px rgba(59,130,246,0.3); flex-shrink: 0;
}
.agent-title {
    font-family: var(--serif) !important; font-size: 2rem !important;
    font-weight: 400 !important; color: var(--text) !important;
    line-height: 1.1 !important; margin: 0 !important;
}
.agent-subtitle {
    font-family: var(--mono) !important; font-size: 0.72rem !important;
    color: var(--text-muted) !important; letter-spacing: 0.12em !important;
    text-transform: uppercase !important; margin-top: 4px !important;
}

/* ── Progress bar ── */
.stProgress > div > div > div { background: var(--accent) !important; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════════════════
def init_state():
    defaults = {
        "api_key":     "",
        "model":       "meta-llama/llama-3.1-8b-instruct",
        "max_steps":   12,
        "show_trace":  True,
        "history":     [],
        "last_result": None,
        "running":     False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# ══════════════════════════════════════════════════════════════
#  AGENT CONFIG  (module-level, updated at runtime)
# ══════════════════════════════════════════════════════════════
OBS_HISTORY_LIMIT  = 600
OBS_CURRENT_LIMIT  = 3000
PAGE_CONTENT_LIMIT = 2500
MAX_CONTEXT_MSGS   = 12

SYSTEM_PROMPT = """You are an autonomous research agent. Follow the ReAct loop:
THOUGHT → ACTION → OBSERVATION → repeat until done.

Output ONLY a single JSON object each turn:
{"thought": "reasoning", "action": "tool_name", "args": {...}}

Tools:
  search_web(query)             — DuckDuckGo search, returns URLs + snippets
  read_page(url)                — Fetch webpage text
  summarize(text, context)      — Summarize long text
  final_answer(answer, sources) — Submit answer (ends loop)

Rules:
- Always search first, then read at least 2 pages before answering.
- Keep thoughts SHORT (1-2 sentences) to save tokens.
- Never repeat the same action + args.
- Output ONLY valid JSON. No markdown. No extra text."""


# ══════════════════════════════════════════════════════════════
#  LLM CLIENT
# ══════════════════════════════════════════════════════════════
def get_client(api_key: str) -> OpenAI:
    if not api_key or not api_key.strip():
        raise ValueError("OpenRouter API key is not set. Enter it in the sidebar.")
    return OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key.strip())


# ══════════════════════════════════════════════════════════════
#  TOOLS
# ══════════════════════════════════════════════════════════════
def search_web(query: str) -> dict:
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}
    try:
        url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        results = []
        for result in soup.select(".result")[:5]:
            title_el   = result.select_one(".result__title a")
            snippet_el = result.select_one(".result__snippet")
            if not title_el:
                continue
            href = title_el.get("href", "")
            if "uddg=" in href:
                m = re.search(r"uddg=([^&]+)", href)
                href = requests.utils.unquote(m.group(1)) if m else ""
            results.append({
                "title":   title_el.get_text(strip=True),
                "url":     href,
                "snippet": (snippet_el.get_text(strip=True) if snippet_el else "")[:200],
            })
        return {"query": query, "results": results, "count": len(results)}
    except Exception as e:
        return {"query": query, "results": [], "error": str(e)}


def read_page(url: str) -> dict:
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}
    try:
        r = requests.get(url, headers=headers, timeout=12)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header",
                          "aside", "iframe", "noscript"]):
            tag.decompose()
        main = (
            soup.find("article") or soup.find("main")
            or soup.find(id=re.compile(r"content|article|main", re.I))
            or soup.find(class_=re.compile(r"content|article|post|entry", re.I))
            or soup.body
        )
        text = (main or soup).get_text(separator="\n", strip=True)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r" {2,}", " ", text)
        return {
            "url":         url,
            "content":     text[:PAGE_CONTENT_LIMIT],
            "total_chars": len(text),
            "truncated":   len(text) > PAGE_CONTENT_LIMIT,
        }
    except Exception as e:
        return {"url": url, "content": "", "error": str(e)}


def summarize(text: str, context: str = "", api_key: str = "", model: str = "") -> dict:
    prompt = (
        f"Summarize concisely, focusing on: {context}\n\n{text[:3000]}"
        if context else
        f"Summarize this text in 2-3 paragraphs:\n\n{text[:3000]}"
    )
    try:
        client = get_client(api_key)
        res = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=400,
        )
        return {"summary": res.choices[0].message.content.strip()}
    except Exception as e:
        return {"summary": text[:800], "error": str(e)}


def final_answer(answer: str, sources: list = None) -> dict:
    return {
        "answer":    answer,
        "sources":   sources or [],
        "timestamp": datetime.utcnow().isoformat(),
    }


def build_tools(api_key: str, model: str) -> dict:
    """Build TOOLS dict with closures capturing api_key + model."""
    return {
        "search_web": {
            "description": "Search DuckDuckGo. Returns top 5 URLs + snippets.",
            "fn": search_web,
        },
        "read_page": {
            "description": "Fetch and extract text from a URL.",
            "fn": read_page,
        },
        "summarize": {
            "description": "Summarize long text (use after read_page).",
            "fn": lambda text, context="": summarize(text, context, api_key, model),
        },
        "final_answer": {
            "description": "Submit final answer — ends the loop.",
            "fn": lambda answer, sources=None: final_answer(answer, sources),
        },
    }


# ══════════════════════════════════════════════════════════════
#  TOKEN BUDGET HELPERS
# ══════════════════════════════════════════════════════════════
def compress_observation(obs_str: str, is_latest: bool) -> str:
    limit = OBS_CURRENT_LIMIT if is_latest else OBS_HISTORY_LIMIT
    if len(obs_str) <= limit:
        return obs_str
    return obs_str[:limit] + f"... [trimmed, {len(obs_str) - limit} chars omitted]"


def sliding_window_messages(messages: list, question_msg: dict) -> list:
    fixed   = [{"role": "system", "content": SYSTEM_PROMPT}, question_msg]
    dynamic = messages[2:]
    if len(dynamic) <= MAX_CONTEXT_MSGS:
        return fixed + dynamic
    trimmed = dynamic[-MAX_CONTEXT_MSGS:]
    note = {
        "role": "user",
        "content": (
            f"[Note: {len(dynamic) - MAX_CONTEXT_MSGS} earlier steps trimmed. "
            "Continue from current knowledge.]"
        ),
    }
    return fixed + [note] + trimmed


def parse_agent_response(raw: str) -> dict:
    raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        return json.loads(match.group())
    raise ValueError(f"No JSON found in: {raw[:200]!r}")


# ══════════════════════════════════════════════════════════════
#  LIVE STEP RENDERER
# ══════════════════════════════════════════════════════════════
STEP_META = {
    "search_web":        ("🔍", "col-search",  "SEARCH WEB"),
    "read_page":         ("📄", "col-read",    "READ PAGE"),
    "summarize":         ("✏️", "col-summary", "SUMMARIZE"),
    "final_answer":      ("✅", "col-final",   "FINAL ANSWER"),
    "parse_error":       ("⚠️", "col-error",   "PARSE ERROR"),
    "duplicate_blocked": ("🔁", "col-error",   "DUPLICATE"),
}

def render_live_step(icon, col_cls, action_label, thought, obs_preview=""):
    obs_html = (
        f'<div class="live-step-obs">{obs_preview[:160]}{"…" if len(obs_preview)>160 else ""}</div>'
        if obs_preview else ""
    )
    return (
        f'<div class="live-step">'
        f'  <div class="live-step-icon">{icon}</div>'
        f'  <div class="live-step-body">'
        f'    <div class="live-step-action {col_cls}">{action_label}</div>'
        f'    <div class="live-step-thought">{thought}</div>'
        f'    {obs_html}'
        f'  </div>'
        f'</div>'
    )


# ══════════════════════════════════════════════════════════════
#  CORE AGENT — yields steps live
# ══════════════════════════════════════════════════════════════
def run_react_agent_live(question: str, api_key: str, model: str, max_steps: int):
    """
    Generator — yields dicts:
      {"type": "step",   "data": {...}}   — one ReAct step completed
      {"type": "result", "data": {...}}   — final answer
      {"type": "error",  "data": str}     — fatal error
    """
    try:
        client = get_client(api_key)
    except ValueError as e:
        yield {"type": "error", "data": str(e)}
        return

    TOOLS = build_tools(api_key, model)

    question_msg = {
        "role": "user",
        "content": f"Question: {question}\nResearch this autonomously and give a comprehensive answer.",
    }
    all_messages = [{"role": "system", "content": SYSTEM_PROMPT}, question_msg]

    trace        = []
    sources_used = []
    parse_errors = 0
    seen_actions = set()

    for step in range(1, max_steps + 1):
        windowed = sliding_window_messages(all_messages, question_msg)

        # ── LLM call ──
        try:
            res = client.chat.completions.create(
                model=model,
                messages=windowed,
                temperature=0.3,
                max_tokens=500,
            )
            raw = res.choices[0].message.content.strip()
        except Exception as e:
            err = str(e)
            hint = " (Upgrade OpenRouter or use a smaller model)" if "402" in err or "token" in err.lower() else ""
            yield {"type": "error", "data": f"LLM call failed at step {step}: {err}{hint}"}
            return

        # ── Parse ──
        try:
            agent_out    = parse_agent_response(raw)
            parse_errors = 0
        except (json.JSONDecodeError, ValueError):
            parse_errors += 1
            step_data = {"step": step, "type": "parse_error", "thought": "Could not parse LLM response as JSON.", "action": "parse_error", "args": {}, "obs_preview": raw[:120]}
            trace.append(step_data)
            yield {"type": "step", "data": step_data}
            if parse_errors >= 3:
                break
            all_messages.append({"role": "assistant", "content": raw})
            all_messages.append({"role": "user", "content": 'Invalid JSON. Reply ONLY with: {"thought":"...","action":"...","args":{...}}'})
            continue

        thought     = agent_out.get("thought", "")
        action_name = agent_out.get("action", "").strip()
        args        = agent_out.get("args", {})

        # ── Duplicate guard ──
        action_key = f"{action_name}:{json.dumps(args, sort_keys=True)}"
        if action_key in seen_actions:
            all_messages.append({"role": "assistant", "content": raw})
            all_messages.append({"role": "user", "content": "Already did this. Choose a different action or arguments."})
            step_data = {"step": step, "type": "duplicate_blocked", "thought": thought, "action": "duplicate_blocked", "args": args, "obs_preview": "Skipped — duplicate action."}
            trace.append(step_data)
            yield {"type": "step", "data": step_data}
            continue
        seen_actions.add(action_key)

        # ── Validate tool ──
        if action_name not in TOOLS:
            obs = f"Unknown tool '{action_name}'. Available: {list(TOOLS.keys())}"
            all_messages.append({"role": "assistant", "content": raw})
            all_messages.append({"role": "user", "content": f"Observation: {obs}"})
            step_data = {"step": step, "thought": thought, "action": action_name, "args": args, "obs_preview": obs}
            trace.append(step_data)
            yield {"type": "step", "data": step_data}
            continue

        # ── Emit step (before execution so UI shows it immediately) ──
        step_data = {"step": step, "thought": thought, "action": action_name, "args": args, "obs_preview": "Running…"}
        yield {"type": "step", "data": step_data}

        # ── Execute tool ──
        try:
            result = TOOLS[action_name]["fn"](**args)
        except TypeError as e:
            obs = f"Wrong args for {action_name}: {e}"
            all_messages.append({"role": "assistant", "content": raw})
            all_messages.append({"role": "user", "content": f"Observation: {obs}"})
            step_data["obs_preview"] = obs
            trace[-1] = step_data if trace and trace[-1].get("step") == step else step_data
            trace.append(step_data)
            yield {"type": "step_update", "data": step_data}
            continue
        except Exception as e:
            obs = f"Tool error: {e}"
            all_messages.append({"role": "assistant", "content": raw})
            all_messages.append({"role": "user", "content": f"Observation: {obs}"})
            step_data["obs_preview"] = obs
            trace.append(step_data)
            yield {"type": "step_update", "data": step_data}
            continue

        # ── Final answer? ──
        if action_name == "final_answer":
            result["trace"]       = trace
            result["steps_taken"] = step
            result["sources"]     = list(dict.fromkeys(sources_used + (result.get("sources") or [])))
            yield {"type": "result", "data": result}
            return

        # ── Collect sources ──
        if action_name == "search_web":
            for r in result.get("results", []):
                if r.get("url"):
                    sources_used.append(r["url"])
        if action_name == "read_page" and args.get("url"):
            sources_used.append(args["url"])

        # ── Observation preview for UI ──
        if action_name == "search_web":
            titles = [r.get("title", "") for r in result.get("results", [])]
            obs_preview = "Found: " + " · ".join(titles[:3])
        elif action_name == "read_page":
            content = result.get("content", "")
            obs_preview = content[:160].replace("\n", " ")
        elif action_name == "summarize":
            obs_preview = result.get("summary", "")[:160]
        else:
            obs_preview = json.dumps(result)[:160]

        step_data["obs_preview"] = obs_preview
        trace.append(step_data)
        yield {"type": "step_update", "data": step_data}

        # ── Build message ──
        obs_str     = json.dumps(result, ensure_ascii=False)
        obs_for_msg = compress_observation(obs_str, is_latest=True)
        all_messages.append({"role": "assistant", "content": raw})
        all_messages.append({"role": "user", "content": f"Observation from {action_name}:\n{obs_for_msg}"})

        # Compress older observations
        for i, msg in enumerate(all_messages[:-2]):
            if msg["role"] == "user" and msg["content"].startswith("Observation from"):
                lines = msg["content"].split("\n", 1)
                if len(lines) > 1 and len(lines[1]) > OBS_HISTORY_LIMIT:
                    all_messages[i]["content"] = (
                        lines[0] + "\n" + lines[1][:OBS_HISTORY_LIMIT] + "... [compressed]"
                    )

        time.sleep(0.2)

    # Max steps reached
    yield {
        "type": "result",
        "data": {
            "answer":      "Agent reached the step limit without a conclusive answer. Try increasing Max Steps.",
            "sources":     list(dict.fromkeys(sources_used)),
            "trace":       trace,
            "steps_taken": max_steps,
            "warning":     "max_steps_reached",
        },
    }


# ══════════════════════════════════════════════════════════════
#  UI HELPERS
# ══════════════════════════════════════════════════════════════
def render_sources(sources: list):
    if not sources:
        return
    pills = " ".join(
        f'<a href="{s}" target="_blank" class="source-pill">'
        f'{s[:60]}{"…" if len(s)>60 else ""}</a>'
        for s in sources
    )
    st.markdown(f'<div style="margin-top:6px">{pills}</div>', unsafe_allow_html=True)


def render_final_result(result: dict):
    answer  = result.get("answer", "")
    sources = result.get("sources", [])
    trace   = result.get("trace", [])
    steps   = result.get("steps_taken", "?")
    warning = result.get("warning", "")

    st.markdown(
        f'<div class="metric-row">'
        f'<div class="metric-box"><div class="metric-val">{steps}</div><div class="metric-label">Steps</div></div>'
        f'<div class="metric-box"><div class="metric-val">{len(sources)}</div><div class="metric-label">Sources</div></div>'
        f'<div class="metric-box"><div class="metric-val">{len(trace)}</div><div class="metric-label">Actions</div></div>'
        f'<div class="metric-box"><div class="metric-val">{len(answer)}</div><div class="metric-label">Chars</div></div>'
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

    if st.session_state.show_trace and trace:
        st.markdown('<p class="section-label">Full reasoning trace</p>', unsafe_allow_html=True)
        for s in trace:
            icon, col_cls, label = STEP_META.get(s.get("action", ""), ("🔧", "col-default", s.get("action", "?").upper()))
            obs = s.get("obs_preview", "")
            st.markdown(render_live_step(icon, col_cls, label, s.get("thought", ""), obs), unsafe_allow_html=True)

    with st.expander("📦 Raw JSON", expanded=False):
        st.json(result)


# ══════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="padding:1.2rem 0 1rem;">
        <p style="font-family:'DM Serif Display',serif;font-size:1.15rem;margin:0;color:#e2e8f0;">⚙ Configuration</p>
        <p style="font-family:'JetBrains Mono',monospace;font-size:0.68rem;color:#475569;letter-spacing:0.1em;margin:3px 0 0;">AGENT · SETTINGS</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="section-label">OpenRouter API Key</p>', unsafe_allow_html=True)
    api_key = st.text_input(
        "API Key", type="password",
        value=st.session_state.api_key,
        placeholder="sk-or-v1-...",
        label_visibility="collapsed",
    )
    st.session_state.api_key = api_key

    if api_key:
        st.markdown(
            '<div style="display:inline-flex;align-items:center;gap:6px;padding:4px 12px;'
            'border-radius:20px;background:rgba(16,185,129,0.12);color:#10b981;'
            'border:1px solid rgba(16,185,129,0.25);font-family:\'JetBrains Mono\',monospace;'
            'font-size:0.72rem;margin-bottom:8px;">'
            '<span style="width:6px;height:6px;border-radius:50%;background:#10b981;display:inline-block;"></span>'
            'Key provided</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div style="display:inline-flex;align-items:center;gap:6px;padding:4px 12px;'
            'border-radius:20px;background:rgba(239,68,68,0.12);color:#ef4444;'
            'border:1px solid rgba(239,68,68,0.25);font-family:\'JetBrains Mono\',monospace;'
            'font-size:0.72rem;margin-bottom:8px;">'
            '<span style="width:6px;height:6px;border-radius:50%;background:#ef4444;display:inline-block;"></span>'
            'No key set</div>',
            unsafe_allow_html=True,
        )

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

    st.markdown('<p class="section-label">Max reasoning steps</p>', unsafe_allow_html=True)
    max_steps = st.slider("Max steps", 4, 20, st.session_state.max_steps, label_visibility="collapsed")
    st.session_state.max_steps = max_steps

    show_trace = st.toggle("Show reasoning trace", value=st.session_state.show_trace)
    st.session_state.show_trace = show_trace

    st.divider()

    st.markdown("""
    <div style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:#475569;line-height:1.8;">
        <div style="color:#64748b;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:6px;">How it works</div>
        🔍 Searches DuckDuckGo<br>
        📄 Reads real web pages<br>
        🧠 Reasons step by step<br>
        ✅ Returns grounded answer
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    if st.session_state.history:
        st.markdown('<p class="section-label">Recent queries</p>', unsafe_allow_html=True)
        for item in reversed(st.session_state.history[-6:]):
            q_short = item["q"][:48] + ("…" if len(item["q"]) > 48 else "")
            st.markdown(
                f'<div class="history-item">'
                f'<div class="history-q">{q_short}</div>'
                f'<div class="history-meta">{item.get("ts", "")}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        if st.button("Clear history", use_container_width=True):
            st.session_state.history     = []
            st.session_state.last_result = None
            st.rerun()


# ══════════════════════════════════════════════════════════════
#  MAIN PANEL
# ══════════════════════════════════════════════════════════════
st.markdown("""
<div class="agent-header">
    <div class="agent-logo">🔬</div>
    <div>
        <h1 class="agent-title">ReAct Research Agent</h1>
        <p class="agent-subtitle">Autonomous · Multi-Step · Web-Grounded · Self-Contained</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Input row ──
col_q, col_btn = st.columns([5, 1])
with col_q:
    question = st.text_input(
        "question",
        placeholder="e.g.  What are the latest breakthroughs in nuclear fusion energy?",
        label_visibility="collapsed",
        disabled=st.session_state.running,
    )
with col_btn:
    run_btn = st.button(
        "Research ➜",
        use_container_width=True,
        disabled=st.session_state.running or not question.strip(),
    )

# ── Example prompts ──
examples = [
    "Latest advances in quantum computing 2025",
    "How does CRISPR gene editing work?",
    "Best open-source LLMs available today",
    "Impact of AI on global job market",
]
ex_cols = st.columns(len(examples))
for col, ex in zip(ex_cols, examples):
    with col:
        if st.button(ex, key=f"ex_{ex[:18]}", use_container_width=True,
                     disabled=st.session_state.running):
            question = ex
            run_btn  = True

st.divider()


# ══════════════════════════════════════════════════════════════
#  RUN — streaming live steps
# ══════════════════════════════════════════════════════════════
if run_btn and question.strip():
    if not st.session_state.api_key:
        st.error("🔑 Enter your OpenRouter API key in the sidebar first.")
    else:
        st.session_state.running = True
        start_ts = time.time()

        # ── Header ──
        st.markdown(
            f'<p class="section-label">Researching: {question.strip()}</p>',
            unsafe_allow_html=True,
        )

        prog_bar    = st.progress(0)
        steps_area  = st.container()   # live steps render here
        result_area = st.empty()       # final result replaces spinner

        step_placeholders = []         # one per step
        final_result      = None
        error_msg         = None
        step_count        = 0

        # ── Stream agent ──
        for event in run_react_agent_live(
            question.strip(),
            st.session_state.api_key,
            st.session_state.model,
            st.session_state.max_steps,
        ):
            etype = event["type"]
            data  = event["data"]

            if etype == "error":
                error_msg = data
                break

            elif etype in ("step", "step_update"):
                action = data.get("action", "unknown")
                thought = data.get("thought", "")
                obs     = data.get("obs_preview", "")
                icon, col_cls, label = STEP_META.get(action, ("🔧", "col-default", action.upper()))
                html = render_live_step(icon, col_cls, label, thought, obs)

                if etype == "step":
                    step_count += 1
                    prog_bar.progress(min(step_count / st.session_state.max_steps, 0.95))
                    with steps_area:
                        ph = st.empty()
                        ph.markdown(html, unsafe_allow_html=True)
                        step_placeholders.append(ph)
                else:
                    # Update the last placeholder with obs_preview filled in
                    if step_placeholders:
                        step_placeholders[-1].markdown(html, unsafe_allow_html=True)

            elif etype == "result":
                final_result = data
                prog_bar.progress(1.0)
                break

        elapsed = time.time() - start_ts
        st.session_state.running = False

        if error_msg:
            st.error(f"**Agent error:** {error_msg}")
        elif final_result:
            st.markdown(
                f'<p style="font-family:\'JetBrains Mono\',monospace;font-size:0.72rem;'
                f'color:#475569;margin:1rem 0 0.25rem;">Completed in {elapsed:.1f}s</p>',
                unsafe_allow_html=True,
            )
            st.divider()
            render_final_result(final_result)

            # Save to history
            st.session_state.history.append({
                "q":      question.strip(),
                "result": final_result,
                "ts":     datetime.now().strftime("%H:%M · %b %d"),
            })
            st.session_state.last_result = (question.strip(), final_result)

elif st.session_state.last_result:
    q, result = st.session_state.last_result
    st.markdown(
        f'<p style="font-family:\'JetBrains Mono\',monospace;font-size:0.72rem;'
        f'color:#475569;margin-bottom:1rem;">Last query: {q}</p>',
        unsafe_allow_html=True,
    )
    render_final_result(result)

else:
    # ── Empty state ──
    st.markdown("""
    <div style="text-align:center;padding:4rem 2rem;">
        <div style="font-size:3.5rem;margin-bottom:1rem;">🔬</div>
        <p style="font-family:'DM Serif Display',serif;font-size:1.5rem;color:#334155;margin:0 0 0.5rem;">
            Ask anything. The agent will figure it out.
        </p>
        <p style="font-family:'Inter',sans-serif;font-size:0.88rem;color:#475569;
                  max-width:520px;margin:0 auto;line-height:1.7;">
            Enter a research question above or pick an example prompt.
            The agent autonomously searches the web, reads pages, and reasons
            step-by-step — you can watch every thought as it happens.
        </p>
        <div style="margin-top:2rem;display:flex;justify-content:center;gap:2rem;
                    font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:#475569;">
            <span>🔍 Web search</span>
            <span>📄 Page reading</span>
            <span>🧠 LLM reasoning</span>
            <span>✅ Grounded answers</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
