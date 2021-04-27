import random
import numpy as np

class Crossword(object):
    def __init__(self, cols, rows, words):
        self.cols = cols #Number of cols
        self.rows = rows #Number of rows
        self.words = words #List of words
        self.current_build = [] #All the words currently in the crossword
        self.current_build_visualizer = [[0] * cols for i in range(rows)] #A matrix representation of crossword. 0 represents a space
        self.end_build = False
        self.boxes = dict()
        for i in range(cols):
            for j in range(cols):
                # boxes[(i,j)]: [whether filled; word it belongs to; whether horizontal (1) or not (0) or N/A (-1); whether it is the end of a word]
                self.boxes[(i,j)] = [False,"",-1,False]  

    def score(self, row, col, word, horizontal): 
        curr_score = 0 #Score = how many intersections there are with existing words. Returns NaN if the word does not fit 
        if horizontal: 
            if col + len(word) > self.cols:
                return np.nan
            for i in range(len(word)):
                if (row>0) and self.boxes[(row-1,col)][0]==True:
                    return np.nan
                if (col>0) and self.boxes[(row,col-1)][0]==True: 
                    return np.nan
                # if there's a final letter from horiz word 
                if (self.boxes[(row,col+i)][2]==1) and (self.boxes[(row,col+i)][3]==True):
                    return np.nan
                if self.current_build_visualizer[row][col + i] == word[i]:
                    curr_score += 1
                elif self.current_build_visualizer[row][col + i] == 0:
                    pass 
                else:
                    print_out(self.current_build_visualizer[row][col + i],p_flag) 
                    return np.nan
        else:
            if row + len(word) > self.rows: 
                return np.nan
            for i in range(len(word)):
                if (row>0) and self.boxes[(row-1,col)][0]==True:
                    return np.nan
                if (col>0) and self.boxes[(row+i,col-1)][0]==True: 
                    return np.nan
                # if there's a final letter from vertical word 
                if (self.boxes[(row+i,col)][2]==0) and (self.boxes[(row+i,col)][3]==True):
                    print_out((word,entry.word),p_flag)
                    return np.nan
                if self.current_build_visualizer[row + i][col] == word[i]:
                    curr_score += 1
                elif self.current_build_visualizer[row + i][col] == 0:
                    pass 
                else: 
                    return np.nan
        return curr_score

    def build(self):
        print_out(self.current_build_visualizer,p_flag)
        print_out("enter build",p_flag)
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
                            except ValueError: #nanargmax returns ValueError when presented with a slice of only NaN
                                continue 
                            ############## CHECK TO MAKE SURE THIS IS RESOLVED
                            if i_max < -1000:
                                continue
                            print_out(self.words[i_max][0],p_flag)
                            print_out((row,col),p_flag)
                            new_word = Entry(self.words[i_max][0], self.words[i_max][1])
                            self.add(new_word, row, col, horizontal)
                            self.words.pop(i_max)
                self.end_build = True # Doesn't really do anything right now but could probably use this as some sort of "timeout" break switch somewhere

    #Add an entry to the board
    def add(self, entry, row, col, horizontal):
        entry.start_row = row 
        entry.start_col = col
        entry.horizontal = horizontal
        self.current_build.append(entry)
        #Add entry to visualizer
        if horizontal: 
            print('adding horizontal entry')
            for i in range(col,col+len(entry.word)):
                if i==(col+len(entry.word)-1):
                    self.current_build_visualizer[row][i] = entry.word[i-col]
                    self.boxes[(row,i)] = [True,entry.word,1,True]
                else:
                    self.current_build_visualizer[row][i] = entry.word[i-col]
                    self.boxes[(row,i)] = [True,entry.word,1,False]
            # self.current_build_visualizer[row][col:(col+len(entry.word))]  = entry.word
        else: 
            print('adding vertical entry')
            for i in range(len(entry.word)):
                if i==(len(entry.word)-1):
                    self.current_build_visualizer[row + i][col]  = entry.word[i]
                    self.boxes[(row+i,col)] = [True,entry.word,0,True]
                else:
                    self.current_build_visualizer[row + i][col]  = entry.word[i]
                    self.boxes[(row+i,col)] = [True,entry.word,0,False]
        print(self.current_build_visualizer)

    def print_data(self):
        print("\nPROGRAM FINISH")
        print("-------------------------------\n")
        # print(self.current_build_visualizer) original display with lists
        for i in range(self.cols):
            s = ""
            for j in range(self.cols):
                temp = str(self.current_build_visualizer[i][j]).upper() +" "
                if temp[0]=="0":
                    temp = u"\u2022 "
                s += temp
            print(s)
        print("\n")
        for entry in self.current_build: 
            print(entry.word + ": " + entry.clue + "; At " + str(entry.start_row) + "," + str(entry.start_col) + " Horizontal = " + str(entry.horizontal))
        print("\n")

# Class for each entry in the crossword
class Entry(object): 
    def __init__(self, word, clue):
        self.word = word
        self.clue = clue
        self.start_row = None
        self.start_col = None
        self.horizontal = None 
        self.is_intersecting = None

# Class for each square on the board
class Square(object):
    def __init__(self):
        self.filled = None
        self.word = None
        self.horizontal = None 
        self.final = None

# shuffle before starting, remove words that will not fit in the crossword to save computation time
def organize_words(words, crossword_size):
    words[:] = [word for word in words if len(word[0]) <= crossword_size]
    random.shuffle(words)
    words.sort(key=lambda x: len(x[0]), reverse=True)

wordbank = [['abracadabra', 'filler'], ["apple", 'a fruit'], ['ant', 'a pest'], ['task', 'something to do'], ['water', 'a beverage'], ['pretzel', 'a snack']]
crossword_size = 7

######## Debugging #########

def print_out(x,flag):
    if flag: 
        print("\n**"); print(x); print("**\n")
 
p_flag = False # flag for printing

###### END Debugging #######

organize_words(wordbank, crossword_size)
a = Crossword(crossword_size, crossword_size, wordbank)
a.build()
a.print_data()