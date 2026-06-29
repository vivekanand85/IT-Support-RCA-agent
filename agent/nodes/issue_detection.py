import os, json, re
from openai import OpenAI
from dotenv import load_dotenv
from agent.state import AgentState

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

VALID_TYPES = ["vpn_auth_failure", "password_reset", "access_denied", "service_down", "unknown"]

def issue_detection_node(state: AgentState) -> AgentState:
    system_prompt = """You are an IT issue classifier. Choose exactly one issue_type:
   - vpn_auth_failure: VPN connection drops, can't connect, VPN login fails
- password_reset: forgot password, locked out of account
- access_denied: can't access a specific resource/file/system, permission errors
- service_down: an internal tool/service itself is down or unreachable for everyone (Jenkins, Jira, etc.)
- unknown: doesn't clearly match any of the above

Return ONLY valid JSON, no markdown:
{"issue_type": "...", "issue_details": {"key": "value pairs of anything specific mentioned"}}"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": state.raw_issue_text}
        ]
    )

    raw = response.choices[0].message.content.strip()
    raw = re.sub(r"```json|```", "", raw).strip()

    try:
        parsed = json.loads(raw)
        state.issue_type = parsed.get("issue_type", "unknown")
        state.issue_details = parsed.get("issue_details", {})
    except Exception:
        state.issue_type = "unknown"
        state.issue_details = {}

    return state