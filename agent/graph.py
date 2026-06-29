from langgraph.graph import StateGraph, END
from agent.state import AgentState
from agent.nodes.issue_detection import issue_detection_node
from agent.nodes.sop_retrieval import sop_retrieval_node
from agent.nodes.execution import execution_node
from agent.nodes.ticket import ticket_node
from agent.nodes.rca import rca_node


def route_after_execution(state: AgentState) -> str:
    """The ONE decision point - mirrors your 'Solution Found?' diamond."""
    return "rca" if state.issue_resolved else "ticket"


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("issue_detection", issue_detection_node)
    graph.add_node("sop_retrieval", sop_retrieval_node)
    graph.add_node("execution", execution_node)
    graph.add_node("ticket", ticket_node)
    graph.add_node("rca", rca_node)

    graph.set_entry_point("issue_detection")

    graph.add_edge("issue_detection", "sop_retrieval")
    graph.add_edge("sop_retrieval", "execution")

    # The branch: YES -> rca directly, NO -> ticket first, then rca
    graph.add_conditional_edges(
        "execution",
        route_after_execution,
        {"rca": "rca", "ticket": "ticket"}
    )

    graph.add_edge("ticket", "rca")
    graph.add_edge("rca", END)

    return graph.compile()


agent_graph = build_graph()