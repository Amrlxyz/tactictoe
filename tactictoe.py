"""
Tic Tac Toe Player
"""

import math
import time
import random
from copy import deepcopy
from pprint import pp


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
    
    return False


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
MAX_DEPTH = 15

# A dictionary to store scores of evaluated states
transposition_table = {}

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    global callcount
    callcount = 0

    startTime = time.time() 

    # # random move
    # return random.choice(list(actions(board)))

    path = list()

    # Starts the recursive function and get the optimal action
    optScore, optAction = eval(board, path, MAX_DEPTH, alpha=-math.inf, beta=math.inf, table=transposition_table)

    # Print the callcount to measure the effect of ab pruning
    print("callcount:", callcount)
    print(f"Calculation Time: {(time.time() - startTime):.4f}s")
    print(f"OptScore: {optScore}, OptMove: {optAction}")

    # return optimal action
    return optAction






def eval(board, path, depth, alpha, beta, table):
    """
    Recursive function that evaluates until it reaches terminal board
    It uses the otherBranchScore argument to keep track of the other min/max of the other branch on the same parent that has been explored
    Returns optimal action and the score for the board
    """
    global callcount
    callcount += 1

    EXACT = 0
    UPPERBOUND = 1
    LOWERBOUND = 2

    alphaOrig = alpha

    boardHashed = hashBoard(board)


    # (* Transposition Table Lookup; node is the lookup key for ttEntry *)
    # ttEntry := transpositionTableLookup(node)
    # if ttEntry.is_valid and ttEntry.depth ≥ depth then
    #     if ttEntry.flag = EXACT then
    #         return ttEntry.value
    #     else if ttEntry.flag = LOWERBOUND and ttEntry.value ≥ beta then
    #         return ttEntry.value
    #     else if ttEntry.flag = UPPERBOUND and ttEntry.value ≤ alpha then
    #         return ttEntry.value

    if boardHashed in table:
        entry = table[boardHashed]
        if entry["depth"] >= depth:     
            score = entry["score"]
            flag = entry["flag"]
            action = entry["action"]
            if flag == EXACT:
                return (score, action)
            elif flag == LOWERBOUND and score >= beta:
                return (score, action)
            elif flag == UPPERBOUND and score <= alpha:
                return (score, action)

    if boardHashed in path:
        return (0, None)

    # If terminal board, just return the utility as score and None as optimal Action
    if terminal(board):
        score = utility(board) * depth 
        return (score, None)
    
    if depth == 0:
        # print("Depth Limit Reached")
        # pp(path)
        score = utility(board)
        return (score, None)

    # Determine current player
    maxPlayer = True if player(board) == X else False
    if depth == MAX_DEPTH:
        print("\n" + ("MaxPlayer" if maxPlayer else "MinPlayer"))
    score = -math.inf if maxPlayer else math.inf

    # Set optimal action as none since none has been explored yet
    optAction = None

    path.append(boardHashed)
    validMoves = list(actions(board))

    # if depth == MAX_DEPTH:
    #     pp(validMoves)

    # symmetricalMoves = list()
    # checkedPairs = list()
    # for i in range(len(validMoves)):
    #     action1 = validMoves[i]
    #     for j in range(len(validMoves) - i - 1):
    #         action2 = validMoves[j + 1 + i]
    #         pair = (action1, action2)
    #         if checkSymmetry(board, action1, action2):
    #             symmetricalMoves.append(pair)
    #         checkedPairs.append(pair)

    # if depth == MAX_DEPTH:
    #     pp(symmetricalMoves)

    # # Remove symmetrical moves
    # for movePair in symmetricalMoves:
    #     move = movePair[0]
    #     try:
    #         validMoves.remove(move)
    #     except:
    #         pass

    # Iterate over each actions available
    for action in validMoves:
        boardResult = result(board, action)
        
        # Call eval() for the resulting board from the action
        newScore, _ = eval(boardResult, path, depth - 1, alpha=alpha, beta=beta, table=table)

        # If its the maxPlayer's turn, update the new score if larger than current score
        if maxPlayer:
            if newScore > score:
                score = newScore
                optAction = action
            alpha = max(alpha, score)

        # If its the minPlayer's turn, update the new score if smaller than current score
        else:
            if newScore < score:
                score = newScore
                optAction = action
            beta = min(beta, score)

        if depth == MAX_DEPTH:
            # pp(boardResult)
            print(f"{newScore}: ({action[0]}, {action[1]}, {alpha}/{beta})")# "a:", alpha, "b:", beta)
            # alpha = -math.inf
            # beta = math.inf

        if alpha >= beta:
            break

    path.remove(boardHashed)
    
    # (* Transposition Table Store; node is the lookup key for ttEntry *)
    # ttEntry.value := value
    # if value ≤ alphaOrig then
    #     ttEntry.flag := UPPERBOUND
    # else if value ≥ β then
    #     ttEntry.flag := LOWERBOUND
    # else
    #     ttEntry.flag := EXACT
    # ttEntry.depth := depth
    # ttEntry.is_valid := true
    # transpositionTableStore(node, ttEntry)

    entry = {}
    entry["score"] = score
    entry["depth"] = depth
    entry["action"] = action 
    if score <= alphaOrig:
        entry["flag"] = UPPERBOUND
    elif score >= beta:
        entry["flag"] = LOWERBOUND
    else:
        entry["flag"] = EXACT
    table[boardHashed] = entry
    
    return (score, optAction)


def hashBoard(board):
    # to be used with sets
    hashable_version = tuple(cell for row in board for cell in row)
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


     
    