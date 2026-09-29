"""核心逻辑单元测试：成本、解析、时区、定价重算。"""
import json
import os
import tempfile
import unittest
from pathlib import Path
from zoneinfo import ZoneInfo

os.environ["TOKEN_VIEWER_DB"] = os.path.join(
    tempfile.gettempdir(), "token_viewer_unittest.db")
for _f in ("token_viewer_unittest.db", "token_viewer_unittest.db-wal",
           "token_viewer_unittest.db-shm"):
    try:
        os.remove(os.path.join(tempfile.gettempdir(), _f))
    except OSError:
        pass

import cost
import db
import parser
import stats

DEFAULT_TZ = stats.DEFAULT_TZ


def _reset_db():
    with db.get_conn() as conn:
        conn.execute("DELETE FROM usage_events")
        conn.execute("DELETE FROM file_index")


def _claude_line(ts, model="claude-sonnet-4", inp=10, cached=2, cw=1, out=3,
                 stop_reason="tool_use", msg_id=None):
    message = {
        "model": model,
        "usage": {
            "input_tokens": inp,
            "cache_read_input_tokens": cached,
            "cache_creation_input_tokens": cw,
            "output_tokens": out,
            "output_tokens_details": {"thinking_tokens": 1},
        },
    }
    if stop_reason is not None:
        message["stop_reason"] = stop_reason
    if msg_id:
        message["id"] = msg_id
    return json.dumps({
        "type": "assistant",
        "timestamp": ts,
        "sessionId": "sess-1",
        "cwd": "C:\\work\\demo",
        "message": message,
    }) + "\n"


def _codex_lines(session="s1", model="gpt-5-codex", turn="t1",
                 ts="2026-08-13T09:00:00+00:00", inp=100, cached=30, cw=10, out=20):
    meta = json.dumps({"type": "session_meta",
                       "payload": {"session_id": session, "cwd": "C:\\work\\demo"},
                       "timestamp": ts})
    turn_ctx = json.dumps({"type": "turn_context",
                           "payload": {"model": model}, "timestamp": ts})
    token = json.dumps({"type": "event_msg", "payload": {
        "type": "token_count", "turn_id": turn,
        "info": {"last_token_usage": {
            "input_tokens": inp, "cached_input_tokens": cached,
            "cache_write_input_tokens": cw, "output_tokens": out}}},
        "timestamp": ts})
    return meta + "\n" + turn_ctx + "\n" + token + "\n"


class CostTest(unittest.TestCase):
    def setUp(self):
        db.init_db()
        _reset_db()

    def test_codex_fresh_input(self):
        costs = cost.compute_costs("codex", "gpt-5", 100, 30, 10, 20,
                                   db.get_pricing_map())
        self.assertEqual(costs["fresh_input"], 60)

    def test_claude_fresh_input_keeps_input(self):
        costs = cost.compute_costs("claude", "claude-sonnet-4", 100, 30, 10, 20,
                                   db.get_pricing_map())
        self.assertEqual(costs["fresh_input"], 100)

    def test_unknown_model_zero_cost(self):
        costs = cost.compute_costs("codex", "nope-model", 100, 30, 10, 20,
                                   db.get_pricing_map())
        self.assertEqual(costs["total_cost"], 0.0)
        self.assertEqual(costs["fresh_input"], 60)

    def test_codex_reasoning_included_in_output_cost(self):
        # Codex 的 output_tokens 不含 reasoning，有效输出 = output + reasoning
        pm = db.get_pricing_map()
        no_reasoning = cost.compute_costs("codex", "gpt-5", 100, 0, 0, 100,
                                          pm, reasoning=0)
        with_reasoning = cost.compute_costs("codex", "gpt-5", 100, 0, 0, 100,
                                            pm, reasoning=50)
        # reasoning 50 token 额外计入输出成本
        self.assertGreater(with_reasoning["output_cost"],
                           no_reasoning["output_cost"])
        self.assertGreater(with_reasoning["total_cost"],
                           no_reasoning["total_cost"])
        # 输出单价 = opm/1e6：额外 50 token
        opm = pm["gpt-5"]["output_per_million"]
        self.assertAlmostEqual(with_reasoning["output_cost"] -
                               no_reasoning["output_cost"], 50 * opm / 1e6, places=8)

    def test_claude_reasoning_not_double_counted(self):
        # Claude 的 thinking 已含在 output_tokens，reasoning 不额外计
        pm = db.get_pricing_map()
        costs = cost.compute_costs("claude", "claude-sonnet-4", 100, 0, 0, 100,
                                   pm, reasoning=50)  # 传了但不该生效
        self.assertEqual(costs["output_cost"],
                         cost.compute_costs("claude", "claude-sonnet-4", 100, 0, 0, 100,
                                            pm, reasoning=0)["output_cost"])


class ParserTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.claude_dir = Path(self.tmp.name) / "claude_projects"
        self.codex_dir = Path(self.tmp.name) / "codex_sessions"
        self.claude_dir.mkdir()
        self.codex_dir.mkdir()
        self._orig = (parser.CLAUDE_PROJECTS_DIR, parser.SESSIONS_DIR,
                      parser.ARCHIVED_DIR, parser.ANTIGRAVITY_CONVERSATIONS_DIR,
                      parser.ZCODE_DB, parser.PI_SESSIONS_DIR)
        parser.CLAUDE_PROJECTS_DIR = self.claude_dir
        parser.SESSIONS_DIR = self.codex_dir
        parser.ARCHIVED_DIR = None
        parser.ANTIGRAVITY_CONVERSATIONS_DIR = None
        parser.ZCODE_DB = None
        parser.PI_SESSIONS_DIR = None
        db.init_db()
        _reset_db()

    def tearDown(self):
        (parser.CLAUDE_PROJECTS_DIR, parser.SESSIONS_DIR,
         parser.ARCHIVED_DIR, parser.ANTIGRAVITY_CONVERSATIONS_DIR,
         parser.ZCODE_DB, parser.PI_SESSIONS_DIR) = self._orig


    def _claude_file(self):
        proj = self.claude_dir / "p1"
        proj.mkdir()
        return proj / "sess.jsonl"

    def test_claude_offset_incremental(self):
        f = self._claude_file()
        f.write_text(_claude_line("2026-08-13T10:00:00+08:00"), encoding="utf-8")
        self.assertEqual(parser.scan_incremental()["new_events"], 1)
        self.assertEqual(parser.scan_incremental()["new_events"], 0)
        with f.open("a", encoding="utf-8") as fh:
            fh.write(_claude_line("2026-08-13T10:05:00+08:00", inp=20))
        r = parser.scan_incremental()
        self.assertEqual(r["changed_files"], 1)
        self.assertEqual(r["new_events"], 1)
        with db.get_conn() as conn:
            n = conn.execute("SELECT COUNT(*) FROM usage_events").fetchone()[0]
        self.assertEqual(n, 2)

    def test_partial_tail_resume(self):
        f = self._claude_file()
        f.write_text(_claude_line("2026-08-13T10:00:00+08:00"), encoding="utf-8")
        full = _claude_line("2026-08-13T10:06:00+08:00", inp=5)
        cut = len(full) // 2
        with f.open("a", encoding="utf-8") as fh:
            fh.write(full[:cut])
        r1 = parser.scan_incremental()
        self.assertEqual(r1["new_events"], 1)
        with db.get_conn() as conn:
            off = conn.execute(
                "SELECT offset FROM file_index WHERE path=?", (str(f),)
            ).fetchone()["offset"]
        self.assertLess(off, os.path.getsize(str(f)))
        with f.open("a", encoding="utf-8") as fh:
            fh.write(full[cut:])
        r2 = parser.scan_incremental()
        self.assertEqual(r2["new_events"], 1)
        with db.get_conn() as conn:
            n = conn.execute("SELECT COUNT(*) FROM usage_events").fetchone()[0]
        self.assertEqual(n, 2)

    def test_same_size_mtime_change_is_rescanned(self):
        f = self._claude_file()
        original = _claude_line("2026-08-13T10:00:00+08:00", inp=10)
        f.write_text(original, encoding="utf-8")
        self.assertEqual(parser.scan_incremental()["changed_files"], 1)
        modified = original.replace('"input_tokens": 10', '"input_tokens": 20')
        self.assertEqual(len(modified), len(original))
        f.write_text(modified, encoding="utf-8")
        st = os.stat(f)
        os.utime(f, ns=(st.st_atime_ns, st.st_mtime_ns + 1_000_000_000))
        result = parser.scan_incremental()
        self.assertEqual(result["changed_files"], 1)
        with db.get_conn() as conn:
            inputs = [r[0] for r in conn.execute(
                "SELECT input_tokens FROM usage_events ORDER BY input_tokens")]
        self.assertIn(20, inputs)

    def test_codex_full_reparse_keeps_context(self):
        f = self.codex_dir / "sess.jsonl"
        f.write_text(_codex_lines(), encoding="utf-8")
        self.assertEqual(parser.scan_incremental()["new_events"], 1)
        with f.open("a", encoding="utf-8") as fh:
            fh.write(_codex_lines(turn="t2", ts="2026-08-13T09:10:00+00:00", inp=50))
        # Codex 文件从头重扫，new_events 包含去重前的解析数，以入库结果为准
        parser.scan_incremental()
        with db.get_conn() as conn:
            rows = conn.execute(
                "SELECT session_id, model, input_tokens FROM usage_events "
                "ORDER BY ts_epoch").fetchall()
        self.assertEqual([dict(x) for x in rows], [
            {"session_id": "s1", "model": "gpt-5-codex", "input_tokens": 100},
            {"session_id": "s1", "model": "gpt-5-codex", "input_tokens": 50},
        ])

    def test_claude_streaming_shards_skipped(self):
        """流式中间分片(无 stop_reason 键)和被中断请求(stop_reason=None)不入库。"""
        f = self._claude_file()
        shards = (
            # 中间分片: 大 input、无 stop_reason 键、output=0
            json.dumps({
                "type": "assistant", "timestamp": "2026-08-13T10:00:00+08:00",
                "sessionId": "sess-1", "cwd": "C:\\work\\demo",
                "message": {"model": "claude-sonnet-4", "id": "msg_1",
                            "usage": {"input_tokens": 54023, "output_tokens": 0}},
            }) + "\n"
            # 被中断: stop_reason=None
            + _claude_line("2026-08-13T10:00:01+08:00", inp=54023, out=0,
                           stop_reason=None, msg_id="msg_1")
            # 收尾条: 真实计费结果
            + _claude_line("2026-08-13T10:00:02+08:00", inp=28078, cached=0,
                           cw=0, out=507, msg_id="msg_1")
        )
        f.write_text(shards, encoding="utf-8")
        self.assertEqual(parser.scan_incremental()["new_events"], 1)
        with db.get_conn() as conn:
            row = conn.execute(
                "SELECT input_tokens, cached_input_tokens FROM usage_events"
            ).fetchone()
        self.assertEqual((row["input_tokens"], row["cached_input_tokens"]),
                         (28078, 0))

    def test_claude_duplicate_final_shards_dedup(self):
        """同一 message 的收尾条被原样重复落盘(时间戳不同)→ 只入一条。"""
        f = self._claude_file()
        f.write_text(
            _claude_line("2026-08-13T10:00:00+08:00", msg_id="msg_1") +
            _claude_line("2026-08-13T10:00:00.300+08:00", msg_id="msg_1") +
            _claude_line("2026-08-13T10:00:00.600+08:00", msg_id="msg_1"),
            encoding="utf-8")
        parser.scan_incremental()
        parser.scan_incremental()
        with db.get_conn() as conn:
            n = conn.execute("SELECT COUNT(*) FROM usage_events").fetchone()[0]
        self.assertEqual(n, 1)


class DedupRegressionTest(unittest.TestCase):
    """回归：真实日志 token_count 无 turn_id，全量重扫/多目录/存量库均不得重复入库。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.claude_dir = Path(self.tmp.name) / "claude_projects"
        self.codex_dir = Path(self.tmp.name) / "codex_sessions"
        self.claude_dir.mkdir()
        self.codex_dir.mkdir()
        self._orig = (parser.CLAUDE_PROJECTS_DIR, parser.SESSIONS_DIR,
                      parser.ARCHIVED_DIR, parser.ANTIGRAVITY_CONVERSATIONS_DIR,
                      parser.ZCODE_DB, parser.PI_SESSIONS_DIR)
        parser.CLAUDE_PROJECTS_DIR = self.claude_dir
        parser.SESSIONS_DIR = self.codex_dir
        parser.ARCHIVED_DIR = None
        parser.ANTIGRAVITY_CONVERSATIONS_DIR = None
        parser.ZCODE_DB = None
        parser.PI_SESSIONS_DIR = None
        db.init_db()
        _reset_db()

    def tearDown(self):
        (parser.CLAUDE_PROJECTS_DIR, parser.SESSIONS_DIR,
         parser.ARCHIVED_DIR, parser.ANTIGRAVITY_CONVERSATIONS_DIR,
         parser.ZCODE_DB, parser.PI_SESSIONS_DIR) = self._orig


    def test_codex_no_turn_id_full_reparse_dedup(self):
        """真实 Codex 日志无 turn_id：文件每次增长触发全量重扫，历史事件不得重复。"""
        header = json.dumps({"timestamp": "2026-08-13T00:43:00Z", "type": "session_meta",
                             "payload": {"session_id": "s1"}}) + "\n"
        ctx = json.dumps({"timestamp": "2026-08-13T00:43:00Z", "type": "turn_context",
                          "payload": {"model": "glm-5.2"}}) + "\n"

        def tok(ts, inp):
            return json.dumps({"timestamp": ts, "type": "event_msg", "payload": {
                "type": "token_count", "info": {"last_token_usage": {
                    "input_tokens": inp, "cached_input_tokens": 0,
                    "cache_write_input_tokens": 0, "output_tokens": 10}}}}) + "\n"

        f = self.codex_dir / "sess.jsonl"
        f.write_text(header + ctx + tok("2026-08-13T00:43:26.865Z", 100), encoding="utf-8")
        self.assertEqual(parser.scan_incremental()["new_events"], 1)
        # 文件增长 → 全量重扫（含历史）+ 新增一条
        f.write_text(header + ctx + tok("2026-08-13T00:43:26.865Z", 100)
                     + tok("2026-08-13T00:43:30.000Z", 150), encoding="utf-8")
        parser.scan_incremental()
        # 再扫一次（大小不变，应跳过）
        parser.scan_incremental()
        with db.get_conn() as c:
            n = c.execute("SELECT COUNT(*) FROM usage_events").fetchone()[0]
        self.assertEqual(n, 2)

    def test_claude_same_session_two_dirs_dedup(self):
        """同一 session 出现在两个项目目录（改名/多 cwd）→ 只计一次。"""
        line = _claude_line("2026-08-13T10:00:00+08:00", inp=10)
        d1 = self.claude_dir / "d1"
        d2 = self.claude_dir / "d2"
        d1.mkdir()
        d2.mkdir()
        (d1 / "a.jsonl").write_text(line, encoding="utf-8")
        (d2 / "b.jsonl").write_text(line, encoding="utf-8")
        parser.scan_incremental()
        with db.get_conn() as c:
            n = c.execute("SELECT COUNT(*) FROM usage_events").fetchone()[0]
        self.assertEqual(n, 1)

    def test_migration_dedups_existing_null_turn_id_rows(self):
        """存量库中 turn_id=NULL 的重复行（历史污染），init_db 迁移后应清理并回填指纹。"""
        ev = ("claude", "sess-m", None, "claude-sonnet-4",
              "2026-08-13T10:00:00+08:00", 1786600000, 10, 10, 2, 1, 3, 1,
              0.0, 0.0, 0.0, 0.0, 0.0, "C:\\x")
        with db.get_conn() as c:
            c.executemany(parser.INSERT_SQL, [ev, ev])
            n = c.execute("SELECT COUNT(*) FROM usage_events").fetchone()[0]
        self.assertEqual(n, 2)
        db.init_db()  # 触发迁移
        with db.get_conn() as c:
            n = c.execute("SELECT COUNT(*) FROM usage_events").fetchone()[0]
            tid = c.execute("SELECT turn_id FROM usage_events").fetchone()["turn_id"]
        self.assertEqual(n, 1)
        self.assertIsNotNone(tid)
        with db.get_conn() as c:
            names = {r[0] for r in c.execute(
                "SELECT name FROM sqlite_master WHERE type='index'")}
        self.assertLessEqual(
            {"idx_usage_ts", "idx_usage_agent_ts", "idx_usage_agent",
             "idx_usage_model"}, names)

    def test_scan_serialized_no_duplicate_on_overlap(self):
        """并发双扫同一文件时，串行化 + 去重键保证只入库一次。"""
        line = _claude_line("2026-08-13T10:00:00+08:00", inp=10)
        f = self.claude_dir / "p1"
        f.mkdir()
        (f / "sess.jsonl").write_text(line, encoding="utf-8")
        results = []
        def worker():
            results.append(parser.scan_incremental())
        import threading
        ts = [threading.Thread(target=worker) for _ in range(4)]
        for t in ts: t.start()
        for t in ts: t.join()
        with db.get_conn() as c:
            n = c.execute("SELECT COUNT(*) FROM usage_events").fetchone()[0]
        self.assertEqual(n, 1)


class StatsTest(unittest.TestCase):
    def setUp(self):
        db.init_db()
        _reset_db()

    def test_today_range_aligned_to_default_tz(self):
        start, end = stats.resolve_range("today", now=1786584000)
        local = __import__("datetime").datetime.fromtimestamp(
            start, ZoneInfo(DEFAULT_TZ))
        self.assertEqual((local.hour, local.minute, local.second), (0, 0, 0))

    def test_trend_uses_configured_tz(self):
        epoch = 1786554000
        with db.get_conn() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO usage_events "
                "(agent_type, session_id, model, ts, ts_epoch, input_tokens, "
                "fresh_input_tokens, cached_input_tokens, "
                "cache_write_input_tokens, output_tokens, total_cost) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                ("claude", "sess-tz", "claude-sonnet-4", str(epoch), epoch,
                 10, 10, 2, 1, 3, 1.0))
        trend = stats.get_trend(epoch - 3600, epoch + 3600, bucket="hour")
        expected = __import__("datetime").datetime.fromtimestamp(
            epoch, ZoneInfo(DEFAULT_TZ)).strftime("%Y-%m-%d %H")
        self.assertEqual([t["bucket"] for t in trend], [expected])


class RecomputeTest(unittest.TestCase):
    def setUp(self):
        db.init_db()
        _reset_db()

    def test_recompute_updates_costs_without_rescan(self):
        with db.get_conn() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO usage_events "
                "(agent_type, session_id, model, ts, ts_epoch, input_tokens, "
                "fresh_input_tokens, cached_input_tokens, "
                "cache_write_input_tokens, output_tokens, total_cost) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                ("codex", "sess-cost", "gpt-5", "2026-08-13T00:00:00Z",
                 1786550400, 100, 60, 30, 10, 20, 0.0))
        with db.get_conn() as conn:
            self.assertEqual(
                conn.execute("SELECT total_cost FROM usage_events").fetchone()["total_cost"],
                0.0)
        db.recompute_costs()
        with db.get_conn() as conn:
            row = conn.execute(
                "SELECT total_cost, fresh_input_tokens FROM usage_events").fetchone()
        self.assertGreater(row["total_cost"], 0.0)
class AntigravityTest(unittest.TestCase):
    def setUp(self):
        db.init_db()
        _reset_db()

    def test_pricing_fuzzy_lookup(self):
        pricing_map = db.get_pricing_map()
        # Direct hit
        pr = cost.find_pricing("gemini-3.8-flash", pricing_map)
        self.assertIsNotNone(pr)
        self.assertEqual(pr["input_per_million"], 1.50)
        self.assertEqual(pr["output_per_million"], 7.50)

        # Fuzzy hit: suffix -high
        pr_high = cost.find_pricing("gemini-3.8-flash-high", pricing_map)
        self.assertIsNotNone(pr_high)
        self.assertEqual(pr_high["input_per_million"], 1.50)

        # Fuzzy hit: suffix -thinking
        pr_think = cost.find_pricing("claude-opus-4-6-thinking", pricing_map)
        self.assertIsNotNone(pr_think)
        self.assertEqual(pr_think["input_per_million"], 15.00)

        # GLM 5.3 flash direct hit
        pr_glm = cost.find_pricing("glm-5.3-flash", pricing_map)
        self.assertIsNotNone(pr_glm)
        self.assertEqual(pr_glm["input_per_million"], 0.15)
        self.assertEqual(pr_glm["output_per_million"], 0.50)
        self.assertEqual(pr_glm["cache_read_per_million"], 0.03)

        # Case-insensitivity test (all uppercase, mixed case)
        pr_upper = cost.find_pricing("GLM-5.3-FLASH", pricing_map)
        self.assertIsNotNone(pr_upper)
        self.assertEqual(pr_upper["input_per_million"], 0.15)

        # Provider prefix + mixed case (e.g. zai-org/GLM-5.3-Flash, openai/GPT-4O)
        pr_prefixed = cost.find_pricing("zai-org/GLM-5.3-Flash", pricing_map)
        self.assertIsNotNone(pr_prefixed)
        self.assertEqual(pr_prefixed["input_per_million"], 0.15)
        self.assertEqual(pr_prefixed["output_per_million"], 0.50)

        pr_openai = cost.find_pricing("openai/GPT-4o", pricing_map)
        self.assertIsNotNone(pr_openai)
        self.assertEqual(pr_openai["input_per_million"], 2.50)

    def test_recompute_costs_with_case_and_prefix(self):
        # Insert events with mixed case and provider prefix
        with db.get_conn() as conn:
            conn.execute(
                "INSERT INTO usage_events (agent_type, session_id, turn_id, model, ts, ts_epoch, "
                "input_tokens, fresh_input_tokens, cached_input_tokens, cache_write_input_tokens, "
                "output_tokens, reasoning_output_tokens, input_cost, output_cost, "
                "cache_read_cost, cache_creation_cost, total_cost) "
                "VALUES ('codex', 's1', 't1', 'zai-org/GLM-5.3-Flash', '2026-09-08T00:00:00Z', 1788825600, "
                "1000000, 1000000, 0, 0, 1000000, 0, 0, 0, 0, 0, 0)"
            )
        db.recompute_costs()
        with db.get_conn() as conn:
            row = conn.execute("SELECT input_cost, output_cost, total_cost FROM usage_events WHERE session_id='s1'").fetchone()
            self.assertIsNotNone(row)
            # 1M input @ $0.15 = 0.15, 1M output @ $0.50 = 0.50, total = 0.65
            self.assertAlmostEqual(row["input_cost"], 0.15, places=4)
            self.assertAlmostEqual(row["output_cost"], 0.50, places=4)
            self.assertAlmostEqual(row["total_cost"], 0.65, places=4)

    def test_antigravity_cost_semantics(self):
        pricing_map = db.get_pricing_map()
        # Antigravity: input_tokens is fresh; output_tokens includes thinking
        c = cost.compute_costs("antigravity", "gemini-3.8-flash", inp=1000,
                               cached=500, cache_w=0, out=200, pricing_map=pricing_map,
                               reasoning=150)
        self.assertEqual(c["fresh_input"], 1000)
        # 1000 * $1.5/1M = $0.0015; 200 * $7.5/1M = $0.0015; 500 * $0.15/1M = $0.000075
        expected_total = 0.0015 + 0.0015 + 0.000075
        self.assertAlmostEqual(c["total_cost"], expected_total, places=6)

    def test_parse_antigravity_db(self):
        # Create a mock Antigravity sqlite database in tempdir
        import sqlite3
        td = tempfile.mkdtemp()
        db_path = os.path.join(td, "mock_ag.db")
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE trajectory_meta (trajectory_id text, cascade_id text, trajectory_type int, source int)")
        conn.execute("CREATE TABLE trajectory_metadata_blob (id text PRIMARY KEY, data blob)")
        conn.execute("CREATE TABLE gen_metadata (idx int PRIMARY KEY, data blob, size int)")
        conn.execute("CREATE TABLE steps (idx int PRIMARY KEY, step_type int, status int, metadata blob)")

        # trajectory_meta
        conn.execute("INSERT INTO trajectory_meta VALUES ('traj-1', 'cascade-mock-123', 4, 1)")

        def encode_varint(v):
            b = bytearray()
            while True:
                part = v & 0x7f
                v >>= 7
                if v: b.append(part | 0x80)
                else: b.append(part); break
            return bytes(b)

        def encode_tag(f, w): return encode_varint((f << 3) | w)
        def encode_bytes(f, d): return encode_tag(f, 2) + encode_varint(len(d)) + d
        def encode_int(f, v): return encode_tag(f, 0) + encode_varint(v)

        # Mock trajectory_metadata_blob: field 7 = "file:///C:/mock/work"
        blob_data = encode_bytes(7, b"file:///C:/mock/work")
        conn.execute("INSERT INTO trajectory_metadata_blob VALUES ('main', ?)", (blob_data,))

        # Mock gen_metadata:
        # msg4 (usage): field 7 = mid "mid-step-1"
        # m1: field 19 = "gemini-3.8-flash", field 4 = msg4
        # data: field 1 = m1
        msg4 = encode_bytes(7, b"mid-step-1")
        m1 = encode_bytes(19, b"gemini-3.8-flash") + encode_bytes(4, msg4)
        gen_data = encode_bytes(1, m1)
        conn.execute("INSERT INTO gen_metadata VALUES (0, ?, ?)", (gen_data, len(gen_data)))

        # Mock steps: idx=1, step_type=15
        # ts_field (field 1): field 1 = 1788629699
        # usage (field 9): field 2=1000, field 3=200, field 5=500, field 7="mid-step-1", field 9=150
        ts_msg = encode_int(1, 1788629699)
        usage_msg = (encode_int(2, 1000) + encode_int(3, 200) +
                     encode_int(5, 500) + encode_bytes(7, b"mid-step-1") +
                     encode_int(9, 150))
        step_meta = encode_bytes(1, ts_msg) + encode_bytes(9, usage_msg)
        conn.execute("INSERT INTO steps VALUES (1, 15, 3, ?)", (step_meta,))
        conn.commit()
        conn.close()

        pricing_map = db.get_pricing_map()
        import adapters.antigravity as antigravity_adapter
        events, next_idx = antigravity_adapter.parse_file(
            db_path, pricing_map, cost.compute_costs)
        self.assertEqual(len(events), 1)
        ev = events[0]
        self.assertEqual(ev[0], "antigravity")
        self.assertEqual(ev[1], "cascade-mock-123")
        self.assertEqual(ev[2], "mid-step-1")
        self.assertEqual(ev[3], "gemini-3.8-flash")
        self.assertEqual(ev[6], 1000)  # input_tokens
        self.assertEqual(ev[7], 1000)  # fresh_input_tokens
        self.assertEqual(ev[8], 500)   # cached_input_tokens
        self.assertEqual(ev[10], 200)  # output_tokens
        self.assertEqual(ev[11], 150)  # reasoning_output_tokens
        self.assertEqual(ev[17], "C:\\mock\\work")
        self.assertEqual(next_idx, 2)

    def test_antigravity_scan_incremental_and_stats(self):
        td = tempfile.mkdtemp()
        ag_dir = Path(td) / "ag_conv"
        ag_dir.mkdir()
        orig_ag = parser.ANTIGRAVITY_CONVERSATIONS_DIR
        orig_claude = parser.CLAUDE_PROJECTS_DIR
        orig_codex = parser.SESSIONS_DIR
        orig_arch = parser.ARCHIVED_DIR
        orig_zcode = parser.ZCODE_DB
        parser.ANTIGRAVITY_CONVERSATIONS_DIR = ag_dir
        parser.CLAUDE_PROJECTS_DIR = Path(td) / "claude_empty"
        parser.SESSIONS_DIR = Path(td) / "codex_empty"
        parser.ARCHIVED_DIR = None
        parser.ZCODE_DB = None
        parser.PI_SESSIONS_DIR = None

        try:
            import sqlite3
            db_path = ag_dir / "sess_ag.db"
            conn = sqlite3.connect(str(db_path))
            conn.execute("CREATE TABLE trajectory_meta (trajectory_id text, cascade_id text, trajectory_type int, source int)")
            conn.execute("CREATE TABLE trajectory_metadata_blob (id text PRIMARY KEY, data blob)")
            conn.execute("CREATE TABLE gen_metadata (idx int PRIMARY KEY, data blob, size int)")
            conn.execute("CREATE TABLE steps (idx int PRIMARY KEY, step_type int, status int, metadata blob)")
            conn.execute("INSERT INTO trajectory_meta VALUES ('traj-1', 'cascade-ag-999', 4, 1)")

            def encode_varint(v):
                b = bytearray()
                while True:
                    part = v & 0x7f
                    v >>= 7
                    if v: b.append(part | 0x80)
                    else: b.append(part); break
                return bytes(b)

            def encode_tag(f, w): return encode_varint((f << 3) | w)
            def encode_bytes(f, d): return encode_tag(f, 2) + encode_varint(len(d)) + d
            def encode_int(f, v): return encode_tag(f, 0) + encode_varint(v)

            # Step 1
            msg4_1 = encode_bytes(7, b"mid-1")
            m1_1 = encode_bytes(19, b"gemini-3.8-flash") + encode_bytes(4, msg4_1)
            gen1 = encode_bytes(1, m1_1)
            conn.execute("INSERT INTO gen_metadata VALUES (0, ?, ?)", (gen1, len(gen1)))

            step1_meta = (encode_bytes(1, encode_int(1, 1788629699)) +
                          encode_bytes(9, encode_int(2, 500) + encode_int(3, 100) +
                                          encode_bytes(7, b"mid-1")))
            conn.execute("INSERT INTO steps VALUES (1, 15, 3, ?)", (step1_meta,))
            conn.commit()

            # First incremental scan
            r1 = parser.scan_incremental()
            self.assertEqual(r1["new_events"], 1)

            # Second scan without changes: 0 new events
            r2 = parser.scan_incremental()
            self.assertEqual(r2["new_events"], 0)

            # Append Step 2
            msg4_2 = encode_bytes(7, b"mid-2")
            m1_2 = encode_bytes(19, b"gemini-3.8-flash") + encode_bytes(4, msg4_2)
            gen2 = encode_bytes(1, m1_2)
            conn.execute("INSERT INTO gen_metadata VALUES (1, ?, ?)", (gen2, len(gen2)))

            step2_meta = (encode_bytes(1, encode_int(1, 1788629799)) +
                          encode_bytes(9, encode_int(2, 600) + encode_int(3, 150) +
                                          encode_bytes(7, b"mid-2")))
            conn.execute("INSERT INTO steps VALUES (3, 15, 3, ?)", (step2_meta,))
            conn.commit()
            conn.close()

            # Third scan with appended step
            r3 = parser.scan_incremental()
            self.assertEqual(r3["new_events"], 1)

            # Check stats
            agents = stats.get_agents(1788629000, 1788630000)
            ag_agents = [a for a in agents if a["agent_type"] == "antigravity"]
            self.assertEqual(len(ag_agents), 1)
            self.assertEqual(ag_agents[0]["display_name"], "Antigravity")
            self.assertEqual(ag_agents[0]["tokens"], (500 + 100) + (600 + 150))

            models = stats.get_models(1788629000, 1788630000, agent="antigravity")
            self.assertEqual(len(models), 1)
            self.assertEqual(models[0]["model"], "gemini-3.8-flash")

            sessions = stats.get_sessions(1788629000, 1788630000, agent="antigravity")
            self.assertEqual(len(sessions), 1)
            self.assertEqual(sessions[0]["session_id"], "cascade-ag-999")
        finally:
            parser.ANTIGRAVITY_CONVERSATIONS_DIR = orig_ag
            parser.CLAUDE_PROJECTS_DIR = orig_claude
            parser.SESSIONS_DIR = orig_codex
            parser.ARCHIVED_DIR = orig_arch
            parser.ZCODE_DB = orig_zcode

    def test_resolve_range_all(self):
        s, e = stats.resolve_range("all", now=1700000000)
        self.assertEqual(s, 0)
        self.assertEqual(e, 1700000000)
        s_1d, e_1d = stats.resolve_range("1d", now=1700000000)
        self.assertEqual(s_1d, 1700000000 - 86400)


if __name__ == "__main__":
    unittest.main()


