from agent.state import AgentState
from agent.nodes.issue_detection import issue_detection_node
from agent.nodes.sop_retrieval import sop_retrieval_node
from agent.nodes.execution import execution_node
from agent.nodes.ticket import ticket_node
from storage.tickets_store import get_all_tickets

state = AgentState(
    ticket_id="TKT-006",
    user_id="vivek@hcl.com",
    raw_issue_text="I can't access the dev S3 bucket, getting access denied"
)

state = issue_detection_node(state)
state = sop_retrieval_node(state)
state = execution_node(state)

print("Issue Resolved:", state.issue_resolved)

if not state.issue_resolved :
    state=ticket_node(state)
    print("ticket created:",state.ticket_created)
    print("Escalation Team", state.escalation_team)


print("-----")
print("All tickets in store:", get_all_tickets())
