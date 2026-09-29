"""Antigravity（反重力）适配器：~/.gemini/antigravity/conversations/*.db。

SQLite + Protobuf blob 存储，基于 steps.idx 增量读取（offset 列存 max_idx）。
"""
import datetime
import sqlite3
import urllib.parse
from pathlib import Path
from config import ANTIGRAVITY_CONVERSATIONS_DIR
from adapters.common import make_event


def list_files():
    if not ANTIGRAVITY_CONVERSATIONS_DIR or not ANTIGRAVITY_CONVERSATIONS_DIR.exists():
        return []
    return [str(p) for p in ANTIGRAVITY_CONVERSATIONS_DIR.glob("*.db")
            if not p.name.endswith(("-shm", "-wal"))]


def is_db_path(path):
    return str(path).replace("\\", "/").lower().endswith(".db")


def _parse_proto(b, subfields=None):
    """纯 Python 轻量 Protobuf TLV/Varint 解码器。

    subfields 为需要递归解析为子消息的字段编号集合/字典。不在集合内的字段
    一律作为 raw bytes 保留，避免 UTF-8 字符串等被误解码为子消息。
    """
    if subfields is None:
        subfields = set()
    idx = 0
    res = {}
    while idx < len(b):
        try:
            shift = 0
            tag = 0
            while True:
                byte = b[idx]
                idx += 1
                tag |= (byte & 0x7f) << shift
                shift += 7
                if not (byte & 0x80):
                    break
            wire = tag & 7
            field = tag >> 3
            if wire == 0:  # varint
                val = 0
                shift = 0
                while True:
                    byte = b[idx]
                    idx += 1
                    val |= (byte & 0x7f) << shift
                    shift += 7
                    if not (byte & 0x80):
                        break
                res.setdefault(field, []).append(('varint', val))
            elif wire == 1:  # fixed64
                res.setdefault(field, []).append(('fixed64', b[idx:idx+8]))
                idx += 8
            elif wire == 2:  # length-delimited
                shift = 0
                length = 0
                while True:
                    byte = b[idx]
                    idx += 1
                    length |= (byte & 0x7f) << shift
                    shift += 7
                    if not (byte & 0x80):
                        break
                val = b[idx:idx+length]
                idx += length
                if field in subfields:
                    nested = subfields.get(field) if isinstance(subfields, dict) else None
                    sub = _parse_proto(val, subfields=nested)
                    res.setdefault(field, []).append(('msg', sub))
                else:
                    res.setdefault(field, []).append(('bytes', val))
            elif wire == 5:  # fixed32
                res.setdefault(field, []).append(('fixed32', b[idx:idx+4]))
                idx += 4
            else:
                break
        except Exception:
            break
    return res


def _extract_str(val):
    if isinstance(val, bytes):
        return val.decode("utf-8", errors="ignore")
    return str(val) if val is not None else ""


def _get_cwd_from_blob(blob_bytes):
    if not blob_bytes:
        return None
    p = _parse_proto(blob_bytes, subfields={1: None})
    raw_uri = None
    if 7 in p and p[7]:
        raw_uri = _extract_str(p[7][0][1])
    elif 1 in p and p[1] and p[1][0][0] == "msg":
        sub = p[1][0][1]
        if 1 in sub and sub[1]:
            raw_uri = _extract_str(sub[1][0][1])
    if raw_uri:
        uri = urllib.parse.unquote(raw_uri)
        if uri.startswith("file:///"):
            path = uri[8:]
            if len(path) >= 3 and path[0] == "/" and path[2] == ":":
                path = path[1:]
            return path.replace("/", "\\")
        return uri
    return None


def parse_file(db_path, pricing_map, compute_costs, min_step_idx=0):
    """解析 Antigravity 会话数据库，支持基于 step.idx 的增量读取。"""
    uri = f"file:{Path(db_path).resolve()}?mode=ro"
    try:
        conn = sqlite3.connect(uri, uri=True)
    except Exception:
        return [], min_step_idx
    conn.row_factory = sqlite3.Row

    session_id = Path(db_path).stem
    cwd = None

    try:
        # 获取 cascade_id 作为稳定会话 ID
        meta_row = conn.execute(
            "SELECT cascade_id FROM trajectory_meta LIMIT 1").fetchone()
        if meta_row and meta_row["cascade_id"]:
            session_id = meta_row["cascade_id"]

        # 获取工作区目录
        blob_row = conn.execute(
            "SELECT data FROM trajectory_metadata_blob WHERE id='main'").fetchone()
        if blob_row and blob_row["data"]:
            cwd = _get_cwd_from_blob(blob_row["data"])

        # 从 gen_metadata 构建 message_id -> model 映射
        model_by_msg_id = {}
        fallback_model = None
        for r in conn.execute("SELECT idx, data FROM gen_metadata"):
            gp = _parse_proto(r["data"], subfields={1: {4: None}})
            m1 = gp.get(1, [{}])[0][1] if gp.get(1) else {}
            model_bytes = (m1.get(19, [('bytes', b'')])[0][1] or
                           m1.get(22, [('bytes', b'')])[0][1] or
                           m1.get(21, [('bytes', b'')])[0][1])
            model_str = _extract_str(model_bytes) if model_bytes else None
            if model_str:
                fallback_model = model_str
            msg4 = m1.get(4, [('msg', {})])[0][1]
            msg7 = msg4.get(7, [])
            mid = _extract_str(msg7[0][1]) if msg7 else None
            if mid and model_str:
                model_by_msg_id[mid] = model_str

        # 读取大模型步骤 (step_type=15)
        steps = conn.execute(
            "SELECT idx, metadata FROM steps WHERE step_type=15 AND idx >= ? ORDER BY idx",
            (min_step_idx,)
        ).fetchall()

        events = []
        max_idx = min_step_idx
        for s in steps:
            s_idx = s["idx"]
            if s_idx >= max_idx:
                max_idx = s_idx + 1
            if not s["metadata"]:
                continue
            sp = _parse_proto(s["metadata"], subfields={1: None, 9: None})
            ts_field = sp.get(1, [('msg', {})])[0][1]
            ts_sec = ts_field.get(1, [('varint', 0)])[0][1]
            if ts_sec:
                ts_iso = datetime.datetime.fromtimestamp(
                    ts_sec, tz=datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            else:
                ts_iso = ""

            usage = sp.get(9, [('msg', {})])[0][1]
            if not usage:
                continue
            varints = {k: v[0][1] for k, v in usage.items() if v[0][0] == "varint"}
            inp = varints.get(2, 0)
            out = varints.get(3, 0)
            cached = varints.get(5, 0)
            cache_w = varints.get(4, 0)
            reasoning = varints.get(9, 0)

            if inp == 0 and out == 0 and cached == 0 and cache_w == 0:
                continue

            msg7 = usage.get(7, [])
            mid = _extract_str(msg7[0][1]) if msg7 else None

            model = model_by_msg_id.get(mid) or fallback_model or "gemini-3.8-flash"
            turn_id = mid or f"{ts_iso}|{s_idx}"

            events.append(make_event(
                "antigravity", session_id, turn_id, model, ts_iso,
                inp, cached, cache_w, out, reasoning, cwd, pricing_map,
                compute_costs
            ))

        return events, max_idx
    finally:
        conn.close()
