"""成本计算（Decimal 高精度，区分 Codex/Claude 的 cache 语义）。

Codex/OpenAI 语义：input_tokens 含 cache_read 和 cache_creation，计费前扣除。
Claude/Anthropic 语义：input_tokens 已是 fresh input，不扣除。
"""
from decimal import Decimal

MILLION = Decimal(1_000_000)


def fresh_input_for(agent_type, input_tokens, cached, cache_w):
    # Codex 与 Zcode 的 input_tokens 都含 cache_read/cache_write（OpenAI 语义），
    # 计费前扣除；Claude/Anthropic 语义 input_tokens 已是 fresh input。
    if agent_type in ("codex", "zcode"):
        return max(input_tokens - cached - cache_w, 0)
    return input_tokens


def find_pricing(model, pricing_map):
    """支持模型名称大小写不敏感、中转站前缀剥离与模糊回退匹配。

    例如：
    - 'zai-org/GLM-5.3-Flash' -> 'glm-5.3-flash'
    - 'OpenAI/GPT-4o' -> 'gpt-4o'
    - 'gemini-3.8-flash-high' -> 'gemini-3.8-flash'
    - 'Claude-3-7-Sonnet-Thinking' -> 'claude-3-7-sonnet'
    """
    if not model or not pricing_map:
        return None

    # 1. 原样精确匹配
    if model in pricing_map:
        return pricing_map[model]

    raw = str(model).strip()
    if not raw:
        return None

    # 构建小写查找字典
    lower_map = {k.lower(): v for k, v in pricing_map.items()}

    # 候选模型名称列表：原名、剥离中转站前缀名
    candidates = [raw]
    if "/" in raw:
        core = raw.split("/")[-1].strip()
        if core:
            candidates.append(core)

    # 2. 对每个候选名称进行大小写无关的精确匹配
    for c in candidates:
        if c in pricing_map:
            return pricing_map[c]
        cl = c.lower()
        if cl in lower_map:
            return lower_map[cl]

    # 3. 后缀模糊回退（大小写无关）
    suffixes = ("-thinking", "-high", "-medium", "-low", "-preview", "-exp", "-latest")
    for c in candidates:
        cl = c.lower()
        for suffix in suffixes:
            if cl.endswith(suffix):
                base = cl[:-len(suffix)]
                if base in lower_map:
                    return lower_map[base]

    return None


def compute_costs(agent_type, model, inp, cached, cache_w, out, pricing_map,
                  reasoning=0):
    """按模型定价计算事件成本；无定价时成本归零，但仍计算 fresh input。

    reasoning 仅对 Codex 生效：其 output_tokens 不含 reasoning_output_tokens，
    需合并计费；Claude/Antigravity 的 thinking 已含在 output_tokens，不重复累加。"""
    pr = find_pricing(model, pricing_map)
    if pr:
        mult = pr.get("multiplier", 1.0) or 1.0
        costs = calc_cost(inp, cached, cache_w, out, pr, mult, agent_type, reasoning)
    else:
        costs = zero_cost()
        costs["fresh_input"] = fresh_input_for(agent_type, inp, cached, cache_w)
    return costs



def calc_cost(input_tokens, cached_input_tokens, cache_write_input_tokens,
              output_tokens, pricing, multiplier=1.0, agent_type="codex",
              reasoning=0):
    fresh = fresh_input_for(agent_type, input_tokens,
                            cached_input_tokens, cache_write_input_tokens)
    inp = Decimal(fresh)
    # Codex 的 output_tokens 不含 reasoning，有效输出 = output + reasoning（均按输出价计）；
    # Claude 的 thinking 已含在 output_tokens，reasoning 恒为 0。
    effective_out = output_tokens + (reasoning if agent_type == "codex" else 0)
    out = Decimal(effective_out)
    cr = Decimal(cached_input_tokens)
    cw = Decimal(cache_write_input_tokens)

    input_cost = inp * Decimal(str(pricing["input_per_million"])) / MILLION
    output_cost = out * Decimal(str(pricing["output_per_million"])) / MILLION
    cache_read_cost = cr * Decimal(str(pricing["cache_read_per_million"])) / MILLION
    cache_creation_cost = cw * Decimal(str(pricing["cache_creation_per_million"])) / MILLION

    base = input_cost + output_cost + cache_read_cost + cache_creation_cost
    total = base * Decimal(str(multiplier))
    return {
        "fresh_input": fresh,
        "input_cost": float(input_cost),
        "output_cost": float(output_cost),
        "cache_read_cost": float(cache_read_cost),
        "cache_creation_cost": float(cache_creation_cost),
        "total_cost": float(total),
    }


def zero_cost():
    return {"fresh_input": 0, "input_cost": 0.0, "output_cost": 0.0,
            "cache_read_cost": 0.0, "cache_creation_cost": 0.0, "total_cost": 0.0}
