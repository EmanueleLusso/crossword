from PyDictionary import PyDictionary
import random, math

dictionary = PyDictionary()

with open("google-10000-english.txt", 'r') as f:
    frequency_list = f.readlines()
    frequency_list = [word[:-1] for word in frequency_list]

with open("wordbank.txt", 'r') as f:
    wordbank = f.readlines()
    wordbank = [word.lower().rstrip() for word in wordbank]

# Converts a word's frequency (higher numerical rank = less frequent) to a score in range [0,8]. Higher index = higher score = less common word
def normalize(idx):
    normalized_idx = 2*math.log10(idx)
    return normalized_idx

write_file = open("wordbank_processed.txt", 'a')

# Converts word to the form word$word_type$definition$score. If a word has multiple definitions, a random one is chosen
for word in wordbank: 
    if len(word) < 4:
        continue
    try: 
        idx = frequency_list.index(word)
        normalized_idx = normalize(idx)
    except ValueError: 
        normalized_idx = normalize(10000)
    try:
        definitions = dictionary.meaning(word).items()
    except: 
        continue
    definition = random.choice(list(definitions))
    if len(definition[1]) == 0:
        continue
    print(definition)
    write_file.write(word + "$" + definition[0] + "$" + definition[1][0] + '$' + str(normalized_idx) + '\n') 