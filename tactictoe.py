"""
Tic Tac Toe Player
"""

import math
import random
from copy import deepcopy


X = 6
O = -6
EMPTY = 0


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    counter = 0

    for row in board:
        for cell in row:
            counter += cell

    turn = None

    if counter > 0:
        turn = O
    else:
        turn = X

    return turn 


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    moves = set()

    for i, row in enumerate(board):
        for j, cell in enumerate(row):
            if cell == EMPTY:
                moves.add((i,j))

    return moves


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    newboard = deepcopy(board)

    symbol = player(newboard)

    for i, row in enumerate(board):
        for j, _ in enumerate(row):
            if newboard[i][j] > 0:
                newboard[i][j] -= 1
            elif newboard[i][j] < 0:
                newboard[i][j] += 1

    i, j = action
    if board[i][j] == EMPTY:
        newboard[i][j] = symbol
    else:
        print(board)
        print(action)
        raise IndexError("Invalid Move")
    
    return newboard


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    boardTransposed = [list(x) for x in zip(*board)]

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


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) != None:
        return True
    
    for row in board:
        for cell in row:
            if cell == EMPTY:
                return False
    
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    winPlayer = winner(board)
    if winPlayer == X:
        return 1
    elif winPlayer == O:
        return -1
    else:
        return 0


# callcount variable to track how many times eval() is called
callcount = 0

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    global callcount
    callcount = 0

    # # random move
    # return random.choice(list(actions(board)))

    # Determine the current player
    maxPlayer = True if player(board) == X else False
    
    # Set the initial branch score (not inversed sign only for the initial call)
    otherBranchScore = math.inf if maxPlayer else -math.inf

    path = set()
    MAX_DEPTH = 10

    # Starts the recursive function and get the optimal action
    optScore, optAction = eval(board, path, MAX_DEPTH, otherBranchScore)

    # Print the callcount to measure the effect of ab pruning
    print("callcount:", callcount)
    print(f"OptScore: {optScore}")

    # return optimal action
    return optAction

# A dictionary to store scores of evaluated states
transposition_table = {}

def eval(board, path, depth, otherBranchScore):
    """
    Recursive function that evaluates until it reaches terminal board
    It uses the otherBranchScore argument to keep track of the other min/max of the other branch on the same parent that has been explored
    Returns optimal action and the score for the board
    """
    global callcount
    callcount += 1

    # if str(board) in transposition_table:
    #     return transposition_table[str(board)]

    if hashBoard(board) in path:
        print("Path Optimised")
        return (0, None)

    # Determine current player
    maxPlayer = True if player(board) == X else False

    # Set the score and branchScore initially as infinite (inversed sign to the player goals)
    score = -math.inf if maxPlayer else math.inf
    
    # Set optimal action as none since none has been explored yet
    optAction = None

    # If terminal board, just return the utility as score and None as optimal Action
    if terminal(board) or depth == 0:
        score = utility(board)
        return (score, None)

    path.add(hashBoard(board))

    # Iterate over each actions available
    for action in actions(board):
        boardResult = result(board, action)
        
        # Call eval() for the resulting board from the action, while passing the explored branches' score (if theres any)
        newScore, _ = eval(boardResult, path, depth - 1, score)

        # If its the maxPlayer's turn, update the new score if larger than current score
        if maxPlayer:
            if newScore > score:
                score = newScore
                optAction = action

            # If the score is larger than the other parent's branch, we can prune this branch (skip checking other branches)
            if score >= otherBranchScore:
                break

        # If its the maxPlayer's turn, update the new score if smaller than current score
        else:
            if newScore < score:
                score = newScore
                optAction = action

            # If the score is larger than the other parent's branch, we can prune this branch (skip checking other branches)
            if score <= otherBranchScore:
                break

    path.remove(hashBoard(board))
    
    # Return the pair of score and optimal action
    # transposition_table[str(board)] = (score, optAction)
    return (score, optAction)


def hashBoard(board):
    # to be used with sets
    hashable_version = tuple(cell for row in board for cell in row)
    return hashable_version