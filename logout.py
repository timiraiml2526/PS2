import streamlit as st

# Clear all session state
for k in list(st.session_state.keys()):
    del st.session_state[k]

# Reset shared posture state if it exists
if hasattr(st, "_ps"):
    import threading
    st._ps = {
        "posture":     "Waiting…",
        "baseline":    None,
        "calib_req":   False,
        "bad_thresh":  0.10,
        "warn_thresh": 0.075,
        "lock":        threading.Lock(),
    }

# Rerun → app.py sees logged_in=False → shows login page
st.rerun()
