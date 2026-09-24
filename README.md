# 🔍 Autonomous Research & LinkedIn Intelligence Agent (`research-01`)

[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI: 0.115+](https://img.shields.io/badge/FastAPI-Framework-009688.svg)](https://fastapi.tiangolo.com/)
[![Engine: Hermes Agent](https://img.shields.io/badge/Engine-Hermes_Agent-purple.svg)](https://hermes-agent.nousresearch.com/)
[![Network: LAN Multi--Agent](https://img.shields.io/badge/Network-LAN_Orchestrated-orange.svg)](#)

An autonomous, production-grade **Research Agent** designed for distributed multi-agent systems and talent/market intelligence. Equipped with the **Hermes Agent** action loop, live web search, DOM extraction, and compliance auditing capabilities (ISO/IEC 27001 & ISO/IEC 42001).

Built for **LAB 3: Multi-Agent LAN Architecture (Agent → API → Orchestrator → API → Agent)**.

---

## 🏛️ Architecture & Network Topology

In a distributed multi-agent network, no agent works in isolation or calls peers directly without governance. All discovery, health monitoring, and task routing are handled through the central **Orchestrator**:

```
                       ┌─────────────────────────┐
                       │   CENTRAL ORCHESTRATOR  │
                       │                         │
                       │ • Agent Registry        │
                       │ • Capability Discovery  │
                       │ • Task Router & Queue   │
                       │ • Event Log & Dashboard │
                       └────────────┬────────────┘
                                    │
                         Local Area Network (LAN)
                                    │
         ┌──────────────────────────┴──────────────────────────┐
         │                                                     │
         ▼                                                     ▼
┌─────────────────────────┐                           ┌─────────────────────────┐
│      BUILDER / CTO      │                           │      RESEARCH AGENT     │
│       (Machine 1)       │                           │   (Machine 2 - THIS)    │
│                         │                           │                         │
│ • Architecture Planning │                           │ • Agent ID: research-01 │
│ • Application Dev       │                           │ • Hermes Reasoning Core │
│ • Frontend / Backend    │                           │ • Live Web Search (DDG) │
│ • Code Review           │                           │ • BeautifulSoup Scraper │
└─────────────────────────┘                           └─────────────────────────┘
```

### Delegation Lifecycle
```text
Builder Agent ──> "I need research on ISO 27001 & 42001"
      ↓
Orchestrator   ──> Capability Match ("research" -> research-01)
      ↓
Research Agent ──> Receives POST /tasks, runs Hermes Reasoning + Search
      ↓
Result Output  ──> Returns structured synthesis to Orchestrator
      ↓
Builder Agent  ──> Consumes research data & constructs the deliverable
```

---

## ⚡ Core Capabilities (`research-01`)

The agent exposes the following capabilities during **Capability Discovery**:

* `web_search`: Live Internet queries with real-time snippet extraction.
* `browser`: Clean text extraction and DOM content stripping (strips ads, scripts, navigation).
* `research`: Deep multi-step reasoning, fact extraction, and synthesis via the **Hermes Agent** engine.
* `documentation`: Production of structured documentation, comparative matrices, and audit summaries.
* `summarization`: Condensation of extensive reports and profiles into concise actionable bullet points.

---

## 🛠️ API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Availability health-check (`{"status": "online"}`) |
| `GET` | `/capabilities` | Self-describes capabilities for the Orchestrator |
| `POST` | `/tasks` | **Core delegation endpoint**: executes research with Hermes + web tools |
| `GET` | `/tasks/{task_id}` | Task status and result retrieval |
| `POST` | `/tools/search` | Direct search (`{"query": "...", "max_results": 5}`) |
| `POST` | `/tools/fetch` | Direct webpage text extraction (`{"url": "...", "max_chars": 3000}`) |
| `POST` | `/register` | Triggers self-registration to any remote Orchestrator |
| `GET` | `/events` | Real-time audit log of all network events and task durations |
| `GET` | `/docs` | Interactive OpenAPI Swagger UI |

---

## 🌐 Included Artifact: ISO 27001 & ISO 42001 Portfolio

Included in this repository is `portfolio_iso.html`, a production-grade responsive web portfolio generated autonomously following architectural specifications provided by the network CTO (`awema-cto`):

* **ISO/IEC 27001:2022 (ISMS):** Breakdown of the 93 controls across Organizational, People, Physical, and Technological themes.
* **ISO/IEC 42001:2023 (AIMS):** Full analysis of the world's first AI Management System standard (bias prevention, data provenance, explicability, human oversight).
* **Harmonized Structure (HS) Convergence:** Interactive SVG diagram showing how ISO 27001 and ISO 42001 integrate through shared Clauses 4–10.
* **West African Market Intelligence:** LinkedIn analysis of certified auditors and compliance demand across the WAEMU/BCEAO region.

---

## 🚀 Quick Start

### 1. Clone & Setup
```bash
git clone https://github.com/Jaheim007/linkedin-research-agent.git
cd linkedin-research-agent

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Launch the Research Agent
```bash
# Starts the agent on port 9001
python research_agent.py
```
*(On Windows, you can simply double-click `start_agent.bat`).*

### 3. Run Self-Tests
Verify all endpoints and security policies:
```bash
python test_agent.py
```

### 4. Connect to an Orchestrator
```bash
# Register to Machine 1 Orchestrator
python register.py http://<ORCHESTRATOR_IP>:8000
```

---

## 🔒 Security & Authentication

* Supports header authentication via `X-API-Key: LAB-RESEARCH-SECRET` or `Authorization: Bearer LAB-RESEARCH-SECRET`.
* Rejects unauthorized requests with `401 Unauthorized`.
* Includes autonomous background heartbeat thread (`POST /heartbeat`) every 20 seconds to keep registration active.

---

## 👤 Author & Credits

* **Developer:** Jaheim Kouaho ([@Jaheim007](https://github.com/Jaheim007))
* **Agent Engine:** Hermes Agent by [Nous Research](https://github.com/NousResearch/hermes-agent)
* **Organization:** HACKTUALIZ Inc. & HACKTUALIZ SAS (Abidjan, Côte d'Ivoire)
* **License:** [MIT](LICENSE)
