# UI/UX Design Specification
## Project: The Lenny Growth Assistant
**Status:** Approved & Forward Deployed  
**Theme:** Obsidian Precision (Dark Mode) with Emerald / Indigo Accents  

---

## 1. Design Principles & Aesthetic Philosophy

1. **Claude-Inspired Fluid Split-Pane:** The interface must feel like an intelligence canvas. When conversation yields a tangible deliverable (a Ship 30 essay, checklist, or HTML prototype), the system naturally partitions into a two-column workspace.
2. **Transparency Over Magic:** When AI retrieves context, the user should never wonder where an assertion originated. Retrieval citations, similarity scores, and episode titles must be clearly accessible via interactive source badges and collapsible inspection drawers.
3. **Extreme Typography & Skimmability:** Product managers consume content quickly. The UI enforces strict hierarchical scale, high-contrast monospace code blocks, and Ship 30 for 30 bold anchor highlights.
4. **Resilient Interaction Feedback:** Every transient state (searching transcripts, waiting for first token, streaming, sandboxing, error fallbacks) must feature fluid micro-animations and status indicators.

---

## 2. Information Architecture & Spatial Layout

```
+-------------------------------------------------------------------------------------------------------------------------+
| [LOGO] The Lenny Growth Assistant        [Mode: Standard | Ship 30]    [Provider: Ollama ▾]   [DB: Healthy ●]   [Github] |
+------------------------------------+-----------------------------------------------------+------------------------------+
| SIDEBAR (260px)                    | CHAT PANE (Flex-1)                                  | ARTIFACT VIEWER (50% Split)  |
|                                    |                                                     |                              |
| [+ New Session]                    | User: "What is Brian Chesky's founder mode advice?" | [Preview] [Code]   [Copy] [⤢]|
|                                    |                                                     |------------------------------|
| Recent Conversations               | Assistant:                                          |                              |
| - Brian Chesky on PM               | [🔍 Searched 5 chunks in 42ms]                      | # Founder Mode Playbook      |
| - Elena Verna B2B PLG              |                                                     |                              |
| - Sean Ellis North Star            | Brian Chesky argues that founders often abdicate    | **Leaders are in details.**  |
| - Rahul Vohra PMF Engine           | responsibility under the guise of "empowerment"...  | Micromanagement is telling   |
|                                    |                                                     | people what to do; details   |
|                                    | ┌ Sources (3 Citations) ─────────────────────────┐  | is knowing reality.          |
|                                    | │ • Brian Chesky's new playbook (00:00:00) [92%] │  |                              |
|                                    | │ • Brian Chesky's new playbook (00:01:27) [88%] │  | 1. Single Company Roadmap    |
|                                    | └────────────────────────────────────────────────┘  | 2. Eliminate Product silos   |
|                                    |                                                     | 3. Drive design directly     |
|                                    | [⚡ Transform to Ship 30 for 30] [📄 Open Artifact] |                              |
|                                    |                                                     |                              |
|                                    | [ Input query...                                 ↑] |                              |
+------------------------------------+-----------------------------------------------------+------------------------------+
```

---

## 3. Key Interaction States

### 3.1 Empty State (New Session)
- **Visuals:** Centered prompt hero with Lenny's Podcast badge, greeting copy, and curated starter query chips:
  - *"Brian Chesky on Founder Mode & Roadmaps"*
  - *"Elena Verna's B2B Product-Led Growth Playbook"*
  - *"Rahul Vohra's 4-Step Engine to Measure Product-Market Fit"*
  - *"Interactive Customer Retention Calculator (HTML/CSS Artifact)"*
- Clicking any chip populates the input and initiates the grounded retrieval flow.

### 3.2 Retrieval & Reasoning State
- An animated pulsing pill in the message stream:
  - Phase 1: `Searching 260+ podcast transcripts...`
  - Phase 2: `Retrieved 5 relevant chunks (avg similarity 87%)`
  - Phase 3: `Streaming answer from Ollama (llama3.2:3b)...`

### 3.3 Streaming & Citation Rendering
- Tokens stream in real time with zero layout jitter.
- Inline citations appear with interactive highlight tags: `[Brian Chesky, 00:00:00]`.
- Clicking a citation scrolls and highlights the specific excerpt in the bottom drawer.

### 3.4 Artifact Drawer State
- **Trigger:** Outputting an `<artifact>` block automatically opens the right-hand panel with a smooth CSS slide-in transition (`translate-x-0`).
- **Tab Header:**
  - **Preview Tab:** Renders either rich Markdown or an isolated HTML/CSS widget.
  - **Code Tab:** Shows raw syntax-highlighted code with line numbers.
  - **Action Toolbar:** One-click Copy button with checkmark animation, Download button (`.md` or `.html`), and Expand to Fullscreen modal.

### 3.5 Error & Fallback States
- **Ollama Offline:** A subtle warning banner appears: *"Ollama is offline on localhost:11434. Switching to Cloud / Resilient Mock Mode."*
- **Out of Domain Query:** Non-podcast queries immediately show a clean grounded card: *"I do not have sufficient information in Lenny's podcast archive to answer this."*

---

## 4. Responsive Behavior

| Viewport | Layout Strategy |
| :--- | :--- |
| **Desktop ($\ge 1280\text{px}$)** | 3-column layout: Persistent sidebar (260px) + Dynamic Chat Pane (50%) + Artifact Viewer (50%). |
| **Laptop ($1024\text{px} - 1279\text{px}$)** | Collapsible sidebar + Chat Pane (55%) + Artifact Viewer (45%). |
| **Tablet / Mobile ($< 1024\text{px}$)** | Single column with bottom drawer or slide-over sheet for the Artifact Viewer and hamburger menu for sessions. |

---

## 5. Accessibility (a11y) & Contrast Standards

- **WCAG 2.1 AA Compliance:** Minimum 4.5:1 text contrast ratio across all light/dark themes.
- **Keyboard Navigation:**
  - `Enter` submits query; `Shift + Enter` inserts newline.
  - `Cmd / Ctrl + K` opens session switcher.
  - `Escape` closes the open Artifact Viewer or modal.
- **ARIA Attributes:**
  - `role="log"` and `aria-live="polite"` on chat stream.
  - `aria-label` on model selector, copy buttons, and iframe containers.
