from agent.state import AgentState
from agent.graph import agent_graph

def get(state, field):
    return state[field] if isinstance(state, dict) else getattr(state, field)

def run(ticket_id, user_id, issue_text):
    initial_state = AgentState(ticket_id=ticket_id, user_id=user_id, raw_issue_text=issue_text)
    final_state = agent_graph.invoke(initial_state)
    print(f"\n========== {ticket_id} ==========")
    print("Issue Type:", get(final_state, "issue_type"))
    print("Resolved:", get(final_state, "issue_resolved"))
    print("Execution Result:", get(final_state, "execution_result"))
    print("Escalated To:", get(final_state, "escalation_team") or "N/A")

# First time for this user - should auto-resolve normally
run("TKT-011", "vivek@hcl.com", "VPN keeps disconnecting every 5 minutes")
# Same user, same issue, second time - should now escalate instead

run("TKT-012", "vivek@hcl.com", "VPN keeps disconnecting every 5 minutes")