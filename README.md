# Enterprise IT Support & RCA Agent

AI-powered multi-agent system that detects IT issues, retrieves troubleshooting
steps via RAG, attempts automated remediation, raises tickets when it can't
resolve something, and generates a Root Cause Analysis (RCA) report — with
each agent's progress streamed live to the UI as it happens.

Built for the **HCLTech–OpenAI Agentic AI Hackathon** (Track 2 — Internal Operations).

- [x] Agent 4 — Ticket Agent (in-memory store, LLM-based team routing)
+ [x] Agent 4 — Ticket Agent (in-memory store, LLM-based team routing; now
+     triggered on-demand via "Create a case" action, not auto-run in the graph)
  [x] Agent 5 — RCA Agent (root cause, resolution summary, prevention)
- [x] LangGraph wiring — full state machine with conditional branching
+ [x] LangGraph wiring — linear state machine (issue_detection → sop_retrieval
+     → execution → rca); ticket creation deferred, called directly from the API
  [x] FastAPI backend — `/resolve-issue` (sync) and `/resolve-issue-stream` (SSE)
+ [x] FastAPI backend — `/create-ticket/{ticket_id}` for on-demand escalation
  [x] Streamlit UI — live per-agent progress via Server-Sent Events
+ [x] Streamlit UI — multi-candidate diagnosis display (Agent 1) + AWS-style
+     guidance-first escalation flow with a "Still need help?" action

## Architecture

```mermaid
flowchart TD
    A[Employee Issue Text] --> B[Agent 1: Issue Detection]
    B --> C[Agent 2: SOP/Runbook Retrieval - RAG]
    C --> D[Agent 3: Execution]
-    D --> E{Issue Resolved?}
-    E -- Yes --> F[Agent 5: RCA Report]
-    E -- No --> G[Agent 4: Ticket Creation]
-    G --> F
+    D --> F[Agent 5: RCA Report / Guidance]
+    F --> H{Issue Resolved?}
+    H -- Yes --> I[Shown as Resolved]
+    H -- No --> J["Still need help?" button]
+    J -->|user clicks| G[Agent 4: Ticket Creation - on demand]
```

**Note on this change:** Agent 1 now internally considers 2–3 candidate
issue types with confidence scores before selecting one — this is a single
structured LLM call, not parallel agents, and is surfaced in the UI for
transparency (not a new reasoning capability).

**Note on Agent 4:** ticket creation is no longer an automatic graph node.
RCA now always runs immediately after execution, regardless of resolution,
so the user sees root-cause guidance first (mirroring AWS Support's
triage UX). Ticket creation only happens if the user explicitly clicks
"Still need help? Create a case," which calls a separate endpoint and runs
`ticket_node` directly against the finished state. Finished-but-unticketed
states are held in an in-memory `pending_states` dict (`main.py`), keyed
by `ticket_id` — a known simplification for the demo; production would use
Redis with a TTL instead of an unbounded dict.

## Tech Stack

- **Python 3.11+**
- **Pydantic** — shared `AgentState` passed between all agents
- **OpenAI API** (`gpt-4o-mini` for reasoning, `text-embedding-3-small` for RAG)
- **LangGraph** — agent orchestration as a state machine with conditional edges
- **FastAPI** — REST API + Server-Sent Events streaming
- **Streamlit** — live demo UI, renders each agent's step as it completes

### Note on RAG implementation
ChromaDB's default local embedding backend (`onnxruntime`) had a Windows DLL
conflict in this environment. Rather than fight the environment, retrieval is
implemented directly: OpenAI embeddings + manual cosine similarity, no vector
DB dependency. Same underlying technique, fewer moving parts.

## Project Structure
├── agent/

│   ├── state.py

│   ├── graph.py

│   └── nodes/

│       ├── issue_detection.py

│       ├── sop_retrieval.py

│       ├── execution.py

│       ├── ticket.py

│       └── rca.py

├── tools/

│   └── action_tools.py

├── storage/

│   └── tickets_store.py

├── knowledge_base/

│   └── docs/              # 4 runbooks: VPN, password reset, access denied, service down

├── main.py                 # FastAPI app

├── streamlit_app.py         # Demo UI

├── test_*.py                # One test script per build step

├── requirements.txt

└── .env                     # not committed — holds OPENAI_API_KEY


## Setup

```bash
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

Create `.env` in the root:

## Running the demo

Terminal 1:
```bash
uvicorn main:app --reload
```

Terminal 2:
```bash
streamlit run streamlit_app.py
```

Open `http://localhost:8501`, describe an IT issue, watch each agent report
its progress live, then view the final RCA report.

- **Streaming over blocking**: the UI uses LangGraph's `.stream()` +
  FastAPI's `StreamingResponse` (SSE) so the multi-agent reasoning is visible
  step-by-step, not hidden behind one blocking call.
+ **Deferred, user-triggered escalation**: ticket creation is decoupled from
+  the LangGraph pipeline entirely. The graph always ends at RCA, presenting
+  guidance first; escalation is a separate, explicit user action
+  (`POST /create-ticket/{ticket_id}`) rather than something that happens
+  silently in the background — closer to how a real support tool should
+  respect the user's intent before creating a ticket on their behalf.

## Known limitations

**`pending_states` (main.py)** — in-memory, unbounded, no TTL, lost on
server restart. Holds finished-but-unticketed states so the "Create a
case" button can act on them later. Production would use Redis with
expiry instead.
**Repeat-issue detection is implemented** (`storage/resolution_history.py`):
if the same issue type recurs for the same user after an automated fix,
`execution_node` refuses to retry it and escalates to a human instead of
repeating the same fix blindly.

## Author

Vivekanand — built for HCLTech–OpenAI Agentic AI Hackathon, Track 2
