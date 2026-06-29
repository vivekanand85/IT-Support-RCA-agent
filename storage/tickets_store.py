_tickets: dict[str,dict] ={}

def save_ticket(ticket_id:str,ticket_data:dict)->None:
    _tickets[ticket_id]=ticket_data

def get_ticket(ticket_id:str)->dict | None:
    return _tickets.get(ticket_id)

def get_all_tickets()->dict:
    return _tickets
