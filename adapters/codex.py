"""Codex CLI 适配器：~/.codex/sessions 与 archived_sessions 的 rollout JSONL。

Codex 文件依赖头部 session_meta/turn_context 的会话与模型状态，
只能从文件头全量解析，靠 turn_id 指纹 + INSERT OR IGNORE 去重。
last_token_usage 优先（单次请求精确值），缺失时回退 total_token_usage。
"""
from pathlib import Path
from config import SESSIONS_DIR, ARCHIVED_DIR
from adapters.common import make_event, iter_jsonl_lines


def list_files():
    files = []
    for root in (SESSIONS_DIR, ARCHIVED_DIR):
        if root and Path(root).exists():
            files.extend(str(p) for p in Path(root).rglob("*.jsonl"))
    return files


def parse_file(path, pricing_map, compute_costs, start_offset=0):
    session_id = "unknown"
    current_model = None
    cwd = None
    events = []
    end_offset = 0
    for text, _start, end in iter_jsonl_lines(path, 0):
        end_offset = end
        line = text.strip()
        if not line or not line.startswith("{"):
            continue
        import json
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        ptype = obj.get("type")
        payload = obj.get("payload", {})
        ts = obj.get("timestamp", "")
        if ptype == "session_meta":
            session_id = payload.get("session_id") or payload.get("id") or "unknown"
            cwd = payload.get("cwd")
            continue
        if ptype == "turn_context":
            _m = payload.get("model")
            if _m:
                current_model = _m
            continue
        if ptype != "event_msg":
            continue
        subtype = payload.get("type")
        if subtype == "thread_settings_applied":
            current_model = payload.get("thread_settings", {}).get("model")
        elif subtype == "token_count":
            info = payload.get("info", {})
            last = info.get("last_token_usage") or info.get("total_token_usage") or {}
            inp = last.get("input_tokens", 0) or 0
            cached = last.get("cached_input_tokens", 0) or 0
            cache_w = last.get("cache_write_input_tokens", 0) or 0
            out = last.get("output_tokens", 0) or 0
            reasoning = last.get("reasoning_output_tokens", 0) or 0
            if inp == 0 and out == 0 and cached == 0 and cache_w == 0:
                continue
            events.append(make_event("codex", session_id,
                payload.get("turn_id"), current_model, ts,
                inp, cached, cache_w, out, reasoning, cwd, pricing_map,
                compute_costs))
    return events, end_offset
