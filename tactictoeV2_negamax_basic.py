"""
Tic Tac Toe Player
"""

import math
import time
import random
from copy import deepcopy
from pprint import pp

X = 3
O = -3
EMPTY = 0


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
    
    # random.shuffle(moves)

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
        return 1 * depth 
    else:
        return 0


# callcount variable to track how many times eval() is called
callcount = 0
MAX_DEPTH = 15

def negamax(state):
    """
    Returns the optimal action for the current player on the board.
    """
    global callcount
    callcount = 0

    startTime = time.time() 

    maxPlayer = True if player(state) == X else False
    print("\n" + ("MaxPlayer" if maxPlayer else "MinPlayer"))
    optScore  = -math.inf
    optAction = None
    sign = 1 if maxPlayer else -1

    validMoves = list(actions(state))
    alpha = -math.inf*sign
    beta = math.inf*sign

    for action in validMoves:
        boardResult = result(state, action)

        # Starts the recursive function and get the optimal action
        score = eval(boardResult, MAX_DEPTH, alpha=alpha, beta=beta, sign=sign)
        score = -score

        if score > optScore:
            optScore = score
            optAction = action

        print(f"{score}: {action}  {alpha}/{beta}")

    # Print the callcount to measure the effect of ab pruning
    print("callcount:", callcount)
    print(f"Calculation Time: {(time.time() - startTime):.4f}s")
    print(f"OPT -> Score: {optScore}, Move: {optAction}")

    # return optimal action
    return optAction



def eval(state, depth, alpha, beta, sign):
    """
    Recursive function that evaluates until it reaches terminal board
    It uses the otherBranchScore argument to keep track of the other min/max of the other branch on the same parent that has been explored
    Returns optimal action and the score for the board
    """
    global callcount
    callcount += 1

    # If terminal board, just return the utility as score and None as optimal Action
    if terminal(state):
        score = utility(state, depth) * sign
        return score
    
    if depth == 0:
        score = 0
        return score

    value = -math.inf
    validMoves = actions(state)

    # Iterate over each actions available
    for action in validMoves:
        boardResult = result(state, action)
        
        # Call eval() for the resulting board from the action
        value = max(value, -eval(boardResult, depth - 1, alpha=-beta, beta=-alpha, sign=-sign))
        alpha = max(alpha, value)

        if alpha >= beta:
            break

    return value


def hashBoard(state):
    
    hash = [cell for row in state["board"] for cell in row]
    hash.append(state["turn"])
    hashable_version = tuple(hash)
    
    return hashable_version


def checkSymmetry(board, move1, move2):
    
    board1 = result(board, move1)
    board2 = result(board, move2)

    def TL_BR_Sym():
        for i in range(3):
            for j in range(3):
                if board1[i][j] != board2[j][i]:
                    return False
        return True

    def TR_BL_Sym():
        for i in range(3):
            for j in range(3):
                if board1[i][j] != board2[2-j][2-i]:
                    return False
        return True

    def L_R_Sym():
        for i in range(3):
            for j in range(3):
                if board1[i][j] != board2[i][2-j]:
                    return False
        return True
    
    def T_B_Sym():
        for i in range(3):
            for j in range(3):
                if board1[i][j] != board2[2-i][j]:
                    return False
        return True
    
    return any([TR_BL_Sym(), TL_BR_Sym(), L_R_Sym(), T_B_Sym()])


     
    