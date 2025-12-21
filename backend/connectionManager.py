from typing import List

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, device_id: str):
        await websocket.accept()
        if device_id not in self.active_connections:
            self.active_connections[device_id] = []
        self.active_connections[device_id].append(websocket)

    def disconnect(self, websocket: WebSocket, device_id: str):
        if device_id in self.active_connections:
            if websocket in self.active_connections[device_id]:
                self.active_connections[device_id].remove(websocket)

            if not self.active_connections[device_id]:
                del self.active_connections[device_id]

    async def broadcast_to_device(self, message: str, device_id: str):
        if device_id in self.active_connections:
            for connection in self.active_connections[device_id]:
                await connection.send_text(message)
