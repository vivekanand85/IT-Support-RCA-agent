from agent.state import AgentState
from agent.nodes.issue_detection import issue_detection_node


state=AgentState(
    ticket_id="TKT-001",
    user_id="vivek@hcl.com",
    raw_issue_text="VPN keeps disconnecting every 5 minutes,cant stay connected"
)
result=issue_detection_node(state)
print("issue type:",result.issuse_type)
print("issue details:",result.issue_details)
