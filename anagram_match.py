import sys

# Return a list of words in a given file.
def read_words(file):
    words = []
    with open(file) as file:
        for line in file:
            line = line.rstrip('\n')
            words.append(line)
    return words

# Sort the characters in a given string.
def sort(string):
    return ''.join(sorted(list(string)))

def main(word_file, string):
    sorted_string = sort(string)
    words = read_words(word_file)
    found = False
    for word in words:
        if word != string and sort(word) == sorted_string:
            print("Found: %s" % word)
            found = True
    if not found:
        print("Not found")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: %s word_file string" % sys.argv[0])
        exit(1)
    main(sys.argv[1], sys.argv[2])
