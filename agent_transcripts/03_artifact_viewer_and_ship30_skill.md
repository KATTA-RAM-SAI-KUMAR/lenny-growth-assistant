# Agent Transcript 03: Artifact Viewer & Ship 30 for 30 Skill Engine
**Timestamp:** 2026-09-05T09:24:00Z  
**Agent:** Antigravity AI (Pair Programming)  
**Objective:** Engineer the Ship 30 for 30 essay generation skill and build the secure Claude-style Artifact Viewer.

## Engineering Notes & Iterations

### 1. Ship 30 for 30 Heuristics Encoding
- **Challenge:** Avoid vague "write like an essay" instructions that produce generic long-form prose.
- **Implementation:** Structured a prompt specification enforcing the core tenets of Nicolas Cole & Dickie Bush's framework:
  1. **Hook:** A tension-filled opening (first 2-3 lines) contrasting common bad advice with the contrarian truth.
  2. **Short Paragraphs:** 1-3 sentences maximum for high mobile skimmability.
  3. **Bold Anchor Words:** Every bullet point starts with a bold actionable anchor (e.g. `**Audit the roadmap**`, `**Centralize review**`).
  4. **Attribution:** Strictly ground insights in guest statements from Lenny's interviews.
  5. **Actionable Conclusion:** End with a 5-point implementation checklist.

### 2. Claude-Style Artifact Viewer Security
- **Security Vector:** A user prompt could elicit HTML containing malicious script tags trying to read `localStorage` or session tokens.
- **Fix:** Two-layer security barrier:
  1. `DOMPurify.sanitize(content, { WHOLE_DOCUMENT: true, ADD_TAGS: ['style', 'link', 'script'] })` cleans malicious tags and handlers.
  2. The sandboxed iframe sets:
     `sandbox="allow-scripts"`
     and **strictly omits** `allow-same-origin`.
  This allows JavaScript execution for interactive calculators, charts, and toggles, while blocking access to parent window cookies, localStorage, and parent DOM manipulation.

### 3. Split-Pane Layout Interaction
- Engineered smooth sliding transitions and responsive drawer behavior on smaller viewports.
- Added Preview vs Code tabs, copy-to-clipboard, and local file download options.
