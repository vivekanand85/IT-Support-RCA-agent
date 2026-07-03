import uuid
from fastapi import FastAPI
from pydantic import BaseModel
from agent.state import AgentState
from agent.graph import agent_graph
from fastapi import UploadFile,File
from tools.log_parser import extract_issue_from_log
from fastapi.responses import StreamingResponse
import json
from agent.nodes.ticket import ticket_node
pending_states: dict[str, AgentState] = {}


app = FastAPI(title="IT Support RCA Agent")


class IssueRequest(BaseModel):
    message: str
    user_id: str = "employee@hcl.com"
    language: str = "en"


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


@app.post("/resolve-issue-stream")
def resolve_issue_stream(request: IssueRequest):
    ticket_id = f"TKT-{uuid.uuid4().hex[:6].upper()}"
    initial_state = AgentState(
        ticket_id=ticket_id,
        user_id=request.user_id,
        raw_issue_text=request.message,
        language=request.language,
    )

    def event_generator():
        last_state = None
        for step in agent_graph.stream(initial_state, stream_mode="updates"):
            for node_name, node_state in step.items():
                payload = {"node": node_name, "data": _serialize(node_state)}
                yield f"data: {json.dumps(payload)}\n\n"
                last_state = node_state

        if last_state is not None:
            final_state = (
                AgentState(**last_state) if isinstance(last_state, dict) else last_state
            )
            if not final_state.issue_resolved:
                pending_states[ticket_id] = final_state
                print(f"[DEBUG] Stored pending state for {ticket_id}")

        yield f"data: {json.dumps({'node': 'done'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

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
        last_state=None
        for step in agent_graph.stream(initial_state,stream_mode="updates"):
            for node_name,node_state in step.items():
                payload={"node":node_name,"data":_serialize(node_state)}
                yield f"data:{json.dumps(payload)}\n\n"
                last_state=node_state

                if last_state is not None:
                    final_state=(
                        AgentState(**last_state) if isinstance(last_state,dict) else last_state
        
                    )
                    if not final_state.issue_resolved:
                        pending_states[ticket_id]=final_state
                        print(f"[DEBUG] Stored pending state for {ticket_id}")
                
                yield f"data:{json.dumps({'node':'done'})}\n\n"

@app.post("/resolve-issue-from-log")
async def resolve_issue_from_log(file: UploadFile = File(...), user_id: str = "employee@hcl.com", language: str = "en"):
    raw_bytes=await file.read()
    log_text= raw_bytes.decode("utf-8", errors="ignore")
    issue_text = extract_issue_from_log(log_text)
    ticket_id = f"TKT-{uuid.uuid4().hex[:6].upper()}"
    initial_state=AgentState(
        ticket_id=ticket_id,
        user_id=user_id,
        raw_issue_text=issue_text,
        language=language,
    )

    result=agent_graph.invoke(initial_state)
    get = (lambda f: result[f]) if isinstance(result, dict) else (lambda f: getattr(result, f))

    final_state = AgentState(**result) if isinstance(result,dict) else (lambda f:getattr(result,f))
    if not final_state.issue_resolved:
        pending_states[ticket_id]=final_state

    return {
        "ticket_id": ticket_id,
        "extracted_issue_text": issue_text,
        "issue_type": get("issue_type"),
        "resolved": get("issue_resolved"),
        "execution_result": get("execution_result"),
        "escalation_team": get("escalation_team") or "N/A",
        "root_cause": get("root_cause"),
        "resolution_summary": get("resolution_summary"),
        "prevention_recommendation": get("prevention_recommendation"),
        "candidate_diagonses":get("candidate_diagnoses"),
        "selection_reasoning": get("selection_reasoning"),
    }



@app.post("/create-ticket/{ticket_id}")
def create_ticket(ticket_id: str):
    state = pending_states.get(ticket_id)

    if state is None:
        return {
            "error": "No pending issue found for this ticket_id. "
                      "It may have already been ticketed, resolved, or the server restarted."
        }

    updated_state = ticket_node(state)

    # Ticket is now created - remove from pending so a second click can't
    # double-create it.
    del pending_states[ticket_id]

    return {
        "ticket_id": ticket_id,
        "ticket_created": updated_state.ticket_created,
        "escalation_team": updated_state.escalation_team,
    }

