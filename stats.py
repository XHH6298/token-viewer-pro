"""聚合统计：汇总、趋势、模型/会话/工具分解、时间范围。

缓存命中率（cache-normalized）：
  cache_read / (fresh_input + cache_creation + cache_read)
fresh_input 已按 agent 语义在写入时计算好存入 fresh_input_tokens。
"""
import time
import datetime
from zoneinfo import ZoneInfo
from config import TIME_RANGE_MAP, DEFAULT_TZ
import db

_TZ = ZoneInfo(DEFAULT_TZ)


def resolve_range(preset, now=None):
    if now is None:
        now = time.time()
    end = int(now)
    if preset == "today":
        local = datetime.datetime.fromtimestamp(now, _TZ).replace(
            hour=0, minute=0, second=0, microsecond=0)
        start = int(local.timestamp())
    elif preset == "all":
        start = 0
    else:
        seconds = TIME_RANGE_MAP.get(preset, 86400)
        start = end - seconds
    return start, end


def _rate(fresh, cached, cw):
    denom = fresh + cw + cached
    return cached / denom if denom > 0 else 0.0


def _where(start, end, agent=None, extra=None):
    w = "WHERE ts_epoch BETWEEN ? AND ?"
    params = [start, end]
    if agent:
        w += " AND agent_type=?"
        params.append(agent)
    if extra:
        w += " " + extra
    return w, params


def get_summary(start, end, agent=None):
    w, params = _where(start, end, agent)
    with db.get_conn() as conn:
        row = conn.execute(
            "SELECT COUNT(*) as cnt, "
            "COALESCE(SUM(fresh_input_tokens),0) as fresh, "
            "COALESCE(SUM(cached_input_tokens),0) as cached, "
            "COALESCE(SUM(cache_write_input_tokens),0) as cw, "
            "COALESCE(SUM(CASE WHEN agent_type IN ('codex','zcode','pi') THEN output_tokens + "
            "reasoning_output_tokens ELSE output_tokens END),0) as outp, "
            "COALESCE(SUM(total_cost),0) as cost, "
            "COALESCE(SUM(input_cost),0) as ic, "
            "COALESCE(SUM(output_cost),0) as oc, "
            "COALESCE(SUM(cache_read_cost),0) as crc, "
            "COALESCE(SUM(cache_creation_cost),0) as ccc "
            "FROM usage_events " + w, params).fetchone()
    fresh = row["fresh"]; cached = row["cached"]; cw = row["cw"]; outp = row["outp"]
    return {
        "request_count": row["cnt"],
        "total_tokens": fresh + outp + cw + cached,
        "total_cost": round(row["cost"], 6),
        "cache_hit_rate": round(_rate(fresh, cached, cw), 4),
        "input_tokens": fresh,
        "output_tokens": outp,
        "cache_read_tokens": cached,
        "cache_creation_tokens": cw,
        "cost_breakdown": {
            "input": round(row["ic"], 6),
            "output": round(row["oc"], 6),
            "cache_read": round(row["crc"], 6),
            "cache_creation": round(row["ccc"], 6),
        },
    }


def get_agents(start, end):
    with db.get_conn() as conn:
        rows = conn.execute(
            "SELECT agent_type, COUNT(*) as cnt, "
            "COALESCE(SUM(fresh_input_tokens),0) as fresh, "
            "COALESCE(SUM(cached_input_tokens),0) as cached, "
            "COALESCE(SUM(cache_write_input_tokens),0) as cw, "
            "COALESCE(SUM(CASE WHEN agent_type IN ('codex','zcode','pi') THEN output_tokens + "
            "reasoning_output_tokens ELSE output_tokens END),0) as outp, "
            "COALESCE(SUM(total_cost),0) as cost "
            "FROM usage_events WHERE ts_epoch BETWEEN ? AND ? "
            "GROUP BY agent_type ORDER BY cost DESC", (start, end)).fetchall()
    out = []
    for r in rows:
        fresh = r["fresh"]; cached = r["cached"]; cw = r["cw"]
        out.append({
            "agent_type": r["agent_type"],
            "display_name": {"codex": "Codex", "claude": "Claude Code", "antigravity": "Antigravity", "zcode": "Zcode", "pi": "Pi"}.get(r["agent_type"], r["agent_type"]),
            "request_count": r["cnt"],
            "tokens": fresh + r["outp"] + cw + cached,
            "cost": round(r["cost"], 6),
            "cache_hit_rate": round(_rate(fresh, cached, cw), 4),
        })
    return out


def get_trend(start, end, agent=None, bucket="day"):
    fmt = "%Y-%m-%d %H" if bucket == "hour" else "%Y-%m-%d"
    w, params = _where(start, end, agent)
    # SQL 按 UTC 小时聚合，再在 Python 中按 DEFAULT_TZ 映射到本地时间桶，
    # 与 resolve_range("today") 的边界保持一致，避免依赖操作系统时区。
    buckets = {}
    with db.get_conn() as conn:
        rows = conn.execute(
            "SELECT CAST(ts_epoch / 3600 AS INTEGER) as utc_hour, "
            "COUNT(*) as cnt, "
            "COALESCE(SUM(fresh_input_tokens),0) as fresh, "
            "COALESCE(SUM(cached_input_tokens),0) as cached, "
            "COALESCE(SUM(cache_write_input_tokens),0) as cw, "
            "COALESCE(SUM(CASE WHEN agent_type IN ('codex','zcode','pi') THEN output_tokens + "
            "reasoning_output_tokens ELSE output_tokens END),0) as outp, "
            "COALESCE(SUM(total_cost),0) as cost "
            "FROM usage_events " + w + " GROUP BY utc_hour ORDER BY utc_hour", params).fetchall()
    for r in rows:
        local = datetime.datetime.fromtimestamp(r["utc_hour"] * 3600, _TZ)
        key = local.strftime(fmt)
        agg = buckets.setdefault(key, {
            "cnt": 0, "fresh": 0, "cached": 0, "cw": 0, "outp": 0, "cost": 0.0})
        agg["cnt"] += r["cnt"]
        agg["fresh"] += r["fresh"]
        agg["cached"] += r["cached"]
        agg["cw"] += r["cw"]
        agg["outp"] += r["outp"]
        agg["cost"] += r["cost"]
    out = []
    for key, agg in buckets.items():
        fresh = agg["fresh"]; cached = agg["cached"]; cw = agg["cw"]
        out.append({
            "bucket": key,
            "tokens": fresh + agg["outp"] + cw + cached,
            "cost": round(agg["cost"], 6),
            "cache_hit_rate": round(_rate(fresh, cached, cw), 4),
            "count": agg["cnt"],
        })
    return out


def get_models(start, end, agent=None):
    w, params = _where(start, end, agent)
    with db.get_conn() as conn:
        rows = conn.execute(
            "SELECT agent_type, model, COUNT(*) as cnt, "
            "COALESCE(SUM(fresh_input_tokens),0) as fresh, "
            "COALESCE(SUM(cached_input_tokens),0) as cached, "
            "COALESCE(SUM(cache_write_input_tokens),0) as cw, "
            "COALESCE(SUM(CASE WHEN agent_type IN ('codex','zcode','pi') THEN output_tokens + "
            "reasoning_output_tokens ELSE output_tokens END),0) as outp, "
            "COALESCE(SUM(total_cost),0) as cost "
            "FROM usage_events " + w + " GROUP BY agent_type, model ORDER BY cost DESC", params).fetchall()
    out = []
    for r in rows:
        fresh = r["fresh"]; cached = r["cached"]; cw = r["cw"]
        out.append({
            "agent_type": r["agent_type"],
            "model": r["model"] or "unknown",
            "request_count": r["cnt"],
            "tokens": fresh + r["outp"] + cw + cached,
            "cost": round(r["cost"], 6),
            "cache_hit_rate": round(_rate(fresh, cached, cw), 4),
        })
    return out


def get_sessions(start, end, agent=None):
    w, params = _where(start, end, agent)
    with db.get_conn() as conn:
        rows = conn.execute(
            "SELECT agent_type, session_id, model, COUNT(*) as cnt, "
            "MIN(ts) as first_ts, MAX(ts) as last_ts, cwd, "
            "COALESCE(SUM(fresh_input_tokens),0) as fresh, "
            "COALESCE(SUM(cached_input_tokens),0) as cached, "
            "COALESCE(SUM(cache_write_input_tokens),0) as cw, "
            "COALESCE(SUM(CASE WHEN agent_type IN ('codex','zcode','pi') THEN output_tokens + "
            "reasoning_output_tokens ELSE output_tokens END),0) as outp, "
            "COALESCE(SUM(total_cost),0) as cost "
            "FROM usage_events " + w + " GROUP BY agent_type, session_id ORDER BY last_ts DESC", params).fetchall()
    out = []
    for r in rows:
        fresh = r["fresh"]; cached = r["cached"]; cw = r["cw"]
        out.append({
            "agent_type": r["agent_type"],
            "session_id": r["session_id"],
            "model": r["model"] or "unknown",
            "request_count": r["cnt"],
            "tokens": fresh + r["outp"] + cw + cached,
            "cost": round(r["cost"], 6),
            "cache_hit_rate": round(_rate(fresh, cached, cw), 4),
            "first_ts": r["first_ts"],
            "last_ts": r["last_ts"],
            "cwd": r["cwd"],
        })
    return out


def get_health():
    with db.get_conn() as conn:
        ev = conn.execute("SELECT COUNT(*) as c FROM usage_events").fetchone()["c"]
        fi = conn.execute("SELECT COUNT(*) as c FROM file_index").fetchone()["c"]
    return {"event_count": ev, "file_count": fi}
