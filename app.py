"""
PostureSense — entry point
All routing is handled here via st.navigation() so st.switch_page() is
NEVER called anywhere in the codebase, eliminating the Cloud path errors.
"""
import streamlit as st

st.set_page_config(
    page_title="PostureSense",
    page_icon="🧘",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Session defaults
for k, v in [("logged_in", False), ("user_id", None), ("user_name", "")]:
    if k not in st.session_state:
        st.session_state[k] = v

# Build page list based on auth state
if st.session_state.logged_in:
    pages = [
        st.Page("monitor.py",   title="Monitor",   icon="🧘"),
        st.Page("analytics.py", title="Analytics", icon="📊"),
        st.Page("logout.py",    title="Logout",    icon="🚪"),
    ]
else:
    pages = [
        st.Page("login.py", title="Login / Register", icon="🔐"),
    ]

pg = st.navigation(pages, position="sidebar" if st.session_state.logged_in else "hidden")
pg.run()
