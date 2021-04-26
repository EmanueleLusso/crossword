import random
import numpy as np

class Crossword(object):
    def __init__(self, cols, rows, words):
        self.cols = cols
        self.rows = rows
        self.words = words
        self.current_build = [] #All the words currently in the crossword
        self.current_build_visualizer = [[0] * cols for i in range(rows)] #A matrix of characters and 0s where 0s represent a spot without a character in it 
        self.end_build = False

    def score(self, row, col, word, horizontal): 
        curr_score = 0 # Just counts how many intersections there are. Returns NaN if the word does not fit
        if horizontal: 
            if col + len(word) > self.cols:
                return np.nan
            for i in range(len(word)):
                if self.current_build_visualizer[row][col + i] == word[i]:
                    curr_score += 1
                elif self.current_build_visualizer[row][col + i] == 0:
                    pass 
                else: 
                    return np.nan
        else:
            if row + len(word) > self.rows: 
                return np.nan
            for i in range(len(word)):
                if self.current_build_visualizer[row + i][col] == word[i]:
                    curr_score += 1
                elif self.current_build_visualizer[row + i][col] == 0:
                    pass 
                else: 
                    return np.nan
        return curr_score

    def build(self):
        while not self.end_build: 
            if len(self.current_build) == 0: #For the first word, add the longest word that fits 
                for word in self.words: 
                    if len(word[0]) <= self.cols:
                        first_word = Entry(word[0], word[1])
                        self.add(first_word, 0, 0, True)
                        self.words.remove(word)
                        break
            else: 
                for row in range(self.rows):
                    for col in range(self.cols):
                        for horizontal in [False, True]:
                            scores = np.zeros(len(self.words))
                            for i, word in enumerate(self.words): 
                                scores[i] = self.score(row, col, word[0], horizontal)
                            try:
                                i_max = np.nanargmax(scores)
                            except ValueError: 
                                continue 
                            new_word = Entry(self.words[i_max][0], self.words[i_max][1])
                            self.add(new_word, row, col, horizontal)
                            self.words.pop(i_max)
                self.end_build = True # Doesn't do anything right now but could probably use this as some sort of "timeout" break switch somewhere

    def build_simple(self):
        pass

    def add(self, entry, row, col, horizontal):
        entry.start_row = row 
        entry.start_col = col
        entry.horizontal = horizontal
        self.current_build.append(entry)
        if horizontal: 
            print('adding horizontal entry')
            self.current_build_visualizer[row][col:col + len(entry.word)-1]  = entry.word
        else: 
            print('adding vertical entry')
            for i in range(len(entry.word)):
                self.current_build_visualizer[row + i][col]  = entry.word[i]
        print(self.current_build_visualizer)

    def print_data(self):
        print("PROGRAM FINISH")
        print("-------------------------------")
        print(self.current_build_visualizer)
        for entry in self.current_build: 
            print(entry.word + ": " + entry.clue + "; At " + str(entry.start_row) + "," + str(entry.start_col) + " Horizontal = " + str(entry.horizontal))


class Entry(object): 
    def __init__(self, word=None, text=None):
        self.word = word
        self.clue = text
        self.start_row = None
        self.start_col = None
        self.horizontal = None 


def organize_words(words):
    random.shuffle(words)
    words.sort(key=lambda x: len(x[0]), reverse=True)

wordbank = [['abracadabra', 'filler'], ["apple", 'a fruit'], ['ant', 'a pest'], ['water', 'a beverage'], ['pretzel', 'a snack']]

a = Crossword(5, 5, wordbank)
a.build()
a.print_data()
