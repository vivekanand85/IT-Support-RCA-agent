import os, json, re
from openai import OpenAI
from dotenv import load_dotenv
from agent.state import AgentState
from agent.lang import language_instruction

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

VALID_TYPES = ["vpn_auth_failure", "password_reset", "access_denied", "service_down", "unknown"]

def issue_detection_node(state: AgentState) -> AgentState:
    system_prompt = """You are an IT issue classifier. Consider the issue and identify 2-3 plausible issue_types with a confidence level each, then select the single best one.

Valid issue_types:
- vpn_auth_failure: VPN connection drops, can't connect, VPN login fails
- password_reset: forgot password, locked out of account
- access_denied: can't access a specific resource/file/system, permission errors
- service_down: an internal tool/service itself is down or unreachable for everyone (Jenkins, Jira, etc.)
- unknown: doesn't clearly match any of the above

Return ONLY valid JSON, no markdown:
{
  "candidates": [
    {"issue_type": "...", "confidence": "high"|"medium"|"low"},
    {"issue_type": "...", "confidence": "high"|"medium"|"low"}
  ],
  "selected_issue_type": "...",
  "selection_reasoning": "one sentence explaining why the selected type was chosen over the others",
  "issue_details": {"key": "value pairs of anything specific mentioned"}
}""" + language_instruction(state.language)


    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": state.raw_issue_text}
        ]
    )

    raw = response.choices[0].message.content.strip()
    raw = re.sub(r"```json|```", "", raw).strip()

    try:
        parsed = json.loads(raw)

        selected = parsed.get("selected_issue_type", "unknown")
        if selected not in VALID_TYPES:
            selected = "unknown"

        candidates = parsed.get("candidates", [])
        candidate_diagnoses = []
        for c in candidates:
            c_type = c.get("issue_type", "unknown")
            candidate_diagnoses.append({
                "issue_type": c_type,
                "confidence": c.get("confidence", "low"),
                "status": "selected" if c_type == selected else "ruled_out"
            })

        if not any(c["issue_type"] == selected for c in candidate_diagnoses):
            candidate_diagnoses.append({
                "issue_type": selected,
                "confidence": "medium",
                "status": "selected"
            })

        state.issue_type = selected
        state.issue_details = parsed.get("issue_details", {})
        state.candidate_diagnoses = candidate_diagnoses
        state.selection_reasoning = parsed.get("selection_reasoning", "")

    except Exception:
        state.issue_type = "unknown"
        state.issue_details = {}
        state.candidate_diagnoses = []
        state.selection_reasoning = "Unable to determine - parsing error"

    return state