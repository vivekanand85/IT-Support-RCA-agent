from agent.state import AgentState
from agent.nodes.issue_detection import issue_detection_node
from agent.nodes.sop_retrieval import sop_retrieval_node
from agent.nodes.execution import execution_node


def run_pipeline(ticket_id,user_id,issue_text):
    state=AgentState(ticket_id=ticket_id,user_id=user_id,raw_issue_text=issue_text)
    state=issue_detection_node(state)
    state=sop_retrieval_node(state)
    state=execution_node(state)

    print(f"\n=== {ticket_id} ===")
    print("Issue Type:", state.issue_type)
    print("Issue Resolved:", state.issue_resolved)
    print("Execution Result:", state.execution_result)
    return state


run_pipeline("TKT-003", "vivek@hcl.com", "VPN keeps disconnecting every 5 minutes")

run_pipeline("TKT-004", "vivek@hcl.com", "I can't access the dev S3 bucket, getting access denied")


run_pipeline("TKT-005", "vivek@hcl.com", "I forgot my password and I'm locked out of my account")