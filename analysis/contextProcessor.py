import os
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from semanticSearch import SemanticSearch
from transcriber import Transcriber
import torch
import numpy as np
import pickle

class ContextProcessor:
    semanticSearch: SemanticSearch
    transciberModel: Transcriber
    segments:list
    passage:list

    def __init__(self):
        load_dotenv()
        SEMSEARCH_MODEL_PATH = os.getenv("SEMSEARCH_MODEL_PATH")
        TRANSCRIBER_MODEL_NAME = os.getenv("TRANSCRIBER_MODEL_NAME")
        TRANSCRIBER_MODELS_PATH = os.getenv("TRANSCRIBER_MODELS_PATH")

        self.semanticSearch = SemanticSearch(SEMSEARCH_MODEL_PATH)                     # if not downloaded, will download to path
        # self.transciberModel = Transcriber(TRANSCRIBER_MODEL_NAME, TRANSCRIBER_MODELS_PATH) # if not downloaded, will download to path
        self.segments = []
        self.passage = []

    def process(self, audio_path:str):
        self.transciberModel.stream_segment_to(audio_path, self.handle_seg)
        
        with open("segments.pkl", "rb") as f:
            self.segments = pickle.load(f)

        for seg in self.segments:
            self.handle_seg(seg)

        pos_queries = [
            # TASK SPECIFIC
            "discussing insertion sort steps",
            "explaining how insertion sort works",
            "talking about array and inserting elements in order",
            # META ACTIVITY
            "students collaborating on a programming excersise",
            "students solving an algorithm and data structures problem",
            "students analyzing an array for sorting",
            # ENVIRONMENT
            "group work in a computer science class",
            "students talking in a computer science class",
            "discussion during algorithms and data structures class",
            # VOCABULARY
            "using terms like element, array, insert, sorted, next element",
            "using numbers"
        ]

        neg_queries = [
            "casual conversation",
            "conversation unrelated to sorting algorithms",
            "students joking or chatting socially",
            "personal talk not related to algorithms"
        ]

        topic_phrases = [
            "insertion sort",
            "sorting an array",
            "algorithm steps",
            "insert element into correct position",
            "sorted subarray",
            "programming exercise",
            "computer science assignment",
            "array element comparison",
            "shift elements to make space"
            ]

        keywords = ["element", "array", "insert", "sorted", "position",
            "shift", "compare", "index", "next", "previous",
            "iteration", "pass", "key", "number", "insertion sort"]

        pos_embeds = self.semanticSearch.encode(pos_queries)
        neg_embeds = self.semanticSearch.encode(neg_queries)
        topic_vector = self.semanticSearch.topic_vec(topic_phrases)
        sentence_embeds = self.semanticSearch.encode(self.passage)

        res = self.semanticSearch.similarity(pos_embeds, sentence_embeds)
        pos_scores = self.max_score(res)

        res = self.semanticSearch.similarity(neg_embeds, sentence_embeds)
        neg_scores = self.max_score(res)
        
        res = self.semanticSearch.similarity(topic_vector, sentence_embeds)
        topic_scores = self.max_score(res)
        
        keyword_count = [sum(1 for k in keywords if k in seg["text"].lower()) for seg in self.segments]
        keyword_bonuses = [min(x * 0.05, 0.20) for x in keyword_count]

        final_scores = np.array(pos_scores) - np.array(neg_scores) + np.array(topic_scores) + np.array(keyword_bonuses)

        with open("output/scores.txt", "w", encoding="utf-8") as f:
            for i, seg in enumerate(self.segments):
                print(f"[{final_scores[i]:.4f}] << {self.segments[i]['start']:.2f} : {self.segments[i]['end']:.2f} => {self.segments[i]['text']}", file=f)
                print(f"{{ pos_score: {pos_scores[i]:.4f}, neg_score: {neg_scores[i]:.4f}, topic_score: {topic_scores[i]:.4f}, keyword_count: {keyword_count[i]} }}\n", file=f)

        # with open("output/segments.pkl", "wb") as f:
        #     pickle.dump(self.segments, f, protocol=pickle.HIGHEST_PROTOCOL)

    def handle_seg(self, seg):
        # self.segments.append(seg)
        self.passage.append(seg['text'])

    def max_score(self, tensor) -> list:
        return tensor.max(dim=0).values.tolist()

    def mean_score(self, tensor) -> list:
        return tensor.mean(dim=0).tolist()

    def weighted_max(self, tensor) -> list:
        return (0.7 * tensor.max(dim=0).values + 0.3 * tensor.mean(dim=0)).tolist()