import argparse
import glob
import json
from pathlib import Path


def puzzle_is_solved(record):
    return any(info.get('r') == 1 for info in record.get('infos', []))


def count_solved(path):
    with open(path, 'r') as f:
        records = json.load(f)

    total = len(records)
    solved = sum(1 for record in records if puzzle_is_solved(record))
    return solved, total


def expand_paths(patterns):
    paths = []
    for pattern in patterns:
        matches = glob.glob(pattern, recursive=True)
        if matches:
            paths.extend(matches)
        else:
            paths.append(pattern)
    return sorted({Path(path) for path in paths if Path(path).is_file()})


def main():
    parser = argparse.ArgumentParser(
        description='Count solved puzzles in Tree-of-Thoughts JSON log files.'
    )
    parser.add_argument(
        'paths',
        nargs='*',
        default=['logs/**/*.json'],
        help='JSON log files or glob patterns. Defaults to logs/**/*.json.',
    )
    args = parser.parse_args()

    paths = expand_paths(args.paths)
    if not paths:
        raise SystemExit('No JSON log files found.')

    grand_solved = 0
    grand_total = 0
    for path in paths:
        solved, total = count_solved(path)
        grand_solved += solved
        grand_total += total
        accuracy = solved / total if total else 0
        print(f'{path}: {solved}/{total} solved ({accuracy:.2%})')

    if len(paths) > 1:
        accuracy = grand_solved / grand_total if grand_total else 0
        print(f'TOTAL: {grand_solved}/{grand_total} solved ({accuracy:.2%})')


if __name__ == '__main__':
    main()
