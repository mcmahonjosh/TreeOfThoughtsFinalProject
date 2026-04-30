# 5-shot
standard_prompt = '''Solve the 4x4 Sudoku puzzle. The puzzle is a 16-character string representing the board row by row. A 0 means the cell is empty. Use digits 1, 2, 3, and 4. Each row, each column, and each 2x2 box must contain 1, 2, 3, and 4 exactly once. Return only the solved 16-character string.
Puzzle: 0321003004002100
Answer: 4321123434122143
Puzzle: 1400000032104020
Answer: 1432234132144123
Puzzle: 0010000402400421
Answer: 4312213412433421
Puzzle: 0300210000011043
Answer: 4312213434211243
Puzzle: 0102203040001020
Answer: 3142243142131324
Puzzle: {input}
'''


# 5-shot
cot_prompt = '''Solve the 4x4 Sudoku puzzle. The puzzle is a 16-character string representing the board row by row. A 0 means the cell is empty. Use digits 1, 2, 3, and 4. Each row, each column, and each 2x2 box must contain 1, 2, 3, and 4 exactly once.

Puzzle: 0321003004002100
Steps:
Board:
0 3 2 1
0 0 3 0
0 4 0 0
2 1 0 0
Fill the missing cells while keeping the given digits fixed.
Solved board:
4 3 2 1
1 2 3 4
3 4 1 2
2 1 4 3
Answer: 4321123434122143

Puzzle: 1400000032104020
Steps:
Board:
1 4 0 0
0 0 0 0
3 2 1 0
4 0 2 0
Fill the missing cells while keeping the given digits fixed.
Solved board:
1 4 3 2
2 3 4 1
3 2 1 4
4 1 2 3
Answer: 1432234132144123

Puzzle: 0010000402400421
Steps:
Board:
0 0 1 0
0 0 0 4
0 2 4 0
0 4 2 1
Fill the missing cells while keeping the given digits fixed.
Solved board:
4 3 1 2
2 1 3 4
1 2 4 3
3 4 2 1
Answer: 4312213412433421

Puzzle: 0300210000011043
Steps:
Board:
0 3 0 0
2 1 0 0
0 0 0 1
1 0 4 3
Fill the missing cells while keeping the given digits fixed.
Solved board:
4 3 1 2
2 1 3 4
3 4 2 1
1 2 4 3
Answer: 4312213434211243

Puzzle: 0102203040001020
Steps:
Board:
0 1 0 2
2 0 3 0
4 0 0 0
1 0 2 0
Fill the missing cells while keeping the given digits fixed.
Solved board:
3 1 4 2
2 4 3 1
4 2 1 3
1 3 2 4
Answer: 3142243142131324

Puzzle: {input}
'''


# 1-shot
propose_prompt = '''Puzzle: 0321003004002100
Current board:
0 3 2 1
0 0 3 0
0 4 0 0
2 1 0 0
Possible next moves:
r1c1 = 4
r2c1 = 1
r2c2 = 2
r2c4 = 4
r3c1 = 3
r3c3 = 1
r3c4 = 2
r4c3 = 4
r4c4 = 3
Puzzle: {input}
Current board:
{board}
Possible next moves:
'''


value_prompt = '''Evaluate if the current 4x4 Sudoku board is valid and can still lead to a solution (sure/likely/impossible).
Use digits 1, 2, 3, and 4. A 0 means empty.
Each row, column, and 2x2 box must not contain duplicate nonzero digits.
If the board is complete and valid, answer sure.
If the board is incomplete but valid, answer likely.
If the board has a contradiction, answer impossible.

Puzzle: 0321003004002100
Current board:
4 3 2 1
1 2 3 4
3 4 1 2
2 1 4 3
sure

Puzzle: 0321003004002100
Current board:
0 3 2 1
0 0 3 0
0 4 0 0
2 1 0 0
likely

Puzzle: 0321003004002100
Current board:
3 3 2 1
0 0 3 0
0 4 0 0
2 1 0 0
impossible

Puzzle: 1400000032104020
Current board:
1 4 3 2
2 3 4 1
3 2 1 4
4 1 2 3
sure

Puzzle: {input}
Current board:
{board}
'''


value_last_step_prompt = '''Use digits 1, 2, 3, and 4 to solve the 4x4 Sudoku puzzle. Given a puzzle and an answer, judge whether the answer is correct (sure/impossible). The answer must keep all nonzero puzzle digits fixed, and every row, column, and 2x2 box must contain 1, 2, 3, and 4 exactly once.

Puzzle: 0321003004002100
Answer: 4321123434122143
Judge:
sure

Puzzle: 0321003004002100
Answer: 3321123434122143
Judge:
impossible

Puzzle: 1400000032104020
Answer: 1432234132144123
Judge:
sure

Puzzle: 1400000032104020
Answer: 1432234132144124
Judge:
impossible

Puzzle: {input}
Answer: {answer}
Judge:'''