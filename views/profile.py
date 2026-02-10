import streamlit as st
from firebase_admin import firestore
from modules.theme import inject_theme
from modules.auth import get_username, set_username


def show_profile_page():
    st.set_page_config(page_title="WisdomAI — Profile", page_icon="🧠", layout="centered")
    inject_theme()

    db = firestore.client()
    user_ref = db.collection("users").document(st.session_state.user_id)
    user_data = user_ref.get().to_dict()

    username = get_username(st.session_state.user_id)

    # ── Sidebar ───────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(
            """
            <div style="padding:0.2rem 0 1rem;">
                <span style="font-family:var(--font-display);font-size:1.5rem;
                      background:linear-gradient(135deg,var(--accent),#F4A261);
                      -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
                WisdomAI</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if username:
            st.markdown(
                f'<div class="username-badge">▸ <span class="uname">{username}</span></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<p style="color:var(--text-muted);font-size:0.85rem;">'
                f'{st.session_state.user_id[:8]}…</p>',
                unsafe_allow_html=True,
            )

        st.write("")  # spacer before action buttons
        if st.button("Logout", use_container_width=True):
            st.session_state.user_id = None
            st.rerun()

        st.divider()

        if st.button("← Back to Chat", use_container_width=True):
            st.session_state.page = "chat"
            st.rerun()

    # ── Header ────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="omni-hero" style="padding:2rem 0 0.8rem;">
            <h1 style="font-size:2.4rem !important;">Profile</h1>
        </div>
        <div class="omni-divider"></div>
        """,
        unsafe_allow_html=True,
    )

    # ── Account info (pure HTML — no wrapper div that eats Streamlit widgets) ──
    email = user_data.get("email", "N/A")
    uid_short = st.session_state.user_id[:12] + "…"
    current_api_key = user_data.get("api_key", "")
    key_status = (
        f'<span style="color:#4ade80;">Active · …{current_api_key[-8:]}</span>'
        if current_api_key
        else '<span style="color:var(--accent);">Not configured</span>'
    )

    st.markdown(
        f"""
        <div class="profile-grid">
            <div class="profile-field">
                <span class="field-label">Email</span>
                <span class="field-value">{email}</span>
            </div>
            <div class="profile-field">
                <span class="field-label">User ID</span>
                <span class="field-value" style="font-family:var(--font-mono);font-size:0.82rem;">{uid_short}</span>
            </div>
            <div class="profile-field">
                <span class="field-label">Display Name</span>
                <span class="field-value">{username or '<em style="color:var(--text-muted);">Not set</em>'}</span>
            </div>
            <div class="profile-field">
                <span class="field-label">API Key</span>
                <span class="field-value">{key_status}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="omni-divider"></div>', unsafe_allow_html=True)

    # ── Edit username ─────────────────────────────────────────────
    st.subheader("Display Name")
    new_username = st.text_input(
        "Display Name",
        value=username or "",
        placeholder="Your display name",
        label_visibility="collapsed",
    )
    if st.button("Save Name", use_container_width=True, key="profile_save_name"):
        if new_username.strip():
            set_username(st.session_state.user_id, new_username.strip())
            st.success("✓ Display name saved")
            st.rerun()
        else:
            st.error("Name cannot be empty")

    st.markdown('<div class="omni-divider"></div>', unsafe_allow_html=True)

    # ── Update API key ────────────────────────────────────────────
    st.subheader("Update API Key")

    new_api_key = st.text_input(
        "OpenRouter API Key",
        type="password",
        placeholder="sk-or-v1-…",
        label_visibility="collapsed",
    )

    if st.button("Save Key", use_container_width=True):
        if new_api_key:
            user_ref.update({"api_key": new_api_key})
            st.success("✓ API Key saved")
            st.rerun()
        else:
            st.error("Please enter a key")

    st.caption("Get your key → [openrouter.ai/keys](https://openrouter.ai/keys)")
