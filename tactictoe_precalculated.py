"""
Tic Tac Toe Player
"""

import calculation as clc

import math
import time
import random
from copy import deepcopy
from pprint import pp

X = 3
O = -3
EMPTY = 0


states_encoded = set()
scores = dict()
move_scores = dict()
best_moves = dict()


def init():
    global states_encoded, scores, move_scores, best_moves
    states_encoded, scores, move_scores, best_moves = clc.calculate()


def initial_state():
    """
    Returns starting state of the board.
    """
    state = {
        "turn": X,
        "board":   [[EMPTY, EMPTY, EMPTY],
                    [EMPTY, EMPTY, EMPTY],
                    [EMPTY, EMPTY, EMPTY]]
    }

    return state


def player(state):
    """
    Returns player who has the next turn on a board.
    """

    return state["turn"]


def actions(state):
    """
    Returns list of all possible actions (i, j) available on the board.
    """
    moves = list()

    for i, row in enumerate(state["board"]):
        for j, cell in enumerate(row):
            if cell == EMPTY:
                moves.append((i,j))
    
    random.shuffle(moves)

    return moves


def result(state, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    newboard = deepcopy(state["board"])
    player = state["turn"]

    if player == X:
        for i in range(3):
            for j in range(3):
                if newboard[i][j] > 0:
                    newboard[i][j] -= 1
        nextPlayer = O

    else:
        for i in range(3):
            for j in range(3):
                if newboard[i][j] < 0:
                    newboard[i][j] += 1
        nextPlayer = X

    i, j = action
    if state["board"][i][j] == EMPTY:
        newboard[i][j] = player
    else:
        print(state["board"])
        print(action)
        raise IndexError("Invalid Move")
    
    newState = {
        "turn": nextPlayer,
        "board": newboard,
    }

    return newState


def winner(state):
    """
    Returns the winner of the game, if there is one.
    """
    board = state["board"]
    boardTransposed = [list(x) for x in zip(*state["board"])]

    for row in board:
        if all(cell > 0 for cell in row):
            return X
        elif all(cell < 0 for cell in row):
            return O

    for row in boardTransposed:
        if all(cell > 0 for cell in row):
            return X
        elif all(cell < 0 for cell in row):
            return O

    if all(board[i][i] > 0 for i in range(3)):
        return X
    if all(board[2-i][i] > 0 for i in range(3)):
        return X
    
    if all(board[i][i] < 0 for i in range(3)):
        return O
    if all(board[2-i][i] < 0 for i in range(3)):
        return O
    
    return None


def terminal(state):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(state) != None:
        return True
    
    return False


def utility(state, depth):
    """
    Returns the value of the board, also based on depth the of the search (higher depth means less steps to get to the position)
    """
    winPlayer = winner(state)
    if winPlayer == X:
        return 1 * depth
    elif winPlayer == O:
        return -1 * depth 
    else:
        return 0


# callcount variable to track how many times eval() is called
callcount = 0


def getBestMove(state):
    """
    Returns the optimal action for the current player on the board.
    """
    state_encoded = clc.get_canonical_form(state["board"], state["turn"])

    print(f"Eval Score: {scores[state_encoded]}")

    best_move_canonical = random.choice(best_moves[state_encoded])  
    new_state = result(clc.decodeState(state_encoded), best_move_canonical)
    best_state_canonical = clc.get_canonical_form(new_state["board"], new_state["turn"])

    valid_best_moves = []
    for move in actions(state):
        new_state = result(state, move)
        # Check if the move results in the best canonical state
        if clc.get_canonical_form(new_state["board"], new_state["turn"]) == best_state_canonical:
            valid_best_moves.append(move)

    # print(f"Valid Moves: {len(valid_best_moves)}")
    return random.choice(valid_best_moves)
    

def getRandomMove(state):

    state_encoded = clc.get_canonical_form(state["board"], state["turn"])
    print(f"Eval Score: {scores[state_encoded]}")

    return random.choice(list(actions(state)))
    