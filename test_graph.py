from agent.state import AgentState
from agent.graph import agent_graph

# LangGraph can return either the Pydantic object or a plain dict
# depending on version - this small helper reads either safely.
def get(state, field):
    return state[field] if isinstance(state, dict) else getattr(state, field)


def run(ticket_id, user_id, issue_text):
    initial_state = AgentState(ticket_id=ticket_id, user_id=user_id, raw_issue_text=issue_text)
    final_state = agent_graph.invoke(initial_state)

    print(f"\n========== {ticket_id} ==========")
    print("Issue Type:", get(final_state, "issue_type"))
    print("Resolved:", get(final_state, "issue_resolved"))
    print("Escalated To:", get(final_state, "escalation_team") or "N/A")
    print("Root Cause:", get(final_state, "root_cause"))
    print("Resolution Summary:", get(final_state, "resolution_summary"))


run("TKT-009", "vivek@hcl.com", "VPN keeps disconnecting every 5 minutes")
run("TKT-010", "vivek@hcl.com", "I can't access the dev S3 bucket, getting access denied")