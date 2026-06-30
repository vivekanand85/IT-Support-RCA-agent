import streamlit as st
import requests
import json
import time

st.set_page_config(page_title="IT Support RCA Agent", page_icon="🤖", layout="centered")

st.markdown("""
<style>
.tag-pill { display: inline-block; padding: 2px 9px; border-radius: 6px; font-size: 12px; background: #f0f0f0; color: #555; margin-right: 6px; }
.badge-ok { background: #e6f4ea; color: #1e7e34; padding: 2px 9px; border-radius: 6px; font-size: 12px; }
.badge-esc { background: #fdf3e0; color: #a8650f; padding: 2px 9px; border-radius: 6px; font-size: 12px; }
</style>
""", unsafe_allow_html=True)

st.title("🤖 IT Support RCA Agent")
st.caption("Five-agent LangGraph pipeline · HCLTech–OpenAI Agentic AI Hackathon")

if "history" not in st.session_state:
    st.session_state.history = []

NODE_LABELS = {
    "issue_detection": "🔍 Agent 1 — Detecting issue type",
    "sop_retrieval": "📚 Agent 2 — Searching knowledge base (RAG)",
    "execution": "🔧 Agent 3 — Attempting automated fix",
    "ticket": "🎫 Agent 4 — Creating support ticket",
    "rca": "📋 Agent 5 — Generating RCA report",
}

def stream_resolution(issue, user_id):
    resp = requests.post(
        "http://127.0.0.1:8000/resolve-issue-stream",
        json={"message": issue, "user_id": user_id},
        stream=True, timeout=120,
    )
    for line in resp.iter_lines():
        if line and line.startswith(b"data: "):
            yield json.loads(line[len(b"data: "):])


with st.expander("📁 Or upload a log file instead"):
    uploaded_file = st.file_uploader("Choose a .log or .txt file", type=["log", "txt"], key="log_uploader")
    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()  # read immediately, before any rerun can stale it
        if st.button("Analyze log file", key="analyze_btn"):
            with st.spinner("Parsing log and running agents..."):
                files = {"file": (uploaded_file.name, file_bytes)}
                resp = requests.post(
                    "http://127.0.0.1:8000/resolve-issue-from-log",
                    files=files,
                    params={"user_id": "vivek@hcl.com"},
                    timeout=120,
                )
                data = resp.json()
                data["issue_resolved"] = data.pop("resolved")
                st.session_state.history.insert(0, data)
                st.success(f"Extracted from log: {data['extracted_issue_text'][:200]}")

def render_result(entry):
    """One single place that renders a result - used for both the live
    submission and history playback, so it can never be drawn twice."""
    st.caption(entry["ticket_id"])
    tag = entry["issue_type"]
    ok = entry["issue_resolved"]
    badge_html = (
        f'<span class="tag-pill">{tag}</span>'
        f'<span class="{"badge-ok" if ok else "badge-esc"}">'
        f'{"✅ Resolved" if ok else "🎫 Escalated"}</span>'
    )
    st.markdown(badge_html, unsafe_allow_html=True)

    if ok:
        st.write("**Action taken:**", entry["execution_result"])
    else:
        st.write("**Escalated to:**", entry["escalation_team"])
        st.write(entry["execution_result"])

    with st.expander("📋 RCA report"):
        st.write("**Root cause**")
        st.write(entry["root_cause"])
        st.write("**Resolution summary**")
        st.write(entry["resolution_summary"])
        st.write("**Prevention**")
        st.write(entry["prevention_recommendation"])


issue = st.chat_input("Describe your IT issue...")

if issue:
    with st.chat_message("user"):
        st.write(issue)

    with st.chat_message("assistant"):
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
            time.sleep(0.4)

        step_box.empty()

        if final_data:
            # Render ONCE here, then store - the history loop below only
            # plays back PREVIOUS entries, never this one again.
            render_result(final_data)
            st.session_state.history.insert(0, final_data)

# Only past entries from before this run - never duplicates the one above
for entry in st.session_state.history[1:] if issue else st.session_state.history:
    with st.chat_message("assistant"):
        render_result(entry)