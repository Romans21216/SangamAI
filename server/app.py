import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from views.login import show_login_page
from views.chat import show_chat_page
from views.profile import show_profile_page

try:
    firebase_admin.get_app()
except ValueError:
    cred_data = dict(st.secrets["firebase"])
    cred_data["private_key"] = cred_data["private_key"].replace('\\n', '\n')
    cred = credentials.Certificate(cred_data)
    firebase_admin.initialize_app(cred)

if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "vectors" not in st.session_state:
    st.session_state.vectors = None
if "dataframe" not in st.session_state:
    st.session_state.dataframe = None
if "active_file" not in st.session_state:
    st.session_state.active_file = None
if "page" not in st.session_state:
    st.session_state.page = "chat"

if st.session_state.user_id:
    # Show a brief loading state on the first run after login
    if "_app_ready" not in st.session_state:
        from modules.theme import inject_theme
        st.set_page_config(page_title="SangamAI", page_icon="🧠", layout="wide")
        inject_theme()
        st.markdown(
            """
            <div class="login-loader-overlay">
                <h2>SangamAI</h2>
                <div class="login-loader-bar"></div>
                <span class="login-loader-text">Preparing your workspace…</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.session_state._app_ready = True
        import time; time.sleep(8)
        st.rerun()
    if st.session_state.page == "profile":
        show_profile_page()
    else:
        show_chat_page()
else:
    # Reset ready flag on logout so loader shows again on next login
    st.session_state.pop("_app_ready", None)
    show_login_page()