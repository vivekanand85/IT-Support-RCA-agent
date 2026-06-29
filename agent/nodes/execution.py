from agent.state import AgentState
from tools.action_tools import restart_vpn_service, reset_password
from storage.resolution_history import was_already_attempted, mark_as_attempted

AUTO_RESOLVABLE = {
    "vpn_auth_failure": restart_vpn_service,
    "password_reset": reset_password,
}


def execution_node(state: AgentState) -> AgentState:
    tool_fn = AUTO_RESOLVABLE.get(state.issue_type)

    if not tool_fn:
        state.execution_attempted = False
        state.execution_result = "No automated fix available - requires human review."
        state.issue_resolved = False
        return state

    if was_already_attempted(state.user_id, state.issue_type):
        # Same user, same issue type, already had this exact fix tried before.
        # Don't trust it again - escalate to a human instead of repeating it.
        state.execution_attempted = False
        state.execution_result = (
            f"This {state.issue_type} issue recurred after a previous automated fix - "
            f"escalating to a human instead of retrying the same fix."
        )
        state.issue_resolved = False
        return state

    result = tool_fn(state.user_id)
    state.execution_attempted = True
    state.execution_result = result
    state.issue_resolved = True
    mark_as_attempted(state.user_id, state.issue_type)
    return state