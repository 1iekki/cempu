import os
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from semanticSearch import SemanticSearch
from transcriber import Transcriber
import numpy as np
import pickle

class ContextProcessor:
    semanticSearchModel: SemanticSearch
    transciberModel: Transcriber
    segments:list
    passage:list

    def __init__(self):
        load_dotenv()
        SEMSEARCH_MODEL_PATH = os.getenv("SEMSEARCH_MODEL_PATH")
        TRANSCRIBER_MODEL_NAME = os.getenv("TRANSCRIBER_MODEL_NAME")
        TRANSCRIBER_MODELS_PATH = os.getenv("TRANSCRIBER_MODELS_PATH")

        self.semanticSearchModel = SemanticSearch(SEMSEARCH_MODEL_PATH)                     # if not downloaded, will download to path
        self.transciberModel = Transcriber(TRANSCRIBER_MODEL_NAME, TRANSCRIBER_MODELS_PATH) # if not downloaded, will download to path
        self.segments = []
        self.passage = []

    def process(self, audio_path:str):
        self.transciberModel.stream_segment_to(audio_path, self.handle_seg)
        self.semanticSearchModel.encode_passage(self.passage)
        
        queries = [
            "Which of these sentence fit in an environment of students solving an excersise concerning insertion sort",
            "Insertion sort",
            "Students solve an excersise about insertion sort",
            "Excersise about insertion sort"
        ]

        with open("output_turbo.txt", "w", encoding="utf-8") as f:
            for q in queries:                
                print("###########################################################", file=f)
                print(f"QUERY: {q}", file=f)
                res = np.array(self.semanticSearchModel.query(q))
                res = res.flatten()
                for i, score in enumerate(res):
                    if(self.segments[i]['compression_ratio'] > 2.0): # remove garbage data
                        continue
                    print(f"[{score:.4f}] << {self.segments[i]['start']:.2f} : {self.segments[i]['end']:.2f} => {self.segments[i]['text']}", file=f)
                print(f"MEAN CONFIDENCE: {np.mean(res)}", file=f)
                print("###########################################################\n", file=f)

        with open("segments.pkl", "wb") as f:
            pickle.dump(self.segments, f, protocol=pickle.HIGHEST_PROTOCOL)

    def handle_seg(self, seg):
        self.segments.append(seg)
        self.passage.append(seg['text'])
