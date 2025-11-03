from sentence_transformers import SentenceTransformer
import os, zipfile, requests

MODEL_PATH = "models/multi-qa-mpnet-base-cos-v1"

def main():

    if not os.path.exists(MODEL_PATH):
        print("Downloading model...")
        model = SentenceTransformer("multi-qa-mpnet-base-cos-v1")
        model.save(MODEL_PATH)
        print("Download completed, model save under: "+MODEL_PATH)

    else:
        model = SentenceTransformer("models/multi-qa-mpnet-base-cos-v1")

    query_embedding = model.encode("How big is London")
    passage_embeddings = model.encode([
        "London is known for its financial district",
        "London has 9,787,426 inhabitants at the 2011 census",
        "The United Kingdom is the fourth largest exporter of goods in the world",
    ])

    similarity = model.similarity(query_embedding, passage_embeddings)
    print(similarity)


if __name__ == "__main__":
    main()
