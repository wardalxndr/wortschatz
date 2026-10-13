"""WortSchatz — German dictionary, Reikun-style landing.

Search-first hero, example pills, gender-colored entries,
compound breakdown chips, CEFR-aware grammar explain (Groq, on demand),
feedback logging. Run from repo root: streamlit run app/app.py
(NOTE: restart the server after changing .streamlit/config.toml)
"""

import csv
import os
import sys
import time
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ingest"))
sys.path.insert(0, os.path.join(ROOT, "rag"))

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from build_index import build_index, vocab
from dictionary import WortSearch, explain
from splitter import split_compound
from words import WORDS

load_dotenv()

BY_ID = {w["id"]: w for w in WORDS}
FEEDBACK_CSV = os.path.join(ROOT, "data", "feedback.csv")
GENDER_STYLE = {
    "m": ("der", "#1d4ed8"),
    "f": ("die", "#dc2626"),
    "n": ("das", "#15803a"),
}
EXAMPLES = ["apple", "Handschuh", "Donaudampfschifffahrt", "how do you say hospital"]


@st.cache_resource
def get_search():
    return WortSearch(build_index(WORDS))


def get_client():
    return OpenAI(
        base_url=os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1"),
        api_key=os.getenv("GROQ_API_KEY", ""),
    )


def log_feedback(query, level, rating):
    os.makedirs(os.path.dirname(FEEDBACK_CSV), exist_ok=True)
    new_file = not os.path.exists(FEEDBACK_CSV)
    with open(FEEDBACK_CSV, "a", newline="") as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow(["timestamp", "level", "query", "rating"])
        writer.writerow([datetime.now(timezone.utc).isoformat(), level, query, rating])


st.set_page_config(page_title="WortSchatz — German dictionary", page_icon="📖", layout="centered")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    h1, h2, h3 { font-family: 'Space Grotesk', sans-serif !important; letter-spacing: -0.02em; }
    code, pre { font-family: 'JetBrains Mono', monospace !important; }
    .stButton > button { border-radius: 999px; font-weight: 600; }
    div[data-testid="stExpander"] { background: #ffffff; border: 1px solid #e7e0d3; border-radius: 16px; }
    .hero-badge {
        display: inline-block; font-family: 'JetBrains Mono', monospace;
        font-size: 12px; letter-spacing: 0.14em; text-transform: uppercase;
        color: #57534e; border: 1px solid #e7e0d3; background: #ffffff;
        border-radius: 999px; padding: 4px 14px;
    }
    .entry-card {
        background: #ffffff; border: 1px solid #e7e0d3; border-radius: 16px;
        padding: 16px 18px; margin-bottom: 12px;
        box-shadow: 0 6px 20px rgba(28, 25, 23, 0.06);
    }
    .chip {
        display: inline-block; border: 1px solid #e7e0d3; background: #fcfaf6;
        border-radius: 999px; padding: 3px 12px; margin: 2px 4px 2px 0;
        font-family: 'JetBrains Mono', monospace; font-size: 13px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

top_left, top_right = st.columns([3, 1])
with top_left:
    st.markdown("<span class='hero-badge'>📖 german dictionary</span>", unsafe_allow_html=True)
with top_right:
    st.markdown("<div style='text-align: right; padding-top: 4px;'>", unsafe_allow_html=True)
    st.markdown("<span style='color:#16a34a; font-weight:700;'>● Online</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.title("WortSchatz")
st.caption("Search English or German, inspect gender and plurals, split compound words, get grammar explanations tuned to your CEFR level.")
st.caption(f"📚 {len(WORDS)} seed words · 🔗 compound splitter · 🎚️ CEFR-aware explanations")

level = st.selectbox("My CEFR level (for grammar explanations)", ["A1", "A2", "B1", "B2", "C1"], index=0)
query = st.text_input("Search", placeholder="e.g.: apple, Handschuh, Donaudampfschifffahrt", key="q_input", label_visibility="collapsed")

if st.button("🔍 Search", type="primary", use_container_width=True):
    st.session_state["ran"] = query

st.caption("Try:")
pill_cols = st.columns(len(EXAMPLES))
for col, ex in zip(pill_cols, EXAMPLES):
    if col.button(ex, use_container_width=True):
        st.session_state["q_input"] = ex
        st.session_state["ran"] = ex

if st.session_state.get("ran"):
    q = (st.session_state["ran"] or "").strip()
    if q:
        search = get_search()
        t0 = time.perf_counter()
        results = search.search(q, num_results=5)
        latency = time.perf_counter() - t0

        # Compound breakdown: the wow demo (Donaudampfschifffahrt!)
        parts = split_compound(q, vocab())
        if len(parts) > 1:
            st.subheader("🔗 Compound breakdown")
            chips = " ".join(f"<span class='chip'>{p}</span>" for p in parts)
            st.markdown(chips, unsafe_allow_html=True)
            for p in parts:
                hit = BY_ID.get(p)
                if hit:
                    gname = GENDER_STYLE.get(hit.get("gender", ""), (hit.get("pos", ""), ""))[0]
                    st.caption(f"`{p}` → {hit['de']} ({gname}): {hit['en']}")
            st.divider()

        st.caption(f"⏱ {latency:.2f}s · 📎 {len(results)} results · 🎚️ level {level}")
        for i, r in enumerate(results):
            g = r.get("gender", "")
            gname, gcolor = GENDER_STYLE.get(g, (r.get("pos", ""), "#57534e"))
            head = f"<span style='color:{gcolor}; font-weight:700;'>{gname}</span> <b>{r['de']}</b>" if g else f"<b>{r['de']}</b>"
            plural = f" · pl. <code>{r['plural']}</code>" if r.get("plural") and r["plural"] != "-" else ""
            st.markdown(
                f"<div class='entry-card'>{head}<br>"
                f"<span style='color:#57534e;'>{r['en']}{plural}</span> · "
                f"<span class='chip'>{r.get('cefr', '')}</span><br>"
                f"<span style='color:#78716c; font-size:13px;'>{r.get('note', '')}</span></div>",
                unsafe_allow_html=True,
            )
            if st.button(f"✨ Explain for {level}", key=f"explain_{i}_{r['id']}"):
                if not os.getenv("GROQ_API_KEY"):
                    st.error("GROQ_API_KEY is missing. Copy .env.example to .env first.")
                else:
                    with st.spinner("Explaining..."):
                        text = explain(get_client(), os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"), q, [r], level)
                    st.markdown(text)

        c1, c2 = st.columns(2)
        if c1.button("👍 Helpful", use_container_width=True, key="fb_up"):
            log_feedback(q, level, "up")
            st.success("Thanks, logged for evaluation.")
        if c2.button("👎 Not quite", use_container_width=True, key="fb_down"):
            log_feedback(q, level, "down")
            st.success("Logged, thanks.")

st.divider()
st.caption("Seed dictionary: hand-built high-frequency words (gender/plural/CEFR approximate — verify before citing). Queries are logged locally (data/feedback.csv) to improve ranking — no account, no tracking.")
