import streamlit as st
import sqlite3
import hashlib
import os

# ──────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG  (must be first Streamlit call)
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PostureSense",
    page_icon="🧘",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ──────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
  --good:   #00e676;
  --warn:   #ffea00;
  --bad:    #ff1744;
  --bg:     #0d0f14;
  --card:   #161922;
  --border: #1e2230;
  --text:   #e8eaf0;
  --muted:  #6b7280;
  --accent: #6c63ff;
}

html, body, [data-testid="stAppViewContainer"] {
  background-color: var(--bg) !important;
  color: var(--text) !important;
  font-family: 'DM Sans', sans-serif;
}

[data-testid="stSidebar"] { display: none !important; }

h1, h2, h3 { font-family: 'Space Mono', monospace; }

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"]  { display: none; }

/* ── Auth card ── */
.auth-wrapper {
  max-width: 440px;
  margin: 4rem auto 0;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 2.5rem 2rem;
  box-shadow: 0 20px 60px rgba(0,0,0,.5);
}

.auth-logo {
  text-align: center;
  font-family: 'Space Mono', monospace;
  font-size: 2rem;
  font-weight: 700;
  color: var(--text);
  margin-bottom: .25rem;
}

.auth-sub {
  text-align: center;
  color: var(--muted);
  font-size: .9rem;
  margin-bottom: 2rem;
}

/* ── Inputs ── */
[data-testid="stTextInput"] > div > div > input {
  background: #0d0f14 !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
  color: var(--text) !important;
  padding: .6rem .85rem !important;
}
[data-testid="stTextInput"] > div > div > input:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 2px rgba(108,99,255,.25) !important;
}

/* ── Primary button ── */
.stButton > button {
  width: 100%;
  border-radius: 8px !important;
  background: var(--accent) !important;
  color: white !important;
  font-weight: 600 !important;
  padding: .6rem 1rem !important;
  border: none !important;
  transition: opacity .2s;
}
.stButton > button:hover { opacity: .85; }

/* ── Radio tab ── */
[data-testid="stRadio"] > div { gap: 0 !important; }
[data-testid="stRadio"] label {
  flex: 1;
  text-align: center;
  padding: .45rem 0;
  border-bottom: 2px solid var(--border);
  color: var(--muted);
  cursor: pointer;
  font-weight: 500;
  transition: all .2s;
}
[data-testid="stRadio"] label[data-checked="true"],
[data-testid="stRadio"] input:checked + div {
  border-bottom-color: var(--accent);
  color: var(--text);
}

div[data-testid="stAlert"] { border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# DATABASE
# ──────────────────────────────────────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")

@st.cache_resource
def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            name     TEXT    NOT NULL,
            phone    TEXT    UNIQUE NOT NULL,
            password TEXT    NOT NULL
        )
    """)
    conn.commit()
    return conn

conn = get_db()

def _hash(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def register_user(name: str, phone: str, pw: str):
    name = name.strip()
    phone = phone.strip()
    if not name:
        return "Name cannot be empty."
    if not phone.isdigit() or len(phone) != 10:
        return "Enter a valid 10-digit phone number."
    if len(pw) < 6:
        return "Password must be at least 6 characters."
    try:
        conn.execute("INSERT INTO users (name, phone, password) VALUES (?,?,?)",
                     (name, phone, _hash(pw)))
        conn.commit()
        return "ok"
    except sqlite3.IntegrityError:
        return "Phone number already registered."

def login_user(phone: str, pw: str):
    row = conn.execute(
        "SELECT id, name FROM users WHERE phone=? AND password=?",
        (phone.strip(), _hash(pw))
    ).fetchone()
    return row  # (id, name) or None

# ──────────────────────────────────────────────────────────────────────────────
# SESSION STATE DEFAULTS
# ──────────────────────────────────────────────────────────────────────────────
for k, v in [("logged_in", False), ("user_id", None), ("user_name", "")]:
    if k not in st.session_state:
        st.session_state[k] = v

# ──────────────────────────────────────────────────────────────────────────────
# IF ALREADY LOGGED IN → jump to monitor
# ──────────────────────────────────────────────────────────────────────────────
if st.session_state.logged_in:
    st.switch_page("pages/1_Monitor.py")

# ──────────────────────────────────────────────────────────────────────────────
# AUTH UI
# ──────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="auth-wrapper">', unsafe_allow_html=True)
st.markdown('<div class="auth-logo">🧘 PostureSense</div>', unsafe_allow_html=True)
st.markdown('<div class="auth-sub">Your real-time posture guardian</div>', unsafe_allow_html=True)

tab = st.radio("", ["Login", "Register"], horizontal=True, label_visibility="collapsed")
st.markdown("<br>", unsafe_allow_html=True)

if tab == "Login":
    phone = st.text_input("📱 Phone Number", placeholder="10-digit mobile number", key="li_phone")
    pw    = st.text_input("🔒 Password",      placeholder="Your password",          type="password", key="li_pw")

    if st.button("Login →", key="btn_login"):
        if not phone or not pw:
            st.error("Please fill in all fields.")
        else:
            row = login_user(phone, pw)
            if row:
                st.session_state.logged_in = True
                st.session_state.user_id   = row[0]
                st.session_state.user_name = row[1]
                st.rerun()
            else:
                st.error("Invalid phone number or password.")

else:  # Register
    name  = st.text_input("👤 Full Name",    placeholder="Your full name",        key="rg_name")
    phone = st.text_input("📱 Phone Number", placeholder="10-digit mobile number", key="rg_phone")
    pw    = st.text_input("🔒 Password",     placeholder="Min. 6 characters",     type="password", key="rg_pw")
    pw2   = st.text_input("🔒 Confirm Password", placeholder="Repeat password",   type="password", key="rg_pw2")

    if st.button("Create Account →", key="btn_register"):
        if not all([name, phone, pw, pw2]):
            st.error("Please fill in all fields.")
        elif pw != pw2:
            st.error("Passwords do not match.")
        else:
            result = register_user(name, phone, pw)
            if result == "ok":
                st.success("Account created! You can now log in.")
            else:
                st.error(result)

st.markdown('</div>', unsafe_allow_html=True)
