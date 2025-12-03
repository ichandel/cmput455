# CMPUT 455 Assignment 4 starter code (PoE2)
# Implement the specified commands to complete the assignment
# Full assignment specification on Canvas

import sys

class CommandInterface:
    # The following is already defined and does not need modification
    # However, you may change or add to this code as you see fit, e.g. adding class variables to init

    def __init__(self):
        # Define the string to function command mapping
        self.command_dict = {
            "help"     : self.help,
            "init_game": self.init_game,   # init_game w h p s [board]
            "show"     : self.show,
            "timelimit": self.timelimit,   # timelimit seconds
            "genmove"  : self.genmove,     # see assignment spec
            "play"     : self.play, 
            "score"    : self.score
        }

        self.board = [[0]]
        self.to_play = 1
        self.handicap = 0.0
        self.score_cutoff = float("inf")
        self.time_limit = 1

    # Convert a raw string to a command and a list of arguments
    def process_command(self, s):
        s = s.lower().strip()
        if len(s) == 0:
            return True
        command = s.split(" ")[0]
        args = [x for x in s.split(" ")[1:] if len(x) > 0]
        if command not in self.command_dict:
            print("? Uknown command.\nType 'help' to list known commands.", file=sys.stderr)
            print("= -1\n")
            return False
        ##Error handling is currently commented out to enable better error messages
        ##You may want to re-enable this for your submission in case there are unknown errors
        #try:
        return self.command_dict[command](args)
        #except Exception as e: 
        #    print("Command '" + s + "' failed with exception:", file=sys.stderr)
        #    print(e, file=sys.stderr)
        #    print("= -1\n")
        #    return False
        
    # Will continuously receive and execute commands
    # Commands should return True on success, and False on failure
    # Every command will print '= 1' or '= -1' at the end of execution to indicate success or failure respectively
    def main_loop(self):
        while True:
            s = input()
            if s.split(" ")[0] == "exit":
                print("= 1\n")
                return True
            if self.process_command(s):
                print("= 1\n")

    # List available commands
    def help(self, args):
        for command in self.command_dict:
            if command != "help":
                print(command)
        print("exit")
        return True

    # Helper function for command argument checking
    # Will make sure there are enough arguments, and that they are valid integers
    def arg_check(self, args, template):
        if len(args) < len(template.split(" ")):
            print("Not enough arguments.\nExpected arguments:", template, file=sys.stderr)
            print("Recieved arguments: ", end="", file=sys.stderr)
            for a in args:
                print(a, end=" ", file=sys.stderr)
            print(file=sys.stderr)
            return False
        for i, arg in enumerate(args):
            try:
                args[i] = int(arg)
            except ValueError:
                try:
                    args[i] = float(arg)
                except ValueError:
                    print("Argument '" + arg + "' cannot be interpreted as a number.\nExpected arguments:", template, file=sys.stderr)
                    return False
        return True
    
    # Command functions needed for playing.
    # Feel free to modify them if needed, but keep their functionality intact.

    # init_game w h p s
    def init_game(self, args):
        # Check arguments
        if len(args) > 4:
            self.board_str = args.pop()
        else:
            self.board_str = ""
        if not self.arg_check(args, "w h p s"):
            return False
        w, h, p, s = args
        if not (1 <= w <= 20 and 1 <= h <= 20):
            print("Invalid board size:", w, h, file=sys.stderr)
            return False
        
        #Initialize game state
        self.width = w
        self.height = h
        self.handicap = p
        if s == 0:
            self.score_cutoff = float("inf")
        else:
            self.score_cutoff = s
        
        self.board = []
        for r in range(self.height):
            self.board.append([0]*self.width)
        self.to_play = 1
        self.p1_score = 0
        self.p2_score = self.handicap
        return True

    def show(self, args):
        for row in self.board:
            print(" ".join(["_" if v == 0 else str(v) for v in row]))
        return True

    # Sets the timelimit for genmove, non-negative integer
    def timelimit(self, args):
        if not self.arg_check(args, "t"):
            return False

        self.time_limit = int(args[0])
        return True

    def play(self, args):
        if not self.arg_check(args, "x y"):
            return False
        
        try:
            x = int(args[0])
            y = int(args[1])
        except ValueError:
            print("Illegal move: " + " ".join(args), file=sys.stderr)
            return False
        
        if not (0 <= x < self.width) or not (0 <= y < self.height) or self.board[y][x] != 0:
            print("Illegal move: " + " ".join(args), file=sys.stderr)
            return False
        
        if self.p1_score >= self.score_cutoff or self.p2_score >= self.score_cutoff:
            print("Illegal move: " + " ".join(args), "game ended.", file=sys.stderr)
            return False
        
        # put the piece onto the board
        self.make_move(x, y)

        return True

    def score(self, args):
        p1_score, p2_score = self.calculate_score()
        print(p1_score, p2_score)
        return True
    
    # Optional helper functions that you may use or replace with your own.

    def get_moves(self):
        moves = []
        for y in range(self.height):
            for x in range(self.width):
                if self.board[y][x] == 0:
                    moves.append((x, y))
        return moves

    def make_move(self, x, y):
        self.board[y][x] = self.to_play
        if self.to_play == 1:
            self.to_play = 2
        else:
            self.to_play = 1

    def undo_move(self, x, y):
        self.board[y][x] = 0
        if self.to_play == 1:
            self.to_play = 2
        else:
            self.to_play = 1

    # Returns p1_score, p2_score
    def calculate_score(self):
        p1_score = 0
        p2_score = self.handicap

        # Progress from left-to-right, top-to-bottom
        # We define lines to start at the topmost (and for horizontal lines leftmost) point of that line
        # At each point, score the lines which start at that point
        # By only scoring the starting points of lines, we never score line subsets
        for y in range(self.height):
            for x in range(self.width):
                c = self.board[y][x]
                if c != 0:
                    lone_piece = True # Keep track of the special case of a lone piece
                    # Horizontal
                    hl = 1
                    if x == 0 or self.board[y][x-1] != c: #Check if this is the start of a horizontal line
                        x1 = x+1
                        while x1 < self.width and self.board[y][x1] == c: #Count to the end
                            hl += 1
                            x1 += 1
                    else:
                        lone_piece = False
                    # Vertical
                    vl = 1
                    if y == 0 or self.board[y-1][x] != c: #Check if this is the start of a vertical line
                        y1 = y+1
                        while y1 < self.height and self.board[y1][x] == c: #Count to the end
                            vl += 1
                            y1 += 1
                    else:
                        lone_piece = False
                    # Diagonal
                    dl = 1
                    if y == 0 or x == 0 or self.board[y-1][x-1] != c: #Check if this is the start of a diagonal line
                        x1 = x+1
                        y1 = y+1
                        while x1 < self.width and y1 < self.height and self.board[y1][x1] == c: #Count to the end
                            dl += 1
                            x1 += 1
                            y1 += 1
                    else:
                        lone_piece = False
                    # Anit-diagonal
                    al = 1
                    if y == 0 or x == self.width-1 or self.board[y-1][x+1] != c: #Check if this is the start of an anti-diagonal line
                        x1 = x-1
                        y1 = y+1
                        while x1 >= 0 and y1 < self.height and self.board[y1][x1] == c: #Count to the end
                            al += 1
                            x1 -= 1
                            y1 += 1
                    else:
                        lone_piece = False
                    # Add scores for found lines
                    for line_length in [hl, vl, dl, al]:
                        if line_length > 1:
                            if c == 1:
                                p1_score += 2 ** (line_length-1)
                            else:
                                p2_score += 2 ** (line_length-1)
                    # If all found lines are length 1, check if it is the special case of a lone piece
                    if hl == vl == dl == al == 1 and lone_piece:
                        if c == 1:
                            p1_score += 1
                        else:
                            p2_score += 1
        return p1_score, p2_score
    
    def get_relative_score(self):
        p1_score, p2_score = self.calculate_score()
        if p1_score >= self.score_cutoff or p2_score >= self.score_cutoff:
            if self.to_play == 1:
                return p1_score - p2_score
            else:
                return p2_score - p1_score
        else:
            # Check if the board is full
            for y in range(self.height):
                for x in range(self.width):
                    if self.board[y][x] == 0:
                        return None
            if self.to_play == 1:
                return p1_score - p2_score
            else:
                return p2_score - p1_score

    # To implement for assignment 4.
    # Make sure you print a move within the specified time limit (1 second by default)
    # Print the x and y coordinates of your chosen move, space separated.
    def genmove(self, args):
        import time
        import random
        import math

        # --- Get legal moves from current position ---
        root_moves = self.get_moves()
        if not root_moves:
            # No legal moves (should not happen in assignment, but handle gracefully)
            # Returning False signals command failure
            return False

        # --- Snapshot root state so we can restore it every iteration ---
        board_snapshot = [row[:] for row in self.board]
        to_play_snapshot = self.to_play
        root_player = self.to_play  # fixed perspective for value estimates

        # --- MCTS node definition ---
        class Node:
            __slots__ = ("parent", "children", "move", "visits", "value", "untried_moves")

            def __init__(self, move=None, parent=None, untried_moves=None):
                self.parent = parent
                self.children = []
                self.move = move                  # move that led to this node (None at root)
                self.visits = 0
                self.value = 0.0                  # total reward from root_player's POV
                self.untried_moves = untried_moves or []

        # UCT formula (standard choice C ≈ sqrt(2))
        def uct_score(child, parent_visits, c=1.41421356237):
            if child.visits == 0:
                return float("inf")
            exploit = child.value / child.visits
            explore = c * math.sqrt(math.log(parent_visits) / child.visits)
            return exploit + explore

        # Compute final reward for root_player as score difference
        def result_for_root_player():
            p1, p2 = self.calculate_score()
            if root_player == 1:
                return p1 - p2
            else:
                return p2 - p1

        # Check whether the current position (self.board, self.to_play) is terminal,
        # and if so, return (True, reward_for_root_player)
        def is_terminal_and_result():
            # Score cutoff case (general; in assignment score_cutoff is usually infinity)
            if self.score_cutoff != float("inf"):
                p1, p2 = self.calculate_score()
                if p1 >= self.score_cutoff or p2 >= self.score_cutoff:
                    return True, result_for_root_player()

            # Normal end: no legal moves (board full)
            moves = self.get_moves()
            if not moves:
                return True, result_for_root_player()

            return False, 0.0

        # --- Root node ---
        root = Node(move=None, parent=None, untried_moves=root_moves[:])

        # If there's only one legal move, just play it without search
        if len(root_moves) == 1:
            best_move = root_moves[0]
            self.make_move(best_move[0], best_move[1])
            print(best_move[0], best_move[1])
            return True

        # --- Time budget ---
        if self.time_limit is None:
            time_limit = 1.0
        else:
            time_limit = float(self.time_limit)

        # Leave a safety margin so we don't exceed the 1s limit
        budget = max(0.05, 0.9 * time_limit)
        start_time = time.time()

        # --- Main MCTS loop ---
        while time.time() - start_time < budget:
            # 1) Restore root state before each simulation
            for y in range(self.height):
                self.board[y][:] = board_snapshot[y][:]
            self.to_play = to_play_snapshot

            node = root

            # 2) SELECTION: walk down while node fully expanded and non-terminal
            while True:
                terminal, _ = is_terminal_and_result()
                if terminal:
                    break
                if node.untried_moves:
                    # Not fully expanded -> stop here for expansion
                    break
                if not node.children:
                    # No moves from here (terminal leaf)
                    break

                parent_visits = max(1, node.visits)
                best_child = None
                best_score = -float("inf")

                for child in node.children:
                    score = uct_score(child, parent_visits)
                    if score > best_score:
                        best_score = score
                        best_child = child

                # Play the move corresponding to the chosen child
                move = best_child.move
                self.make_move(move[0], move[1])
                node = best_child

            # 3) EXPANSION: if non-terminal and there are untried moves, expand one
            terminal, _ = is_terminal_and_result()
            if (not terminal) and node.untried_moves:
                idx = random.randrange(len(node.untried_moves))
                move = node.untried_moves.pop(idx)
                self.make_move(move[0], move[1])
                child_moves = self.get_moves()
                child = Node(move=move, parent=node, untried_moves=child_moves)
                node.children.append(child)
                node = child

            # 4) ROLLOUT: random playout from node until terminal
            while True:
                terminal, result = is_terminal_and_result()
                if terminal:
                    break
                moves = self.get_moves()
                if not moves:
                    # Should be covered by is_terminal_and_result, but keep as guard
                    result = result_for_root_player()
                    break
                move = random.choice(moves)
                self.make_move(move[0], move[1])

            # 5) BACKPROP: update along the path up to the root
            while node is not None:
                node.visits += 1
                node.value += result  # reward already in root_player's perspective
                node = node.parent

        # --- Choose final move: child of root with most visits ---
        if not root.children:
            # Fallback if something weird happened
            best_move = random.choice(root_moves)
        else:
            best_child = max(root.children, key=lambda c: c.visits)
            best_move = best_child.move

        # Restore root state, then actually play the chosen move for real
        for y in range(self.height):
            self.board[y][:] = board_snapshot[y][:]
        self.to_play = to_play_snapshot

        self.make_move(best_move[0], best_move[1])
        print(best_move[0], best_move[1])
        return True

if __name__ == "__main__":
    interface = CommandInterface()
    interface.main_loop()
