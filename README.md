# 🚀 The Lenny Growth Assistant
> **Enterprise-Grade RAG Assistant, Ship 30 for 30 Content Engine, and Claude-Style Artifact Viewer**  
> *Forward Deployed Engineer Take-Home Assessment*

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16%20%2B%20pgvector-336791?style=flat&logo=postgresql)](https://github.com/pgvector/pgvector)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-000000?style=flat)](https://ollama.com)
[![React](https://img.shields.io/badge/React-18%20%2B%20Vite%20%2B%20Tailwind-61DAFB?style=flat&logo=react)](https://react.dev)
[![Docker](https://img.shields.io/badge/Docker%20Compose-Ready-2496ED?style=flat&logo=docker)](https://www.docker.com)

---

## 📖 Table of Contents
1. [Overview & Highlights](#-overview--highlights)
2. [Forward Deployment Deliverables](#-forward-deployment-deliverables)
3. [System Architecture](#-system-architecture)
4. [Prerequisites](#-prerequisites)
5. [Quickstart (One-Command Docker Setup)](#-quickstart-one-command-docker-setup)
6. [Local Development (Without Docker)](#-local-development-without-docker)
7. [Knowledge Base & Transcript Ingestion](#-knowledge-base--transcript-ingestion)
8. [Dynamic LLM Routing (Ollama Local & Cloud)](#-dynamic-llm-routing-ollama-local--cloud)
9. [Ship 30 for 30 Skill & Claude Artifact Viewer](#-ship-30-for-30-skill--claude-artifact-viewer)
10. [Automated Tests](#-automated-tests)
11. [Troubleshooting & Resilience](#-troubleshooting--resilience)

---

## 🌟 Overview & Highlights

The **Lenny Growth Assistant** transforms 200+ hours of *Lenny’s Podcast* transcripts into an internal intelligence partner for Product Managers and Growth Leaders.

- **Strict Source Grounding:** Every insight cites episode titles, guest names, and timestamps (e.g., `[Episode: Brian Chesky's new playbook, 00:00:00]`). Out-of-domain queries strictly trigger an honest refusal rather than hallucinating.
- **Ship 30 for 30 Content Engine:** Transforms grounded answers into atomic, ~1,250-word essays formatted with curiosity hooks, short paragraphs (1–3 sentences), bold anchor words, and tactical checklists.
- **Claude-Style In-App Artifact Viewer:** Dual-pane split-screen previewing generated Markdown playbooks and sandboxed HTML/CSS calculators and prototypes.
- **Zero-Trust Sandboxed Iframe:** HTML artifacts are sanitized with `DOMPurify` and isolated inside an iframe using `sandbox="allow-scripts"` (strictly omitting `allow-same-origin` to block parent cookie/DOM access).
- **Dual-Model Routing Layer:** Seamless zero-code toggle between local Ollama (`llama3.2:3b`, `llama3.1:8b`) and frontier cloud models (Anthropic Claude 3.5 Sonnet, OpenAI GPT-4o) with intelligent fallback.

---

## 📁 Forward Deployment Deliverables

| Deliverable | Location | Description |
| :--- | :--- | :--- |
| **Product Requirements (PRD)** | [`docs/PRD.md`](docs/PRD.md) | Persona discovery, success metrics ($\ge 90\%$ citations), scope decisions, risks, and acceptance criteria. |
| **Architecture Specification** | [`docs/architecture.md`](docs/architecture.md) | Data models, pgvector HNSW indexing, component boundaries, SSE event streams, and security boundaries. |
| **UI/UX Design Specification** | [`docs/design.md`](docs/design.md) | Fluid split-pane design, state transitions, skimmability typography, and WCAG accessibility standards. |
| **Agent Transcripts** | [`agent_transcripts/`](agent_transcripts/) | Forward deployment logs covering scaffolding, pgvector debugging, skill tuning, and resilience tests. |
| **Automated Tests** | [`backend/tests/`](backend/tests/) | Full test suite covering retrieval accuracy, model switching, API contracts, and skill outputs. |
| **Demo Video Script** | [`demo/DEMO_SCRIPT.md`](demo/DEMO_SCRIPT.md) | Turnkey 2–3 minute video recording script with camera setup, speaking points, and trade-off analysis. |

---

## 🏛 System Architecture

```
+-----------------------------------------------------------------------------------------+
|                                    REACT FRONTEND (Vite + TS)                           |
|   - Split-Pane Chat Interface + Claude-Style Artifact Viewer (DOMPurify + Sandboxed)     |
+-----------------------------------------------------------------------------------------+
                                           |  SSE / JSON
                                           v
+-----------------------------------------------------------------------------------------+
|                                  FASTAPI ASGI BACKEND                                   |
|   - /api/sessions: Session & message history persistence                                |
|   - /api/chat: Grounded streaming QA, Ship 30 for 30 skill, Artifact parser            |
|   - /api/health: Live diagnostic probe (DB, pgvector, Ollama, Cloud)                    |
+------------------------------------+----------------------------------------------------+
                                     |
           +-------------------------+-------------------------+
           |                                                   |
           v                                                   v
+----------------------+  +----------------------+  +-------------------------------------+
|   LOCAL LLM ENGINE   |  |   CLOUD LLM ENGINE   |  |          PERSISTENCE LAYER          |
|  - Ollama via HTTP   |  |  - Anthropic Claude  |  |  - PostgreSQL 16 + pgvector         |
|  - llama3.2 / 3.1    |  |  - OpenAI GPT-4o     |  |  - HNSW Cosine Distance Index       |
+----------------------+  +----------------------+  +-------------------------------------+
```

---

## 🛠 Prerequisites

- **Runtimes:** Python `3.11+`, Node.js `v18+` (or `v20+` LTS), Docker & Docker Compose `v24+`.
- **Local Model (Mandatory for Demo):** [Ollama](https://ollama.com) installed with `llama3.2:3b` or `llama3.1:8b`:
  ```bash
  ollama pull llama3.2:3b
  ollama run llama3.2:3b
  ```

---

## ⚡ Quickstart (One-Command Docker Setup)

The quickest way to evaluate the complete stack is with Docker Compose:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-org/lenny-growth-assistant.git
   cd lenny-growth-assistant
   ```

2. **Copy environment variables:**
   ```bash
   cp .env.example .env
   ```

3. **Start all services:**
   ```bash
   docker-compose up --build
   ```

4. **Access the application:**
   - **Frontend UI:** Open [http://localhost:3000](http://localhost:3000)
   - **Backend API Docs:** Open [http://localhost:8000/docs](http://localhost:8000/docs)
   - **Health Probe:** Open [http://localhost:8000/api/health](http://localhost:8000/api/health)

---

## 💻 Local Development (Without Docker)

You can run the frontend and backend directly on your host machine:

### 1. Backend Setup
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt

# Run transcript ingestion into local storage:
python scripts/ingest.py

# Start the FastAPI dev server:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 📚 Knowledge Base & Transcript Ingestion

The repository includes a curated collection of full-length transcripts from iconic Lenny's Podcast episodes:
- **Brian Chesky:** Founder Mode, eliminating product management silos, and running Airbnb.
- **Shreyas Doshi:** High-leverage PM frameworks, LNO framework, and avoiding failure modes.
- **Elena Verna:** B2B Product-Led Growth, freemium loops, and monetization funnels.
- **Sean Ellis:** The North Star metric, growth experiments, and viral flywheels.
- **Rahul Vohra:** The Superhuman Product-Market Fit engine and the 40% rule.

### Ingesting & Refreshing Transcripts
To ingest new transcripts or re-index the archive:
```bash
python backend/scripts/ingest.py
```
To download the complete 260+ episode archive from GitHub:
```bash
python backend/scripts/download_transcripts.py
```

---

## 🔀 Dynamic LLM Routing (Ollama Local & Cloud)

Switch between models directly from the top navigation bar without touching any code:

1. **Local Ollama (Default for Evaluation):**
   - Routes to `http://localhost:11434` (or `http://host.docker.internal:11434`).
   - Zero API cost, private, and fast.
2. **Anthropic Claude 3.5 Sonnet:**
   - Supply `ANTHROPIC_API_KEY` in `.env`.
   - Generates nuanced long-form strategic essays and complex HTML artifacts.
3. **OpenAI GPT-4o:**
   - Supply `OPENAI_API_KEY` in `.env`.
4. **Resilient Mock Mode:**
   - If Ollama is offline and no cloud keys are provided, the system seamlessly transitions into a context-grounded evaluation mode so evaluators can inspect UI flows and streaming without interruptions.

---

## ✍️ Ship 30 for 30 Skill & Claude Artifact Viewer

### Ship 30 for 30 Content Engine
Click **"⚡ Transform to Ship 30 for 30"** on any response to generate:
- **Hook:** 2–3 tension-filled opening sentences establishing a curiosity gap.
- **Form:** Skimmable 1–3 sentence paragraphs with section dividers.
- **Emphasis:** **Bold anchor words** at the head of every bullet.
- **Attribution:** Direct guest attribution from podcast context.
- **Takeaway:** Step-by-step operational checklist.

### Claude-Style Sandboxed Artifact Viewer
When the assistant generates a standalone artifact, it formats it as:
```xml
<artifact identifier="pmf-calculator" type="html" title="Interactive PMF Engine Calculator">
<!DOCTYPE html>
<html>...</html>
</artifact>
```
The frontend automatically slides open the right-hand panel:
- **Preview Tab:** Renders rich Markdown or live HTML/CSS.
- **Code Tab:** View and inspect clean syntax.
- **Security:** Strict iframe isolation (`sandbox="allow-scripts"` without `allow-same-origin`) + `DOMPurify` protection.
- **Actions:** One-click copy and file download.

---

## 🧪 Automated Tests

Run the full automated test suite covering retrieval accuracy, out-of-domain refusal, model switching, and persistence:

```bash
cd backend
pytest tests/ -v
```

### Manual UI Test Plan
1. **Grounded Query:** Ask *"What is Brian Chesky's advice on founder mode?"* Verify timestamp citations and sources drawer.
2. **Out-of-Domain Refusal:** Ask *"How do I bake a sourdough loaf?"* Verify strict refusal response.
3. **Ship 30 Transform:** Click the Ship 30 button and verify essay structure in the Artifact Viewer.
4. **HTML Artifact:** Request an interactive HTML retention calculator and test widget buttons inside the sandboxed preview.
5. **Model Toggle:** Switch provider in the dropdown and confirm proper provider badge in subsequent message items.

---

## 🛡 Troubleshooting & Resilience

| Issue | Root Cause | Solution |
| :--- | :--- | :--- |
| **Ollama connection refused** | Ollama daemon not running on port `11434`. | Run `ollama serve` or click the provider selector to switch to Cloud / Mock mode. |
| **Model not found in Ollama** | Target model has not been downloaded. | Run `ollama pull llama3.2:3b` in your terminal. |
| **PostgreSQL connection error** | Docker container starting or port `5432` busy. | The backend automatically activates its resilient local vector engine while waiting for DB readiness. |
| **Docker host gateway on Linux** | `host.docker.internal` not mapped by default. | Run with `--add-host host.docker.internal:host-gateway` or specify `OLLAMA_BASE_URL=http://172.17.0.1:11434`. |

---

## 📄 License & Evaluation Notice
*Developed for the Forward Deployed Engineer Take-Home Assessment. Transcripts sourced from public archives of Lenny's Podcast.*
