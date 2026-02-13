import os
import time
import streamlit as st
import pandas as pd
from firebase_admin import firestore

from modules.llm import get_llm
from modules.rag import (process_pdf, process_youtube, get_retriever, get_embeddings,
                         load_and_split_pdf, create_vectorstore)
from modules.memory import get_memory, clear_memory, get_chat_messages, add_chat_message
from modules.chains import build_conversational_chain, ask_question
from modules.database import (
    save_vectorstore_to_firestore, load_vectorstore_from_firestore,
    save_dataframe_to_firestore, load_dataframe_from_firestore
)
from modules.agents import create_pandas_agent_chain, ask_dataframe_question
from modules.prompts import get_youtube_summary_prompt
from modules.theme import inject_theme
from modules.auth import get_username, set_username

MODEL_OPTIONS = [
    "google/gemini-2.5-flash",
    "google/gemini-3-flash-preview",
    "anthropic/claude-sonnet-4.5",
    "anthropic/claude-3.7-sonnet",
    "openai/gpt-5.2",
    "openai/gpt-4o-mini",
    "x-ai/grok-4.1-fast",
    "x-ai/grok-4-fast",
]

# ── Pipeline visualization helper ─────────────────────────────────────

_PIPELINE_STEPS = [
    ("📄", "Reading PDF pages…"),
    ("✂️", "Chunking into semantic segments…"),
    ("🔢", "Generating vector embeddings…"),
    ("☁️", "Saving to cloud storage…"),
]


def _render_pipeline_html(current_step: int) -> str:
    """Return HTML for the creative loading pipeline at *current_step* (0-based)."""
    rows = ""
    for i, (icon, label) in enumerate(_PIPELINE_STEPS):
        if i < current_step:
            cls = "done"
            trail = f'<span class="step-icon">✓</span>'
        elif i == current_step:
            cls = "active"
            trail = ""
        else:
            cls = ""
            trail = ""
        rows += (
            f'<div class="pipeline-step {cls}">'
            f'  <span class="dot"></span>'
            f'  <span class="step-label">{icon}  {label}</span>'
            f'  {trail}'
            f'</div>'
        )
    return f'<div class="pipeline-container">{rows}</div>'


# ── Sidebar ───────────────────────────────────────────────────────────

def _render_sidebar() -> tuple[str, str]:
    """Draw sidebar controls. Returns ``(api_key, model_name)``."""
    db = firestore.client()
    user_ref = db.collection("users").document(st.session_state.user_id)
    user_data = user_ref.get().to_dict()
    saved_api_key = user_data.get("api_key", "")

    with st.sidebar:
        # branding
        st.markdown(
            """
            <div style="padding:0.2rem 0 1rem;">
                <span style="font-family:var(--font-display);font-size:1.5rem;
                      background:linear-gradient(135deg,var(--accent),#F4A261);
                      -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
                SangamAI</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── username display / prompt ─────────────────────────────
        username = get_username(st.session_state.user_id)

        if username:
            st.markdown(
                f'<div class="username-badge">▸ <span class="uname">{username}</span></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="username-hint">⚡ Set a display name below</div>',
                unsafe_allow_html=True,
            )
            new_name = st.text_input(
                "Display name",
                placeholder="Your name",
                label_visibility="collapsed",
                key="sidebar_username_input",
            )
            if new_name and st.button("Save name", key="save_uname_btn", use_container_width=True):
                set_username(st.session_state.user_id, new_name.strip())
                st.rerun()

        st.write("")  # spacer before action buttons
        col_p, col_l = st.columns(2)
        with col_p:
            if st.button("👤 Profile", use_container_width=True):
                st.session_state.page = "profile"
                st.rerun()
        with col_l:
            if st.button("Logout", use_container_width=True):
                st.session_state.user_id = None
                st.rerun()

        st.divider()
        st.markdown('<p class="omni-label">Model</p>', unsafe_allow_html=True)
        model_name = st.selectbox("Model", options=MODEL_OPTIONS, label_visibility="collapsed")

        st.divider()
        st.markdown('<p class="omni-label">API Key</p>', unsafe_allow_html=True)
        if saved_api_key:
            st.success("Loaded from profile")
            api_key = saved_api_key
        else:
            api_key = st.text_input(
                "API Key", type="password", label_visibility="collapsed",
                placeholder="sk-or-v1-…",
            )
            st.caption("[Get a key →](https://openrouter.ai/keys)")

    return api_key, model_name


# ── Upload Tab ────────────────────────────────────────────────────────

def _render_upload_tab() -> None:
    """Multi-modal upload: PDF | YouTube | CSV."""
    st.markdown(
        """
        <div style="padding:0.5rem 0 1.2rem;">
            <h2 style="margin:0;">Upload Knowledge</h2>
            <p style="color:var(--text-muted);margin:0.2rem 0 0;">
                Feed documents, videos, or datasets to SangamAI.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    pdf_tab, youtube_tab, csv_tab = st.tabs(["📄 PDF", "🎥 YouTube", "📊 CSV"])

    # ──────────────── PDF Tab ────────────────
    with pdf_tab:
        st.caption("Upload PDF documents for conversational retrieval")
        uploaded_file = st.file_uploader(
            "Choose a PDF",
            type="pdf",
            label_visibility="collapsed",
            key="pdf_uploader",
        )

        if uploaded_file and st.button("Process & Save", use_container_width=True, key="pdf_btn"):
            pipeline_slot = st.empty()

            try:
                # Step 0 — reading
                pipeline_slot.markdown(_render_pipeline_html(0), unsafe_allow_html=True)
                temp_filename = f"temp_{uploaded_file.name}"
                with open(temp_filename, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                # Step 1 — chunking
                pipeline_slot.markdown(_render_pipeline_html(1), unsafe_allow_html=True)
                splits = load_and_split_pdf(temp_filename)

                # Step 2 — embedding
                pipeline_slot.markdown(_render_pipeline_html(2), unsafe_allow_html=True)
                vectorstore = create_vectorstore(splits)

                # Step 3 — saving
                pipeline_slot.markdown(_render_pipeline_html(3), unsafe_allow_html=True)
                save_vectorstore_to_firestore(
                    st.session_state.user_id, uploaded_file.name, vectorstore, content_type="pdf"
                )

                # done
                pipeline_slot.markdown(
                    _render_pipeline_html(len(_PIPELINE_STEPS)),
                    unsafe_allow_html=True,
                )
                st.success(f"**{uploaded_file.name}** indexed and saved ✓")
                os.remove(temp_filename)
            except Exception as e:
                st.error(f"Error: {e}")

    # ──────────────── YouTube Tab ────────────────
    with youtube_tab:
        st.caption("Paste a YouTube URL to extract transcript and chat/summarize")
        video_url = st.text_input(
            "YouTube URL",
            placeholder="https://www.youtube.com/watch?v=...",
            label_visibility="collapsed",
            key="youtube_url",
        )

        if video_url and st.button("Process & Save", use_container_width=True, key="youtube_btn"):
            pipeline_slot = st.empty()

            try:
                from modules.rag import extract_video_id
                
                video_id = extract_video_id(video_url)
                if not video_id:
                    st.error("Invalid YouTube URL")
                else:
                    # Step 0 — fetching transcript
                    pipeline_slot.markdown(
                        '<div class="pipeline-container">' +
                        '<div class="pipeline-step active"><span class="dot"></span>' +
                        '<span class="step-label">📥  Fetching transcript…</span></div>' +
                        '</div>',
                        unsafe_allow_html=True
                    )

                    # Step 1 — chunking
                    pipeline_slot.markdown(
                        '<div class="pipeline-container">' +
                        '<div class="pipeline-step done"><span class="dot"></span>' +
                        '<span class="step-label">📥  Fetching transcript…</span><span class="step-icon">✓</span></div>' +
                        '<div class="pipeline-step active"><span class="dot"></span>' +
                        '<span class="step-label">✂️  Chunking transcript…</span></div>' +
                        '</div>',
                        unsafe_allow_html=True
                    )
                    vectorstore, transcript = process_youtube(video_url)

                    # Step 2 — embedding & saving
                    pipeline_slot.markdown(_render_pipeline_html(2), unsafe_allow_html=True)
                    
                    file_name = f"youtube_{video_id}"
                    save_vectorstore_to_firestore(
                        st.session_state.user_id, file_name, vectorstore, content_type="youtube"
                    )

                    pipeline_slot.empty()
                    st.success(f"**Video {video_id}** transcript indexed ✓")
                    
                    # Optional: Generate initial summary (only if API key available)
                    st.caption("💡 Go to the Chat tab to ask questions about this video!")

            except Exception as e:
                st.error(f"Error: {e}")

    # ──────────────── CSV Tab ────────────────
    with csv_tab:
        st.caption("Upload CSV for data analysis via Pandas agent")
        uploaded_csv = st.file_uploader(
            "Choose a CSV",
            type=["csv"],
            label_visibility="collapsed",
            key="csv_uploader",
        )

        if uploaded_csv and st.button("Process & Save", use_container_width=True, key="csv_btn"):
            try:
                df = pd.read_csv(uploaded_csv)
                
                st.write("**Preview:**")
                st.dataframe(df.head(10), use_container_width=True)
                st.caption(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")

                # Save DataFrame to Firestore
                save_dataframe_to_firestore(
                    st.session_state.user_id, uploaded_csv.name, df
                )
                st.success(f"**{uploaded_csv.name}** uploaded ✓")

            except Exception as e:
                st.error(f"Error: {e}")


# ── Chat Tab ──────────────────────────────────────────────────────────

def _render_chat_tab(api_key: str, model_name: str) -> None:
    """Multi-modal chat: handles PDF/YouTube (RAG) and CSV (Pandas agent)."""
    st.markdown(
        """
        <div style="padding:0.5rem 0 1.2rem;">
            <h2 style="margin:0;">Chat</h2>
            <p style="color:var(--text-muted);margin:0.2rem 0 0;">
                Ask questions about your uploaded content.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── file selector ─────────────────────────────────────────────
    db = firestore.client()
    user_files_ref = (
        db.collection("users")
        .document(st.session_state.user_id)
        .collection("files")
    )
    
    # Get all files with metadata
    files_data = {}
    for doc in user_files_ref.stream():
        doc_dict = doc.to_dict()
        files_data[doc.id] = doc_dict.get("content_type", "pdf")
    
    available_files = list(files_data.keys())

    if not available_files:
        st.info("No content yet — upload something in the first tab.")
        return

    st.markdown('<p class="omni-label">Select Content</p>', unsafe_allow_html=True)
    file_name = st.selectbox(
        "Select file", 
        options=available_files,
        format_func=lambda x: f"{'📄' if files_data[x]=='pdf' else '🎥' if files_data[x]=='youtube' else '📊'} {x}",
        label_visibility="collapsed",
        key="chat_file_selector",
    )

    content_type = files_data.get(file_name, "pdf")

    # ── auto-load content when file changes ───────────────────────
    active_file = st.session_state.get("active_file")

    if file_name != active_file:
        with st.spinner("Loading…"):
            try:
                if content_type == "csv":
                    # Load DataFrame for CSV
                    df = load_dataframe_from_firestore(st.session_state.user_id, file_name)
                    if df is not None:
                        st.session_state.dataframe = df
                        st.session_state.vectors = None  # Clear vectorstore
                        st.session_state.active_file = file_name
                        active_file = file_name
                    else:
                        st.error("CSV not found in storage.")
                        return
                else:
                    # Load vectorstore for PDF/YouTube
                    embeddings = get_embeddings()
                    vectorstore = load_vectorstore_from_firestore(
                        st.session_state.user_id, file_name, embeddings
                    )
                    if vectorstore:
                        st.session_state.vectors = vectorstore
                        st.session_state.dataframe = None  # Clear dataframe
                        st.session_state.active_file = file_name
                        active_file = file_name
                    else:
                        st.error("File not found in storage.")
                        return
            except Exception as e:
                st.error(f"Error loading: {e}")
                return

    # ── clear history button ──────────────────────────────────────
    if st.button("🗑️ Clear History", use_container_width=False):
        if active_file:
            clear_memory(active_file)
            st.rerun()

    st.markdown('<div class="omni-divider"></div>', unsafe_allow_html=True)

    # ── chat interface (different for CSV vs RAG) ─────────────────
    
    if content_type == "csv":
        # ═══════════════ CSV MODE (Pandas Agent) ═══════════════
        df = st.session_state.get("dataframe")
        if df is None:
            st.caption("Select a CSV above to start querying.")
            return
        
        with st.expander("📊 DataFrame Preview", expanded=False):
            st.dataframe(df.head(20), use_container_width=True)
            st.caption(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")
            st.caption(f"Columns: {', '.join(df.columns)}")
        
        chat_messages = get_chat_messages(active_file)

        # replay history
        for msg in chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # new user input
        if query := st.chat_input("Ask a question about the data (e.g., 'What is the average sales by region?')"):
            with st.chat_message("user"):
                st.markdown(query)
            add_chat_message(active_file, "user", query)

            with st.chat_message("assistant"):
                with st.spinner("Analyzing data…"):
                    llm = get_llm(api_key, model_name)
                    agent = create_pandas_agent_chain(llm, df, verbose=False)
                    answer = ask_dataframe_question(agent, query)
                    
                    st.markdown(answer)

            add_chat_message(active_file, "assistant", answer)
    
    else:
        # ═══════════════ RAG MODE (PDF/YouTube) ═══════════════
        if not st.session_state.vectors:
            st.caption("Select a document above to start chatting.")
            return

        chat_messages = get_chat_messages(active_file)

        # replay history
        for msg in chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # new user input
        if query := st.chat_input("Ask something about the content…"):
            with st.chat_message("user"):
                st.markdown(query)
            add_chat_message(active_file, "user", query)

            with st.chat_message("assistant"):
                with st.spinner("Thinking…"):
                    llm = get_llm(api_key, model_name)
                    retriever = get_retriever(st.session_state.vectors)
                    memory = get_memory(active_file, llm=llm)
                    chain = build_conversational_chain(llm, retriever, memory)
                    result = ask_question(chain, query)

                    st.markdown(result["answer"])

                    if result["source_documents"]:
                        with st.expander("📚 Source chunks"):
                            for i, doc in enumerate(result["source_documents"], 1):
                                st.caption(f"**Chunk {i}**")
                                st.text(doc.page_content[:300] + "…")

            add_chat_message(active_file, "assistant", result["answer"])


# ── Main entry point ──────────────────────────────────────────────────

def show_chat_page():
    st.set_page_config(page_title="SangamAI", page_icon="🧠", layout="wide")
    inject_theme()

    api_key, model_name = _render_sidebar()

    if not api_key:
        st.markdown(
            """
            <div class="omni-hero">
                <h1>SangamAI</h1>
                <p class="tagline">Enter your OpenRouter API key in the sidebar to begin.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.stop()

    tab1, tab2 = st.tabs(["📄 Upload", "💬 Chat"])

    with tab1:
        _render_upload_tab()
    with tab2:
        _render_chat_tab(api_key, model_name)
