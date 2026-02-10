"""Per-file conversation memory backed by Streamlit session_state + Firestore.

Each uploaded document gets its own **windowed** memory that retains the
last *k* conversation turns.  This avoids any token-counting calls that
fail with OpenRouter-proxied models while still giving the chain enough
recent context for follow-up questions.

Display messages (the full chat history shown in the UI) are persisted to
Firestore so they survive page refreshes.
"""

import streamlit as st
from langchain.memory import ConversationBufferWindowMemory

from modules.database import (
    save_chat_message as _fb_save,
    load_chat_history as _fb_load,
    clear_chat_history as _fb_clear,
)


def get_memory(file_name: str, *, k: int = 8, **_kw) -> ConversationBufferWindowMemory:
    """Return (or create) a ConversationBufferWindowMemory for *file_name*.

    - Keeps the last *k* human/AI exchanges (default 8).
    - ``memory_key="chat_history"`` matches what ConversationalRetrievalChain expects.
    - ``return_messages=True`` keeps messages as LangChain Message objects.

    Any extra keyword arguments (e.g. ``llm=``) are silently ignored so
    callers that used to pass an LLM for the old summary-buffer memory
    don't need to be updated.
    """
    key = f"memory_{file_name}"

    if key not in st.session_state:
        st.session_state[key] = ConversationBufferWindowMemory(
            k=k,
            memory_key="chat_history",
            return_messages=True,
            output_key="answer",
            input_key="question",
        )

    return st.session_state[key]


def clear_memory(file_name: str) -> None:
    """Delete the LangChain memory, display messages, AND Firestore chat history."""
    for prefix in ("memory_", "messages_"):
        full_key = f"{prefix}{file_name}"
        if full_key in st.session_state:
            del st.session_state[full_key]

    # wipe Firestore messages
    user_id = st.session_state.get("user_id")
    if user_id:
        _fb_clear(user_id, file_name)


# ------------------------------------------------------------------
# Display-message helpers  (separate from LangChain memory so the
# Streamlit chat_message UI can replay the full history on reruns)
#
# On first access per file per session, messages are hydrated from
# Firestore.  New messages are written to both session_state AND
# Firestore in real-time.
# ------------------------------------------------------------------

def get_chat_messages(file_name: str) -> list[dict]:
    """Return the list of ``{"role": ..., "content": ...}`` dicts for the UI.

    First call per session loads from Firestore; subsequent calls return
    the cached session_state list.
    """
    key = f"messages_{file_name}"
    if key not in st.session_state:
        user_id = st.session_state.get("user_id")
        if user_id:
            st.session_state[key] = _fb_load(user_id, file_name)
        else:
            st.session_state[key] = []
    return st.session_state[key]


def add_chat_message(file_name: str, role: str, content: str) -> None:
    """Append a message to session_state AND persist to Firestore."""
    get_chat_messages(file_name).append({"role": role, "content": content})

    user_id = st.session_state.get("user_id")
    if user_id:
        _fb_save(user_id, file_name, role, content)
