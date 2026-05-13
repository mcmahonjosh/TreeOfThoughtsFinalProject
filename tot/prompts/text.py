standard_prompt = '''/no_think
Write a coherent passage of exactly 4 short paragraphs.


Required ending:
{input}




Rules:
- Write only the final passage.
- The passage must contain exactly 4 paragraphs.
- Each paragraph must be short, about 2 to 4 sentences.
- The final sentence of each paragraph must be exactly the required ending.
- Use the required ending exactly as written.
- Do not change any words, punctuation, or capitalization in the required ending.
- Do not use placeholders like [Paragraph 1].
- Do not mention these rules.
- Do not write a plan.
- Do not explain.
- Do not include markdown.
- Do not write anything after the fourth paragraph.




Passage:
'''








cot_prompt = '''/no_think
Write a coherent passage of exactly 4 short paragraphs.


Required paragraph endings:
{input}


Interpretation:
- The required endings above contain 4 sentences.
- Paragraph 1 must end with the first required sentence.
- Paragraph 2 must end with the second required sentence.
- Paragraph 3 must end with the third required sentence.
- Paragraph 4 must end with the fourth required sentence.


Rules:
- First write a brief plan.
- Then write the final passage.
- Do not discuss the rules.
- Do not mention ambiguity.
- Do not include <think>.
- Do not include markdown.
- The passage should be coherent and unified.
- Each paragraph should naturally lead into its required ending sentence.


Output exactly:


Plan:
A brief plan.


Passage:
'''








vote_prompt = '''/no_think


Return exactly one line.


Choose the best candidate passage.


Your entire response must be exactly:
The best choice is {s}


where {s} is the integer id of the best choice.


Do not explain.
Do not analyze.
Do not include <think>.
Do not write anything before or after the required line.
'''






compare_prompt = '''/no_think


Briefly compare the coherency of the following two passages.


Rules:
- Prefer the passage that is more coherent, complete, and natural.
- Prefer the passage that better follows the required ending constraint.
- Penalize placeholders, notes, markdown, meta-analysis, or unfinished text.
- Penalize passages that explain the task instead of completing it.
- The final line must be exactly one of these three lines:
The more coherent passage is 1
The more coherent passage is 2
The two passages are similarly coherent
- Do not explain more than needed.
- Do not include <think>.
- Do not write anything after the final line.
'''



score_prompt = '''/no_think


Return exactly one line and nothing else.


Score the passage's coherency from 1 to 10.


Your entire response must match this exact format:
Thus the coherency score is {s}


where {s} is an integer from 1 to 10.


Do not explain.
Do not analyze.
Do not include <think>.
Do not write anything before or after the required line.


Passage:
'''



