from agent.state import AgentState
from agent.nodes.issue_detection import issue_detection_node
from agent.nodes.sop_retrieval import sop_retrieval_node
from agent.nodes.execution import execution_node
from agent.nodes.ticket import ticket_node
from agent.nodes.rca import rca_node

def run_full_pipeline(ticket_id,user_id,issue_text):
    state=AgentState(ticket_id=ticket_id,user_id=user_id,raw_issue_text=issue_text)
    state=issue_detection_node(state)
    state=sop_retrieval_node(state)
    state=execution_node(state)

    if not state.issue_resolved:
        state=ticket_node(state)
    
    state=rca_node(state)
    print(f"\n========== {ticket_id} ==========")
    print("Issue Type:", state.issue_type)
    print("Resolved:", state.issue_resolved)
    print("Escalated To:", state.escalation_team or "N/A")
    print("Root Cause:", state.root_cause)
    print("Resolution Summary:", state.resolution_summary)
    print("Prevention:", state.prevention_recommendation)

run_full_pipeline("TKT-007", "vivek@hcl.com", "VPN keeps disconnecting every 5 minutes")

run_full_pipeline("TKT-008", "vivek@hcl.com", "I can't access the dev S3 bucket, getting access denied")


