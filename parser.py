"""扫描调度层：按适配器发现文件、增量解析、统一入库。

每个 AI 工具一个 adapter（adapters/ 包），本模块只负责：
文件枚举 → mtime 门 → 解析 → INSERT OR IGNORE → file_index 游标更新。
file_index.offset 对普通文件是字节偏移；对 antigravity 是 max_step_idx；
对 zcode（单文件游标）是 (max_started_at_ms, max_id) 元组序列化值。
"""
import os
import sqlite3
import threading
from config import SESSIONS_DIR, ARCHIVED_DIR
import adapters.claude as claude_adapter
import adapters.codex as codex_adapter
import adapters.antigravity as antigravity_adapter
import adapters.zcode as zcode_adapter
import adapters.pi as pi_adapter

# 兼容旧引用（测试通过给 parser 模块属性赋值来重定向目录，扫描时读取这里）
CLAUDE_PROJECTS_DIR = claude_adapter.CLAUDE_PROJECTS_DIR
SESSIONS_DIR = SESSIONS_DIR
ARCHIVED_DIR = ARCHIVED_DIR
ANTIGRAVITY_CONVERSATIONS_DIR = antigravity_adapter.ANTIGRAVITY_CONVERSATIONS_DIR
PI_SESSIONS_DIR = pi_adapter.PI_SESSIONS_DIR
# zcode 单文件数据源；测试设为 None 可隔离（不扫真实 Zcode 库）
ZCODE_DB = zcode_adapter.ZCODE_DB
from adapters.common import stable_turn_id as _stable_turn_id, parse_iso  # noqa: F401

INSERT_SQL = (
    "INSERT OR IGNORE INTO usage_events "
    "(agent_type, session_id, turn_id, model, ts, ts_epoch, "
    " input_tokens, fresh_input_tokens, cached_input_tokens, "
    " cache_write_input_tokens, output_tokens, reasoning_output_tokens, "
    " input_cost, output_cost, cache_read_cost, "
    " cache_creation_cost, total_cost, cwd) "
    "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
)


def list_session_files():
    files = []
    files.extend(codex_adapter.list_files())
    files.extend(claude_adapter.list_files())
    files.extend(antigravity_adapter.list_files())
    files.extend(zcode_adapter.list_files())
    files.extend(pi_adapter.list_files())
    return files


def _adapter_for(path):
    if antigravity_adapter.is_db_path(path):
        return antigravity_adapter
    if zcode_adapter.available() and path == str(zcode_adapter.ZCODE_DB):
        return zcode_adapter
    if path in claude_adapter.list_files():
        return claude_adapter
    if pi_adapter.PI_SESSIONS_DIR and path in pi_adapter.list_files():
        return pi_adapter
    return codex_adapter


# 串行化扫描：前端 10s 定时 refresh 可能重叠，并发双扫在去重修复前必然双写，
# 修复后仍会互相抢写锁，统一加锁保证一次只有一个扫描在写库。
_SCAN_LOCK = threading.Lock()


def scan_incremental():
    with _SCAN_LOCK:
        return _scan_incremental_locked()


def _scan_incremental_locked():
    import db
    import cost
    # 测试会重定向 parser 模块级目录变量，适配器目录须先于文件枚举同步
    claude_adapter.CLAUDE_PROJECTS_DIR = CLAUDE_PROJECTS_DIR
    codex_adapter.SESSIONS_DIR = SESSIONS_DIR
    codex_adapter.ARCHIVED_DIR = ARCHIVED_DIR
    antigravity_adapter.ANTIGRAVITY_CONVERSATIONS_DIR = ANTIGRAVITY_CONVERSATIONS_DIR
    zcode_adapter.ZCODE_DB = ZCODE_DB
    pi_adapter.PI_SESSIONS_DIR = PI_SESSIONS_DIR
    pricing_map = db.get_pricing_map()
    compute = cost.compute_costs
    files = list_session_files()
    with db.get_conn() as conn:
        indexed = {r["path"]: {"size": r["size"], "offset": r["offset"],
                                "mtime": r["mtime"]}
                   for r in conn.execute(
                       "SELECT path, size, offset, mtime FROM file_index")}
        changed = []
        for spath in files:
            if antigravity_adapter.is_db_path(spath):
                try:
                    st = os.stat(spath)
                    wal_path = spath + "-wal"
                    wal_st = os.stat(wal_path) if os.path.exists(wal_path) else None
                    size = st.st_size + (wal_st.st_size if wal_st else 0)
                    mtime = str(max(st.st_mtime, wal_st.st_mtime if wal_st else 0))
                except OSError:
                    continue
            else:
                try:
                    st = os.stat(spath)
                except OSError:
                    continue
                size = st.st_size
                mtime = str(st.st_mtime)
            old = indexed.get(spath)
            if (old and old["size"] == size and size > 0 and
                    old.get("mtime") == mtime):
                continue
            changed.append((spath, size, mtime, old))
        total_new = 0
        for spath, size, mtime, old in changed:
            adapter = _adapter_for(spath)
            start_offset = 0
            # Normal appends keep the old offset. A same-size rewrite must be
            # parsed from the beginning; continuing at EOF would hide changes.
            if old and old.get("offset"):
                if adapter is antigravity_adapter:
                    start_offset = old["offset"]
                elif (adapter is claude_adapter and size > old["size"] and
                        size >= old["offset"]):
                    start_offset = old["offset"]
                elif adapter is zcode_adapter:
                    start_offset = old["offset"]
            events, end_offset = adapter.parse_file(
                spath, pricing_map, compute, start_offset)
            if events:
                conn.executemany(INSERT_SQL, events)
                total_new += len(events)
            if isinstance(end_offset, tuple):
                # zcode 游标：(max_started_at_ms, max_id) 序列化为字符串
                offset_val = f"{end_offset[0]}:{end_offset[1]}"
            else:
                offset_val = end_offset
            conn.execute(
                "INSERT INTO file_index(path, size, offset, mtime, parsed_events) "
                "VALUES(?,?,?,?,?) ON CONFLICT(path) DO UPDATE SET "
                "size=excluded.size, offset=excluded.offset, mtime=excluded.mtime, "
                "parsed_events=excluded.parsed_events",
                (spath, size, offset_val, mtime, len(events)))
        # 清理已不存在文件的残留索引（归档/改名/删除后），避免 file_index 无限膨胀
        current_paths = set(files)
        if current_paths:
            conn.execute(
                "DELETE FROM file_index WHERE path NOT IN (%s)" %
                ",".join("?" * len(current_paths)), list(current_paths))
    return {"changed_files": len(changed), "new_events": total_new,
            "total_files": len(files)}
