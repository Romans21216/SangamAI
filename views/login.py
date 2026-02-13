import streamlit as st
from modules.auth import verify_password, register_user
from modules.theme import inject_theme


def show_login_page():
    st.set_page_config(page_title="SangamAI — Login", page_icon="🧠", layout="centered")
    inject_theme()

    # ── Hero ──────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="omni-hero">
            <h1>SangamAI</h1>
            <p class="tagline">Where content meets clarity</p>
        </div>
        <div class="omni-divider"></div>
        """,
        unsafe_allow_html=True,
    )

    tab1, tab2 = st.tabs(["Sign In", "Create Account"])

    with tab1:
        st.markdown('<p class="omni-label">Email</p>', unsafe_allow_html=True)
        email = st.text_input("Email", label_visibility="collapsed", placeholder="you@example.com")
        st.markdown('<p class="omni-label">Password</p>', unsafe_allow_html=True)
        password = st.text_input("Password", type="password", label_visibility="collapsed", placeholder="••••••••")

        st.write("")  # spacer
        if st.button("Sign In", use_container_width=True):
            uid = verify_password(email, password)
            if uid:
                st.session_state.user_id = uid
                st.rerun()
            else:
                st.error("Invalid email or password")

    with tab2:
        st.markdown('<p class="omni-label">Email</p>', unsafe_allow_html=True)
        new_email = st.text_input("New Email", label_visibility="collapsed", placeholder="you@example.com")
        st.markdown('<p class="omni-label">Password</p>', unsafe_allow_html=True)
        new_pass = st.text_input("New Password", type="password", label_visibility="collapsed", placeholder="Choose a strong password")
        st.markdown('<p class="omni-label">Display Name <span style="color:var(--text-muted);">(optional)</span></p>', unsafe_allow_html=True)
        new_username = st.text_input("Username", label_visibility="collapsed", placeholder="Your name")

        st.write("")
        if st.button("Create Account", use_container_width=True):
            uid = register_user(new_email, new_pass)
            if uid:
                if new_username.strip():
                    from modules.auth import set_username
                    set_username(uid, new_username.strip())
                st.success("Account created — switch to **Sign In** to continue.")
