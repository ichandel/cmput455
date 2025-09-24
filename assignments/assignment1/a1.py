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

        if len(args) != 4:
            print("init_game requires 4 arguments.", file=sys.stderr)
            raise Exception("init_game requires 4 arguments.")

        nc = int(args[0])
        nr = int(args[1])
        h = float(args[2])
        sc = float(args[3]) # check if this is nonnegative 


        self.num_cols = nc
        self.num_rows = nr
        self.handicap = h
        self.score_cutoff = sc

        self.p1score = 0
        self.p2score = h
        

        self.current_player = "1" # Player 1 starts
        self.moves = [] # List of moves played

        self.board = [["_"] * self.num_cols for _ in range(self.num_rows)]
        return True
    
    def legal(self, args):
        '''
            >> legal <col> <row>
            Checks if the current player can play at position (<col>, <row>) on the board.
        '''

        if len(args) != 2:
            print("legal requires 2 arguments.", file=sys.stderr)
            raise Exception("legal requires 2 arguments.")
        
        col = int(args[0])
        row = int(args[1])
        
        if self.check_legal([col, row]):
            print("yes")
        else:
            print("no")
        return True
    
    def check_legal(self, args):

        
        col = int(args[0])
        row = int(args[1])

        if not self.in_bounds(col, row):
            return False
        
        # Check if the game has already been won

        
        if self.score_cutoff > 0:
            self.calculate_score()
            if (self.p1score >= self.score_cutoff or self.p2score >= self.score_cutoff):
                return False
            
        return self.board[row][col] == "_"

    def play(self, args):
        '''
            >> play <col> <row>
            Places the current player's piece at position (<col>, <row>). Check if the move is legal before playing it.
        '''
        
        if len(args) != 2:
            print("play requires 2 arguments.", file=sys.stderr)
            raise Exception("play requires 2 arguments.")
                
        col = int(args[0]) # column
        row = int(args[1]) # row

        if not self.check_legal(args):
            raise Exception("Illegal move.")
        
        self.board[row][col] = self.current_player
        self.current_player = "2" if self.current_player == "1" else "1"
        
        self.moves.append((col, row))

        return True
    
    def in_bounds(self, col, row):
        return 0 <= col < self.num_cols and 0 <= row < self.num_rows
        
    def genmove(self, args):
        '''
            >> genmove
            Generates and plays a random valid move.
        '''
        
        if self.check_filled():
            print("resign")
            return True
        
        # check if the game has already been won
        if self.score_cutoff > 0:
            self.calculate_score()
            if (self.p1score >= self.score_cutoff or self.p2score >= self.score_cutoff):
                print("resign")
                return True
        
        while True:
            row = random.randint(0, self.num_rows - 1)
            col = random.randint(0, self.num_cols - 1)
            if self.check_legal([col, row]):
                print(col, row)
                self.play([col, row])
                return True

    def undo(self, args):
        '''
            >> undo
            Undoes the last move.
        '''

        if len(self.moves) == 0:
            raise Exception("No moves to undo.")
        
        last_col, last_row = self.moves.pop()

        self.board[last_row][last_col] = "_"

        self.current_player = "2" if self.current_player == "1" else "1"
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
        player1_score = 0
        player2_score = self.handicap

        # avoids double counting, by keeping track of which cells have already been counted in a line
        in_line = [[False] * self.num_cols for _ in range(self.num_rows)]


        directions = [(1,0), (1,1), (0,1), (-1,1)] # right, bottom right diagonal, bottom, bottom left diagonal

        for row in range(self.num_rows):
            for col in range(self.num_cols):
                cell = self.board[row][col]

                if cell == "_":
                    continue
                
                for dir_col, dir_row in directions:
                    prev_col = col - dir_col
                    prev_row = row - dir_row

                    if self.in_bounds(prev_col, prev_row) and self.board[prev_row][prev_col] == cell:
                        continue

                    line_length = 0
                    temp_col, temp_row = col, row
                    while self.in_bounds(temp_col, temp_row) and self.board[temp_row][temp_col] == cell:
                        line_length += 1
                        temp_col += dir_col
                        temp_row += dir_row

                    if line_length >= 2:
                        points = 2 ** (line_length - 1)
                        if cell == "1":
                            player1_score += points
                        else:
                            player2_score += points
                        
                        temp_col, temp_row = col, row
                        for _ in range(line_length):
                            in_line[temp_row][temp_col] = True
                            temp_col += dir_col
                            temp_row += dir_row
                
        
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

        if self.score_cutoff == 0:
            if not self.check_filled():
                print("unknown")
                return True
            if self.p1score > self.p2score:
                print("1")
            if self.p2score > self.p1score:
                print("2")
            return True
        else:
            filled = self.check_filled()
            if (self.p1score >= self.score_cutoff or filled) and self.p1score > self.p2score:
                print("1")
            elif (self.p2score >= self.score_cutoff or filled) and self.p2score > self.p1score:
                print("2")
            else:
                print("unknown")
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
