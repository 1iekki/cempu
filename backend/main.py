import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from contextlib import asynccontextmanager
from cempuMQTT import CempuMQTT
from connectionManager import ConnectionManager

async def handleMQTTMessages(queue: asyncio.Queue, manager: ConnectionManager):
    while True:
        # 1. Wait for a message from MQTT
        message = await queue.get()
        # 2. Send it to ALL connected users
        await manager.broadcast(message)

        queue.task_done()

@asynccontextmanager
async def lifespan(app: FastAPI):
    manager = ConnectionManager()
    app.state.connectionManager = manager

    loop = asyncio.get_running_loop()
    
    # The Single Shared Queue
    mqtt_queue = asyncio.Queue()

    # Start the worker that reads the queue and broadcasts
    worker_task = asyncio.create_task(handleMQTTMessages(mqtt_queue, manager))
                                      
    with CempuMQTT("server", mqtt_queue, loop) as mqtt:
        app.state.mqtt = mqtt
        yield

        worker_task.cancel()

app = FastAPI(lifespan=lifespan)

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await app.state.connectionManager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        app.state.connectionManager.disconnect(websocket)
        await app.state.connectionManager.broadcast(f"Client left the chat")