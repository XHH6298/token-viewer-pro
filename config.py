"""配置：路径、默认定价、时间档位。"""
import os
from pathlib import Path

HOME = Path.home()
CODEX_DIR = HOME / ".codex"
SESSIONS_DIR = CODEX_DIR / "sessions"
ARCHIVED_DIR = CODEX_DIR / "archived_sessions"
ANTIGRAVITY_DIR = HOME / ".gemini" / "antigravity"
ANTIGRAVITY_CONVERSATIONS_DIR = ANTIGRAVITY_DIR / "conversations"

DB_PATH = Path(os.environ.get(
    "TOKEN_VIEWER_DB", HOME / ".codex" / "token_viewer.db"))

# 默认模型定价（每百万 token，USD）。
# 基准：主流大模型 API 挂牌价（标准在线按量价；GLM/豆包为官方人民币按
# ¥7.2 折算的美元参考值）。缓存读取默认取输入价 10%，缓存写入取输入价 125%，
# 个别模型按官方标注覆盖。数值可在运行时于 UI 维护；此处是"未定制模型"的默认值，
# 用户手工改过的定价（updated_at 非空）不会被覆盖。
def _price(inp, out, cache_read=None, cache_creation=None):
    return {"input": inp, "output": out,
            "cache_read": round(inp * 0.1, 4) if cache_read is None else cache_read,
            "cache_creation": round(inp * 1.25, 4) if cache_creation is None else cache_creation}

DEFAULT_PRICING = {
    # OpenAI Flagship & Reasoning (GPT-6 / GPT-5 / o-series)
    "gpt-6-astra":              _price(10.00, 50.00, cache_read=1.00, cache_creation=12.50),
    "gpt-6":                    _price(3.00, 15.00, cache_read=0.75),
    "gpt-6-mini":               _price(0.25, 1.00, cache_read=0.06),
    "gpt-6-codex":              _price(3.00, 15.00, cache_read=0.75),
    "gpt-5.3":                  _price(2.50, 10.00, cache_read=0.625),
    "gpt-5.3-codex":            _price(2.50, 10.00, cache_read=0.625),
    "gpt-5.2":                  _price(2.50, 10.00, cache_read=0.625),
    "gpt-5":                    _price(2.50, 10.00, cache_read=1.25),
    "gpt-5-codex":              _price(2.50, 10.00, cache_read=1.25),
    "o4":                       _price(5.00, 20.00, cache_read=2.50),
    "o4-mini":                  _price(1.10, 4.40, cache_read=0.55),
    "o3":                       _price(5.00, 20.00, cache_read=2.50),
    "o3-mini":                  _price(1.10, 4.40, cache_read=0.55),
    "o1":                       _price(15.00, 60.00, cache_read=7.50),
    "o1-mini":                  _price(1.10, 4.40, cache_read=0.55),
    "o1-preview":               _price(15.00, 60.00, cache_read=7.50),
    "gpt-4.5-preview":          _price(75.00, 150.00, cache_read=37.50),
    "gpt-4o":                   _price(2.50, 10.00, cache_read=1.25),
    "gpt-4o-2024-11-20":        _price(2.50, 10.00, cache_read=1.25),
    "gpt-4o-mini":              _price(0.15, 0.60, cache_read=0.075),
    "gpt-4-turbo":              _price(10.00, 30.00),
    "gpt-4":                    _price(30.00, 60.00),
    "gpt-3.5-turbo":            _price(0.50, 1.50),
    # Anthropic Claude 3 / 3.5 / 3.7 Official Pricing & Prompt Caching
    "claude-3-7-sonnet":            _price(3.00, 15.00, cache_read=0.30, cache_creation=3.75),
    "claude-3-7-sonnet-20250219":   _price(3.00, 15.00, cache_read=0.30, cache_creation=3.75),
    "claude-3-7-sonnet-thinking":   _price(3.00, 15.00, cache_read=0.30, cache_creation=3.75),
    "claude-3-5-sonnet":            _price(3.00, 15.00, cache_read=0.30, cache_creation=3.75),
    "claude-3-5-sonnet-20241022":   _price(3.00, 15.00, cache_read=0.30, cache_creation=3.75),
    "claude-3-5-sonnet-20240620":   _price(3.00, 15.00, cache_read=0.30, cache_creation=3.75),
    "claude-3-5-haiku":             _price(0.80, 4.00, cache_read=0.08, cache_creation=1.00),
    "claude-3-5-haiku-20241022":    _price(0.80, 4.00, cache_read=0.08, cache_creation=1.00),
    "claude-3-opus":                _price(15.00, 75.00, cache_read=1.50, cache_creation=18.75),
    "claude-3-opus-20240229":       _price(15.00, 75.00, cache_read=1.50, cache_creation=18.75),
    "claude-3-sonnet":              _price(3.00, 15.00, cache_read=0.30, cache_creation=3.75),
    "claude-3-haiku":               _price(0.25, 1.25, cache_read=0.025, cache_creation=0.30),
    # Anthropic Extended / Next-Gen Aliases
    "claude-opus-4-6-thinking":     _price(15.00, 75.00, cache_read=1.50, cache_creation=18.75),
    "claude-opus-4-6":              _price(15.00, 75.00, cache_read=1.50, cache_creation=18.75),
    "claude-opus-4-5":              _price(15.00, 75.00, cache_read=1.50, cache_creation=18.75),
    "claude-sonnet-4-6-thinking":   _price(3.00, 15.00, cache_read=0.30, cache_creation=3.75),
    "claude-sonnet-4-6":            _price(3.00, 15.00, cache_read=0.30, cache_creation=3.75),
    "claude-sonnet-4-5":            _price(3.00, 15.00, cache_read=0.30, cache_creation=3.75),
    "claude-haiku-4-5":             _price(0.80, 4.00, cache_read=0.08, cache_creation=1.00),
    # Google Gemini Official Standard & 2.x/1.5 Pricing
    "gemini-2.5-pro":               _price(1.25, 10.00, cache_read=0.125),
    "gemini-2.5-flash":             _price(0.30, 2.50, cache_read=0.03),
    "gemini-2.5-flash-lite":        _price(0.10, 0.40, cache_read=0.01),
    "gemini-2.0-flash":             _price(0.10, 0.40, cache_read=0.025),
    "gemini-2.0-flash-exp":         _price(0.10, 0.40, cache_read=0.025),
    "gemini-2.0-flash-thinking-exp": _price(0.10, 0.40, cache_read=0.025),
    "gemini-2.0-flash-lite":        _price(0.075, 0.30, cache_read=0.01875),
    "gemini-2.0-pro":               _price(1.25, 5.00, cache_read=0.3125),
    "gemini-2.0-pro-exp-02-05":     _price(1.25, 5.00, cache_read=0.3125),
    "gemini-1.5-pro":               _price(1.25, 5.00, cache_read=0.3125),
    "gemini-1.5-flash":             _price(0.075, 0.30, cache_read=0.01875),
    "gemini-1.5-flash-8b":          _price(0.0375, 0.15, cache_read=0.009375),
    # Google Antigravity & Experimental Presets
    "gemini-3.8-flash":             _price(1.50, 7.50, cache_read=0.15),
    "gemini-3.8-pro":               _price(2.00, 12.00, cache_read=0.20),
    "gemini-3.7-flash":             _price(1.50, 7.50, cache_read=0.15),
    "gemini-3.7-pro":               _price(2.00, 12.00, cache_read=0.20),
    "gemini-3.1-pro":               _price(2.00, 12.00, cache_read=0.20),
    "gemini-3.1-flash":             _price(1.50, 7.50, cache_read=0.15),
    # DeepSeek V3 / R1 Official Pricing
    "deepseek-chat":                _price(0.14, 0.28, cache_read=0.014),
    "deepseek-reasoner":            _price(0.55, 2.19, cache_read=0.14),
    "deepseek-v3":                  _price(0.14, 0.28, cache_read=0.014),
    "deepseek-r1":                  _price(0.55, 2.19, cache_read=0.14),
    # DeepSeek V4.1（deepseek-flash 挂牌峰值价；旧名 v4-flash 已由 V4.1-Flash 接管）
    "deepseek-v4.1-flash":          _price(0.15, 0.60, cache_read=0.003),
    "deepseek-v4-pro":              _price(0.66, 1.98, cache_read=0.022),
    "deepseek-v4-flash":            _price(0.15, 0.60, cache_read=0.003),
    # xAI Grok
    "grok-2":                       _price(2.00, 10.00),
    "grok-2-mini":                  _price(0.20, 1.00),
    "grok-beta":                    _price(5.00, 15.00),
    "grok-4.5":                     _price(2.00, 6.00),
    # 阿里通义千问 (Qwen)
    "qwen-max":                     _price(1.60, 6.40),
    "qwen-plus":                    _price(0.40, 1.20),
    "qwen-turbo":                   _price(0.05, 0.20),
    "qwen-2.5-coder-32b":           _price(0.20, 0.60),
    "qwen-2.5-coder-72b":           _price(0.40, 1.20),
    "qwen3.8-max":                  _price(2.00, 6.00),
    "qwen3.7-max":                  _price(1.25, 3.75),
    # Moonshot Kimi
    "moonshot-v1-8k":               _price(1.60, 1.60),
    "moonshot-v1-32k":              _price(3.20, 3.20),
    "moonshot-v1-128k":             _price(8.00, 8.00),
    "kimi-k3":                      _price(3.00, 15.00, cache_read=0.30),
    "kimi-k2.5":                    _price(0.60, 3.00),
    # 智谱 GLM
    "glm-4-plus":                   _price(1.40, 1.40),
    "glm-4-flash":                  _price(0.01, 0.01),
    "glm-4-long":                   _price(0.14, 0.14),
    "glm-5":                        _price(0.56, 2.50),
    "glm-5.3-flash":                _price(0.15, 0.50, cache_read=0.03),
    # 字节豆包 / 火山方舟
    "doubao-seed-2.1-pro":          _price(0.83, 4.17, cache_read=0.17),
    "doubao-seed-2.1-turbo":        _price(0.42, 2.08),
    "doubao-seed-2.0-pro":          _price(0.44, 2.22),
    "doubao-seed-2.0-mini":         _price(0.03, 0.28),
}


# 时间档位：preset -> 回看秒数（None 表示当天 0 点起）
TIME_RANGE_PRESETS = [
    ("today", None),
    ("1d", 86400),
    ("3d", 86400 * 3),
    ("7d", 86400 * 7),
    ("30d", 86400 * 30),
    ("180d", 86400 * 180),
    ("365d", 86400 * 365),
    ("all", None),
]
TIME_RANGE_MAP = dict(TIME_RANGE_PRESETS)

# 默认时区（与 Codex turn_context 一致）
DEFAULT_TZ = "Asia/Hong_Kong"

# ?????????????????????
SUBSCRIPTION_URL = (
    "https://console.volcengine.com/ark/region:cn-beijing/"
    "subscription/coding-plan?agentMode=close"
)

