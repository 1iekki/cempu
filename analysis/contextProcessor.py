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
    task_q:list
    meta_q:list
    env_q:list
    vocab_q:list
    litq_q:list
    backch_q:list
    neg_q:list
    topic_phrases:list
    keywords:list
    
    # EMBED STORAGE
    task_embeds:torch.Tensor
    meta_embeds:torch.Tensor
    env_embeds:torch.Tensor
    vocab_embeds:torch.Tensor
    litq_embeds:torch.Tensor
    backch_embeds:torch.Tensor
    neg_embeds:torch.Tensor
    topic_vector:torch.Tensor

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
        self.task_q = params['task_queries']
        self.meta_q = params['meta_queries']
        self.env_q = params['env_queries']
        self.vocab_q = params['vocab_queries']
        self.litq_q = params['litq_queries']
        self.backch_q = params['backch_queries']
        self.neg_q = params['neg_queries']
        self.topic_phrases = params['topic_phrases']
        self.keywords = params['keywords']

        self.task_embeds = self.semanticSearch.encode(self.task_q)
        self.meta_embeds = self.semanticSearch.encode(self.meta_q)
        self.env_embeds = self.semanticSearch.encode(self.env_q)
        self.vocab_embeds = self.semanticSearch.encode(self.vocab_q)
        self.litq_embeds = self.semanticSearch.encode(self.litq_q)
        self.backch_embeds = self.semanticSearch.encode(self.backch_q)
        self.neg_embeds = self.semanticSearch.encode(self.neg_q)
        self.topic_vector = self.semanticSearch.topic_vec(self.topic_phrases)
        
        if params['debug_skip_transcriber']:
            with open("outputs/segments.pkl", "rb") as f:
                self.segments = pickle.load(f)

            for seg in self.segments:
                self.passage.append(seg['text'])


    def process(self, audio_path:str) -> np.ndarray:
        if not self.params['debug_skip_transcriber']:
            self.transciberModel.stream_segment_to(audio_path, self.handle_seg)

        sentence_embeds = self.semanticSearch.encode(self.passage)

        res = self.semanticSearch.similarity(self.task_embeds, sentence_embeds)
        task_scores = self.max_score(res)

        res = self.semanticSearch.similarity(self.meta_embeds, sentence_embeds)
        meta_scores = self.max_score(res)

        res = self.semanticSearch.similarity(self.env_embeds, sentence_embeds)
        env_scores = self.max_score(res)

        res = self.semanticSearch.similarity(self.vocab_embeds, sentence_embeds)
        vocab_scores = self.max_score(res)

        res = self.semanticSearch.similarity(self.litq_embeds, sentence_embeds)
        litq_scores = self.max_score(res)

        res = self.semanticSearch.similarity(self.backch_embeds, sentence_embeds)
        backch_scores = self.max_score(res)

        res = self.semanticSearch.similarity(self.neg_embeds, sentence_embeds)
        neg_scores = self.max_score(res)
        
        res = self.semanticSearch.similarity(self.topic_vector, sentence_embeds)
        topic_scores = self.max_score(res)

        keyword_count = [sum(1 for k in self.keywords if k in seg["text"].lower()) for seg in self.segments]

        prev_list = []
        next_list = []

        for i in range(1, len(sentence_embeds) - 1):

            prev_list.append([
                self.semanticSearch.similarity(sentence_embeds[i], sentence_embeds[i - 1]).item(),
                task_scores[i - 1],
                meta_scores[i - 1],
                env_scores[i - 1],
                vocab_scores[i - 1],
                litq_scores[i - 1],
                backch_scores[i - 1],
                neg_scores[i - 1],
                topic_scores[i - 1],
                keyword_count[i - 1],
            ])

            next_list.append([
                self.semanticSearch.similarity(sentence_embeds[i], sentence_embeds[i + 1]).item(),
                task_scores[i + 1],
                meta_scores[i + 1],
                env_scores[i + 1],
                vocab_scores[i + 1],
                litq_scores[i + 1],
                backch_scores[i + 1],
                neg_scores[i + 1],
                topic_scores[i + 1],
                keyword_count[i + 1],
            ])

        prev_matrix = np.array(prev_list)
        next_matrix = np.array(next_list)

        scores_matrix = np.column_stack([
            task_scores,
            meta_scores,
            env_scores,
            vocab_scores,
            litq_scores,
            backch_scores,
            neg_scores,
            topic_scores,
            keyword_count,
        ])[1:-1]

        final_matrix = np.hstack([
            scores_matrix,
            prev_matrix,
            next_matrix
        ])

        if self.params['log_results']:
            with open("outputs/scores.txt", "w", encoding="utf-8") as f:
                print("SENTENCE SCORES", file=f)
                for i, seg in enumerate(self.segments):
                    print(f"[{i}] << {seg['start']:.2f} : {seg['end']:.2f} => {seg['text']}", file=f)
                
                print("RESULTS:", file=f)
                print("task, meta, env, vocab, litq, backch, prev, prev_task, prev_meta, prev_env, prev_vocab, prev_litq, prev_backch, next, next_task, next_meta, next_env, next_vocab, next_litq, next_backch", file=f)
                for i in range(len(final_matrix)):
                    print(final_matrix[i], file=f)

        if self.params['save_segments_bin']:
            with open("outputs/segments.pkl", "wb") as f:
                pickle.dump(self.segments, f, protocol=pickle.HIGHEST_PROTOCOL)


        return final_matrix

    def handle_seg(self, seg):
        self.passage.append(seg['text'])
        self.segments.append(seg)

    def max_score(self, tensor) -> np.ndarray:
        return tensor.max(dim=0).values.numpy()

    def mean_score(self, tensor) -> np.ndarray:
        return tensor.mean(dim=0).numpy()

    def weighted_max(self, tensor) -> np.ndarray:
        return (0.7 * tensor.max(dim=0).values + 0.3 * tensor.mean(dim=0)).numpy()
    

    def z_score_norm(self, arr: np.ndarray) -> np.ndarray:
        mean = arr.mean()
        std = arr.std() + 1e-9
        z = (arr - mean) / std
        return (z - z.min()) / (z.max() - z.min())