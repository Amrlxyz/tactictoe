import sys
sys.setrecursionlimit(10000)
from typing import List, Tuple, Optional, Dict, Set

WIN_COMBOS: Tuple[Tuple[int, int, int], ...] = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6)
)

Board = Tuple[str, ...]
Order = Tuple[int, ...]
State = Tuple[Board, Order, Order, str]
Outcome = int

def check_winner(board: Board) -> Optional[str]:
    for a, b, c in WIN_COMBOS:
        if board[a] != " " and board[a] == board[b] == board[c]:
            return board[a]
    return None

def legal_moves(board: Board) -> List[int]:
    return [i for i, v in enumerate(board) if v == " "]

def apply_move(state: State, move: int) -> State:
    board, xq, oq, player = state
    b = list(board)
    x = list(xq)
    o = list(oq)
    if player == "X":
        if len(x) == 3:
            b[x.pop(0)] = " "
        b[move] = "X"
        x.append(move)
        return (tuple(b), tuple(x), tuple(o), "O")
    else:
        if len(o) == 3:
            b[o.pop(0)] = " "
        b[move] = "O"
        o.append(move)
        return (tuple(b), tuple(x), tuple(o), "X")

MemoValue = Tuple[Outcome, Tuple[int, ...]]

class Solver:
    def __init__(self) -> None:
        self.memo: Dict[State, MemoValue] = {}
        self.nodes: int = 0

    def solve(self, state: State) -> MemoValue:
        return self._dfs(state, set())

    def _dfs(self, state: State, path: Set[State]) -> MemoValue:
        if state in self.memo:
            return self.memo[state]
        if state in path:
            # cycle detected
            self.memo[state] = (0, tuple())
            return (0, tuple())

        board, _, _, player = state
        winner = check_winner(board)
        if winner == "X":
            self.memo[state] = (1, tuple())
            return (1, tuple())
        if winner == "O":
            self.memo[state] = (-1, tuple())
            return (-1, tuple())

        moves = legal_moves(board)
        if not moves:
            self.memo[state] = (0, tuple())
            return (0, tuple())

        self.nodes += 1
        path.add(state)

        outcomes: List[Tuple[int, int]] = []
        for mv in moves:
            child = apply_move(state, mv)
            val, _ = self._dfs(child, path)
            outcomes.append((mv, val))

        path.remove(state)

        if player == "X":
            best_val = max(v for _, v in outcomes)
        else:
            best_val = min(v for _, v in outcomes)
        best_moves = tuple(m for m, v in outcomes if v == best_val)
        self.memo[state] = (best_val, best_moves)
        return (best_val, best_moves)

    def principal_variation(self, start: State) -> List[int]:
        pv: List[int] = []
        state = start
        seen: Set[State] = set()
        while state not in seen and state in self.memo:
            seen.add(state)
            _, moves = self.memo[state]
            if not moves:
                break
            mv = moves[0]
            pv.append(mv)
            state = apply_move(state, mv)
        return pv

def empty_state(start_player: str = "X") -> State:
    return (tuple([" "] * 9), tuple(), tuple(), start_player)

def render(board: Board) -> str:
    return "\n---+---+---\n".join(f" {board[i]} | {board[i+1]} | {board[i+2]} " for i in range(0, 9, 3))

def print_board(board: Board) -> None:
    idx_board = "\n---+---+---\n".join(f" {i} | {i+1} | {i+2} " for i in range(0, 9, 3))
    print(f"Indexes:\n{idx_board}\n\nBoard:\n{render(board)}")

def solve_and_report(start_player: str = "X") -> Tuple[Solver, MemoValue]:
    solver = Solver()
    start = empty_state(start_player)
    outcome, _ = solver.solve(start)
    print("=== 3-Mark Tic-Tac-Toe Solver ===")
    print(f"Start player: {start_player}")
    print(f"Solved outcome (X perspective): {outcome}")
    print(f"States evaluated: {len(solver.memo)}")
    print(f"DFS nodes visited: {solver.nodes}")
    print("One optimal line:", solver.principal_variation(start))
    return solver, (outcome, tuple())

def choose_ai_move(solver: Solver, state: State) -> int:
    if state not in solver.memo:
        solver.solve(state)
    _, moves = solver.memo[state]
    if not moves:
        return legal_moves(state[0])[0]
    for pref in [4, 0, 2, 6, 8, 1, 3, 5, 7]:
        if pref in moves:
            return pref
    return moves[0]

def interactive_play(start_player: str = "X", human: str = "X") -> None:
    solver = Solver()
    state = empty_state(start_player)
    while True:
        board, _, _, player = state
        w = check_winner(board)
        if w or not legal_moves(board):
            print_board(board)
            print(f"Game over: {'draw' if not w else w + ' wins!'}")
            return
        print_board(board)
        if player == human:
            while True:
                try:
                    mv = int(input(f"Your move ({player}): "))
                    if mv in legal_moves(board):
                        break
                except:
                    pass
                print("Invalid.")
            state = apply_move(state, mv)
        else:
            mv = choose_ai_move(solver, state)
            print(f"AI ({player}) plays {mv}")
            state = apply_move(state, mv)

if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] == "solve":
        sp = args[1].upper() if len(args) >= 2 else "X"
        solve_and_report(sp)
    elif args[0] == "play":
        sp = args[1].upper() if len(args) >= 2 else "X"
        human = args[2].upper() if len(args) >= 3 else "X"
        interactive_play(sp, human)
