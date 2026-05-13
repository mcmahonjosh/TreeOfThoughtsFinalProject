# 5-shot
standard_prompt = '''Solve 4x4 Sudoku. The digits are 1, 2, 3, 4.
Each row, column, and 2x2 box (4 total 2x2 boxes: top-left, top-right, bottom-left, bottom-right) must contain each digit exactly once.
Dots "." are empty cells.
Return only the completed grid as 4 rows, with digits separated by spaces.

Input:
1 4 . .
. . . 1
3 . 1 .
4 . 2 .

Output:
1 4 3 2
2 3 4 1
3 2 1 4
4 1 2 3

Input:
. 1 4 .
. 3 2 .
. . . 4
3 4 . 2

Output:
2 1 4 3
4 3 2 1
1 2 3 4
3 4 1 2

Input:
3 . . 4
. . 3 1
4 . 1 .
. 2 . .

Output:
3 1 2 4
2 4 3 1
4 3 1 2
1 2 4 3

Input:
4 . . 3
. 1 . 2
. 3 . .
. . . 1

Output:
4 2 1 3
3 1 4 2
1 3 2 4
2 4 3 1

Input:
. . . .
2 . . .
4 . 1 .
. 3 . 2

Output:
3 4 2 1
2 1 3 4
4 2 1 3
1 3 4 2

Input:
{input}

Output:
'''


# 5-shot
cot_prompt = '''Solve 4x4 Sudoku. The digits are 1, 2, 3, 4.
Each row, column, and 2x2 box must contain each digit exactly once.
Dots "." are empty cells.

Use concise chain-of-thought moves.
Each move must fill exactly one empty cell on one line:
r{{row}}c{{col}} = {{digit}} - short reason.
Do not add extra analysis, restatements, markdown, or planning text.
After the moves, always write Output: followed by exactly 4 completed grid rows.

Input:
1 4 . .
. . . 1
3 . 1 .
4 . 2 .

Thoughts:
r2c1 = 2 - Column 1 missing only 2.
r2c2 = 3 - Top-left box missing only 3.
r2c3 = 4 - Row 2 missing only 4.
r1c3 = 3 - Column 3 missing only 3.
r1c4 = 2 - Row 1 missing only 2.
r3c2 = 2 - Row 3 needs 2; column and box allow it.
r3c4 = 4 - Row 3 missing only 4.
r4c2 = 1 - Column 2 missing only 1.
r4c4 = 3 - Row 4 missing only 3.

Output:
1 4 3 2
2 3 4 1
3 2 1 4
4 1 2 3

Input:
. 1 4 .
. 3 2 .
. . . 4
3 4 . 2

Thoughts:
r3c2 = 2 - Column 2 missing only 2.
r4c3 = 1 - Row 4 missing only 1.
r3c3 = 3 - Column 3 missing only 3.
r3c1 = 1 - Row 3 missing only 1.
r2c4 = 1 - Row 2 must place 1 at r2c4.
r1c4 = 3 - Column 4 missing only 3.
r1c1 = 2 - Row 1 missing only 2.
r2c1 = 4 - Row 2 missing only 4.

Output:
2 1 4 3
4 3 2 1
1 2 3 4
3 4 1 2

Input:
3 . . 4
. . 3 1
4 . 1 .
. 2 . .

Thoughts:
r1c3 = 2 - Top-right box missing only 2.
r1c2 = 1 - Row 1 missing only 1.
r4c3 = 4 - Column 3 missing only 4.
r2c1 = 2 - Column 1 eliminates 4 from row 2 pair.
r2c2 = 4 - Row 2 missing only 4.
r4c1 = 1 - Row 4 missing only 1.
r4c4 = 3 - Row 4 missing only 3.
r3c2 = 3 - Column 2 missing only 3.
r3c4 = 2 - Row 3 missing only 2.

Output:
3 1 2 4
2 4 3 1
4 3 1 2
1 2 4 3

Input:
4 . . 3
. 1 . 2
. 3 . .
. . . 1

Thoughts:
r3c4 = 4 - Column 4 missing only 4.
r1c2 = 2 - Row 2 eliminates 2 from top-left pair.
r2c1 = 3 - Top-left box missing only 3.
r1c3 = 1 - Row 1 missing only 1.
r2c3 = 4 - Row 2 missing only 4.
r4c2 = 4 - Column 2 missing only 4.
r3c1 = 1 - Row 4 eliminates 1 from bottom-left pair.
r4c1 = 2 - Column 1 missing only 2.
r4c3 = 3 - Row 4 missing only 3.
r3c3 = 2 - Row 3 missing only 2.

Output:
4 2 1 3
3 1 4 2
1 3 2 4
2 4 3 1

Input:
. . . .
2 . . .
4 . 1 .
. 3 . 2

Thoughts:
r3c2 = 2 - Row 4 eliminates 2 from bottom-left pair.
r4c1 = 1 - Bottom-left box missing only 1.
r1c1 = 3 - Column 1 missing only 3.
r3c4 = 3 - Row 3 missing only 3.
r4c3 = 4 - Row 4 missing only 4.
r1c3 = 2 - Row 1 must place 2 at r1c3.
r2c3 = 3 - Row 2 must place 3 at r2c3.
r1c2 = 4 - Choose legal 4 for row 1 pair.
r1c4 = 1 - Row 1 missing only 1.
r2c2 = 1 - Column 2 missing only 1.
r2c4 = 4 - Row 2 missing only 4.

Output:
3 4 2 1
2 1 3 4
4 2 1 3
1 3 4 2

Input:
{input}

Thoughts:
'''


# Proposal prompt for ToT.
# This should be called on a partial board/state.
# The intended thought unit is one placement, not a whole solution.
propose_prompt = '''You are solving a 4x4 Sudoku. The digits are 1, 2, 3, 4.
Each row, column, and 2x2 box (4 total: top-left, top-right, bottom-left, bottom-right) must contain each digit exactly once.
Dots "." or zeros "0" are empty cells.

List possible next thoughts for the current board.
Each thought must be exactly one legal placement on one line, using this parseable format:
r2c3 = 4 - Brief reason.

Prefer forced moves:
- a row, column, or 2x2 box has only one missing digit
- candidate elimination leaves only one legal cell or digit
- a placement is legal in its row, column, and box

Do not solve the whole puzzle. Do not output confidence labels. If no forced move is available, list only a few legal candidates and say they are not forced.

Original puzzle:
. 2 3 4
3 4 . 2
2 . 4 3
4 3 2 .
Current board:
. 2 3 4
3 4 . 2
2 . 4 3
4 3 2 .

Possible next moves:
r1c1 = 1 - Row 1 is missing only 1; column 1 and the top-left box allow it.
r2c3 = 1 - Row 2 is missing only 1; column 3 and the top-right box allow it.
r3c2 = 1 - Row 3 is missing only 1; column 2 and the bottom-left box allow it.
r4c4 = 1 - Row 4 is missing only 1; column 4 and the bottom-right box allow it.

Example:

Original puzzle:
. 2 . 4
3 . . 2
. 1 4 .
4 . 2 .
Current board:
. 2 . 4
3 . . 2
. 1 4 .
4 . 2 .

Possible next moves:
r1c1 = 1 - Row 1 is missing 1 and 3; column 1 already has 3 and 4, so only 1 fits.
r2c2 = 4 - Row 2 is missing 1 and 4; column 2 already has 1 and 2, so only 4 fits.
r2c3 = 1 - Row 2 is missing 1 and 4; column 3 and the top-right box allow only 1.
r3c1 = 2 - Row 3 is missing 2 and 3; column 1 and the bottom-left box allow only 2.

Example:

Original puzzle:
. . . .
2 . . .
4 . 1 .
. 3 . 2
Current board:
3 . 2 1
2 . 3 .
4 2 1 3
1 3 4 2

Possible next moves:
r1c2 = 4 - Row 1 is missing only 4; column 2 and the top-left box allow it.
r2c4 = 4 - Column 4 is missing only 4; row 2 and the top-right box allow it.

Original puzzle:
{input}
Current board:
{board}

Possible next moves:
'''


# Value prompt for ToT state evaluation.
# Intended labels:
# sure       -> solved, or very promising because there are clear forced moves.
# likely     -> legal and still viable, but may require branching.
# impossible -> violates Sudoku constraints, or some empty cell has no possible digit.
value_prompt = '''Evaluate whether a 4x4 Sudoku state is solvable/promising.
The digits are 1, 2, 3, 4.
Each row, column, and 2x2 box (4 total: top-left, top-right, bottom-left, bottom-right) must contain each digit exactly once.
Dots "." or zeros "0" are empty cells.

Check the state in this order:
1. All given digits from the original puzzle are unchanged.
2. No row, column, or 2x2 box contains duplicate non-empty digits.
3. Every empty cell has at least one legal candidate.
4. Forced moves or near-complete units make the state more promising.

Use one of three labels:
sure: the board is solved correctly, or the state is legal and has clear forced moves.
likely: the state is legal and every empty cell has at least one possible digit, but the continuation is not obvious.
impossible: the state violates Sudoku rules, or at least one empty cell has no legal digit.

End with exactly one label on its own final line: sure, likely, or impossible.

Original puzzle:
1 4 . .
. . . 1
3 . 1 .
4 . 2 .
Current board:
1 2 3 4
3 4 1 2
2 1 4 3
4 3 2 1

Evaluation:
The answer changed given r1c2 from 4 to 2, so it cannot be a valid continuation.
impossible

Original puzzle:
. 2 3 4
3 4 . 2
2 . 4 3
4 3 2 .
Current board:
. 2 3 4
3 4 . 2
2 . 4 3
4 3 2 .

Evaluation:
All givens are unchanged. There are no duplicate non-empty digits. Each empty cell has a legal candidate, and every row has one missing digit: r1c1, r2c3, r3c2, and r4c4 must all be 1.
sure

Original puzzle:
. 2 . 4
3 . . 2
. 1 4 .
4 . 2 .
Current board:
. 2 . 4
3 . . 2
. 1 4 .
4 . 2 .

Evaluation:
All givens are unchanged. There are no duplicate non-empty digits, and every empty cell has at least one legal candidate. The state is consistent, but several cells still require branching.
likely

Original puzzle:
. 2 3 4
3 4 . 2
2 . 4 3
4 3 2 .
Current board:
1 2 1 4
3 4 . 2
2 . 4 3
4 3 2 .

Evaluation:
Row 1 contains two 1s, so the state violates Sudoku rules.
impossible

Original puzzle:
. 1 2 3
4 . . .
2 . . .
3 . . .
Current board:
. 1 2 3
4 . . .
2 . . .
3 . . .

Evaluation:
Cell r1c1 has no legal digit. Row 1 is missing only 4, but column 1 already contains 4. Therefore this state cannot lead to a valid solution.
impossible

Original puzzle:
{input}
Current board:
{board}

Evaluation:
'''


# Optional but useful final-answer judge, mirroring game24.py's value_last_step_prompt.
# This is helpful for IO / CoT / ToT output validation.
value_last_step_prompt = '''Judge whether the proposed answer correctly solves the 4x4 Sudoku.
The digits are 1, 2, 3, 4.
Each row, column, and 2x2 box (4 total: top-left, top-right, bottom-left, bottom-right) must contain each digit exactly once.
Dots "." or zeros "0" are empty cells in the input puzzle.

Check the answer in this order:
1. It preserves all given digits from the input puzzle.
2. It has no empty cells.
3. Every row contains 1, 2, 3, 4 exactly once.
4. Every column contains 1, 2, 3, 4 exactly once.
5. Every 2x2 box contains 1, 2, 3, 4 exactly once.

End with exactly one judgement on its own final line: sure or impossible.

Input:
. 2 3 4
3 4 . 2
2 . 4 3
4 3 2 .

Answer:
1 2 3 4
3 4 1 2
2 1 4 3
4 3 2 1

Judge:
All givens are preserved. Each row, column, and 2x2 box contains 1, 2, 3, 4 exactly once.
sure

Input:
. 2 3 4
3 4 . 2
2 . 4 3
4 3 2 .

Answer:
1 2 3 4
3 4 1 2
2 1 4 3
4 3 1 2

Judge:
Rows 3 and 4 contain duplicate digits, and the bottom-right box is missing 4. This is not a valid solution.
impossible

Input:
2 . 4 3
4 3 2 .
1 2 . 4
. 4 1 2

Answer:
2 1 4 3
4 3 2 1
1 2 3 4
3 4 1 2

Judge:
All givens are preserved. Each row, column, and 2x2 box contains 1, 2, 3, 4 exactly once.
sure

Input:
4 . . 3
. 1 . 2
. 3 . .
. . . 1

Answer:
4 2 1 3
3 1 4 2
1 3 2 4
2 4 3 1

Judge:
All givens are preserved. Each row, column, and 2x2 box contains 1, 2, 3, 4 exactly once.
sure

Input:
4 . . 3
. 1 . 2
. 3 . .
. . . 1

Answer:
4 2 1 3
3 1 4 2
1 3 2 4
2 4 3 .

Judge:
The answer still has an empty cell at r4c4, so it is not a completed Sudoku solution.
impossible

Input:
{input}

Answer:
{answer}

Judge:
'''
