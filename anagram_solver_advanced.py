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


# Homework #3 (advanced)
def find_best_words_advanced(word_file, dataset_file):
    # Recursive search
    # 'index': The current index in 'words'
    # 'score': The current score
    # 'answers': The set of words that achieve the score
    # 'unused_vector': The vector of unused characters
    # 'unused_characters': The number of unused characters
    def search(index, score, answers, unused_vector, unused_characters):
        nonlocal best_score, best_answers, memo, search_threshold

        # Update the best score
        if score > best_score:
            best_score = score
            best_answers = list(answers)
            
        # Finish searching when we found a complete anagram
        if best_score == query_score:
            return

        # Memorization
        memo_index, memo_score = memo.get(
            tuple(unused_vector), (len(valid_words), -1))
        if score <= memo_score and index >= memo_index:
            return
        if score > memo_score or (
                score == memo_score and index < memo_index):
            memo[tuple(unused_vector)] = (index, score)
        
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
            
            # If we find a word that can be constructed from 'unused_vector'
            if can_construct(word['vector'], unused_vector):
                count += 1
                # Pruning: We search the first 'search_threshold' words that
                # can be constructed from 'unused_vector'
                if count >= search_threshold:
                    break

                # Remove the used characters from 'unused_vector'
                new_unused_vector = [
                    unused_vector[k] - word["vector"][k] for k in range(26)]
                answers.append(word['word'])
                
                # Recursion
                search(i + 1, score + word['score'], answers,
                       new_unused_vector, unused_characters - word['length'])
                answers.pop()


    words = read_words(word_file)
    # Sort the words in the reverse order of word lengths.
    # For Homework #3, this is more effective than sorting by word scores
    # because the search space narrows down faster by selecting longer words.
    words.sort(key=lambda word: (len(word), get_score(word)), reverse=True)

    queries = read_words(dataset_file)
    for query in queries:
        query_score = get_score(query)
        query_vector = get_vector(query)
        
        # Store the best score
        best_score = 0
        # Store the set of words that achieve the best score
        best_answers = []

        # Pre-calculate a list of words that can be constructed from the query.
        # This allows us to skip searching words that cannot be constructed
        # from the query.
        valid_words = []
        for word in words:
            word_vector = get_vector(word)
            if can_construct(word_vector, query_vector):
                valid_words.append({
                    'word': word,
                    'vector': word_vector,
                    'score': get_score(word),
                    'length': len(word)
                })

        # Iterative deepening
        for iteration in range(1, 4):
            # Memorization
            memo = {}
            
            # Start a recursive search
            search_threshold = iteration * 20
            search(0, 0, [], query_vector, len(query))

            score = 0
            for answer in best_answers:
                score += get_score(answer)
            if score / query_score > 0.95:
                break
        # print(score / query_score)
        print(" ".join(best_answers))
    

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: %s word_file dataset_file" % sys.argv[0])
        exit(1)
    find_best_words_advanced(sys.argv[1], sys.argv[2])
