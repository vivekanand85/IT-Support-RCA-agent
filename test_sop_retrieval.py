from agent.state import AgentState
from agent.nodes.issue_detection import issue_detection_node
from agent.nodes.sop_retrieval import sop_retrieval_node

state=AgentState(
    ticket_id="TKT-002",
    user_id="vivek@hcl.com",
    raw_issue_text="VPN keeps disconnecting every 5 minutes, can't stay connected"
)

state=issue_detection_node(state)
print("Issue Type:", state.issue_type)
state=sop_retrieval_node(state)
print("-----")
print("SOP Found:",state.sop_found)
print("SOP Content:\n", state.sop_content)