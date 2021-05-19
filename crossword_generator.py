import random
import numpy as np

crossword_size = 10
frequency_multiplier = 1
length_multiplier = 1
position_multiplier = 1
# List of words in the wordbank in the from [word, definition, frequency ranking]
wordbank = []

num_to_box = dict()

class Crossword(object):
    def __init__(self, cols, rows, wordbank):
        self.cols = cols #Number of cols
        self.rows = rows #Number of rows
        self.wordbank = wordbank #List of words
        self.current_build = [] #All the words currently in the crossword
        self.current_build_visualizer = [[0] * cols for i in range(rows)] #A matrix representation of crossword. 0 represents a space
        self.end_build = False
        self.boxes = dict()
        for i in range(cols):
            for j in range(cols):
                # boxes[(i,j)]: [whether filled; word it belongs to; whether horizontal (1) or not (0) or N/A (-1); whether it is the beginning (0) or end (2) of a word (1 if inside)]
                self.boxes[(i,j)] = [False,"",-1,-1]  

    def score(self, row, col, word, horizontal): 
        curr_score = 0 #Score = how many intersections there are with existing words. Returns NaN if the word does not fit 
        # horizontal word
        if horizontal: 
            if len(word)>= (self.cols-2) and (random.randint(0,100) < 55): 
                return np.nan
            if col + len(word) > self.cols:
                return np.nan
            # anything in the box to the left
            if (col>0) and self.boxes[(row,col-1)][0]==True:
                return np.nan
            # limit density of board
            if (row>0) and (len(self.boxes[(row-1,col)][1]) >= (self.cols - 1)) and len(word) >= (self.cols-1):
                return np.nan
            for i in range(len(word)): 
                # final letter above or initial letter below belonging to a vertical word, or run into another horizontal word 
                if ((row>0) and self.boxes[(row-1,col+i)][3]==2 and self.boxes[(row-1,col+i)][2]==0) or (row+1<self.cols and self.boxes[(row+1,col+i)][3]==0 and self.boxes[(row+1,col+i)][2]==0) or (self.boxes[(row,col+i)][2]==1):
                    return np.nan
                # anything in the box after the end of the word
                if (col+len(word)+1<self.cols) and self.boxes[(row,col+len(word))][0]==True:
                    return np.nan


                if self.current_build_visualizer[row][col + i] == word[i]:
                    curr_score += 1
                elif self.current_build_visualizer[row][col + i] == 0:
                    pass 
                else:
                    print_out(self.current_build_visualizer[row][col + i],p_flag) 
                    return np.nan

        # Vertical word
        else:
            if len(word)>= (self.cols-2) and (random.randint(0,100) < 55): 
                return np.nan
            if row + len(word) > self.rows: 
                return np.nan
            # anything in the box above
            if (row>0) and self.boxes[(row-1,col)][0]==True:
                return np.nan
            # limit density of board
            if (col>0) and ((len(self.boxes[(row,col-1)][1])) >= (self.cols-1)) and (len(word) >= self.cols - 1):
                return np.nan
            if (row==0 and col>0) and self.boxes[(row,col-1)][3]==0 and self.boxes[(row,col-1)][2]==0:
                return np.nan
            for i in range(len(word)):
                # final letter to the left or initial letter to the right belonging to horizontal word, or run into another vertical word
                if ((col>0) and self.boxes[(row+i,col-1)][3]==2 and self.boxes[(row+i,col-1)][2]==1) or (col+1<self.cols and self.boxes[(row+i,col+1)][3]==0 and self.boxes[(row+i,col+1)][2]==1) or (self.boxes[(row+i,col)][2]==0):
                    return np.nan
                # anything in the box below the end of the word
                if (row+len(word)+1<self.cols) and self.boxes[(row+len(word),col)][0]==True:
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
            if len(self.current_build) == 0: #For the first word, add the highest-scoring word that fits 
                for word in self.wordbank: 
                    if len(word.word) <= self.cols:
                        first_word = Entry(word.word, word.type, word.clue)
                        self.add(first_word, 0, 0, True)
                        self.wordbank.remove(word)
                        break
            else: 
                for row in range(self.rows):
                    for col in range(self.cols):
                        for horizontal in [False, True]:
                            scores = np.zeros(len(self.wordbank))
                            for i, word in enumerate(self.wordbank): 
                                scores[i] = word.points + position_multiplier*self.score(row, col, word.word, horizontal)
                            try:
                                i_max = np.nanargmax(scores)
                            except ValueError: #nanargmax returns ValueError when presented with a slice of only NaN
                                continue 
                            ############## CHECK TO MAKE SURE THIS IS RESOLVED
                            if i_max < -1000:
                                continue
                            print_out(self.wordbank[i_max].word,p_flag)
                            print_out((row,col),p_flag)
                            new_word = Entry(self.wordbank[i_max].word, self.wordbank[i_max].type, self.wordbank[i_max].clue)
                            self.add(new_word, row, col, horizontal)
                            self.wordbank.pop(i_max)
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
                if i==0:
                    self.current_build_visualizer[row][i] = entry.word[i-col]
                    self.boxes[(row,i)] = [True,entry.word,1,0]
                elif i==(col+len(entry.word)-1):
                    self.current_build_visualizer[row][i] = entry.word[i-col]
                    self.boxes[(row,i)] = [True,entry.word,1,2]
                else:
                    self.current_build_visualizer[row][i] = entry.word[i-col]
                    self.boxes[(row,i)] = [True,entry.word,1,1]
        else: 
            print('adding vertical entry')
            for i in range(len(entry.word)):
                if i==0:
                    self.current_build_visualizer[row + i][col]  = entry.word[i]
                    self.boxes[(row+i,col)] = [True,entry.word,0,0]
                elif i==(len(entry.word)-1):
                    self.current_build_visualizer[row + i][col]  = entry.word[i]
                    self.boxes[(row+i,col)] = [True,entry.word,0,2]
                else:
                    self.current_build_visualizer[row + i][col]  = entry.word[i]
                    self.boxes[(row+i,col)] = [True,entry.word,0,1]
        print(self.current_build_visualizer)


    def print_blank(self):
        print("-" * ((crossword_size * 4) + 1))
        for i in range((crossword_size*2)-1):
            even = (i%2==0)
            rowstring = "|" if (even) else "+"
            for j in range((crossword_size*4)-1):
                if not even:
                    rowstring+= "+" if (j%4 == 3) else " "
                else:
                    rowstring+= " "
                # else: # pseudo/notes for later
                #     if itstherightindex:
                #         rowstring += that_entrynum
                #     else:
                #         rowstring+= " "
            print(((rowstring+"|") if (i%2==0) else rowstring+"+"))
        print("-" * crossword_size * 4)


    def print_answers(self):
        BOLD = '\033[1m'
        END_BOLD = '\033[0m'
        print("\nPROGRAM FINISH")
        print("-------------------------------\n")
        # print(self.current_build_visualizer) original display with lists
        for i in range(self.cols):
            s = ""
            for j in range(self.cols):
                content = str(self.current_build_visualizer[i][j]).upper()
                temp = BOLD + content + END_BOLD
                if content=="0":
                    temp = u"\u2022"
                s += temp + " "
            print(s)
        print("\n")
        entry_num = 0
        for entry in self.current_build:
            location = (entry.start_row, entry.start_col)
            if location not in num_to_box.keys():
                entry_num += 1
                num_to_box[location] = entry_num
            ori = " (Horizontal)" if (entry.horizontal) else " (Vertical)"
            print(str(entry_num) + ori + " at " +  "(" + str(entry.start_row) + "," + str(entry.start_col) + "): " + entry.word.capitalize() + ": " + entry.clue)
        print("\n")

# Class for each entry in the crossword
class WordBankEntry(object):
    def __init__(self, word, wordtype, clue, usage):
        self.word = word
        self.type = wordtype
        self.clue = clue
        self.usagefrequency = usage
        self.points = None


class Entry(object): 
    def __init__(self, word, wordtype, clue):
        self.word = word
        self.type = wordtype
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
        
def create_wordbank():
    with open("wordbank_processed.txt", 'r') as f: 
        unprocessed_word = f.readline()[:-1]
        while unprocessed_word:
            # print(unprocessed_word)
            split = unprocessed_word.split('$')
            wordbank.append(WordBankEntry(split[0], split[1], split[2], split[3]))
            unprocessed_word = f.readline()

def score_words(wordbank):
    for word in wordbank:
        word.points = length_multiplier*len(word.word) + frequency_multiplier*float(word.usagefrequency)

# shuffle before starting, remove words that will not fit in the crossword to save computation time
def organize_words(wordbank, crossword_size):
    wordbank[:] = [word for word in wordbank if len(word.word) <= crossword_size]
    random.shuffle(wordbank)
    wordbank.sort(key=lambda x: x.points, reverse=True)

create_wordbank()
if print_words:
    for word in wordbank:
        print(word.word + "; " + word.type + "; " + word.clue + "; score: " + str(word.points) +".\n")
a = Crossword(crossword_size, crossword_size, wordbank)

feedback = ""
print("Welcome to Crossword Puzzle Generator! Type \"exit\" to exit this game at any time.  \n")
while feedback != "exit": 
    print("Here's a puzzle for you: \n")
    score_words(wordbank)
    organize_words(wordbank, crossword_size)
    a.build()
    a.print_blank()
    a.print_answers()
    feedback = input("Would you like a puzzle that is harder or easier? Type \"harder\" or \"easier\" for a new puzzle or \"exit\" to exit the game.\n")
    if feedback == "harder":
        frequency_multiplier = frequency_multiplier + 1
        length_multiplier = length_multiplier + 1
    elif feedback == "easier":
        frequency_multiplier = frequency_multiplier * -1
        length_multiplier = length_multiplier * -1

# ignore for now 
box_to_num = dict()
for k in num_to_box:
    box_to_num[num_to_box[k]] = k

######## Debugging #########
def print_out(x,flag):
    if flag: 
        print("\n**"); print(x); print("**\n")
 
p_flag = False # flag for printing
print_words = False

###### END Debugging #######