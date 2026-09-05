# 2–3 Minute Demo Video Guide & Script
## Project: The Lenny Growth Assistant
**Assessment:** Forward Deployed Engineer Take-Home Assessment  
**Format:** Screen Recording with Camera Enabled (Picture-in-Picture)  
**Target Duration:** 2 minutes 45 seconds  

---

## Pre-Recording Checklist
1. **Local Model Ready:** Ensure Ollama is running (`ollama serve`) with `llama3.2:3b` or `llama3.1:8b` pulled.
2. **Application Running:** Open `http://localhost:3000` in your browser. Ensure the backend health indicator shows green.
3. **Camera & Mic Setup:** Position your camera in the top-right corner of the screen recording software (OBS, Loom, or CleanShot).

---

## Timed Video Script

### Segment 1: The Problem & Forward Deployment Context (0:00 – 0:40)
* **Visual:** Camera on you, then switch focus to the Lenny Growth Assistant landing screen.
* **Speaking Points:**
  > *"Hi everyone, I’m presenting **The Lenny Growth Assistant**—a full-stack, enterprise-grade retrieval-augmented generation platform designed for product managers and growth leaders.*
  >
  > *Product teams face a recurring challenge: Lenny’s Podcast contains over 200 hours of the most tactical, battle-tested advice in tech—from Brian Chesky to Elena Verna. But when you need to know how to set a North Star metric or run a product-led growth motion today, you can’t listen to a 90-minute audio episode, and generic LLMs hallucinate vague advice.*
  >
  > *Our goal as Forward Deployed Engineers was to build a reliable internal assistant that ingests these transcripts, answers questions with verifiable citations, turns insights into executive Ship 30 for 30 essays, and renders interactive artifacts—all deployable in a single command."*

---

### Segment 2: Grounded Q&A with Local Ollama (0:40 – 1:25)
* **Visual:** Select **Ollama (Local - llama3.2:3b)** from the model badge in the top navbar. Click the starter chip: *"Brian Chesky on Founder Mode & Roadmaps"*.
* **Actions:**
  - Point out the real-time status pill: `Searching transcripts...` $\rightarrow$ `Retrieved 5 chunks`.
  - Watch the answer stream in real time.
  - Expand the **Sources Drawer** showing the exact episode title, guest name, timestamp (`00:00:00`), and cosine similarity score ($\ge 88\%$).
* **Speaking Points:**
  > *"First, notice that we are running entirely locally on Ollama without any cloud API dependencies. I ask about Brian Chesky's founder mode. In under two seconds, our pgvector HNSW index retrieves the top matching chunks from the transcript archive.*
  >
  > *Every claim is strictly cited with timestamps. If you ask an out-of-domain question, like 'how to bake bread,' our strict similarity threshold triggers an immediate, grounded refusal rather than hallucinating."*

---

### Segment 3: Ship 30 for 30 & Claude-Style Artifact Viewer (1:25 – 2:10)
* **Visual:** Click the **"⚡ Transform to Ship 30 for 30"** action button or switch mode.
* **Actions:**
  - The right-hand pane slides open smoothly: **The Claude-Style Artifact Viewer**.
  - Show the essay formatted with a curiosity-driven Hook, short 1-3 sentence paragraphs, bold anchor words, and a concrete 5-step checklist.
  - Next, ask for an interactive artifact: *"Generate an interactive retention calculator in HTML/CSS."*
  - Toggle between **Preview** (live sandboxed interactive widget) and **Code** (clean HTML/CSS syntax).
  - Highlight the security badge: `Sandboxed Preview (iframe sandbox="allow-scripts", no allow-same-origin)`.
* **Speaking Points:**
  > *"Next is our Ship 30 for 30 skill engine. Instead of a generic prompt, it follows the structured heuristics of Nicolas Cole's framework: high-retention hook, rapid skimmability, bold anchors, and operational takeaways.*
  >
  > *Notice our side-by-side Artifact Viewer modeled on Claude Artifacts. When we generate HTML widgets or calculators, they render natively in a secure, sandboxed container. By omitting `allow-same-origin`, we isolate the untrusted HTML from parent cookies and storage, completely mitigating XSS vulnerabilities."*

---

### Segment 4: Architecture, Operability & Key Trade-Off (2:10 – 2:45)
* **Visual:** Briefly show the terminal running `docker-compose up` or tests passing with `pytest`.
* **Speaking Points:**
  > *"To ensure seamless client handoff, the entire system runs with `docker-compose up`, orchestrating pgvector PostgreSQL, FastAPI, and Vite.*
  >
  > *An important technical trade-off we navigated was **local 8B parameter model quantization vs. retrieval density**. Running quantized local models on consumer hardware restricts the context window and reasoning nuance compared to Claude 3.5 Sonnet. To mitigate this, we optimized our chunking strategy with semantic recursive splitting and metadata injection at chunk headers. This ensures local models receive dense, pre-digested context, achieving near-frontier grounding accuracy at zero operational inference cost.*
  >
  > *Thank you, and I look forward to walking through the architecture in detail!"*
