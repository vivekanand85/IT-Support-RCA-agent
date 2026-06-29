import uuid
from fastapi import FastAPI
from pydantic import BaseModel
from agent.state import AgentState
from agent.graph import agent_graph

from fastapi.responses import StreamingResponse
import json

app = FastAPI(title="IT Support RCA Agent")


class IssueRequest(BaseModel):
    message: str
    user_id: str = "employee@hcl.com"


class IssueResponse(BaseModel):
    ticket_id: str
    issue_type: str
    resolved: bool
    execution_result: str
    escalation_team: str
    root_cause: str
    resolution_summary: str
    prevention_recommendation: str

@app.get("/")
def health_check():
    return {"status": "IT Support RCA Agent is running"}


@app.post("/resolve-issue", response_model=IssueResponse)
def resolve_issue(request: IssueRequest):
    ticket_id = f"TKT-{uuid.uuid4().hex[:6].upper()}"

    initial_state = AgentState(
        ticket_id=ticket_id,
        user_id=request.user_id,
        raw_issue_text=request.message,
    )

    result = agent_graph.invoke(initial_state)

    get = (lambda f: result[f]) if isinstance(result, dict) else (lambda f: getattr(result, f))

    return IssueResponse(
        ticket_id=ticket_id,
        issue_type=get("issue_type"),
        resolved=get("issue_resolved"),
        execution_result=get("execution_result"),
        escalation_team=get("escalation_team") or "N/A",
        root_cause=get("root_cause"),
        resolution_summary=get("resolution_summary"),
        prevention_recommendation=get("prevention_recommendation"),
    )



def _serialize(state_obj):
    """LangGraph may hand back a dict or the Pydantic object - normalize either way."""
    if isinstance(state_obj, dict):
        return state_obj
    return state_obj.model_dump()


@app.post("/resolve-issue-stream")
def resolve_issue_stream(request: IssueRequest):
    ticket_id = f"TKT-{uuid.uuid4().hex[:6].upper()}"
    initial_state = AgentState(
        ticket_id=ticket_id,
        user_id=request.user_id,
        raw_issue_text=request.message,
    )

    def event_generator():
        for step in agent_graph.stream(initial_state, stream_mode="updates"):
            for node_name, node_state in step.items():
                payload = {"node": node_name, "data": _serialize(node_state)}
                yield f"data: {json.dumps(payload)}\n\n"
        yield f"data: {json.dumps({'node': 'done'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")