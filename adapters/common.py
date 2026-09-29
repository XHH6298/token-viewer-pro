"""共享工具：turn_id 指纹、事件构造、JSONL 增量读取。"""
import datetime


def parse_iso(ts):
    try:
        return int(datetime.datetime.fromisoformat(
            ts.replace("Z", "+00:00")).timestamp())
    except Exception:
        return 0


def stable_turn_id(ts, model, inp, cached, cache_w, out, reasoning):
    """真实日志的 token_count 事件普遍没有 turn_id。

    SQLite 的 UNIQUE 索引对 NULL 视为互不相同，因此 turn_id 为 NULL 时
    UNIQUE(agent_type, session_id, turn_id) 完全失效，全量重扫会重复入库。
    这里用事件自身字段构造稳定指纹：同一条事件无论解析几次、来自哪个目录，
    都得到相同 turn_id，从而让 INSERT OR IGNORE 真正去重。"""
    return f"{ts}|{model or ''}|{inp}|{cached}|{cache_w}|{out}|{reasoning}"


def make_event(agent_type, session_id, turn_id, model, ts,
               inp, cached, cache_w, out, reasoning, cwd, pricing_map,
               compute_costs, dedup_key=None):
    if not turn_id:
        turn_id = stable_turn_id(ts, model, inp, cached, cache_w, out, reasoning)
        # Claude：以 message.id 为去重键。同一回复的流式落盘可能带不同时间戳
        # （分片/重复收尾条），指纹里含 ts 会让 INSERT OR IGNORE 失效，
        # 换成 message.id 后同一次请求无论落盘几份都只入一条。
        if dedup_key:
            turn_id = f"mid:{dedup_key}"
    costs = compute_costs(agent_type, model, inp, cached, cache_w, out, pricing_map,
                          reasoning=reasoning)
    return (agent_type, session_id, turn_id, model, ts, parse_iso(ts),
            inp, costs["fresh_input"], cached, cache_w, out, reasoning,
            costs["input_cost"], costs["output_cost"],
            costs["cache_read_cost"], costs["cache_creation_cost"],
            costs["total_cost"], cwd)


def iter_jsonl_lines(path, start_offset):
    """逐行读取 jsonl，返回 (文本, 行起始字节, 行结束字节)。

    末行若没有换行符（写入中）仍会返回，下次从行起始处续读，
    避免遗漏补齐后的记录。
    """
    with open(path, "rb") as f:
        if start_offset > 0:
            f.seek(start_offset)
        line_start = f.tell()
        while True:
            raw = f.readline()
            if not raw:
                break
            line_end = f.tell()
            end = line_start if not raw.endswith(b"\n") else line_end
            yield raw.decode("utf-8", errors="replace"), line_start, end
            line_start = line_end


def parse_jsonl_events(path, pricing_map, start_offset, line_parser):
    """按行解析 jsonl，行解析器返回事件列表。返回 (events, end_offset)。"""
    import json
    events = []
    end_offset = start_offset
    for text, _start, end in iter_jsonl_lines(path, start_offset):
        end_offset = end
        line = text.strip()
        if not line or not line.startswith("{"):
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        events.extend(line_parser(obj, pricing_map))
    return events, end_offset
