# MitsuCare — AI-Powered Predictive Maintenance System
**Hacktiv8 LLM Bootcamp — Final Project (PTP Program)**

> *"Most vehicles don't break down from bad parts — they break down because no one saw it coming."*

MitsuCare is an end-to-end AI system that detects vehicle fault patterns **before warning lights appear**, delivering a structured diagnostic brief to workshop technicians and a plain-language Bahasa Indonesia alert to vehicle owners — grounded in Standard Operating Procedure documents via a RAG pipeline.

---

## System Architecture

```
Vehicle Sensors & OBD
        │
        ▼
  IoT Layer (1–2 hr intervals, 7 AM – 7 PM)
        │
        ▼
  PostgreSQL Database
        │
        ├────────────────────────────────────┐
        ▼                                    ▼
Track 1 — Workshop / Mechanic        Track 2 — Vehicle Owner
        │                                    │
ML Anomaly Detection                  ML Risk Detection
(30-day telemetry, 8 classes)         (12-hr window, 4 classes)
        │                                    │
   [Normal] → No action              [No Risk] → No notification
        │                                    │
   [Anomaly] ↓                         [Risk] ↓
        │                                    │
LLM + RAG (Gemini 2.0 Flash)         LLM Summarizer (Gemini 2.0 Flash)
SOP: sop_track1_*.md                 SOP: sop_track2_*.md
ChromaDB vector store                ChromaDB vector store
        │                                    │
        ▼                                    ▼
Technician Fault Brief               Push Alert — Bahasa Indonesia
(English, structured)                (Plain language, urgency + action)
        │                                    │
app_technician.py :8501              app_owner.py :8502
```

**Monitoring:** Prometheus scrapes `:8000/metrics` → Grafana dashboard at `:3000`

---

## Project Structure

```
mitsucare/
├── app_technician.py                    # Streamlit tablet UI — Track 1
├── app_owner.py                         # Streamlit mobile UI — Track 2
├── rag_pipeline.py                      # RAG: load → chunk → embed → store → retrieve
├── llm_chain.py                         # LLM prompt chains (Track 1 + Track 2)
├── monitoring.py                        # Prometheus metrics
├── db.py                                # PostgreSQL connection + queries
│
├── docs/
│   ├── sop_track1_technician_fault_diagnosis.md   # RAG knowledge base (Track 1)
│   └── sop_track2_owner_risk_alert.md             # RAG knowledge base (Track 2)
│
├── ml_models/
│   ├── track1_fault_classifier.pkl      # SVM classifier — 8 fault classes
│   └── track2_risk_classifier.pkl       # Logistic Regression — 4 risk levels
│
├── notebooks/
│   ├── vehicle_predictive_maintenance_ml.py         # ML training script
│   ├── Vehicle_Predictive_Maintenance_Model_Research.ipynb
│   ├── rag_pipeline_notebook.ipynb
│   └── llm_chain_notebook.ipynb
│
├── chroma_db/                           # ChromaDB vector store (auto-generated)
├── .env                                 # API keys and DB config (never commit)
├── .env.example                         # Template — copy to .env
└── requirements.txt
```

---

## Setup

### 1. Clone and install dependencies

```bash
git clone https://github.com/your-username/mitsucare.git
cd mitsucare
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env`:

```env
# Google Gemini API
GOOGLE_API_KEY=your_google_api_key_here

# PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=vehicle_maintenance
DB_USER=vpm_user
DB_PASSWORD=your_password_here

# Dataset path (for seeding the database)
DATASET_PATH=Vehicle_Sensor_TestSet.xlsx
```

Get a free Google API key at: https://aistudio.google.com/app/apikey

### 3. Set up PostgreSQL

```bash
# Install PostgreSQL on the VM
sudo apt update && sudo apt install postgresql -y

# Create database and user
sudo -u postgres psql << EOF
CREATE DATABASE vehicle_maintenance;
CREATE USER vpm_user WITH PASSWORD 'your_password_here';
GRANT ALL PRIVILEGES ON DATABASE vehicle_maintenance TO vpm_user;
EOF
```

### 4. Create schema and seed data

```bash
python db.py
```

This creates all tables and loads the test dataset (`Vehicle_Sensor_TestSet.xlsx`) into PostgreSQL automatically.

### 5. Build the RAG vector store

```bash
python rag_pipeline.py
```

This embeds the two SOP documents into ChromaDB and persists the vector store to `chroma_db/`. Only needs to run once — subsequent app starts load from disk.

---

## Running the Applications

### Both apps (recommended — run in separate terminals or use `nohup`)

```bash
# Terminal 1 — Technician app (tablet)
streamlit run app_technician.py --server.port 8501

# Terminal 2 — Owner app (mobile)
streamlit run app_owner.py --server.port 8502
```

### Background mode (keeps running after SSH disconnect)

```bash
nohup streamlit run app_technician.py --server.port 8501 > logs/technician.log 2>&1 &
nohup streamlit run app_owner.py      --server.port 8502 > logs/owner.log      2>&1 &
```

### Access URLs

| App | URL | Device |
|---|---|---|
| Technician | `http://VM_IP:8501` | Tablet (landscape) |
| Owner | `http://VM_IP:8502` | Phone (portrait) |
| Grafana | `http://VM_IP:3000` | Laptop |
| Prometheus | `http://VM_IP:9090` | Laptop |
| Metrics endpoint | `http://VM_IP:8000/metrics` | Prometheus scrape target |

---

## Monitoring Setup (Prometheus + Grafana)

### Install on the VM

```bash
# Prometheus
sudo apt install prometheus -y

# Grafana
sudo apt install grafana -y
sudo systemctl start grafana-server
sudo systemctl enable grafana-server
```

### Configure Prometheus scrape target

Edit `/etc/prometheus/prometheus.yml` and add:

```yaml
scrape_configs:
  - job_name: 'mitsucare'
    static_configs:
      - targets: ['localhost:8000']
    scrape_interval: 15s
```

```bash
sudo systemctl restart prometheus
```

### Grafana dashboard

1. Open `http://VM_IP:3000` (default login: `admin` / `admin`)
2. Add data source → Prometheus → URL: `http://localhost:9090`
3. Create panels using these PromQL queries:

| Panel | Query |
|---|---|
| Total Queries by Track | `sum by (track) (vpm_queries_total)` |
| LLM Response Time p95 | `histogram_quantile(0.95, rate(vpm_response_time_seconds_bucket[5m]))` |
| Fault Class Distribution | `vpm_fault_class_total` |
| Risk Class Distribution | `vpm_risk_class_total` |
| Query Rate per Minute | `rate(vpm_queries_total[1m])` |
| Active Sessions | `vpm_active_sessions` |

### Open firewall ports (Google Cloud)

In the Google Cloud Console → VPC Network → Firewall Rules, allow inbound TCP on:

| Port | Service |
|---|---|
| 8501 | Technician app |
| 8502 | Owner app |
| 8000 | Prometheus metrics endpoint |
| 9090 | Prometheus UI |
| 3000 | Grafana |

---

## ML Models

Two scikit-learn classifiers trained on 2,300 simulated Mitsubishi sensor readings:

| Model | Algorithm | Classes | CV F1 |
|---|---|---|---|
| Track 1 — Fault Classifier | SVM (RBF kernel) | 8 fault types | 0.9508 |
| Track 2 — Risk Classifier | Logistic Regression | 4 risk levels | 0.9918 |

To retrain from scratch:
```bash
python vehicle_predictive_maintenance_ml.py
```

---

## RAG Pipeline

| Stage | Implementation |
|---|---|
| Document Loading | `TextLoader` — 2 SOP `.md` files, ~80 chunks |
| Chunking | `RecursiveCharacterTextSplitter` — 500 chars / 50 overlap |
| Embedding | Google `text-embedding-004` (768 dimensions) |
| Vector Store | ChromaDB, persisted to `chroma_db/` |
| Retrieval | MMR, k=4, lambda=0.7 |

---

## Classification Reference

### Track 1 — Fault Classes

| Class | Fault | Priority |
|---|---|---|
| 0 | Normal | None |
| 1 | Battery Degradation | Medium — 14 days |
| 2 | Brake System Issue | High — 3 days |
| 3 | Cooling System Problem | High — 3 days |
| 4 | Engine Misfire | High — 3 days |
| 5 | Alternator Failure | Medium — 7 days |
| 6 | Oil Pressure Issue | **Critical — do not drive** |
| 7 | Transmission Problem | High — 3 days |

### Track 2 — Risk Classes

| Class | Level | Owner Action |
|---|---|---|
| 0 | No Risk | No notification |
| 1 | Low Risk (Risiko Rendah) | Monitor 3–5 days |
| 2 | Medium Risk (Risiko Sedang) | Schedule service within 7 days |
| 3 | High Risk (Risiko Tinggi) | Stop driving — call 1-500-989 |

---

## Key Design Decisions

**Anti-hallucination:** LLM system prompt explicitly restricts output to retrieved SOP context only. `temperature=0.1` minimises deviation. Every fault brief cites its SOP source section.

**No-alert efficiency:** Class 0 / Risk 0 results skip the LLM call entirely — no API cost, no latency for healthy vehicles.

**Task-type embeddings:** Google `text-embedding-004` uses `retrieval_document` for indexing SOP chunks and `retrieval_query` at retrieval time, improving retrieval accuracy.

**Dual-track monitoring:** Prometheus metrics are labelled by track — fault/risk class distributions, response times, and RAG chunk counts are tracked separately for Track 1 and Track 2.

---

## Target Users

**Workshop Technician** — Receives a pre-inspection fault brief before lifting the hood. Knows exactly what to check and why, based on 30 days of OBD telemetry.

**Vehicle Owner** — Receives a plain-language push alert in Bahasa Indonesia. Never sees raw sensor values or OBD codes — only what to do and how urgently.

---

*MitsuCare — Hacktiv8 LLM Bootcamp Final Project | May 2026*
