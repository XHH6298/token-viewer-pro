"""Claude Code 适配器：~/.claude/projects/**/*.jsonl。

每行自带 sessionId/model，可从字节偏移增量续读。流式分片与重复收尾条
按 message.id 去重（见 make_event 的 dedup_key）。
"""
from pathlib import Path
from adapters.common import make_event

CLAUDE_PROJECTS_DIR = Path.home() / ".claude" / "projects"


def list_files():
    if not CLAUDE_PROJECTS_DIR or not CLAUDE_PROJECTS_DIR.exists():
        return []
    return [str(p) for p in CLAUDE_PROJECTS_DIR.rglob("*.jsonl")]


def parse_line(obj, pricing_map, compute_costs):
    if obj.get("type") != "assistant":
        return []
    msg = obj.get("message", {})
    usage = msg.get("usage")
    if not usage or not isinstance(usage, dict):
        return []
    # Claude Code 把一次 API 回复按流式分片落盘成多条 assistant 行：
    # 中间分片带大额 input_tokens 但没有 stop_reason 键，被中断的请求
    # 只有 stop_reason=None 的分片，两者都不是完整计费结果；收尾条
    # (stop_reason 非空) 才带最终 usage，且可能被原样重复落盘数份
    # （时间戳不同、usage 逐字节一致）。三种都只按 message.id 记一次。
    if msg.get("stop_reason") is None:
        return []
    inp = usage.get("input_tokens")
    if inp is None:
        return []
    inp = inp or 0
    cached = usage.get("cache_read_input_tokens", 0) or 0
    cache_w = usage.get("cache_creation_input_tokens", 0) or 0
    out = usage.get("output_tokens", 0) or 0
    reasoning = (usage.get("output_tokens_details") or {}).get("thinking_tokens", 0) or 0
    if inp == 0 and out == 0 and cached == 0 and cache_w == 0:
        return []
    model = msg.get("model")
    ts = obj.get("timestamp", "")
    session_id = obj.get("sessionId", "unknown") or "unknown"
    cwd = obj.get("cwd")
    return [make_event("claude", session_id, None, model, ts,
        inp, cached, cache_w, out, reasoning, cwd, pricing_map,
        compute_costs, dedup_key=msg.get("id"))]


def parse_file(path, pricing_map, compute_costs, start_offset=0):
    from adapters.common import parse_jsonl_events
    return parse_jsonl_events(
        path, pricing_map, start_offset,
        lambda obj, pm: parse_line(obj, pm, compute_costs))
