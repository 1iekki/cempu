import os
import whisper
from typing import Callable

class Transcriber:
    model: whisper.model.Whisper = None
    modelName: str = ""

    def __init__(self, modelName="turbo", modelPath="models/whisper"):
        if not os.path.exists(modelPath):
            print(f"Directory {modelPath} not found, creating it...")
            os.makedirs(modelPath, exist_ok=True)
            print(f"Downloading whisper model {modelName}...")
        else:
            print(f"Checking for whisper model '{modelName}' in {modelPath}...")

        self.model = whisper.load_model(modelName, download_root=modelPath)
        print(f"Model loaded from {modelPath}. Using whisper model: {modelName}")
        self.modelName = modelName

    def transcribe(self, audio_path:str, printWithProcessing:bool = False, gpuEnabled: bool = False) -> dict:
        """
        outputs a transcription result as a dictionary
        {
            "text": "...",
            "segments": [...],
            "language": "en",
            "task": "transcribe"
        }
        segment:
        {
            "id": 0,
            "seek": 0,
            "start": 0.0,
            "end": 3.2,
            "text": " Hello everyone.",
            "tokens": [...],
            "temperature": 0.0,
            "avg_logprob": -0.2,
            "compression_ratio": 1.1,
            "no_speech_prob": 0.01
        }

        avg_logprob:
            0 = confident
            less = less confident
        
        compression_ratio:
            < 2.0 = normal
            high values = repetitive or hallucinated text
        """
        print(f"Starting the tracsrpition using whiper model: {self.modelName}")
        result = self.model.transcribe(audio_path, fp16=gpuEnabled, verbose=printWithProcessing, language="en")
        return result
    
    def stream_segment_to(self, audio_path:str, on_segment:Callable) -> None:
        result = self.transcribe(audio_path)

        for seg in result["segments"]:
            on_segment(seg)
