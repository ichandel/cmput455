# CMPUT 455 Assignment 1 starter code
# Implement the specified commands to complete the assignment
# Full assignment specification on Canvas

import random
import sys

class CommandInterface:
    # The following is already defined and does not need modification
    # However, you may change or add to this code as you see fit, e.g. adding class variables to init

    def __init__(self):
        # Define the string to function command mapping
        self.command_dict = {
            "help" : self.help,
            "init_game" : self.init_game,
            "legal" : self.legal,
            "play" : self.play,
            "genmove" : self.genmove,
            "undo" : self.undo,
            "score" : self.score,
            "winner" : self.winner,
            "show" : self.show,
        }

    # Convert a raw string to a command and a list of arguments
    def process_command(self, string):
        string = string.lower().strip()
        command = string.split(" ")[0]
        args = [x for x in string.split(" ")[1:] if len(x) > 0]
        if command not in self.command_dict:
            print("? Uknown command.\nType 'help' to list known commands.", file=sys.stderr)
            print("= -1\n")
            return False
        try:
            return self.command_dict[command](args)
        except Exception as e:
            print("Command '" + string + "' failed with exception:", file=sys.stderr)
            print(e, file=sys.stderr)
            print("= -1\n")
            return False
        
    # Will continuously receive and execute commands
    # Commands should return True on success, and False on failure
    # Commands will automatically print '= 1' at the end of execution on success
    def main_loop(self):
        while True:
            string = input()
            if string.split(" ")[0] == "exit":
                print("= 1\n")
                return True
            if self.process_command(string):
                print("= 1\n")

    # List available commands
    def help(self, args):
        for command in self.command_dict:
            if command != "help":
                print(command)
        print("exit")
        return True

    #======================================================================================
    # End of predefined functionality. You will need to implement the following functions.
    # Arguments are given as a list of strings
    # We will only test error handling of the play command
    #======================================================================================

    def init_game(self, args):
        '''
            >> init_game <num_cols> <num_rows> <handicap> <score_cutoff>
            Initializes the game board with the dimension (<num_cols>, <num_rows>).
            Sets the handicap for the second player as <handicap>.
            Sets the winning score as <score_cutoff>.
        '''

        # check for correct number of arguments
        if len(args) != 4:
            print("init_game requires 4 arguments.", file=sys.stderr)
            raise Exception("init_game requires 4 arguments.")

        # parse arguments
        nc = int(args[0])
        nr = int(args[1])
        h = float(args[2])
        sc = float(args[3])  # check if this is nonnegative 

        # set class variables
        self.num_cols = nc
        self.num_rows = nr
        self.handicap = h
        self.score_cutoff = sc

        self.p1score = 0
        self.p2score = h
        

        self.current_player = "1"  # player 1 starts
        self.moves = []  # list of moves played

        self.board = [["_"] * self.num_cols for _ in range(self.num_rows)]  # Initialize empty board
        return True
    
    def legal(self, args):
        '''
            >> legal <col> <row>
            Checks if the current player can play at position (<col>, <row>) on the board.
        '''

        # check for correct number of arguments
        if len(args) != 2:
            print("legal requires 2 arguments.", file=sys.stderr)
            raise Exception("legal requires 2 arguments.")
        
        col = int(args[0])
        row = int(args[1])
        
        if self.check_legal([col, row]):  # check if the move is legal
            print("yes")
        else:
            print("no")
        return True
    
    def check_legal(self, args):

        
        col = int(args[0])
        row = int(args[1])

        if not self.in_bounds(col, row):  # check if the move is in bounds
            return False
        
        # check if the game has already been won
        if self.score_cutoff > 0:
            self.calculate_score()
            if (self.p1score >= self.score_cutoff or self.p2score >= self.score_cutoff):
                return False
            
        return self.board[row][col] == "_"  # check if the cell is empty

    def play(self, args):
        '''
            >> play <col> <row>
            Places the current player's piece at position (<col>, <row>). Check if the move is legal before playing it.
        '''
        
        # check for correct number of arguments
        if len(args) != 2:
            print("play requires 2 arguments.", file=sys.stderr)
            raise Exception("play requires 2 arguments.")
                
        col = int(args[0]) # column
        row = int(args[1]) # row

        if not self.check_legal(args):  # check if the move is legal
            raise Exception("Illegal move.")
        
        # play the move
        self.board[row][col] = self.current_player
        self.current_player = "2" if self.current_player == "1" else "1"  # switch players
        
        self.moves.append((col, row))  # add move to move list

        return True
    
    def in_bounds(self, col, row):
        return 0 <= col < self.num_cols and 0 <= row < self.num_rows  # check if the move is in bounds
        
    def genmove(self, args):
        '''
            >> genmove
            Generates and plays a random valid move.
        '''
        
        # check if the board is full, if so resign
        if self.check_filled():
            print("resign")
            return True
        
        # check if the game has already been won, if so resign again
        if self.score_cutoff > 0:
            self.calculate_score()
            if (self.p1score >= self.score_cutoff or self.p2score >= self.score_cutoff):
                print("resign")
                return True
        
        # since board is not full, generate random moves until a legal one is found
        while True:
            row = random.randint(0, self.num_rows - 1)
            col = random.randint(0, self.num_cols - 1)
            if self.check_legal([col, row]):
                print(col, row)  # print the move
                self.play([col, row])
                return True

    def undo(self, args):
        '''
            >> undo
            Undoes the last move.
        '''
        
        # check if there are moves to undo, if not raise exception
        if len(self.moves) == 0:
            raise Exception("No moves to undo.")
        
        last_col, last_row = self.moves.pop()  # get the last move

        self.board[last_row][last_col] = "_"  # remove the piece from the board

        self.current_player = "2" if self.current_player == "1" else "1"  # switch players back
        return True

    def score(self, args):
        '''
            >> score
            Prints the scores.
        '''

        self.calculate_score()
        print(f"{self.p1score} {self.p2score}")
        return True

    def calculate_score(self):
        # calculates the score for both players based on the current board state
        player1_score = 0
        player2_score = self.handicap

        # avoids double counting, by keeping track of which cells have already been counted in a line
        in_line = [[False] * self.num_cols for _ in range(self.num_rows)]


        directions = [(1,0), (1,1), (0,1), (-1,1)] # right, bottom right diagonal, bottom, bottom left diagonal

        for row in range(self.num_rows):
            for col in range(self.num_cols):
                cell = self.board[row][col]

                if cell == "_":  # empty cell, skip
                    continue
                
                for dir_col, dir_row in directions:  # for each direction

                    # get the previous cell in the direction
                    prev_col = col - dir_col
                    prev_row = row - dir_row

                    # if the previous cell is in bounds and has the same value, skip this direction 
                    # to avoid double counting as the previous cell will have counted the current and later cells in this line
                    if self.in_bounds(prev_col, prev_row) and self.board[prev_row][prev_col] == cell:
                        continue

                    # count the length of the line in this direction
                    line_length = 0
                    temp_col, temp_row = col, row  # temp coords for cell traversal
                    while self.in_bounds(temp_col, temp_row) and self.board[temp_row][temp_col] == cell:  # while in bounds and same cell value as current cell
                        line_length += 1
                        temp_col += dir_col
                        temp_row += dir_row

                    if line_length >= 2:  # only count lines of length 2 or more
                        points = 2 ** (line_length - 1)  # points calculation formula
                        if cell == "1":
                            player1_score += points
                        else:
                            player2_score += points
                        
                        # traverse along the line to update in_line to avoid double counting
                        temp_col, temp_row = col, row
                        for _ in range(line_length):
                            in_line[temp_row][temp_col] = True
                            temp_col += dir_col
                            temp_row += dir_row
        
        # add points for single pieces, that are not in a line
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                cell = self.board[row][col]
                if cell != "_" and not in_line[row][col]:
                    if cell == "1":
                        player1_score += 1
                    else:
                        player2_score += 1

        self.p1score = player1_score
        self.p2score = player2_score
    
    def check_filled(self):
        # checks if the board is completely filled
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                if self.board[row][col] == "_":
                    return False
        return True

    def winner(self, args):
        '''
            >> winner
            Prints the winner information.
        '''
        self.calculate_score()

        # if score_cutoff is 0, the game ends when the board is filled
        if self.score_cutoff == 0:
            if not self.check_filled():  # if the board is not filled, the winner is unknown
                print("unknown")
                return True
            if self.p1score > self.p2score:
                print("1")
            if self.p2score > self.p1score:
                print("2")
            return True
        else:
            filled = self.check_filled()  # check if the board is filled
            if (self.p1score >= self.score_cutoff or filled) and self.p1score > self.p2score:  # if player 1 has reached the score cutoff or the board is filled and player 1 has a higher score
                print("1")
            elif (self.p2score >= self.score_cutoff or filled) and self.p2score > self.p1score:  # vice versa for player 2
                print("2")
            else:
                print("unknown")  # otherwise the winner is unknown
            return True

    def show(self, args):
        '''
            >> show
            Shows the game board.
        '''
        for row in range(self.num_rows):
            print(" ".join(self.board[row]))
        return True
    
    #======================================================================================
    # End of functions requiring implementation
    #======================================================================================

if __name__ == "__main__":
    interface = CommandInterface()
    interface.main_loop()
