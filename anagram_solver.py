import sys

# SCORES of the characters:
# ----------------------------------------
# | 1 point  | a, e, h, i, n, o, r, s, t |
# | 2 points | c, d, l, m, u             |
# | 3 points | b, f, g, p, v, w, y       |
# | 4 points | j, k, q, x, z             |
# ----------------------------------------
SCORES = [1, 3, 2, 2, 1, 3, 3, 1, 1, 4, 4, 2, 2, 1, 1, 3, 4, 1, 1, 1, 2, 3, 3, 4, 3, 4]

# Return a list of words in a given file.
def read_words(file):
    words = []
    with open(file) as file:
        for line in file:
            line = line.rstrip('\n')
            words.append(line)
    return words

# Calculate the score of a given word.
def calculate_score(word):
    score = 0
    for character in list(word):
        score += SCORES[ord(character) - ord('a')]
    return score

# Calculate the occurrences of 'a', 'b', ... and 'z' in a given word.
def build_occurrence(word):
    occurrence = [0] * 26 # 26 characters
    for character in list(word):
        occurrence[ord(character) - ord('a')] += 1
    return occurrence

# Return true if for all characters ('a', 'b', ... and 'z'), the occurrence in
# |data_occurrence| is equal to or lager than that in |word_occurrence|.
# This means the |word| can be constructed as an anagram of the |data|.
def compare_occurrence(data_occurrence, word_occurrence):
    for i in range(26):
        if data_occurrence[i] < word_occurrence[i]:
            return False
    return True

def main(word_file, dataset_file):
    words = read_words(word_file)
    # Sort the words in the reverse order of the word length so that we can
    # search longer words first.
    words.sort(key=lambda word: calculate_score(word), reverse=True)

    # Build the character occurrences for the words.
    word_occurrences = []
    for word in words:
        word_occurrences.append(build_occurrence(word))

    dataset = read_words(dataset_file)
    for data in dataset:
        # Build the character occurrence for a given data.
        data_occurrence = build_occurrence(data)
        for index in range(len(words)):
            # Find a word that can be constructed as an anagram of the given
            # data.
            if compare_occurrence(data_occurrence, word_occurrences[index]):
                print(data, words[index])
                break

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: %s word_file dataset_file" % sys.argv[0])
        exit(1)
    main(sys.argv[1], sys.argv[2])
