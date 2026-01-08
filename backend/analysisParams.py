AUDIO_PATH = 'recordings'
REMOVE_FILES = True

params = {
    "task_queries": [
        "discussing insertion sort steps",
        "explaining how insertion sort works",
        "talking about array and inserting elements in order"
    ],

    "meta_queries": [
        "students collaborating on a programming excersise",
        "students solving an algorithm and data structures problem",
        "students analyzing an array for sorting"
    ],

    "env_queries": [
        "group work in a computer science class",
        "students talking in a computer science class",
        "discussion during algorithms and data structures class"
    ],

    "vocab_queries": [
        "using terms like element, array, insert, sorted, next element",
        "using numbers"
    ],

    "litq_queries": [
        "How many time steps are shown?",
        "How many slots are in the input array and the output array?",
        "In each time step, how many slots are empty?",
        "What value goes into the output array first?",
        "What was that values index in the input array?",
        "What value goes into the output array second?",
        "What was that values index in the input array?",
        "What value goes into the output array last?",
        "What was that values index in the input array?",
        "Explain the sorting algorithm shown above in complete sentences.",
        "Show each step when this algorithm is applied to the array shown at right.",
        "How many time steps are shown?",
        "How many slots are in the array?",
        "In each time step, how many slots are empty?",
        "What color is used for unsorted values?",
        "What color is used for sorted values?",
        "Which value is moved from input to output first?",
        "Which value is moved from input to output last?",
        "Describe the difference between the two algorithms. Which is better?",
        "Enter the number of comparisons for each time step.",
        "Over time, does the comparison count tend to increase, decrease, or stay the same? Explain your answer.",
        "What variable stores the next value to be inserted?",
        "Which line gets the next value to be inserted?",
        "Which line inserts the value in the correct position?",
        "Which line shifts sorted values by one position?",
        "Which line controls the execution of the while loop?",
        "How many times will the for loop run?",
        "For some value of j, what is the most times the body of the while loop could run?",
        "For some value of j, what is the fewest times the body of the while loop could run?",
        "For some value of j, what is the most times the pre-test of the while loop could run?",
        "For some value of j, what is the fewest times the pre-test of the while loop could run?",
        "The array length must be a power of 2. True or false?",
        "An invalid array index can occur in some cases. True or false?",
        "Duplicate or negative data values could cause problems. True or false?",
        "Which lines run 0 times in the best case?",
        "Which lines run exactly n (or n-1) times in the best case?",
        "Which lines run more than n times in the best case?",
        "Which lines run 0 times in the worst case?",
        "Which lines run exactly n (or n-1) times in the worst case?",
        "Which lines run more than n times in the worst case?",
        "What can we say about the original array in the best case and in the worst case?",
        "What is the value of tj in the best case?",
        "What is the value of tj in the worst case?",
        "Complete the total cost T(n) expression based on the pseudocode.",
        "Explain the roles of the two last terms of T(n).",
        "Express and simplify T(n) for the best and worst case scenarios.",
        "Determine the O() and Ω() behavior of the best and worst cases.",
        "Determine the O() and Ω() behavior of the generic case for insertion sort."
    ],

    "backch_queries": [
        "yeah", "sure", "okay", "ok", "alright",
        "uh", "um", "uhm", "hmm",
        "like", "you know", "i mean",
        "maybe", "probably", "kinda", "sorta",
        "i don't know", "i dunno",
        "right", "well", "so", "anyway",
        "basically", "literally", "actually",
        "huh", "mm-hm", "uh-huh", "nah", "yep",
        "totally", "honestly"
    ],

    "neg_queries": [
        "casual social conversation",
        "jokes or unrelated chatting",
        "personal or emotional discussions",
        "topics unrelated to programming or algorithms",
        "small talk"
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
        "shift", "compare", "comparison", "index", "value", "number",
        "iteration", "pass", "key", "loop", "while", "for", "swap"
    ],
    "debug_skip_transcriber": False,
    "log_results": False,
    "save_segments_bin": False
}