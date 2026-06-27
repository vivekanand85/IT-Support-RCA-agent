from pydantic import BaseModel

class AgentState(BaseModel):

    ticket_id : str=""
    user_id : str=""
    raw_issue_text : str =""

    issuse_type:str=""
    issue_details:str=""

    sop_found:bool=False
    sop_content:str=""

    execution_attempted: bool = False
    execution_result: str = ""
    issue_resolved: bool = False

    ticket_created: bool = False
    escalation_team: str = ""

    root_cause: str = ""
    resolution_summary: str = ""
    prevention_recommendation: str = ""

    
