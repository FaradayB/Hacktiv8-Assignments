"""
=============================================================================
 app_owner.py
 Vehicle Predictive Maintenance — Car Owner Mobile App
 Run: streamlit run app_owner.py --server.port 8502
=============================================================================
"""

import os, logging
import numpy as np
import joblib
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MitsuCare — My Car",
    page_icon="🚗",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Project imports ──────────────────────────────────────────────────────────
try:
    from db import (
        get_all_plates, get_track2_record,
        save_track2_prediction, log_query,
        row_to_track2_sensors, get_query_log,
    )
    from rag_pipeline import build_vectorstore
    from llm_chain import build_chains, run_track2
    from monitoring import (
        record_track2_query, set_active_sessions, start_metrics_server,
    )
    DB_AVAILABLE  = True
    LLM_AVAILABLE = True
except Exception as e:
    DB_AVAILABLE  = False
    LLM_AVAILABLE = False

try:
    start_metrics_server(port=8000)
except Exception:
    pass

# ─────────────────────────────────────────────────────────────────────────────
# STYLING — Clean mobile-first, warm & approachable
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=DM+Mono:wght@400;500&display=swap');

:root {
    --bg:       #f5f4f0;
    --surface:  #ffffff;
    --border:   #e2e0d8;
    --accent:   #c8381a;
    --accent2:  #e8531a;
    --text:     #1a1a1a;
    --muted:    #8a8578;
    --ok:       #16803c;
    --ok-bg:    #dcfce7;
    --warn:     #b45309;
    --warn-bg:  #fef9c3;
    --med:      #c2410c;
    --med-bg:   #ffedd5;
    --danger:   #b91c1c;
    --danger-bg:#fee2e2;
}

html, body, [data-testid="stApp"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    max-width: 480px;
    margin: 0 auto;
}

/* Hide Streamlit chrome for mobile feel */
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stHeader"] { display: none !important; }

footer { display: none !important; }

[data-testid="stSidebar"] { display: none; }

/* App shell */
.block-container { padding: 16px 16px 60px !important; max-width: 480px !important; }

/* Typography */
h1 { font-size: 1.5rem !important; font-weight: 800 !important; color: var(--text) !important; margin-bottom: 4px !important; }
h2 { font-size: 1.1rem !important; font-weight: 700 !important; color: var(--text) !important; }
h3 { font-size: 0.8rem !important; font-weight: 600 !important; color: var(--muted) !important; text-transform: uppercase; letter-spacing: 0.07em; }

/* Top nav bar */
.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 0 20px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 20px;
}
.topbar-logo { font-size: 1.1rem; font-weight: 800; color: var(--accent); }
.topbar-sub  { font-size: 0.75rem; color: var(--muted); }

/* Vehicle card */
.vehicle-card {
    background: var(--text);
    color: white;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
}
.vehicle-card::before {
    content: '';
    position: absolute;
    top: -30px; right: -30px;
    width: 120px; height: 120px;
    background: var(--accent);
    border-radius: 50%;
    opacity: 0.15;
}
.vehicle-plate {
    font-family: 'DM Mono', monospace;
    font-size: 1.4rem;
    font-weight: 500;
    letter-spacing: 0.05em;
    margin-bottom: 4px;
}
.vehicle-name { font-size: 0.85rem; opacity: 0.7; }
.vehicle-owner { font-size: 1rem; font-weight: 700; margin-bottom: 2px; }

/* Risk card variants */
.risk-card {
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 16px;
}
.risk-none   { background: var(--ok-bg);     border: 1.5px solid #bbf7d0; }
.risk-low    { background: var(--warn-bg);   border: 1.5px solid #fde68a; }
.risk-medium { background: var(--med-bg);    border: 1.5px solid #fed7aa; }
.risk-high   { background: var(--danger-bg); border: 1.5px solid #fecaca; }

.risk-title {
    font-size: 1.1rem;
    font-weight: 800;
    margin-bottom: 4px;
}
.risk-none   .risk-title { color: var(--ok);     }
.risk-low    .risk-title { color: var(--warn);   }
.risk-medium .risk-title { color: var(--med);    }
.risk-high   .risk-title { color: var(--danger); }

/* Alert bubble */
.alert-bubble {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    border-top-left-radius: 4px;
    padding: 16px;
    margin-bottom: 16px;
    font-size: 0.9rem;
    line-height: 1.65;
    color: var(--text);
    white-space: pre-wrap;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

/* Sensor pills */
.sensor-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin-bottom: 16px;
}
.sensor-pill {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 10px 12px;
}
.sensor-pill-label { font-size: 0.7rem; color: var(--muted); font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 2px; }
.sensor-pill-value { font-family: 'DM Mono', monospace; font-size: 1rem; font-weight: 500; }
.sensor-pill.ok     { border-color: #bbf7d0; }
.sensor-pill.warn   { border-color: #fde68a; background: #fefce8; }
.sensor-pill.danger { border-color: #fecaca; background: #fff5f5; }

/* CTA button */
[data-testid="stButton"] button {
    background: var(--accent) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    padding: 12px 24px !important;
    width: 100%;
    letter-spacing: 0.01em !important;
}
[data-testid="stButton"] button:hover { background: var(--accent2) !important; }

/* Selectbox */
[data-testid="stSelectbox"] > div > div {
    background: var(--surface) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

.stSpinner > div { border-color: var(--accent) !important; }

/* Bottom safe area */
.bottom-space { height: 40px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

TRACK2_FEATURES = [
    "O2 SENSOR V", "MAF G PER S", "THROTTLE POS PCT",
    "COOLANT TEMP C", "OIL PRESSURE PSI", "BATTERY VOLTAGE V",
    "TPMS PSI", "AMBIENT TEMP C", "CABIN HUMIDITY PCT",
    "FUEL LEVEL PCT", "BRAKE PEDAL EVENTS", "SPEED KMH",
]

RISK_META = {
    0: ("Tidak Ada Risiko", "none",   "🟢", "Kendaraan Anda dalam kondisi baik"),
    1: ("Risiko Rendah",    "low",    "🟡", "Pantau kondisi kendaraan"),
    2: ("Risiko Sedang",    "medium", "🟠", "Jadwalkan servis segera"),
    3: ("Risiko Tinggi",    "high",   "🔴", "Inspeksi segera diperlukan!"),
}

SENSOR_DISPLAY = {
    "COOLANT TEMP C":     ("Suhu Mesin",    "°C"),
    "OIL PRESSURE PSI":   ("Tekanan Oli",   "PSI"),
    "BATTERY VOLTAGE V":  ("Daya Baterai",  "V"),
    "TPMS PSI":           ("Tekanan Ban",   "PSI"),
    "FUEL LEVEL PCT":     ("Bahan Bakar",   "%"),
    "SPEED KMH":          ("Kecepatan",     "km/h"),
}

SENSOR_THRESHOLDS_T2 = {
    "COOLANT TEMP C":    (95.0, 105.0),
    "OIL PRESSURE PSI":  (35.0, 25.0),
    "BATTERY VOLTAGE V": (13.8, 12.5),
    "TPMS PSI":          (30.0, 27.0),
    "FUEL LEVEL PCT":    (25.0, 10.0),
    "SPEED KMH":         (60.0, 90.0),
}

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────

for key in ["vectorstore", "chains", "result"]:
    if key not in st.session_state:
        st.session_state[key] = None

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_resource(show_spinner=False)
def load_model():
    return joblib.load("ml_models/track2_risk_classifier.pkl")

@st.cache_resource(show_spinner=False)
def load_vectorstore():
    return build_vectorstore(force_rebuild=False)

@st.cache_resource(show_spinner=False)
def load_chains(_vs):
    return build_chains(_vs)

def sensor_status_t2(name, value):
    if name not in SENSOR_THRESHOLDS_T2:
        return "ok"
    warn_th, danger_th = SENSOR_THRESHOLDS_T2[name]
    # Low-is-bad sensors
    if name in ("OIL PRESSURE PSI", "BATTERY VOLTAGE V", "TPMS PSI", "FUEL LEVEL PCT"):
        if value <= danger_th: return "danger"
        if value <= warn_th:   return "warn"
        return "ok"
    # High-is-bad sensors
    if value >= danger_th: return "danger"
    if value >= warn_th:   return "warn"
    return "ok"

# ─────────────────────────────────────────────────────────────────────────────
# TOP BAR
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="topbar">
    <div>
        <div class="topbar-logo">🚗 MitsuCare</div>
        <div class="topbar-sub">Pemantauan Kesehatan Kendaraan</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# PLATE SELECTOR
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("### Pilih Kendaraan Anda")

if DB_AVAILABLE:
    plates = get_all_plates(track=2)
    selected_plate = st.selectbox(
        "Nomor Plat",
        options=plates,
        label_visibility="collapsed",
    )
else:
    selected_plate = st.text_input("Nomor Plat", value="B 1234 ABC", label_visibility="collapsed")

check_clicked = st.button("Cek Kondisi Kendaraan 🔍", use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# LOAD & RUN
# ─────────────────────────────────────────────────────────────────────────────

if check_clicked and selected_plate:
    with st.spinner("Memuat data kendaraan ..."):
        record = get_track2_record(selected_plate) if DB_AVAILABLE else None

    if record is None:
        st.error(f"Data tidak ditemukan untuk plat: {selected_plate}")
    else:
        sensors = row_to_track2_sensors(record) if DB_AVAILABLE else {}
        sensor_array = np.array([[sensors[f] for f in TRACK2_FEATURES]])

        # ML classification
        try:
            model = load_model()
            predicted_class = int(model.predict(sensor_array)[0])
            predicted_label = RISK_META[predicted_class][0]
        except Exception as e:
            predicted_class = int(record["true_risk_class"])
            predicted_label = record["true_risk_label"]

        if DB_AVAILABLE:
            try:
                save_track2_prediction(record["test_id"], predicted_class, predicted_label)
            except Exception:
                pass

        # LLM alert (only if risk > 0)
        alert       = None
        resp_ms     = 0
        chunks_used = 0
        llm_called  = False

        if predicted_class > 0 and LLM_AVAILABLE:
            with st.spinner("Membuat notifikasi ..."):
                try:
                    if st.session_state.vectorstore is None:
                        st.session_state.vectorstore = load_vectorstore()
                    if st.session_state.chains is None:
                        st.session_state.chains = load_chains(st.session_state.vectorstore)
                    result = run_track2(
                        st.session_state.chains,
                        risk_class=predicted_class,
                        sensor_readings=sensors,
                    )
                    alert       = result["alert"]
                    resp_ms     = result["response_time_ms"]
                    chunks_used = result["context_chunks"]
                    llm_called  = True
                    record_track2_query(result)
                except Exception as e:
                    st.warning(f"LLM tidak tersedia: {e}")
        else:
            record_track2_query({
                "risk_class": predicted_class, "risk_label": predicted_label,
                "response_time_ms": 0, "context_chunks": 0,
            })

        if DB_AVAILABLE:
            try:
                log_query(
                    track=2,
                    plate_number=selected_plate,
                    test_id=record["test_id"],
                    predicted_class=predicted_class,
                    predicted_label=predicted_label,
                    response_time_ms=resp_ms,
                    context_chunks=chunks_used,
                    llm_called=llm_called,
                )
            except Exception:
                pass

        st.session_state.result = {
            "record": record, "sensors": sensors,
            "predicted_class": predicted_class, "predicted_label": predicted_label,
            "alert": alert, "resp_ms": resp_ms,
        }
        set_active_sessions("owner", 1)

# ─────────────────────────────────────────────────────────────────────────────
# RESULTS
# ─────────────────────────────────────────────────────────────────────────────

if st.session_state.result:
    r       = st.session_state.result
    record  = r["record"]
    sensors = r["sensors"]
    p_class = r["predicted_class"]
    p_label = RISK_META[p_class][0]
    emoji   = RISK_META[p_class][2]
    tagline = RISK_META[p_class][3]
    risk_css = RISK_META[p_class][1]

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Vehicle card ──────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="vehicle-card">
        <div class="vehicle-owner">{record['owner_name']}</div>
        <div class="vehicle-plate">{record['plate_number']}</div>
        <div class="vehicle-name">{record['car_model']} · {record['car_year']}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Risk status card ──────────────────────────────────────────────────
    st.markdown(f"""
    <div class="risk-card risk-{risk_css}">
        <div class="risk-title">{emoji} {p_label}</div>
        <div style="font-size:0.88rem;">{tagline}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Push alert bubble ─────────────────────────────────────────────────
    if p_class == 0:
        st.markdown("""
        <div class="alert-bubble" style="border-color:#bbf7d0;">
✅ <b>Kendaraan Anda dalam kondisi baik.</b>

Semua sensor berada dalam rentang normal hari ini. Tidak ada tindakan yang diperlukan.

Tetap pantau kondisi kendaraan Anda secara rutin.</div>
        """, unsafe_allow_html=True)
    elif r["alert"]:
        st.markdown(f'<div class="alert-bubble">{r["alert"]}</div>', unsafe_allow_html=True)
    else:
        # Fallback if LLM unavailable
        fallback_msgs = {
            1: "🟡 Pantau kondisi kendaraan Anda selama 3-5 hari ke depan.",
            2: "🟠 Jadwalkan servis di bengkel resmi Mitsubishi dalam 7 hari.\nHubungi: 1-500-989",
            3: "🔴 JANGAN MENGENDARAI KENDARAAN.\nHubungi layanan darurat Mitsubishi: 1-500-989",
        }
        st.markdown(f'<div class="alert-bubble">{fallback_msgs.get(p_class, "")}</div>', unsafe_allow_html=True)

    # ── Sensor pills (owner-friendly labels only) ─────────────────────────
    st.markdown("### Status Sensor")
    st.markdown('<div class="sensor-grid">', unsafe_allow_html=True)
    for feat, (label, unit) in SENSOR_DISPLAY.items():
        val    = sensors.get(feat, "—")
        status = sensor_status_t2(feat, float(val)) if val != "—" else "ok"
        st.markdown(
            f'<div class="sensor-pill {status}">'
            f'<div class="sensor-pill-label">{label}</div>'
            f'<div class="sensor-pill-value">{val} <span style="font-size:0.7rem;opacity:0.6">{unit}</span></div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Ground truth (small, for evaluation) ─────────────────────────────
    with st.expander("ℹ️ Detail evaluasi"):
        st.caption(f"True Risk Class : {record['true_risk_class']} — {record['true_risk_label']}")
        st.caption(f"Predicted Class : {p_class} — {p_label}")
        if r["resp_ms"] > 0:
            st.caption(f"Response time   : {r['resp_ms']} ms")

    st.markdown('<div class="bottom-space"></div>', unsafe_allow_html=True)

else:
    # Empty state
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center;padding:32px 16px;">
        <div style="font-size:3.5rem;margin-bottom:12px;">🚗</div>
        <div style="font-size:1rem;font-weight:700;margin-bottom:6px;color:#1a1a1a;">Cek Kondisi Kendaraan Anda</div>
        <div style="color:#8a8578;font-size:0.88rem;">Pilih nomor plat dan tekan tombol di atas untuk melihat status kendaraan hari ini.</div>
    </div>
    """, unsafe_allow_html=True)
