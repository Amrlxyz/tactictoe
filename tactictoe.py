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

    maxPlayer = True if player(board) == X else False
    print("\n" + ("MaxPlayer" if maxPlayer else "MinPlayer"))
    optScore  = -math.inf if maxPlayer else math.inf
    optAction = None

    path = list()
    validMoves = list(actions(board))
    alpha = -math.inf
    beta = math.inf

    for action in validMoves:
        boardResult = result(board, action)

        # Starts the recursive function and get the optimal action
        score, _, _ = eval(boardResult, path, MAX_DEPTH, alpha=alpha, beta=beta, table=transposition_table)

        if maxPlayer:
            if score > optScore:
                optScore = score
                optAction = action
            alpha = max(alpha, score)
            
        else:
            if score < optScore:
                optScore = score
                optAction = action
            beta = min(beta, score)

        if alpha >= beta:
            break

        print(f"{score}: {action}  {alpha}/{beta}")

    # Print the callcount to measure the effect of ab pruning
    print("callcount:", callcount)
    print(f"Calculation Time: {(time.time() - startTime):.4f}s")
    print(f"OPT -> Score: {optScore}, Move: {optAction}")
    print(len(transposition_table))
    # pp([(state, value) for state, value in transposition_table.items() if value["depth"] == MAX_DEPTH])

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

    # --- VISUALIZATION CODE ---
    INDENT_MAX = MAX_DEPTH + 1
    INDENT_MAX = 0

    # Calculate indentation level for printing
    indent_level = MAX_DEPTH - depth
    indent = "    " * indent_level

    if indent_level < INDENT_MAX: 
        print(f"{indent}Depth {depth}: Player {player(board)}, Alpha={alpha}, Beta={beta}, Board={board}")
    # --- END VISUALIZATION CODE ---

    EXACT = 0
    UPPERBOUND = 1
    LOWERBOUND = 2

    alphaOrig = alpha
    betaOrig = beta
    isValid = False

    boardHashed = hashBoard(board)

    if boardHashed in table:
        entry = table[boardHashed]
        if entry["depth"] >= depth:     
            score = entry["score"]
            flag = entry["flag"]
            action = entry["action"]
            if flag == EXACT:
                if indent_level < INDENT_MAX: 
                    print(f"{indent}L--> TABLE EXACT: Returning Score: {score}, Best Move: {action}, {boardHashed}")
                return (score, action, True)
            elif flag == LOWERBOUND and score >= beta:
                if indent_level < INDENT_MAX: 
                    print(f"{indent}L--> TABLE LOWER: Returning Score: {score}, Best Move: {action}, {boardHashed}")
                return (score, action, True)
            elif flag == UPPERBOUND and score <= alpha:
                if indent_level < INDENT_MAX: 
                    print(f"{indent}L--> TABLE UPPER: Returning Score: {score}, Best Move: {action}, {boardHashed}")
                return (score, action, True)

    if boardHashed in path:
        score = 0
        if indent_level < INDENT_MAX: 
            print(f"{indent}L-> Path Repeated! Score: {score}, Board: {boardHashed}")
        return (score, None, False)

    # If terminal board, just return the utility as score and None as optimal Action
    if terminal(board):
        score = utility(board) * depth 
        if indent_level < INDENT_MAX: 
            print(f"{indent}L-> Terminal Node! Score: {score}, Prev Board: {path[-1]}, Curr Board: {boardHashed}")
        return (score, None, True)
    
    if depth == 0:
        score = utility(board)
        if indent_level < INDENT_MAX: 
            print(f"{indent}L-> Depth Limit! Score: {score}, Board: {boardHashed}")
        # print(indent + "Depth Limited")
        return (score, None, False)

    # Determine current player
    maxPlayer = True if player(board) == X else False
    optScore = -math.inf if maxPlayer else math.inf
    optAction = None        # Set optimal action as none since none has been explored yet

    path.append(boardHashed)
    validMoves = list(actions(board))

    # Iterate over each actions available
    for action in validMoves:
        boardResult = result(board, action)
        
        # Call eval() for the resulting board from the action
        score, optNextAction, isNextValid = eval(boardResult, path, depth - 1, alpha=alpha, beta=beta, table=table)

        # If its the maxPlayer's turn, update the new score if larger than current score
        if maxPlayer:
            if score > optScore:
                optScore = score
                optAction = action
                isValid = isNextValid
            alpha = max(alpha, optScore)
            if optScore >= beta:
                if indent_level < INDENT_MAX: 
                    print(f"{indent}--> PRUNING! (Alpha={alpha}, Beta={beta})")
                break

        # If its the minPlayer's turn, update the new score if smaller than current score
        else:
            if score < optScore:
                optScore = score
                optAction = action
                isValid = isNextValid
            beta = min(beta, optScore)
            if optScore <= alpha:
                if indent_level < INDENT_MAX: 
                    print(f"{indent}--> PRUNING! (Alpha={alpha}, Beta={beta})")
                break

    path.pop(-1)

    if isValid:
        entry = {}
        entry["score"] = optScore
        entry["action"] = optAction 
        entry["depth"] = depth    
        if maxPlayer:
            if optScore <= alphaOrig:
                entry["flag"] = UPPERBOUND
            elif optScore >= beta:
                entry["flag"] = LOWERBOUND
            else:
                entry["flag"] = EXACT
        else:
            if optScore >= betaOrig:
                entry["flag"] = LOWERBOUND
            elif optScore <= alpha:
                entry["flag"] = UPPERBOUND
            else:
                entry["flag"] = EXACT
        table[boardHashed] = entry

    # Final print showing what this level is returning
    if indent_level < INDENT_MAX: 
        print(f"{indent}L--> Returning Score: {optScore}, Best Move: {optAction}, {boardHashed}, Flag: {entry['flag']}")
    
    return (optScore, optAction, True)


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


     
    