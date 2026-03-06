from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import uuid

app = FastAPI()

storage = []

class ItemIn(BaseModel):
    name: str
    status: str

class ItemOut(ItemIn):
    id: str

@app.get("/tickets", response_model=List[ItemOut])
def list_tickets():
    return storage

@app.post("/tickets", response_model=ItemOut, status_code=201)
def add_ticket(data: ItemIn):
    record = data.model_dump()
    record["id"] = str(uuid.uuid4())
    storage.append(record)
    return record

@app.get("/tickets/{ticket_id}", response_model=ItemOut)
def fetch_ticket(ticket_id: str):
    for record in storage:
        if record["id"] == ticket_id:
            return record
    raise HTTPException(status_code=404, detail="Not found")