import logging

from fastapi import FastAPI

app = FastAPI()
logging.basicConfig(level=logging.INFO)

messages = []


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/notify", status_code=201)
def notify(message: dict):
    messages.append(message)
    logging.info("notification sent")
    return {"status": "sent", "message": message}


@app.get("/notify")
def get_messages():
    return messages
