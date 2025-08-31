
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


def boardToPosition(board_flat):
    # - storing the position of each "tick" rather than value of each cell
    # So each tick can be stored in 3 bits, but in total the whole board is 3 bytes for easier access

    CELL_MAP = {
        -3: 0,
        -2: 1,
        -1: 2,
        1:  3,
        2:  4,
        3:  5,
    }

    location_arr = [0x0F for x in range(6)]
    for i, cell in enumerate(board_flat):
        if cell in CELL_MAP:
            location_arr[CELL_MAP[cell]] = i

    return location_arr


def encodeState(board_flat, turn):

    location_arr = boardToPosition(board_flat) 

    # turn_sign = 1 if (turn_sign == 1) else 0
    encoded_bytes = bytes([
        (location_arr[0] << 4) | location_arr[1],
        (location_arr[2] << 4) | location_arr[3],
        (location_arr[4] << 4) | location_arr[5],
        1 if (turn == X) else 0
    ])

    return encoded_bytes


def decodeState(state_encoded):

    turn = X if (state_encoded[3] & 0x01 == 1) else O
    
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

    state = {
        "board": board,
        "turn" : turn,
    }

    return state


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

def get_canonical_form(board, turn):

    # -- getting the canonical state form -- #
    min_state_encoded = encodeState(flatten_board(board), turn)

    for transform_map in TRANSFORMATION_MAPS:

        flat_board = flatten_board(board)
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

    states_list.add(get_canonical_form(initial_state["board"], initial_state["turn"]))
    queue.append((initial_state, depth))

    while queue:
        # get a vertex from queue
        state, depth = queue.popleft()
        # if depth == 2:
        #     print(f"Turn: {state["turn"]}, Depth: {depth}")

        if winner(state) != 0:
            continue

        # if not in list, add to list and queue
        moves = get_moves(state)
        for move in moves:
            newstate = result(state, move)
            if get_canonical_form(newstate["board"], newstate["turn"]) in states_list:
                continue
            else:
                states_list.add(get_canonical_form(newstate["board"], newstate["turn"]))
                queue.append((newstate, depth+1))
                # print(len(states_list), depth+1)

    print(f"Total states: {len(states_list)}, Depth: {depth+1}")
    return states_list


def findDuplicates(states_encoded):

    duplicates_pair = set()
    duplicates = set()
    
    for state_encoded in states_encoded:
        if state_encoded in duplicates_pair:
            continue

        state = decodeState(state_encoded)
        board = state["board"]
        turn = state["turn"]
        turn = X if turn == O else O
        reversed_state = encodeState(flatten_board(board), turn)

        if reversed_state in duplicates_pair:
            continue
        elif reversed_state in states_encoded:
            duplicates_pair.add(state_encoded)
            duplicates_pair.add(reversed_state)
            # gather the state that is O to be removed so that X states with X turn is kept
            if state["turn"] == O:
                duplicates.add(state_encoded)
            else:
                duplicates.add(reversed_state)
    
    print(f"Found {len(duplicates_pair)} duplicate pairs (same board, diff turn)")

    return duplicates


def evaluate_best_moves(states_encoded):
    # Base Scores
    MAX_SCORE = 100
    MIN_SCORE = -100
    DRAW_SCORE = 0

    scores = {}
    
    # Create a lookup for the children of each state to avoid re-calculating
    # children = {encoded_state: set((move1, child1), (move2, child2), ...)}
    children = {}
    for state_encoded in states_encoded:

        state = decodeState(state_encoded)

        # Only calculate children for non-terminal states
        if winner(state) == 0:
            children[state_encoded] = set([(move, get_canonical_form(result(state, move)["board"], result(state, move)["turn"])) for move in get_moves(state)])
        else:
            children[state_encoded] = set()

        # 1. Init scores
        state_winner = winner(state)
        if state_winner == X:
            scores[state_encoded] = MAX_SCORE
            # print("winn")
        elif state_winner == O:
            scores[state_encoded] = MIN_SCORE
            # print("loss")
        else:
            scores[state_encoded] = DRAW_SCORE


    # 2. Iteration until convergence
    iteration_count = 0
    while True:
        iteration_count += 1
        print(f"Starting iteration {iteration_count}...")
        
        # Keep track of changes in a single pass
        changes = 0
        
        # Go through every state that is not a terminal win/loss
        for state_encoded, children_data in children.items():
            if len(children_data) == 0:
                continue

            state_children_encoded = [data[1] for data in children_data]

            # Get the current scores of all children states
            # Note: We use the scores from the *previous* iteration to calculate the new ones
            child_scores = [scores[state_child_encoded] for state_child_encoded in state_children_encoded]
            # pprint(child_scores)

            # Apply the minimax principle
            best_child_score = 0
            if decodeState(state_encoded)["turn"] == X:
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

            if scores[state_encoded] != new_score:
                scores[state_encoded] = new_score
                changes += 1

        print(f"Iteration {iteration_count} finished with {changes} updates.")
        
        # 3. Convergence Check
        if changes == 0:
            # pprint(children)
            print("Scores have converged. Halting.")
            break


    # Normalize the scores
    score_positive = min([score for score in scores.values() if score != 0 and score > 0])
    score_negative = max([score for score in scores.values() if score != 0 and score < 0])
    for state_encoded, score in scores.items():
        if score > 0:
            score = score - score_positive + 1
        elif score < 0:
            score = score - score_negative - 1
        scores[state_encoded] = score
    print(f"Max Score: {max(scores.values())}")
    print(f"Min Score: {min(scores.values())}")

    # Store the new best moves
    best_moves = {}
    for state_encoded, children_data in children.items():
        if len(children_data) == 0:
            continue
        if decodeState(state_encoded)["turn"] == X:
            best_moves[state_encoded] = [(move, scores[child]) for move, child in children_data if scores[child] == scores[state_encoded] + 1]
        else:
            best_moves[state_encoded] = [(move, scores[child]) for move, child in children_data if scores[child] == scores[state_encoded] - 1]

    pprint(best_moves)

    move_scores = {}
    for state_encoded, children_data in children.items():
        if len(children_data) == 0:
            continue
        move_scores[state_encoded] = [(move, scores[child], child) for move, child in children_data]

    print("")
    print(f"Found scores for {len(states_encoded)} states")
    print(f"Found best moves for {len(best_moves)} states")
    print("")

    return (scores, move_scores, best_moves)



def storeMoves(states_encoded, states_duplicate, best_moves):
    
    encoded_moves = set()

    for state_encoded in states_encoded:
        state = decodeState(state_encoded)
        board_flat = flatten_board(state["board"])
        turn = state["turn"]

        location_arr = boardToPosition(board_flat)

        if (state_encoded in states_duplicate):
            if (turn == O):
                raise KeyError  # the duplicates thats left should only be X's turn
            best_move_x = best_moves[state_encoded][0]
            state_o = encodeState(board_flat, O)
            best_move_o = best_moves[state_o][0]

        elif (turn == X):
            pprint(best_moves[state_encoded])
            best_move_x = best_moves[state_encoded][0]
            best_move_o = 0x0F

        elif (turn == O):
            best_move_x = 0x0F
            best_move_o = best_moves[state_encoded][0]


        encoded_bytes = bytes([
            (location_arr[0] << 4) | location_arr[1],
            (location_arr[2] << 4) | location_arr[3],
            (location_arr[4] << 4) | location_arr[5],
            (    best_move_x << 4) | best_move_o,
        ])

        encoded_moves.add(encoded_bytes)
    
    return encoded_moves


if __name__ == "__main__":
    
    states_encoded = generate_states()
    scores, move_scores, best_moves = evaluate_best_moves(states_encoded)

    board_flat = flatten_board(initial_state()["board"])
    pprint([(score, decodeState(state)) for move, score, state in move_scores[encodeState(board_flat, X)]])


    # Optimising the amount of states to be stored
    print("")
    print("Optimising...")
    
    # 1 - remove terminal states
    original_len = len(states_encoded)
    optimised_states = set([state for state in states_encoded if winner(decodeState(state)) == 0])
    new_len = len(optimised_states)
    print(f"1. Removed terminal states -> {original_len} to {new_len} (-{original_len - new_len})")

    # 2 - find board duplicates but diff turns
    original_len = len(optimised_states)
    duplicates = findDuplicates(optimised_states)
    for duplicate in duplicates:
        optimised_states.remove(duplicate)
    new_len = len(optimised_states)
    print(f"2. Removed duplicate states -> {original_len} to {new_len} (-{original_len - new_len})")


    # pprint([decodeState(state) for state in optimised_states if scores[state] == 17])

    # 3 - remove the states that is {depth} moves from winning
    depth_to_remove = 7
    for depth in range(depth_to_remove+1):
        original_len = len(optimised_states)
        state_to_remove = set()
        for state in optimised_states:
            state_score = scores[state]
            if state_score >= 18-depth or state_score <= -18+depth:
                state_to_remove.add(state)
        for state in state_to_remove:
            optimised_states.remove(state)
        new_len = len(optimised_states)
        print(f"3.{depth} Removed states that is {depth} moves to winning -> {original_len} to {new_len} (-{original_len - new_len})")

    print("Storing best moves to the 4 bytes")
    encoded_best_moves = storeMoves(optimised_states, duplicates, best_moves)

    # pprint([decodeState(state) for state in optimised_states if scores[state] == 17])







