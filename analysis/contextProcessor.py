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
            self.passage = [
                "Is the microphone on?",
                "Yeah, the red light is blinking",
                "Okay, sweet",
                "So we are doing the insertion sort trace?",
                "Yeah, question number three",
                "Do we have the array values?",
                "Scroll down a bit",
                "More",
                "Stop, right there",
                "Okay, so it's 5, 2, 9, 1, 5",
                "Two fives?",
                "Yeah, probably to test stability",
                "Oh god, I hate stability questions",
                "It's fine, just keep track of the indices",
                "Okay, so first pass",
                "Index 0 is sorted effectively, right?",
                "Yeah, start at index 1",
                "So we take the 2",
                "Compare 2 with 5",
                "2 is smaller, so we swap",
                "Or shift?",
                "The code says swap",
                "No, look at line 4",
                "It's a shift assignment",
                "Ah, true",
                "Did you guys see the email from Professor Klein?",
                "About the midterm?",
                "Yeah",
                "No, what did it say?",
                "He moved it to Monday",
                "You're joking",
                "I wish I was",
                "Bro, I have a physics lab on Monday",
                "That sucks",
                "Anyway, back to the array",
                "So array is now 2, 5, 9, 1, 5",
                "Right",
                "Next iteration, i equals 2",
                "Element is 9",
                "Compare 9 with 5",
                "It's greater",
                "So do nothing?",
                "Yeah, the while loop condition fails",
                "Wait, does it check 2 as well?",
                "No, it breaks immediately",
                "Optimizations, baby",
                "Haha, okay",
                "So the array doesn't change",
                "Still 2, 5, 9, 1, 5",
                "Next i is 3",
                "The value is 1",
                "Oof, this is gonna go all the way back",
                "Yeah, worst case scenario for this element",
                "Man, I'm hungry",
                "Same",
                "Did you eat at the cafeteria?",
                "No, the line was huge",
                "They had those tacos today",
                "The soggy ones?",
                "Hey, they're not that bad if you put enough hot sauce",
                "Disgusting",
                "Focus, guys",
                "Value 1",
                "Compare with 9",
                "Shift 9",
                "Compare with 5",
                "Shift 5",
                "Compare with 2",
                "Shift 2",
                "Insert 1 at index 0",
                "So now it's 1, 2, 5, 9, 5",
                "Yes",
                "Wait",
                "What?",
                "Did we mess up the indices?",
                "I don't think so",
                "No, looks right",
                "Okay, last element",
                "The second 5",
                "This is the interesting part",
                "Compare with 9",
                "Shift 9",
                "Compare with the first 5",
                "It is not smaller",
                "Is it strictly less than?",
                "Let me check the code snippet",
                "Where is the paper?",
                "Under your laptop",
                "Oh, thanks",
                "It says while a[j] > key",
                "Okay so strictly greater",
                "So 5 is not greater than 5",
                "So we stop",
                "And insert after the first 5",
                "Stability preserved!",
                "Nice",
                "We are geniuses",
                "Speak for yourself",
                "I'm totally failing this class",
                "Don't say that",
                "No seriously, I got a 40 on the quiz",
                "The one about recursion?",
                "Yeah, I forgot the base case",
                "Infinite loop?",
                "Stack overflow in my brain",
                "Hahaha",
                "That's rough buddy",
                "Okay, are we done with part A?",
                "Yeah, write down the final array",
                "1, 2, 5, 5, 9",
                "Got it",
                "Now part B",
                "\"How many comparisons were made?\"",
                "Oh no, we have to count them?",
                "We should have tallied them as we went",
                "Rookie mistake",
                "Let's retrace",
                "Pass 1: 2 vs 5. That's one.",
                "Pass 2: 9 vs 5. That's one.",
                "Pass 3: 1 vs 9, 1 vs 5, 1 vs 2. That's three.",
                "Wait, does it check against index -1?",
                "No, the loop condition handles the boundary",
                "Depends on the implementation",
                "Look at line 3 again",
                "j >= 0 comes first",
                "Short circuit evaluation",
                "So it checks indices, then value",
                "So no extra value comparison",
                "Right, so just three comparisons for that pass",
                "Okay, so 1 + 1 + 3",
                "And the last pass",
                "5 vs 9, and 5 vs 5",
                "That's two",
                "So total is...",
                "Seven?",
                "1, 2, 5, 7. Yeah.",
                "Does anyone have a calculator?",
                "To add single digits?",
                "Listen, my brain is fried",
                "I stayed up till 4am playing Valorant",
                "Why would you do that?",
                "Ranked climb, bro",
                "Did you win?",
                "I lost 300 RR",
                "tragic",
                "absolutely tragic",
                "Back to sorting, please",
                "I want to go home",
                "Okay, Part C",
                "\"What is the worst case time complexity?\"",
                "Oh that's easy",
                "O(n squared)",
                "Do we need to prove it?",
                "Just say \"nested loops\"",
                "And \"reverse sorted input\"",
                "Yeah write that down",
                "Reverse sorted input causes maximum swaps",
                "Maximum comparisons too",
                "Are we supposed to draw the graph?",
                "It says \"explain briefly\"",
                "No graphs",
                "Thank god, I don't have a ruler",
                "You don't need a ruler for a sketch",
                "I like my lines straight",
                "Weirdo",
                "Hey, is that Sarah over there?",
                "Where?",
                "By the vending machine",
                "Oh yeah",
                "She still has my hoodie",
                "Go get it",
                "Nah, we're recording",
                "Prioritizing the group work, I respect it",
                "Also I'm scared of her",
                "Fair enough",
                "Okay, last question",
                "\"Is this algorithm in-place?\"",
                "Yes",
                "Why?",
                "Because we didn't make a new array",
                "We just moved stuff around in the original",
                "Constant extra space",
                "Just the key variable",
                "And the iterator i and j",
                "So O(1) space",
                "Perfect",
                "Write that down",
                "\"Yes, O(1) auxiliary space\"",
                "Do you think he'll dock points for handwriting?",
                "Yours is terrible",
                "Shut up, it's artistic",
                "It looks like a chicken walked on the paper",
                "A chicken that knows insertion sort",
                "Okay, are we done?",
                "Think so",
                "Don't forget to put our names at the top",
                "Oh right",
                "Team 4",
                "Is that it?",
                "Yeah, hitting stop on the recording now"
            ]

            # with open("outputs/segments.pkl", "rb") as f:
            #     self.segments = pickle.load(f)

            # for seg in self.segments:
            #     self.passage.append(seg['text'])


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

        keyword_count = [sum(1 for k in self.keywords if k in sent.lower()) for sent in self.passage]

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