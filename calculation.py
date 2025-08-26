
import collections
from copy import deepcopy
from pprint import pprint

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


def flatten_board(board):
    return [cell for row in board for cell in row]


def encodeState(board_flat, turn):

    # - encode the current turn as if its always the +ve player move, 
    # so no need to store the current turn of a board
    turn_sign = round(turn/3)
    encoded_board = [cell*turn_sign for cell in board_flat]

    CELL_MAP = {
        -3: 0,
        -2: 1,
        -1: 2,
        1:  3,
        2:  4,
        3:  5,
    }

    # - storing the position of each "tick" rather than value of each cell
    # So each tick can be stored in 3 bits, but in total the whole board is 3 bytes for easier access
    location_arr = [0x0F for x in range(6)]
    for i, cell in enumerate(encoded_board):
        if cell in CELL_MAP:
            location_arr[CELL_MAP[cell]] = i
    
    encoded_bytes = bytes([
        (location_arr[0] << 4) | location_arr[1],
        (location_arr[2] << 4) | location_arr[3],
        (location_arr[4] << 4) | location_arr[5],
    ])

    return encoded_bytes


TRANSFORMATION_MAPS = (
    # (0, 1, 2, 3, 4, 5, 6, 7, 8), # 0: Identity
    (2, 5, 8, 1, 4, 7, 0, 3, 6), # 1: Rotate 90  degrees CC
    (8, 7, 6, 5, 4, 3, 2, 1, 0), # 2: Rotate 180 degrees CC
    (6, 3, 0, 7, 4, 1, 8, 5, 2), # 3: Rotate 270 degrees CC
    (2, 1, 0, 5, 4, 3, 8, 7, 6), # 4: Flip horizontally
    (0, 3, 6, 1, 4, 7, 2, 5, 8), # 5: Flip Horizontally -> Rotate 90  CC (TL / BR Sym)
    (6, 7, 8, 3, 4, 5, 0, 1, 2), # 6: Flip Horizontally -> Rotate 180 CC (Vertical Flip)
    (8, 5, 2, 7, 4, 1, 6, 3, 0), # 7: Flip Horizontally -> Rotate 270 CC (TR / BL Sym)
)

def get_canonical_form(state):

    # -- getting the canonical state form -- #
    turn = state["turn"]
    min_state_encoded = encodeState(flatten_board(state["board"]), turn)

    for transform_map in TRANSFORMATION_MAPS:

        flat_board = flatten_board(state["board"])
        transformed_board = [flat_board[i] for i in transform_map]

        transformed_state_encoded = encodeState(transformed_board, turn)

        if transformed_state_encoded < min_state_encoded:
            min_state_encoded = transformed_state_encoded

    return min_state_encoded


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
    
    return 0


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
    depth = 0

    states_list.add(get_canonical_form(initial_state))
    queue.append((initial_state, depth))

    while queue:
        # get a vertex from queue
        state, depth = queue.popleft()

        if winner(state) != 0:
            continue

        # if not in list, add to list and queue
        moves = get_moves(state)
        for move in moves:
            newstate = result(state, move)
            if get_canonical_form(newstate) in states_list:
                continue
            else:
                states_list.add(get_canonical_form(newstate))
                queue.append((newstate, depth+1))
                print(len(states_list), depth+1)

    return states_list


def hashBoard(state):
    
    hash = [cell for row in state["board"] for cell in row]
    hash.append(state["turn"])
    hashable_version = tuple(hash)
    
    return hashable_version


def hashToState(hash):
    board = [list(hash[0:3]), list(hash[3:6]), list(hash[6:9])]
    
    return {
        "board": board,
        "turn" : hash[9]
    }


def hashDiff(hash1, hash2):
    """
    Returns move that changes hash1 to hash2
    """
    player = hash1[-1]
    board_index = hash2.index(player)

    return (board_index // 3, board_index % 3)


def evaluate_best_moves(states_hash):
    # Create a lookup for the children of each state to avoid re-calculating
    children = {}
    for hash_val in states_hash:
        state = hashToState(hash_val)
        # Only calculate children for non-terminal states
        if winner(state) == 0:
            children[hash_val] = [hashBoard(result(state, move)) for move in get_moves(state)]
        else:
            children[hash_val] = []

    # Base Scores
    MAX_SCORE = 100
    MIN_SCORE = -100
    DRAW_SCORE = 0

    scores = {}

    # 1. Initialization
    for hash_val in states_hash:
        state_winner = winner(hashToState(hash_val))
        if state_winner == X:
            scores[hash_val] = MAX_SCORE
        elif state_winner == O:
            scores[hash_val] = MIN_SCORE
        else:
            scores[hash_val] = DRAW_SCORE


    # 2. Iteration until convergence
    iteration_count = 0
    while True:
        iteration_count += 1
        print(f"Starting iteration {iteration_count}...")
        
        # Keep track of changes in a single pass
        changes = 0
        
        # Go through every state that is not a terminal win/loss
        for hash_val in states_hash:
            if winner(hashToState(hash_val)) != 0:
                continue

            # Get the current scores of all children states
            # Note: We use the scores from the *previous* iteration to calculate the new ones
            child_hashes = children[hash_val]
            
            child_scores = [scores[child_hash] for child_hash in child_hashes]

            # Apply the minimax principle
            best_child_score = 0
            if hashToState(hash_val)["turn"] == X:
                best_child_score = max(child_scores)
            else:  # Turn is O
                best_child_score = min(child_scores)
            
            # Adjust the score based on depth
            new_score = 0
            if best_child_score > DRAW_SCORE:  # It's a path to a win
                new_score = best_child_score - 1
            elif best_child_score < DRAW_SCORE: # It's a path to a loss
                new_score = best_child_score + 1
            else: # It's a draw
                new_score = DRAW_SCORE

            if scores[hash_val] != new_score:
                scores[hash_val] = new_score
                changes += 1

        print(f"Iteration {iteration_count} finished with {changes} updates.")
        
        # 3. Convergence Check
        if changes == 0:
            print("Scores have converged. Halting.")
            break

    # Store the new best moves
    best_moves = {}
    for hash_val in scores:
        best_moves[hash_val] = [hashDiff(hash_val, child_hash) for child_hash in children[hash_val] if scores[child_hash] == scores[hash_val] + 1]
            
    print(f"\nFound scores for {len(scores)} states.")
    # You can now inspect the 'scores' dictionary for the optimal value of any state.
    # For example, to find the score of the initial empty board:
    initial_hash = hashBoard(initial_state())
    print(f"Starting board optimal score: {MAX_SCORE - scores[initial_hash]}, Best Moves: {best_moves[initial_hash]}")

    # pprint([move for move in best_moves if move == []])
    # pprint([score for score in scores if score == 0])

    return (scores, best_moves)


if __name__ == "__main__":
    
    states_hash = generate_states()
    print(f"Generated {len(states_hash)} unique states.")

    scores, best_moves = evaluate_best_moves(states_hash)

    initial_hash = hashBoard(initial_state())
    pprint([
        (move, scores[hashBoard(result(initial_state(), move))]) for move in get_moves(initial_state())
    ])

    pprint([(scores[state_hash], state_hash, best_moves[state_hash]) for state_hash in states_hash if scores[state_hash] <= 100-17 and scores[state_hash] > 0])

