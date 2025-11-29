import os
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from semanticSearch import SemanticSearch
from transcriber import Transcriber

def main():
    load_dotenv()
    s = SemanticSearch(os.getenv("SEMSEARCH_MODEL_PATH")) # if model not downloaded, will download to path
    passage = [
            "London is known for its financial district",
            "London has 9,787,426 inhabitants at the 2011 census",
            "The United Kingdom is the fourth largest exporter of goods in the world",
        ]
    query = "How big is London"

    s.encode_passage(passage)
    s.query(query)

    passage.append("Which of these recipes contain eggs")
    s.encode_passage(passage)
    s.query("I just made an omelette")

    transcribe()
    
def transcribe():
    transcrib = Transcriber(os.getenv("TRANSCRIBER_MODEL_NAME")) # tiny/base/small/medium/large/turbo
    transcrib.transcribe(os.getenv("AUDIO_PATH"), printWithProcessing=True) 

if __name__ == "__main__":
    main()
