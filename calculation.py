
import collections
from copy import deepcopy

X = 3
O = -3
EMPTY = 0

validStates = [-3, -2, -1, 1, 2, 3]


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


def get_moves(state):
    """
    Returns list of all possible actions (i, j) available on the board.
    """
    moves = list()

    for i, row in enumerate(state["board"]):
        for j, cell in enumerate(row):
            if cell == EMPTY:
                moves.append((i,j))

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


def generate_states():

    starting_state = initial_state()

    states = BFS(starting_state)

    return states



def BFS(initial_state):

    states_list = set()
    queue = collections.deque()
    
    states_list.add(hashBoard(initial_state))
    queue.append(initial_state)

    while queue:
        # get a vertex from queue
        state = queue.popleft()

        if winner(state) != None:
            continue

        # if not in list, add to list and queue
        moves = get_moves(state)
        for move in moves:
            newstate = result(state, move)
            if hashBoard(newstate) in states_list:
                continue
            else:
                states_list.add(hashBoard(newstate))
                queue.append(newstate)

        print(len(states_list))

    return states_list


def hashBoard(state):
    
    hash = [cell for row in state["board"] for cell in row]
    hash.append(state["turn"])
    hashable_version = tuple(hash)
    
    return hashable_version


if __name__ == "__main__":
    states = generate_states()
    print(len(states))

