import streamlit as st
import requests
import json
import time

st.set_page_config(page_title="IT Support RCA Agent", page_icon="🤖", layout="centered")


LANGUAGES = {
    "English": "en",
    "हिन्दी (Hindi)": "hi",
    "日本語 (Japanese)": "ja",
}

UI_STRINGS = {
    "en": {
        "title": "🤖 IT Support RCA Agent",
        "caption": "Five-agent LangGraph pipeline · HCLTech–OpenAI Agentic AI Hackathon",
        "upload_expander": "📁 Or upload a log file instead",
        "upload_label": "Choose a .log or .txt file",
        "analyze_btn": "Analyze log file",
        "chat_placeholder": "Describe your IT issue...",
        "found_heading": "**Here's what we found:**",
        "still_need_help": "Still need help? Create a case",
        "ticket_info": "🎫 **Still need help?** Ticket **{ticket_id}** has been created and routed to **{team}**. They'll pick this up from here — no further action needed from you right now.",
        "action_taken": "**Action taken:**",
        "rca_report": "📋 RCA report",
        "root_cause": "**Root cause**",
        "resolution_summary": "**Resolution summary**",
        "prevention": "**Prevention**",
    },
    "hi": {
        "title": "🤖 आईटी सपोर्ट RCA एजेंट",
        "caption": "पाँच-एजेंट LangGraph पाइपलाइन · HCLTech–OpenAI Agentic AI Hackathon",
        "upload_expander": "📁 या इसके बजाय लॉग फ़ाइल अपलोड करें",
        "upload_label": "एक .log या .txt फ़ाइल चुनें",
        "analyze_btn": "लॉग फ़ाइल विश्लेषण करें",
        "chat_placeholder": "अपनी आईटी समस्या बताएं...",
        "found_heading": "**हमें यह मिला:**",
        "still_need_help": "अभी भी मदद चाहिए? केस बनाएं",
        "ticket_info": "🎫 **अभी भी मदद चाहिए?** टिकट **{ticket_id}** बनाया गया है और **{team}** को भेजा गया है। वे इसे यहां से संभालेंगे — अभी आपको कुछ करने की आवश्यकता नहीं है।",
        "action_taken": "**की गई कार्रवाई:**",
        "rca_report": "📋 RCA रिपोर्ट",
        "root_cause": "**मूल कारण**",
        "resolution_summary": "**समाधान सारांश**",
        "prevention": "**रोकथाम**",
    },
    "ja": {
        "title": "🤖 ITサポート RCA エージェント",
        "caption": "5エージェント LangGraph パイプライン · HCLTech–OpenAI Agentic AI Hackathon",
        "upload_expander": "📁 またはログファイルをアップロード",
        "upload_label": ".log または .txt ファイルを選択",
        "analyze_btn": "ログファイルを分析",
        "chat_placeholder": "ITの問題を説明してください...",
        "found_heading": "**わかったこと:**",
        "still_need_help": "まだサポートが必要ですか？ケースを作成",
        "ticket_info": "🎫 **まだサポートが必要ですか？** チケット **{ticket_id}** が作成され、**{team}** に転送されました。以降はチームが対応します — お客様側で追加の対応は不要です。",
        "action_taken": "**実施した対応:**",
        "rca_report": "📋 RCA レポート",
        "root_cause": "**根本原因**",
        "resolution_summary": "**解決サマリー**",
        "prevention": "**再発防止策**",
    },
}

if "language" not in st.session_state:
    st.session_state.language = "en"

selected_label = st.selectbox(
    "🌐 Language",
    options=list(LANGUAGES.keys()),
    index=list(LANGUAGES.values()).index(st.session_state.language),
)
st.session_state.language = LANGUAGES[selected_label]

t = UI_STRINGS[st.session_state.language]

st.markdown("""
<style>
.tag-pill { display: inline-block; padding: 2px 9px; border-radius: 6px; font-size: 12px; background: #f0f0f0; color: #555; margin-right: 6px; }
.badge-ok { background: #e6f4ea; color: #1e7e34; padding: 2px 9px; border-radius: 6px; font-size: 12px; }
.badge-esc { background: #fdf3e0; color: #a8650f; padding: 2px 9px; border-radius: 6px; font-size: 12px; }
</style>
""", unsafe_allow_html=True)

st.title(t["title"])
st.caption(t["caption"])

if "history" not in st.session_state:
    st.session_state.history = []

NODE_LABELS = {
    "issue_detection": "🔍 Agent 1 — Detecting issue type",
    "sop_retrieval": "📚 Agent 2 — Searching knowledge base (RAG)",
    "execution": "🔧 Agent 3 — Attempting automated fix",
    "ticket": "🎫 Agent 4 — Creating support ticket",
    "rca": "📋 Agent 5 — Generating RCA report",
}


def render_result(entry):
    """One single place that renders a result - used for both the live
    submission, log upload, and history playback, so it can never be
    drawn twice or drift out of sync between entry points."""
    t = UI_STRINGS[st.session_state.language]
    st.caption(entry["ticket_id"])
    tag = entry["issue_type"]
    ok = entry["issue_resolved"]

    if ok:
        badge_html = (
            f'<span class="tag-pill">{tag}</span>'
            f'<span class="badge-ok">✅ Resolved</span>'
        )
        st.markdown(badge_html, unsafe_allow_html=True)
        st.write(t["action_taken"], entry["execution_result"])
        with st.expander(t["rca_report"]):
            st.write(t["root_cause"])
            st.write(entry["root_cause"])
            st.write(t["resolution_summary"])
            st.write(entry["resolution_summary"])
            st.write(t["prevention"])
            st.write(entry["prevention_recommendation"])
        return

    # --- Unresolved: guidance-first, AWS-style ---
    badge_html = f'<span class="tag-pill">{tag}</span>'
    st.markdown(badge_html, unsafe_allow_html=True)

    st.write(t["found_heading"])
    st.write(entry["root_cause"])
    st.write(entry["resolution_summary"])
    if entry.get("prevention_recommendation"):
        st.caption(f"💡 {entry['prevention_recommendation']}")

    ticket_key = f"ticketed_{entry['ticket_id']}"
    already_ticketed = st.session_state.get(ticket_key)

    if already_ticketed:
        st.info(t["ticket_info"].format(ticket_id=entry["ticket_id"], team=already_ticketed))
    else:
        if st.button(t["still_need_help"], key=f"create_{entry['ticket_id']}"):
            resp = requests.post(f"http://127.0.0.1:8000/create-ticket/{entry['ticket_id']}")
            data = resp.json()
            if data.get("ticket_created"):
                st.session_state[ticket_key] = data["escalation_team"]
                st.rerun()
            else:
                st.error(data.get("error", "Could not create ticket."))


def stream_resolution(issue, user_id):
    resp = requests.post(
        "http://127.0.0.1:8000/resolve-issue-stream",
        json={"message": issue, "user_id": user_id, "language": st.session_state.language},
        stream=True, timeout=120,
    )
    for line in resp.iter_lines():
        if line and line.startswith(b"data: "):
            yield json.loads(line[len(b"data: "):])


with st.expander(t["upload_expander"]):
    uploaded_file = st.file_uploader(t["upload_label"], type=["log", "txt"], key="log_uploader")
    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()  # read immediately, before any rerun can stale it
        if st.button(t["analyze_btn"], key="analyze_btn"):
            with st.spinner("Parsing log and running agents..."):
                files = {"file": (uploaded_file.name, file_bytes)}
                resp = requests.post(
                    "http://127.0.0.1:8000/resolve-issue-from-log",
                    files=files,
                    params={"user_id": "vivek@hcl.com", "language": st.session_state.language},
                    timeout=120,
                )
                data = resp.json()
                data["issue_resolved"] = data.pop("resolved")
                st.session_state.history.insert(0, data)
                st.success(f"Extracted from log: {data['extracted_issue_text'][:200]}")
                


issue = st.chat_input(t["chat_placeholder"])

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

            data = payload["data"]
            label = NODE_LABELS.get(node, node)

            # Presentational surfacing of candidates the single Agent-1 call
            # already considered internally - not a second LLM call or a
            # real parallel agent.
            extra = None
            if node == "issue_detection":
                extra = {
                    "candidates": data.get("candidate_diagnoses", []),
                    "reasoning": data.get("selection_reasoning", ""),
                }

            steps_seen.append((label, extra))

            with step_box.container():
                for step_label, step_extra in steps_seen:
                    st.write(step_label)
                    if step_extra:
                        for c in step_extra["candidates"]:
                            icon = "✅" if c["status"] == "selected" else "◻️"
                            line = f"&nbsp;&nbsp;&nbsp;&nbsp;{icon} `{c['issue_type']}` — {c['confidence']} confidence"
                            if c["status"] == "ruled_out":
                                line = f"<span style='color:#999'>{line}</span>"
                            st.markdown(line, unsafe_allow_html=True)
                        if step_extra["reasoning"]:
                            st.caption(f"↳ {step_extra['reasoning']}")

            final_data = data
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