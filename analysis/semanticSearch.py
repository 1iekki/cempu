import os
from sentence_transformers import SentenceTransformer
from torch import Tensor

class SemanticSearch:
    model: SentenceTransformer = None
    passage_embeddings: Tensor = None
    query_embedding: Tensor = None

    def __init__(self, modelPath):
        if not os.path.exists(modelPath):
            print(f"Downloading model semantic search model to {modelPath}...")
            self.model = SentenceTransformer("multi-qa-mpnet-base-cos-v1")
            self.model.save(modelPath)
            print(f"Download completed, model saved under: {modelPath}")

        else:
            print(f"Loaded semantic search model from: {modelPath}")
            self.model = SentenceTransformer(modelPath)

    def encode_passage(self, passage:list):
        self.passage_embeddings = self.model.encode(passage)

    def query(self, query:str) -> list:
        self.query_embedding = self.model.encode(query)
        return self.model.similarity(self.query_embedding, self.passage_embeddings).tolist()