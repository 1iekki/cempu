import os
from sentence_transformers import SentenceTransformer, util
import torch
import numpy as np

class SemanticSearch:
    model: SentenceTransformer = None

    def __init__(self, modelPath):
        if not os.path.exists(modelPath):
            print(f"Downloading model semantic search model to {modelPath}...")
            self.model = SentenceTransformer("multi-qa-mpnet-base-cos-v1")
            self.model.save(modelPath)
            print(f"Download completed, model saved under: {modelPath}")

        else:
            print(f"Loaded semantic search model from: {modelPath}")
            self.model = SentenceTransformer(modelPath)

    def encode(self, passage:list) -> torch.Tensor:
        return self.model.encode(passage)

    def similarity(self, t1:torch.Tensor, t2:torch.Tensor) -> torch.Tensor:
        return self.model.similarity(t1, t2)

    def topic_vec(self, topic_phrases) -> torch.Tensor:
        topic_embeds = self.encode(topic_phrases)
        topic_vector = torch.tensor(np.mean(topic_embeds, axis=0)).unsqueeze(0)
        return topic_vector

    def query(self, query:str, passage_embeddings:torch.Tensor) -> torch.Tensor:
        query_embedding = self.model.encode(query)
        return self.model.similarity(query_embedding, passage_embeddings)