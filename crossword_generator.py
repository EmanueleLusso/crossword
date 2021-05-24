import random
import numpy as np

crossword_size = 10
rand_factor = 95
frequency_multiplier = 1
length_multiplier = 1
position_multiplier = 1
AWL = None # average word length
LTM = 2 # length tolerance margin
potential = crossword_size*50
UCL = "qxzyjvwfg"
wordbank = [] # List of words in the wordbank in the from [word, definition, frequency ranking]


num_to_box = dict()
word_set = []

######## Debugging/Testing ############################################################################################################################################################################################
def print_out(x,flag):
    if flag: 
        print("\n**"); print(x); print("**\n")
 
p_flag = False # flag for printing
print_words = False

# hash sum of words in puzzle
def puzzle_ID(c):
    counter = 0
    for e in c:
        counter += hash(e)
    return counter

###### END Debugging/Testing ############################################################################################################################################################################################

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
            if len(word)>= (self.cols-LTM) and (random.randint(0,100) < rand_factor-100): 
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

                if (row==self.rows-1) and (self.boxes[(row-1,col+i)][3]==2):
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
            if len(word)>= (self.cols-LTM) and (random.randint(0,100) < rand_factor-100): 
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
                if (col==self.cols-1) and (self.boxes[(row+i,col-1)][2]==1 and self.boxes[(row+i,col-1)][3]==2):
                    return np.nan
                # anything in the box below the end of the word
                if (row+len(word)+1<self.cols) and self.boxes[(row+len(word),col)][0]==True:
                    return np.nan

                if (col==self.cols-1) and (self.boxes[(row+i,col-1)][3]==2):
                    return np.nan

                if self.current_build_visualizer[row + i][col] == word[i]:
                    curr_score += 1
                elif self.current_build_visualizer[row + i][col] == 0:
                    pass 
                else: 
                    return np.nan
        sub_score = curr_score
        for l in word:
            if l in UCL:
                curr_score -= sub_score+1
        return curr_score


    def build(self):
        while not self.end_build: 
            if len(self.current_build) == 0: # For the first word, add the highest-scoring word that fits 
                for word in self.wordbank: 
                    if len(word.word) <= self.cols:
                        first_word = Entry(word.word, word.type, word.clue)
                        self.add(first_word, 0, 0, True)
                        self.wordbank.remove(word)
                        break
            else: 
                for row in range(self.rows):
                    for col in range(self.cols):
                        bools = [True, False] if (random.randint(0,100) < 50) else [False, True]
                        for horizontal in bools:
                            scores = np.zeros(len(self.wordbank))
                            for i, word in enumerate(self.wordbank): 
                                scores[i] = word.points + position_multiplier*self.score(row, col, word.word, horizontal)
                            try:
                                i_max = np.nanargmax(scores)
                            except ValueError: # nanargmax returns ValueError when presented with a slice of only NaN
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
            # print('adding horizontal entry') 
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
            # print('adding vertical entry')
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
        # print(self.current_build_visualizer)


#### DISPLAY FUNCTIONS ################################################################################################# DISPLAY FUNCTIONS ###########################################################################
    # Print empty crossword board with entry numbers and word descriptions
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
            print(((rowstring+"|") if (i%2==0) else rowstring+"+"))
        print("-" * crossword_size * 4)

    # Print solution to crossword
    def print_answers(self):
        num_to_box = dict()
        word_set.clear()
        BOLD = '\033[1m'
        END_BOLD = '\033[0m'
        print(BOLD)
        print("A new puzzle is ready for you! Find it in \"puzzle.txt\"")
        print(END_BOLD)
        # print(self.current_build_visualizer) original display with lists
        for i in range(self.cols):
            s = ""
            for j in range(self.cols):
                content = str(self.current_build_visualizer[i][j]).upper()
                temp = BOLD + content + END_BOLD
                if content=="0":
                    temp = u"\u2022"
                s += temp + " "
            # print(s)
        # print("\n")
        entry_num = 0
        for entry in self.current_build:
            location = (entry.start_row, entry.start_col)
            if location not in num_to_box.keys():
                entry_num += 1
                num_to_box[location] = entry_num
            ori = " (Horizontal)" if (entry.horizontal) else " (Vertical)"
            word_set.append((entry_num, entry.horizontal, (entry.start_row,entry.start_col), entry.word.capitalize(), entry.clue))
            # print(str(entry_num) + ori + " at " +  "(" + str(entry.start_row) + "," + str(entry.start_col) + "): " + entry.word.capitalize() + ": " + entry.clue)
        hori_words = [elt for elt in word_set if elt[1]]
        vert_words = [elt for elt in word_set if not elt[1]]
        # print("Horizontal:\n")
        # for hw in hori_words:
        #     print(str(hw[0]) + " at " +  "(" + str(hw[2][0]) + "," + str(hw[2][1]) + "): " + hw[3] + ": " + hw[4])
        # print("\n")
        # print("Vertical:\n")
        # for vw in vert_words:
        #     print(str(vw[0]) + " at " +  "(" + str(vw[2][0]) + "," + str(vw[2][1]) + "): " + vw[3] + ": " + vw[4])
        # print("\n")
        
    def write_puzzle(self):
        write_file = open("puzzle.txt", 'a')
        write_file.write("######################################################################################\n")
        write_file.write("NEW PUZZLE\n")
        write_file.write("\n\n")
        BOLD = '\033[1m'
        END_BOLD = '\033[0m'
        # print(self.current_build_visualizer) original display with lists

        entry_num = 0
        across_words = []
        down_words = []
        for entry in self.current_build:
            location = (entry.start_row, entry.start_col)
            if location not in num_to_box.keys():
                entry_num += 1
                num_to_box[location] = entry_num
            if entry.horizontal: 
                across_words.append((num_to_box[location], entry))
            else:
                down_words.append((num_to_box[location], entry))

        print_string = ""
        for i in range(crossword_size):
            print_string += " ______"

        print_string += "\n"

        for i in range(crossword_size): 
            for j in range(crossword_size):
                location = (i,j)
                print_string += "|"
                if location in num_to_box.keys():
                    if num_to_box[location] < 10: 
                        print_string += str(num_to_box[location]) 
                        print_string += " "
                    else: 
                        print_string += str(num_to_box[location]) 
                else:
                    print_string += "  "
                print_string += "    "
            print_string += "|"
            print_string += "\n"
            for j in range(crossword_size):
                if self.current_build_visualizer[i][j] != 0:
                    print_string += "|      "
                else: 
                    print_string += "| XXXX "
            print_string += "|\n"
            for j in range(crossword_size):
                print_string += "|______"
            print_string += "|\n"
                    
        write_file.write(print_string)
        write_file.write("Across \n")
        for x in across_words:
            entry_num = x[0]
            entry = x[1]
            write_file.write(str(entry_num) + ": " + entry.clue + "\n")
        write_file.write("\n")

        write_file.write("Down \n")
        for x in down_words:
            entry_num = x[0]
            entry = x[1]
            write_file.write(str(entry_num) + ": " + entry.clue + "\n")
        write_file.write("\n\n\n\n")

    def write_solutions(self):
        write_file = open("puzzle_solution.txt", 'a')
        write_file.write("######################################################################################\n")
        write_file.write("NEW PUZZLE\n")
        write_file.write("\n\n")

        entry_num = 0
        across_words = []
        down_words = []
        for entry in self.current_build:
            location = (entry.start_row, entry.start_col)
            if location not in num_to_box.keys():
                entry_num += 1
                num_to_box[location] = entry_num
            if entry.horizontal: 
                across_words.append((num_to_box[location], entry))
            else:
                down_words.append((num_to_box[location], entry))
        
        print_string = ""
        for i in range(crossword_size):
            print_string += " ______"

        print_string += "\n"

        for i in range(crossword_size): 
            for j in range(crossword_size):
                location = (i,j)
                print_string += "|"
                if location in num_to_box.keys():
                    if num_to_box[location] < 10: 
                        print_string += str(num_to_box[location]) 
                        print_string += " "
                    else: 
                        print_string += str(num_to_box[location]) 
                else:
                    print_string += "  "
                print_string += "    "
            print_string += "|"
            print_string += "\n"
            for j in range(crossword_size):
                if self.current_build_visualizer[i][j] == 0:
                    print_string += "| XXXX "
                else: 
                    print_string += "|  " 
                    print_string += self.current_build_visualizer[i][j].upper()
                    print_string += "   "
            print_string += "|\n"
            for j in range(crossword_size):
                print_string += "|______"
            print_string += "|\n"
                    
        write_file.write(print_string)
        write_file.write("Across \n")
        for x in across_words:
            entry_num = x[0]
            entry = x[1]
            write_file.write(str(entry_num) + ": " + entry.word + "\n")
        write_file.write("\n")

        write_file.write("Down \n")
        for x in down_words:
            entry_num = x[0]
            entry = x[1]
            write_file.write(str(entry_num) + ": " + entry.word + "\n")
        write_file.write("\n\n\n\n")


#### END DISPLAY FUNCTIONS ############################################################################################## END DISPLAY FUNCTIONS ###########################################################################


#### CLASSES  ########################################################################################################### CLASSES ###########################################################################

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
        
#### END CLASSES  ####################################################################################################### END CLASSES ###########################################################################

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
    # wordbank.sort(key=lambda x: x.points, reverse=True)

create_wordbank()
a = Crossword(crossword_size, crossword_size, wordbank)

def reset():
    pass


print("Welcome to Crossword Puzzle Generator! Type \"exit\" to exit this game at any time.  \n")
feedback = ""
skip = False
while True: 
    num_to_box = dict()
    # print(("randfactor",rand_factor))
    # print(w.word for w in a.current_build)
    # print(puzzle_ID(w.word for w in wordbank))
    if not skip:
        # reset()
        answers = ["harder","easier","exit","same"]
        print("\n" + "-"*140)
        # print("A puzzle is ready for you, \n")
        score_words(wordbank)
        organize_words(wordbank, crossword_size)
        # print((len(wordbank),[w.word for w in wordbank]))
        a = Crossword(crossword_size, crossword_size, wordbank)
        a.build()
        # a.print_blank() 
        a.print_answers()
        a.write_puzzle()
        a.write_solutions()
        # print("avg word length: " + str(np.average([len(e[3]) for e in word_set])))
        score_fb = input("\nFinished? How was your puzzle? Rate from 1 to 10: ")
        while score_fb not in [str(i) for i in range(1,11)]:
            score_fb = (input("make sure to type your answer correctly: "))
        score_fb = int(score_fb)
        differential = 0 if (score_fb > 8) else (0.1 if score_fb > 6 else (0.2 if score_fb > 3 else (0.3)))
        feedback1 = input("\n\nWould you like to keep playing? \n\n(Type \"yes\" to continue, or \"no\" to quit): ")
        while (feedback1.lower()!="yes" and feedback1.lower()!="no"):
            feedback1 = input("make sure to type your answer correctly: ")
        if feedback1.lower()=="no":
            exit()
        feedback = input("\n\n\nWould you like a harder, easier, or equally challenging puzzle? \n\n" +
         "(Type \"harder\", \"easier\", or \"same\"): ")
    skip = False
    if feedback.lower() == answers[0]: # HARDER
        # print("HARDER") 
        frequency_multiplier *= (1.5 + differential)                          # was frequency_multiplier += 1
        length_multiplier *= (1.5 + differential)                            # was length_multiplier += 1
        rand_factor = max(10,rand_factor-20)
        LTM = max(1,LTM-1)
    elif feedback.lower() == answers[1]: # EASIER
        # print("EASIER")
        frequency_multiplier *= (0.8 - (0.6*differential))                       # was frequency_multiplier = frequency_multiplier * -1
        length_multiplier *= (0.8 - (0.6*differential))                           # was length_multiplier = length_multiplier * -1
        rand_factor = min(95, rand_factor+20)
        LTM = min(4,LTM+1)
    elif feedback.lower() == answers[2]: # EXIT
        exit()
    elif feedback.lower() == answers[3]: # SAME
        continue
    else:
        skip = True
        feedback = input("\nPlease retype your answer (you wrote: " + "\"" + feedback + "\"):  ")

# ignore for now 
box_to_num = dict()
for k in num_to_box:
    box_to_num[num_to_box[k]] = k
