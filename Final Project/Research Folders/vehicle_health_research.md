# Predictive Vehicle Health — Research & Presentation Notes
*Compiled from research session, May 2026*

---

## 1. The Core Claim

> "Most vehicles don't break down from bad parts — they break down because no one saw it coming."

### Why It Holds

The evidence consistently points to the same pattern: vehicles don't fail out of nowhere. They fail because wear signals go unread, maintenance gets deferred, and no system is in place to catch what's coming. The problem isn't the parts — it's visibility.

---

## 2. Global Research Backing (2022–2026)

### Academic & Research

- **arXiv (2022)** — ~60% of traffic congestion delay is triggered by non-recurrent incidents. Vehicle breakdowns account for ~30% of all road incidents in NSW and 64% of incidents on a UK motorway.
- **MDPI Sustainability, April 2025** — Traditional "run-to-failure" approaches cause excessive downtime; time-based maintenance leads to premature replacement. Calls for integrated predictive approaches that identify failures *before* they disrupt operations.
- **PubMed Central, 2023** — "Early detection of anomalies facilitates prediction of potential breakdown issues which, if undetected, could lead to breakdowns and warranty claims."
- **arXiv — Air Force Ground Vehicles** — Most vehicle maintenance systems "do not have predictive maintenance infrastructure to counteract the influx of unscheduled repairs," resulting in lower readiness.

### Industry Data

- **AAA, 2024** — Over 27 million emergency roadside calls in the US in 2024. AAA urges all vehicle owners to "keep up with car care basics to prevent unexpected breakdowns."
- **ChooseCharlie, February 2026** — Americans experience 69 million breakdowns annually, costing $44 billion/year. Average US vehicle age hit a record 12.6 years in 2023.
- **LookUpAPlate, January 2026** — Congestion caused by vehicle breakdowns impacts 150 million American drivers annually, with 120 million hours lost. 566 people killed and 14,371 injured annually in collisions involving disabled vehicles — $8.8 billion financial impact.
- **Fleet Rabbit, February 2026** — Fleets average 4.2 unplanned breakdowns per truck per year, 2.3 days downtime per incident. Predictive maintenance systems surface risks 20–45 days before traditional diagnostics, reducing unplanned downtime by 30%.
- **FASTER Asset Management, March 2026** — Many fleets "still manage downtime reactively — vehicles break, shops respond, and budgets absorb the impact." The missing link is lifecycle visibility.
- **Wiley, December 2024** — Traffic congestion arises in 60% of instances from unforeseen events including vehicle breakdowns (non-recurrent congestion).

---

## 3. Indonesia-Specific Research (2022–2026)

### Government & Official Bodies

- **KNKT, January 2026** — Brake failure (*rem blong*) remains a recurring pattern in public and freight vehicle accidents. Monitoring of vehicle condition is "suboptimal."
- **KNKT / Kompas.id, December 2025** — *"Unlike train and aircraft transportation, land transportation does not yet have a mandatory maintenance program. There are no specific regulations mandating what must be done during maintenance."* — Chairman Soerjanto Tjahjono
- **Kemenhub, November 2024** — Many commercial vehicles not undergoing mandatory KIR roadworthiness inspection. KIR testing made free of charge in January 2024 to encourage uptake.
- **Polri / Pusiknas, 2023** — Of 148,798 traffic accidents in 2023, 5,320 cases (3.57%) were directly caused by vehicle malfunctions.
- **Asian Transport Observatory, 2025** — Indonesia had 566 vehicles per thousand population by 2023, with two-wheelers making up 84% of the entire fleet.

### Documented Fatal Incidents (Expired KIR at Time of Accident)

| Incident | Date | KIR Status | Outcome | Source |
|---|---|---|---|---|
| Probolinggo truck crash | April 2026 | Expired Oct 2023 — 2.5 yrs | 4 killed | Kabar Nusantara / Detik Oto |
| Padang Besi multi-vehicle crash | May 2026 | Expired March 2, 2026 | 4 killed | Kompas.com Regional |
| Kota Batu tourist bus | January 2025 | Permit expired 2020, KIR overdue Dec 2023 | 4 killed, 10 injured | IDN Times Jatim |
| Trans Putera Fajar bus, Ciater Subang | April 2024 | KIR lapsed Dec 2023 | Fatal school group accident | Kompas.com / Kemenhub |
| Tol Bawen & Bakauheni — same day | September 2023 | Suspected KIR non-compliance | Brake failure pattern | Kompas.com Otomotif |

### Breakdown-Triggered Kemacetan (Indonesian Sources Only)

| Incident | Date | Impact | Source |
|---|---|---|---|
| Truk tangki mogok, Tol Cipali | April 2022 | 15 km standstill KM 128–113 | Detik.com / detikJabar |
| Truk mogok, Tol Cikampek | June 2022 | Delayed contraflow, multiple congestion points Bekasi→Jakarta | Detik.com |
| Tiga truk mogok, Tol Jakarta-Tangerang | June 2025 | Kemacetan panjang Gelong Tomang area | Tribunnews.com |
| Truk & trailer mogok, Tol Dalam Kota | February 2024 | Congestion Tomang → Semanggi → Season City Mall | Detik.com |
| Truk trailer bermasalah, Cawang | December 2025 | Lane 1 + shoulder blocked, reported twice by Jasa Marga | Kompas.com |
| Kontainer mogok, Tol JORR & Dalam Kota | May 2026 | Multiple congestion points, confirmed Jasa Marga X account | Kompas.com |
| Bus mogok + kecelakaan, Tol Japek | April 2025 | Congestion KM 49 JORR arah Rorotan | Kompas.com |
| Kendaraan mogok, Tol Layang MBZ (Lebaran) | April 2024 | 8 km queue on elevated section | Tempo.co |

### Jasa Marga's Own Admission

PT Jasa Marga officially listed vehicle breakdowns, component failures, and mechanical disruptions as the **sixth of seven identified causes** of recurring congestion on the Jakarta-Cikampek toll road — their busiest corridor.
*(Kompas.com / Jasa Marga official statement)*

### Economic Scale

- **Kompas.com, August 2025** — Jakarta's economic losses from congestion reach **Rp 100 trillion per year** — equivalent to 6× the cost of building MRT Phase 1. Residents lose up to 174 hours annually in peak-hour traffic.
- **Geotab Indonesia, April 2026** — Predictive diagnostics are "3× cheaper than a roadside breakdown." Jakarta ranked 59.8% congestion on TomTom Index 2026.
- **World Bank Logistics Performance Index** — Indonesia dropped from 46th (2018) to 61st (2023), with Tracking & Tracing among the deteriorating components.

---

## 4. Mitsubishi Indonesia — Ecosystem Audit

### Current Apps & Capabilities (as of May 2026)

#### My Mitsubishi Motors ID (MMID) — All models
Most recent update: early 2024.
- Service history & next service reminder
- Warranty status & digital documents
- Service booking (with real-time dealer slot availability since 2024)
- 24-hour emergency bengkel siaga
- Diagnosis history (via Connect ID integration)
- OTP WhatsApp authentication
- Loyalty program (MiMate)

#### Mitsubishi Connect ID — Xforce Ultimate & select models
Connects via Bluetooth / cable (no embedded SIM).
- Real-time vehicle status
- Diagnosis history
- Fuel consumption data
- Driving score

#### Mitsubishi Connect — Destinator Ultimate only (launched 2025)
Full cloud-based telematics via embedded 4G SIM.
- Vehicle Status Report & Mileage Tracker
- SOS / eCall / bCall (roadside assistance)
- Automatic Collision Notification
- Remote lock, horn, AC, car finder
- Geofence, speed & curfew alerts

### The Gap — What None of Them Do

| Missing capability | Why it matters |
|---|---|
| Predictive alerts before a fault code triggers | They only alert *after* the ECU logs an error |
| Pattern recognition across service history | MMID stores history but doesn't analyze it |
| Cross-vehicle anomaly detection | No fleet-level or population-level learning |
| Proactive "book now before this fails" push | Service booking is user-initiated, not system-triggered |
| Coverage for older/non-Ultimate models | Xpander, L300, Triton, Pajero — zero diagnostic connectivity |

### The Critical Detail for the Pitch

The majority of Mitsubishi's Indonesian fleet — **L300, Triton, Pajero Sport, Xpander** — has zero diagnostic connectivity in any of these apps. They rely entirely on manual service records.

These are also the vehicles most likely to cause a breakdown-triggered kemacetan on the toll road.

**The gap isn't just about adding a predictive layer — it's that the majority of the fleet isn't even connected yet.**

---

## 5. Hooks & Punchlines Considered

### Strongest Options

- *"Rem blong bukan nasib. Itu adalah hasil dari kendaraan yang tidak pernah diperiksa."*
- *"The brakes didn't fail on the road. They failed months ago — when no one was looking."*
- *"Indonesia has 147 million vehicles on the road. Not one of them is legally required to be maintained."*
- *"Planes get checked before every flight. Trucks carry schoolchildren with certifications expired since 2020."*
- *"The data exists. The warning was there. No one was reading it."*
- *"See it before the road does."* *(campaign / product one-liner)*
- *"Most breakdowns are scheduled. They just don't know it yet."*

### Why the Hook Felt Flat on Slide 01

The headline was a **conclusion**, not an opening — telling the audience the answer before they'd felt the problem. A proper problem statement opens with undeniable facts and lets the audience arrive at the conclusion themselves.

---

## 6. Problem Statement Structure (Corrected)

A proper problem statement follows this causal chain:

1. **Context** — What is the current state of the world? *(factual, neutral)*
2. **Observation** — What pattern do we see?
3. **Consequence** — What does that pattern cost?
4. **Gap** — Why hasn't it been solved?
5. **Tension** — One sentence that earns the solution slide

| Current approach | Proper approach |
|---|---|
| Opens with a rhetorical claim | Opens with undeniable facts |
| Audience must trust the claim | Audience arrives at the conclusion themselves |
| Hook → stats (disconnected) | Context → evidence → gap (causal chain) |
| Sounds like a pitch | Sounds like a finding |

---

## 7. Slide Content (Final)

### Slide 01 — The System Gap
**Title:** Indonesia's Vehicles Are Connected. The Warning System Isn't.

**Lead:** Mitsubishi already collects vehicle data through MMID and Mitsubishi Connect ID. But the system only responds after a fault code appears — not before.

**Left column — The Reality:**
- 147 million registered vehicles in Indonesia (2022)
- Average vehicle age: 12.6 years — highest on record
- 84% of the fleet are motorcycles; commercial trucks carry the rest
- No mandatory maintenance program exists for land vehicles in Indonesia
- KIR compliance is declining — many commercial vehicles operate with expired certification for years

**Right column — What Mitsubishi Has Today:**

| App | What it does | What it misses |
|---|---|---|
| MMID | Service history, next service reminder | Doesn't analyze patterns |
| Connect ID | Diagnosis history, fuel data | Only reads, doesn't predict |
| Mitsubishi Connect | Vehicle status, malfunction alerts | Alerts after fault — not before |

**Bottom tension line:**
*The data pipeline exists. The predictive layer doesn't.*

---

### Slide 02 — The Cost of Not Seeing
**Title:** Every Failure Had a Prequel. No System Was Reading It.

**Lead:** These are not random accidents. Each one involved a vehicle whose condition was knowable — weeks before it failed.

**Case 1 — Probolinggo, April 2026**
Truck KIR expired October 2023. Drove for 2.5 years without a single inspection. Brake failure at a railway crossing. 4 killed.

**Case 2 — Kota Batu, January 2025**
Tourist bus. Permit expired 2020. KIR overdue since December 2023. Carrying vocational school students. 4 killed, 10 injured.

**Case 3 — Tol Cipali, April 2022**
One tanker truck breaks down. Traffic standstill from KM 128 to KM 113 — 15 kilometres. Hundreds of vehicles. Hours of delay.

**Case 4 — Tol Dalam Kota, February 2024**
Two truck breakdowns on one evening. Congestion from Tomang flyover back to Semanggi. Confirmed by Jasa Marga via official X account.

**The pattern:**
None of these were sudden. Brake wear is gradual. KIR expiry is scheduled. Battery degradation is measurable. Cooling system failure shows temperature signals days before collapse.

**Closing gap statement:**
*The breakdown was the last event in a long story. The story was readable. Nobody was reading it.*

---

### Slide 03 — System Architecture
**Title:** How the System Works

**Lead:** One data pipeline. Two parallel outputs. Each designed for the person who needs to act.

**Pipeline:** Vehicle Sensors & OBD → IoT Layer (1–2 hr intervals, 7AM–7PM) → Central Database (30-day rolling telemetry)

**Track 1 — Workshop / Mechanic**
- ML Anomaly Detection on 30-day telemetry
- LLM + RAG queries fault libraries, service history, Bahasa Indonesia technical docs
- Output: Technician Fault Brief — component, likely cause, recommended action, severity

**Track 2 — Vehicle Owner**
- Risk score crosses threshold in Owner Alert Module
- LLM Summarizer converts technical signal to plain language
- Output: Push notification — what's at risk, how urgent, what to do — in Bahasa Indonesia

**Note:** Both tracks include a "Normal → No action" branch. The system is selective — silence is also a feature.

---

## 8. Document Review Notes (problem_framing_automotive_safety_v1.md)

### What Was Working
- Two-track system (mechanic brief + owner alert) is the strongest differentiator
- Indonesia specificity is structural, not cosmetic — KIR gap, Bahasa Indonesia output, informal records
- "The gap costs lives, strands drivers, and turns manageable maintenance into emergency repairs" is pitch-ready

### What Needed Fixing

1. **Hook vs. product misalignment** — The punchline was about invisibility; the product is about connecting data that's already being captured. More precise hook: *"The data is already there. The car already knows. It just hasn't told anyone yet."*

2. **RAG oversimplification** — "Zero hallucination on safety-critical outputs" is not accurate. RAG reduces hallucination, it doesn't eliminate it. Replace with: *"grounded outputs — every fault interpretation is cited against retrieved documentation, not generated from model weights alone."*

3. **Soft citations** — "McKinsey via Infraspeak" and "Deloitte Automotive, 2022" link to homepages, not actual reports. Either link directly to the report or cite as "as cited in [source]."

4. **Fleet Manager persona floats** — Appears in business relevance but has no presence in system architecture or flow. Either build it as a third track (risk-ranked dashboard) or fold into Track 2 as a multi-vehicle view.

5. **Architecture ambiguity** — Track 2 (Owner Alert) — does it use its own ML anomaly detection or inherit flags from Track 1? The diagram skips the ML step for Track 2. Needs clarification before a pitch.

6. **Three competing framings** — The document sits between a safety product, an AI/ML showcase, and a business pitch. Pick one primary purpose and reorder sections around it.

### Recommended Addition — Before/After Table

| | Before this system | After this system |
|---|---|---|
| Vehicle owner | Warning light = fault already happened | Push alert 3–7 days before failure, in plain Bahasa |
| Mechanic | 20+ min diagnosis from scratch | Pre-inspection brief waiting before vehicle arrives |
| Fleet operator | Reactive breakdown, route disruption | Risk-ranked fleet view, proactive scheduling |

---

*End of research notes.*
