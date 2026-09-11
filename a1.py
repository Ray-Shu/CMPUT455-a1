# CMPUT 455 Assignment 1 starter code
# Implement the specified commands to complete the assignment
# Full assignment specification and game rules on Canvas

from sys import stderr
from typing import List, Dict, Callable
import ast
import random

def not_yet() -> bool:
    raise NotImplementedError("Command not implemented.")
    return False

def print_error(error: str) -> None:
    print(error, file = stderr)

CommandMap = Dict[str, Callable[[str], bool]]

BLACK = 'b'
WHITE = 'w'
class CommandInterface:
    def __init__(self) -> None:
        # you can add your own initialisation here
        self.commands: CommandMap = {
            "help": self.cmd_help,
            "heapgo": self.cmd_heapgo,
            "show": self.cmd_show,
            "toplay": self.cmd_toplay,
            "play": self.cmd_play,
            "legal": self.cmd_legal,
            "genmove": self.cmd_genmove,
            "score": self.cmd_score,
            "winner": self.cmd_winner,
            }

        self.to_play:str = 'b'
        self.komi:float = 0.0
        self.black_score:float = 0.0
        self.white_score:float = 0.0
        self.moves:List = [] #idk abt this one
        self.game_state:List[List[tuple]]

#============================================================================
# You need to implement the following methods.
#============================================================================
    def cmd_heapgo(self, args: str) -> bool:
        """
        Start heapgo game. 
        Args: 
            'heapgo komi G'
            - komi is a number 
            - G is a string specifying the game state 
            e.g. heapgo 0.5 [[('w', 2)]]
        Returns: 
            1: command was successfully executed 
            0: command failed 
        """

        # check if gamestate exists
        if "[" not in args:
            return 0

        # split args
        split_idx = args.index("[")
        komi_str = args[:split_idx].strip()
        game_state_str = args[split_idx:].strip()

        # check if komi exists
        if not komi_str: 
            return 0
        try:
            self.komi = float(komi_str) # checks if komi is a float
        except ValueError:
            return 0

        # check if game state is proper typing
        self.game_state = ast.literal_eval(game_state_str) 
        if not isinstance(self.game_state, list):
            return 0

        # Komi check 
        if not (-100 < self.komi < 100): return 0
        self.black_score = 0 
        self.white_score = self.komi
        self.to_play = "b"

        # num heaps & num tokens check & token correctness check 
        num_heaps = 0
        for i in range(len(self.game_state)): # num heaps
            num_heaps += 1
            num_tokens = 0
            if not isinstance(self.game_state[i], list): return 0 # checks if List[List[...]]
            for j in range(len(self.game_state[i])):  # num tokens
                num_tokens += 1
                heap = self.game_state[i][j]

                if not isinstance(heap, tuple): return 0 # checks if List[List[Tuple]]
                if len(heap) != 2: return 0 # checks that heap has only 2 elements (c,n)
                if heap[0] != 'b' and heap[0] != 'w': return 0 # checks player colours
                if not (1 <= heap[1] <= 20): return 0 # checks heap value in [1,20] 
                if num_tokens > 10: return 0
            if num_heaps > 10: return 0
                
        return 1

    def cmd_show(self, args: str) -> bool:
        """
        Shows Komi and current game state.

        Returns: 
            1: command was successfully executed 
            0: command failed 
        """
        try:
            print(f"k {self.komi} {self.game_state}")
            return 1
        except: 
            return 0
        
    def cmd_toplay(self, args: str) -> bool:
        if (args == "b" or args == "w"):
            self.to_play = args # set to_play to that color
            return 1
        else:
            return 0

    def cmd_play(self, args: str) -> bool:
        try:
            heap = int(args)
        except:
            return 0

        # false if heap is negative, out of range, or already empty
        if heap < 0 or heap >= len(self.game_state) or len(self.game_state[heap]) == 0: 
            return 0

        color = self.to_play
        score = 0.0

        while self.game_state[heap] and self.game_state[heap][-1][0] == color: # take all tokens if its current player's color
            score += self.game_state[heap].pop()[1]
        if self.game_state[heap]: # if tokens left take exactly one
            score += self.game_state[heap].pop()[1]

        if color == "b":
            self.black_score += score

        else:
            self.white_score += score
        self.to_play = "w" if color == "b" else "b" #
        return 1
        
    def cmd_legal(self, args: str) -> bool:
        try:
            heap = int(args)
        except:
            return 0

        try:
            self.game_state
        except:
            return 0
        
        if heap < 0:
            return 0
        if heap < len(self.game_state) and len(self.game_state[heap]) > 0:
            print("yes")
        else:
            print("no")
        return 1

    def cmd_genmove(self, args: str) -> bool:
        try:
            self.game_state
        except:
            return 0
        
        legal_heaps = []
        for i in range(len(self.game_state)):
            if len(self.game_state[i]) > 0:
                legal_heaps.append(i)
        if not legal_heaps:
            return 0
        heap = random.choice(legal_heaps)
        self.cmd_play(str(heap))
        print(heap)  
        return 1

    def _fmt(self, x): # helper to control how score gets printed, failing otherwise
        return str(int(x)) if x == int(x) else str(x)

    def cmd_score(self, args: str) -> bool:
        try:
            self.game_state
        except:
            return 0
        print(f"b {self._fmt(self.black_score)} w {self._fmt(self.white_score)}")
        return 1

    def cmd_winner(self, args: str) -> bool:
        try:
            self.game_state
        except:
            return 0
        
        if any(len(heap) > 0 for heap in self.game_state): # game not finished, return -1
            return 0

        if self.black_score > self.white_score:
            print("b")
        else:
            print("w")
        return 1
        
#============================================================================
# End of functions requiring implementation
#============================================================================

#============================================================================
# The code below should not need modification
# Anyway, you may change or add to this code as you see fit
# Examples:
# You can add class variables to __init__ above
# You can add better error messages
# You can put commands inside your own Heap Go class
# etc.
#============================================================================
    # List available commands
    def cmd_help(self, ignore_args: str) -> bool:
        print("\nKnown commands:")
        for cmd in self.commands:
            print(cmd)
        return True

    def process_command(self, cmd_name: str, cmd_args: str) -> None:
        # Try to find command, None if wrong name
        status = "= -1"
        cmd = self.commands.get(cmd_name)
        if cmd:
            try:
                if cmd(cmd_args): # success!
                    status = "= 1"
            except Exception as e:
                print_error(f"Command {cmd_name} with arguments {cmd_args} failed with exception: {e}")
        else:
            print_error("Unknown command. Type 'help' for commands.")
        print(status)
    
    def main_loop(self) -> None:
        process_commands = True
        while process_commands:
            try:
                line = input()
            except EOFError:
                break
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(maxsplit=1)
            cmd_name = parts[0]
            if cmd_name == "exit":
                process_commands = False
                continue
            cmd_args = parts[1] if len(parts) > 1 else ""
            self.process_command(cmd_name, cmd_args)

if __name__ == "__main__":
    interface = CommandInterface()
    # below is causing the one of the command outputs to mismatch
    # print("Game Start (input command, 'help' to show commands)")
    interface.main_loop()

