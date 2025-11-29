import whisper

class Transcriber:
    model: whisper.model = None
    
    def __init__(self, modelName = "turbo"):
        print("Loading model...")
        self.model = whisper.load_model(modelName)
        print("Model loaded")
        
    def transcribe(self, audioFile, printWithProcessing = False):
        print("Processing...")
        result = self.model.transcribe(audioFile, fp16=False, verbose=printWithProcessing)
        print(result["text"])
        return result
        
   