from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

tickets = []
last_id = 0


class TicketCreate(BaseModel):
    name: str
    status: str


class Ticket(TicketCreate):
    id: int


@app.get("/tickets", response_model=list[Ticket])
def get_tickets():
    return tickets


@app.post("/tickets", response_model=Ticket, status_code=201)
def create_ticket(ticket: TicketCreate):
    global last_id

    last_id += 1
    new_ticket = ticket.model_dump()
    new_ticket["id"] = last_id
    tickets.append(new_ticket)

    return new_ticket


@app.get("/tickets/{ticket_id}", response_model=Ticket)
def get_ticket(ticket_id: int):
    for ticket in tickets:
        if ticket["id"] == ticket_id:
            return ticket

    raise HTTPException(status_code=404, detail="Ticket not found")
