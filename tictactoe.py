"""
Tic Tac Toe Player
"""

import math
from copy import deepcopy

X = "X"
O = "O"
EMPTY = None


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
    countx = 0
    counto = 0

    for row in board:
        for cell in row:
            if cell == X:
                countx += 1
            elif cell == O:
                counto += 1

    if countx == counto:
        return X
    else:
        return O


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
    i, j = action
    
    if newboard[i][j] == EMPTY:
        newboard[i][j] = player(newboard)
    else:
        raise IndexError("Invalid Move")
    
    return newboard


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    winCondition = [[X, X, X], [O, O, O]]

    boardTransposed = [list(x) for x in zip(*board)]

    for i in range(3):
        if board[i] in winCondition:
            return board[i][0]
        if boardTransposed[i] in winCondition:
            return boardTransposed[i][0]
    
    TLtoBR = []
    BLtoTR = []

    for i in range(3):
        TLtoBR.append(board[i][i])
        BLtoTR.append(board[2-i][i])

    if TLtoBR in winCondition:
        return TLtoBR[0]
    if BLtoTR in winCondition:
        return BLtoTR[0]
    
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) != None:
        return True
    
    for row in board:
        for cell in row:
            if cell == None:
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

    # Determine the current player
    maxPlayer = True if player(board) == X else False
    
    # Set the initial branch score (not inversed sign only for the initial call)
    otherBranchScore = math.inf if maxPlayer else -math.inf

    # Starts the recursive function and get the optimal action
    _, optAction = eval(board, otherBranchScore)

    # Print the callcount to measure the effect of ab pruning
    print("callcount:", callcount)

    # return optimal action
    return optAction


def eval(board, otherBranchScore):
    """
    Recursive function that evaluates until it reaches terminal board
    It uses the otherBranchScore argument to keep track of the other min/max of the other branch on the same parent that has been explored
    Returns optimal action and the score for the board
    """
    global callcount
    callcount += 1

    # Determine current player
    maxPlayer = True if player(board) == X else False

    # Set the score and branchScore initially as infinite (inversed sign to the player goals)
    score = -math.inf if maxPlayer else math.inf
    
    # Set optimal action as none since none has been explored yet
    optAction = None

    # If terminal board, just return the utility as score and None as optimal Action
    if terminal(board):
        score = utility(board)
        return (score, None)

    # Iterate over each actions available
    for action in actions(board):
        boardResult = result(board, action)
        
        # Call eval() for the resulting board from the action, while passing the explored branches' score (if theres any)
        newScore, _ = eval(boardResult, score)

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
    
    # Return the pair of score and optimal action
    return (score, optAction)