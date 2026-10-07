import streamlit as st
from datetime import datetime

st.set_page_config(page_title="SafeTox-AI", page_icon="🛡️", layout="wide")

# ---- Risk model (same thresholds as the React version) ----
GAS = [
    {"key": "h2s", "formula": "H₂S", "unit": "ppm",  "max": 40,  "med": 10, "high": 20,  "sensor": "MQ-136"},
    {"key": "ch4", "formula": "CH₄", "unit": "%LEL", "max": 50,  "med": 10, "high": 25,  "sensor": "MQ-2"},
    {"key": "nh3", "formula": "NH₃", "unit": "ppm",  "max": 80,  "med": 25, "high": 50,  "sensor": "MQ-137"},
    {"key": "co",  "formula": "CO",  "unit": "ppm",  "max": 150, "med": 35, "high": 100, "sensor": "MQ-7"},
]
RISK = ["LOW", "MEDIUM", "HIGH"]
BUZZER = ["Silent", "Intermittent beep", "Continuous alarm"]
COLORS = ["#10b981", "#f59e0b", "#ef4444"]
CONF = [96, 88, 93]

PRESETS = {
    "normal":   {"h2s": 4,  "ch4": 3,  "nh3": 8,  "co": 12},
    "moderate": {"h2s": 7,  "ch4": 14, "nh3": 12, "co": 20},
    "leak":     {"h2s": 28, "ch4": 6,  "nh3": 10, "co": 18},
}

def severity(v, med, high):
    return 2 if v >= high else 1 if v >= med else 0

def now():
    return datetime.now().strftime("%H:%M:%S")

# ---- Session state ----
if "init" not in st.session_state:
    st.session_state.update(PRESETS["normal"])
    st.session_state.update(helmet=False, mask=False, gloves=False, approved=False,
                            prev_overall=0, prev_granted=False, init=True,
                            log=[(now(), "System initialized — monitoring sewage chamber conditions.")])

def apply_preset(name):
    st.session_state.update(PRESETS[name])
    if name != "normal":
        st.session_state.update(helmet=False, mask=False, gloves=False, approved=False)

def reset_all():
    apply_preset("normal")
    st.session_state.update(helmet=False, mask=False, gloves=False, approved=False,
                            prev_overall=0, prev_granted=False,
                            log=[(now(), "Console reset — monitoring resumed.")])

def approve():
    st.session_state.approved = True

# ---- Derived values (computed before widgets draw) ----
ss = st.session_state
sevs = [severity(ss[g["key"]], g["med"], g["high"]) for g in GAS]
overall = max(sevs)
trig = GAS[sevs.index(overall)]

gas_ok = overall == 0
ppe_ok = ss.helmet and ss.mask and ss.gloves
if ss.approved and not (gas_ok and ppe_ok):
    ss.approved = False          # auto-revoke approval
granted = gas_ok and ppe_ok and ss.approved

# ---- Event log ----
if overall != ss.prev_overall:
    if overall == 0:
        msg = "Gas levels returned to safe range — LED green, buzzer silent."
    else:
        thr = trig["high"] if overall == 2 else trig["med"]
        msg = (f"Risk reclassified {RISK[overall]} — {trig['formula']} at "
               f"{ss[trig['key']]}{trig['unit']} (threshold {thr}{trig['unit']}).")
    ss.log.insert(0, (now(), msg))
    ss.prev_overall = overall
if granted != ss.prev_granted:
    ss.log.insert(0, (now(), "Entry authorization GRANTED — green signal active." if granted
                      else "Entry authorization BLOCKED — red signal active."))
    ss.prev_granted = granted
ss.log = ss.log[:12]

# ---- UI ----
st.title("🛡️ SafeTox-AI")
st.caption("Sewage entry control — live simulation console")

b1, b2, b3, b4 = st.columns([1, 1, 1, 1])
b1.button("Normal conditions", on_click=apply_preset, args=("normal",), use_container_width=True)
b2.button("Moderate gas rise", on_click=apply_preset, args=("moderate",), use_container_width=True)
b3.button("H₂S leak", on_click=apply_preset, args=("leak",), use_container_width=True)
b4.button("Reset console", on_click=reset_all, use_container_width=True)

col1, col2, col3 = st.columns(3)

# Panel 1: sensors
with col1:
    st.subheader("Sensor readings")
    for g in GAS:
        st.slider(f"{g['formula']} ({g['sensor']}) — {g['unit']}", 0, g["max"], key=g["key"],
                  help=f"Medium ≥ {g['med']}, High ≥ {g['high']} {g['unit']}")
    st.caption("🌡️ Temp / Humidity: 31°C / 68%")

# Panel 2: AI risk + hardware
with col2:
    st.subheader("AI risk prediction")
    c = COLORS[overall]
    st.markdown(
        f"""<div style="border:1px solid {c};background:{c}22;border-radius:8px;
        padding:24px;text-align:center">
        <div style="font-size:42px;font-weight:700;color:{c}">{RISK[overall]}</div>
        <div style="font-size:12px;color:#94a3b8">Random Forest classifier · confidence {CONF[overall]}%</div>
        </div>""", unsafe_allow_html=True)
    if overall == 0:
        st.caption("All monitored gases are within safe limits.")
    else:
        thr = trig["high"] if overall == 2 else trig["med"]
        st.caption(f"Driven by {trig['formula']} at {ss[trig['key']]} {trig['unit']} (threshold {thr}{trig['unit']}).")

    st.markdown("**Alert hardware**")
    leds = "".join(
        f"<span style='display:inline-block;width:18px;height:18px;border-radius:50%;"
        f"background:{COLORS[i]};margin-right:10px;opacity:{1 if i == overall else 0.15}'></span>"
        for i in range(3))
    st.markdown(leds, unsafe_allow_html=True)
    st.write(f"🔔 Buzzer: **{BUZZER[overall]}**" if overall else f"🔕 Buzzer: **{BUZZER[0]}**")

# Panel 3: entry authorization
with col3:
    st.subheader("Entry authorization")

    st.markdown(f"{'✅' if gas_ok else '❌'} **1. Gas safety check**")
    st.caption("Risk level LOW — cleared." if gas_ok else "Blocked until risk returns to LOW.")

    st.markdown(f"{'✅' if ppe_ok else ('❌' if gas_ok else '⚪')} **2. PPE verification**")
    st.checkbox("Helmet", key="helmet", disabled=not gas_ok)
    st.checkbox("Mask", key="mask", disabled=not gas_ok)
    st.checkbox("Gloves", key="gloves", disabled=not gas_ok)

    st.markdown(f"{'✅' if ss.approved else ('❌' if gas_ok and ppe_ok else '⚪')} **3. Supervisor approval**")
    st.button("Approved" if ss.approved else "Approve entry", on_click=approve,
              disabled=not (gas_ok and ppe_ok) or ss.approved)

    if granted:
        st.success("🟢 Entry granted — green LED")
    else:
        st.error("🔴 Entry blocked — red LED")

# Event log
st.subheader("Event log")
for t, m in ss.log:
    st.text(f"{t}  {m}")

st.caption("Simulated console for demonstration — sensor values are generated locally, not read from live hardware.")