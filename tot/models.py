import os
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
#         # log completion tokens
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
            n_gpu_layers=-1,  # Use GPU acceleration
            chat_format="chatml"
        )
    return qwen_llm

def qwen(prompt, repo_id="unsloth/Qwen3.6-27B-GGUF", model="*Qwen3.6-27B-Q4_K_M.gguf", temperature=0.7, max_tokens=1000, n=1, stop=None) -> list:
    llm = get_qwen_llm(repo_id, model)

    outputs = []
    for _ in range(n):
        res = llm.create_chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
            stop=stop
        )
        # llama.cpp returns a dict, not an object
        outputs.append(res['choices'][0]['message']['content'])
    return outputs