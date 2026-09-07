import os
import tempfile

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question


st.set_page_config(
    page_title="Chalchitra | Video intelligence",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)


def run_pipeline(source: str, language: str = "english") -> dict:
    """Run the existing media-to-insights pipeline for a local path or URL."""
    chunks = process_input(source)
    transcript = transcribe_all(chunks, language)
    return {
        "title": generate_title(transcript),
        "transcript": transcript,
        "summary": summarize(transcript),
        "action_items": extract_action_items(transcript),
        "key_decisions": extract_key_decisions(transcript),
        "open_questions": extract_questions(transcript),
        "rag_chain": build_rag_chain(transcript),
    }


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
        :root { --ink: #18213d; --muted: #68718c; --orange: #ff7657; --yellow: #ffd166; --mint: #b8f2df; --blue: #b9d8ff; }
        .stApp { background: #fffaf5; color: var(--ink); }
        [data-testid="stSidebar"] { background: #18213d; border-right: 0; }
        [data-testid="stSidebar"] * { color: #f9fbff !important; }
        [data-testid="stSidebar"] .stCaption { color: #aeb9d9 !important; }
        h1, h2, h3, h4, p, label, button, input, textarea { font-family: 'DM Sans', sans-serif !important; }
        h1, h2, h3 { font-family: 'Space Grotesk', sans-serif !important; color: var(--ink); }
        .hero { padding: 1.6rem 0 1.2rem; animation: rise .55s ease-out both; }
        .eyebrow { color: var(--orange); font-weight: 700; letter-spacing: .12em; text-transform: uppercase; font-size: .75rem; }
        .hero h1 { font-size: clamp(2.4rem, 5vw, 4.8rem); line-height: .98; margin: .45rem 0 .8rem; letter-spacing: -.04em; }
        .hero p { color: var(--muted); max-width: 38rem; font-size: 1.06rem; }
        .hero-mark { float: right; font-size: 5rem; color: var(--orange); line-height: .8; transform: rotate(12deg); }
        .source-card { background: white; border: 1px solid #f0e5da; border-radius: 18px; padding: 1.1rem 1.25rem .8rem; box-shadow: 0 16px 40px rgba(89, 59, 37, .08); animation: rise .65s .08s ease-out both; }
        .metric { background: var(--mint); border-radius: 14px; padding: .9rem 1rem; min-height: 96px; }
        .metric.blue { background: var(--blue); }
        .metric.yellow { background: var(--yellow); }
        .metric strong { display: block; font: 700 1.8rem 'Space Grotesk'; color: var(--ink); }
        .metric span { color: #526078; font-size: .82rem; }
        .insight { border-left: 5px solid var(--orange); background: #fff; border-radius: 0 14px 14px 0; padding: .9rem 1.1rem; box-shadow: 0 8px 25px rgba(89, 59, 37, .06); }
        .stButton > button, .stDownloadButton > button { border-radius: 10px; border: 0; font-weight: 700; min-height: 2.7rem; }
        .stButton > button[kind="primary"] { background: var(--orange); color: white; }
        .chat-head { display: flex; align-items: center; justify-content: space-between; margin-top: 1.5rem; }
        @keyframes rise { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }
        @media (max-width: 700px) { .hero-mark { display: none; } .hero h1 { font-size: 2.8rem; } }
        </style>
        """,
        unsafe_allow_html=True,
    )


def save_upload(uploaded_file) -> str:
    suffix = os.path.splitext(uploaded_file.name)[1] or ".mp4"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as handle:
        handle.write(uploaded_file.getbuffer())
        return handle.name


def render_sidebar() -> tuple[str, str, str | None]:
    with st.sidebar:
        st.markdown("## ✦ Chalchitra")
        st.caption("Turn long videos into clear next steps.")
        st.markdown("---")
        st.markdown("**How it works**")
        st.markdown("1. Add a video or YouTube link\n2. Choose your language\n3. Explore the insights")
        st.markdown("---")
        st.markdown("**Configuration**")
        language = st.selectbox("Transcription mode", ["english", "hinglish"], format_func=lambda value: value.title())
        st.caption("Hinglish uses Sarvam AI translation. English runs locally with Whisper.")
        st.markdown("---")
        st.caption("Powered by Whisper, Sarvam AI & Mistral")

    uploaded_file = st.file_uploader("", type=["mp4", "mov", "mkv", "avi", "mp3", "wav", "m4a"], label_visibility="collapsed")
    url = st.text_input("", placeholder="Paste a YouTube link", label_visibility="collapsed")
    return language, url.strip(), uploaded_file


def render_results(result: dict) -> None:
    transcript = result.get("transcript", "")
    st.markdown(f"### {result.get('title', 'Your video brief')}")
    st.caption("Your video has been distilled into a working brief.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="metric"><strong>{len(transcript.split()):,}</strong><span>words captured</span></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric blue"><strong>5</strong><span>insight lenses</span></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric yellow"><strong>1</strong><span>conversation ready</span></div>', unsafe_allow_html=True)

    st.markdown("### Your brief")
    tabs = st.tabs(["Overview", "Action items", "Decisions", "Open questions", "Transcript"])
    with tabs[0]:
        st.markdown('<div class="insight">A concise summary of the ideas that matter most from this video.</div>', unsafe_allow_html=True)
        st.markdown(result.get("summary", "No summary returned."))
    with tabs[1]:
        st.markdown(result.get("action_items", "No action items found."))
    with tabs[2]:
        st.markdown(result.get("key_decisions", "No key decisions found."))
    with tabs[3]:
        st.markdown(result.get("open_questions", "No open questions found."))
    with tabs[4]:
        st.text_area("Transcript", transcript, height=360, label_visibility="collapsed")
        st.download_button("Download transcript", transcript, file_name="chalchitra-transcript.txt", mime="text/plain", use_container_width=True)


def render_chat() -> None:
    st.markdown('<div class="chat-head"><h3>Ask your video</h3><span>✦ grounded in the transcript</span></div>', unsafe_allow_html=True)
    st.caption("Ask for a detail, a quote, a recap, or the next step. The assistant only uses this video’s transcript.")
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    question = st.chat_input("What should I know about this video?")
    if question:
        st.session_state.chat_history.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)
        with st.chat_message("assistant"):
            with st.spinner("Finding that in the transcript..."):
                answer = ask_question(st.session_state.result["rag_chain"], question)
            st.markdown(answer)
        st.session_state.chat_history.append({"role": "assistant", "content": answer})


def main() -> None:
    inject_styles()
    st.markdown('<div class="hero"><span class="hero-mark">✦</span><div class="eyebrow">Video intelligence, made human</div><h1>Make every minute<br>count.</h1><p>Chalchitra turns your videos into a thoughtful brief, clear decisions, and a conversation you can return to.</p></div>', unsafe_allow_html=True)
    language, url, uploaded_file = render_sidebar()

    with st.container(border=True):
        st.markdown("### Bring a video to life")
        st.caption("Upload a file or paste a YouTube link. Your workspace will appear here when it is ready.")
        if uploaded_file:
            st.info(f"Ready to analyze **{uploaded_file.name}**")
        elif url:
            st.info("Ready to analyze the YouTube link")
        analyze = st.button("Analyze video  →", type="primary", use_container_width=True, disabled=not (uploaded_file or url))

    if analyze:
        source_path = None
        try:
            with st.status("Building your video brief...", expanded=True) as status:
                if uploaded_file:
                    source_path = save_upload(uploaded_file)
                    st.write("Video uploaded")
                else:
                    source_path = url
                    st.write("YouTube source connected")
                st.write("Transcribing and extracting insights")
                result = run_pipeline(source_path, language)
                status.update(label="Your brief is ready", state="complete", expanded=False)
            st.session_state.result = result
            st.session_state.chat_history = []
        except Exception as error:
            st.error(f"We could not analyze this source: {error}")
        finally:
            if source_path and uploaded_file and os.path.exists(source_path):
                os.remove(source_path)

    if "result" in st.session_state:
        render_results(st.session_state.result)
        st.divider()
        render_chat()
    else:
        st.markdown("<div style='height: 5rem'></div>", unsafe_allow_html=True)
        st.markdown("### A calmer way to catch up")
        st.caption("Summaries for focus. Decisions for momentum. A chat companion for the details you do not want to replay.")


if __name__ == "__main__":
    main()