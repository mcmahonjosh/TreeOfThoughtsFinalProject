import numpy as np
from functools import partial

from tot.models import qwen


def get_value(task, x, y, n_evaluate_sample, cache_value=True):
    value_prompt = task.value_prompt_wrap(x, y)
    if cache_value and value_prompt in task.value_cache:
        return task.value_cache[value_prompt]
    value_outputs = qwen(value_prompt, n=n_evaluate_sample, stop=None)
    value = task.value_outputs_unwrap(x, y, value_outputs)
    if cache_value:
        task.value_cache[value_prompt] = value
    return value


def get_values(task, x, ys, n_evaluate_sample, cache_value=True):
    values = []
    local_value_cache = {}
    for y in ys:
        state_key = task.state_key(x, y) if hasattr(task, 'state_key') else y
        if state_key in local_value_cache:
            value = 0
        else:
            value = get_value(task, x, y, n_evaluate_sample, cache_value=cache_value)
            local_value_cache[state_key] = value
        values.append(value)
    return values


def get_votes(task, x, ys, n_evaluate_sample):
    vote_prompt = task.vote_prompt_wrap(x, ys)
    vote_outputs = qwen(vote_prompt, n=n_evaluate_sample, stop=None)
    return task.vote_outputs_unwrap(vote_outputs, len(ys))


def get_proposals(task, x, y):
    propose_prompt = task.propose_prompt_wrap(x, y)
    proposal_outputs = qwen(propose_prompt, n=1, stop=None)
    proposals = []
    for output in proposal_outputs:
        for line in output.split('\n'):
            line = line.strip()
            if line:
                proposals.append(y + line + '\n')
    return proposals


def get_samples(task, x, y, n_generate_sample, prompt_sample, stop):
    if prompt_sample == 'standard':
        prompt = task.standard_prompt_wrap(x, y)
    elif prompt_sample == 'cot':
        prompt = task.cot_prompt_wrap(x, y)
    else:
        raise ValueError(f'prompt_sample {prompt_sample} not recognized')
    samples = qwen(prompt, n=n_generate_sample, stop=stop)
    return [y + sample for sample in samples]


def _is_finished(task, x, y):
    return hasattr(task, 'is_finished') and task.is_finished(x, y)


def _state_key(task, x, y):
    return task.state_key(x, y) if hasattr(task, 'state_key') else y


def _select_candidate_ids(args, values):
    ids = list(range(len(values)))
    n_select = min(args.n_select_sample, len(ids))
    if n_select == 0:
        return []

    if args.method_select == 'sample':
        total = sum(values)
        if total <= 0:
            ps = np.ones(len(values)) / len(values)
        else:
            ps = np.array(values) / total
        return np.random.choice(ids, size=n_select, replace=False, p=ps).tolist()

    if args.method_select == 'greedy':
        return sorted(ids, key=lambda idx: values[idx], reverse=True)[:n_select]

    raise ValueError(f'method_select {args.method_select} not recognized')


def _generate_candidates(args, task, x, y, depth):
    if args.method_generate == 'sample':
        stop = task.stops[depth] if depth < len(task.stops) else None
        return get_samples(task, x, y, args.n_generate_sample, args.prompt_sample, stop)

    if args.method_generate == 'propose':
        return get_proposals(task, x, y)

    raise ValueError(f'method_generate {args.method_generate} not recognized')


def _filter_candidates(task, x, y, candidates, seen_states):
    filtered_candidates = []
    current_state_key = _state_key(task, x, y)
    for candidate in candidates:
        state_key = _state_key(task, x, candidate)
        if state_key == current_state_key:
            continue
        if hasattr(task, 'is_valid_state') and not task.is_valid_state(x, candidate):
            continue
        if state_key in seen_states:
            continue
        seen_states.add(state_key)
        filtered_candidates.append(candidate)
    return filtered_candidates


def _fallback_candidates(task, x, y, seen_states):
    if not hasattr(task, 'fallback_proposals'):
        return []
    return _filter_candidates(task, x, y, task.fallback_proposals(x, y), seen_states)


def _evaluate_candidates(args, task, x, candidates, used_fallback=False):
    if used_fallback and getattr(args, 'fallback_evaluate', 'model') == 'local':
        if hasattr(task, 'fallback_values'):
            return task.fallback_values(x, candidates), 'local'

    if args.method_evaluate == 'vote':
        return get_votes(task, x, candidates, args.n_evaluate_sample), 'model'

    if args.method_evaluate == 'value':
        return get_values(task, x, candidates, args.n_evaluate_sample), 'model'

    raise ValueError(f'method_evaluate {args.method_evaluate} not recognized')


def solve(args, task, idx, to_print=True):
    global qwen
    qwen = partial(qwen, temperature=args.temperature)
    if to_print:
        print(qwen)

    x = task.get_input(idx)
    stack = [('', 0)]
    seen_states = {_state_key(task, x, '')}
    infos = []
    solutions = []
    best_seen = []
    nodes = 0
    max_nodes = getattr(args, 'dfs_max_nodes', None)
    max_depth = getattr(args, 'dfs_max_depth', None) or task.steps

    while stack:
        if max_nodes is not None and nodes >= max_nodes:
            break

        y, depth = stack.pop()
        nodes += 1

        output_info = task.test_output(idx, y)
        if output_info.get('r', 0):
            solutions.append(y)
            break

        if depth >= max_depth or _is_finished(task, x, y):
            continue

        candidates = _generate_candidates(args, task, x, y, depth)

        filtered_candidates = _filter_candidates(task, x, y, candidates, seen_states)
        used_fallback = False

        if not filtered_candidates:
            filtered_candidates = _fallback_candidates(task, x, y, seen_states)
            used_fallback = bool(filtered_candidates)

        if not filtered_candidates:
            infos.append({
                'depth': depth,
                'x': x,
                'y': y,
                'new_ys': [],
                'values': [],
                'select_new_ys': [],
                'used_fallback': used_fallback,
                'evaluation_source': 'none',
            })
            continue

        values, evaluation_source = _evaluate_candidates(
            args,
            task,
            x,
            filtered_candidates,
            used_fallback=used_fallback,
        )
        select_ids = _select_candidate_ids(args, values)
        selected = [filtered_candidates[select_id] for select_id in select_ids]
        selected_values = [values[select_id] for select_id in select_ids]
        best_seen.extend(zip(selected, selected_values))

        if to_print:
            sorted_new_ys, sorted_values = zip(
                *sorted(zip(filtered_candidates, values), key=lambda item: item[1], reverse=True)
            )
            print(
                f'-- depth --: {depth}\n'
                f'-- new_ys --: {sorted_new_ys}\n'
                f'-- sol values --: {sorted_values}\n'
                f'-- choices --: {selected}\n'
            )

        infos.append({
            'depth': depth,
            'x': x,
            'y': y,
            'new_ys': filtered_candidates,
            'values': values,
            'select_new_ys': selected,
            'used_fallback': used_fallback,
            'evaluation_source': evaluation_source,
        })

        for candidate in reversed(selected):
            stack.append((candidate, depth + 1))

    if solutions:
        ys = solutions[:args.n_select_sample]
    else:
        ys = [
            candidate
            for candidate, _ in sorted(best_seen, key=lambda item: item[1], reverse=True)[:args.n_select_sample]
        ]

    if to_print:
        print(ys)
    return ys, {'steps': infos, 'nodes': nodes}


def naive_solve(args, task, idx, to_print=True):
    global qwen
    qwen = partial(qwen, temperature=args.temperature)
    if to_print:
        print(qwen)
    x = task.get_input(idx)
    ys = get_samples(task, x, '', args.n_generate_sample, args.prompt_sample, stop=None)
    return ys, {}
