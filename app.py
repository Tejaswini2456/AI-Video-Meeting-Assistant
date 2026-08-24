import sys
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import time
from utils.audio_processor import process_input
from core.transcriber import transcribe_all, get_transcription_engine
from core.summarizer import summarize, generate_title
from core.extractor import (
    extract_action_items,
    extract_key_decisions,
    extract_questions,
    extract_timestamped_topics,
)
from core.rag_engine import build_rag_chain, ask_question
from utils.exporter import generate_pdf_report, generate_markdown_report
from utils.history_manager import (
    save_meeting,
    load_all_meetings,
    get_meeting_by_id,
    delete_meeting,
)

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Video Assistant",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@300;400;500&display=swap');

:root {
    --bg: #0a0a0f;
    --surface: #111118;
    --surface-2: #1a1a25;
    --border: #2a2a3a;
    --accent: #7c3aed;
    --accent-glow: #9f67ff;
    --accent-2: #06b6d4;
    --text: #e8e8f0;
    --text-muted: #7070a0;
    --success: #10b981;
    --warning: #f59e0b;
    --danger: #ef4444;
}

html, body, [class*="css"] {
    font-family: 'JetBrains Mono', monospace;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

.stApp {
    background: var(--bg) !important;
}

.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background-image:
        linear-gradient(rgba(124, 58, 237, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(124, 58, 237, 0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
}

[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}

[data-testid="stSidebar"] * {
    color: var(--text) !important;
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Syne', sans-serif !important;
    color: var(--text) !important;
}

.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2rem, 5vw, 3.5rem);
    font-weight: 800;
    line-height: 1.1;
    margin: 0;
    background: linear-gradient(135deg, #ffffff 0%, var(--accent-glow) 50%, var(--accent-2) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: var(--text-muted);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-top: 0.5rem;
}

.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
}

.card:hover {
    border-color: var(--accent);
}

.card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    background: linear-gradient(180deg, var(--accent), var(--accent-2));
}

.card-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.card-content {
    font-size: 0.875rem;
    line-height: 1.7;
    color: var(--text);
}

.metric-card {
    background: var(--surface-2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem;
    text-align: center;
}
.metric-value {
    font-family: 'Syne', sans-serif;
    font-size: 1.4rem;
    font-weight: 800;
    color: var(--accent-glow);
}
.metric-label {
    font-size: 0.7rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

.badge {
    display: inline-block;
    padding: 0.2rem 0.6rem;
    border-radius: 4px;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

.badge-purple { background: rgba(124,58,237,0.2); color: var(--accent-glow); border: 1px solid rgba(124,58,237,0.3); }
.badge-cyan   { background: rgba(6,182,212,0.15); color: var(--accent-2);    border: 1px solid rgba(6,182,212,0.3); }
.badge-green  { background: rgba(16,185,129,0.15); color: var(--success);    border: 1px solid rgba(16,185,129,0.3); }

.stTextInput > div > div > input,
.stSelectbox > div > div {
    background: var(--surface-2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: 'JetBrains Mono', monospace !important;
}

.stButton > button {
    background: linear-gradient(135deg, var(--accent), #5b21b6) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.875rem !important;
    letter-spacing: 0.05em !important;
    padding: 0.6rem 1.5rem !important;
    transition: all 0.2s !important;
    text-transform: uppercase !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 25px rgba(124,58,237,0.4) !important;
}

.status-bar {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 1rem;
    background: var(--surface-2);
    border-radius: 8px;
    margin: 0.4rem 0;
    border: 1px solid var(--border);
    font-size: 0.8rem;
}

.status-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
}

.dot-active   { background: var(--accent-glow); box-shadow: 0 0 8px var(--accent-glow); animation: pulse 1.5s infinite; }
.dot-done     { background: var(--success); }
.dot-pending  { background: var(--border); }

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.4; }
}

.chat-container {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem;
    max-height: 420px;
    overflow-y: auto;
    margin-bottom: 1rem;
}

.chat-msg {
    margin-bottom: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.chat-label {
    font-size: 0.7rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
}

.chat-bubble {
    display: inline-block;
    padding: 0.75rem 1.1rem !important;
    border-radius: 10px !important;
    font-size: 0.9rem !important;
    line-height: 1.6 !important;
    max-width: 85% !important;
    color: #ffffff !important;
    word-break: break-word !important;
}

.user-label  { color: #c084fc !important; }
.bot-label   { color: #22d3ee !important; }

.user-bubble {
    background: linear-gradient(135deg, #6d28d9 0%, #4c1d95 100%) !important;
    border: 1px solid #a855f7 !important;
    color: #ffffff !important;
    align-self: flex-end !important;
    box-shadow: 0 4px 12px rgba(109, 40, 217, 0.35) !important;
}

.bot-bubble  {
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%) !important;
    border: 1px solid #06b6d4 !important;
    color: #ffffff !important;
    align-self: flex-start !important;
    box-shadow: 0 4px 12px rgba(6, 182, 212, 0.25) !important;
}

hr {
    border: none !important;
    border-top: 1px solid var(--border) !important;
    margin: 1.5rem 0 !important;
}

.transcript-box {
    background: var(--surface-2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.25rem;
    font-size: 0.82rem;
    line-height: 1.8;
    max-height: 300px;
    overflow-y: auto;
    color: var(--text-muted);
    white-space: pre-wrap;
    word-break: break-word;
}
</style>
""", unsafe_allow_html=True)

# ─── Session State Init ──────────────────────────────────────────────────────────
for key, default in {
    "result": None,
    "chat_history": [],
    "processing": False,
    "pipeline_done": False,
    "pipeline_steps": {},
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ─── Helpers ────────────────────────────────────────────────────────────────────
LANGUAGE_OPTIONS = {
    "🇬🇧 English": "english",
    "🇮🇳 Telugu (తెలుగు)": "telugu",
    "🇮🇳 Hindi / Hinglish (हिंदी)": "hinglish",
    "🇮🇳 Tamil (தமிழ்)": "tamil",
    "🇮🇳 Kannada (ಕನ್ನಡ)": "kannada",
    "🇮🇳 Malayalam (മലയാളം)": "malayalam",
    "🇮🇳 Bengali (বাংলা)": "bengali",
    "🇮🇳 Gujarati (ગુજરાતી)": "gujarati",
    "🇮🇳 Marathi (मराठी)": "marathi",
    "🇮🇳 Punjabi (ਪੰਜਾਬੀ)": "punjabi",
    "🌐 Auto-Detect / Global Language": "auto",
}

def step_status(steps: dict, key: str) -> str:
    s = steps.get(key, "pending")
    if s == "active":  return "dot-active"
    if s == "done":    return "dot-done"
    return "dot-pending"

def render_step_bar(label: str, key: str, icon: str):
    css = step_status(st.session_state.pipeline_steps, key)
    st.markdown(f"""
    <div class="status-bar">
        <div class="status-dot {css}"></div>
        <span>{icon} {label}</span>
    </div>""", unsafe_allow_html=True)

# ─── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="hero-title" style="font-size:1.6rem">🎬 AI<br>Video</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Meeting Intelligence</div>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown('<span class="badge badge-purple">Input Source</span>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload Media (.mp4, .mp3, .wav, .m4a)", type=["mp4", "mp3", "wav", "m4a", "webm"])
    url_input = st.text_input("Or paste YouTube URL", placeholder="https://youtube.com/watch?v=...")
    st.caption("💡 *Note: For uncaptioned YouTube videos, please use the File Uploader above.*")

    source = ""
    if uploaded_file is not None:
        save_dir = "downloades"
        os.makedirs(save_dir, exist_ok=True)
        source = os.path.join(save_dir, uploaded_file.name)
        uploaded_file.seek(0)
        with open(source, "wb") as f:
            f.write(uploaded_file.getbuffer())
    elif url_input.strip():
        source = url_input.strip()

    selected_lang_label = st.selectbox("Speech Language", list(LANGUAGE_OPTIONS.keys()), index=0)
    language = LANGUAGE_OPTIONS[selected_lang_label]

    # Engine indicator (High Contrast Badge)
    engine_name = get_transcription_engine(language)
    st.markdown(f"""
    <div style="
        background: rgba(124, 58, 237, 0.15);
        border: 1px solid rgba(124, 58, 237, 0.4);
        border-radius: 8px;
        padding: 0.5rem 0.75rem;
        margin-top: 0.4rem;
        margin-bottom: 0.8rem;
        font-size: 0.78rem;
        color: #e8e8f0;
        display: flex;
        align-items: center;
        gap: 0.4rem;
        word-break: break-word;
    ">
        <span>⚡ <strong>Engine:</strong></span>
        <span style="color:#9f67ff; font-weight:600">{engine_name}</span>
    </div>
    """, unsafe_allow_html=True)

    # ⚙️ Advanced Settings Expander
    with st.expander("⚙️ Advanced Settings", expanded=False):
        whisper_model_choice = st.selectbox("Whisper Model", ["small", "base", "tiny"], index=0)
        os.environ["WHISPER_MODEL"] = whisper_model_choice

    run_btn = st.button("⚡  Analyse", use_container_width=True)

    # 📚 Saved Meetings Library
    st.markdown("---")
    st.markdown('<span class="badge badge-cyan">📚 Saved Meetings</span>', unsafe_allow_html=True)
    saved_meetings = load_all_meetings()
    if saved_meetings:
        meeting_titles = {f"{m.get('title', 'Untitled')} ({m.get('timestamp', '')[:10]})": m['id'] for m in saved_meetings}
        selected_mtg_title = st.selectbox("Load Previous Session", list(meeting_titles.keys()))
        col_load, col_del = st.columns(2)
        with col_load:
            if st.button("📂 Load", use_container_width=True):
                mtg_id = meeting_titles[selected_mtg_title]
                data = get_meeting_by_id(mtg_id)
                if data:
                    with st.spinner("Rebuilding RAG Index..."):
                        rag_chain = build_rag_chain(data["transcript"])
                        data["rag_chain"] = rag_chain
                        st.session_state.result = data
                        st.session_state.pipeline_done = True
                        st.session_state.chat_history = []
                    st.rerun()
        with col_del:
            if st.button("🗑️ Delete", use_container_width=True):
                mtg_id = meeting_titles[selected_mtg_title]
                delete_meeting(mtg_id)
                st.rerun()
    else:
        st.caption("No saved sessions found yet.")

    if st.session_state.pipeline_done:
        st.markdown("---")
        st.markdown('<span class="badge badge-green">Pipeline Status</span>', unsafe_allow_html=True)
        for step, icon, label in [
            ("audio",      "🔊", "Audio Processing"),
            ("transcript", "📝", "Transcription"),
            ("title",      "🏷️", "Title Generation"),
            ("summary",    "📋", "Summarisation"),
            ("extract",    "🔍", "Extraction"),
            ("rag",        "🧠", "RAG Engine"),
        ]:
            render_step_bar(label, step, icon)

# ─── Main Area ──────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">AI Video Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Transcribe · Summarise · Export · Chat with your meetings</div>', unsafe_allow_html=True)
st.markdown("---")

# ── Run Pipeline ────────────────────────────────────────────────────────────────
if run_btn:
    if not source.strip():
        st.error("Please enter a YouTube URL or file path.")
    else:
        st.session_state.pipeline_done = False
        st.session_state.result = None
        st.session_state.chat_history = []
        st.session_state.pipeline_steps = {}

        progress_placeholder = st.empty()

        def update_step(key, state):
            st.session_state.pipeline_steps[key] = state

        try:
            with progress_placeholder.container():
                st.info("⚙️ Pipeline running — see sidebar for live status…")

            update_step("audio", "active")
            chunks, wav_path, duration_sec = process_input(source)
            update_step("audio", "done")

            update_step("transcript", "active")
            transcript = transcribe_all(chunks, language)
            update_step("transcript", "done")

            update_step("title", "active")
            title = generate_title(transcript)
            update_step("title", "done")

            update_step("summary", "active")
            summary = summarize(transcript)
            update_step("summary", "done")

            update_step("extract", "active")
            action_items       = extract_action_items(transcript)
            decisions          = extract_key_decisions(transcript)
            questions          = extract_questions(transcript)
            timestamped_topics = extract_timestamped_topics(transcript, duration_sec)
            update_step("extract", "done")

            update_step("rag", "active")
            rag_chain = build_rag_chain(transcript)
            update_step("rag", "done")

            res = {
                "source": source,
                "language": language,
                "title": title,
                "transcript": transcript,
                "summary": summary,
                "action_items": action_items,
                "key_decisions": decisions,
                "open_questions": questions,
                "timestamped_topics": timestamped_topics,
                "audio_path": wav_path,
                "duration_sec": duration_sec,
                "rag_chain": rag_chain,
            }

            # Save to persistent history
            save_meeting(res)

            st.session_state.result = res
            st.session_state.pipeline_done = True
            progress_placeholder.success("✅ Analysis complete!")
            time.sleep(0.5)
            progress_placeholder.empty()
            st.rerun()

        except Exception as e:
            for k in ["audio","transcript","title","summary","extract","rag"]:
                if st.session_state.pipeline_steps.get(k) == "active":
                    st.session_state.pipeline_steps[k] = "pending"
            progress_placeholder.empty()
            err_str = str(e)
            if "YouTube 403 Forbidden" in err_str or "403" in err_str or "Forbidden" in err_str:
                st.warning("""
                ### ⚠️ YouTube Cloud Audio Download Restricted
                
                The YouTube URL you provided does not have subtitles/captions enabled, and YouTube blocks cloud servers (Streamlit Cloud) from downloading raw audio streams.
                
                #### 💡 How to process this video:
                * **Upload Media File Directly**: Download the video/audio file locally and use the **Upload Media (.mp4, .mp3, .wav)** section in the sidebar.
                * **Try Captioned Videos**: Any YouTube video with Closed Captions (CC) or auto-generated subtitles processes instantly!
                """)
            else:
                st.error(f"❌ Error: {e}")

# ── Results Area ─────────────────────────────────────────────────────────────────
if st.session_state.result:
    r = st.session_state.result

    # Title Banner & Actions
    title_col, btn_col1, btn_col2 = st.columns([4, 1.5, 1.5], gap="small")

    with title_col:
        st.markdown(f"""
        <div class="card" style="margin-bottom:0">
            <div class="card-title">📌 Session Title</div>
            <div style="font-family:'Syne',sans-serif;font-size:1.3rem;font-weight:700;color:var(--text)">
                {r['title']}
            </div>
        </div>""", unsafe_allow_html=True)

    with btn_col1:
        pdf_bytes = generate_pdf_report(r)
        st.download_button(
            label="📥 Download PDF",
            data=pdf_bytes,
            file_name=f"{r.get('title','report')[:20]}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    with btn_col2:
        md_text = generate_markdown_report(r)
        st.download_button(
            label="📝 Download MD",
            data=md_text,
            file_name=f"{r.get('title','report')[:20]}.md",
            mime="text/markdown",
            use_container_width=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # 📊 Analytics Dashboard Header
    m1, m2, m3, m4 = st.columns(4)
    duration_min = int(r.get("duration_sec", 0) // 60)
    duration_s = int(r.get("duration_sec", 0) % 60)
    word_count = len(r.get("transcript", "").split())
    read_time = max(1, word_count // 200)

    with m1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">⏱️ {duration_min}m {duration_s}s</div>
            <div class="metric-label">Audio Duration</div>
        </div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">💬 {word_count:,}</div>
            <div class="metric-label">Total Words</div>
        </div>""", unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">📖 ~{read_time} min</div>
            <div class="metric-label">Reading Time</div>
        </div>""", unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">🌐 {r.get('language','english').title()}</div>
            <div class="metric-label">Language Mode</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # 🎧 Master Audio Player & Timestamped Topics
    if r.get("audio_path") and os.path.exists(r.get("audio_path")):
        st.markdown('<div class="card-title">🎧 Master Audio Playback</div>', unsafe_allow_html=True)
        st.audio(r["audio_path"])

    if r.get("timestamped_topics"):
        with st.expander("📌 Timestamped Agenda & Key Moments", expanded=False):
            st.markdown(f'<div class="card-content">{r["timestamped_topics"]}</div>', unsafe_allow_html=True)

    # Summary & Transcript Split
    col1, col2 = st.columns([3, 2], gap="medium")

    with col1:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">📋 Executive Summary</div>
            <div class="card-content">{r['summary']}</div>
        </div>""", unsafe_allow_html=True)

    with col2:
        with st.expander("📝 Full Transcript", expanded=False):
            st.markdown(f'<div class="transcript-box">{r["transcript"]}</div>', unsafe_allow_html=True)

    # Action Items | Key Decisions | Open Questions
    c1, c2, c3 = st.columns(3, gap="medium")

    with c1:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">✅ Action Items</div>
            <div class="card-content">{r['action_items']}</div>
        </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">🔑 Key Decisions</div>
            <div class="card-content">{r['key_decisions']}</div>
        </div>""", unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">❓ Open Questions</div>
            <div class="card-content">{r['open_questions']}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── RAG Chat ──────────────────────────────────────────────────────────────
    st.markdown('<div style="font-family:\'Syne\',sans-serif;font-size:1.25rem;font-weight:700;margin-bottom:1rem;color:#ffffff !important">💬 Chat with your Meeting</div>', unsafe_allow_html=True)

    if st.session_state.chat_history:
        chat_html = '<div class="chat-container">'
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                chat_html += f"""
                <div class="chat-msg" style="align-items:flex-end">
                    <span class="chat-label user-label">You</span>
                    <div class="chat-bubble user-bubble">{msg['content']}</div>
                </div>"""
            else:
                chat_html += f"""
                <div class="chat-msg" style="align-items:flex-start">
                    <span class="chat-label bot-label">🤖 Assistant</span>
                    <div class="chat-bubble bot-bubble">{msg['content']}</div>
                </div>"""
        chat_html += '</div>'
        st.markdown(chat_html, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="card" style="text-align:center;padding:2rem">
            <div style="font-size:2rem;margin-bottom:0.5rem">💬</div>
            <div style="color:var(--text-muted);font-size:0.85rem">Ask anything about your meeting transcript</div>
        </div>""", unsafe_allow_html=True)

    chat_col1, chat_col2 = st.columns([5, 1], gap="small")
    with chat_col1:
        user_input = st.text_input("Your question", placeholder="What were the main decisions made?", label_visibility="collapsed")
    with chat_col2:
        send_btn = st.button("Send →", use_container_width=True)

    if send_btn and user_input.strip():
        with st.spinner("Thinking…"):
            answer = ask_question(r["rag_chain"], user_input.strip())
        st.session_state.chat_history.append({"role": "user",      "content": user_input.strip()})
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()

    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat", type="secondary"):
            st.session_state.chat_history = []
            st.rerun()

else:
    # Empty state
    st.markdown("""
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;padding:5rem 2rem;text-align:center">
        <div style="font-size:4rem;margin-bottom:1rem">🎬</div>
        <div style="font-family:'Syne',sans-serif;font-size:1.5rem;font-weight:700;color:var(--text);margin-bottom:0.5rem">
            Ready to Analyse
        </div>
        <div style="color:var(--text-muted);font-size:0.85rem;max-width:380px;line-height:1.7">
            Paste a YouTube URL or local file path in the sidebar, choose your language, and hit <strong>Analyse</strong> to get started.
        </div>
        <div style="margin-top:2rem;display:flex;gap:1rem;flex-wrap:wrap;justify-content:center">
            <span class="badge badge-purple">Multi-Language STT</span>
            <span class="badge badge-cyan">PDF & MD Export</span>
            <span class="badge badge-green">Meeting History</span>
        </div>
    </div>""", unsafe_allow_html=True)