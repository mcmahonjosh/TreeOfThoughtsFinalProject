import os
import re
import pandas as pd
from tot.tasks.base import Task, DATA_PATH
from tot.prompts.sudoku import *


def board_to_string(board):
    """Convert a list of 16 chars/digits to a 16-char puzzle string."""
    return ''.join(str(x) for x in board)


def string_to_board(s):
    """Convert a puzzle string to a list of 16 characters."""
    s = re.sub(r'[^0-4]', '', str(s))
    if len(s) != 16:
        raise ValueError(f'Expected 16 digits for a 4x4 Sudoku board, got {len(s)}: {s}')
    return list(s)


def render_board(board):
    """Render a 16-cell board as 4 rows."""
    board = list(board)
    rows = []
    for r in range(4):
        rows.append(' '.join(board[r * 4:(r + 1) * 4]))
    return '\n'.join(rows)


def extract_solution(output):
    """
    Extract a 16-digit solution from model output.
    Supports:
    - raw 16-digit answer
    - 'Answer: 4321...'
    - 'Solution: 4321...'
    """
    output = output.strip()

    # Prefer text after Answer/Solution if present.
    match = re.search(r'(?:answer|solution)\s*:\s*([1-4]{16})', output, re.IGNORECASE)
    if match:
        return match.group(1)

    # Otherwise use the last 16-digit 1-4-only sequence.
    matches = re.findall(r'[1-4]{16}', output)
    if matches:
        return matches[-1]

    return ''


def is_valid_group(vals):
    """A group is valid if its nonzero values have no duplicates."""
    vals = [v for v in vals if v != '0']
    return len(vals) == len(set(vals))


def is_complete_group(vals):
    return sorted(vals) == ['1', '2', '3', '4']


def check_board(puzzle, board):
    """
    Return info about a board:
    - valid_partial: no duplicate nonzero values and givens preserved
    - complete_valid: solved Sudoku
    """
    puzzle = string_to_board(puzzle)
    board = string_to_board(board)

    # Keep given digits fixed.
    for p, b in zip(puzzle, board):
        if p != '0' and p != b:
            return {
                'valid_partial': False,
                'complete_valid': False,
                'reason': 'given digit changed'
            }

    groups = []

    # Rows.
    for r in range(4):
        groups.append(board[r * 4:(r + 1) * 4])

    # Columns.
    for c in range(4):
        groups.append([board[r * 4 + c] for r in range(4)])

    # 2x2 boxes.
    for br in [0, 2]:
        for bc in [0, 2]:
            groups.append([
                board[(br + dr) * 4 + (bc + dc)]
                for dr in range(2)
                for dc in range(2)
            ])

    valid_partial = all(is_valid_group(group) for group in groups)
    complete_valid = valid_partial and all(is_complete_group(group) for group in groups)

    return {
        'valid_partial': valid_partial,
        'complete_valid': complete_valid,
        'reason': ''
    }


def apply_move(puzzle, current, move):
    """
    Apply a move like:
    r2c3 = 4

    Returns the new 16-char board string.
    """
    puzzle_board = string_to_board(puzzle)
    board = string_to_board(current)

    match = re.search(r'r([1-4])c([1-4])\s*=\s*([1-4])', move.strip(), re.IGNORECASE)
    if not match:
        return current

    r = int(match.group(1)) - 1
    c = int(match.group(2)) - 1
    val = match.group(3)
    idx = r * 4 + c

    # Do not overwrite original givens.
    if puzzle_board[idx] != '0':
        return current

    board[idx] = val
    return board_to_string(board)


def get_current_board(x, y):
    """
    y is the accumulated trajectory of moves.
    Start from puzzle x and apply each rXcY = D move in y.
    """
    current = x
    for line in y.strip().split('\n'):
        current = apply_move(x, current, line)
    return current


class SudokuTask(Task):
    """
    Input (x)   : a 16-digit 4x4 Sudoku puzzle string
    Output (y)  : either a solved 16-digit string or a trajectory of cell-filling moves
    Reward (r)  : 1 if solved correctly, else 0
    """

    def __init__(self, file='4x4_sudoku_unique_puzzles.csv'):
        """
        Expected CSV columns:
        Puzzle,Solution
        """
        super().__init__()
        path = os.path.join(DATA_PATH, 'sudoku_4x4', file)
        df = pd.read_csv(path, dtype={'Puzzle': str, 'Solution': str})

        self.data = list(df['Puzzle'])
        self.solutions = list(df['Solution'])

        self.value_cache = {}

        # For ToT/propose mode, at most 16 cells can be filled.
        # Most puzzles have fewer blanks, but this is safe.
        self.steps = 16
        self.stops = ['\n'] * self.steps

    def __len__(self) -> int:
        return len(self.data)

    def get_input(self, idx: int) -> str:
        return self.data[idx]

    def test_output(self, idx: int, output: str):
        puzzle = self.data[idx]
        gt = self.solutions[idx]

        # Case 1: direct final solution from standard/cot prompting.
        solution = extract_solution(output)
        if solution:
            info = check_board(puzzle, solution)
            return {
                'r': int(solution == gt and info['complete_valid']),
                'r_valid': int(info['complete_valid']),
                'solution': solution
            }

        # Case 2: trajectory of moves from propose prompting.
        current = get_current_board(puzzle, output)
        info = check_board(puzzle, current)
        return {
            'r': int(current == gt and info['complete_valid']),
            'r_valid': int(info['complete_valid']),
            'solution': current
        }

    @staticmethod
    def standard_prompt_wrap(x: str, y: str = '') -> str:
        return standard_prompt.format(input=x) + y

    @staticmethod
    def cot_prompt_wrap(x: str, y: str = '') -> str:
        return cot_prompt.format(input=x) + y

    @staticmethod
    def propose_prompt_wrap(x: str, y: str = '') -> str:
        current = get_current_board(x, y)

        # If already complete, ask for final answer.
        if '0' not in current:
            return value_last_step_prompt.format(input=x, answer=current)

        return propose_prompt.format(
            input=x,
            board=render_board(current)
        )

    @staticmethod
    def value_prompt_wrap(x: str, y: str) -> str:
        current = get_current_board(x, y)

        if '0' not in current:
            return value_last_step_prompt.format(input=x, answer=current)

        return value_prompt.format(
            input=x,
            board=render_board(current)
        )

    @staticmethod
    def value_outputs_unwrap(x: str, y: str, value_outputs: list) -> float:
        value_names = [_.strip().split('\n')[-1].strip().lower() for _ in value_outputs]

        value_map = {
            'impossible': 0.001,
            'likely': 1,
            'sure': 20
        }

        value = sum(score * value_names.count(name) for name, score in value_map.items())

        # Small deterministic bonus/penalty from actual board validity.
        current = get_current_board(x, y)
        info = check_board(x, current)

        if not info['valid_partial']:
            return 0.001

        if info['complete_valid']:
            return max(value, 20)

        return value