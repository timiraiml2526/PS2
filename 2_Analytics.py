import streamlit as st
import time
from collections import deque

# ──────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PostureSense · Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────────────
# AUTH GUARD
# ──────────────────────────────────────────────────────────────────────────────
if not st.session_state.get("logged_in"):
    st.warning("⚠️ Please log in first.")
    if st.button("Go to Login →"):
        st.switch_page("Home.py")
    st.stop()

# ──────────────────────────────────────────────────────────────────────────────
# CSS
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');
:root{--good:#00e676;--warn:#ffea00;--bad:#ff1744;--bg:#0d0f14;--card:#161922;--border:#1e2230;--text:#e8eaf0;--muted:#6b7280;--accent:#6c63ff}
html,body,[data-testid="stAppViewContainer"]{background:var(--bg)!important;color:var(--text)!important;font-family:'DM Sans',sans-serif}
[data-testid="stSidebar"]{background:#0a0c10!important;border-right:1px solid var(--border)}
h1,h2,h3,h4{font-family:'Space Mono',monospace}
.mc{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:1.2rem 1.3rem;text-align:center;margin-bottom:.6rem}
.mc .lbl{font-size:.68rem;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin-bottom:.3rem}
.mc .val{font-family:'Space Mono',monospace;font-size:2rem;font-weight:700;line-height:1}
.val.good{color:var(--good)}.val.warn{color:var(--warn)}.val.bad{color:var(--bad)}.val.wht{color:var(--text)}.val.acc{color:var(--accent)}
.sh{font-family:'Space Mono',monospace;font-size:.68rem;letter-spacing:.15em;text-transform:uppercase;color:var(--muted);border-bottom:1px solid var(--border);padding-bottom:.3rem;margin:1.3rem 0 .75rem}
.grade-card{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:1.5rem 2rem;margin-bottom:1rem;display:flex;align-items:center;gap:1.5rem}
.grade-emoji{font-size:3.5rem;line-height:1}
.grade-title{font-family:'Space Mono',monospace;font-size:1.25rem;font-weight:700;margin-bottom:.25rem}
.grade-sub{color:var(--muted);font-size:.9rem}
.rec-card{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:1.1rem 1.3rem;margin-bottom:.65rem}
.rec-card h4{font-family:'Space Mono',monospace;font-size:.92rem;color:var(--text);margin:0 0 .45rem}
.rec-card p{color:#b0bcc8;font-size:.87rem;margin:0;line-height:1.55}
.rec-card .tag{display:inline-block;padding:.2rem .65rem;border-radius:999px;font-size:.7rem;font-weight:700;letter-spacing:.05em;margin-bottom:.5rem}
.tag-stretch{background:rgba(0,230,118,.12);color:var(--good);border:1px solid rgba(0,230,118,.25)}
.tag-exercise{background:rgba(108,99,255,.15);color:#a89fff;border:1px solid rgba(108,99,255,.3)}
.tag-habit{background:rgba(255,234,0,.1);color:var(--warn);border:1px solid rgba(255,234,0,.25)}
.tag-ergo{background:rgba(255,23,68,.1);color:#ff6b8a;border:1px solid rgba(255,23,68,.2)}
.prog-bar-bg{background:#1e2230;border-radius:999px;height:10px;width:100%;overflow:hidden;margin-top:.3rem}
.prog-bar-fill{height:100%;border-radius:999px;transition:width .5s ease}
#MainMenu,footer,header{visibility:hidden}[data-testid="stToolbar"]{display:none}
.stButton>button{border-radius:8px!important;font-weight:600!important}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR NAV
# ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 Analytics")
    st.markdown(f"👤 **{st.session_state.get('user_name', 'User')}**")
    st.markdown("---")
    if st.button("🧘 Back to Monitor", use_container_width=True, type="primary"):
        st.switch_page("pages/1_Monitor.py")
    if st.button("🚪 Logout", use_container_width=True):
        for k in ["logged_in", "user_id", "user_name",
                  "session_active", "session_start",
                  "total_good", "total_warn", "total_bad",
                  "alert_count", "last_alert_time", "history"]:
            if k in st.session_state:
                del st.session_state[k]
        st.switch_page("Home.py")

# ──────────────────────────────────────────────────────────────────────────────
# READ SESSION DATA
# ──────────────────────────────────────────────────────────────────────────────
total_good = st.session_state.get("total_good", 0)
total_warn = st.session_state.get("total_warn", 0)
total_bad  = st.session_state.get("total_bad",  0)
total      = total_good + total_warn + total_bad
alert_count = st.session_state.get("alert_count", 0)
session_start = st.session_state.get("session_start")
history    = list(st.session_state.get("history", deque()))

good_pct = round(total_good / total * 100) if total else 0
warn_pct = round(total_warn / total * 100) if total else 0
bad_pct  = round(total_bad  / total * 100) if total else 0

if session_start:
    dur = int(time.time() - session_start)
    dur_str = f"{dur//3600:02d}:{(dur%3600)//60:02d}:{dur%60:02d}"
    good_sec = round(total_good / total * dur) if total else 0
    bad_sec  = round(total_bad  / total * dur) if total else 0
else:
    dur     = 0
    dur_str = "00:00:00"
    good_sec = bad_sec = 0

# ──────────────────────────────────────────────────────────────────────────────
# GRADE LOGIC
# ──────────────────────────────────────────────────────────────────────────────
def get_grade(pct):
    if pct >= 80: return ("🏆", "Excellent", "Outstanding session! Your posture habits are top-notch.")
    if pct >= 65: return ("👍", "Good",       "Solid performance. A little more mindfulness and you'll be great.")
    if pct >= 45: return ("⚠️", "Needs Work", "Room for improvement. Use the tips below to build better habits.")
    return          ("❌", "Poor",          "Your posture needs serious attention. Start with the exercises below.")

# ──────────────────────────────────────────────────────────────────────────────
# RECOMMENDATIONS DATABASE
# ──────────────────────────────────────────────────────────────────────────────
ALL_RECS = [
    # Stretches
    {
        "tag": "stretch", "title": "Chin Tucks",
        "desc": "Sit up straight and gently pull your chin straight back, creating a 'double chin'. Hold for 5 seconds. Repeat 10× every hour. Counters forward-head posture caused by screen use.",
        "priority": "bad",
    },
    {
        "tag": "stretch", "title": "Doorway Chest Stretch",
        "desc": "Stand in a doorway, place forearms on the frame at 90°, and gently lean forward until you feel a stretch across your chest. Hold 20–30 sec. Releases tightness from hunching.",
        "priority": "bad",
    },
    {
        "tag": "stretch", "title": "Upper Trapezius Stretch",
        "desc": "Drop your right ear toward your right shoulder while reaching your left arm down. Hold 20 sec each side. Relieves shoulder and neck tension from uneven sitting.",
        "priority": "warn",
    },
    {
        "tag": "stretch", "title": "Cat–Cow Stretch",
        "desc": "On all fours, alternate arching (cow) and rounding (cat) your back for 10 slow reps. A perfect morning or break-time routine to mobilise the entire spine.",
        "priority": "warn",
    },
    # Exercises
    {
        "tag": "exercise", "title": "Wall Angels",
        "desc": "Stand with your back flat against a wall, arms at 90°, and slowly slide them up and down like a snow angel. 3 sets of 10. Activates deep postural muscles and opens the shoulders.",
        "priority": "bad",
    },
    {
        "tag": "exercise", "title": "Band Pull-Aparts",
        "desc": "Hold a resistance band at shoulder width and pull it apart horizontally. 3 × 15 reps. Strengthens rhomboids and rear deltoids—the muscles that keep shoulders back.",
        "priority": "bad",
    },
    {
        "tag": "exercise", "title": "Dead Bug",
        "desc": "Lie on your back, extend opposite arm and leg slowly while keeping your lower back pressed into the floor. 3 × 8 per side. Builds core stability essential for upright posture.",
        "priority": "warn",
    },
    {
        "tag": "exercise", "title": "Prone Cobra (Back Extension)",
        "desc": "Lie face down, squeeze shoulder blades, and lift chest slightly off the floor. Hold 10 sec, repeat 10×. Strengthens spinal extensors weakened by prolonged sitting.",
        "priority": "warn",
    },
    {
        "tag": "exercise", "title": "Plank",
        "desc": "Hold a forearm plank for 30–60 seconds, keeping hips level. 3 sets. A full-chain core exercise that directly supports upright posture throughout the day.",
        "priority": "good",
    },
    # Habits
    {
        "tag": "habit", "title": "20-20-2 Rule",
        "desc": "Every 20 minutes, look 20 feet away for 20 seconds, then stand and move for 2 minutes. This simple rhythm reduces eye strain and prevents postural fatigue.",
        "priority": "bad",
    },
    {
        "tag": "habit", "title": "Set Hourly Posture Alarms",
        "desc": "Use your phone or watch to buzz every hour as a posture check-in. Ask yourself: are my feet flat, back straight, shoulders relaxed, screen at eye level?",
        "priority": "bad",
    },
    {
        "tag": "habit", "title": "Mindful Sitting Reset",
        "desc": "Each time you sit down, do a 3-second reset: feet flat → hips back → spine tall → shoulders relaxed → chin neutral. Make it automatic.",
        "priority": "warn",
    },
    {
        "tag": "habit", "title": "Stay Hydrated",
        "desc": "Drink a glass of water every hour. Dehydrated spinal discs compress more easily, worsening posture pain. Hydration literally keeps you straighter.",
        "priority": "good",
    },
    # Ergonomics
    {
        "tag": "ergo", "title": "Monitor at Eye Level",
        "desc": "The top of your screen should be at or slightly below eye level. If you use a laptop, add an external monitor or a riser + external keyboard to avoid constant neck flexion.",
        "priority": "bad",
    },
    {
        "tag": "ergo", "title": "Chair Height & Lumbar Support",
        "desc": "Adjust chair height so feet rest flat on the floor and knees are at ~90°. Use a lumbar pillow or rolled towel behind your lower back to maintain natural spinal curve.",
        "priority": "bad",
    },
    {
        "tag": "ergo", "title": "Keyboard & Mouse Position",
        "desc": "Keep keyboard and mouse at elbow height so arms rest comfortably without shrugging. Wrists should float, not rest, while typing to prevent shoulder elevation.",
        "priority": "warn",
    },
]

TAG_META = {
    "stretch":  ("🤸", "Stretch",   "tag-stretch"),
    "exercise": ("💪", "Exercise",  "tag-exercise"),
    "habit":    ("🧠", "Habit",     "tag-habit"),
    "ergo":     ("🪑", "Ergonomics","tag-ergo"),
}

def get_recommendations(good_pct, bad_pct):
    """Return a prioritised list of recommendations based on session score."""
    if bad_pct >= 40:
        priority_order = ["bad", "warn", "ergo", "good"]
    elif bad_pct >= 20:
        priority_order = ["warn", "bad", "ergo", "good"]
    else:
        priority_order = ["good", "warn", "bad", "ergo"]

    sorted_recs = []
    for p in priority_order:
        sorted_recs += [r for r in ALL_RECS if r["priority"] == p]

    # Always include at least 2 ergo items
    ergo_in = [r for r in sorted_recs if r["tag"] == "ergo"]
    if len(ergo_in) < 2:
        for r in ALL_RECS:
            if r["tag"] == "ergo" and r not in sorted_recs:
                sorted_recs.append(r)

    return sorted_recs

# ──────────────────────────────────────────────────────────────────────────────
# PAGE HEADER
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("# 📊 Analytics & Recommendations")
st.markdown(f"##### Session insights for **{st.session_state.get('user_name','User')}**")

if total == 0:
    st.info("🔍 No session data yet. Go to the **Monitor** page, start a session, and come back here to see your analytics.")
    if st.button("🧘 Go to Monitor →", type="primary"):
        st.switch_page("pages/1_Monitor.py")
    st.stop()

# ──────────────────────────────────────────────────────────────────────────────
# GRADE CARD
# ──────────────────────────────────────────────────────────────────────────────
emoji, grade_label, grade_desc = get_grade(good_pct)
grade_color = ("#00e676" if good_pct >= 65 else "#ffea00" if good_pct >= 45 else "#ff1744")

st.markdown(f"""
<div class="grade-card">
  <div class="grade-emoji">{emoji}</div>
  <div>
    <div class="grade-title" style="color:{grade_color}">{grade_label}</div>
    <div class="grade-sub">{grade_desc}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# TOP METRICS
# ──────────────────────────────────────────────────────────────────────────────
m1, m2, m3, m4, m5 = st.columns(5)
metrics = [
    (m1, "Posture Score",  f"{good_pct}%",     "good" if good_pct >= 65 else "warn" if good_pct >= 45 else "bad"),
    (m2, "Session Time",   dur_str,             "wht"),
    (m3, "Good Posture",   f"{good_pct}%",      "good"),
    (m4, "Bad Posture",    f"{bad_pct}%",       "bad" if bad_pct > 20 else "wht"),
    (m5, "Alerts Fired",   str(alert_count),    "bad" if alert_count > 3 else "warn" if alert_count else "good"),
]
for col, lbl, val, cls in metrics:
    with col:
        st.markdown(f"<div class='mc'><div class='lbl'>{lbl}</div><div class='val {cls}'>{val}</div></div>",
                    unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# SECTION A: Posture Breakdown + Timeline
# ──────────────────────────────────────────────────────────────────────────────
cola, colb = st.columns([1, 1], gap="large")

with cola:
    st.markdown("<div class='sh'>Posture Breakdown</div>", unsafe_allow_html=True)

    def prog(label, pct, color):
        st.markdown(f"""
        <div style="margin-bottom:.9rem">
          <div style="display:flex;justify-content:space-between;font-size:.85rem;margin-bottom:.3rem">
            <span style="color:var(--text)">{label}</span>
            <span style="font-family:'Space Mono',monospace;color:{color};font-weight:700">{pct}%</span>
          </div>
          <div class="prog-bar-bg">
            <div class="prog-bar-fill" style="width:{pct}%;background:{color}"></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    prog("🟢 Good Posture",    good_pct, "#00e676")
    prog("🟡 Slightly Bent",   warn_pct, "#ffea00")
    prog("🔴 Bad Posture",     bad_pct,  "#ff1744")

    # Time breakdown
    st.markdown("<div class='sh'>Time Breakdown</div>", unsafe_allow_html=True)
    ta, tb = st.columns(2)
    with ta:
        gs_str = f"{good_sec//60}m {good_sec%60}s"
        st.markdown(f"<div class='mc'><div class='lbl'>Good Posture Time</div><div class='val good'>{gs_str}</div></div>",
                    unsafe_allow_html=True)
    with tb:
        bs_str = f"{bad_sec//60}m {bad_sec%60}s"
        st.markdown(f"<div class='mc'><div class='lbl'>Bad Posture Time</div><div class='val bad'>{bs_str}</div></div>",
                    unsafe_allow_html=True)

with colb:
    st.markdown("<div class='sh'>Posture Timeline</div>", unsafe_allow_html=True)
    if history:
        n = len(history); svw, svh = 400, 100; bw = max(2, svw // n - 1)
        bars = "".join(
            f'<rect x="{i*(svw//n)}" y="{svh - int(v*svh)}" width="{bw}" height="{int(v*svh)}" fill="{c}" rx="1"/>'
            for i, p in enumerate(history)
            for v, c in [(
                (1.00, "#00e676") if p == "Good Posture" else
                (0.55, "#ffea00") if p == "Slightly Bent" else
                (0.18, "#ff1744")
            )]
        )
        st.markdown(
            f'<svg viewBox="0 0 {svw} {svh}" xmlns="http://www.w3.org/2000/svg" '
            f'style="width:100%;border-radius:10px;background:#161922;display:block;">'
            f'{bars}</svg>', unsafe_allow_html=True)
        st.caption("🟢 Good  🟡 Slightly Bent  🔴 Bad  —  Each bar = 1 frame")
    else:
        st.info("No timeline data available.")

    # Donut-style pie via SVG
    st.markdown("<div class='sh'>Distribution</div>", unsafe_allow_html=True)
    if total > 0:
        def arc_path(cx, cy, r, start_deg, end_deg):
            import math
            s = math.radians(start_deg - 90)
            e = math.radians(end_deg   - 90)
            x1, y1 = cx + r * math.cos(s), cy + r * math.sin(s)
            x2, y2 = cx + r * math.cos(e), cy + r * math.sin(e)
            large  = 1 if (end_deg - start_deg) > 180 else 0
            return f"M {cx} {cy} L {x1:.1f} {y1:.1f} A {r} {r} 0 {large} 1 {x2:.1f} {y2:.1f} Z"

        segs = [(good_pct, "#00e676"), (warn_pct, "#ffea00"), (bad_pct, "#ff1744")]
        paths = ""
        cur = 0
        for pct, col_ in segs:
            if pct > 0:
                end = cur + pct * 3.6
                paths += f'<path d="{arc_path(70,70,55,cur,end)}" fill="{col_}" opacity=".85"/>'
                cur = end
        paths += '<circle cx="70" cy="70" r="30" fill="#161922"/>'
        paths += f'<text x="70" y="74" text-anchor="middle" font-family="Space Mono" font-size="14" fill="#e8eaf0" font-weight="700">{good_pct}%</text>'

        st.markdown(
            f'<svg viewBox="0 0 180 140" xmlns="http://www.w3.org/2000/svg" style="width:100%;background:#161922;border-radius:10px">'
            f'{paths}'
            f'<rect x="140" y="20" width="10" height="10" fill="#00e676" rx="2"/>'
            f'<text x="155" y="29" font-size="9" fill="#b0bcc8" font-family="DM Sans">Good</text>'
            f'<rect x="140" y="40" width="10" height="10" fill="#ffea00" rx="2"/>'
            f'<text x="155" y="49" font-size="9" fill="#b0bcc8" font-family="DM Sans">Slight</text>'
            f'<rect x="140" y="60" width="10" height="10" fill="#ff1744" rx="2"/>'
            f'<text x="155" y="69" font-size="9" fill="#b0bcc8" font-family="DM Sans">Bad</text>'
            f'</svg>', unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# SECTION B: Recommendations & Exercises
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("## 💡 Personalised Recommendations & Exercises")

if bad_pct >= 40:
    st.error(f"⚠️ Your bad posture was **{bad_pct}%** of the session. The high-priority recommendations below will help significantly.")
elif bad_pct >= 20:
    st.warning(f"🟡 {bad_pct}% bad posture detected. Review the tips below to improve.")
else:
    st.success(f"🟢 Great session! Below are habits and exercises to maintain your excellent posture.")

recs = get_recommendations(good_pct, bad_pct)

# Group by category
cat_order = ["stretch", "exercise", "habit", "ergo"]
cat_labels = {
    "stretch":  "🤸 Stretches",
    "exercise": "💪 Strengthening Exercises",
    "habit":    "🧠 Posture Habits",
    "ergo":     "🪑 Ergonomic Fixes",
}

for cat in cat_order:
    cat_recs = [r for r in recs if r["tag"] == cat]
    if not cat_recs:
        continue

    st.markdown(f"<div class='sh'>{cat_labels[cat]}</div>", unsafe_allow_html=True)
    icon, label_txt, tag_cls = TAG_META[cat]

    cols = st.columns(2)
    for i, rec in enumerate(cat_recs):
        with cols[i % 2]:
            st.markdown(f"""
            <div class="rec-card">
              <span class="tag {tag_cls}">{icon} {label_txt}</span>
              <h4>{rec['title']}</h4>
              <p>{rec['desc']}</p>
            </div>
            """, unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# FOOTER CTA
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("---")
c1, c2 = st.columns(2)
with c1:
    st.markdown("### Ready to improve?")
    st.markdown("Start a new monitoring session and track your progress.")
    if st.button("🧘 Back to Monitor →", use_container_width=True, type="primary"):
        st.switch_page("pages/1_Monitor.py")
with c2:
    st.markdown("### Quick Stats Reminder")
    st.markdown(f"""
    - 🕒 **Session duration:** {dur_str}
    - 🟢 **Good posture:** {good_pct}% ({good_sec//60}m {good_sec%60}s)
    - 🔴 **Bad posture:** {bad_pct}% ({bad_sec//60}m {bad_sec%60}s)
    - 🔔 **Alerts triggered:** {alert_count}
    - 🏆 **Grade:** {grade_label}
    """)
