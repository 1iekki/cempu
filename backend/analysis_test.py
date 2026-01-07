import asyncio
from concurrent.futures import ProcessPoolExecutor
from fastapi import FastAPI
import uuid

app = FastAPI()
executor = ProcessPoolExecutor()
tasks = {}

def analyze(audio_path:str):
    pass

@app.post("/analyze/{audio_path}")
async def start_analysis(audio_path:str):
    loop = asyncio.get_running_loop()
    task = loop.run_in_executor(executor, analyze, audio_path)

    task_id = str(uuid.uuid4())
    tasks[task_id] = task

    return {"task_id": task_id}