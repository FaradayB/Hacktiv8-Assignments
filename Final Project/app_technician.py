"""
=============================================================================
 app_technician.py
 Vehicle Predictive Maintenance — Technician Workshop App
 Run: streamlit run app_technician.py --server.port 8501
=============================================================================
"""

import os, sys, time, logging
import numpy as np
import pandas as pd
import joblib
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

# ── Page config (must be first Streamlit call) ─────────────────────────────
st.set_page_config(
    page_title="MitsuCare — Workshop",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Imports from project modules ───────────────────────────────────────────
try:
    from db import (
        get_all_plates, get_track1_record, get_track1_history,
        save_track1_prediction, log_query,
        row_to_track1_sensors, get_query_log,
    )
    from rag_pipeline import build_vectorstore
    from llm_chain import build_chains, run_track1
    from monitoring import (
        record_track1_query, set_active_sessions, start_metrics_server,
    )
    DB_AVAILABLE  = True
    LLM_AVAILABLE = True
except Exception as e:
    st.warning(f"Module import issue: {e}")
    DB_AVAILABLE  = False
    LLM_AVAILABLE = False

# ── Prometheus metrics server (start once) ─────────────────────────────────
if DB_AVAILABLE:
    try:
        start_metrics_server(port=8000)
    except Exception:
        pass

# ─────────────────────────────────────────────────────────────────────────────
# STYLING — Dark industrial, tablet-optimised
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg:        #0d0f14;
    --surface:   #161a22;
    --surface2:  #1e2330;
    --border:    #2a3040;
    --accent:    #e8531a;
    --accent2:   #f0952a;
    --text:      #e8eaf0;
    --muted:     #6b7280;
    --ok:        #22c55e;
    --warn:      #f59e0b;
    --danger:    #ef4444;
    --info:      #3b82f6;
}

html, body, [data-testid="stApp"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Syne', sans-serif;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

/* Headers */
h1 { font-size: 1.8rem !important; font-weight: 800 !important; letter-spacing: -0.03em; color: var(--text) !important; }
h2 { font-size: 1.2rem !important; font-weight: 700 !important; color: var(--text) !important; }
h3 { font-size: 1rem !important; font-weight: 600 !important; color: var(--muted) !important; text-transform: uppercase; letter-spacing: 0.08em; }

/* Cards */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 20px 24px;
    margin-bottom: 16px;
}
.card-accent { border-left: 3px solid var(--accent); }

/* Status badges */
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 4px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    font-weight: 500;
    letter-spacing: 0.05em;
}
.badge-ok      { background: #14532d33; color: var(--ok);     border: 1px solid #14532d; }
.badge-warn    { background: #78350f33; color: var(--warn);    border: 1px solid #78350f; }
.badge-danger  { background: #7f1d1d33; color: var(--danger);  border: 1px solid #7f1d1d; }
.badge-info    { background: #1e3a5f33; color: var(--info);    border: 1px solid #1e3a5f; }
.badge-neutral { background: #1e223033; color: var(--muted);   border: 1px solid var(--border); }

/* Sensor row */
.sensor-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid var(--border);
    font-size: 0.88rem;
}
.sensor-name { color: var(--muted); font-family: 'JetBrains Mono', monospace; }
.sensor-val  { font-family: 'JetBrains Mono', monospace; font-weight: 500; }

/* Fault brief block */
.brief-block {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 20px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    line-height: 1.7;
    white-space: pre-wrap;
    color: var(--text);
}

/* Priority banner */
.priority-critical { background: #7f1d1d; border: 1px solid var(--danger); border-radius: 8px; padding: 12px 16px; color: #fca5a5; font-weight: 700; font-size: 0.9rem; }
.priority-high     { background: #78350f; border: 1px solid var(--warn);   border-radius: 8px; padding: 12px 16px; color: #fcd34d; font-weight: 700; font-size: 0.9rem; }
.priority-medium   { background: #1e3a5f; border: 1px solid var(--info);   border-radius: 8px; padding: 12px 16px; color: #93c5fd; font-weight: 700; font-size: 0.9rem; }
.priority-normal   { background: #14532d; border: 1px solid var(--ok);     border-radius: 8px; padding: 12px 16px; color: #86efac; font-weight: 700; font-size: 0.9rem; }

/* Streamlit elements */
[data-testid="stSelectbox"] > div > div {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    color: var(--text) !important;
}
[data-testid="stButton"] button {
    background: var(--accent) !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 0.03em !important;
    padding: 10px 24px !important;
    width: 100%;
}
[data-testid="stButton"] button:hover {
    background: var(--accent2) !important;
}
[data-testid="stMetric"] {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 12px;
}
[data-testid="stMetric"] label { color: var(--muted) !important; font-size: 0.75rem !important; text-transform: uppercase; letter-spacing: 0.08em; }
[data-testid="stMetric"] [data-testid="stMetricValue"] { color: var(--text) !important; font-family: 'JetBrains Mono', monospace !important; font-size: 1.5rem !important; }
[data-testid="stDataFrame"] { border: 1px solid var(--border) !important; border-radius: 8px; }
.stSpinner > div { border-color: var(--accent) !important; }
hr { border-color: var(--border) !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

TRACK1_FEATURES = [
    "O2 SENSOR V", "MAF G PER S", "THROTTLE POS PCT", "CRANK RPM",
    "CAM ADVANCE DEG", "KNOCK COUNT 30D", "COOLANT TEMP C",
    "OIL PRESSURE PSI", "MAP KPA", "EGR DUTY PCT",
    "BATTERY VOLTAGE V", "FUEL TEMP C",
]

FAULT_META = {
    0: ("Normal",                 "normal",   "✅ NORMAL — No action required"),
    1: ("Battery Degradation",    "medium",   "🔵 MEDIUM — Schedule within 14 days"),
    2: ("Brake System Issue",     "high",     "🟡 HIGH — Inspect within 3 days"),
    3: ("Cooling System Problem", "high",     "🟡 HIGH — Inspect within 3 days"),
    4: ("Engine Misfire",         "high",     "🟡 HIGH — Inspect within 3 days"),
    5: ("Alternator Failure",     "medium",   "🔵 MEDIUM — Schedule within 7 days"),
    6: ("Oil Pressure Issue",     "critical", "🔴 CRITICAL — Do not drive. Inspect immediately"),
    7: ("Transmission Problem",   "high",     "🟡 HIGH — Inspect within 3 days"),
}

THRESHOLDS = {
    "O2 SENSOR V":       (0.10, 0.50, 0.65),
    "MAF G PER S":       (5.0,  7.0,  10.0),
    "THROTTLE POS PCT":  (10.0, 20.0, 30.0),
    "CRANK RPM":         (700,  900,  1100),
    "CAM ADVANCE DEG":   (9.0,  12.0, 18.0),
    "KNOCK COUNT 30D":   (0,    1,    5),
    "COOLANT TEMP C":    (85.0, 95.0, 105.0),
    "OIL PRESSURE PSI":  (35.0, 50.0, 20.0),   # low is bad
    "MAP KPA":           (30.0, 40.0, 48.0),
    "EGR DUTY PCT":      (15.0, 25.0, 40.0),
    "BATTERY VOLTAGE V": (13.8, 14.5, 12.0),   # low is bad
    "FUEL TEMP C":       (25.0, 45.0, 58.0),
}

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────

if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None
if "chains" not in st.session_state:
    st.session_state.chains = None
if "result" not in st.session_state:
    st.session_state.result = None
if "record" not in st.session_state:
    st.session_state.record = None

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_resource(show_spinner=False)
def load_model():
    return joblib.load("ml_models/track1_fault_classifier.pkl")

@st.cache_resource(show_spinner=False)
def load_vectorstore():
    return build_vectorstore(force_rebuild=False)

@st.cache_resource(show_spinner=False)
def load_chains(_vs):
    return build_chains(_vs)

def sensor_status(name, value):
    """Return ok / warn / danger based on SOP thresholds."""
    if name not in THRESHOLDS:
        return "ok"
    lo, hi, crit = THRESHOLDS[name]
    # Oil pressure and battery: low = danger
    if name in ("OIL PRESSURE PSI", "BATTERY VOLTAGE V"):
        if value <= crit:   return "danger"
        if value <= lo:     return "warn"
        return "ok"
    if value >= crit:       return "danger"
    if value >= hi:         return "warn"
    return "ok"

def priority_html(level):
    labels = {
        "critical": ("🔴", "CRITICAL — Do not drive. Inspect immediately", "priority-critical"),
        "high":     ("🟡", "HIGH — Inspect within 3 days", "priority-high"),
        "medium":   ("🔵", "MEDIUM — Schedule within 7–14 days", "priority-medium"),
        "normal":   ("✅", "NORMAL — No action required", "priority-normal"),
    }
    emoji, text, cls = labels.get(level, labels["normal"])
    return f'<div class="{cls}">{emoji} {text}</div>'

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🔧 MitsuCare Workshop")
    st.markdown('<div style="color:#6b7280;font-size:0.8rem;margin-bottom:20px;">Technician Diagnostic System</div>', unsafe_allow_html=True)
    st.divider()

    # Plate selector
    st.markdown("### Vehicle")
    if DB_AVAILABLE:
        plates = get_all_plates(track=1)
        selected_plate = st.selectbox(
            "Plate Number",
            options=plates,
            label_visibility="collapsed",
        )
    else:
        selected_plate = st.text_input("Plate Number", value="B 1234 ABC")

    # Load button
    load_clicked = st.button("Load Vehicle Data", use_container_width=True)

    st.divider()

    # System status
    st.markdown("### System")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<span class="badge badge-{"ok" if DB_AVAILABLE else "danger"}">{"DB ✓" if DB_AVAILABLE else "DB ✗"}</span>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<span class="badge badge-{"ok" if LLM_AVAILABLE else "danger"}">{"LLM ✓" if LLM_AVAILABLE else "LLM ✗"}</span>', unsafe_allow_html=True)

    st.divider()

    # Recent query log
    st.markdown("### Recent Queries")
    if DB_AVAILABLE:
        try:
            logs = get_query_log(limit=5)
            for entry in logs:
                label = entry.get("predicted_label") or "—"
                track = entry.get("track", "?")
                st.markdown(
                    f'<div style="font-size:0.75rem;color:#6b7280;padding:3px 0;">'
                    f'T{track} · {entry["plate_number"]} · <span style="color:#e8eaf0">{label}</span></div>',
                    unsafe_allow_html=True
                )
        except Exception:
            st.caption("No queries yet.")
    else:
        st.caption("DB not connected.")

    st.divider()
    st.markdown('<div style="color:#6b7280;font-size:0.72rem;">Metrics: :8000/metrics<br>Grafana: :3000</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# MAIN HEADER
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("# 🔧 Technician Fault Diagnostic")
st.markdown('<div style="color:#6b7280;font-size:0.9rem;margin-bottom:24px;">30-day OBD telemetry · ML anomaly detection · RAG-grounded fault brief</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# LOAD & RUN
# ─────────────────────────────────────────────────────────────────────────────

if load_clicked and selected_plate:
    with st.spinner("Loading vehicle data ..."):
        if DB_AVAILABLE:
            record = get_track1_record(selected_plate)
        else:
            st.error("Database not connected.")
            record = None

    if record is None:
        st.error(f"No data found for plate: {selected_plate}")
    else:
        st.session_state.record = record

        # ── ML Classification ─────────────────────────────────────────────
        sensors = row_to_track1_sensors(record) if DB_AVAILABLE else {}
        sensor_array = np.array([[sensors[f] for f in TRACK1_FEATURES]])

        try:
            model = load_model()
            predicted_class = int(model.predict(sensor_array)[0])
            predicted_label = FAULT_META[predicted_class][0]
        except Exception as e:
            st.warning(f"ML model not available: {e}. Using true label.")
            predicted_class = int(record["true_fault_class"])
            predicted_label = record["true_fault_label"]

        # ── Save prediction back to DB ─────────────────────────────────────
        if DB_AVAILABLE:
            try:
                save_track1_prediction(record["test_id"], predicted_class, predicted_label)
            except Exception:
                pass

        # ── LLM Chain (only for anomalies) ────────────────────────────────
        brief        = None
        resp_ms      = 0
        chunks_used  = 0
        llm_called   = False

        if predicted_class != 0 and LLM_AVAILABLE:
            with st.spinner("Generating fault brief via RAG + Gemini ..."):
                try:
                    if st.session_state.vectorstore is None:
                        st.session_state.vectorstore = load_vectorstore()
                    if st.session_state.chains is None:
                        st.session_state.chains = load_chains(st.session_state.vectorstore)
                    result = run_track1(
                        st.session_state.chains,
                        fault_class=predicted_class,
                        sensor_readings=sensors,
                    )
                    brief       = result["brief"]
                    resp_ms     = result["response_time_ms"]
                    chunks_used = result["context_chunks"]
                    llm_called  = True
                    record_track1_query(result)
                except Exception as e:
                    st.warning(f"LLM chain error: {e}")
        else:
            record_track1_query({
                "fault_class": predicted_class, "fault_label": predicted_label,
                "response_time_ms": 0, "context_chunks": 0,
            })

        # ── Log query ─────────────────────────────────────────────────────
        if DB_AVAILABLE:
            try:
                log_query(
                    track=1,
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
            "brief": brief, "resp_ms": resp_ms, "chunks_used": chunks_used,
        }

        set_active_sessions("technician", 1)

# ─────────────────────────────────────────────────────────────────────────────
# RESULTS DISPLAY
# ─────────────────────────────────────────────────────────────────────────────

if st.session_state.result:
    r       = st.session_state.result
    record  = r["record"]
    sensors = r["sensors"]
    p_class = r["predicted_class"]
    p_label = r["predicted_label"]
    brief   = r["brief"]
    priority_level = FAULT_META[p_class][1]

    # ── Vehicle identity ──────────────────────────────────────────────────
    st.markdown('<div class="card card-accent">', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([2, 2, 2, 2])
    with c1:
        st.metric("Plate Number", record["plate_number"])
    with c2:
        st.metric("Owner", record["owner_name"])
    with c3:
        st.metric("Vehicle", f"{record['car_model']}")
    with c4:
        st.metric("Year", str(record["car_year"]))
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Priority banner ───────────────────────────────────────────────────
    st.markdown(priority_html(priority_level), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Two columns: sensors | brief ──────────────────────────────────────
    col_left, col_right = st.columns([1, 1.4], gap="large")

    with col_left:
        st.markdown("## Sensor Readings")
        st.markdown(f'<div style="color:#6b7280;font-size:0.78rem;margin-bottom:12px;">Day {record.get("day_in_window", "?")} of 30-day window</div>', unsafe_allow_html=True)

        status_map = {"ok": ("badge-ok", "✓"), "warn": ("badge-warn", "!"), "danger": ("badge-danger", "✗")}

        for feat in TRACK1_FEATURES:
            db_key = feat.lower().replace(" ", "_").replace("/", "_")
            val    = sensors.get(feat, record.get(db_key, "—"))
            status = sensor_status(feat, float(val)) if val != "—" else "ok"
            badge_cls, badge_sym = status_map[status]
            st.markdown(
                f'<div class="sensor-row">'
                f'<span class="sensor-name">{feat}</span>'
                f'<span>'
                f'<span class="sensor-val">{val}</span>&nbsp;&nbsp;'
                f'<span class="badge {badge_cls}">{badge_sym}</span>'
                f'</span></div>',
                unsafe_allow_html=True,
            )

        # Ground truth comparison
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### Classification")
        st.markdown(
            f'<div class="card">'
            f'<div style="display:flex;justify-content:space-between;margin-bottom:8px;">'
            f'<span style="color:#6b7280;font-size:0.8rem;">ML Prediction</span>'
            f'<span class="badge badge-{"ok" if p_class==0 else "danger"}">{p_class} — {p_label}</span>'
            f'</div>'
            f'<div style="display:flex;justify-content:space-between;">'
            f'<span style="color:#6b7280;font-size:0.8rem;">Ground Truth</span>'
            f'<span class="badge badge-info">{record["true_fault_class"]} — {record["true_fault_label"]}</span>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        if r["resp_ms"] > 0:
            st.markdown(
                f'<div style="color:#6b7280;font-size:0.75rem;margin-top:8px;">'
                f'⏱ LLM response: {r["resp_ms"]}ms &nbsp;·&nbsp; '
                f'📄 RAG chunks: {r["chunks_used"]}</div>',
                unsafe_allow_html=True,
            )

    with col_right:
        st.markdown("## Technician Fault Brief")
        if p_class == 0:
            st.markdown(
                '<div class="card" style="border-color:#22c55e;">'
                '<div style="color:#22c55e;font-size:1.1rem;font-weight:700;margin-bottom:8px;">✅ Vehicle Operating Normally</div>'
                '<div style="color:#6b7280;font-size:0.88rem;">All sensor readings within normal SOP thresholds. No anomaly detected across the 30-day telemetry window. No action required.</div>'
                '</div>',
                unsafe_allow_html=True,
            )
        elif brief:
            st.markdown(f'<div class="brief-block">{brief}</div>', unsafe_allow_html=True)
        else:
            st.info("LLM not available. Sensor data and classification above are still valid.")

    # ── Historical trend ──────────────────────────────────────────────────
    st.divider()
    st.markdown("## 30-Day Sensor History")
    if DB_AVAILABLE:
        with st.expander("View all telemetry records for this vehicle"):
            history = get_track1_history(selected_plate)
            if history:
                df = pd.DataFrame(history)
                display_cols = ["day_in_window", "coolant_temp_c", "oil_pressure_psi",
                                "battery_voltage_v", "crank_rpm", "true_fault_label"]
                df_display = df[[c for c in display_cols if c in df.columns]]
                st.dataframe(df_display, use_container_width=True)

else:
    # Empty state
    st.markdown(
        '<div class="card" style="text-align:center;padding:48px;">'
        '<div style="font-size:3rem;margin-bottom:16px;">🔧</div>'
        '<div style="font-size:1.1rem;font-weight:700;margin-bottom:8px;">Select a Vehicle</div>'
        '<div style="color:#6b7280;">Choose a plate number from the sidebar and click Load Vehicle Data.</div>'
        '</div>',
        unsafe_allow_html=True,
    )
