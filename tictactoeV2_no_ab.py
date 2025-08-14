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


callcount = 0

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    global callcount
    callcount = 0

    _, optAction = eval(board)

    print("callcount:", callcount)
    return optAction


def eval(board):
    """
    Recursive function that evaluates until it reaches terminal board
    Returns optimal action and the score of the board
    """
    global callcount
    callcount += 1

    maxPlayer = True if player(board) == X else False
    score = -math.inf if maxPlayer else math.inf
    optAction = None

    if terminal(board):
        score = utility(board)
        return (score, None)

    for action in actions(board):
        boardResult = result(board, action)
        newScore, _ = eval(boardResult)

        if maxPlayer:
            if newScore > score:
                score = newScore
                optAction = action

        else:
            if newScore < score:
                score = newScore
                optAction = action

    return (score, optAction)

    



    


        
