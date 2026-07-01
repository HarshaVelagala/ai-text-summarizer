"""
app.py  —  AI Text Summarizer + Plagiarism Checker
────────────────────────────────────────────────────
Run locally:
    streamlit run app.py

Deploy:
    Push to GitHub → connect on share.streamlit.io → add secrets → done.
"""

import json
import random
import streamlit as st
from datetime import datetime, timezone

# ── Page config (MUST be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="AI Text Summarizer",
    page_icon="✦",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── General ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 820px; }

/* ── Hide default Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }

/* ── Hero ── */
.hero { text-align: center; padding: 1.5rem 0 1rem; }
.hero h1 { font-size: 2rem; font-weight: 700; color: #1a1a2e; margin-bottom: .4rem; }
.hero p  { color: #6b7280; font-size: 1rem; line-height: 1.6; }
.badge {
    display: inline-block; background: #EEEDFE; color: #534AB7;
    font-size: .72rem; font-weight: 600; padding: 4px 14px;
    border-radius: 20px; margin-bottom: 14px; letter-spacing: .03em;
}

/* ── Cards ── */
.card {
    background: #fff; border: 1px solid #e5e7eb;
    border-radius: 16px; padding: 1.4rem 1.5rem; margin-bottom: 1rem;
}
.card-title {
    font-size: .7rem; font-weight: 600; color: #9ca3af;
    text-transform: uppercase; letter-spacing: .06em; margin-bottom: .6rem;
}

/* ── Summary result tabs ── */
.result-wrap {
    background: #fff; border: 1px solid #e5e7eb;
    border-radius: 16px; padding: 1.5rem; margin-top: .5rem;
}
.result-header {
    display: flex; justify-content: space-between;
    align-items: center; margin-bottom: 1rem; flex-wrap: wrap; gap: .5rem;
}
.type-badge {
    background: #EEEDFE; color: #534AB7; font-size: .72rem;
    font-weight: 600; padding: 3px 12px; border-radius: 20px;
}
.summary-text { font-size: .9rem; line-height: 1.8; color: #374151; }
.bullet-item {
    display: flex; gap: .5rem; font-size: .9rem;
    line-height: 1.7; color: #374151; margin-bottom: .3rem;
}
.bullet-dot { color: #7F77DD; font-weight: 700; flex-shrink: 0; }
.takeaway-item {
    background: #F5F3FF; border-left: 3px solid #7F77DD;
    border-radius: 0 10px 10px 0; padding: 10px 14px;
    font-size: .88rem; color: #374151; margin-bottom: .5rem; line-height: 1.6;
}

/* ── Stats row ── */
.stats-row { display: grid; grid-template-columns: repeat(3,1fr); gap: 10px; margin-top: 1rem; }
.stat-card {
    background: #F9F8FF; border-radius: 12px;
    padding: 10px 14px; text-align: center;
}
.stat-label { font-size: .7rem; color: #9ca3af; font-weight: 500; margin-bottom: 2px; }
.stat-value { font-size: 1.3rem; font-weight: 700; color: #534AB7; }

/* ── Plagiarism CTA ── */
.plag-cta {
    background: linear-gradient(135deg,#7F77DD 0%,#6356C9 60%,#3C3489 100%);
    border-radius: 18px; padding: 1.6rem 1.8rem; margin: 1.5rem 0;
    cursor: pointer; position: relative; overflow: hidden;
}
.plag-cta-title { color: #fff; font-size: 1.1rem; font-weight: 700; margin-bottom: 4px; }
.plag-cta-desc  { color: #D5D2F7; font-size: .88rem; line-height: 1.5; }
.plag-new-badge {
    display: inline-block; background: rgba(255,255,255,.2); color: #fff;
    font-size: .65rem; font-weight: 700; padding: 2px 8px;
    border-radius: 20px; margin-left: 8px; vertical-align: middle;
}

/* ── Gauge ── */
.gauge-wrap { text-align: center; padding: 1rem 0; }
.gauge-score { font-size: 2.8rem; font-weight: 800; }
.gauge-label { font-size: .9rem; font-weight: 600; padding: 4px 16px; border-radius: 20px; display: inline-block; margin-top: 6px; }

/* ── Compare cards ── */
.compare-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-top: 1rem; }
@media(max-width:600px){ .compare-grid{ grid-template-columns:1fr; } }
.compare-card { border-radius: 16px; padding: 1.2rem; position: relative; overflow: hidden; }
.compare-card.ai     { background: #FFF5F5; border: 2px solid #FECACA; }
.compare-card.human  { background: #F0FDF4; border: 2px solid #A7F3D0; }
.compare-bar { height: 4px; border-radius: 4px; margin-bottom: 10px; }
.compare-bar.ai    { background: linear-gradient(90deg,#f87171,#ef4444); }
.compare-bar.human { background: linear-gradient(90deg,#34d399,#22c55e); }
.compare-tag { font-size: .72rem; font-weight: 700; padding: 4px 10px; border-radius: 20px; display: inline-block; margin-bottom: 10px; }
.compare-tag.ai    { background: #FEE2E2; color: #EF4444; }
.compare-tag.human { background: #D1FAE5; color: #059669; }
.compare-text { font-size: .85rem; line-height: 1.7; max-height: 260px; overflow-y: auto; }
.compare-text.ai    { color: #6b7280; }
.compare-text.human { color: #1f2937; }

/* ── Transform header ── */
.transform-header {
    display: flex; justify-content: center; margin-bottom: 1.2rem;
}
.transform-card {
    display: inline-flex; align-items: center; gap: 1.2rem;
    background: #fff; border: 1px solid #e5e7eb;
    border-radius: 16px; padding: 14px 24px;
}
.transform-stat { text-align: center; }
.transform-label { font-size: .65rem; color: #9ca3af; font-weight: 600; text-transform: uppercase; letter-spacing: .05em; }
.transform-value { font-size: 1.8rem; font-weight: 800; }
.transform-drop { font-size: .72rem; font-weight: 700; color: #059669; }

/* ── Flagged phrases ── */
.flagged-box {
    background: #FFFBEB; border: 1px solid #FDE68A;
    border-radius: 10px; padding: 10px 14px; margin-bottom: 8px;
}
.flagged-phrase { font-size: .88rem; color: #92400E; font-style: italic; font-weight: 500; }
.flagged-reason { font-size: .75rem; color: #B45309; margin-top: 3px; }

/* ── History ── */
.history-item {
    background: #fff; border: 1px solid #e5e7eb;
    border-radius: 14px; padding: 1rem 1.2rem; margin-bottom: .75rem;
}
.history-type {
    font-size: .7rem; font-weight: 600; background: #EEEDFE; color: #534AB7;
    padding: 3px 10px; border-radius: 20px; display: inline-block; margin-bottom: 6px;
}
.history-preview { font-size: .88rem; color: #6b7280; line-height: 1.5; }
.history-date { font-size: .72rem; color: #d1d5db; margin-top: 6px; }

/* ── Footer ── */
.footer {
    text-align: center; padding: 1.5rem 0 .5rem;
    border-top: 1px solid #f3f4f6; margin-top: 2rem;
}
.footer-text { font-size: .8rem; color: #9ca3af; margin-bottom: .8rem; }
.social-link {
    display: inline-flex; align-items: center; gap: 6px;
    color: #7F77DD; text-decoration: none; font-size: .85rem;
    font-weight: 500; padding: 6px 14px; border-radius: 10px;
    background: #F5F3FF; margin: 0 4px; transition: all .2s;
}
.social-link:hover { background: #EEEDFE; }

/* ── Buttons (override Streamlit) ── */
div[data-testid="stButton"] > button {
    border-radius: 12px !important; font-weight: 600 !important;
    transition: all .2s !important;
}
div[data-testid="stButton"] > button:first-child {
    background-color: #7F77DD !important; color: white !important;
    border: none !important; padding: .5rem 1.5rem !important;
}
div[data-testid="stButton"] > button:hover {
    background-color: #534AB7 !important; box-shadow: 0 4px 14px rgba(127,119,221,.35) !important;
}

/* ── Tabs ── */
div[data-testid="stTabs"] button {
    font-size: .88rem !important; font-weight: 500 !important;
}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIG & HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

MAX_CHARS = 10_000

def get_secret(key: str, fallback: str = "") -> str:
    """Read from st.secrets (cloud) with a graceful fallback."""
    try:
        return st.secrets[key]
    except Exception:
        return fallback

OPENAI_KEY  = get_secret("OPENAI_API_KEY")
MONGODB_URL = get_secret("MONGODB_URL")
MONGODB_DB  = get_secret("MONGODB_DB", "ai_summarizer")
IS_MOCK     = not OPENAI_KEY or OPENAI_KEY.startswith("sk-your")


# ── MongoDB ───────────────────────────────────────────────────────────────────

@st.cache_resource
def get_mongo():
    """Cached MongoDB client — one connection for the whole session."""
    if not MONGODB_URL or MONGODB_URL.startswith("mongodb+srv://user"):
        return None
    try:
        import pymongo
        client = pymongo.MongoClient(MONGODB_URL, serverSelectionTimeoutMS=3000)
        client.admin.command("ping")
        return client[MONGODB_DB]
    except Exception:
        return None


def save_to_db(collection: str, doc: dict):
    db = get_mongo()
    if db:
        try:
            db[collection].insert_one(doc)
        except Exception:
            pass  # DB errors are non-fatal


def load_history(limit: int = 20) -> list:
    db = get_mongo()
    if not db:
        return []
    try:
        cursor = db["summaries"].find(
            {}, {"original_text": 0}
        ).sort("created_at", -1).limit(limit)
        return list(cursor)
    except Exception:
        return []


# ═══════════════════════════════════════════════════════════════════════════════
# AI SERVICE LAYER
# ═══════════════════════════════════════════════════════════════════════════════

def call_openai(prompt: str, temperature: float = 0.3) -> dict:
    """Call OpenAI and return parsed JSON dict."""
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_KEY)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)


# ── Mock responses ─────────────────────────────────────────────────────────────

def mock_summary(summary_type: str) -> dict:
    base = {
        "short": "This text explores several important ideas, highlighting key trends and practical implications for readers to consider.",
        "detailed": (
            "The text provides a comprehensive overview of the subject matter, drawing on multiple perspectives to build a nuanced argument. "
            "The author begins by establishing context, explaining why this topic is relevant and timely.\n\n"
            "In the central sections, the author examines core concepts in detail, providing examples and evidence to support each claim. "
            "This analytical depth helps readers develop a thorough understanding of the material.\n\n"
            "The conclusion synthesizes key ideas, offering practical implications and suggesting directions for further exploration."
        ),
        "bullets": [
            "The text introduces a multifaceted topic framed within a broader context.",
            "Key concepts are examined with supporting evidence and real-world examples.",
            "The author presents contrasting viewpoints to provide a balanced perspective.",
            "Practical applications link theory to real-world scenarios.",
            "The conclusion reinforces the main arguments and suggests next steps.",
        ],
        "takeaways": [
            "Understanding context is essential before drawing conclusions on complex topics.",
            "Evidence-based reasoning leads to more reliable insights.",
            "Applying these concepts can lead to measurable improvements in practice.",
        ],
    }
    return base if summary_type == "all" else {summary_type: base[summary_type]}


def mock_plagiarism_check(text: str) -> dict:
    ai_phrases = ["in conclusion", "moreover", "it is important to note",
                  "furthermore", "overall", "in today's world", "delve into"]
    hits = sum(1 for p in ai_phrases if p in text.lower())
    score = min(95, 35 + hits * 15 + random.randint(-5, 8))
    score = max(5, score)
    verdict = ("Likely AI-Generated" if score >= 65
               else "Mixed / Uncertain" if score >= 35 else "Likely Human")
    flagged = []
    words = text.split()
    if hits and len(words) > 12:
        flagged.append({"phrase": " ".join(words[:8]), "reason": "Generic phrasing common in AI-generated text"})
    return {"ai_likelihood_score": score, "verdict": verdict,
            "explanation": "This text shows patterns associated with AI-generated writing." if score >= 50
            else "This text shows natural variation consistent with human writing.",
            "flagged_phrases": flagged}


def mock_humanize(text: str) -> str:
    replacements = {
        "In conclusion, ": "So, ", "in conclusion, ": "so, ",
        "Moreover, ": "Also, ", "moreover, ": "also, ",
        "It is important to note that ": "Worth noting: ",
        "it is important to note that ": "worth noting: ",
        "Furthermore, ": "Plus, ", "furthermore, ": "plus, ",
        "delve into": "dig into",
    }
    result = text
    for old, new in replacements.items():
        result = result.replace(old, new)
    return result


# ── Real AI functions ──────────────────────────────────────────────────────────

def generate_summary(text: str, summary_type: str) -> dict:
    if IS_MOCK:
        return mock_summary(summary_type)

    type_instructions = {
        "all": ('Return JSON with keys: "short" (1-2 sentence overview, max 60 words), '
                '"detailed" (3-5 paragraph summary), "bullets" (array of 5-7 strings), '
                '"takeaways" (array of 3-5 actionable insight strings).'),
        "short":     'Return JSON: {"short": "1-2 sentence overview, max 60 words"}',
        "detailed":  'Return JSON: {"detailed": "3-5 paragraph in-depth summary"}',
        "bullets":   'Return JSON: {"bullets": ["point 1", ...]} with 5-7 items',
        "takeaways": 'Return JSON: {"takeaways": ["insight 1", ...]} with 3-5 items',
    }
    prompt = f"""Summarize the text below.

{type_instructions[summary_type]}
Respond with ONLY valid JSON, no markdown, no preamble.

TEXT:
{text}"""
    return call_openai(prompt, temperature=0.3)


def check_plagiarism(text: str) -> dict:
    if IS_MOCK:
        return mock_plagiarism_check(text)

    prompt = f"""You are an AI content detector. Analyze the text and estimate how likely it was AI-generated.

Return ONLY valid JSON:
{{"ai_likelihood_score": <0-100>, "verdict": "<Likely Human|Mixed / Uncertain|Likely AI-Generated>",
"explanation": "<2-3 sentences>",
"flagged_phrases": [{{"phrase": "<excerpt max 12 words>", "reason": "<why it reads as AI>"}}]}}

Include 0-4 flagged_phrases. No markdown.

TEXT:
{text}"""
    return call_openai(prompt, temperature=0.2)


def humanize_text(text: str) -> str:
    if IS_MOCK:
        return mock_humanize(text)

    prompt = f"""Rewrite the text below to read as natural human writing, not AI-generated.

- Vary sentence lengths and rhythm naturally
- Replace generic phrases ("In conclusion", "Moreover") with natural transitions
- Add a personal voice where appropriate
- Preserve the original meaning and length
- Do NOT add a preamble

Return ONLY valid JSON: {{"humanized_text": "<rewritten text>"}}

TEXT:
{text}"""
    result = call_openai(prompt, temperature=0.7)
    return result["humanized_text"]


# ═══════════════════════════════════════════════════════════════════════════════
# UI COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════════

def render_score_gauge(score: int):
    color = "#ef4444" if score >= 65 else "#f59e0b" if score >= 35 else "#22c55e"
    label = "Likely AI-Generated" if score >= 65 else "Mixed / Uncertain" if score >= 35 else "Likely Human"
    label_bg = "#FEF2F2" if score >= 65 else "#FFFBEB" if score >= 35 else "#F0FDF4"

    # SVG gauge
    circumference = 2 * 3.14159 * 52
    offset = circumference - (score / 100) * circumference

    svg = f"""
    <div style="display:flex;flex-direction:column;align-items:center;padding:1.2rem 0">
      <svg width="140" height="140" style="transform:rotate(-90deg)">
        <circle cx="70" cy="70" r="52" fill="none" stroke="#f3f4f6" stroke-width="12"/>
        <circle cx="70" cy="70" r="52" fill="none" stroke="{color}" stroke-width="12"
          stroke-linecap="round" stroke-dasharray="{circumference:.1f}"
          stroke-dashoffset="{offset:.1f}"/>
      </svg>
      <div style="margin-top:-88px;text-align:center;pointer-events:none;padding-bottom:2.5rem">
        <div class="gauge-score" style="color:{color}">{score}%</div>
        <div style="font-size:.75rem;color:#9ca3af;font-weight:500">AI likelihood</div>
      </div>
      <span class="gauge-label" style="color:{color};background:{label_bg}">{label}</span>
    </div>
    """
    st.markdown(svg, unsafe_allow_html=True)


def render_summary_result(result: dict, summary_type: str):
    type_labels = {
        "all": "All summaries", "short": "Short summary",
        "detailed": "Detailed summary", "bullets": "Bullet points",
        "takeaways": "Key takeaways",
    }
    label = type_labels.get(summary_type, summary_type)

    # Build tab list
    tabs_to_show = []
    if result.get("short"):     tabs_to_show.append(("Short",     "short"))
    if result.get("detailed"):  tabs_to_show.append(("Detailed",  "detailed"))
    if result.get("bullets"):   tabs_to_show.append(("Bullets",   "bullets"))
    if result.get("takeaways"): tabs_to_show.append(("Takeaways", "takeaways"))

    if not tabs_to_show:
        st.warning("No summary content returned.")
        return

    st.markdown(f"""
    <div class="result-header">
      <span style="font-weight:600;font-size:1rem">Summary Result</span>
      <span class="type-badge">{label}</span>
    </div>
    """, unsafe_allow_html=True)

    tab_objects = st.tabs([t[0] for t in tabs_to_show])

    for tab_obj, (_, key) in zip(tab_objects, tabs_to_show):
        with tab_obj:
            if key == "short":
                st.markdown(f'<p class="summary-text">{result["short"]}</p>', unsafe_allow_html=True)

            elif key == "detailed":
                for para in result["detailed"].split("\n\n"):
                    st.markdown(f'<p class="summary-text">{para}</p>', unsafe_allow_html=True)

            elif key == "bullets":
                html = "".join(
                    f'<div class="bullet-item"><span class="bullet-dot">•</span><span>{b}</span></div>'
                    for b in result["bullets"]
                )
                st.markdown(html, unsafe_allow_html=True)

            elif key == "takeaways":
                html = "".join(
                    f'<div class="takeaway-item">{t}</div>'
                    for t in result["takeaways"]
                )
                st.markdown(html, unsafe_allow_html=True)

    # Stats
    orig_words    = len(st.session_state.get("last_input", "").split())
    summary_words = len((result.get("short") or result.get("detailed") or "").split())
    compression   = max(0, round((1 - summary_words / max(orig_words, 1)) * 100))
    time_saved    = max(1, round((orig_words - summary_words) / 200))

    st.markdown(f"""
    <div class="stats-row">
      <div class="stat-card"><div class="stat-label">Original words</div><div class="stat-value">{orig_words:,}</div></div>
      <div class="stat-card"><div class="stat-label">Compression</div><div class="stat-value">{compression}%</div></div>
      <div class="stat-card"><div class="stat-label">Time saved</div><div class="stat-value">{time_saved} min</div></div>
    </div>
    """, unsafe_allow_html=True)


def render_footer():
    st.markdown("""
    <div class="footer">
      <div class="footer-text">© 2026 AI Text Summarizer — built by Harsha Velagala</div>
      <a class="social-link" href="https://github.com/HarshaVelagala" target="_blank">
        <svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 .5C5.73.5.5 5.73.5 12c0 5.1 3.29 9.42 7.86 10.95.57.1.78-.25.78-.55
            0-.27-.01-1.17-.02-2.12-3.2.7-3.88-1.36-3.88-1.36-.52-1.33-1.28-1.68-1.28-1.68
            -1.04-.71.08-.7.08-.7 1.15.08 1.76 1.18 1.76 1.18 1.02 1.75 2.68 1.25 3.33.96
            .1-.74.4-1.25.72-1.54-2.55-.29-5.24-1.28-5.24-5.7 0-1.26.45-2.29 1.18-3.1
            -.12-.29-.51-1.46.11-3.05 0 0 .97-.31 3.18 1.18a11 11 0 0 1 5.79 0
            c2.2-1.49 3.17-1.18 3.17-1.18.63 1.59.24 2.76.12 3.05.74.81 1.18 1.84 1.18 3.1
            0 4.43-2.7 5.41-5.27 5.7.42.36.78 1.08.78 2.18 0 1.58-.01 2.85-.01 3.24
            0 .31.21.66.79.55A10.51 10.51 0 0 0 23.5 12C23.5 5.73 18.27.5 12 .5Z"/>
        </svg>
        GitHub
      </a>
      <a class="social-link" href="https://www.linkedin.com/in/harshavelagala" target="_blank">
        <svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24">
          <path d="M20.45 20.45h-3.56v-5.57c0-1.33-.02-3.04-1.85-3.04-1.85 0-2.14 1.45-2.14 2.94v5.67H9.34V9
            h3.41v1.56h.05c.48-.9 1.64-1.85 3.38-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28ZM5.34 7.43
            a2.06 2.06 0 1 1 0-4.12 2.06 2.06 0 0 1 0 4.12ZM7.12 20.45H3.56V9h3.56v11.45Z"/>
        </svg>
        LinkedIn
      </a>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# SESSION STATE INIT
# ═══════════════════════════════════════════════════════════════════════════════

for key, default in {
    "page": "summarizer",
    "summary_result": None,
    "last_input": "",
    "plag_check_result": None,
    "plag_humanize_result": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ═══════════════════════════════════════════════════════════════════════════════
# NAVIGATION
# ═══════════════════════════════════════════════════════════════════════════════

col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
with col1:
    st.markdown('<div style="font-size:1.1rem;font-weight:700;color:#534AB7;padding:.4rem 0">✦ AI Summarizer</div>', unsafe_allow_html=True)
with col2:
    if st.button("Summarize", use_container_width=True):
        st.session_state.page = "summarizer"
with col3:
    if st.button("Plagiarism", use_container_width=True):
        st.session_state.page = "plagiarism"
with col4:
    if st.button("History", use_container_width=True):
        st.session_state.page = "history"

st.markdown('<hr style="margin:.5rem 0 1.5rem;border-color:#f3f4f6">', unsafe_allow_html=True)

if IS_MOCK:
    st.info("🤖 **Mock mode** — no OpenAI key found. Add `OPENAI_API_KEY` to `.streamlit/secrets.toml` for real AI output.", icon="ℹ️")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: SUMMARIZER
# ═══════════════════════════════════════════════════════════════════════════════

if st.session_state.page == "summarizer":

    st.markdown("""
    <div class="hero">
      <div class="badge">Powered by OpenAI GPT-4o-mini</div>
      <h1>Summarize any text, instantly</h1>
      <p>Paste any article, essay, or report — get a short summary, detailed breakdown,<br>bullet points, or key takeaways in seconds.</p>
    </div>
    """, unsafe_allow_html=True)

    # Input
    text_input = st.text_area(
        "Your text",
        placeholder="Paste your text here — articles, research papers, meeting transcripts, reports…",
        height=220,
        max_chars=MAX_CHARS,
        label_visibility="collapsed",
    )

    # Meta row
    words = len(text_input.strip().split()) if text_input.strip() else 0
    chars = len(text_input)
    read_min = max(1, round(words / 200))
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Words", f"{words:,}")
    c2.metric("Characters", f"{chars:,}")
    c3.metric("Read time", f"~{read_min} min")
    c4.metric("Limit", f"{chars}/{MAX_CHARS:,}")

    # Controls
    col_sel, col_btn = st.columns([3, 1])
    with col_sel:
        summary_type = st.selectbox(
            "Summary type",
            options=["all", "short", "detailed", "bullets", "takeaways"],
            format_func=lambda x: {
                "all": "All summaries (short + detailed + bullets + takeaways)",
                "short": "Short summary only",
                "detailed": "Detailed summary only",
                "bullets": "Bullet point summary only",
                "takeaways": "Key takeaways only",
            }[x],
            label_visibility="collapsed",
        )
    with col_btn:
        summarize_clicked = st.button("✦ Summarize", use_container_width=True)

    if summarize_clicked:
        trimmed = text_input.strip()
        if not trimmed:
            st.error("Please paste some text first.")
        elif words < 10:
            st.error("Please enter at least 10 words.")
        else:
            st.session_state.last_input = trimmed
            with st.spinner("Generating summary…"):
                try:
                    result = generate_summary(trimmed[:MAX_CHARS], summary_type)
                    st.session_state.summary_result = result

                    # Save to MongoDB
                    save_to_db("summaries", {
                        "original_text": trimmed[:500],  # store preview only
                        "preview": trimmed[:150],
                        "summary_type": summary_type,
                        "summary": result,
                        "word_count": words,
                        "reading_time_minutes": read_min,
                        "created_at": datetime.now(timezone.utc),
                    })
                    st.success("Summary generated!", icon="✅")
                except Exception as e:
                    st.error(f"Error: {e}")

    # Show result
    if st.session_state.summary_result:
        render_summary_result(st.session_state.summary_result, summary_type)

        # Download + Copy
        full_text = ""
        r = st.session_state.summary_result
        if r.get("short"):     full_text += f"SHORT SUMMARY\n{r['short']}\n\n"
        if r.get("detailed"):  full_text += f"DETAILED SUMMARY\n{r['detailed']}\n\n"
        if r.get("bullets"):   full_text += "BULLET POINTS\n" + "\n".join(f"• {b}" for b in r["bullets"]) + "\n\n"
        if r.get("takeaways"): full_text += "KEY TAKEAWAYS\n" + "\n".join(f"{i+1}. {t}" for i,t in enumerate(r["takeaways"]))

        dl_col, _ = st.columns([1, 3])
        with dl_col:
            st.download_button(
                "⬇ Download .txt",
                data=full_text,
                file_name=f"summary-{summary_type}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True,
            )

    # ── Plagiarism CTA ────────────────────────────────────────────────────────
    st.markdown("""
    <div class="plag-cta">
      <div style="font-size:1.6rem;margin-bottom:.5rem">🛡️</div>
      <div class="plag-cta-title">AI Plagiarism Checker <span class="plag-new-badge">NEW</span></div>
      <div class="plag-cta-desc">
        Check if your text reads as AI-generated — then humanize it into natural,
        authentic writing in one click.
      </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("→ Try AI Plagiarism Checker", use_container_width=True):
        st.session_state.page = "plagiarism"
        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: AI PLAGIARISM CHECKER
# ═══════════════════════════════════════════════════════════════════════════════

elif st.session_state.page == "plagiarism":

    st.markdown("""
    <div class="hero">
      <div class="badge">🛡️ AI Plagiarism Checker</div>
      <h1>Is your text AI-generated?</h1>
      <p>Paste your text to get an AI-likelihood score.<br>
         If it reads too robotic, humanize it into natural writing in one click.</p>
    </div>
    """, unsafe_allow_html=True)

    plag_text = st.text_area(
        "Text to analyze",
        placeholder="Paste an essay, article, or any text you want to check…",
        height=200,
        max_chars=MAX_CHARS,
        label_visibility="collapsed",
    )

    p_words = len(plag_text.strip().split()) if plag_text.strip() else 0
    p_c1, p_c2 = st.columns(2)
    p_c1.metric("Words", f"{p_words:,}")
    p_c2.metric("Characters", f"{len(plag_text):,}")

    col_check, col_reset = st.columns([2, 1])
    with col_check:
        check_clicked = st.button("🔍 Check for AI", use_container_width=True)
    with col_reset:
        if st.button("↺ Reset", use_container_width=True):
            st.session_state.plag_check_result   = None
            st.session_state.plag_humanize_result = None
            st.rerun()

    if check_clicked:
        trimmed = plag_text.strip()
        if not trimmed:
            st.error("Please paste some text first.")
        elif p_words < 10:
            st.error("Please enter at least 10 words.")
        else:
            with st.spinner("Analyzing for AI patterns…"):
                try:
                    result = check_plagiarism(trimmed[:MAX_CHARS])
                    st.session_state.plag_check_result   = result
                    st.session_state.plag_humanize_result = None
                    st.success("Analysis complete!", icon="✅")
                except Exception as e:
                    st.error(f"Error: {e}")

    # ── Check result ──────────────────────────────────────────────────────────
    cr = st.session_state.plag_check_result
    if cr and not st.session_state.plag_humanize_result:

        render_score_gauge(cr["ai_likelihood_score"])

        st.markdown(
            f'<p style="text-align:center;font-size:.9rem;color:#6b7280;max-width:480px;margin:0 auto 1rem;line-height:1.6">'
            f'{cr["explanation"]}</p>',
            unsafe_allow_html=True
        )

        # Flagged phrases
        if cr.get("flagged_phrases"):
            st.markdown("**Flagged phrases**")
            for f in cr["flagged_phrases"]:
                st.markdown(
                    f'<div class="flagged-box">'
                    f'<div class="flagged-phrase">"{f["phrase"]}"</div>'
                    f'<div class="flagged-reason">{f["reason"]}</div></div>',
                    unsafe_allow_html=True
                )

        # Humanize button
        if cr["ai_likelihood_score"] >= 25:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("✨ Humanize this text", use_container_width=False):
                with st.spinner("Rewriting text into natural human writing…"):
                    try:
                        trimmed = plag_text.strip()
                        humanized = humanize_text(trimmed[:MAX_CHARS])
                        after_check = check_plagiarism(humanized)
                        st.session_state.plag_humanize_result = {
                            "original_text":  trimmed,
                            "humanized_text": humanized,
                            "original_score": cr["ai_likelihood_score"],
                            "new_score":      after_check["ai_likelihood_score"],
                        }
                        st.success("Text humanized!", icon="✅")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

    # ── Humanize result ────────────────────────────────────────────────────────
    hr = st.session_state.plag_humanize_result
    if hr:
        drop = max(0, hr["original_score"] - hr["new_score"])

        st.markdown(f"""
        <div class="transform-header">
          <div class="transform-card">
            <div class="transform-stat">
              <div class="transform-label">Before</div>
              <div class="transform-value" style="color:#ef4444">{hr['original_score']}%</div>
            </div>
            <div style="text-align:center;padding:0 6px">
              <div style="font-size:1.4rem">→</div>
              <div class="transform-drop">−{drop}%</div>
            </div>
            <div class="transform-stat">
              <div class="transform-label">After</div>
              <div class="transform-value" style="color:#22c55e">{hr['new_score']}%</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="compare-grid">
          <div class="compare-card ai">
            <div class="compare-bar ai"></div>
            <span class="compare-tag ai">🤖 AI PLAGIARISM</span>
            <div class="compare-text ai">{hr['original_text'][:800]}</div>
          </div>
          <div class="compare-card human">
            <div class="compare-bar human"></div>
            <span class="compare-tag human">✓ NON-AI PLAGIARISM</span>
            <div class="compare-text human">{hr['humanized_text'][:800]}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        dl2_col, recheck_col, reset_col = st.columns(3)

        with dl2_col:
            st.download_button(
                "⬇ Download humanized",
                data=hr["humanized_text"],
                file_name=f"humanized-{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True,
            )
        with recheck_col:
            if st.button("🔄 Re-check humanized", use_container_width=True):
                # Load humanized text back into check
                st.session_state.plag_check_result = {
                    "ai_likelihood_score": hr["new_score"],
                    "verdict": ("Likely AI-Generated" if hr["new_score"] >= 65
                                else "Mixed / Uncertain" if hr["new_score"] >= 35
                                else "Likely Human"),
                    "explanation": "This is the re-scored humanized version of your text.",
                    "flagged_phrases": [],
                }
                st.session_state.plag_humanize_result = None
                st.rerun()
        with reset_col:
            if st.button("✕ Start over", use_container_width=True):
                st.session_state.plag_check_result   = None
                st.session_state.plag_humanize_result = None
                st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: HISTORY
# ═══════════════════════════════════════════════════════════════════════════════

elif st.session_state.page == "history":

    st.markdown("## History")
    st.markdown("Your recent summaries saved to MongoDB.")

    items = load_history(limit=20)

    if not items:
        st.markdown("""
        <div style="text-align:center;padding:4rem 1rem;color:#9ca3af">
          <div style="font-size:3rem;margin-bottom:.8rem">📋</div>
          <div style="font-size:1rem;font-weight:500">No summaries yet</div>
          <div style="font-size:.85rem;margin-top:.3rem">Generate your first summary and it'll appear here.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        type_labels = {
            "all": "All summaries", "short": "Short", "detailed": "Detailed",
            "bullets": "Bullets", "takeaways": "Takeaways",
        }
        for item in items:
            created = item.get("created_at")
            date_str = created.strftime("%b %d, %Y · %H:%M") if created else "—"
            stype = item.get("summary_type", "all")
            preview = item.get("preview", "")
            wcount = item.get("word_count", 0)

            st.markdown(f"""
            <div class="history-item">
              <span class="history-type">{type_labels.get(stype, stype)}</span>
              <div class="history-preview">{preview}…</div>
              <div class="history-date">{date_str} · {wcount:,} words</div>
            </div>
            """, unsafe_allow_html=True)


# ── Footer (shown on all pages) ───────────────────────────────────────────────
render_footer()
