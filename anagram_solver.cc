#include <algorithm>
#include <fstream>
#include <iostream>
#include <stdio.h>
#include <string>
#include <vector>

#define ALPHABET_MAX 26

// SCORES of the characters:
// ----------------------------------------
// | 1 point  | a, e, h, i, n, o, r, s, t |
// | 2 points | c, d, l, m, u             |
// | 3 points | b, f, g, p, v, w, y       |
// | 4 points | j, k, q, x, z             |
// ----------------------------------------
int SCORES[ALPHABET_MAX] = {1, 3, 2, 2, 1, 3, 3, 1, 1, 4, 4, 2, 2, 1, 1, 3, 4, 1, 1, 1, 2, 3, 3, 4, 3, 4};

// Return a list of words in a given file.
void read_words(std::string file, std::vector<std::string>& words) {
  std::ifstream ifs(file);
  if (ifs.fail()) {
    printf("Failed to open file\n");
    exit(1);
  }
  std::string str;
  while (getline(ifs, str)) {
    words.push_back(str);
  }
}

// Calculate the score of a given word.
int calculate_score(std::string word) {
  int score = 0;
  for (int i = 0; i < word.length(); i++) {
    score += SCORES[word[i] - 'a'];
  }
  return score;
}

// Calculate the occurrences of 'a', 'b', ... and 'z' in a given word.
void build_occurrence(std::string word, std::vector<int>& occurrence) {
  for (int i = 0; i < word.length(); i++) {
    occurrence[word[i] - 'a'] += 1;
  }
}

// Return true if for all characters ('a', 'b', ... and 'z'), the occurrence in
// |data_occurrence| is equal to or lager than that in |word_occurrence|.
// This means the |word| can be constructed as an anagram of the |data|.
bool compare_occurrence(
    std::vector<int>& data_occurrence, std::vector<int>& word_occurrence) {
  for (int i = 0; i < ALPHABET_MAX; i++) {
    if (data_occurrence[i] < word_occurrence[i]) {
      return false;
    }
  }
  return true;
}

bool compare(const std::string& str1, const std::string& str2) {
  return str1.length() > str2.length();
}

int main(int argc, char** argv) {
  if (argc != 4) {
    printf("usage: %s word_file dataset_file threshold\n", argv[0]);
    exit(1);
  }
  std::string word_file = argv[1];
  std::string dataset_file = argv[2];
  int threshold = atoi(argv[3]);

  std::vector<std::string> words;
  read_words(word_file, words);
  // Sort the words in the reverse order of the word length so that we can
  // search longer words first.
  std::sort(words.begin(), words.end(), compare);

  // Build the character occurrences for the words.
  std::vector<std::vector<int>> word_occurrences;
  for (size_t i = 0; i < words.size(); i++) {
    std::vector<int> word_occurrence(ALPHABET_MAX);
    build_occurrence(words[i], word_occurrence);
    word_occurrences.push_back(word_occurrence);
  }

  std::vector<std::string> dataset;
  read_words(dataset_file, dataset);
  for (size_t i = 0; i < dataset.size(); i++) {
    // Build the character occurrence for a given data.
    std::vector<int> data_occurrence(ALPHABET_MAX);
    build_occurrence(dataset[i], data_occurrence);
    std::string best_word;
    int best_score = 0;
    int matched = 0;
    for (size_t index = 0; index < words.size(); index++) {
      // Find a word that can be constructed as an anagram of the given data.
      if (compare_occurrence(data_occurrence, word_occurrences[index])) {
        int score = calculate_score(words[index]);
        if (score > best_score) {
          best_score = score;
          best_word = words[index];
        }
        matched++;
        // For performance reasons, stop the search at some threshold.
        if (matched >= threshold) {
          break;
        }
      }
    }
    printf("%s\n", best_word.c_str());
  }
  return 0;
}
