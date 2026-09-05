# Product Requirements Document (PRD)
## Project: The Lenny Growth Assistant
**Status:** Approved & Forward Deployed  
**Target Persona:** Growth Product Managers, Founders, and Product Leaders  
**Author:** Forward Deployed Engineering Team  

---

## 1. Executive Summary & Problem Framing

### 1.1 The Primary User & Job-To-Be-Done (JTBD)
* **Primary Persona:** Growth PMs, Heads of Product, and Early-Stage Founders.
* **Core Job:** When facing mission-critical growth challenges (e.g. choosing a North Star metric, designing viral loops, diagnosing churn, or shifting to product-led sales), these leaders need proven, battle-tested playbooks from the world's best operators.
* **The Pain Point:** *Lenny’s Podcast* contains 200+ hours of tactical, high-leverage product knowledge. However, finding specific answers is painful:
  - Audio and video search is slow and imprecise.
  - Generic LLMs (e.g., vanilla ChatGPT) hallucinate generic PM platitudes without verbatim quotes, concrete formulas, or guest attribution.
  - Leaders lack the time to listen to 90-minute episodes or distill scattered advice into executive summaries and operational artifacts.

### 1.2 Value Proposition
*The Lenny Growth Assistant* is an enterprise-grade, retrieval-augmented intelligence system that:
1. **Answers with Grounded Authority:** Directly retrieves relevant passages from podcast transcripts, enforcing strict attribution (`[Episode: Guest Name, Topic/Timestamp]`) and declaring when knowledge is missing.
2. **Transforms into High-Retention Written Assets:** Encodes the *Ship 30 for 30* writing methodology to convert grounded knowledge into skimmable, ~1,250-word essays with bold hooks, short paragraphs, and execution checklists.
3. **Renders Live Interactive Artifacts:** Delivers a Claude-style split-pane Artifact Viewer that securely renders Markdown playbooks and sandboxed HTML/CSS calculators and prototypes without navigating away from the conversation.

---

## 2. Measurable Success Metrics

| Metric | Target | Operational Rationale |
| :--- | :--- | :--- |
| **Retrieval Citation Accuracy** | $\ge 90\%$ | Retrieved chunks must directly back up every factual assertion made by the model. |
| **Local TTFT (Time To First Token)** | $< 4.0\text{ seconds}$ | Local Ollama (`llama3.2:3b` / `llama3.1:8b`) response stream must engage users without perceptible lag. |
| **Out-of-Domain Refusal Rate** | $100\%$ | When queried about ungrounded topics (e.g., cooking recipes, general trivia), the assistant strictly refuses to hallucinate. |
| **Artifact Render Safety** | $0\text{ XSS vulnerabilities}$ | No malicious or accidental scripts may access parent document cookies, localStorage, or session tokens. |
| **Operational Handoff Success** | $< 5\text{ minutes}$ | A new engineer or evaluator must be able to clone the repository, run `docker-compose up`, and interact with the application smoothly. |

---

## 3. Assumptions & Constraints

Because the client brief had open parameters, the following explicit assumptions were recorded:
1. **Offline & Air-Gapped Evaluation Priority:** Evaluators may run the project without paying for cloud API keys. Therefore, local Ollama execution is first-class, and an intelligent resilient mock provider is embedded as a safety net.
2. **Deterministic Chunk Attribution:** Transcripts must retain speaker identifiers, episode titles, and section timestamps across chunk boundaries to ensure citation accuracy.
3. **Untrusted Artifact Content:** Even though the LLM is controlled, any HTML/CSS code snippet generated must be treated as untrusted user input and isolated in a sandboxed iframe without `allow-same-origin`.
4. **Data Sourcing:** Transcripts are sourced from the public Lenny's Podcast Transcripts archive, normalized with YAML frontmatter metadata and structured transcript markdown.

---

## 4. Scope Choices: Inclusions & Deliberate Exclusions

### 4.1 In Scope
- **Full-Stack Application:** FastAPI backend with async streaming endpoints + React TypeScript frontend with Vite and Tailwind CSS.
- **Dynamic Dual-Model Provider Layer:** Real-time UI toggle between local Ollama (`llama3.2`, `llama3.1`, `mistral`) and cloud models (`claude-3-5-sonnet`, `gpt-4o`).
- **PostgreSQL + pgvector Persistence:** Persistent storage for chat sessions, message histories, source citations, and generated artifacts, utilizing HNSW cosine similarity search.
- **Ship 30 for 30 Skill Engine:** Structured prompt engineering producing ~1,250 words, hook formulas, 1-3 sentence paragraphs, bold anchors, and operational takeaways.
- **Claude-Style In-App Artifact Viewer:** Interactive dual pane with live preview, code inspector, copy-to-clipboard, download file, and strict iframe sandboxing.
- **Docker Compose Setup:** Multi-service composition (`db`, `backend`, `frontend`, `ollama`) with healthchecks.

### 4.2 Deliberately Excluded (Out of Scope for Initial Deployment)
- **Live Audio/Video Streaming:** The assistant operates on text transcripts to maximize processing speed, token density, and retrieval determinism.
- **User Authentication / Multi-Tenancy:** Omitted in favor of lightweight session-based isolation to minimize evaluation friction. Can be extended with OAuth/Clerk in Phase 2.
- **Voice Input / Whisper Transcription on the Fly:** Transcripts are pre-ingested into vector storage to avoid GPU overhead during conversational queries.

---

## 5. User Journeys & Core Interaction Flows

### Flow 1: Grounded Strategic Query
1. User enters: *"What is Brian Chesky's advice on founder mode and running a product company?"*
2. System computes embedding, searches `pgvector` with cosine similarity, retrieves top 5 relevant transcript segments with scores $\ge 0.60$.
3. System emits SSE status: `Retrieving transcripts...` $\rightarrow$ `Analyzing 5 excerpts from Brian Chesky...`
4. Assistant streams answer with grounded facts and cites `[Episode: Brian Chesky's new playbook, 00:00:00]`.
5. User expands the **Sources Drawer** to inspect verbatim context chunks and similarity scores.

### Flow 2: Ship 30 for 30 Essay Transformation
1. User clicks **"Transform to Ship 30 for 30"** on the grounded answer or toggles the **Ship 30 for 30 Mode**.
2. The skill engine reformulates the grounded insights into an atomic essay:
   - Hook with a counterintuitive insight on micromanagement vs. being in the details.
   - 1-3 sentence paragraphs.
   - Bold anchor words for rapid scanning.
   - Step-by-step tactical checklist.
3. Automatically opens the essay inside the **Artifact Viewer** as a polished Markdown document.

### Flow 3: Interactive Artifact Generation & Sandboxed Preview
1. User asks: *"Generate an interactive retention curve calculator in HTML/CSS based on Lenny's metrics frameworks."*
2. Assistant streams conversational explanation and outputs an `<artifact>` block containing full HTML/CSS/JS.
3. Frontend detects artifact tags, extracts title and code, and slides open the right-hand **Artifact Viewer**.
4. The artifact renders in real time inside a sandboxed iframe (`sandbox="allow-scripts"`), sanitized with `DOMPurify`.
5. User toggles between **Preview** and **Code**, or clicks **Download** to save the snippet locally.

---

## 6. Risk Assessment & Mitigation Matrix

| Risk | Likelihood | Impact | Mitigation Strategy |
| :--- | :--- | :--- | :--- |
| **Model Hallucination** | Medium | High | Strict RAG prompt framing with low temperature ($0.2$–$0.3$) and automated fallback refusal when similarity is below threshold. |
| **Ollama Service Unreachable** | Medium | Medium | Backend health probe continuously detects Ollama status; UI displays diagnostic badge and offers seamless fallback to Cloud or Resilient Mock. |
| **XSS / Sandbox Escape via HTML Artifacts** | High | Critical | Render inside an iframe with `sandbox="allow-scripts"` (strictly avoiding `allow-same-origin`), paired with DOMPurify sanitization. |
| **Local 7B/8B Model Reasoning Limits** | Medium | Medium | Tailored system prompt templates with explicit step-by-step structural guidelines and concise few-shot framing. |
| **Database Connection Latency / Port Conflicts** | Low | Medium | Resilient dual-mode DB engine: PostgreSQL with pgvector for production/Docker; automatic in-memory fallback for zero-friction local testing. |
