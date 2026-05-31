"""
=============================================================================
 monitoring.py
 Vehicle Predictive Maintenance — Prometheus Metrics
=============================================================================
 Exposes metrics at http://localhost:8000/metrics
 Scraped by Prometheus, visualised in Grafana.

 Metrics exposed:
   vpm_queries_total          Counter   — total queries by track and fault/risk label
   vpm_response_time_seconds  Histogram — LLM response latency per track
   vpm_fault_class_total      Counter   — fault class distribution (Track 1)
   vpm_risk_class_total       Counter   — risk class distribution (Track 2)
   vpm_rag_chunks_retrieved   Histogram — number of RAG chunks retrieved per query
   vpm_active_sessions        Gauge     — currently active Streamlit sessions

 Usage in app_technician.py / app_owner.py:
   from monitoring import (
       record_track1_query,
       record_track2_query,
       set_active_sessions,
       start_metrics_server,
   )

   start_metrics_server(port=8000)   # call once at app startup
   record_track1_query(result)       # call after every Track 1 LLM response
   record_track2_query(result)       # call after every Track 2 LLM response
=============================================================================
"""

import logging
import threading
from typing import Dict, Any, Optional

from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    start_http_server,
    REGISTRY,
)

log = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# METRIC DEFINITIONS
# ─────────────────────────────────────────────────────────────────────────────

# Total queries — labelled by track (1 or 2) and result label
QUERIES_TOTAL = Counter(
    name="vpm_queries_total",
    documentation="Total number of prediction queries processed",
    labelnames=["track", "label"],
)

# LLM response time — labelled by track
# Buckets cover expected range: 0.5s to 30s
RESPONSE_TIME = Histogram(
    name="vpm_response_time_seconds",
    documentation="LLM chain response time in seconds",
    labelnames=["track"],
    buckets=[0.5, 1.0, 2.0, 3.0, 5.0, 8.0, 10.0, 15.0, 20.0, 30.0],
)

# Fault class distribution — Track 1 only
FAULT_CLASS_TOTAL = Counter(
    name="vpm_fault_class_total",
    documentation="Track 1: count of each fault class detected",
    labelnames=["fault_class", "fault_label"],
)

# Risk class distribution — Track 2 only
RISK_CLASS_TOTAL = Counter(
    name="vpm_risk_class_total",
    documentation="Track 2: count of each risk class detected",
    labelnames=["risk_class", "risk_label"],
)

# RAG chunks retrieved per query — labelled by track
RAG_CHUNKS = Histogram(
    name="vpm_rag_chunks_retrieved",
    documentation="Number of RAG context chunks retrieved per query",
    labelnames=["track"],
    buckets=[1, 2, 3, 4, 5, 6, 8],
)

# Active sessions — current number of open Streamlit sessions
ACTIVE_SESSIONS = Gauge(
    name="vpm_active_sessions",
    documentation="Currently active Streamlit sessions across both apps",
    labelnames=["app"],
)

# Normal (no-alert) skips — how often the system correctly stays silent
NORMAL_SKIP_TOTAL = Counter(
    name="vpm_normal_skip_total",
    documentation="Queries where result was Normal/No Risk and no LLM call was made",
    labelnames=["track"],
)


# ─────────────────────────────────────────────────────────────────────────────
# RECORD HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def record_track1_query(result: Dict[str, Any]) -> None:
    """
    Record metrics for a completed Track 1 (Technician) query.

    Args:
        result: Dict returned by llm_chain.run_track1()
                Expected keys: fault_class, fault_label, response_time_ms,
                               context_chunks
    """
    fault_class = str(result.get("fault_class", "unknown"))
    fault_label = result.get("fault_label", "unknown")
    resp_ms     = result.get("response_time_ms", 0)
    chunks      = result.get("context_chunks", 0)

    # Count query
    QUERIES_TOTAL.labels(track="1", label=fault_label).inc()

    # Count fault class
    FAULT_CLASS_TOTAL.labels(
        fault_class=fault_class,
        fault_label=fault_label,
    ).inc()

    # Record response time (convert ms → seconds)
    if resp_ms > 0:
        RESPONSE_TIME.labels(track="1").observe(resp_ms / 1000)

    # Record RAG chunks
    if chunks > 0:
        RAG_CHUNKS.labels(track="1").observe(chunks)

    # Track normal (no-action) results separately
    if fault_class == "0":
        NORMAL_SKIP_TOTAL.labels(track="1").inc()

    log.debug(
        f"[Metrics T1] fault={fault_label}  "
        f"resp={resp_ms}ms  chunks={chunks}"
    )


def record_track2_query(result: Dict[str, Any]) -> None:
    """
    Record metrics for a completed Track 2 (Owner) query.

    Args:
        result: Dict returned by llm_chain.run_track2()
                Expected keys: risk_class, risk_label, response_time_ms,
                               context_chunks
    """
    risk_class = str(result.get("risk_class", "unknown"))
    risk_label = result.get("risk_label", "unknown")
    resp_ms    = result.get("response_time_ms", 0)
    chunks     = result.get("context_chunks", 0)

    # Count query
    QUERIES_TOTAL.labels(track="2", label=risk_label).inc()

    # Count risk class
    RISK_CLASS_TOTAL.labels(
        risk_class=risk_class,
        risk_label=risk_label,
    ).inc()

    # Record response time
    if resp_ms > 0:
        RESPONSE_TIME.labels(track="2").observe(resp_ms / 1000)

    # Record RAG chunks (0 for Class 0 — no LLM call)
    if chunks > 0:
        RAG_CHUNKS.labels(track="2").observe(chunks)

    # Track no-risk skips
    if risk_class == "0":
        NORMAL_SKIP_TOTAL.labels(track="2").inc()

    log.debug(
        f"[Metrics T2] risk={risk_label}  "
        f"resp={resp_ms}ms  chunks={chunks}"
    )


def set_active_sessions(app: str, count: int) -> None:
    """
    Update the active session gauge for a given app.

    Args:
        app:   "technician" or "owner"
        count: Current number of active sessions
    """
    ACTIVE_SESSIONS.labels(app=app).set(count)


# ─────────────────────────────────────────────────────────────────────────────
# METRICS SERVER
# ─────────────────────────────────────────────────────────────────────────────

_server_started = False
_server_lock    = threading.Lock()


def start_metrics_server(port: int = 8000) -> None:
    """
    Start the Prometheus HTTP metrics server on the given port.
    Safe to call multiple times — only starts once.

    Metrics are exposed at:  http://localhost:{port}/metrics

    Args:
        port: Port for the Prometheus scrape endpoint (default 8000).
              Must be open in Google Cloud VM firewall rules.
    """
    global _server_started
    with _server_lock:
        if _server_started:
            log.info(f"Metrics server already running on :{port}")
            return
        try:
            start_http_server(port)
            _server_started = True
            log.info(f"Prometheus metrics server started on :{port}/metrics")
        except OSError as e:
            # Port already in use — another process (e.g. the other app) has it
            log.warning(f"Could not start metrics server on :{port} — {e}")
            log.warning("Metrics will still be recorded in-process.")


# ─────────────────────────────────────────────────────────────────────────────
# GRAFANA DASHBOARD CONFIG (printed for reference)
# ─────────────────────────────────────────────────────────────────────────────

GRAFANA_PANELS = {
    "Total Queries by Track": {
        "type":  "stat",
        "query": 'sum by (track) (vpm_queries_total)',
        "note":  "Shows total queries split between Track 1 and Track 2",
    },
    "LLM Response Time (p95)": {
        "type":  "gauge",
        "query": 'histogram_quantile(0.95, rate(vpm_response_time_seconds_bucket[5m]))',
        "note":  "95th percentile response time — key SLA metric",
    },
    "LLM Response Time Distribution": {
        "type":  "heatmap",
        "query": 'rate(vpm_response_time_seconds_bucket[5m])',
        "note":  "Response time heatmap over time",
    },
    "Fault Class Distribution (Track 1)": {
        "type":  "pie",
        "query": 'vpm_fault_class_total',
        "note":  "Breakdown of fault types detected by the workshop system",
    },
    "Risk Class Distribution (Track 2)": {
        "type":  "pie",
        "query": 'vpm_risk_class_total',
        "note":  "Breakdown of risk levels detected in owner alerts",
    },
    "Query Rate (per minute)": {
        "type":  "timeseries",
        "query": 'rate(vpm_queries_total[1m])',
        "note":  "Real-time query throughput",
    },
    "Active Sessions": {
        "type":  "stat",
        "query": 'vpm_active_sessions',
        "note":  "Live session count per app",
    },
    "Normal / No-Risk Skips": {
        "type":  "stat",
        "query": 'vpm_normal_skip_total',
        "note":  "Queries correctly skipped (vehicle healthy — no LLM call needed)",
    },
}


def print_grafana_reference() -> None:
    """Print Grafana panel configuration for manual setup."""
    print("\n" + "=" * 60)
    print("  Grafana Dashboard Panel Reference")
    print("=" * 60)
    for panel, cfg in GRAFANA_PANELS.items():
        print(f"\n  Panel : {panel}")
        print(f"  Type  : {cfg['type']}")
        print(f"  Query : {cfg['query']}")
        print(f"  Note  : {cfg['note']}")
    print()


# ─────────────────────────────────────────────────────────────────────────────
# SELF-TEST
# ─────────────────────────────────────────────────────────────────────────────

# if __name__ == "__main__":
#     import time

#     logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")

#     print("\n" + "=" * 60)
#     print("  Monitoring — Self Test")
#     print("=" * 60)

#     # Start metrics server
#     start_metrics_server(port=8000)

#     # Simulate Track 1 queries
#     print("\nSimulating Track 1 queries ...")
#     mock_t1_results = [
#         {"fault_class": 0, "fault_label": "Normal",              "response_time_ms": 0,    "context_chunks": 0},
#         {"fault_class": 6, "fault_label": "Oil Pressure Issue",  "response_time_ms": 3200, "context_chunks": 4},
#         {"fault_class": 3, "fault_label": "Cooling System Problem","response_time_ms": 2800,"context_chunks": 4},
#         {"fault_class": 1, "fault_label": "Battery Degradation", "response_time_ms": 2500, "context_chunks": 4},
#         {"fault_class": 4, "fault_label": "Engine Misfire",      "response_time_ms": 3100, "context_chunks": 4},
#     ]
#     for r in mock_t1_results:
#         record_track1_query(r)
#         print(f"  Recorded T1: {r['fault_label']}")

#     # Simulate Track 2 queries
#     print("\nSimulating Track 2 queries ...")
#     mock_t2_results = [
#         {"risk_class": 0, "risk_label": "No Risk",     "response_time_ms": 0,    "context_chunks": 0},
#         {"risk_class": 3, "risk_label": "High Risk",   "response_time_ms": 2900, "context_chunks": 4},
#         {"risk_class": 2, "risk_label": "Medium Risk", "response_time_ms": 2600, "context_chunks": 4},
#         {"risk_class": 1, "risk_label": "Low Risk",    "response_time_ms": 2200, "context_chunks": 4},
#     ]
#     for r in mock_t2_results:
#         record_track2_query(r)
#         print(f"  Recorded T2: {r['risk_label']}")

#     # Set session counts
#     set_active_sessions("technician", 2)
#     set_active_sessions("owner", 5)
#     print("\nActive sessions set: technician=2, owner=5")

#     # Print Grafana reference
#     print_grafana_reference()

#     print(f"Metrics exposed at: http://localhost:8000/metrics")
#     print("Keeping server alive for 15s so you can visit the URL ...")
#     time.sleep(15)
#     print("\nSelf-test complete.")
