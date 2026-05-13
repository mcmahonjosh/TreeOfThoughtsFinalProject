import os
import re
import openai
import backoff
from llama_cpp import Llama


# completion_tokens = prompt_tokens = 0


# api_key = os.getenv("OPENAI_API_KEY", "")
# if api_key != "":
#     openai.api_key = api_key
# else:
#     print("Warning: OPENAI_API_KEY is not set")


# api_base = os.getenv("OPENAI_API_BASE", "")
# if api_base != "":
#     print("Warning: OPENAI_API_BASE is set to {}".format(api_base))
#     openai.api_base = api_base


# @backoff.on_exception(backoff.expo, openai.error.OpenAIError)
# def completions_with_backoff(**kwargs):
#     return openai.ChatCompletion.create(**kwargs)


# def gpt(prompt, model="gpt-4", temperature=0.7, max_tokens=1000, n=1, stop=None) -> list:
#     messages = [{"role": "user", "content": prompt}]
#     return chatgpt(messages, model=model, temperature=temperature, max_tokens=max_tokens, n=n, stop=stop)


# def chatgpt(messages, model="gpt-4", temperature=0.7, max_tokens=1000, n=1, stop=None) -> list:
#     global completion_tokens, prompt_tokens
#     outputs = []
#     while n > 0:
#         cnt = min(n, 20)
#         n -= cnt
#         res = completions_with_backoff(model=model, messages=messages, temperature=temperature, max_tokens=max_tokens, n=cnt, stop=stop)
#         outputs.extend([choice.message.content for choice in res.choices])
#         completion_tokens += res.usage.completion_tokens
#         prompt_tokens += res.usage.prompt_tokens
#     return outputs


# def gpt_usage(backend="gpt-4"):
#     global completion_tokens, prompt_tokens
#     if backend == "gpt-4":
#         cost = completion_tokens / 1000 * 0.06 + prompt_tokens / 1000 * 0.03
#     elif backend == "gpt-3.5-turbo":
#         cost = completion_tokens / 1000 * 0.002 + prompt_tokens / 1000 * 0.0015
#     elif backend == "gpt-4o":
#         cost = completion_tokens / 1000 * 0.00250 + prompt_tokens / 1000 * 0.01
#     return {"completion_tokens": completion_tokens, "prompt_tokens": prompt_tokens, "cost": cost}


# Lazy-loaded Qwen model (loaded once on first call)
qwen_llm = None
qwen_repo_id = None
qwen_model = None


def get_qwen_llm(repo_id, model):
    """Load and cache the Qwen model (lazy initialization)."""
    global qwen_llm, qwen_repo_id, qwen_model

    if qwen_llm is None or qwen_repo_id != repo_id or qwen_model != model:
        qwen_repo_id = repo_id
        qwen_model = model

        qwen_llm = Llama.from_pretrained(
            repo_id=repo_id,
            filename=model,
            n_gpu_layers=-1,   # On A100, offload as much as possible to GPU
            n_ctx=16384,       # Context window
            chat_format="chatml",
            verbose=False      # Removes most CUDA spam
        )

    return qwen_llm


def choose_max_tokens(prompt):
    """Pick a smaller/larger output limit depending on what the prompt is doing."""

    # Text scoring: should return only one line, but Qwen may still start with <think>
    if (
        "Thus the coherency score is" in prompt
        or "Score the passage's coherency" in prompt
        or "score the passage" in prompt.lower()
    ):
        return 120

    # Text voting: needs a short comparison plus final choice
    if "The best choice is" in prompt:
        return 250

    # Text comparison: needs a short comparison plus final decision
    if "The more coherent passage is" in prompt:
        return 200

    # Text generation: needs room for plan + 4 short paragraphs
    if "Write a coherent passage" in prompt:
        return 1200

    # Game24/Sudoku value calls should be short
    if (
        "sure" in prompt.lower()
        and "likely" in prompt.lower()
        and "impossible" in prompt.lower()
    ):
        return 60

    # Game24/Sudoku proposal calls should be short but may need several lines
    if "Possible next steps" in prompt:
        return 200

    # Default fallback
    return 300


def clean_qwen_output(text):
    """Remove Qwen reasoning and keep the final answer when possible."""

    # Remove complete <think>...</think> blocks.
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)

    # Remove leftover unmatched think tags.
    text = text.replace("<think>", "").replace("</think>", "").strip()

    # If the model includes a final-answer marker, keep the content after the last one.
    markers = ["Passage:", "Final passage:", "Draft Passage:", "Final answer:"]

    best_idx = -1
    best_marker = None

    for marker in markers:
        idx = text.rfind(marker)
        if idx > best_idx:
            best_idx = idx
            best_marker = marker

    if best_marker is not None:
        text = text[best_idx + len(best_marker):].strip()

    # Cut off post-answer analysis/checking if present.
    stop_markers = [
        "\nCheck constraints:",
        "\nConstraint Check:",
        "\nReview:",
        "\nSelf-Correction",
        "\nVerification",
        "\n*Check:",
        "\nWait,",
        "\nLet's verify",
    ]

    for marker in stop_markers:
        if marker in text:
            text = text.split(marker)[0].strip()

    # Remove obvious leftover headings/placeholders.
    text = text.replace("[passage]", "").replace("[Passage]", "").replace("[final passage]", "").strip()

    return text.strip()


def qwen(
    prompt,
    repo_id="unsloth/Qwen3.6-27B-GGUF",
    model="*Qwen3.6-27B-Q4_K_M.gguf",
    temperature=0.7,
    max_tokens=None,
    n=1,
    stop=None
) -> list:
    llm = get_qwen_llm(repo_id, model)

    if max_tokens is None:
        max_tokens = choose_max_tokens(prompt)

    outputs = []
    for _ in range(n):
        res = llm.create_chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
            stop=stop
        )

        text = res["choices"][0]["message"]["content"]
        text = clean_qwen_output(text)
        outputs.append(text)

    return outputs