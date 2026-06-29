import os, json, re
from openai import OpenAI
from dotenv import load_dotenv
from agent.state import AgentState
from storage.tickets_store import save_ticket

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

VALID_TEAMS = ["L2-Network", "L2-Security", "L2-CloudOps", "L2-Platform", "L2-General"]


def ticket_node(state: AgentState) -> AgentState:
    """Only called when execution_node could NOT resolve the issue."""

    system_prompt = f"""You are an IT escalation specialist. Based on the issue,
pick exactly one team from {VALID_TEAMS} and write a 2-3 line summary for them.

Return ONLY valid JSON, no markdown:
{{"team": "...", "summary": "..."}}"""

    context = f"""Issue type: {state.issue_type}
Employee message: {state.raw_issue_text}
Runbook consulted: {state.sop_content if state.sop_found else 'None found'}
Execution attempted: {state.execution_attempted}"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": context}
        ]
    )

    raw = re.sub(r"```json|```", "", response.choices[0].message.content.strip()).strip()

    try:
        parsed = json.loads(raw)
        state.escalation_team = parsed.get("team", "L2-General")
    except Exception:
        state.escalation_team = "L2-General"

    # Plain Python from here - no LLM needed for storage
    save_ticket(state.ticket_id, {
        "user_id": state.user_id,
        "issue_type": state.issue_type,
        "issue_text": state.raw_issue_text,
        "team": state.escalation_team,
    })
    state.ticket_created = True

    return state