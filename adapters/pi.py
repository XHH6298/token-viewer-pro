"""Pi 适配器：~/.pi/agent/sessions/**/*.jsonl。

会话首行是 {"type":"session",...} 元数据（cwd 等），其余为事件流。
assistant 的 message 行自带 usage：
  {input, output, cacheRead, cacheWrite, reasoning, totalTokens, cost}
- totalTokens = input + output + cacheRead + cacheWrite（OpenAI 语义，
  input 是不含缓存的 fresh input）；
- stopReason ∈ toolUse/stop/error/...：error 行 usage 全 0，跳过；
- message.id 可为 None，make_event 指纹兜底去重。
"""
import json
from pathlib import Path
from adapters.common import make_event

PI_SESSIONS_DIR = Path.home() / ".pi" / "agent" / "sessions"

AGENT_TYPE = "pi"


def list_files():
    if not PI_SESSIONS_DIR or not PI_SESSIONS_DIR.exists():
        return []
    return [str(p) for p in PI_SESSIONS_DIR.rglob("*.jsonl")]


def parse_line(obj, pricing_map, compute_costs, session_id="unknown"):
    if obj.get("type") != "message":
        return []
    msg = obj.get("message")
    if not isinstance(msg, dict) or msg.get("role") != "assistant":
        return []
    usage = msg.get("usage")
    if not isinstance(usage, dict):
        return []
    inp = usage.get("input") or 0
    out = usage.get("output") or 0
    cached = usage.get("cacheRead") or 0
    cache_w = usage.get("cacheWrite") or 0
    reasoning = usage.get("reasoning") or 0
    if inp == 0 and out == 0 and cached == 0 and cache_w == 0:
        return []
    model = msg.get("model")
    if not model:
        return []
    ts = obj.get("timestamp", "")
    cwd = obj.get("cwd")
    return [make_event(AGENT_TYPE, session_id, msg.get("id"), model, ts,
        inp, cached, cache_w, out, reasoning, cwd, pricing_map,
        compute_costs)]


def parse_file(path, pricing_map, compute_costs, start_offset=0):
    """消息行不带 sessionId，从文件名取（<时间戳>_<session-uuid>.jsonl）。"""
    from adapters.common import parse_jsonl_events
    session_id = Path(path).stem.split("_", 1)[-1]
    return parse_jsonl_events(
        path, pricing_map, start_offset,
        lambda obj, pm: parse_line(obj, pm, compute_costs, session_id))
