import streamlit as st
import sqlite3
import hashlib
import os

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@400;500;600&display=swap');
:root{--bg:#0d0f14;--card:#161922;--border:#1e2230;--text:#e8eaf0;--muted:#6b7280;--accent:#6c63ff}
html,body,[data-testid="stAppViewContainer"]{background:var(--bg)!important;color:var(--text)!important;font-family:'DM Sans',sans-serif}
[data-testid="stSidebar"]{display:none!important}
#MainMenu,footer,header{visibility:hidden}[data-testid="stToolbar"]{display:none}
h1,h2,h3{font-family:'Space Mono',monospace}
.auth-wrap{max-width:440px;margin:3rem auto 0;background:var(--card);border:1px solid var(--border);border-radius:16px;padding:2.5rem 2rem;box-shadow:0 20px 60px rgba(0,0,0,.5)}
.auth-logo{text-align:center;font-family:'Space Mono',monospace;font-size:2rem;font-weight:700;margin-bottom:.2rem}
.auth-sub{text-align:center;color:var(--muted);font-size:.9rem;margin-bottom:2rem}
[data-testid="stTextInput"]>div>div>input{background:#0d0f14!important;border:1px solid var(--border)!important;border-radius:8px!important;color:var(--text)!important}
[data-testid="stTextInput"]>div>div>input:focus{border-color:var(--accent)!important;box-shadow:0 0 0 2px rgba(108,99,255,.25)!important}
.stButton>button{width:100%;border-radius:8px!important;background:var(--accent)!important;color:#fff!important;font-weight:600!important;border:none!important}
div[data-testid="stAlert"]{border-radius:8px}
</style>
""", unsafe_allow_html=True)

# ── DB ────────────────────────────────────────────────────────────────────────
_HERE   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root
DB_PATH = os.path.join(_HERE, "users.db")

@st.cache_resource
def get_db():
    c = sqlite3.connect(DB_PATH, check_same_thread=False)
    c.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL, phone TEXT UNIQUE NOT NULL, password TEXT NOT NULL)""")
    c.commit()
    return c

conn = get_db()
_hash = lambda pw: hashlib.sha256(pw.encode()).hexdigest()

def register(name, phone, pw):
    name, phone = name.strip(), phone.strip()
    if not name:                           return "Name cannot be empty."
    if not phone.isdigit() or len(phone)!=10: return "Enter a valid 10-digit phone number."
    if len(pw) < 6:                        return "Password must be at least 6 characters."
    try:
        conn.execute("INSERT INTO users(name,phone,password) VALUES(?,?,?)", (name,phone,_hash(pw)))
        conn.commit(); return "ok"
    except sqlite3.IntegrityError:         return "Phone number already registered."

def login(phone, pw):
    return conn.execute(
        "SELECT id,name FROM users WHERE phone=? AND password=?",
        (phone.strip(), _hash(pw))
    ).fetchone()

# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown('<div class="auth-wrap">', unsafe_allow_html=True)
st.markdown('<div class="auth-logo">🧘 PostureSense</div>', unsafe_allow_html=True)
st.markdown('<div class="auth-sub">Your real-time posture guardian</div>', unsafe_allow_html=True)

tab = st.radio("", ["Login","Register"], horizontal=True, label_visibility="collapsed")
st.markdown("<br>", unsafe_allow_html=True)

if tab == "Login":
    phone = st.text_input("📱 Phone Number", placeholder="10-digit number", key="l_ph")
    pw    = st.text_input("🔒 Password",     placeholder="Password", type="password", key="l_pw")
    if st.button("Login →"):
        if not phone or not pw:
            st.error("Fill in all fields.")
        else:
            row = login(phone, pw)
            if row:
                st.session_state.logged_in = True
                st.session_state.user_id   = row[0]
                st.session_state.user_name = row[1]
                st.rerun()   # app.py rebuilds nav → lands on Monitor automatically
            else:
                st.error("Invalid phone or password.")
else:
    name  = st.text_input("👤 Full Name",       placeholder="Your name",          key="r_nm")
    phone = st.text_input("📱 Phone Number",     placeholder="10-digit number",    key="r_ph")
    pw    = st.text_input("🔒 Password",         placeholder="Min. 6 chars",       type="password", key="r_pw")
    pw2   = st.text_input("🔒 Confirm Password", placeholder="Repeat password",    type="password", key="r_pw2")
    if st.button("Create Account →"):
        if not all([name, phone, pw, pw2]):  st.error("Fill in all fields.")
        elif pw != pw2:                      st.error("Passwords do not match.")
        else:
            res = register(name, phone, pw)
            if res == "ok": st.success("✅ Account created! You can now log in.")
            else:           st.error(res)

st.markdown('</div>', unsafe_allow_html=True)
