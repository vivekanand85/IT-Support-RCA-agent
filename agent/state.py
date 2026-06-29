from pydantic import BaseModel

class AgentState(BaseModel):
    # --- INPUT (set once, at the start) ---
    ticket_id: str = ""
    user_id: str = ""
    raw_issue_text: str = ""

    # --- AFTER Agent 1: Issue Detection ---
    issue_type: str = ""
    issue_details: dict = {}

    # --- AFTER Agent 2: SOP/Runbook Retrieval (RAG) ---
    sop_found: bool = False
    sop_content: str = ""

    # --- AFTER Agent 3: Execution ---
    execution_attempted: bool = False
    execution_result: str = ""
    issue_resolved: bool = False

    # --- AFTER Agent 4: Ticket (only runs if NOT resolved) ---
    ticket_created: bool = False
    escalation_team: str = ""

    # --- AFTER Agent 5: RCA (always runs, last) ---
    root_cause: str = ""
    resolution_summary: str = ""
    prevention_recommendation: str = ""