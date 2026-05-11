import sys


# SCORES of the characters:
# ----------------------------------------
# | 1 point  | a, e, h, i, n, o, r, s, t |
# | 2 points | c, d, l, m, u             |
# | 3 points | b, f, g, p, v, w, y       |
# | 4 points | j, k, q, x, z             |
# ----------------------------------------
SCORES = [1, 3, 2, 2, 1, 3, 3, 1, 1, 4, 4, 2, 2, 1, 1, 3, 4, 1, 1, 1, 2, 3, 3, 4, 3, 4]


# Calculate the score of a given word.
def get_score(word):
    score = 0
    for character in list(word):
        score += SCORES[ord(character) - ord('a')]
    return score


# Build the occurrence vector of characters in a given word.
def get_vector(word):
    vector = [0] * 26
    for character in list(word):
        vector[ord(character) - ord('a')] += 1
    return vector


# Read a given file and return a list of words.
def read_words(file):
    words = []
    with open(file) as file:
        for line in file:
            word = line.rstrip('\n')
            words.append(word)
    return words


# Return true if 'word_vector' can be constructed as an anagram of
# 'query_vector'.
def can_construct(word_vector, query_vector):
    for i in range(26):
        if query_vector[i] < word_vector[i]:
            return False
    return True


# Find the best score word that can be constructed as an anagram of 'query'.
# Example: if 'query' is "rlsneeesufmrsqyo" => "queensferry"
def find_best_word(words, query):
    query_vector = get_vector(query)
    for word in words:
        word_vector = get_vector(word)
        if can_construct(word_vector, query_vector):
            # Since 'words' is sorted in the reverse order of scores, the
            # first found word is guaranteed to have the best score.
            return word


# Find the set of best score words that can be constructed as an anagram of
# 'query'.
# Example: if 'query' is "rlsneeesufmrsqyo" => ["queenly", "ferms", "ross"]
def find_best_words(words, query):
    # Pre-calculate the occurrence vectors for all words
    words_vector = [get_vector(word) for word in words]
    # Pre-calculate the scores for all words
    words_score = [get_score(word) for word in words]
    
    # Store the best score
    best_score = 0
    # Store the set of words that achieve the best score
    best_answers = []

    # See the comments below
    SEARCH_THRESHOLD = 6

    # Recursive search
    # 'index': The current index in 'words'
    # 'score': The current score
    # 'answers': The set of words that achieve the score
    # 'unused_vector': The occurrence vector of unused characters
    # 'unused_characters': The number of unused characters
    def search(index, score, answers, unused_vector, unused_characters):
        nonlocal words_vector
        nonlocal words_score
        nonlocal best_score
        nonlocal best_answers

        # Update the best score
        if score > best_score:
            best_score = score
            best_answers = list(answers)
            
        # Finish searching when we found a complete anagram (i.e., the
        # theoretical best score).
        if unused_characters == 0:
            return

        count = 0
        # Start a search from 'index', instead of 0, to avoid searching
        # the same set of words.
        for i in range(index, len(words)):
            if unused_characters < len(words[i]):
                continue
            
            # If we find a word that can be constructed from 'unused_vector'
            if can_construct(words_vector[i], unused_vector):
                count += 1
                # Pruning: We search the first SEARCH_THRESHOLD words that can
                # be constructed from 'unused_vector'
                if count >= SEARCH_THRESHOLD:
                    break

                # Remove the used characters from 'unused_vector'
                new_unused_vector = [
                    unused_vector[k] - words_vector[i][k] for k in range(26)]
                answers.append(words[i])
                
                # Recursion
                search(i + 1, score + words_score[i], answers,
                       new_unused_vector, unused_characters - len(words[i]))
                answers.pop()

    # Start a recursive search
    search(0, 0, [], get_vector(query), len(query))
    return best_answers
    

# Homework #2
def find_best_word_main(word_file, dataset_file):
    words = read_words(word_file)
    # Sort the words in the reverse order of scores.
    words.sort(key=lambda word: get_score(word), reverse=True)

    queries = read_words(dataset_file)
    for query in queries:
        print(find_best_word(words, query))


# Homework #3
def find_best_words_main(word_file, dataset_file):
    words = read_words(word_file)
    # Sort the words in the reverse order of word lengths.
    # For Homework #3, this looks more effective than sorting by word scores
    # because the search space narrows down faster by selecting longer words.
    words.sort(key=lambda word: len(word), reverse=True)

    queries = read_words(dataset_file)
    for query in queries:
        print(" ".join(find_best_words(words, query)))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: %s word_file dataset_file" % sys.argv[0])
        exit(1)
    # find_best_word_main(sys.argv[1], sys.argv[2])
    find_best_words_main(sys.argv[1], sys.argv[2])
