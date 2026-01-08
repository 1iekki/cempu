import asyncio
from concurrent.futures import ProcessPoolExecutor
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import analysisParams
from cempuMQTT import CempuMQTT
from connectionManager import ConnectionManager
from contextClassifier import ContextClassifier
from contextProcessor import ContextProcessor

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
tasks = {}
executor = ProcessPoolExecutor()

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

def analyze(group_num:int) -> float:
    path = f"{analysisParams.AUDIO_PATH}/{group_num}/rec.wav"
    p = ContextProcessor(analysisParams.params)
    clf = ContextClassifier(True)
    res = p.process(path)
    score = clf.getScore(res)
    return score


@app.post("/analyze/{group_num}")
async def start_analysis(group_num:int):
    loop = asyncio.get_running_loop()
    task = loop.run_in_executor(executor, analyze, group_num)

    if(tasks.get(group_num)):
        tasks.get(group_num).cancel()
    tasks[group_num] = task

    return {
        "message" : f"Analysis started for group {group_num}",
        "audioPath" : f"{analysisParams.AUDIO_PATH}/{group_num}/rec.wav"
        }

@app.get("/analyze/{group_num}")
async def get_analysis_results(group_num:int):
    if not tasks.get(group_num):
        return "TASK NOT FOUND"
    if(tasks[group_num].done()):
        return tasks[group_num].result()
    else:
        return "TASK IN PROGRESS"