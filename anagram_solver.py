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


# Homework #2
#
# Find the best score word that can be constructed as an anagram of a given
# query.
#
# Example: if a query is "rlsneeesufmrsqyo" => "queensferry"
def find_best_word(word_file, dataset_file):
    words = read_words(word_file)
    # Sort the words in the reverse order of scores.
    words.sort(key=lambda word: get_score(word), reverse=True)
    word_vectors = [get_vector(word) for word in words]

    queries = read_words(dataset_file)
    for query in queries:
        query_vector = get_vector(query)
        for i in range(len(words)):
            if can_construct(word_vectors[i], query_vector):
                # Since 'words' is sorted in the reverse order of scores, the
                # first found word is guaranteed to have the best score.
                print(words[i])
                break


# Homework #3
#
# Find the set of best score words that can be constructed as an anagram of
# a given query.
#
# Example: if a query is "rlsneeesufmrsqyo" => ["queenly", "ferms", "ross"]
def find_best_words(word_file, dataset_file):
    SEARCH_THRESHOLD = 4

    # Recursive search
    # 'index': The current index in 'words'
    # 'score': The current score
    # 'answers': The set of words that achieve the score
    # 'unused_vector': The occurrence vector of unused characters
    # 'unused_characters': The number of unused characters
    def search(index, score, answers, unused_vector, unused_characters):
        nonlocal best_score, best_answers

        # Update the best score
        if score > best_score:
            best_score = score
            best_answers = list(answers)
            
        count = 0
        # Start a search from 'index', instead of 0, to avoid searching
        # the same set of words.
        for i in range(index, len(words)):
            # Skip words longer than 'unused_characters'. This optimization
            # works because we sorted words by word lengths (instead of
            # word scores).
            if unused_characters < len(words[i]):
                continue
            
            # If we find a word that can be constructed from 'unused_vector'
            if can_construct(word_vectors[i], unused_vector):
                count += 1
                # Pruning: We search the first SEARCH_THRESHOLD words that
                # can be constructed from 'unused_vector'
                if count >= SEARCH_THRESHOLD:
                    break

                # Remove the used characters from 'unused_vector'
                new_unused_vector = [
                    unused_vector[k] - word_vectors[i][k] for k in range(26)]
                answers.append(words[i])
                
                # Recursion
                search(i + 1, score + word_scores[i], answers,
                       new_unused_vector, unused_characters - len(words[i]))
                answers.pop()

                
    words = read_words(word_file)
    # Sort the words in the reverse order of word lengths.
    # For Homework #3, this is more effective than sorting by word scores
    # because the search space narrows down faster by selecting longer words.
    words.sort(key=lambda word: len(word), reverse=True)
    
    # Pre-calculate the occurrence vectors for all words
    word_vectors = [get_vector(word) for word in words]
    # Pre-calculate the scores for all words
    word_scores = [get_score(word) for word in words]

    queries = read_words(dataset_file)
    for query in queries:
        # Store the best score
        best_score = 0
        # Store the set of words that achieve the best score
        best_answers = []

        # Start a recursive search
        search(0, 0, [], get_vector(query), len(query))
        print(" ".join(best_answers))


# Homework #3 (advanced)

# SWAR (SIMD Within A Register)
BITS_PER_CHAR = 7
SIGN_MASK = sum(1 << (i * BITS_PER_CHAR + 5) for i in range(26))

# Calculate a bitmask for a given word.
def get_bitmask(word):
    bitmask = 0
    vector = [0] * 26
    for character in word:
        index = ord(character) - ord('a')
        shift = index * BITS_PER_CHAR
        bitmask += (1 << shift)
        vector[index] += 1
        assert(vector[index] < (1 << (BITS_PER_CHAR - 1)))
    return bitmask


# Return true if the word can be constructed from the query.
def can_construct_bitmask(word_bitmask, query_bitmask):
    return ((query_bitmask - word_bitmask) & SIGN_MASK) == 0


# Homework #3 (advanced)
def find_best_words_advanced(word_file, dataset_file):
    # Recursive search
    # 'index': The current index in 'words'
    # 'score': The current score
    # 'answers': The set of words that achieve the score
    # 'unused_bitmask': The bitmask of unused characters
    # 'unused_characters': The number of unused characters
    # 'unused_score': The total score of unused characters
    def search(index, score, answers,
               unused_bitmask, unused_characters, unused_score):
        nonlocal best_score, best_answers, memo, search_threshold

        # Update the best score
        if score > best_score:
            best_score = score
            best_answers = list(answers)
            
        # Finish searching when we found a complete anagram (i.e., the
        # theoretical best score).
        if unused_characters == 0:
            return

        # Finish searching if this search will not reach the best score.
        if score + unused_score <= best_score:
            return

        # Memorization
        if memo.get(unused_bitmask, -1) >= score:
            return
        memo[unused_bitmask] = score
        
        count = 0
        # Start a search from 'index', instead of 0, to avoid searching
        # the same set of words.
        for i in range(index, len(valid_words)):
            word = valid_words[i]
            
            # Skip words longer than 'unused_characters'. This optimization
            # works because we sorted words by word lengths (instead of
            # word scores).
            if unused_characters < word['length']:
                continue
            
            # If we find a word that can be constructed from 'unused_bitmask'
            if can_construct_bitmask(word['bitmask'], unused_bitmask):
                count += 1
                # Pruning: We search the first 'search_threshold' words that
                # can be constructed from 'unused_bitmask'
                if count >= search_threshold:
                    break

                # Remove the used characters from 'unused_bitmask'
                new_unused_bitmask = unused_bitmask - word['bitmask']
                answers.append(word['word'])
                
                # Recursion
                search(i + 1, score + word['score'], answers,
                       new_unused_bitmask, unused_characters - word['length'],
                       unused_score - word['score'])
                answers.pop()


    words = read_words(word_file)
    # Sort the words in the reverse order of word lengths.
    # For Homework #3, this is more effective than sorting by word scores
    # because the search space narrows down faster by selecting longer words.
    words.sort(key=lambda word: (len(word), get_score(word)), reverse=True)

    queries = read_words(dataset_file)
    for query in queries:
        query_bitmask = get_bitmask(query)
        
        # Store the best score
        best_score = 0
        # Store the set of words that achieve the best score
        best_answers = []

        # Pre-calculate a list of words that can be constructed from the query.
        # This allows us to skip searching words that cannot be constructed
        # from the query.
        valid_words = []
        for word in words:
            word_bitmask = get_bitmask(word)
            if can_construct_bitmask(word_bitmask, query_bitmask):
                valid_words.append({
                    'word': word,
                    'bitmask': word_bitmask,
                    'score': get_score(word),
                    'length': len(word)
                })

        # Iterative deepening
        for iteration in range(1, 7):
            search_threshold = 10 * iteration
            
            # Memorization
            memo = {}
            
            # Start a recursive search
            search(0, 0, [], get_bitmask(query), len(query), get_score(query))

            score = 0
            for answer in best_answers:
                score += get_score(answer)
            if score / get_score(query) > 0.95:
                break
            
        print(" ".join(best_answers))
    

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: %s word_file dataset_file" % sys.argv[0])
        exit(1)
    find_best_word(sys.argv[1], sys.argv[2])
    # find_best_words(sys.argv[1], sys.argv[2])
    # find_best_words_advanced(sys.argv[1], sys.argv[2])
