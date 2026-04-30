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
Each row, column, and 2x2 box (4 total: top-left, top-right, bottom-left, bottom-right) must contain each digit exactly once.
Dots "." are empty cells.

Think step by step. Each thought should fill exactly one empty cell using the format:
r{row}c{col} = {digit}
Briefly explain why the placement is legal or forced.
After all thoughts, output the completed grid as 4 rows, with digits separated by spaces.

Input:
1 4 . .
. . . 1
3 . 1 .
4 . 2 .

Thoughts:
r2c1 = 2
Column 1 is missing only 2; row 2 and the top-left box allow 2 at r2c1.
r2c2 = 3
Top-left box is missing only 3; row 2 and column 2 allow 3 at r2c2.
r2c3 = 4
Row 2 is missing only 4; column 3 and the top-right box allow 4 at r2c3.
r1c3 = 3
Column 3 is missing only 3; row 1 and the top-right box allow 3 at r1c3.
r1c4 = 2
Row 1 is missing only 2; column 4 and the top-right box allow 2 at r1c4.
r3c2 = 2
Rows 1,2,4 already have 2; columns 1,3,4 already have 2; therefore row 3 must have 2 at r3c2; bottom-left box allows 2 at r3c2.
r3c4 = 4
Row 3 is missing only 4; column 4 and the bottom-right box allow 4 at r3c4.
r4c2 = 1
Column 2 is missing only 1; row 4 and the bottom-left box allow 1 at r4c2.
r4c4 = 3
Row 4 is missing only 3; column 4 and the bottom-right box allow 3 at r4c4.

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
r3c2 = 2
Column 2 is missing only 2; row 3 and the bottom-left box allow 2 at r3c2.
r4c3 = 1
Row 4 is missing only 1; column 3 and the bottom-right box allow 1 at r4c3.
r3c3 = 3
Column 3 is missing only 3; row 3 and the bottom-right box allow 3 at r3c3.
r3c1 = 1
Row 3 is missing only 1; column 1 and the bottom-left box allow 1 at r3c1.
r2c4 = 1
Rows 1,3,4 already have 1; columns 1,2,3 already have 1; therefore row 2 must have 1 at r2c4; top-right box allows 1 at r2c4.
r1c4 = 3
Column 4 is missing only 3; row 1 and the top-right box allow 3 at r1c4.
r1c1 = 2
Row 1 is missing only 2; column 1 and the top-left box allow 2 at r1c1.
r2c1 = 4
Row 2 is missing only 4; column 1 and the top-left box allow 4 at r2c1.

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
r1c3 = 2
Top-right box is missing only 2; row 1 and column 3 allow 2 at r1c3.
r1c2 = 1
Row 1 is missing only 1; column 2 and the top-left box allow 1 at r1c2.
r4c3 = 4
Column 3 is missing only 4; row 4 and the bottom-right box allow 4 at r4c3.
r2c1 = 2
Row 2 is missing {2,4} at {r2c1,r2c2}; column 1 already has 4 at r3c1, so row 2 must have 2 at r2c1; top-left box allows 2 at r2c1.
r2c2 = 4
Row 2 is missing only 4; column 2 and the top-left box allow 4 at r2c2.
r4c1 = 1
Row 4 is missing only 1; column 1 and the bottom-left box allow 1 at r4c1.
r4c4 = 3
Row 4 is missing only 3; column 4 and the bottom-right box allow 3 at r4c4.
r3c2 = 3
Column 2 is missing only 3; row 3 and the bottom-left box allow 3 at r3c2.
r3c4 = 2
Row 3 is missing only 2; column 4 and the bottom-right box allow 2 at r3c4.

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
r3c4 = 4
Column 4 is missing only 4; row 3 and the bottom-right box allow 4 at r3c4.
r1c2 = 2
Top-left box is missing {2,3} at {r1c2,r2c1}; row 2 already has 2 at r2c4, so row 1 must have 2 at r1c2; column 2 allows 2 at r1c2.
r2c1 = 3
Top-left box is missing only 3; row 2 and column 1 allow 3 at r2c1.
r1c3 = 1
Row 1 is missing only 1; column 3 and the top-right box allow 1 at r1c3.
r2c3 = 4
Row 2 is missing only 4; column 3 and the top-right box allow 4 at r2c3.
r4c2 = 4
Column 2 is missing only 4; row 4 and the bottom-left box allow 4 at r4c2.
r3c1 = 1
Bottom-left box is missing {1,2} at {r3c1,r4c1}; row 4 already has 1 at r4c4, so row 3 must have 1 at r3c1; column 1 allows 1 at r3c1.
r4c1 = 2
Column 1 is missing only 2; row 4 and the bottom-left box allow 2 at r4c1.
r4c3 = 3
Row 4 is missing only 3; column 3 and the bottom-right box allow 3 at r4c3.
r3c3 = 2
Row 3 is missing only 2; column 3 and the bottom-right box allow 2 at r3c3.

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
r3c2 = 2
Bottom-left box is missing {1,2} at {r3c2,r4c1}; row 4 already has 2 at r4c4, so row 3 must have 2 at r3c2; column 2 allows 2 at r3c2.
r4c1 = 1
Bottom-left box is missing only 1; row 4 and column 1 allow 1 at r4c1.
r1c1 = 3
Column 1 is missing only 3; row 1 and the top-left box allow 3 at r1c1.
r3c4 = 3
Row 3 is missing only 3; column 4 and the bottom-right box allow 3 at r3c4.
r4c3 = 4
Row 4 is missing only 4; column 3 and the bottom-right box allow 4 at r4c3.
r1c3 = 2
Rows 2,3,4 already have 2; columns 1,2,4 already have 2; therefore row 1 must have 2 at r1c3; top-right box allows 2 at r1c3.
r2c3 = 3
Rows 1,3,4 already have 3; columns 1,2,4 already have 3; therefore row 2 must have 3 at r2c3; top-right box allows 3 at r2c3.
r1c2 = 4
Row 1 is missing {1,4} at {r1c2,r1c4}; any of {1,4} would be legal at r1c2; pick 4 with no strong reason; column 2 at top-left box allows 4 at r1c2.
r1c4 = 1
Row 1 is missing only 1; column 4 and the top-right box allow 1 at r1c4.
r2c2 = 1
Column 2 is missing only 1; row 2 and the top-left box allow 1 at r2c2.
r2c4 = 4
Row 2 is missing only 4; column 4 and the top-right box allow 4 at r2c4.

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
Dots "." are empty cells.

A possible next thought is exactly one legal placement:
r{row}c{col} = {digit}
Reason: brief explanation.
Confidence: certain/high/medium/low

Do not solve the whole puzzle.
List several possible next placements for the current board.
Prefer forced moves when they exist.
If a move is legal but not forced, you may still list it with lower confidence.

Example:

Current board:
. 2 3 4
3 4 . 2
2 . 4 3
4 3 2 .

Possible next moves:
r1c1 = 1
Reason: row 1 is missing only 1.
Confidence: certain

r2c3 = 1
Reason: row 2 is missing only 1.
Confidence: certain

r3c2 = 1
Reason: row 3 is missing only 1.
Confidence: certain

r4c4 = 1
Reason: row 4 is missing only 1.
Confidence: certain

Example:

Current board:
. 2 . 4
3 . . 2
. 1 4 .
4 . 2 .

Possible next moves:
r1c1 = 1
Reason: row 1 is missing {1, 3}; column 1 already has 3 and 4; the top-left box allows 1 at r1c1.
Confidence: high

r1c3 = 3
Reason: row 1 would then contain 1, 2, 3, 4; column 3 and the top-right box allow 3.
Confidence: high

r2c2 = 4
Reason: row 2 is missing {1, 4}; the top-left box is missing {1, 4}, and column 2 allows 4.
Confidence: medium

Current board:
{input}

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
Dots "." are empty cells.

Use one of three labels:
sure: the board is solved correctly, or the state is legal and has clear forced moves.
likely: the state is legal and every empty cell has at least one possible digit, but the continuation is not obvious.
impossible: the state violates Sudoku rules, or at least one empty cell has no legal digit.

Current board:
1 2 3 4
3 4 1 2
2 1 4 3
4 3 2 1

Evaluation:
All rows, columns, and 2x2 boxes contain 1, 2, 3, 4 exactly once.
sure

Current board:
. 2 3 4
3 4 . 2
2 . 4 3
4 3 2 .

Evaluation:
There are no duplicate digits in any row, column, or 2x2 box. Each empty cell has a legal value, and several rows have only one missing digit.
sure

Current board:
. 2 . 4
3 . . 2
. 1 4 .
4 . 2 .

Evaluation:
There are no duplicate digits in any row, column, or 2x2 box. The board is still consistent, but multiple cells remain open and some choices may require search.
likely

Current board:
1 2 1 4
3 4 . 2
2 . 4 3
4 3 2 .

Evaluation:
Row 1 contains two 1s, so this violates Sudoku rules.
impossible

Current board:
. 1 2 3
4 . . .
2 . . .
3 . . .

Evaluation:
Cell r1c1 has no legal digit. Row 1 is missing only 4, but column 1 already contains 4. Therefore this state cannot lead to a valid solution.
impossible

Current board:
{input}

Evaluation:
'''


# Optional but useful final-answer judge, mirroring game24.py's value_last_step_prompt.
# This is helpful for IO / CoT / ToT output validation.
value_last_step_prompt = '''Judge whether the proposed answer correctly solves the 4x4 Sudoku.
The digits are 1, 2, 3, 4.
Each row, column, and 2x2 box (4 total: top-left, top-right, bottom-left, bottom-right) must contain each digit exactly once.
The answer must preserve all given digits from the input puzzle.

Give exactly one judgement: sure or impossible.

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
sure

Input:
{input}

Answer:
{answer}

Judge:
'''