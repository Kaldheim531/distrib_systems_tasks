from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import uuid

app = FastAPI()

# In-memory storage
tickets_db = []

# Модель для входных данных (без id)
class TicketCreate(BaseModel):
    name: str
    status: str  # Ваше дополнительное поле из варианта

# Модель для данных в БД (с id)
class Ticket(TicketCreate):
    id: str

# GET /tickets - список всех билетов
@app.get("/tickets", response_model=List[Ticket])
def get_tickets():
    return tickets_db

# POST /tickets - создать новый билет
@app.post("/tickets", response_model=Ticket, status_code=201)
def create_ticket(ticket: TicketCreate):
    ticket_dict = ticket.model_dump()
    ticket_dict["id"] = str(uuid.uuid4())
    tickets_db.append(ticket_dict)
    return ticket_dict

# GET /tickets/{id} - получить билет по ID
@app.get("/tickets/{ticket_id}", response_model=Ticket)
def get_ticket(ticket_id: str):
    for ticket in tickets_db:
        if ticket["id"] == ticket_id:
            return ticket
    raise HTTPException(status_code=404, detail="Ticket not found")