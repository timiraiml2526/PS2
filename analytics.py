import streamlit as st
import time, math
from collections import deque

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@400;500;600&display=swap');
:root{--good:#00e676;--warn:#ffea00;--bad:#ff1744;--bg:#0d0f14;--card:#161922;--border:#1e2230;--text:#e8eaf0;--muted:#6b7280;--accent:#6c63ff}
html,body,[data-testid="stAppViewContainer"]{background:var(--bg)!important;color:var(--text)!important;font-family:'DM Sans',sans-serif}
[data-testid="stSidebar"]{display:none!important}
[data-testid="stSidebarCollapsedControl"]{display:none!important}
h1,h2,h3,h4{font-family:'Space Mono',monospace}
#MainMenu,footer{visibility:hidden}
[data-testid="stToolbar"]{display:none}
[data-testid="stHeader"]{background:transparent!important}
header [data-testid="stDecoration"]{display:none}
header [data-testid="stStatusWidget"]{display:none}
.mc{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:1.2rem 1.3rem;text-align:center;margin-bottom:.6rem}
.mc .lbl{font-size:.68rem;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin-bottom:.3rem}
.mc .val{font-family:'Space Mono',monospace;font-size:2rem;font-weight:700;line-height:1}
.val.good{color:var(--good)}.val.warn{color:var(--warn)}.val.bad{color:var(--bad)}.val.wht{color:var(--text)}
.sh{font-family:'Space Mono',monospace;font-size:.68rem;letter-spacing:.15em;text-transform:uppercase;color:var(--muted);border-bottom:1px solid var(--border);padding-bottom:.3rem;margin:1.3rem 0 .75rem}
.grade-card{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:1.5rem 2rem;margin-bottom:1rem;display:flex;align-items:center;gap:1.5rem}
.grade-emoji{font-size:3.5rem;line-height:1}
.grade-title{font-family:'Space Mono',monospace;font-size:1.25rem;font-weight:700;margin-bottom:.25rem}
.grade-sub{color:var(--muted);font-size:.9rem}
.rec-card{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:1.1rem 1.3rem;margin-bottom:.65rem}
.rec-card h4{font-family:'Space Mono',monospace;font-size:.88rem;margin:0 0 .4rem}
.rec-card p{color:#b0bcc8;font-size:.87rem;margin:0;line-height:1.55}
.tag{display:inline-block;padding:.2rem .65rem;border-radius:999px;font-size:.7rem;font-weight:700;letter-spacing:.05em;margin-bottom:.5rem}
.tag-s{background:rgba(0,230,118,.12);color:var(--good);border:1px solid rgba(0,230,118,.25)}
.tag-e{background:rgba(108,99,255,.15);color:#a89fff;border:1px solid rgba(108,99,255,.3)}
.tag-h{background:rgba(255,234,0,.1);color:var(--warn);border:1px solid rgba(255,234,0,.25)}
.tag-g{background:rgba(255,23,68,.1);color:#ff6b8a;border:1px solid rgba(255,23,68,.2)}
.pb-bg{background:#1e2230;border-radius:999px;height:10px;width:100%;overflow:hidden;margin-top:.3rem}
.pb-fill{height:100%;border-radius:999px}
.stButton>button{border-radius:8px!important;font-weight:600!important}
.nav-btn>button{background:var(--card)!important;border:1px solid var(--border)!important;color:var(--text)!important;font-size:.82rem!important;padding:.3rem .85rem!important;border-radius:8px!important;font-weight:600!important;transition:all .2s}
.nav-btn>button:hover{border-color:var(--accent)!important;color:var(--accent)!important}
.logout-btn>button{background:rgba(255,23,68,.10)!important;border:1px solid rgba(255,23,68,.35)!important;color:#ff1744!important;font-size:.82rem!important;padding:.3rem .85rem!important;border-radius:8px!important;font-weight:600!important;transition:all .2s}
.logout-btn>button:hover{background:rgba(255,23,68,.22)!important}
</style>
""", unsafe_allow_html=True)

# ── DATA ──────────────────────────────────────────────────────────────────────
total_good    = st.session_state.get("total_good",    0)
total_warn    = st.session_state.get("total_warn",    0)
total_bad     = st.session_state.get("total_bad",     0)
total         = total_good + total_warn + total_bad
alert_count   = st.session_state.get("alert_count",  0)
session_start = st.session_state.get("session_start", None)
history       = list(st.session_state.get("history",  deque()))

good_pct = round(total_good / total * 100) if total else 0
warn_pct = round(total_warn / total * 100) if total else 0
bad_pct  = round(total_bad  / total * 100) if total else 0

if st.session_state.session_active:
    dur = int(time.time() - st.session_state.session_start)
else:
    dur = int(st.session_state.session_end - st.session_state.session_start)
dur_str  = f"{dur//3600:02d}:{(dur%3600)//60:02d}:{dur%60:02d}"
good_sec = round(total_good / total * dur) if total else 0
bad_sec  = round(total_bad  / total * dur) if total else 0

# ── GRADES & RECS ─────────────────────────────────────────────────────────────
def grade(pct):
    if pct>=80: return "🏆","Excellent","Outstanding session! Your posture habits are top-notch.","#00e676"
    if pct>=65: return "👍","Good","Solid. A little more mindfulness and you'll be great.","#00e676"
    if pct>=45: return "⚠️","Needs Work","Room for improvement. Use the tips below.","#ffea00"
    return        "❌","Poor","Posture needs serious attention. Start with the exercises below.","#ff1744"

RECS = [
    ("s","🤸 Stretch","Chin Tucks",
     "Gently pull chin straight back, creating a double chin. Hold 5 sec, repeat 10x/hr. Counters forward-head posture.","bad"),
    ("s","🤸 Stretch","Doorway Chest Stretch",
     "Stand in doorway, forearms on frame at 90 degrees, lean forward gently. Hold 20-30 sec. Releases hunching tightness.","bad"),
    ("s","🤸 Stretch","Upper Trapezius Stretch",
     "Drop right ear to right shoulder, reach left arm down. Hold 20 sec each side. Relieves shoulder/neck tension.","warn"),
    ("s","🤸 Stretch","Cat-Cow",
     "On all fours, alternate arching and rounding your back for 10 slow reps. Mobilises the entire spine.","warn"),
    ("e","💪 Exercise","Wall Angels",
     "Back flat on wall, arms at 90 degrees, slide up and down like a snow angel. 3x10. Activates deep postural muscles.","bad"),
    ("e","💪 Exercise","Band Pull-Aparts",
     "Hold resistance band at shoulder width, pull it apart horizontally. 3x15. Strengthens rhomboids and rear delts.","bad"),
    ("e","💪 Exercise","Dead Bug",
     "Lie on back, extend opposite arm and leg slowly, lower back pressed down. 3x8/side. Core stability for upright posture.","warn"),
    ("e","💪 Exercise","Prone Cobra",
     "Face down, squeeze shoulder blades, lift chest slightly. Hold 10 sec, repeat 10x. Strengthens spinal extensors.","warn"),
    ("e","💪 Exercise","Plank",
     "Forearm plank 30-60 sec, hips level. 3 sets. Full-chain core exercise that directly supports upright posture.","good"),
    ("h","🧠 Habit","20-20-2 Rule",
     "Every 20 min, look 20 feet away for 20 sec, then stand and move for 2 min. Reduces fatigue and postural collapse.","bad"),
    ("h","🧠 Habit","Hourly Posture Alarm",
     "Set a phone buzz every hour. Check: feet flat, back straight, shoulders relaxed, screen at eye level.","bad"),
    ("h","🧠 Habit","Mindful Sitting Reset",
     "Each time you sit, do a 3-second reset: feet flat, hips back, spine tall, shoulders relaxed, chin neutral.","warn"),
    ("h","🧠 Habit","Stay Hydrated",
     "Drink water every hour. Dehydrated spinal discs compress more easily. Hydration literally keeps you straighter.","good"),
    ("g","🪑 Ergonomics","Monitor at Eye Level",
     "Top of screen at or slightly below eye level. Use a monitor riser + external keyboard if on a laptop.","bad"),
    ("g","🪑 Ergonomics","Chair Height & Lumbar",
     "Feet flat on floor, knees at ~90 degrees. Use a lumbar pillow behind lower back to maintain natural spinal curve.","bad"),
    ("g","🪑 Ergonomics","Keyboard & Mouse Position",
     "Keep at elbow height so arms rest without shrugging. Wrists should float while typing.","warn"),
]

TAG_CSS  = {"s":"tag-s","e":"tag-e","h":"tag-h","g":"tag-g"}
CAT_LABEL= {"s":"Stretches","e":"Exercises","h":"Habits","g":"Ergonomics"}

def get_recs(bad_pct):
    order = ["bad","warn","g","good"] if bad_pct>=40 else \
            ["warn","bad","g","good"] if bad_pct>=20 else ["good","warn","bad","g"]
    out=[]
    for p in order:
        out+=[r for r in RECS if r[4]==p and r not in out]
    return out

# ── PAGE HEADER ───────────────────────────────────────────────────────────────
hdr_left, hdr_right = st.columns([5, 1], gap="small")
with hdr_left:
    st.markdown("# 📊 Analytics & Recommendations")
    st.markdown(f"Session insights for **{st.session_state.get('user_name','User')}**")
with hdr_right:
    st.markdown("<div style='height:1.1rem'></div>", unsafe_allow_html=True)
    st.markdown("<div class='nav-btn'>", unsafe_allow_html=True)
    if st.button("🧘 Home", use_container_width=True, key="nav_monitor"):
        st.switch_page("monitor.py")
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div class='logout-btn'>", unsafe_allow_html=True)
    if st.button("🚪 Logout", use_container_width=True, key="nav_logout"):
        st.switch_page("logout.py")
    st.markdown("</div>", unsafe_allow_html=True)

if total == 0:
    st.info("🔍 No session data yet. Go to **Monitor**, start a session, then come back here.")
    st.stop()

# Grade card
em, gl, gd, gc = grade(good_pct)
st.markdown(f"""
<div class="grade-card">
  <div class="grade-emoji">{em}</div>
  <div><div class="grade-title" style="color:{gc}">{gl}</div>
       <div class="grade-sub">{gd}</div></div>
</div>""", unsafe_allow_html=True)

# Top metrics
m1,m2,m3,m4,m5 = st.columns(5)
for col,lbl,val,cls in [(m1,"Posture Score",f"{good_pct}%",
                          "good" if good_pct>=65 else "warn" if good_pct>=45 else "bad"),
                         (m2,"Session Time",dur_str,"wht"),
                         (m3,"Good Posture",f"{good_pct}%","good"),
                         (m4,"Bad Posture", f"{bad_pct}%","bad" if bad_pct>20 else "wht"),
                         (m5,"Alerts Fired",str(alert_count),
                          "bad" if alert_count>3 else "warn" if alert_count else "good")]:
    with col:
        st.markdown(f"<div class='mc'><div class='lbl'>{lbl}</div>"
                    f"<div class='val {cls}'>{val}</div></div>", unsafe_allow_html=True)

# Breakdown + timeline
cola, colb = st.columns(2, gap="large")

with cola:
    st.markdown("<div class='sh'>Posture Breakdown</div>", unsafe_allow_html=True)
    for lbl,pct,color in [("🟢 Good Posture",good_pct,"#00e676"),
                           ("🟡 Slightly Bent",warn_pct,"#ffea00"),
                           ("🔴 Bad Posture",bad_pct,"#ff1744")]:
        st.markdown(f"""
        <div style="margin-bottom:.9rem">
          <div style="display:flex;justify-content:space-between;font-size:.85rem;margin-bottom:.3rem">
            <span>{lbl}</span>
            <span style="font-family:'Space Mono';color:{color};font-weight:700">{pct}%</span>
          </div>
          <div class="pb-bg"><div class="pb-fill" style="width:{pct}%;background:{color}"></div></div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div class='sh'>Time Breakdown</div>", unsafe_allow_html=True)
    ta,tb = st.columns(2)
    with ta:
        st.markdown(f"<div class='mc'><div class='lbl'>Good Time</div>"
                    f"<div class='val good'>{good_sec//60}m {good_sec%60}s</div></div>",
                    unsafe_allow_html=True)
    with tb:
        st.markdown(f"<div class='mc'><div class='lbl'>Bad Time</div>"
                    f"<div class='val bad'>{bad_sec//60}m {bad_sec%60}s</div></div>",
                    unsafe_allow_html=True)

with colb:
    st.markdown("<div class='sh'>Posture Timeline</div>", unsafe_allow_html=True)
    if history:
        n=len(history); svw,svh=400,100; bw=max(2,svw//n-1)
        bars="".join(
            f'<rect x="{i*(svw//n)}" y="{svh-int(v*svh)}" width="{bw}" height="{int(v*svh)}" fill="{c}" rx="1"/>'
            for i,p in enumerate(history)
            for v,c in [((1.00,"#00e676") if p=="Good Posture" else
                         (0.55,"#ffea00") if p=="Slightly Bent" else (0.18,"#ff1744"))])
        st.markdown(f'<svg viewBox="0 0 {svw} {svh}" xmlns="http://www.w3.org/2000/svg" '
                    f'style="width:100%;border-radius:10px;background:#161922;display:block;">'
                    f'{bars}</svg>', unsafe_allow_html=True)
        st.caption("Each bar = 1 detection frame")
    else:
        st.info("No timeline data.")

    # Mini donut
    st.markdown("<div class='sh'>Distribution</div>", unsafe_allow_html=True)
    def arc(cx,cy,r,s,e):
        s,e=math.radians(s-90),math.radians(e-90)
        x1,y1=cx+r*math.cos(s),cy+r*math.sin(s)
        x2,y2=cx+r*math.cos(e),cy+r*math.sin(e)
        lg=1 if (e-s)>math.pi else 0
        return f"M{cx} {cy}L{x1:.1f} {y1:.1f}A{r} {r} 0 {lg} 1 {x2:.1f} {y2:.1f}Z"
    segs=[(good_pct,"#00e676"),(warn_pct,"#ffea00"),(bad_pct,"#ff1744")]
    paths=""; cur=0
    for pct,col_ in segs:
        if pct>0:
            end=cur+pct*3.6
            paths+=f'<path d="{arc(70,70,55,cur,end)}" fill="{col_}" opacity=".85"/>'
            cur=end
    paths+='<circle cx="70" cy="70" r="30" fill="#161922"/>'
    paths+=f'<text x="70" y="74" text-anchor="middle" font-family="Space Mono" font-size="13" fill="#e8eaf0" font-weight="700">{good_pct}%</text>'
    st.markdown(f'<svg viewBox="0 0 180 140" xmlns="http://www.w3.org/2000/svg" '
                f'style="width:100%;background:#161922;border-radius:10px">'
                f'{paths}'
                f'<rect x="140" y="18" width="9" height="9" fill="#00e676" rx="2"/>'
                f'<text x="153" y="26" font-size="9" fill="#b0bcc8">Good</text>'
                f'<rect x="140" y="36" width="9" height="9" fill="#ffea00" rx="2"/>'
                f'<text x="153" y="44" font-size="9" fill="#b0bcc8">Slight</text>'
                f'<rect x="140" y="54" width="9" height="9" fill="#ff1744" rx="2"/>'
                f'<text x="153" y="62" font-size="9" fill="#b0bcc8">Bad</text>'
                f'</svg>', unsafe_allow_html=True)

# Recommendations
st.markdown("---")
st.markdown("## 💡 Personalised Recommendations")
if bad_pct>=40:   st.error(f"Bad posture was **{bad_pct}%** of the session. High-priority fixes below.")
elif bad_pct>=20: st.warning(f"{bad_pct}% bad posture. Review the tips below.")
else:             st.success(f"Great session! Habits below will maintain your excellent posture.")

recs = get_recs(bad_pct)
for cat in ["s","e","h","g"]:
    cat_recs=[r for r in recs if r[0]==cat]
    if not cat_recs: continue
    st.markdown(f"<div class='sh'>{CAT_LABEL[cat]}</div>", unsafe_allow_html=True)
    cols=st.columns(2)
    for i,rec in enumerate(cat_recs):
        with cols[i%2]:
            st.markdown(f"""
            <div class="rec-card">
              <span class="tag {TAG_CSS[rec[0]]}">{rec[1]}</span>
              <h4>{rec[2]}</h4><p>{rec[3]}</p>
            </div>""", unsafe_allow_html=True)

st.markdown("---")
c1,c2=st.columns(2)
with c1:
    st.markdown("### Ready to improve?")
    st.markdown("Go back to Monitor and start a new session.")
with c2:
    st.markdown(f"""
    **Session:** {dur_str} &nbsp;|&nbsp; **Score:** {good_pct}% &nbsp;|&nbsp;
    **Grade:** {gl} &nbsp;|&nbsp; **Alerts:** {alert_count}
    """)
