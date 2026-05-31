# Vehicle Predictive Maintenance System — Project Summary

---

## 1. Vehicle Sensors & Their Functions

A reference table of 25 car sensors was identified, covering engine management, safety, and driver-assist systems.

| Sensor | Function |
|---|---|
| Oxygen (O2) Sensor | Monitors exhaust gases to optimise the air-fuel ratio |
| Mass Air Flow (MAF) Sensor | Measures air entering the engine for fuel delivery |
| Throttle Position Sensor | Detects throttle valve position for acceleration and fuel injection |
| Crankshaft Position Sensor | Determines crankshaft position for ignition timing |
| Camshaft Position Sensor | Syncs with crankshaft for valve timing and fuel injection |
| Knock Sensor | Detects engine knocking and adjusts ignition |
| ABS Wheel Speed Sensor | Monitors wheel speed for ABS and traction control |
| Coolant Temperature Sensor | Measures coolant temperature to prevent overheating |
| Oil Pressure Sensor | Monitors engine oil pressure for proper lubrication |
| Parking (Proximity) Sensor | Assists parking by detecting nearby objects |
| Rain Sensor | Detects rain to activate wipers automatically |
| Tyre Pressure Monitoring Sensor (TPMS) | Measures tyre pressure and alerts if below recommended levels |
| Vehicle Speed Sensor (VSS) | Measures vehicle speed for cruise control and speedometer |
| Ambient Light Sensor | Adjusts dashboard and headlight brightness |
| Fuel Temperature Sensor | Detects fuel temperature to prevent vapour lock |
| Airbag Crash Sensor | Detects sudden deceleration to deploy airbags |
| Manifold Absolute Pressure (MAP) Sensor | Measures intake manifold pressure for fuel delivery |
| Exhaust Gas Recirculation (EGR) Sensor | Manages exhaust recirculation to reduce NOx emissions |
| Battery Voltage Sensor | Monitors battery voltage to prevent overcharging |
| Humidity Sensor | Detects cabin humidity for climate control |
| Blind Spot Detection Sensor | Identifies vehicles in blind spots |
| Lane Departure Warning Sensor | Tracks lane markings to warn of unintentional drifting |
| Pedestrian Detection Sensor | Detects nearby pedestrians to help avoid collisions |
| Forward Collision Sensor | Monitors distance from vehicles ahead |
| Ultrasonic Sensor | Detects nearby objects using ultrasonic waves |

---

## 2. Sensors Used During Maintenance

The following sensors are most relevant during routine vehicle maintenance:

- **O2 Sensor** — Checked during emissions testing and air-fuel tuning
- **MAF Sensor** — Inspected when diagnosing fuel delivery issues
- **Throttle Position Sensor** — Checked for acceleration or injection faults
- **Crankshaft Position Sensor** — Critical for ignition timing diagnosis
- **Camshaft Position Sensor** — Inspected for valve timing and injection faults
- **Knock Sensor** — Checked to prevent engine damage from knocking
- **Coolant Temperature Sensor** — Monitored to prevent overheating; commonly replaced
- **Oil Pressure Sensor** — Checked during oil changes and engine inspections
- **Battery Voltage Sensor** — Tested during electrical system checks
- **MAP Sensor** — Diagnosed when fuel delivery issues arise
- **EGR Sensor** — Checked during emissions-related maintenance
- **TPMS** — Checked during tyre rotation or replacement

> Sensors like Rain, Ambient Light, Blind Spot, Lane Departure, and Pedestrian Detection are driver-assist/comfort features and are only serviced if they malfunction.

---

## 3. Mitsubishi & These Sensors

Modern Mitsubishi vehicles (Outlander, Eclipse Cross, Xpander — 2020 onwards) carry most of the sensors listed:

### Standard Across All Mitsubishi Models
- O2, MAF, Throttle Position, Crankshaft & Camshaft Position, Knock Sensor
- Coolant Temperature, Oil Pressure, Battery Voltage
- TPMS

### Turbocharged Models (e.g. Eclipse Cross 1.5T)
- MAP Sensor, EGR Sensor

### Mid to High Trims
- Forward Collision Mitigation (radar-based)
- Lane Departure Warning
- Blind Spot Warning, Rear Cross Traffic Alert
- 360-degree camera system (Outlander)
- Parking / Ultrasonic Sensors
- Rain Sensor, Ambient Light Sensor
- Pedestrian Detection
- Humidity Sensor (with auto climate control)

---

## 4. System Architecture — Flow Diagram

The system collects data from **Vehicle Sensors & OBD** and transmits it via an **IoT Layer** (1–2 hour intervals, 7 AM – 7 PM) to a **Central Database**, which feeds two parallel tracks:

```
Vehicle Sensors & OBD
        │
        ▼
  IoT Layer (1–2 hr intervals, 7 AM–7 PM)
        │
        ▼
  Central Database
       / \
      /   \
     ▼     ▼
Track 2   Track 1
(Owner)  (Technician)
```

### Track 1 — Workshop / Mechanic
- **ML Anomaly Detection** on 30-day telemetry
- If **Normal** → No action
- If **Anomaly** → **LLM + RAG** (Fault libraries, Service history, Bahasa Indonesia docs) → **Technician Fault Brief**

### Track 2 — Vehicle Owner
- **Owner Alert Module** checks risk level
- If **No Risk** → No notification
- If **Risk** → **LLM Summarizer in Bahasa Indonesia** → **Push Alert** (plain language, urgency + action)

---

## 5. Classification Schemas

### Track 1 — Maintenance Classification (Technician)

| Class ID | Fault Type |
|---|---|
| 0 | Normal |
| 1 | Battery Degradation |
| 2 | Brake System Issue |
| 3 | Cooling System Problem |
| 4 | Engine Misfire |
| 5 | Alternator Failure |
| 6 | Oil Pressure Issue |
| 7 | Transmission Problem |

### Track 2 — Risk Detection (Owner)

| Class | Meaning | Notification |
|---|---|---|
| 0 | No Risk | No notification |
| 1 | Low Risk | Monitor condition |
| 2 | Medium Risk | Schedule maintenance |
| 3 | High Risk | Immediate inspection required |

---

## 6. Risk Level Rationale

### 🟢 Class 0 — No Risk
All sensors within normal operating range:
- Battery ~14.2V, Coolant ~90°C, Oil Pressure ~40 PSI, TPMS ~32 PSI
- No action needed.

### 🟡 Class 1 — Low Risk
Minor deviations worth monitoring:
- Battery drops to ~13.6V (possible early alternator wear)
- TPMS drops to ~29.5 PSI (slightly underinflated)
- Car still runs fine but warrants observation.

### 🟠 Class 2 — Medium Risk (Schedule Maintenance)
Multiple notable deviations in combination:
- Coolant ~98°C, Oil Pressure ~30 PSI, Battery ~12.8V, TPMS ~27 PSI
- No single reading is catastrophic, but together they signal a workshop visit is needed soon.

### 🔴 Class 3 — High Risk (Immediate Inspection Required)
Multiple sensors in danger territory:
- Coolant ~112°C (overheating), Oil Pressure ~18 PSI (near seizure), Battery ~11.2V (near failure)
- O2 ~0.68V (rich mixture), TPMS ~24 PSI (blowout risk)
- Continuing to drive risks serious mechanical damage or a safety incident.

> **Key logic:** The more sensors that deviate AND the further they deviate from normal, the higher the risk class.

---

## 7. Generated Datasets

Two balanced datasets were generated simulating real sensor readings for both tracks.

### Track 1 — Technician Dataset
| Property | Value |
|---|---|
| Total Rows | **1,200** |
| Classes | 8 fault types |
| Rows per Class | 150 (perfectly balanced) |
| Detection Window | 30-day telemetry |
| Sensors Used | O2, MAF, Throttle, Crank RPM, Cam Advance, Knock Count, Coolant Temp, Oil Pressure, MAP, EGR Duty, Battery Voltage, Fuel Temp |

### Track 2 — Owner Dataset
| Property | Value |
|---|---|
| Total Rows | **1,100** |
| Classes | 4 risk levels |
| Rows per Class | 275 (perfectly balanced) |
| Detection Window | 12-hour daily window (7 AM – 7 PM) |
| Sensors Used | O2, MAF, Throttle, Coolant Temp, Oil Pressure, Battery Voltage, TPMS, Ambient Temp, Cabin Humidity, Fuel Level, Brake Pedal Events, Speed |

---

## 8. Sensor Health Thresholds

### Track 1 Sensors (Technician)

| Sensor | ✅ Good | ⚠️ Going Bad | 🔴 Really Bad |
|---|---|---|---|
| O2 Voltage | 0.1 – 0.5V | 0.5 – 0.6V | >0.65V |
| MAF (g/s) | 5.0 – 7.0 | 4.0–5.0 or 7.5–9.0 | <3.5 or >10.0 |
| Throttle Position | 10% – 20% | <5% or 20–30% | >30% stuck |
| Crankshaft RPM | 700 – 900 | 900 – 1,100 | >1,100 or <600 |
| Cam Advance | 9° – 12° | 7°–9° or 12°–15° | <6° or >18° |
| Knock Count (30d) | 0 – 1 | 2 – 4 | >5 |
| Coolant Temp | 85°C – 95°C | 95°C – 105°C | >105°C |
| Oil Pressure | 35 – 50 PSI | 25 – 34 PSI | <20 PSI |
| MAP (kPa) | 30 – 40 | 40 – 45 | >48 or <20 |
| EGR Duty | 15% – 25% | 25% – 35% | >40% or <5% |
| Battery Voltage | 13.8 – 14.5V | 12.5 – 13.7V | <12.0V |
| Fuel Temp | 25°C – 45°C | 45°C – 55°C | >58°C |

### Track 2 Sensors (Owner)

| Sensor | ✅ Good | ⚠️ Going Bad | 🔴 Really Bad |
|---|---|---|---|
| TPMS | 30 – 34 PSI | 27 – 29 PSI | <25 PSI |
| Ambient Temp | 20°C – 35°C | 35°C – 38°C | >40°C |
| Cabin Humidity | 40% – 65% | 65% – 75% | >80% |
| Fuel Level | 25% – 100% | 10% – 24% | <10% |
| Brake Pedal Events | 5 – 20 | 20 – 35 | >40 |
| Avg Speed | 20 – 60 km/h | 60 – 90 km/h | >100 km/h |

---

## 9. Mitsubishi & Predictive Maintenance — Current State

### What Mitsubishi Currently Has
- **My MITSUBISHI CONNECT App** — real-time maintenance alerts, malfunction notifications, service scheduling, vehicle health reports (2025 Outlander onwards), fuel level, mileage tracking.
- **Basic telematics** via the Eclipse Cross and Outlander platforms.

### What Mitsubishi Does NOT Have (Yet)
- True **AI-driven predictive maintenance** — no proactive sensor trend analysis to predict failures before warning lights appear.
- Competitors like **Tesla** (real-time AI battery/motor monitoring) and **GM OnStar** (monthly diagnostic reports + predictive alerts) are ahead in this area.

### Gap This Project Fills
This system builds the **predictive maintenance layer that Mitsubishi consumer cars currently lack**, using:
- IoT sensor collection via OBD
- ML anomaly detection on 30-day telemetry
- LLM + RAG for technician fault briefs
- LLM summarization in **Bahasa Indonesia** for owner push alerts

> This makes the project more advanced than what Mitsubishi currently offers natively to its owners.

---

*Document generated from project discussion — May 2026*
