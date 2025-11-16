import os
from sentence_transformers import SentenceTransformer
from torch import Tensor

class SemanticSearch:
    model: SentenceTransformer = None
    passage_embeddings: Tensor = None
    query_embedding: Tensor = None

    def __init__(self, modelPath):
        if not os.path.exists(modelPath):
            print("Downloading model...")
            self.model = SentenceTransformer("multi-qa-mpnet-base-cos-v1")
            self.model.save(modelPath)
            print("Download completed, model save under: "+modelPath)

        else:
            self.model = SentenceTransformer(modelPath)

    def encode_passage(self, passage:list):
        self.passage_embeddings = self.model.encode(passage)

    def query(self, query:str):
        self.query_embedding = self.model.encode(query)
        similarity = self.model.similarity(self.query_embedding, self.passage_embeddings)
        print(similarity)