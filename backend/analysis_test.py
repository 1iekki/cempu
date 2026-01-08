import asyncio
from concurrent.futures import ProcessPoolExecutor
from fastapi import FastAPI
import uuid
import analysisParams
from contextClassifier import ContextClassifier
from contextProcessor import ContextProcessor


app = FastAPI()
executor = ProcessPoolExecutor()
tasks = {}

def analyze(group_num:int) -> float:
    path = f"{analysisParams.AUDIO_PATH}/{group_num}/rec.wav"
    p = ContextProcessor(analysisParams.params)
    clf = ContextClassifier(True)
    res = p.process(path)

    return clf.getScore(res)


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