import os
import re
from typing import Dict, Iterable, List, Optional

import pandas as pd

from tot.tasks.base import DATA_PATH, Task
from tot.prompts.sudoku4x4 import *


DIGITS = ('1', '2', '3', '4')
EMPTY = '0'


def normalize_board(board: str) -> str:
    """Return a 16-character raw board string, using 0 for empty cells."""
    cells = []
    for cell in re.findall(r'[0-4.]', str(board)):
        cells.append(EMPTY if cell == '.' else cell)
    if len(cells) != 16:
        raise ValueError(f'Expected 16 Sudoku cells, got {len(cells)} from: {board!r}')
    return ''.join(cells)


def raw_to_board(raw: str) -> str:
    """Convert a raw 16-character puzzle into the prompt's 4-row board format."""
    raw = normalize_board(raw)
    rows = []
    for r in range(4):
        row = raw[r * 4:(r + 1) * 4]
        rows.append(' '.join('.' if cell == EMPTY else cell for cell in row))
    return '\n'.join(rows)


def board_to_raw(board: str) -> str:
    """Convert a prompt-format 4x4 board into the raw CSV format."""
    return normalize_board(board)


def _raw_to_solution_board(raw: str) -> str:
    raw = normalize_board(raw)
    rows = []
    for r in range(4):
        rows.append(' '.join(raw[r * 4:(r + 1) * 4]))
    return '\n'.join(rows)


def _read_sudoku_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, sep=None, engine='python').fillna('')


def _load_solution_map(solution_file: str) -> Dict[str, str]:
    if not solution_file:
        return {}

    path = os.path.join(DATA_PATH, 'sudoku_4x4', solution_file)
    if not os.path.exists(path):
        return {}

    df = _read_sudoku_csv(path)
    if 'Puzzle' not in df.columns or 'Solution' not in df.columns:
        return {}

    mapping = {}
    for puzzle, solution in zip(df['Puzzle'], df['Solution']):
        try:
            mapping[normalize_board(puzzle)] = normalize_board(solution)
        except ValueError:
            continue
    return mapping


def _groups(raw: str) -> Iterable[List[str]]:
    raw = normalize_board(raw)

    for r in range(4):
        yield list(raw[r * 4:(r + 1) * 4])

    for c in range(4):
        yield [raw[r * 4 + c] for r in range(4)]

    for br in (0, 2):
        for bc in (0, 2):
            yield [
                raw[(br + dr) * 4 + (bc + dc)]
                for dr in range(2)
                for dc in range(2)
            ]


def _is_valid_group(values: List[str]) -> bool:
    filled = [value for value in values if value != EMPTY]
    return len(filled) == len(set(filled))


def _is_complete_group(values: List[str]) -> bool:
    return sorted(values) == list(DIGITS)


def candidates_for_cell(raw: str, index: int) -> List[str]:
    raw = normalize_board(raw)
    if raw[index] != EMPTY:
        return []

    row, col = divmod(index, 4)
    used = set(raw[row * 4:(row + 1) * 4])
    used.update(raw[r * 4 + col] for r in range(4))

    box_row = (row // 2) * 2
    box_col = (col // 2) * 2
    used.update(
        raw[(box_row + dr) * 4 + (box_col + dc)]
        for dr in range(2)
        for dc in range(2)
    )
    return [digit for digit in DIGITS if digit not in used]


def has_forced_move(raw: str) -> bool:
    raw = normalize_board(raw)
    return any(
        cell == EMPTY and len(candidates_for_cell(raw, idx)) == 1
        for idx, cell in enumerate(raw)
    )


def legal_moves(raw: str) -> List[Dict[str, object]]:
    raw = normalize_board(raw)
    moves = []
    for idx, cell in enumerate(raw):
        if cell != EMPTY:
            continue
        candidates = candidates_for_cell(raw, idx)
        if not candidates:
            continue
        row, col = divmod(idx, 4)
        for digit in candidates:
            moves.append({
                'row': row + 1,
                'col': col + 1,
                'digit': digit,
                'n_candidates': len(candidates),
            })
    return sorted(moves, key=lambda move: (move['n_candidates'], move['row'], move['col'], move['digit']))


def check_board(puzzle: str, board: str) -> Dict[str, object]:
    puzzle = normalize_board(puzzle)
    board = normalize_board(board)

    for idx, (given, value) in enumerate(zip(puzzle, board)):
        if given != EMPTY and given != value:
            row, col = divmod(idx, 4)
            return {
                'valid_partial': False,
                'complete_valid': False,
                'reason': f'given digit changed at r{row + 1}c{col + 1}',
            }

    if not all(_is_valid_group(group) for group in _groups(board)):
        return {
            'valid_partial': False,
            'complete_valid': False,
            'reason': 'duplicate digit in a row, column, or box',
        }

    for idx, cell in enumerate(board):
        if cell == EMPTY and not candidates_for_cell(board, idx):
            row, col = divmod(idx, 4)
            return {
                'valid_partial': False,
                'complete_valid': False,
                'reason': f'no legal candidates at r{row + 1}c{col + 1}',
            }

    complete_valid = all(_is_complete_group(group) for group in _groups(board))
    return {
        'valid_partial': True,
        'complete_valid': complete_valid,
        'reason': '',
    }


def apply_move(puzzle: str, current: str, move: str) -> str:
    puzzle = normalize_board(puzzle)
    board = list(normalize_board(current))

    match = re.search(r'r([1-4])c([1-4])\s*=\s*([1-4])', move, re.IGNORECASE)
    if not match:
        return ''.join(board)

    row = int(match.group(1)) - 1
    col = int(match.group(2)) - 1
    value = match.group(3)
    idx = row * 4 + col

    if puzzle[idx] != EMPTY or board[idx] != EMPTY:
        return ''.join(board)

    candidate_board = board[:]
    candidate_board[idx] = value
    return ''.join(candidate_board)


def get_current_board(x: str, y: str = '') -> str:
    puzzle = normalize_board(x)
    current = puzzle
    for line in y.strip().split('\n'):
        current = apply_move(puzzle, current, line)
    return current


def _extract_grid_solution(output: str) -> str:
    grid_rows = []
    row_pattern = re.compile(r'^\s*([1-4])\s+([1-4])\s+([1-4])\s+([1-4])\s*$')

    for line in output.splitlines():
        match = row_pattern.match(line)
        if match:
            grid_rows.append(''.join(match.groups()))
            if len(grid_rows) > 4:
                grid_rows.pop(0)
        elif grid_rows and len(grid_rows) < 4:
            grid_rows = []

    if len(grid_rows) == 4:
        return ''.join(grid_rows)
    return ''


def extract_solution(output: str) -> str:
    output = output.strip()

    grid_solution = _extract_grid_solution(output)
    if grid_solution:
        return grid_solution

    labelled = re.search(r'(?:answer|solution)\s*:\s*([1-4]{16})', output, re.IGNORECASE)
    if labelled:
        return labelled.group(1)

    matches = re.findall(r'[1-4]{16}', output)
    return matches[-1] if matches else ''


def _last_value_label(value_output: str) -> Optional[str]:
    labels = re.findall(r'\b(sure|likely|impossible)\b', value_output.lower())
    return labels[-1] if labels else None


def _last_move_prefix(y: str):
    lines = [line for line in y.strip().split('\n') if line.strip()]
    for idx in range(len(lines) - 1, -1, -1):
        if re.search(r'r([1-4])c([1-4])\s*=\s*([1-4])', lines[idx], re.IGNORECASE):
            prefix = '\n'.join(lines[:idx])
            if prefix:
                prefix += '\n'
            return prefix, lines[idx]
    return '', ''


class Sudoku4x4Task(Task):
    """
    Input (x)  : a 4-row 4x4 Sudoku board using dots for empty cells
    Output (y) : either a completed 4-row board or a trajectory of rNcM = D moves
    Reward (r): 1 for a valid solved board, and exact-match when a reference is available
    """

    def __init__(
        self,
        file: str = '4x4_sudoku_unique_puzzles.csv',
        solution_file: str = '4x4_sudoku_unique_solution.csv',
    ):
        super().__init__()
        path = os.path.join(DATA_PATH, 'sudoku_4x4', file)
        df = _read_sudoku_csv(path)
        if 'Puzzle' not in df.columns:
            raise ValueError(f'{path} must contain a Puzzle column')

        self.raw_data = [normalize_board(puzzle) for puzzle in df['Puzzle']]
        solution_map = _load_solution_map(solution_file)

        self.solutions = []
        for puzzle, solution in zip(self.raw_data, df.get('Solution', [''] * len(df))):
            try:
                self.solutions.append(normalize_board(solution))
            except ValueError:
                self.solutions.append(solution_map.get(puzzle, ''))

        self.data = [raw_to_board(puzzle) for puzzle in self.raw_data]
        self.value_cache = {}
        self.steps = max((puzzle.count(EMPTY) for puzzle in self.raw_data), default=0)
        self.stops = ['\n'] * max(self.steps, 1)

    def __len__(self) -> int:
        return len(self.raw_data)

    def get_input(self, idx: int) -> str:
        return self.data[idx]

    def is_finished(self, x: str, y: str = '') -> bool:
        return EMPTY not in get_current_board(x, y)

    def state_key(self, x: str, y: str = '') -> str:
        return get_current_board(x, y)

    def is_valid_state(self, x: str, y: str = '') -> bool:
        return bool(check_board(x, get_current_board(x, y))['valid_partial'])

    def fallback_proposals(self, x: str, y: str = '') -> List[str]:
        current = get_current_board(x, y)
        info = check_board(x, current)
        if not info['valid_partial'] or info['complete_valid']:
            return []

        proposals = []
        for move in legal_moves(current):
            row = move['row']
            col = move['col']
            digit = move['digit']
            if move['n_candidates'] == 1:
                reason = 'forced: this cell has only one legal candidate'
            else:
                reason = 'legal candidate from deterministic Sudoku fallback'
            proposals.append(f'{y}r{row}c{col} = {digit} - {reason}.\n')
        return proposals

    def fallback_values(self, x: str, ys: List[str]) -> List[float]:
        values = []
        for y in ys:
            current = get_current_board(x, y)
            info = check_board(x, current)
            if not info['valid_partial']:
                values.append(0.001)
                continue
            if info['complete_valid']:
                values.append(20)
                continue

            prefix, move = _last_move_prefix(y)
            match = re.search(r'r([1-4])c([1-4])\s*=\s*([1-4])', move, re.IGNORECASE)
            if not match:
                values.append(0.001)
                continue

            row = int(match.group(1)) - 1
            col = int(match.group(2)) - 1
            digit = match.group(3)
            previous = get_current_board(x, prefix)
            candidates = candidates_for_cell(previous, row * 4 + col)

            if digit not in candidates:
                values.append(0.001)
            elif len(candidates) == 1:
                values.append(20)
            else:
                values.append(1)
        return values

    def test_output(self, idx: int, output: str):
        puzzle = self.raw_data[idx]
        gt = self.solutions[idx] if idx < len(self.solutions) else ''

        solution = extract_solution(output)
        if solution:
            info = check_board(puzzle, solution)
            solved = bool(info['complete_valid'])
            exact = not gt or solution == gt
            return {
                'r': int(solved and exact),
                'r_valid': int(solved),
                'solution': solution,
                'solution_board': _raw_to_solution_board(solution),
                'reason': info['reason'],
            }

        current = get_current_board(puzzle, output)
        info = check_board(puzzle, current)
        solved = bool(info['complete_valid'])
        exact = not gt or current == gt
        return {
            'r': int(solved and exact),
            'r_valid': int(solved),
            'solution': current,
            'solution_board': _raw_to_solution_board(current),
            'reason': info['reason'],
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
        return propose_prompt.format(
            input=raw_to_board(x),
            board=raw_to_board(current),
        )

    @staticmethod
    def value_prompt_wrap(x: str, y: str) -> str:
        current = get_current_board(x, y)
        if EMPTY not in current:
            return value_last_step_prompt.format(
                input=raw_to_board(x),
                answer=_raw_to_solution_board(current),
            )

        return value_prompt.format(
            input=raw_to_board(x),
            board=raw_to_board(current),
        )

    @staticmethod
    def value_outputs_unwrap(x: str, y: str, value_outputs: list) -> float:
        labels = [_last_value_label(output) for output in value_outputs]
        labels = [label for label in labels if label]
        value_map = {'impossible': 0.001, 'likely': 1, 'sure': 20}
        value = sum(value_map[label] for label in labels)

        current = get_current_board(x, y)
        info = check_board(x, current)
        if not info['valid_partial']:
            return 0.001
        if info['complete_valid']:
            return max(value, 20)
        if not labels:
            return 1
        if has_forced_move(current):
            return max(value, 1)
        return value


SudokuTask = Sudoku4x4Task
