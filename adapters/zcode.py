"""Zcode 适配器：直接读 ~/.zcode/cli/db/db.sqlite 的 model_usage 表。

Zcode 自带完整的模型请求账本（input/output/reasoning/cache_read/时长/状态），
无需解析日志。表语义：
- input_tokens 不含 cache_read（Anthropic 语义，fresh input），缓存成本同 Claude；
- logical_request_id 全局唯一且无重复，天然去重键（turn_id = logical_request_id）；
- error/cancelled 行 usage 全 0，跳过；
- started_at 为毫秒 epoch；
- 只读 URI 打开，WAL 模式下安全，不干扰 Zcode 自身写入。

增量：file_index.offset 存 (max_started_at_ms, max_id)，只取新增行。
"""
import datetime
import sqlite3
from pathlib import Path
from adapters.common import make_event

ZCODE_DB = Path.home() / ".zcode" / "cli" / "db" / "db.sqlite"

AGENT_TYPE = "zcode"
_DISPLAY_NAME = {"zcode-agent": "主 Agent", "zcode-Explore": "Explore",
                 "zcode-general-purpose": "通用子代理", "zcode-judge": "评审代理"}


def available():
    # 测试会把 ZCODE_DB 置 None 来隔离真实 Zcode 库
    return bool(ZCODE_DB) and ZCODE_DB.exists()


def list_files():
    """游标键固定为 Zcode 库路径本身，offset 语义由 parse_file 自定义。"""
    return [str(ZCODE_DB)] if available() else []


def _ts_iso(ms):
    return datetime.datetime.fromtimestamp(
        ms / 1000, tz=datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def _cursor_id(s):
    """游标 id 兼容两代格式：旧版整数、新版字符串（usage_model_main_turn_msg_*）。
    比较时统一转 str：同代内字典序与写入顺序一致；跨代时新旧 id 必然不同毫秒，
    started_at 主门兜底，tie-break 仅防同毫秒重扫。"""
    try:
        return int(s)
    except (TypeError, ValueError):
        return s


def parse_file(path, pricing_map, compute_costs, cursor=0):
    """cursor = (max_started_at_ms, max_id)，返回 (events, new_cursor)。

    以 started_at 为主增量门、id 为同毫秒兜底：只导入
    (started_at > max_started_at) OR (started_at = max AND id > max_id) 的行。
    """
    if not available():
        return [], (0, 0)
    # 游标可能是 tuple、file_index 回读的 "ts:id" 字符串，或 None
    if isinstance(cursor, tuple):
        max_ts, max_id = cursor
    elif isinstance(cursor, str) and ":" in cursor:
        ts_s, _, id_s = cursor.partition(":")
        max_ts, max_id = int(ts_s), _cursor_id(id_s)
    else:
        max_ts, max_id = (cursor or 0), 0
    uri = f"file:{ZCODE_DB.as_posix()}?mode=ro"
    try:
        con = sqlite3.connect(uri, uri=True, timeout=3)
    except sqlite3.Error:
        return [], (max_ts, max_id)
    con.row_factory = sqlite3.Row
    events = []
    try:
        rows = con.execute(
            "SELECT mu.id, mu.logical_request_id, mu.session_id, mu.model_id, "
            "       mu.started_at, mu.input_tokens, mu.output_tokens, "
            "       mu.reasoning_tokens, mu.cache_read_input_tokens, "
            "       mu.cache_creation_input_tokens, mu.agent, "
            "       s.directory AS cwd "
            "FROM model_usage mu "
            "LEFT JOIN session s ON s.id = mu.session_id "
            "WHERE mu.status = 'completed' AND mu.started_at >= ? "
            "  AND (mu.input_tokens > 0 OR mu.output_tokens > 0) "
            "ORDER BY mu.started_at, mu.id",
            (max_ts,)).fetchall()
        new_ts, new_id = max_ts, max_id
        for r in rows:
            if (r["started_at"], r["id"]) <= (max_ts, max_id):
                continue
            new_ts, new_id = r["started_at"], r["id"]
            inp = r["input_tokens"] or 0
            out = r["output_tokens"] or 0
            cached = r["cache_read_input_tokens"] or 0
            cache_w = r["cache_creation_input_tokens"] or 0
            reasoning = r["reasoning_tokens"] or 0
            if inp == 0 and out == 0 and cached == 0 and cache_w == 0:
                continue
            agent_label = _DISPLAY_NAME.get(r["agent"] or "", r["agent"] or "")
            # cwd 记为「目录 | 子代理」便于 UI 分辨会话来源
            cwd = r["cwd"]
            if agent_label and agent_label != "主 Agent":
                cwd = f"{cwd} · {agent_label}" if cwd else agent_label
            events.append(make_event(
                AGENT_TYPE, r["session_id"] or "unknown",
                r["logical_request_id"], r["model_id"], _ts_iso(r["started_at"]),
                inp, cached, cache_w, out, reasoning, cwd, pricing_map,
                compute_costs))
        return events, (new_ts, new_id)
    except sqlite3.Error:
        return events, (max_ts, max_id)
    finally:
        con.close()
