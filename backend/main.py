import asyncio
import os
import shutil
from concurrent.futures import ProcessPoolExecutor
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import (
    FastAPI,
    Response,
    UploadFile,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

import analysisParams
from cempuMQTT import CempuMQTT
from connectionManager import ConnectionManager
from contextClassifier import ContextClassifier
from contextProcessor import ContextProcessor
from speakerDiarization import SpeakerDiarization


async def handleMQTTMessages(queue: asyncio.Queue, manager: ConnectionManager):
    while True:
        data = await queue.get()

        device_id = data["device_id"]
        payload = data["payload"]

        await manager.broadcast_to_device(payload, device_id)

        queue.task_done()


@asynccontextmanager
async def lifespan(app: FastAPI):
    manager = ConnectionManager()
    app.state.connectionManager = manager

    loop = asyncio.get_running_loop()

    mqtt_queue = asyncio.Queue()
    worker_task = asyncio.create_task(handleMQTTMessages(mqtt_queue, manager))

    with CempuMQTT("server", mqtt_queue, loop) as mqtt:
        app.state.mqtt = mqtt
        yield

        worker_task.cancel()


os.makedirs(analysisParams.AUDIO_PATH, exist_ok=True)
app = FastAPI(lifespan=lifespan)

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
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


@app.websocket("/ws/{device_id}")
async def websocket_endpoint(websocket: WebSocket, device_id: str):
    await app.state.connectionManager.connect(websocket, device_id)
    try:
        while True:
            data = await websocket.receive_text()
            app.state.mqtt.sendCommand(data, device_id)
    except WebSocketDisconnect:
        app.state.connectionManager.disconnect(websocket, device_id)


def analyze(device_name: str) -> dict:
    path = f"{analysisParams.AUDIO_PATH}/{device_name}/rec.wav"

    p = ContextProcessor(analysisParams.params)
    clf = ContextClassifier(True)
    res = p.process(path)
    context_score = clf.getScore(res)

    diarizer = SpeakerDiarization()
    output = diarizer.run(path)
    speaker_times = diarizer.get_speaker_times(output)
    diarization_score = diarizer.engagement_score(speaker_times)

    return {
        "context_score": context_score, 
        "engagement_score": diarization_score
    }


@app.post("/analyze/{device_name}")
async def start_analysis(device_name: str):
    loop = asyncio.get_running_loop()
    task = loop.run_in_executor(executor, analyze, device_name)

    if tasks.get(device_name):
        tasks.get(device_name).cancel()
    tasks[device_name] = task

    return {
        "message": f"Analysis started for group {device_name}",
        "audioPath": f"{analysisParams.AUDIO_PATH}/{device_name}/rec.wav",
    }


@app.get("/analyze/{device_name}")
async def get_analysis_results(device_name: str):
    if not tasks.get(device_name):
        return "TASK NOT FOUND"
    if tasks[device_name].done():
        return tasks[device_name].result()
    else:
        return "TASK IN PROGRESS"


@app.post("/upload/{device_name}")
def upload_file(device_name: str, file: UploadFile, response: Response):
    if file.content_type != "audio/wave":
        response.status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
        return {"message": "Invalid file type"}

    baseFilePath = Path(analysisParams.AUDIO_PATH, device_name)
    os.makedirs(baseFilePath, exist_ok=True)
    fullFilePath = baseFilePath / "rec.wav"

    with open(fullFilePath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"message": "Success"}
