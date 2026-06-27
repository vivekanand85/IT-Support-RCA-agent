from agent.state import AgentState

state=AgentState(
    ticket_id="TKT-001",
    user_id="vivek@hcl.com",
    raw_issue_text="VPN keeps disconnecting every 5 minutes"
)

print(state)

print("------")

print("issuse resolved ? ",state.issue_resolved)

state.issuse_type="vpn_auth_failure"
state.issue_resolved=True
print('--------------')
print(state.issuse_type,state.issue_resolved)

