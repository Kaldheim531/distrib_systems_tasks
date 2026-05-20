import logging

from fastapi import FastAPI

app = FastAPI()
logging.basicConfig(level=logging.INFO)

messages = []


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/notify", status_code=201)
async def notify(message: dict):
    messages.append(message)
    logging.info("notification sent")
    return {"status": "sent", "message": message}


@app.get("/notify")
async def get_messages():
    return messages
