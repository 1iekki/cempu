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

    # SETTABLE PARAMS    
    params:dict
    pos_queries:list
    neg_queries:list
    topic_phrases:list
    keywords:list
    
    # EMBED STORAGE
    pos_embeds:torch.Tensor
    neg_embeds:torch.Tensor
    topic_vector:torch.Tensor
    filler_embeds:torch.Tensor

    FILLER_WORDS = [
        "yeah", "sure", "okay", "ok", "alright",
        "uh", "um", "uhm", "hmm",
        "like", "you know", "i mean",
        "maybe", "probably", "kinda", "sorta",
        "i don't know", "i dunno",
        "right", "well", "so", "anyway",
        "basically", "literally", "actually",
        "huh", "mm-hm", "uh-huh", "nah", "yep",
        "totally", "honestly"
    ]



    def __init__(self, params:dict):
        load_dotenv()
        SEMSEARCH_MODEL_PATH = os.getenv("SEMSEARCH_MODEL_PATH")
        TRANSCRIBER_MODEL_NAME = os.getenv("TRANSCRIBER_MODEL_NAME")
        TRANSCRIBER_MODELS_PATH = os.getenv("TRANSCRIBER_MODELS_PATH")

        self.semanticSearch = SemanticSearch(SEMSEARCH_MODEL_PATH)                     # if not downloaded, will download to path
        
        if not params["debug_skip_transcriber"]:
            self.transciberModel = Transcriber(TRANSCRIBER_MODEL_NAME, TRANSCRIBER_MODELS_PATH) # if not downloaded, will download to path
        self.segments = []
        self.passage = []

        self.params = params
        self.pos_queries = params['pos_queries']
        self.neg_queries = params['neg_queries']
        self.topic_phrases = params['topic_phrases']
        self.keywords = params['keywords']

        self.pos_embeds = self.semanticSearch.encode(self.pos_queries)
        self.neg_embeds = self.semanticSearch.encode(self.neg_queries)
        self.topic_vector = self.semanticSearch.topic_vec(self.topic_phrases)
        self.filler_embeds = self.semanticSearch.encode(self.FILLER_WORDS)

        if params['debug_skip_transcriber']:
            with open("outputs/segments_large.pkl", "rb") as f:
                self.segments = pickle.load(f)

            for seg in self.segments:
                self.handle_seg(seg)


    def process(self, audio_path:str):
        if not self.params['debug_skip_transcriber']:
            self.transciberModel.stream_segment_to(audio_path, self.handle_seg)

        if self.params['remove_filler_words']:
            self.remove_fillers()

        sentence_embeds = self.semanticSearch.encode(self.passage)
        
        res = self.semanticSearch.similarity(self.pos_embeds, sentence_embeds)
        pos_scores = self.max_score(res)

        res = self.semanticSearch.similarity(self.neg_embeds, sentence_embeds)
        neg_scores = self.max_score(res)
        
        res = self.semanticSearch.similarity(self.topic_vector, sentence_embeds)
        topic_scores = self.max_score(res)

        keyword_count = [sum(1 for k in self.keywords if k in seg["text"].lower()) for seg in self.segments]
        keyword_bonuses = [min(x * 0.05, 0.20) for x in keyword_count]

        final_scores = np.array(pos_scores) - np.array(neg_scores) + np.array(topic_scores) + np.array(keyword_bonuses)

        with open("outputs/scores.txt", "w", encoding="utf-8") as f:
            for i, seg in enumerate(self.segments):
                print(f"[{final_scores[i]:.4f}] << {self.segments[i]['start']:.2f} : {self.segments[i]['end']:.2f} => {self.segments[i]['text']}", file=f)
                print(f"{{ pos_score: {pos_scores[i]:.4f}, neg_score: {neg_scores[i]:.4f}, topic_score: {topic_scores[i]:.4f}, keyword_count: {keyword_count[i]} }}\n", file=f)
            for i, seg in enumerate(self.removed):
                print(f"{seg['start']:.2f} : {seg['end']:.2f} => {seg['text']}", file=f)
            

        # with open("output/segments.pkl", "wb") as f:
        #     pickle.dump(self.segments, f, protocol=pickle.HIGHEST_PROTOCOL)

    def handle_seg(self, seg):
        self.passage.append(seg['text'])
        if self.params['debug_skip_transcriber']:
            return
        
        self.segments.append(seg)

    def max_score(self, tensor) -> list:
        return tensor.max(dim=0).values.tolist()

    def mean_score(self, tensor) -> list:
        return tensor.mean(dim=0).tolist()

    def weighted_max(self, tensor) -> list:
        return (0.7 * tensor.max(dim=0).values + 0.3 * tensor.mean(dim=0)).tolist()
    
    def remove_fillers(self):
        passage_enc = self.semanticSearch.encode(self.passage)
        s = self.semanticSearch.similarity(self.filler_embeds, passage_enc)
        max_s = self.max_score(s)
        remove = []
        for i, value in enumerate(max_s):
            if value > 0.7:
                remove.append(i)
        self.removed = [v for i, v in enumerate(self.segments) if i in remove]
        self.passage = [v for i, v in enumerate(self.passage) if i not in remove]
        self.segments = [v for i, v in enumerate(self.segments) if i not in remove]
        