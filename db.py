"""SQLite 存储层：增量用量记录、文件偏移、定价表。"""
import sqlite3
from contextlib import contextmanager
from config import DB_PATH, DEFAULT_PRICING

SCHEMA_STATEMENTS = [
    """CREATE TABLE IF NOT EXISTS usage_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        agent_type TEXT NOT NULL,
        session_id TEXT NOT NULL,
        turn_id TEXT,
        model TEXT,
        ts TEXT NOT NULL,
        ts_epoch INTEGER NOT NULL,
        input_tokens INTEGER DEFAULT 0,
        fresh_input_tokens INTEGER DEFAULT 0,
        cached_input_tokens INTEGER DEFAULT 0,
        cache_write_input_tokens INTEGER DEFAULT 0,
        output_tokens INTEGER DEFAULT 0,
        reasoning_output_tokens INTEGER DEFAULT 0,
        input_cost REAL DEFAULT 0,
        output_cost REAL DEFAULT 0,
        cache_read_cost REAL DEFAULT 0,
        cache_creation_cost REAL DEFAULT 0,
        total_cost REAL DEFAULT 0,
        cwd TEXT,
        UNIQUE(agent_type, session_id, turn_id)
    )""",
    """CREATE TABLE IF NOT EXISTS file_index (
        path TEXT PRIMARY KEY,
        size INTEGER DEFAULT 0,
        offset INTEGER DEFAULT 0,
        mtime TEXT,
        parsed_events INTEGER DEFAULT 0
    )""",
    """CREATE TABLE IF NOT EXISTS pricing (
        model TEXT PRIMARY KEY,
        display_name TEXT,
        input_per_million REAL,
        output_per_million REAL,
        cache_read_per_million REAL,
        cache_creation_per_million REAL,
        multiplier REAL DEFAULT 1.0,
        updated_at TEXT
    )""",
    """CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )""",
    "CREATE INDEX IF NOT EXISTS idx_usage_ts ON usage_events(ts_epoch)",
    "CREATE INDEX IF NOT EXISTS idx_usage_agent_ts ON usage_events(agent_type, ts_epoch)",
    "CREATE INDEX IF NOT EXISTS idx_usage_agent ON usage_events(agent_type)",
    "CREATE INDEX IF NOT EXISTS idx_usage_model ON usage_events(model)",
]


def _exec_schema(conn):
    """逐条执行建表/建索引。

    不用 executescript：它在 SQLite 里会先隐式 COMMIT 当前事务，
    会把迁移中的 RENAME/INSERT 拆成多个事务，中途失败会留下半完成状态。
    逐条 execute 让整段迁移保持在同一事务内，崩溃可整体回滚。"""
    for stmt in SCHEMA_STATEMENTS:
        conn.execute(stmt)


@contextmanager
def get_conn():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout=5000")
    conn.execute("PRAGMA journal_mode=WAL")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


_EVENT_COLS = (
    "agent_type, session_id, turn_id, model, ts, ts_epoch, "
    "input_tokens, fresh_input_tokens, cached_input_tokens, "
    "cache_write_input_tokens, output_tokens, reasoning_output_tokens, "
    "input_cost, output_cost, cache_read_cost, cache_creation_cost, "
    "total_cost, cwd"
)


def _migrate_dedup(conn):
    """修复历史重复数据 + 去重键升级。

    两类历史问题：
    1. 真实日志 token_count 无 turn_id，UNIQUE 对 NULL 不去重 → 回填指纹；
    2. 旧 UNIQUE 含 ts：Claude 同一回复重复落盘（时间戳不同）会各入一条，
       约束升级为 UNIQUE(agent_type, session_id, turn_id)，turn_id 指纹
       对 Codex 含 ts、对 Claude 为 message.id，均能真正去重。
    表结构保持不变，用重建表方式规避 UNIQUE 索引对回填的冲突。
    幂等：无 NULL turn_id、无重复、约束已升级时直接跳过。
    """
    from parser import _stable_turn_id
    def _fingerprint(r):
        return _stable_turn_id(
            r["ts"], r["model"], r["input_tokens"],
            r["cached_input_tokens"], r["cache_write_input_tokens"],
            r["output_tokens"], r["reasoning_output_tokens"])
    has_null = conn.execute(
        "SELECT COUNT(*) c FROM usage_events WHERE turn_id IS NULL"
    ).fetchone()["c"] > 0
    has_dup = conn.execute(
        "SELECT COUNT(*) c FROM (SELECT 1 FROM usage_events "
        "GROUP BY agent_type, session_id, turn_id HAVING COUNT(*)>1)"
    ).fetchone()["c"] > 0
    sql = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='usage_events'"
    ).fetchone()
    unique_has_ts = bool(sql) and "UNIQUE(agent_type, session_id, ts, turn_id)" in sql[0]
    if not (has_null or has_dup or unique_has_ts):
        return
    conn.execute("ALTER TABLE usage_events RENAME TO usage_events_old")
    _exec_schema(conn)
    rows = conn.execute(
        "SELECT " + _EVENT_COLS + " FROM usage_events_old ORDER BY id"
    ).fetchall()
    seen = set()
    batch = []
    for r in rows:
        turn_id = r["turn_id"]
        if not turn_id:
            turn_id = _fingerprint(r)
        key = (r["agent_type"], r["session_id"], turn_id)
        if key in seen:
            continue
        seen.add(key)
        batch.append((r["agent_type"], r["session_id"], turn_id, r["model"],
                      r["ts"], r["ts_epoch"], r["input_tokens"],
                      r["fresh_input_tokens"], r["cached_input_tokens"],
                      r["cache_write_input_tokens"], r["output_tokens"],
                      r["reasoning_output_tokens"], r["input_cost"],
                      r["output_cost"], r["cache_read_cost"],
                      r["cache_creation_cost"], r["total_cost"], r["cwd"]))
    conn.executemany(
        "INSERT INTO usage_events (" + _EVENT_COLS + ") VALUES(" +
        ",".join("?" * len(_EVENT_COLS.split(", "))) + ")", batch)
    conn.execute("DROP TABLE usage_events_old")
    # Renaming keeps old index names alive, so CREATE IF NOT EXISTS skips them.
    # Recreate the schema after dropping the old table to attach indexes newly.
    _exec_schema(conn)



def init_db():
    """初始化/迁移。返回是否发生默认定价变更（用于触发成本重算）。"""
    changed = 0
    with get_conn() as conn:
        cols = [r[1] for r in conn.execute(
            "PRAGMA table_info(usage_events)").fetchall()]
        if cols and "agent_type" not in cols:
            conn.execute("DROP TABLE IF EXISTS usage_events")
            conn.execute("DELETE FROM file_index")
        fi_cols = [r[1] for r in conn.execute(
            "PRAGMA table_info(file_index)").fetchall()]
        if fi_cols and "offset" not in fi_cols:
            conn.execute("ALTER TABLE file_index ADD COLUMN offset INTEGER DEFAULT 0")
        _exec_schema(conn)
        _migrate_dedup(conn)
        # 默认定价：新增模型插入；未定制过的模型（updated_at IS NULL，即从未在
        # UI 编辑过）随软件默认值升级，用户手工改过的（updated_at 非空）保留。
        for model, p in DEFAULT_PRICING.items():
            conn.execute(
                "INSERT OR IGNORE INTO pricing(model, display_name, "
                "input_per_million, output_per_million, "
                "cache_read_per_million, cache_creation_per_million, multiplier) "
                "VALUES(?,?,?,?,?,?,1.0)",
                (model, model, p["input"], p["output"],
                 p["cache_read"], p["cache_creation"]))
            cur = conn.execute(
                "UPDATE pricing SET input_per_million=?, output_per_million=?, "
                "cache_read_per_million=?, cache_creation_per_million=?, multiplier=1.0 "
                "WHERE model=? AND updated_at IS NULL "
                "AND (input_per_million != ? OR output_per_million != ? "
                "     OR cache_read_per_million != ? OR cache_creation_per_million != ?)",
                (p["input"], p["output"], p["cache_read"], p["cache_creation"], model,
                 p["input"], p["output"], p["cache_read"], p["cache_creation"]))
            changed += cur.rowcount
    # 默认价变化后或存在尚未计费的历史事件时重算成本（在事务提交后调用，避免写锁自死）
    with get_conn() as conn:
        has_unpriced = conn.execute(
            "SELECT 1 FROM usage_events WHERE total_cost = 0 "
            "AND (input_tokens > 0 OR output_tokens > 0) LIMIT 1"
        ).fetchone()
    if changed or has_unpriced:
        recompute_costs()
    return changed


def get_setting(key, default=None):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return row["value"] if row else default


def set_setting(key, value):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO settings(key, value) VALUES(?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, str(value)))


def get_pricing():
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM pricing ORDER BY model").fetchall()]


def get_pricing_map():
    with get_conn() as conn:
        return {r["model"]: dict(r) for r in conn.execute(
            "SELECT * FROM pricing").fetchall()}


def upsert_pricing(model, display_name, input_p, output_p,
                   cache_read_p, cache_creation_p, multiplier=1.0):
    import datetime
    now = datetime.datetime.now().isoformat()
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO pricing(model, display_name, input_per_million, "
            "output_per_million, cache_read_per_million, "
            "cache_creation_per_million, multiplier, updated_at) "
            "VALUES(?,?,?,?,?,?,?,?) "
            "ON CONFLICT(model) DO UPDATE SET display_name=excluded.display_name, "
            "input_per_million=excluded.input_per_million, "
            "output_per_million=excluded.output_per_million, "
            "cache_read_per_million=excluded.cache_read_per_million, "
            "cache_creation_per_million=excluded.cache_creation_per_million, "
            "multiplier=excluded.multiplier, updated_at=excluded.updated_at",
            (model, display_name, input_p, output_p,
             cache_read_p, cache_creation_p, multiplier, now))


_PRICE = "COALESCE((SELECT {col} FROM pricing WHERE model=usage_events.model),0)"

def delete_pricing(model):
    """删除某模型定价；删除后该模型视为未定价（成本归零），并重算历史成本。"""
    with get_conn() as conn:
        conn.execute("DELETE FROM pricing WHERE model=?", (model,))


def recompute_costs():
    """依据 pricing 表重新计算所有事件成本，支持大小写与中转站前缀。

    按 DISTINCT model 批量计算：每个模型使用 cost.find_pricing 获得统一定价，
    单条 SQL UPDATE 批量执行；计算语义与 cost.compute_costs 保持严格一致。
    """
    import cost
    pricing_map = get_pricing_map()
    with get_conn() as conn:
        distinct_models = [r[0] for r in conn.execute(
            "SELECT DISTINCT model FROM usage_events WHERE model IS NOT NULL").fetchall()]

        # Codex 与 Zcode 的 input_tokens 均含 cache（OpenAI 语义）
        fresh_expr = ("CASE WHEN agent_type IN ('codex','zcode') THEN "
                      "MAX(input_tokens - cached_input_tokens - cache_write_input_tokens, 0) "
                      "ELSE input_tokens END")
        effective_out_expr = ("CASE WHEN agent_type IN ('codex','zcode') THEN "
                              "output_tokens + reasoning_output_tokens "
                              "ELSE output_tokens END")

        for m in distinct_models:
            pr = cost.find_pricing(m, pricing_map)
            if pr:
                inp_p = float(pr["input_per_million"])
                out_p = float(pr["output_per_million"])
                cr_p = float(pr["cache_read_per_million"])
                cc_p = float(pr["cache_creation_per_million"])
                mult = float(pr.get("multiplier", 1.0) or 1.0)

                ic_expr = f"({inp_p} * {fresh_expr} / 1000000.0)"
                oc_expr = f"({out_p} * {effective_out_expr} / 1000000.0)"
                crc_expr = f"({cr_p} * cached_input_tokens / 1000000.0)"
                ccc_expr = f"({cc_p} * cache_write_input_tokens / 1000000.0)"

                conn.execute(
                    f"UPDATE usage_events SET "
                    f"fresh_input_tokens = {fresh_expr}, "
                    f"input_cost = {ic_expr}, "
                    f"output_cost = {oc_expr}, "
                    f"cache_read_cost = {crc_expr}, "
                    f"cache_creation_cost = {ccc_expr}, "
                    f"total_cost = ({ic_expr} + {oc_expr} + {crc_expr} + {ccc_expr}) * {mult} "
                    f"WHERE model = ?",
                    (m,)
                )
            else:
                conn.execute(
                    f"UPDATE usage_events SET "
                    f"fresh_input_tokens = {fresh_expr}, "
                    f"input_cost = 0.0, "
                    f"output_cost = 0.0, "
                    f"cache_read_cost = 0.0, "
                    f"cache_creation_cost = 0.0, "
                    f"total_cost = 0.0 "
                    f"WHERE model = ?",
                    (m,)
                )

        conn.execute(
            f"UPDATE usage_events SET "
            f"fresh_input_tokens = {fresh_expr}, "
            f"input_cost = 0.0, output_cost = 0.0, "
            f"cache_read_cost = 0.0, cache_creation_cost = 0.0, total_cost = 0.0 "
            f"WHERE model IS NULL"
        )
