import streamlit as st
import requests
import json
import time

st.set_page_config(page_title="IT Support RCA Agent", page_icon="🤖")
st.title("🤖 IT Support RCA Agent")
st.caption("5-agent LangGraph pipeline · HCLTech–OpenAI Agentic AI Hackathon")

if "history" not in st.session_state:
    st.session_state.history = []

NODE_LABELS = {
    "issue_detection": "🔍 Agent 1 — Detecting issue type...",
    "sop_retrieval": "📚 Agent 2 — Searching knowledge base (RAG)...",
    "execution": "🔧 Agent 3 — Attempting automated fix...",
    "ticket": "🎫 Agent 4 — Creating support ticket...",
    "rca": "📋 Agent 5 — Generating RCA report...",
}

def stream_resolution(issue, user_id):
    resp = requests.post(
        "http://127.0.0.1:8000/resolve-issue-stream",
        json={"message": issue, "user_id": user_id},
        stream=True,
        timeout=120,
    )
    for line in resp.iter_lines():
        if line and line.startswith(b"data: "):
            yield json.loads(line[len(b"data: "):])


issue = st.text_input("Describe your IT issue:")

if st.button("Submit") and issue:
    step_box = st.empty()
    steps_seen = []
    final_data = None

    for payload in stream_resolution(issue, "vivek@hcl.com"):
        node = payload.get("node")
        if node == "done":
            break

        steps_seen.append(NODE_LABELS.get(node, node))
        with step_box.container():
            for s in steps_seen:
                st.write(s)

        final_data = payload["data"]
        time.sleep(0.5)  # purely cosmetic pacing so each step is visible to a viewer -
                          # the agent work already happened at full speed; this just
                          # stops the UI from rendering 5 steps in one invisible blink

    if final_data:
        st.session_state.history.insert(0, final_data)
        step_box.empty()

for entry in st.session_state.history:
    with st.container(border=True):
        st.subheader(entry["ticket_id"])

        col1, col2 = st.columns(2)
        col1.metric("Issue Type", entry["issue_type"])
        col2.metric("Status", "✅ Resolved" if entry["issue_resolved"] else "🎫 Escalated")

        if entry["issue_resolved"]:
            st.write("**Action taken:**", entry["execution_result"])
        else:
            st.write("**Escalated to:**", entry["escalation_team"])

        with st.expander("📋 RCA Report"):
            st.write("**Root Cause:**", entry["root_cause"])
            st.write("**Resolution Summary:**", entry["resolution_summary"])
            st.write("**Prevention:**", entry["prevention_recommendation"])