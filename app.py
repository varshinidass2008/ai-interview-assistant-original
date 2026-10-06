"""
app.py
AI Interview Assistant — Main Streamlit Entry Point
Practice smarter. Interview better.

Run:  streamlit run app.py
"""

import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Interview Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inject minimal custom CSS ─────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stSidebar"] { background: #0f172a; }
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
.stButton > button { border-radius: 8px; font-weight: 600; }
.stExpander { border: 1px solid #e2e8f0; border-radius: 8px; }
h1 { color: #1e40af; }
h2, h3 { color: #1e3a8a; }
</style>
""", unsafe_allow_html=True)

# ── Login gate ────────────────────────────────────────────────────────────────
def show_login():
    col_center = st.columns([1, 2, 1])[1]
    with col_center:
        st.markdown("## 🤖 AI Interview Assistant")
        st.markdown("### *Practice smarter. Interview better.*")
        st.divider()

        tab_login, tab_signup = st.tabs(["🔑 Login", "📝 Create Account"])

        with tab_login:
            email = st.text_input("Email", placeholder="you@example.com", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            remember = st.checkbox("Remember Me")

            if st.button("🚀 Login", type="primary", use_container_width=True):
                from utilities.auth import validate_login, get_user_name
                if validate_login(email, password):
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = email.strip().lower()
                    st.session_state["user_name"] = get_user_name(email.strip().lower())
                    st.rerun()
                else:
                    st.error("Invalid email or password.")

            st.caption("Demo account: demo@example.com / demo123")

        with tab_signup:
            new_name = st.text_input("Full Name", key="signup_name")
            new_email = st.text_input("Email", key="signup_email")
            new_pass = st.text_input("Password (min 6 chars)", type="password", key="signup_pass")

            if st.button("✅ Create Account", type="primary", use_container_width=True):
                from utilities.auth import create_account
                ok, msg = create_account(new_email, new_pass, new_name)
                if ok:
                    st.success(msg + " You can now log in.")
                else:
                    st.error(msg)


# ── Main router ───────────────────────────────────────────────────────────────
def main():
    if not st.session_state.get("logged_in", False):
        show_login()
        return

    username = st.session_state["username"]

    # Navigation sidebar
    from Components.Navigation import show_navigation
    show_navigation()

    page = st.session_state.get("current_page", "🏠 Dashboard")

    if page == "🏠 Dashboard":
        from pages.dashboard import show_dashboard
        show_dashboard(username)

    elif page == "🎯 Start Interview":
        from pages.start_interview import show_start_interview
        show_start_interview(username)

    elif page == "📋 Interview History":
        from pages.interview_history_page import show_history
        show_history(username)

    elif page == "⚙️ Profile & Settings":
        from pages.profile_settings import show_profile
        show_profile(username)


if __name__ == "__main__":
    main()
