import os, json, re
from openai import OpenAI
from dotenv import load_dotenv
from agent.state import AgentState

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def rca_node(state: AgentState) -> AgentState:
    """Always runs last - regardless of whether the issue was auto-resolved or escalated."""

    system_prompt = """You are an IT Root Cause Analysis generator.
Based on the full incident context, write a concise RCA with three parts.
If the issue was auto-resolved, describe what was actually fixed.
If it was escalated, say resolution is pending human investigation - do not invent a fix.

Return ONLY valid JSON, no markdown:
{"root_cause": "...", "resolution_summary": "...", "prevention_recommendation": "..."}"""

    context = f"""Issue type: {state.issue_type}
Employee reported: {state.raw_issue_text}
Runbook consulted: {state.sop_content if state.sop_found else 'None found'}
Auto-resolution attempted: {state.execution_attempted}
Execution result: {state.execution_result}
Issue resolved: {state.issue_resolved}
Ticket created: {state.ticket_created}
Escalated to: {state.escalation_team if state.escalation_team else 'N/A'}"""

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
        state.root_cause = parsed.get("root_cause", "")
        state.resolution_summary = parsed.get("resolution_summary", "")
        state.prevention_recommendation = parsed.get("prevention_recommendation", "")
    except Exception:
        state.root_cause = "Unable to determine - parsing error"
        state.resolution_summary = ""
        state.prevention_recommendation = ""

    return state