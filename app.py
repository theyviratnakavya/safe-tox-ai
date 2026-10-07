import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime

st.set_page_config(page_title="SafeTox-AI", page_icon="🛡️", layout="wide")

# =========================================================
# CONFIG
# =========================================================
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

# Blinking LED animation (same timing as the React version)
st.markdown(
    """
<style>
@keyframes ledBlinkMed  { 0%,49% {opacity:1} 50%,100% {opacity:.25} }
@keyframes ledBlinkHigh { 0%,29% {opacity:1} 30%,100% {opacity:.25} }
.led { display:inline-block; width:22px; height:22px; border-radius:50%; margin-right:14px; }
.led-med  { animation: ledBlinkMed 1.3s steps(1) infinite; }
.led-high { animation: ledBlinkHigh 0.45s steps(1) infinite; }
</style>
""",
    unsafe_allow_html=True,
)

# =========================================================
# HELPERS
# =========================================================
def severity(v, med, high):
    return 2 if v >= high else 1 if v >= med else 0

def now():
    return datetime.now().strftime("%H:%M:%S")

def apply_preset(name):
    st.session_state.update(PRESETS[name])
    if name != "normal":
        st.session_state.update(helmet=False, mask=False, gloves=False, approved=False)

def reset_all():
    apply_preset("normal")
    st.session_state.update(
        helmet=False, mask=False, gloves=False, approved=False,
        prev_overall=0, prev_granted=False,
        log=[(now(), "Console reset — monitoring resumed.")],
    )

def approve():
    st.session_state.approved = True

def zone_bar(g, value):
    med = g["med"] / g["max"] * 100
    high = g["high"] / g["max"] * 100
    pos = min(value / g["max"] * 100, 100)
    return f"""
<div style="position:relative;height:6px;border-radius:3px;overflow:hidden;display:flex;margin:-6px 0 2px 0;">
  <div style="width:{med}%;background:#059669b3"></div>
  <div style="width:{high - med}%;background:#d97706b3"></div>
  <div style="width:{100 - high}%;background:#dc2626b3"></div>
  <div style="position:absolute;left:{pos}%;top:0;width:2px;height:6px;background:white"></div>
</div>
<div style="display:flex;justify-content:space-between;font-size:10px;color:#64748b;font-family:monospace;margin-bottom:14px;">
  <span>0</span><span>med {g['med']}</span><span>high {g['high']}</span><span>{g['max']}</span>
</div>
"""

# =========================================================
# SESSION STATE
# =========================================================
if "init" not in st.session_state:
    st.session_state.update(PRESETS["normal"])
    st.session_state.update(
        helmet=False, mask=False, gloves=False, approved=False,
        sound=False, prev_overall=0, prev_granted=False,
        log=[(now(), "System initialized — monitoring sewage chamber conditions.")],
        init=True,
    )

ss = st.session_state

# =========================================================
# DERIVED VALUES
# =========================================================
sevs = [severity(ss[g["key"]], g["med"], g["high"]) for g in GAS]
overall = max(sevs)
trig = GAS[sevs.index(overall)]
thr = trig["high"] if overall == 2 else trig["med"]

gas_ok = overall == 0
ppe_ok = ss.helmet and ss.mask and ss.gloves

# Auto-revoke supervisor approval if upstream checks fail
if ss.approved and not (gas_ok and ppe_ok):
    ss.approved = False

granted = gas_ok and ppe_ok and ss.approved

# =========================================================
# EVENT LOG
# =========================================================
if overall != ss.prev_overall:
    if overall == 0:
        msg = "Gas levels returned to safe range — LED green, buzzer silent."
    else:
        msg = (
            f"Risk reclassified {RISK[overall]} — {trig['formula']} at "
            f"{ss[trig['key']]}{trig['unit']} (threshold {thr}{trig['unit']}). "
            f"{'Red' if overall == 2 else 'Amber'} LED + buzzer active."
        )
    ss.log.insert(0, (now(), msg))
    ss.prev_overall = overall

if granted != ss.prev_granted:
    ss.log.insert(0, (now(), "Entry authorization GRANTED — green signal active."
                      if granted else "Entry authorization BLOCKED — red signal active."))
    ss.prev_granted = granted

ss.log = ss.log[:12]

# =========================================================
# HEADER
# =========================================================
st.title("🛡️ SafeTox-AI")
st.caption("Sewage entry control — live simulation console")

b1, b2, b3, b4 = st.columns(4)
b1.button("🟢 Normal conditions", on_click=apply_preset, args=("normal",), use_container_width=True)
b2.button("🟡 Moderate gas rise", on_click=apply_preset, args=("moderate",), use_container_width=True)
b3.button("🔴 H₂S leak", on_click=apply_preset, args=("leak",), use_container_width=True)
b4.button("🔄 Reset console", on_click=reset_all, use_container_width=True)

st.divider()

col1, col2, col3 = st.columns(3)

# =========================================================
# PANEL 1 — SENSOR READINGS
# =========================================================
with col1:
    st.subheader("🌫️ Sensor readings")
    for g in GAS:
        st.slider(
            f"{g['formula']} ({g['sensor']}) — {g['unit']}",
            0, g["max"], key=g["key"],
            help=f"Medium ≥ {g['med']}, High ≥ {g['high']} {g['unit']}",
        )
        st.markdown(zone_bar(g, ss[g["key"]]), unsafe_allow_html=True)
    st.caption("🌡️ Temp / Humidity: 31°C / 68%")

# =========================================================
# PANEL 2 — AI RISK + ALERT HARDWARE
# =========================================================
with col2:
    st.subheader("🤖 AI risk prediction")
    c = COLORS[overall]

    st.markdown(
        f"""
<div style="border:2px solid {c};background:{c}22;border-radius:12px;padding:24px;text-align:center;">
  <div style="font-size:42px;font-weight:700;color:{c};">{RISK[overall]}</div>
  <div style="font-size:12px;color:#94a3b8;">Random Forest classifier · confidence {CONF[overall]}%</div>
</div>
""",
        unsafe_allow_html=True,
    )

    if overall == 0:
        st.caption("All monitored gases are within safe limits.")
    else:
        st.caption(f"Driven by {trig['formula']} at {ss[trig['key']]} {trig['unit']} "
                   f"(threshold {thr}{trig['unit']}).")

    st.markdown("### 🚨 Alert hardware")

    leds = ""
    for i in range(3):
        if i == overall:
            cls = "led-high" if i == 2 else "led-med" if i == 1 else ""
            style = f"background:{COLORS[i]};box-shadow:0 0 14px {COLORS[i]};"
        else:
            cls = ""
            style = f"background:{COLORS[i]};opacity:.15;"
        leds += (
            f"<span style='display:inline-block;text-align:center;'>"
            f"<span class='led {cls}' style='{style}'></span><br>"
            f"<span style='font-size:10px;color:#64748b;'>{RISK[i]}</span></span>"
        )
    st.markdown(leds, unsafe_allow_html=True)

    if overall == 0:
        st.success(f"🔕 Buzzer: {BUZZER[0]}")
    elif overall == 1:
        st.warning(f"🔔 Buzzer: {BUZZER[1]}")
    else:
        st.error(f"🚨 Buzzer: {BUZZER[2]}")

    # ---- Real browser buzzer ----
    st.toggle("🔊 Buzzer sound", key="sound")

    if ss.sound and overall > 0:
        interval = 450 if overall == 2 else 1300  # ms between beeps
        freq = 1000 if overall == 2 else 700      # Hz
        components.html(
            f"""
<style>
  body {{ margin:0; font-family:Arial,sans-serif; }}
  button {{ display:none; width:100%; padding:10px; border:none; border-radius:8px;
            background:#334155; color:white; font-weight:bold; cursor:pointer; }}
</style>
<button id="tap" onclick="ctx.resume(); this.style.display='none'">🔊 Tap to start sound</button>
<script>
  const ctx = new (window.AudioContext || window.webkitAudioContext)();
  ctx.resume();
  function beep() {{
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = "square";
    osc.frequency.value = {freq};
    gain.gain.setValueAtTime(0.0001, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.12, ctx.currentTime + 0.01);
    gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.16);
    osc.connect(gain).connect(ctx.destination);
    osc.start();
    osc.stop(ctx.currentTime + 0.17);
  }}
  beep();
  setInterval(beep, {interval});
  setTimeout(() => {{
    if (ctx.state !== "running") document.getElementById("tap").style.display = "block";
  }}, 300);
</script>
""",
            height=50,
        )

# =========================================================
# PANEL 3 — ENTRY AUTHORIZATION
# =========================================================
with col3:
    st.subheader("🚪 Entry authorization")

    st.markdown(f"{'✅' if gas_ok else '❌'} **1. Gas safety check**")
    st.caption("Risk level LOW — cleared." if gas_ok else "Blocked until risk returns to LOW.")

    st.markdown(f"{'✅' if ppe_ok else ('❌' if gas_ok else '⚪')} **2. PPE verification**")
    st.checkbox("🪖 Helmet", key="helmet", disabled=not gas_ok)
    st.checkbox("😷 Mask", key="mask", disabled=not gas_ok)
    st.checkbox("🧤 Gloves", key="gloves", disabled=not gas_ok)

    st.markdown(
        f"{'✅' if ss.approved else ('❌' if gas_ok and ppe_ok else '⚪')} **3. Supervisor approval**"
    )
    st.button(
        "✅ Approved" if ss.approved else "Approve entry",
        on_click=approve,
        disabled=not (gas_ok and ppe_ok) or ss.approved,
        use_container_width=True,
    )

    if granted:
        st.success("🟢 ENTRY GRANTED — green LED")
    else:
        st.error("🔴 ENTRY BLOCKED — red LED")

# =========================================================
# EVENT LOG + FOOTER
# =========================================================
st.divider()
st.subheader("📋 Event log")
for t, m in ss.log:
    st.text(f"{t}  {m}")

st.divider()
st.caption(
    "⚠️ Simulated console for demonstration — sensor values are generated locally, "
    "not read from live hardware. Enable “Buzzer sound” to hear the alert tone."
)