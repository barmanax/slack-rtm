from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse

app = FastAPI()


@app.get("/")
def home():
    return FileResponse("static/index.html")


class ConnectionManager:
    def __init__(self):
        # room name -> list of websocket connections
        self.rooms = {}

    async def connect(self, room: str, websocket: WebSocket):
        await websocket.accept()

        if room not in self.rooms:
            self.rooms[room] = []

        self.rooms[room].append(websocket)

    def disconnect(self, room: str, websocket: WebSocket):
        if room in self.rooms and websocket in self.rooms[room]:
            self.rooms[room].remove(websocket)

            if len(self.rooms[room]) == 0:
                del self.rooms[room]

    async def broadcast_to_room(self, room: str, message: str):
        if room not in self.rooms:
            return

        for connection in self.rooms[room]:
            await connection.send_text(message)


manager = ConnectionManager()


@app.websocket("/ws/{room}")
async def websocket_endpoint(websocket: WebSocket, room: str):
    await manager.connect(room, websocket)

    try:
        while True:
            message = await websocket.receive_text()
            await manager.broadcast_to_room(room, message)
    except WebSocketDisconnect:
        manager.disconnect(room, websocket)