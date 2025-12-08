from contextProcessor import ContextProcessor

def main():
    AUDIO_PATH = 'audio/pogil.wav'

    params = {
        "pos_queries": [
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
        ],
        "neg_queries": [
            "casual conversation",
            "joking or chatting socially",
            "personal talk"
        ],
        "topic_phrases": [
            "insertion sort",
            "sorting an array",
            "algorithm steps",
            "insert element into correct position",
            "sorted subarray",
            "programming exercise",
            "computer science assignment",
            "array element comparison",
            "shift elements to make space"
        ],
        "keywords": [
            "element", "array", "insert", "sort", "position",
            "shift", "compare", "index", "next", "previous",
            "iteration", "pass", "key", "number", "loop", "value"
        ]
    }

    p = ContextProcessor(params)
    
    p.process(AUDIO_PATH)

if __name__ == "__main__":
    main()
