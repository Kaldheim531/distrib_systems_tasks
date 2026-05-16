import json
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse

app = FastAPI()
connections = []
client_path = Path(__file__).resolve().parents[1] / "client" / "index.html"


@app.get("/")
def index():
    return FileResponse(client_path)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    role = "caller" if not connections else "receiver"
    connections.append(websocket)
    await websocket.send_text(json.dumps({"type": "role", "role": role}))

    if len(connections) >= 2:
        await broadcast({"type": "ready"})

    try:
        while True:
            message = await websocket.receive_text()
            for connection in list(connections):
                if connection != websocket:
                    await connection.send_text(message)
    except WebSocketDisconnect:
        if websocket in connections:
            connections.remove(websocket)
        await broadcast({"type": "peer-left"})


async def broadcast(message: dict):
    text = json.dumps(message)
    for connection in list(connections):
        await connection.send_text(text)
