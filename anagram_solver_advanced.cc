#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <algorithm>
#include <unordered_map>

// SCORES of the characters:
// ----------------------------------------
// | 1 point  | a, e, h, i, n, o, r, s, t |
// | 2 points | c, d, l, m, u             |
// | 3 points | b, f, g, p, v, w, y       |
// | 4 points | j, k, q, x, z             |
// ----------------------------------------
const int SCORES[26] = {1, 3, 2, 2, 1, 3, 3, 1, 1, 4, 4, 2, 2, 1, 1, 3, 4, 1, 1, 1, 2, 3, 3, 4, 3, 4};

// Calculate the score of a given word.
int get_score(const std::string& word) {
    int score = 0;
    for (char character : word) {
        score += SCORES[character - 'a'];
    }
    return score;
}

// Build the occurrence vector of characters in a given word.
std::vector<int> get_vector(const std::string& word) {
    std::vector<int> vector(26, 0);
    for (char character : word) {
        vector[character - 'a'] += 1;
    }
    return vector;
}

// Read a given file and return a list of words.
std::vector<std::string> read_words(const std::string& filename) {
    std::vector<std::string> words;
    std::ifstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Error: Cannot open file " << filename << "\n";
        exit(1);
    }
    std::string line;
    while (std::getline(file, line)) {
        // Handle Windows CRLF correctly
        if (!line.empty() && line.back() == '\r') {
            line.pop_back();
        }
        words.push_back(line);
    }
    return words;
}

// Return true if 'word_vector' can be constructed as an anagram of
// 'query_vector'.
bool can_construct(const std::vector<int>& word_vector, const std::vector<int>& query_vector) {
    for (int i = 0; i < 26; ++i) {
        if (query_vector[i] < word_vector[i]) {
            return false;
        }
    }
    return true;
}

// Helper structure to store pre-calculated valid words
struct ValidWord {
    std::string word;
    std::vector<int> vector;
    int score;
    int length;
};

// Custom Hash function for using std::vector<int> as a key in std::unordered_map
struct VectorHash {
    std::size_t operator()(const std::vector<int>& v) const {
        std::size_t seed = v.size();
        for (int i : v) {
            seed ^= i + 0x9e3779b9 + (seed << 6) + (seed >> 2);
        }
        return seed;
    }
};

// Homework #3 (advanced)
void find_best_words_advanced(const std::string& word_file, const std::string& dataset_file) {
    std::vector<std::string> words = read_words(word_file);
    
    // Sort the words in the reverse order of word lengths.
    // For Homework #3, this is more effective than sorting by word scores
    // because the search space narrows down faster by selecting longer words.
    std::sort(words.begin(), words.end(), [](const std::string& a, const std::string& b) {
        if (a.length() != b.length()) {
            return a.length() > b.length();
        }
        return get_score(a) > get_score(b);
    });

    std::vector<std::string> queries = read_words(dataset_file);
    for (const auto& query : queries) {
        int query_score = get_score(query);
        std::vector<int> query_vector = get_vector(query);
        
        // Store the best score
        int best_score = 0;
        // Store the set of words that achieve the best score
        std::vector<std::string> best_answers;

        // Pre-calculate a list of words that can be constructed from the query.
        // This allows us to skip searching words that cannot be constructed
        // from the query.
        std::vector<ValidWord> valid_words;
        for (const auto& word : words) {
            std::vector<int> word_vector = get_vector(word);
            if (can_construct(word_vector, query_vector)) {
                valid_words.push_back({
                    word,
                    word_vector,
                    get_score(word),
                    static_cast<int>(word.length())
                });
            }
        }

        // Iterative deepening
        for (int iteration = 1; iteration < 4; ++iteration) {
            // Memorization
            // Map: unused_vector -> pair<index, score>
            std::unordered_map<std::vector<int>, std::pair<int, int>, VectorHash> memo;
            
            // Start a recursive search
            int search_threshold = iteration * 20;

            // Recursive search
            // 'index': The current index in 'words'
            // 'score': The current score
            // 'answers': The set of words that achieve the score
            // 'unused_vector': The vector of unused characters
            // 'unused_characters': The number of unused characters
            auto search = [&](auto& self, int index, int score, std::vector<std::string>& answers,
                              const std::vector<int>& unused_vector, int unused_characters) -> void {
                
                // Update the best score
                if (score > best_score) {
                    best_score = score;
                    best_answers = answers;
                }
                
                // Finish searching when we found a complete anagram
                if (best_score == query_score) {
                    return;
                }

                // Memorization
                int memo_index = static_cast<int>(valid_words.size());
                int memo_score = -1;
                auto it = memo.find(unused_vector);
                if (it != memo.end()) {
                    memo_index = it->second.first;
                    memo_score = it->second.second;
                }

                if (score <= memo_score && index >= memo_index) {
                    return;
                }
                if (score > memo_score || (score == memo_score && index < memo_index)) {
                    memo[unused_vector] = {index, score};
                }
                
                int count = 0;
                // Start a search from 'index', instead of 0, to avoid searching
                // the same set of words.
                for (int i = index; i < static_cast<int>(valid_words.size()); ++i) {
                    const auto& word = valid_words[i];
                    
                    // Skip words longer than 'unused_characters'.
                    if (unused_characters < word.length) {
                        continue;
                    }
                    
                    // If we find a word that can be constructed from 'unused_vector'
                    if (can_construct(word.vector, unused_vector)) {
                        count += 1;
                        // Pruning: We search the first 'search_threshold' words that
                        // can be constructed from 'unused_vector'
                        if (count >= search_threshold) {
                            break;
                        }

                        // Remove the used characters from 'unused_vector'
                        std::vector<int> new_unused_vector(26);
                        for (int k = 0; k < 26; ++k) {
                            new_unused_vector[k] = unused_vector[k] - word.vector[k];
                        }
                        
                        answers.push_back(word.word);
                        
                        // Recursion
                        self(self, i + 1, score + word.score, answers,
                             new_unused_vector, unused_characters - word.length);
                        
                        answers.pop_back();
                    }
                }
            };

            std::vector<std::string> current_answers;
            search(search, 0, 0, current_answers, query_vector, static_cast<int>(query.length()));

            int iteration_score = 0;
            for (const auto& answer : best_answers) {
                iteration_score += get_score(answer);
            }
            if (static_cast<double>(iteration_score) / query_score > 0.95) {
                break;
            }
        }
        
        // print(score / query_score)
        for (size_t i = 0; i < best_answers.size(); ++i) {
            std::cout << best_answers[i] << (i + 1 == best_answers.size() ? "" : " ");
        }
        std::cout << std::endl;
    }
}

int main(int argc, char* argv[]) {
    // Optimize standard I/O operations for speed
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);

    if (argc != 3) {
        std::cerr << "usage: " << argv[0] << " word_file dataset_file\n";
        return 1;
    }
    
    find_best_words_advanced(argv[1], argv[2]);
    
    return 0;
}
