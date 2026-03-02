from contextProcessor import ContextProcessor
from analysisParams import params
import numpy as np
import pickle

AUDIO_PATH = "Provide audio path if not using debug_skip_transcriber"
p = ContextProcessor(params)
res = p.process(AUDIO_PATH)

topics = []
with open("outputs/topics_prepared.txt", "r", encoding="utf-8") as f:
    for line in f.readlines():
        topics.append(int(line))
topics = topics[1:-1]
topics = np.array(topics).reshape(-1, 1)  # make it a column vector

res = np.hstack([res, topics])
res = res.tolist()
with open("outputs/classifier_data.pkl", "wb") as f:
    pickle.dump(res, f)