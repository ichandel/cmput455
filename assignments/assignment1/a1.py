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
            return False

        self.num_cols, self.num_rows, self.handicap, self.score_cutoff = args

        self.num_cols = int(self.num_cols)
        self.num_rows = int(self.num_rows)
        self.handicap = float(self.handicap)
        self.score_cutoff = float(self.score_cutoff) # check if this is nonnegative 

        self.current_player = "1" # Player 1 starts
        self.moves = [] # List of moves played

        self.board = []

        for i in range(self.num_rows):
            current_row = []
            for j in range(self.num_cols):
                current_row.append("_")
            self.board.append(current_row)
        return True
    
    def legal(self, args):
        '''
            >> legal <col> <row>
            Checks if the current player can play at position (<col>, <row>) on the board.
        '''

        args[0] = int(args[0])
        args[1] = int(args[1])
        
        if self.check_legal(args):
            print("Yes")
            return True
        else:
            print("No")
            return False
    
    def check_legal(self, args):

        
        args[0] = int(args[0])
        args[1] = int(args[1])

        player1_score, player2_score = self.calculate_score()
        if self.score_cutoff > 0 and (player1_score >= self.score_cutoff or player2_score >= self.score_cutoff):
            return False
        return self.board[args[1]][args[0]] == "_"

    def play(self, args):
        '''
            >> play <col> <row>
            Places the current player's piece at position (<col>, <row>). Check if the move is legal before playing it.
        '''
        
        if len(args) != 2:
            print("play requires 2 arguments.", file=sys.stderr)
            return False
        x = int(args[0]) # column
        y = int(args[1]) # row

        if self.check_legal(args):
            self.board[y][x] = self.current_player
            if self.current_player == "1":
                self.current_player = "2"
            else:
                self.current_player = "1"
            
            self.moves.append(args)
            return True
        else:
            return False
        
    def genmove(self, args):
        '''
            >> genmove
            Generates and plays a random valid move.
        '''
        
        i = random.randint(0, self.num_rows - 1)
        j = random.randint(0, self.num_cols - 1)

        if self.check_filled():
            return False
        
        player1_score, player2_score = self.calculate_score()
        if self.score_cutoff > 0 and (player1_score >= self.score_cutoff or player2_score >= self.score_cutoff):
            return False

        while not self.check_legal([j, i]):
            i = random.randint(0, self.num_rows - 1)
            j = random.randint(0, self.num_cols - 1)
        
        self.play([j, i])

        return True

    def undo(self, args):
        '''
            >> undo
            Undoes the last move.
        '''
        if len(self.moves) == 0:
            return False
        
        last_move = self.moves.pop()

        self.board[last_move[1]][last_move[0]] = "_"

        if self.current_player == "1":
            self.current_player = "2"
        else:
            self.current_player = "1"

        return True

    def score(self, args):
        '''
            >> score
            Prints the scores.
        '''

        print(*self.calculate_score())
        return True

    def calculate_score(self):
        player1_score = 0
        player2_score = self.handicap
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.board[i][j] != "_":
                    
                    cell = self.board[i][j]

                    # check right
                    if j == 0 or self.board[i][j - 1] != cell:
                        count_right = 1
                        while j + count_right < self.num_cols and self.board[i][j + count_right] == cell:
                            count_right += 1

                    # check bottom right diagonal
                    if (j == 0 and i == 0) or (self.board[i - 1 ][j - 1] != cell):
                        count_botright = 1
                        while (j + count_botright < self.num_cols) and (i + count_botright < self.num_rows) and self.board[i + count_botright][j + count_botright] == cell:
                            count_botright += 1

                    # check bottom
                    if i == 0 or self.board[i-1][j] != cell:
                        count_bot = 1
                        while i + count_bot < self.num_rows and self.board[i + count_bot][j] == cell:
                            count_bot += 1

                    # check bottom left diagonal
                    if ((j == self.num_cols + 1) and i == 0) or (self.board[i - 1][j + 1] != cell):
                        count_botleft = 1
                        while (j - count_botleft > 0) and (i + count_botleft < self.num_rows) and self.board[i + count_botleft][j - count_botleft] == cell:
                            count_botleft += 1
                    
                    # point calculation and score update
                    right_points = 2**(count_right - 1) if count_right > 0 else 0
                    botright_points = 2**(count_botright - 1) if count_botright > 0 else 0
                    bot_points = 2**(count_bot - 1) if count_bot > 0 else 0
                    botleft_points = 2**(count_botleft - 1) if count_botleft > 0 else 0

                    points = right_points + botright_points + bot_points + botleft_points

                    if cell == "1":
                        player1_score += points
                    elif cell == "2":
                        player2_score += points
        
        return (player1_score, player2_score)
    
    def check_filled(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.board[i][j] == "_":
                    return False
        return True

    def winner(self, args):
        '''
            >> winner
            Prints the winner information.
        '''
        player1_score, player2_score = self.calculate_score()

        if self.score_cutoff == 0:
            filled = self.check_filled()
            print("Unknown" if not filled else ("1" if player1_score > player2_score else ("2" if player2_score > player1_score else "Tie")))
            return True
        else:
            if (player1_score >= self.score_cutoff or self.check_filled()) and player1_score > player2_score:
                print("1")
            elif (player2_score >= self.score_cutoff or self.check_filled()) and player2_score > player1_score:
                print("2")
            else:
                print("Unknown")
            return True

    def show(self, args):
        '''
            >> show
            Shows the game board.
        '''
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                print(self.board[i][j], end=" ")
            print()
        
        return True
    
    #======================================================================================
    # End of functions requiring implementation
    #======================================================================================

if __name__ == "__main__":
    interface = CommandInterface()
    interface.main_loop()
