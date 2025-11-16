import os
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from semanticSearch import SemanticSearch

def main():
    load_dotenv()
    s = SemanticSearch(os.getenv("SEMSEARCH_MODEL_PATH"))
    passage = [
            "London is known for its financial district",
            "London has 9,787,426 inhabitants at the 2011 census",
            "The United Kingdom is the fourth largest exporter of goods in the world",
        ]
    query = "How big is London"

    s.encode_passage(passage)``
    s.query(query)

    passage.append("Which of these recipes contain eggs")
    s.encode_passage(passage)
    s.query("I just made an omelette")

if __name__ == "__main__":
    main()
