
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
    
    # turn_sign = 1 if (turn_sign == 1) else 0
    encoded_bytes = bytes([
        (location_arr[0] << 4) | location_arr[1],
        (location_arr[2] << 4) | location_arr[3],
        (location_arr[4] << 4) | location_arr[5],
        # turn_sign,
    ])

    return encoded_bytes


def decodeBoard(state_encoded):

    location_arr = [
        state_encoded[0] >> 4,
        state_encoded[0] & 0x0F,
        state_encoded[1] >> 4,
        state_encoded[1] & 0x0F,
        state_encoded[2] >> 4,
        state_encoded[2] & 0x0F,
    ]

    CELL_MAP_REV = {
        0: -3,
        1: -2,
        2: -1,
        3:  1,
        4:  2,
        5:  3,
    }

    board_flat = [0 for x in range(9)]
    for i, location in enumerate(location_arr):
        if location != 0x0F:
            board_flat[location] = CELL_MAP_REV[i]

    board = [board_flat[i:i+3] for i in range(0, len(board_flat), 3)]

    return board


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
                # print(len(states_list), depth+1)

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


def evaluate_best_moves(states_encoded):
    # Base Scores
    MAX_SCORE = 100
    MIN_SCORE = -100
    DRAW_SCORE = 0

    scores_min = {}
    scores_max = {}
    
    # Create a lookup for the children of each state to avoid re-calculating
    children = {}
    for state_encoded in states_encoded:

        board = decodeBoard(state_encoded)
        state = {
            "turn": X,
            "board": board
        }
        # Only calculate children for non-terminal states
        if winner(state) == 0:
            children[state_encoded] = set([get_canonical_form(result(state, move)) for move in get_moves(state)])
        else:
            children[state_encoded] = set()


        # 1. Init scores
        state_winner = winner(state)
        if state_winner == X:
            scores_min[state_encoded] = MAX_SCORE
            scores_max[state_encoded] = MAX_SCORE
            # print("winn")
        elif state_winner == O:
            scores_min[state_encoded] = MIN_SCORE
            scores_max[state_encoded] = MIN_SCORE
            # print("loss")
        else:
            scores_min[state_encoded] = DRAW_SCORE
            scores_max[state_encoded] = DRAW_SCORE


    # 2. Iteration until convergence
    iteration_count = 0
    while True:
        iteration_count += 1
        print(f"Starting iteration {iteration_count}...")
        
        # Keep track of changes in a single pass
        changes = 0
        
        # Go through every state that is not a terminal win/loss
        for state_encoded, state_children_encoded in children.items():
            if len(state_children_encoded) == 0:
                continue

            # Get the current scores of all children states
            # Note: We use the scores from the *previous* iteration to calculate the new ones
            child_scores_min = [scores_min[state_child_encoded] for state_child_encoded in state_children_encoded]
            child_scores_max = [scores_max[state_child_encoded] for state_child_encoded in state_children_encoded]
            child_scores = child_scores_max + child_scores_min
            # pprint(child_scores)

            # Apply the minimax principle
            # best_child_score = 0
            # if decodeBoard(state_encoded)["turn"] == X:
            # if True:
            #     best_child_score = max(child_scores)
            # else:  # Turn is O
            #     best_child_score = min(child_scores)
            # best_child_score = min(child_scores)
            
            # Get the new max out of all children
            new_max = max(child_scores)
            if new_max > DRAW_SCORE:
                new_max -= 1
            elif new_max < DRAW_SCORE:
                new_max += 1
            else:
                new_max = 0


            # Get the new min out of all children  
            new_min = min(child_scores)
            if new_min > DRAW_SCORE:
                new_min -= 1
            elif new_min < DRAW_SCORE:
                new_min += 1
            else:
                new_min = 0

            # # Adjust the score based on depth
            # new_score = 0
            # if best_child_score > DRAW_SCORE:  # It's a path to a win
            #     new_score = best_child_score - 1
            # elif best_child_score < DRAW_SCORE: # It's a path to a loss
            #     new_score = best_child_score + 1
            # else: # It's a draw
            #     new_score = DRAW_SCORE

            if scores_max[state_encoded] != new_max:
                scores_max[state_encoded] = new_max
                changes += 1

            if scores_min[state_encoded] != new_min:
                scores_min[state_encoded] = new_min
                changes += 1

        print(f"Iteration {iteration_count} finished with {changes} updates.")
        
        # 3. Convergence Check
        if changes == 0:
            # pprint(children)
            print("Scores have converged. Halting.")
            break

    # Store the new best moves
    best_moves = {}
    # for hash_val in scores:
    #     best_moves[hash_val] = [hashDiff(hash_val, child_hash) for child_hash in children[hash_val] if scores[child_hash] == scores[hash_val] + 1]
    # for hash_val in scores:
    #     best_moves[hash_val] = [hashDiff(hash_val, child_hash) for child_hash in children[hash_val] if scores[child_hash] == scores[hash_val] + 1]
            
    pprint(max([score for _, score in scores_min.items() if score != 0]))
    
    print(f"\nFound scores for {len(states_encoded)} states.")

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

