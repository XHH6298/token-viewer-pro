"""Token 消耗量查看器 - 玻璃小组件版。"""
import os, sys, time, socket, threading, datetime
os.environ["WEBVIEW2_DEFAULT_BACKGROUND_COLOR"] = "0"

# 启用 Windows Per-Monitor V2 原生高 DPI 清晰渲染，避免任何位图缩放模糊
try:
    import ctypes
    ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
except Exception:
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

import webbrowser
import urllib.request
from contextlib import asynccontextmanager

LOG = os.path.join(os.path.expanduser("~"), ".codex", "token_viewer.log")
def log(msg):
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(datetime.datetime.now().isoformat() + " " + str(msg) + "\n")
    except Exception:
        pass

log("=== app start ===")

try:
    from fastapi import FastAPI, Body
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse, Response, JSONResponse
    from pydantic import BaseModel
    import uvicorn
    import webview
    log("imports ok")
except Exception as e:
    log("IMPORT FAIL: " + repr(e))
    raise

import db, parser, stats, config

if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
DEFAULT_PORT = 18377
UI_REVISION = "20261002-light-entrance"


def _background_log_scanner():
    """实时后台增量扫描线程：持续轻量轮询会话日志，秒级同步最新 Token 事件"""
    while True:
        try:
            parser.scan_incremental()
        except Exception as e:
            log("scan_incremental background error: " + repr(e))
        time.sleep(1.5)


@asynccontextmanager
async def lifespan(app):
    global _subscription_url, _theme, _language
    db.init_db()
    _subscription_url = db.get_setting("subscription_url", config.SUBSCRIPTION_URL)
    _theme = db.get_setting("theme", "auto")
    _language = db.get_setting("language", "zh")
    # 后台持续轻量增量扫描线程（延迟仅 16ms）
    threading.Thread(target=_background_log_scanner, daemon=True).start()
    yield

app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def host_guard(request, call_next):
    """仅接受本机回环 Host，阻止浏览器 DNS rebinding 类攻击读取/触发本地 API。

    服务本身绑定 127.0.0.1，但任意网页可通过 DNS rebinding 访问；
    校验 Host 头为 127.0.0.1 / localhost / ::1 后直接 403。"""
    raw = request.headers.get("host") or ""
    if raw.startswith("["):
        host = raw.split("]")[0].strip("[]")
    else:
        host = raw.rsplit(":", 1)[0] if ":" in raw else raw
    if host.lower() not in ("127.0.0.1", "localhost", "::1"):
        return JSONResponse({"error": "forbidden"}, status_code=403)
    return await call_next(request)



@app.get("/api/status")
def api_status():
    return {"is_alive": True, "time": time.time()}


@app.get("/api/dashboard")
def api_dashboard(range: str = "today", agent: str = None):
    # Normalize range keys: "today" is today from 00:00, "1d" is rolling 24 hours
    range_map = {"today": "today", "1d": "1d", "7d": "7d", "30d": "30d", "all": "all"}
    r = range_map.get(range, range)
    start, end = stats.resolve_range(r)
    if agent == "":
        agent = None

    summary = stats.get_summary(start, end, agent)
    bucket = "hour" if (end - start) <= 2 * 86400 else "day"
    trend = stats.get_trend(start, end, agent, bucket)
    models = stats.get_models(start, end, agent)
    agents_list = stats.get_agents(start, end)

    # Clean models list with proper display labels
    models_breakdown = []
    for m in models:
        models_breakdown.append({
            "name": m.get("model", ""),
            "label": m.get("display_name") or m.get("model", ""),
            "tokens": m.get("tokens", 0),
            "cost": m.get("cost", 0.0),
            "request_count": m.get("request_count", 0),
            "cache_hit_rate": m.get("cache_hit_rate", 0.0)
        })
    models_breakdown.sort(key=lambda x: x["tokens"], reverse=True)

    # Clean projects list
    projects_breakdown = []
    for a in agents_list:
        projects_breakdown.append({
            "name": a.get("agent_type", ""),
            "label": a.get("display_name") or a.get("agent_type", ""),
            "tokens": a.get("tokens", 0),
            "cost": a.get("cost", 0.0),
            "request_count": a.get("request_count", 0),
            "cache_hit_rate": a.get("cache_hit_rate", 0.0)
        })
    projects_breakdown.sort(key=lambda x: x["tokens"], reverse=True)

    # Clean timeline points
    timeline = []
    for pt in trend:
        # bucket key like "2026-09-06 14" -> "14:00" or "09-06"
        b_str = pt.get("bucket", "")
        if " " in b_str:
            time_label = b_str.split(" ")[1] + ":00"
        else:
            time_label = b_str[-5:] if len(b_str) >= 5 else b_str
        timeline.append({
            "time": time_label,
            "tokens": pt.get("tokens", 0),
            "cost": pt.get("cost", 0.0),
            "count": pt.get("count", 0)
        })

    return {
        "total_tokens": summary.get("total_tokens", 0),
        "total_cost": summary.get("total_cost", 0.0),
        "input_fresh": summary.get("input_tokens", 0),
        "cache_read": summary.get("cache_read_tokens", 0),
        "output": summary.get("output_tokens", 0),
        "cache_hit_rate": summary.get("cache_hit_rate", 0.0),
        "timeline": timeline,
        "models_breakdown": models_breakdown,
        "projects_breakdown": projects_breakdown,
        "active_projects_count": len(projects_breakdown) if projects_breakdown else 1
    }


@app.post("/api/window/close")
def api_window_close():
    threading.Thread(target=_exit_now, daemon=True).start()
    return {"ok": True}


@app.post("/api/window/minimize")
def api_window_minimize():
    if _hwnd:
        import ctypes
        from ctypes import wintypes
        user32 = ctypes.windll.user32
        user32.ShowWindow(_hwnd, 6) # SW_MINIMIZE
    return {"ok": True}


@app.post("/api/window/maximize")
def api_window_maximize():
    api = JsApi()
    res = api.toggle_fullscreen_or_maximize()
    return {"maximized": bool(res), "fullscreen": bool(res)}


@app.post("/api/window/fullscreen")
def api_window_fullscreen():
    api = JsApi()
    res = api.toggle_fullscreen_or_maximize()
    return {"fullscreen": bool(res), "maximized": bool(res)}


class CapsuleRequest(BaseModel):
    is_capsule: bool = True


@app.post("/api/window/capsule")
def api_window_capsule(data: CapsuleRequest = None):
    api = JsApi()
    is_cap = data.is_capsule if data else True
    res = api.set_capsule_mode(is_cap)
    return {"ok": bool(res), "is_capsule": is_cap}


@app.get("/api/window/state")
def api_window_state():
    api = JsApi()
    return {
        "maximized": api.is_maximized(),
        "fullscreen": api.is_fullscreen()
    }


@app.get("/api/summary")
def api_summary(range: str = "today", agent: str = None):
    start, end = stats.resolve_range(range)
    return stats.get_summary(start, end, agent)


@app.get("/api/agents")
def api_agents(range: str = "today"):
    start, end = stats.resolve_range(range)
    return stats.get_agents(start, end)


@app.get("/api/trend")
def api_trend(range: str = "today", agent: str = None, bucket: str = None):
    start, end = stats.resolve_range(range)
    if not bucket:
        bucket = "hour" if (end - start) <= 2 * 86400 else "day"
    return stats.get_trend(start, end, agent, bucket)


@app.get("/api/models")
def api_models(range: str = "today", agent: str = None):
    start, end = stats.resolve_range(range)
    return stats.get_models(start, end, agent)


@app.get("/api/sessions")
def api_sessions(range: str = "today", agent: str = None):
    start, end = stats.resolve_range(range)
    return stats.get_sessions(start, end, agent)


@app.get("/api/pricing")
def api_pricing():
    return db.get_pricing()


class PricingUpdate(BaseModel):
    model: str
    display_name: str
    input_per_million: float
    output_per_million: float
    cache_read_per_million: float
    cache_creation_per_million: float
    multiplier: float = 1.0


@app.put("/api/pricing")
def api_pricing_update(data: PricingUpdate):
    db.upsert_pricing(data.model, data.display_name, data.input_per_million,
                      data.output_per_million, data.cache_read_per_million,
                      data.cache_creation_per_million, data.multiplier)
    db.recompute_costs()
    return {"ok": True}


class PricingBatchUpdate(BaseModel):
    items: list[PricingUpdate]


@app.put("/api/pricing/batch")
def api_pricing_batch(data: PricingBatchUpdate):
    """批量保存定价：单事务 upsert 全部条目后仅重算一次历史成本。

    前端"保存并重算"逐行调用单条接口时每行都触发一次全表重算，
    N 个模型即 N 次全量 UPDATE；批量接口将成本降为 1 次。"""
    for item in data.items:
        db.upsert_pricing(item.model, item.display_name, item.input_per_million,
                          item.output_per_million, item.cache_read_per_million,
                          item.cache_creation_per_million, item.multiplier)
    db.recompute_costs()
    return {"ok": True, "count": len(data.items)}


@app.delete("/api/pricing/{model}")
def api_pricing_delete(model: str):
    db.delete_pricing(model)
    db.recompute_costs()
    return {"ok": True}


@app.get("/api/live_status")
def api_live_status():
    """为桌面灵动胶囊与呼吸灯提供即时流速与今日消费数据"""
    now = time.time()
    dt = datetime.datetime.fromtimestamp(now)
    today_epoch = int(datetime.datetime(dt.year, dt.month, dt.day).timestamp())
    speed = 0
    today_cost = 0.0
    today_tokens = 0
    active_model = ""
    is_active = False

    try:
        with db.get_conn() as conn:
            # 今日累计消费与 Token 总消耗
            r_today = conn.execute(
                "SELECT COALESCE(SUM(total_cost), 0) as c, "
                "COALESCE(SUM(fresh_input_tokens + output_tokens + reasoning_output_tokens + cached_input_tokens), 0) as t "
                "FROM usage_events WHERE ts_epoch >= ?",
                (today_epoch,)).fetchone()
            today_cost = round(float(r_today["c"]), 2)
            today_tokens = int(r_today["t"])

            # 最近 10 秒内是否有调用（以 10 秒滑动窗口平滑计算每秒 Token 消耗量）
            r_recent = conn.execute(
                "SELECT model, ts_epoch, (fresh_input_tokens + output_tokens + reasoning_output_tokens + cached_input_tokens) as tokens "
                "FROM usage_events WHERE ts_epoch >= ? ORDER BY ts_epoch DESC LIMIT 20",
                (int(now - 10),)).fetchall()
            if r_recent:
                is_active = True
                active_model = r_recent[0]["model"] or ""
                recent_tokens = sum(r["tokens"] or 0 for r in r_recent)
                speed = max(1, int(recent_tokens / 10.0))
            else:
                r_last = conn.execute(
                    "SELECT model FROM usage_events ORDER BY ts_epoch DESC LIMIT 1"
                ).fetchone()
                if r_last and r_last["model"]:
                    active_model = r_last["model"]
    except Exception as e:
        log("api_live_status error: " + repr(e))

    status = "idle"
    if speed >= 8000:
        status = "burst"
    elif is_active or speed > 0:
        status = "active"

    return {
        "status": status,
        "speed_tokens_per_sec": speed,
        "today_cost": today_cost,
        "today_tokens": today_tokens,
        "active_model": active_model,
        "is_active": is_active
    }


class CapsuleModeRequest(BaseModel):
    is_capsule: bool


class SettingsUpdate(BaseModel):
    subscription_url: str = None
    theme: str = None
    language: str = None
    avatar: str = None
    window_width: int = None
    window_height: int = None


_THEMES = ("auto", "light", "dark")


def _valid_url(url):
    """仅接受 http/https 链接，避免注入任意协议/命令。"""
    url = (url or "").strip()
    return url.lower().startswith(("http://", "https://"))


@app.get("/api/settings")
def api_settings():
    avatar_val = db.get_setting("user_avatar", "")
    return {
        "subscription_url": _subscription_url,
        "theme": _theme,
        "language": _language,
        "avatar": avatar_val
    }


@app.put("/api/settings")
def api_settings_update(data: SettingsUpdate):
    global _subscription_url, _theme, _language
    if data.language is not None and data.language not in SUPPORTED_LANGUAGES:
        return JSONResponse({"error": "invalid language"}, status_code=400)
    if data.subscription_url is not None:
        url = (data.subscription_url or "").strip()
        if not _valid_url(url):
            return JSONResponse({"error": "invalid url"}, status_code=400)
        _subscription_url = url
        db.set_setting("subscription_url", url)
    if data.language is not None:
        if data.language in SUPPORTED_LANGUAGES:
            _language = data.language
            db.set_setting("language", _language)
    if data.theme is not None:
        if data.theme not in _THEMES:
            return JSONResponse({"error": "invalid theme"}, status_code=400)
        _theme = data.theme
        db.set_setting("theme", _theme)
        if _theme == "light":
            update_dwm_theme(False)
        elif _theme == "dark":
            update_dwm_theme(True)
        else:
            sys_t = api_system_theme().get("theme", "dark")
            update_dwm_theme(sys_t == "dark")
    if data.avatar is not None:
        db.set_setting("user_avatar", data.avatar)
    if data.window_width is not None and data.window_height is not None:
        if 400 <= data.window_width <= 4000 and 520 <= data.window_height <= 4000:
            db.set_setting("window_width", str(int(data.window_width)))
            db.set_setting("window_height", str(int(data.window_height)))
    return {
        "ok": True,
        "subscription_url": _subscription_url,
        "theme": _theme,
        "avatar": db.get_setting("user_avatar", "")
    }


@app.post("/api/refresh")
def api_refresh():
    return parser.scan_incremental()


def _is_maximized():
    """窗口是否处于最大化（供前端判断与保存窗口尺寸）。"""
    try:
        if window:
            native = getattr(window, "native", None)
            if native:
                import clr
                clr.AddReference("System.Windows.Forms")
                import System.Windows.Forms as WinForms
                return bool(native.WindowState == WinForms.FormWindowState.Maximized)
    except Exception:
        pass
    if _hwnd:
        try:
            import ctypes
            return bool(ctypes.windll.user32.IsZoomed(_hwnd))
        except Exception:
            pass
    return False


def _is_fullscreen():
    """窗口是否处于真全屏模式。"""
    if window:
        return bool(getattr(window, "fullscreen", False))
    return False


@app.get("/api/system_theme")
def api_system_theme():
    """读取 Windows 系统深浅色偏好（注册表）。

    WebView2 的 prefers-color-scheme 未必跟随系统主题，auto 模式改用此值，
    保证自动模式真实匹配系统白天/黑夜。"""
    try:
        import winreg
        k = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                           r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
        val, _ = winreg.QueryValueEx(k, "AppsUseLightTheme")
        winreg.CloseKey(k)
        return {"theme": "light" if val == 1 else "dark"}
    except Exception:
        return {"theme": "light"}


@app.post("/api/settings_beacon")
def api_settings_beacon(payload: dict = Body(...)):
    """关闭/卸载前的尺寸兜底保存（sendBeacon 走 POST，无法带自定义 header）。"""
    try:
        w = int(payload.get("window_width") or 0)
        h = int(payload.get("window_height") or 0)
        if 480 <= w <= 4000 and 640 <= h <= 4000:
            db.set_setting("window_width", str(w))
            db.set_setting("window_height", str(h))
    except Exception:
        pass
    return {"ok": True}


@app.get("/api/health")
def api_health():
    return stats.get_health()


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/favicon.ico")
def favicon():
    return Response(status_code=204)


@app.get("/")
def index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"),
                        headers={"Cache-Control": "no-store"})


def find_free_port(start=DEFAULT_PORT, count=30):
    """预绑定一个空闲端口并返回仍被本进程持有的 socket。

    先关闭探测 socket 再交给 uvicorn 存在端口竞态；这里直接把已绑定 socket
    传给 uvicorn，端口从选择到监听期间不会被其他进程抢占。
    """
    for port in range(start, start + count):
        s = socket.socket()
        try:
            s.bind(("127.0.0.1", port))
            s.listen(128)
            return s
        except OSError:
            s.close()
            continue
    return None


def _wait_port(port, timeout=10):
    """Wait for an HTTP response, not merely a TCP accept.

    The server socket is pre-listened before uvicorn owns it, so a TCP connect
    would succeed even if uvicorn never starts.
    探测 "/" 而非 "/api/health"：后者每次触发 usage_events/file_index 两张表
    的全表 COUNT(*)，启动期 0.25s 一次的重试会白白消耗 DB IO。
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(
                    "http://127.0.0.1:%d/" % port, timeout=0.5):
                return True
        except Exception:
            time.sleep(0.25)
    return False


_hwnd = 0
_drag = None  # 拖拽起点状态（物理像素坐标）
_subscription_url = config.SUBSCRIPTION_URL  # 订阅套餐链接（可在设置面板修改，持久化）
_theme = "auto"
_language = "zh"  # 外观：auto(跟随系统)/light/dark，持久化到 DB
_is_capsule = False  # 是否处于桌面灵动胶囊模式
SUPPORTED_LANGUAGES = ("zh", "zh-TW", "en", "ja", "ko", "fr", "de", "es", "pt", "ru", "it")
_backdrop_refresh_pending = False
_backdrop_surface_hwnd = 0
_backdrop_surface_timer = None
_frame_procs = {}
_frame_proc_refs = []


def _topmost_watchdog():
    """灵动胶囊置顶守护线程：周期性保证胶囊在任何全屏软件或置顶窗口下稳固浮于最前，且绝不抢夺用户输入焦点。"""
    while True:
        try:
            if _hwnd and _is_capsule and not _drag and sys.platform == "win32":
                import ctypes
                # HWND_TOPMOST = -1, SWP_NOMOVE = 0x0002, SWP_NOSIZE = 0x0001, SWP_NOACTIVATE = 0x0010
                ctypes.windll.user32.SetWindowPos(_hwnd, -1, 0, 0, 0, 0, 0x0002 | 0x0001 | 0x0010)
        except Exception:
            pass
        time.sleep(0.25)


def update_dwm_theme(is_dark: bool):
    """根据主题切换 DWM 深浅色模式 (DWMWA_USE_IMMERSIVE_DARK_MODE = 20)。"""
    if not _hwnd:
        return
    try:
        import ctypes
        dwmapi = ctypes.windll.dwmapi
        dark_val = ctypes.c_int(1 if is_dark else 0)
        dwmapi.DwmSetWindowAttribute(_hwnd, 20, ctypes.byref(dark_val), ctypes.sizeof(dark_val))
        log("update_dwm_theme: is_dark=" + str(is_dark))
    except Exception as e:
        log("update_dwm_theme FAIL: " + repr(e))


def _queue_backdrop_refresh(*_args):
    """Coalesce native events and apply after WinForms finishes its state change."""
    global _backdrop_refresh_pending
    native = getattr(window, "native", None) if window else None
    if native is None or native.IsDisposed or not native.IsHandleCreated:
        return
    if _backdrop_refresh_pending:
        return
    _backdrop_refresh_pending = True
    from System import Action

    def refresh():
        global _backdrop_refresh_pending
        _backdrop_refresh_pending = False
        _apply_backdrop()

    try:
        native.BeginInvoke(Action(refresh))
    except Exception as e:
        _backdrop_refresh_pending = False
        log("backdrop queue FAIL: " + repr(e))


def _setup_window():
    """Run on before_show, once WinForms and WebView2 controls exist."""
    if sys.platform != "win32":
        return
    native = getattr(window, "native", None)
    if native is None:
        return
    # These events also cover HWND recreation and restore after fullscreen.
    native.HandleCreated += _queue_backdrop_refresh
    native.Activated += _queue_backdrop_refresh
    native.Resize += _queue_backdrop_refresh
    native.Shown += _queue_backdrop_refresh
    native.MaximizeBox = True
    native.MinimizeBox = True
    _apply_backdrop()
    threading.Thread(target=_topmost_watchdog, daemon=True).start()
    log("setup: native lifecycle effects installed")


def _prime_backdrop_surface():
    """Rebuild the initial WinForms composition surface with a one-pixel resize.

    Reapplying DWM attributes alone does not fix its initial opaque surface.
    Keep the original size and restore it on the next UI tick, without changing
    fullscreen state, focus, position, or the user's saved window dimensions.
    """
    global _backdrop_surface_hwnd, _backdrop_surface_timer
    native = getattr(window, "native", None) if window else None
    if native is None or native.IsDisposed or not native.IsHandleCreated:
        return
    if native.InvokeRequired:
        from System import Action
        native.Invoke(Action(_prime_backdrop_surface))
        return
    hwnd = int(native.Handle.ToInt64())
    if _backdrop_surface_hwnd == hwnd or _is_capsule or native.is_fullscreen:
        return
    from System.Drawing import Size
    from System.Windows.Forms import Timer
    _backdrop_surface_hwnd = hwnd
    size = native.Size
    timer = Timer()
    timer.Interval = 32

    def restore_size(*_args):
        global _backdrop_surface_timer
        timer.Stop()
        timer.Dispose()
        _backdrop_surface_timer = None
        if native.IsDisposed or _is_capsule or native.is_fullscreen:
            return
        # Do not overwrite a concurrent user resize.
        if native.Width == size.Width + 1 and native.Height == size.Height:
            native.Size = size
        _apply_backdrop()
        log("backdrop: initial composition surface rebuilt")

    timer.Tick += restore_size
    _backdrop_surface_timer = timer
    native.Size = Size(size.Width + 1, size.Height)
    timer.Start()


def _configure_window_frame(native):
    """Keep a resizable DWM frame while drawing all non-client space ourselves.

    WS_THICKFRAME lets DWM actually round a restored frameless window. Handling
    WM_NCCALCSIZE keeps that frame from adding a visible system border/title bar.
    """
    import ctypes
    from ctypes import wintypes
    user32 = ctypes.windll.user32
    hwnd = int(native.Handle.ToInt64())
    user32.GetWindowLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int]
    user32.GetWindowLongPtrW.restype = ctypes.c_ssize_t
    user32.SetWindowLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_ssize_t]
    user32.SetWindowLongPtrW.restype = ctypes.c_ssize_t
    user32.CallWindowProcW.argtypes = [ctypes.c_ssize_t, wintypes.HWND,
        wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
    user32.CallWindowProcW.restype = ctypes.c_ssize_t
    user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
    user32.GetDpiForWindow.argtypes = [wintypes.HWND]
    user32.IsZoomed.argtypes = [wintypes.HWND]
    user32.IsIconic.argtypes = [wintypes.HWND]
    if hwnd not in _frame_procs:
        original_proc = user32.GetWindowLongPtrW(hwnd, -4)
        WNDPROC = ctypes.WINFUNCTYPE(ctypes.c_ssize_t, wintypes.HWND,
            wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)

        def wndproc(h, message, wparam, lparam):
            try:
                if message == 0x0083:  # WM_NCCALCSIZE, both RECT forms
                    return 0
                if message == 0x0086 and not _is_capsule and not user32.IsIconic(h):
                    # Keep DWM's visual material active, without changing actual
                    # activation/focus (WM_ACTIVATE / WM_SETFOCUS are untouched).
                    user32.CallWindowProcW(original_proc, h, message, 1, lparam)
                    return 1  # Always permit the real window to deactivate.
                if message == 0x0084:  # WM_NCHITTEST
                    if _is_capsule or native.is_fullscreen or user32.IsZoomed(h):
                        return 1  # HTCLIENT
                    rect = wintypes.RECT()
                    user32.GetWindowRect(h, ctypes.byref(rect))
                    x = ctypes.c_short(lparam & 0xFFFF).value
                    y = ctypes.c_short((lparam >> 16) & 0xFFFF).value
                    edge = max(4, round(6 * user32.GetDpiForWindow(h) / 96))
                    left, right = x < rect.left + edge, x >= rect.right - edge
                    top, bottom = y < rect.top + edge, y >= rect.bottom - edge
                    if top:
                        return 13 if left else 14 if right else 12
                    if bottom:
                        return 16 if left else 17 if right else 15
                    if left or right:
                        return 10 if left else 11
                if message == 0x0082:  # WM_NCDESTROY: handle may be reused.
                    _frame_procs.pop(int(h), None)
            except Exception as e:
                log("custom frame FAIL: " + repr(e))
            return user32.CallWindowProcW(original_proc, h, message, wparam, lparam)

        callback = WNDPROC(wndproc)
        _frame_proc_refs.append(callback)  # Keep callbacks alive through WM_NCDESTROY.
        user32.SetWindowLongPtrW(hwnd, -4, ctypes.cast(callback, ctypes.c_void_p).value)
        _frame_procs[hwnd] = original_proc

    style = user32.GetWindowLongPtrW(hwnd, -16)
    new_style = style & ~0x00040000 if native.is_fullscreen else style | 0x00040000
    if new_style != style:
        user32.SetWindowLongPtrW(hwnd, -16, new_style)
        user32.SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND,
            ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, wintypes.UINT]
        user32.SetWindowPos(hwnd, None, 0, 0, 0, 0,
                            0x0001 | 0x0002 | 0x0004 | 0x0010 | 0x0020)


def _apply_backdrop(target_hwnd=None):
    """Apply backdrop to the current HWND on its owning UI thread."""
    global _hwnd, _backdrop_surface_hwnd
    if sys.platform != "win32":
        return False
    native = getattr(window, "native", None) if window else None
    if native is None or native.IsDisposed or not native.IsHandleCreated:
        return False
    try:
        if native.InvokeRequired:
            from System import Func, Boolean
            return bool(native.Invoke(Func[Boolean](lambda: _apply_backdrop())))

        import ctypes
        from ctypes import wintypes
        from System.Drawing import Color
        # Never reuse a handle cached while BrowserForm was still constructing.
        _hwnd = int(native.Handle.ToInt64())
        if _is_capsule:
            return True  # Preserve the capsule's region and disabled DWM backdrop.
        user32 = ctypes.windll.user32
        user32.IsIconic.argtypes = [wintypes.HWND]
        if user32.IsIconic(_hwnd):
            # The minimized WebView2 surface is discarded. Rebuild it on restore,
            # not while the hidden/minimized window is being laid out.
            _backdrop_surface_hwnd = 0
            return True

        _configure_window_frame(native)
        native.BackColor = Color.Black
        native.webview.DefaultBackgroundColor = Color.Transparent
        # CSS owns the three zoom levels; disable WebView2's independent zoom.
        if native.webview.CoreWebView2 is not None:
            native.webview.CoreWebView2.Settings.IsZoomControlEnabled = False
            native.webview.ZoomFactor = 1.0
        dwmapi = ctypes.windll.dwmapi
        dwmapi.DwmSetWindowAttribute.argtypes = [
            wintypes.HWND, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD]
        dwmapi.DwmSetWindowAttribute.restype = ctypes.c_long
        dwmapi.DwmExtendFrameIntoClientArea.argtypes = [wintypes.HWND, ctypes.c_void_p]
        dwmapi.DwmExtendFrameIntoClientArea.restype = ctypes.c_long

        class MARGINS(ctypes.Structure):
            _fields_ = [(name, ctypes.c_int) for name in
                       ("left", "right", "top", "bottom")]

        margins = MARGINS(-1, -1, -1, -1)
        hr_extend = dwmapi.DwmExtendFrameIntoClientArea(_hwnd, ctypes.byref(margins))
        try:
            backdrop = int(os.environ.get("TOKEN_VIEWER_BACKDROP", "3"))
        except ValueError:
            backdrop = 3
        if backdrop not in (2, 3, 4):
            backdrop = 3
        attributes = {
            20: 0 if _theme == "light" else 1,
            38: backdrop,
            33: 1 if native.is_fullscreen else 2,
            34: 0xFFFFFFFE if native.is_fullscreen else 0xFFFFFFFF,
        }
        results = {}
        for attribute, value in attributes.items():
            val = wintypes.DWORD(value)
            results[attribute] = dwmapi.DwmSetWindowAttribute(
                _hwnd, attribute, ctypes.byref(val), ctypes.sizeof(val))
        log(f"backdrop applied: hwnd={_hwnd}, extend={hr_extend}, attrs={results}, fullscreen={native.is_fullscreen}")
        if window.events.loaded.is_set():
            _prime_backdrop_surface()
        return hr_extend == 0 and all(hr == 0 for hr in results.values())
    except Exception as e:
        log("backdrop apply FAIL: " + repr(e))
        return False


def _exit_now():
    """优雅退出：先把 WAL 落盘（checkpoint）再结束进程，避免硬杀丢弃未落盘数据。"""
    log("close: exit now")
    try:
        import db
        with db.get_conn() as conn:
            conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    except Exception as e:
        log("close: checkpoint FAIL " + repr(e))
    import ctypes
    ctypes.windll.kernel32.ExitProcess(0)


class JsApi:
    def exit_app(self):
        _exit_now()

    def refresh_backdrop(self):
        """前端页面 DOM 加载或焦点恢复时补刷 DWM 背景"""
        return _apply_backdrop(_hwnd)

    def _win(self):
        import ctypes
        from ctypes import wintypes
        user32 = ctypes.windll.user32
        # 规范化 HWND 为 64 位句柄传递，避免默认按 32 位 int 截断
        user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
        user32.ShowWindow.restype = wintypes.BOOL
        user32.GetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int]
        user32.GetWindowLongW.restype = ctypes.c_long
        return user32

    def minimize(self):
        if _hwnd:
            self._win().ShowWindow(_hwnd, 6)  # SW_MINIMIZE

    def toggle_fullscreen_or_maximize(self):
        """核心切换：若当前处于全屏或最大化，则平滑还原为普通窗口；否则进入真全屏（完全覆盖隐藏任务栏）"""
        try:
            if window:
                native = getattr(window, "native", None)
                if native:
                    import System.Windows.Forms as WinForms
                    is_full = bool(getattr(native, "is_fullscreen", False))
                    is_max = bool(native.WindowState == WinForms.FormWindowState.Maximized)
                    if is_full:
                        window.toggle_fullscreen()
                        _apply_backdrop()
                        return False
                    elif is_max:
                        native.WindowState = WinForms.FormWindowState.Normal
                        _apply_backdrop()
                        return False
                    else:
                        window.toggle_fullscreen()
                        _apply_backdrop()
                        return True
        except Exception as e:
            log("JsApi toggle_fullscreen_or_maximize FAIL: " + repr(e))
        if _hwnd:
            import ctypes
            user32 = ctypes.windll.user32
            is_max = bool(user32.IsZoomed(_hwnd))
            if is_max:
                user32.ShowWindow(_hwnd, 9)  # SW_RESTORE
                return False
            else:
                user32.ShowWindow(_hwnd, 3)  # SW_MAXIMIZE
                return True
        return False

    def toggle_fullscreen(self):
        """切换真全屏模式 (覆盖任务栏)"""
        return self.toggle_fullscreen_or_maximize()

    def maximize(self):
        """最大化/全屏切换"""
        return self.toggle_fullscreen_or_maximize()

    def restore_window(self):
        """平滑恢复为普通窗口化模式，绝不卡死"""
        try:
            if window:
                native = getattr(window, "native", None)
                if native:
                    import System.Windows.Forms as WinForms
                    if getattr(native, "is_fullscreen", False):
                        window.toggle_fullscreen()
                    elif native.WindowState == WinForms.FormWindowState.Maximized:
                        native.WindowState = WinForms.FormWindowState.Normal
                    _apply_backdrop()
                    return True
        except Exception as e:
            log("JsApi restore_window FAIL: " + repr(e))
        if _hwnd:
            import ctypes
            ctypes.windll.user32.ShowWindow(_hwnd, 9)
            return True
        return False

    def is_maximized(self):
        try:
            if window:
                native = getattr(window, "native", None)
                if native:
                    import System.Windows.Forms as WinForms
                    return bool(native.WindowState == WinForms.FormWindowState.Maximized)
        except Exception:
            pass
        if _hwnd:
            import ctypes
            return bool(ctypes.windll.user32.IsZoomed(_hwnd))
        return False

    def is_fullscreen(self):
        try:
            if window:
                native = getattr(window, "native", None)
                if native:
                    return bool(getattr(native, "is_fullscreen", False))
        except Exception:
            pass
        return False

    def set_capsule_mode(self, is_capsule: bool):
        """切换桌面灵动胶囊模式 (Apple 灵动岛风格) / 完整仪表盘模式"""
        global _is_capsule
        try:
            if sys.platform == "win32" and _hwnd:
                import ctypes
                from ctypes import wintypes
                user32 = ctypes.windll.user32
                HWND_TOPMOST = -1
                HWND_NOTOPMOST = -2
                SWP_SHOWWINDOW = 0x0040

                # 准确获取主显示器工作区 (排除任务栏，支持多显示器)
                rect = wintypes.RECT()
                # SPI_GETWORKAREA = 48
                user32.SystemParametersInfoW(48, 0, ctypes.byref(rect), 0)
                work_w = rect.right - rect.left
                work_h = rect.bottom - rect.top

                # 获取屏幕 DPI 比例
                dpi = 96
                try:
                    dpi = user32.GetDpiForWindow(_hwnd)
                    if not dpi:
                        dpi = 96
                except Exception:
                    dpi = 96
                scale = dpi / 96.0

                if is_capsule:
                    # 若当前处于全屏或最大化，先退出还原，避免尺寸被 WinForms 锁定
                    try:
                        native = getattr(window, "native", None)
                        if native:
                            import System.Windows.Forms as WinForms
                            if getattr(native, "is_fullscreen", False):
                                window.toggle_fullscreen()
                            if native.WindowState == WinForms.FormWindowState.Maximized:
                                native.WindowState = WinForms.FormWindowState.Normal
                    except Exception:
                        pass
                    if user32.IsZoomed(_hwnd):
                        user32.ShowWindow(_hwnd, 9)

                    # 灵动胶囊物理尺寸：严丝合缝 296px x 38px (按 DPI 缩放)
                    capsule_w = int(296 * scale)
                    capsule_h = int(38 * scale)
                    # 居中在屏幕正上方 (Top-Center)，贴近顶部悬浮 8px
                    capsule_x = rect.left + (work_w - capsule_w) // 2
                    capsule_y = rect.top + int(8 * scale)

                    if window:
                        try:
                            window.resize(296, 38)
                        except Exception:
                            pass
                    user32.SetWindowPos(_hwnd, HWND_TOPMOST, capsule_x, capsule_y, capsule_w, capsule_h, SWP_SHOWWINDOW)

                    # 1. 设置 WS_EX_TOPMOST 扩展样式，强化系统级始终置顶
                    try:
                        ex_style = user32.GetWindowLongW(_hwnd, -20)
                        user32.SetWindowLongW(_hwnd, -20, ex_style | 0x00000008)  # WS_EX_TOPMOST
                    except Exception as e:
                        log("set WS_EX_TOPMOST error: " + repr(e))

                    # 2. 精确圆角物理裁剪：彻底清除所有外部矩形白框与背景留白！
                    # GDI CreateRoundRectRgn 的右下坐标为 Exclusive，故使用 capsule_w + 1, capsule_h + 1
                    try:
                        gdi32 = ctypes.windll.gdi32
                        hrgn = gdi32.CreateRoundRectRgn(0, 0, capsule_w + 1, capsule_h + 1, capsule_h, capsule_h)
                        user32.SetWindowRgn(_hwnd, hrgn, True)
                    except Exception as e:
                        log("set SetWindowRgn error: " + repr(e))

                    # 3. 保持 WinForms 窗体底色为纯黑，避免 WinForms 默认灰白底色
                    try:
                        native = getattr(window, "native", None)
                        if native:
                            import clr
                            clr.AddReference("System.Drawing")
                            import System.Drawing
                            native.BackColor = System.Drawing.Color.Black
                    except Exception as e:
                        log("set native BackColor Black error: " + repr(e))

                    # 4. 重置 DWM 边框扩展，由胶囊自身完整呈现
                    try:
                        dwmapi = ctypes.windll.dwmapi
                        class MARGINS(ctypes.Structure):
                            _fields_ = [
                                ("cxLeftWidth", ctypes.c_int),
                                ("cxRightWidth", ctypes.c_int),
                                ("cyTopHeight", ctypes.c_int),
                                ("cyBottomHeight", ctypes.c_int),
                            ]
                        m0 = MARGINS(0, 0, 0, 0)
                        dwmapi.DwmExtendFrameIntoClientArea(_hwnd, ctypes.byref(m0))
                        val_none = ctypes.c_int(1)  # DWMSBT_NONE
                        dwmapi.DwmSetWindowAttribute(_hwnd, 38, ctypes.byref(val_none), ctypes.sizeof(val_none))
                        val_noround = ctypes.c_int(1)  # DWMWCP_DONOTROUND
                        dwmapi.DwmSetWindowAttribute(_hwnd, 33, ctypes.byref(val_noround), ctypes.sizeof(val_noround))
                    except Exception as e:
                        log("dwm capsule attribute error: " + repr(e))

                    _is_capsule = True
                    return True
                else:
                    _is_capsule = False
                    # 恢复主窗口：1160x730，屏幕中央居中，解除始终置顶
                    try:
                        user32.SetWindowRgn(_hwnd, 0, True)
                    except Exception:
                        pass

                    norm_w = int(1160 * scale)
                    norm_h = int(730 * scale)
                    norm_x = rect.left + max(20, (work_w - norm_w) // 2)
                    norm_y = rect.top + max(20, (work_h - norm_h) // 2)

                    if window:
                        try:
                            window.resize(1160, 730)
                        except Exception:
                            pass
                    user32.SetWindowPos(_hwnd, HWND_NOTOPMOST, norm_x, norm_y, norm_w, norm_h, SWP_SHOWWINDOW)

                    try:
                        ex_style = user32.GetWindowLongW(_hwnd, -20)
                        user32.SetWindowLongW(_hwnd, -20, ex_style & ~0x00000008)
                    except Exception:
                        pass

                    _apply_backdrop()

                    return True
        except Exception as e:
            log("set_capsule_mode failed: " + repr(e))
        return False

    def open_subscription(self):
        import webbrowser
        webbrowser.open(_subscription_url)

    def _cursor(self):
        import ctypes
        from ctypes import wintypes
        pt = wintypes.POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
        return pt.x, pt.y

    def _window_rect(self):
        import ctypes
        from ctypes import wintypes
        rect = wintypes.RECT()
        ctypes.windll.user32.GetWindowRect(_hwnd, ctypes.byref(rect))
        return (rect.left, rect.top, rect.right - rect.left, rect.bottom - rect.top)

    def drag_begin(self):
        """记录拖动起点：窗口原点 + 鼠标起点，全部用物理像素。最大化状态下禁止拖动。"""
        global _drag
        if not _hwnd:
            return
        import ctypes
        if ctypes.windll.user32.IsZoomed(_hwnd):
            _drag = None
            return
        x, y = self._cursor()
        rx, ry, rw, rh = self._window_rect()
        _drag = {"mode": "drag", "ox": rx, "oy": ry, "mx": x, "my": y}

    def drag_move(self):
        """鼠标移动：delta = 当前光标(物理) - 起点光标(物理)；窗口 = 起点窗口 + delta。"""
        if not _hwnd or not _drag or _drag.get("mode") != "drag":
            return
        import ctypes
        x, y = self._cursor()
        dx = x - _drag["mx"]
        dy = y - _drag["my"]
        if _is_capsule:
            # 胶囊模式下使用 SWP_NOSIZE | SWP_NOZORDER | SWP_NOACTIVATE (0x0001 | 0x0004 | 0x0010)
            # 绝不重新计算 Z-Order，极速响应并平滑跟随光标移动
            ctypes.windll.user32.SetWindowPos(
                _hwnd, 0, _drag["ox"] + dx, _drag["oy"] + dy, 0, 0, 0x0001 | 0x0004 | 0x0010)
        else:
            ctypes.windll.user32.SetWindowPos(
                _hwnd, 0, _drag["ox"] + dx, _drag["oy"] + dy, 0, 0, 0x0001 | 0x0004)

    def drag_end(self):
        global _drag
        _drag = None
        if _hwnd and _is_capsule and sys.platform == "win32":
            import ctypes
            # 拖拽释放后，强化一次始终置顶
            ctypes.windll.user32.SetWindowPos(_hwnd, -1, 0, 0, 0, 0, 0x0002 | 0x0001 | 0x0010)

    def resize_begin(self, left, top, right, bottom):
        pass

    def resize_move(self):
        pass

    def resize_end(self):
        pass


def _start_server(server_socket):
    """使用预先绑定的 socket 启动 uvicorn，避免端口探测/监听之间的竞态。"""
    try:
        config = uvicorn.Config(
            app, host="127.0.0.1", port=server_socket.getsockname()[1],
            log_level="warning", log_config=None)
        uvicorn.Server(config).run(sockets=[server_socket])
    except BaseException as e:
        # SystemExit 也记录下来；socket 已由本函数持有，若 uvicorn 启动失败，
        # main 侧 _wait_port 会超时并进入错误分支，而不是加载死链接。
        log("SERVER ERROR: " + repr(e))
    finally:
        try:
            server_socket.close()
        except OSError:
            pass


_single_instance_mutex = None


def _activate_existing_window():
    """查找并唤醒已存在的 TokenViewer Pro 窗口至最前台"""
    if sys.platform != "win32":
        return
    import ctypes
    from ctypes import wintypes
    user32 = ctypes.windll.user32

    hwnd = user32.FindWindowW(None, "TokenViewer Pro")
    if not hwnd:
        found = []
        EnumWindowsProc = ctypes.WINFUNCTYPE(
            wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

        def cb(h, _lp):
            if user32.IsWindowVisible(h):
                n = user32.GetWindowTextLengthW(h)
                if n > 0:
                    buf = ctypes.create_unicode_buffer(n + 1)
                    user32.GetWindowTextW(h, buf, n + 1)
                    if "TokenViewer Pro" in buf.value:
                        found.append(h)
            return True

        user32.EnumWindows(EnumWindowsProc(cb), 0)
        if found:
            hwnd = found[0]

    if hwnd:
        try:
            if user32.IsIconic(hwnd):
                user32.ShowWindow(hwnd, 9)  # SW_RESTORE
            else:
                user32.ShowWindow(hwnd, 5)  # SW_SHOW
            user32.SetForegroundWindow(hwnd)
            user32.BringWindowToTop(hwnd)
            log(f"Activated existing window: hwnd={hwnd}")
        except Exception as e:
            log("activate existing window error: " + repr(e))


def ensure_single_instance():
    """确保单实例运行：若已有进程运行，唤醒已有窗口并立即退出当前进程。"""
    global _single_instance_mutex
    if sys.platform != "win32":
        return True
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        MUTEX_NAME = "Local\\TokenViewerPro_SingleInstance_Mutex"
        mutex = kernel32.CreateMutexW(None, False, MUTEX_NAME)
        last_error = kernel32.GetLastError()
        # 183 = ERROR_ALREADY_EXISTS
        if last_error == 183 or not mutex:
            log("Single instance check: Another instance already running. Activating window and exiting.")
            for _ in range(3):
                _activate_existing_window()
                time.sleep(0.15)
            if mutex:
                kernel32.CloseHandle(mutex)
            os._exit(0)
        _single_instance_mutex = mutex
        return True
    except SystemExit:
        os._exit(0)
    except Exception as e:
        log("single instance check exception: " + repr(e))
        return True


def main():
    global window
    log("main start")
    ensure_single_instance()
    server_socket = find_free_port()
    if server_socket is None:
        log("no free port")
        return
    port = server_socket.getsockname()[1]
    log("port=" + str(port))

    threading.Thread(target=_start_server, args=(server_socket,), daemon=True).start()
    ok = _wait_port(port)
    log("port ready: " + str(ok))
    if not ok:
        server_socket.close()
        webbrowser.open("about:blank")
        return
    # 读取上次保存的窗口尺寸（逻辑像素，与 webview create_window 同单位），
    # 保证调整过的窗口大小下次打开不恢复默认；并钳制到屏幕工作区内，
    # 固定初始窗口尺寸（600x780），不可拉伸，保证界面比例与美观一致性
    width = 1160
    height = 730
    log("win size fixed = %dx%d" % (width, height))
    try:
        api = JsApi()
        window = webview.create_window(
            "TokenViewer Pro", f"http://127.0.0.1:{port}/?v={UI_REVISION}",
            width=width, height=height, resizable=True, frameless=True, easy_drag=False,
            transparent=True, background_color="#000000", min_size=(180, 36), js_api=api)
        window.events.closing += _exit_now

        def _on_loaded():
            log("window loaded event fired: reinforcing backdrop")
            _apply_backdrop()
            _prime_backdrop_surface()

        window.events.before_show += _setup_window
        window.events.loaded += _on_loaded
        window.events.restored += _queue_backdrop_refresh
        # storage_path：WebView2 持久数据目录固定到 ~/.codex/token_viewer_webview，
        # 避免每次启动重建浏览器环境，显著加快后续启动。
        webview.start(private_mode=False, storage_path=os.path.join(
            os.path.expanduser("~"), ".codex", "token_viewer_webview"))
        log("webview returned")
    except Exception as e:
        log("WEBVIEW FAIL: " + repr(e))
        # WebView2 不可用时保留 daemon 服务线程并打开系统浏览器；不能立刻
        # os._exit，否则浏览器兜底页面还没有加载完服务就会一起退出。
        webbrowser.open("http://127.0.0.1:" + str(port))
        while _wait_port(port, timeout=1):
            time.sleep(1)
        log("browser fallback: server stopped")
    os._exit(0)


if __name__ == "__main__":
    main()
