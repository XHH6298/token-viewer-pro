# TokenViewer Pro

<p align="left">
  <a href="README.md">English</a> | <b>简体中文</b>
</p>

一款专为本地 AI 编程智能体打造的高颜值**空间毛玻璃**桌面监控仪表盘。聚合 **Codex CLI、Claude Code、ZCode、Pi 与 Antigravity** 五大主流 AI 编程 Agent 的 Token 实时用量与成本核算，呈现宛如 macOS / VisionOS 的极致视觉交互。

![界面预览](docs/screenshot.png)

## 功能亮点

- **五大 Agent 一屏掌握** — 深度适配各 Agent 的本地会话日志与 SQLite 数据库，汇聚为标准化的统一事件流。
- **实时用量捕获** — 毫秒级后台扫描器实时监听日志变动；内置 10 秒活跃呼吸灯，模型调用动态一目了然。
- **精细化成本分析** — 内置各模型百万 Token 单价表（支持在界面内直接编辑维护），精确拆解全新输入（Fresh Input）、缓存读取（Cache Read）、缓存写入（Cache Write）与输出（Output）。
- **缓存命中率统计** — 针对具备 Prompt Caching 的模型独立折算缓存利用率，直观洞察上下文缓存节省效果。
- **多维度时间范围** — 支持 今天 / 24小时 / 7天 / 30天 / 全部 视图，提供小时级与天级趋势折线，自动标记峰值（Peak）。
- **项目与占比透视** — 甜甜圈图直观呈现各 Agent 及项目 Token 占比，支持下钻查看会话详情与工作目录。
- **双语与双主题适配** — 界面原生支持简中/英文一键热切换；自动感知 Windows 系统注册表的主题变化，无缝同步深色/浅色毛玻璃外观。
- **自愈式毛玻璃与液态流体微光** — 深度整合 Windows 11 DWM 焦点状态自愈机制与 Apple Liquid Glass 空间微光层，彻底杜绝窗口失焦时的平铺死灰感，任何时刻均保持通透灵动。

## 支持的 Agent 与数据源

所有数据读取均为**严格只读（Read-Only）**，绝不修改、覆盖或删除各 Agent 本身的任何日志与数据。

| Agent | 数据读取源 |
|---|---|
| Codex CLI | `~/.codex/sessions/` 与 `~/.codex/archived_sessions/` (rollout JSONL) |
| Claude Code | `~/.claude/projects/**/*.jsonl` |
| ZCode | `~/.zcode/cli/db/db.sqlite` (`model_usage` 数据表) |
| Pi | `~/.pi/agent/sessions/**/*.jsonl` |
| Antigravity | `~/.gemini/antigravity/conversations/*.db` |

本工具自身聚合缓存存储于 `~/.codex/token_viewer.db`（SQLite WAL 模式），实现亚毫秒级的历史分析与极速检索。

## 隐私与安全承诺

- **严格绑定本地** — Web 服务仅监听 `127.0.0.1` 环回地址，不暴露于局域网或公网。
- **防御 DNS 重新绑定（DNS Rebinding）** — 服务端强制校验 HTTP `Host` 标头，拒绝一切非 loopback 来源的跨站恶意探测，杜绝浏览器其他恶意网页偷取本地数据。
- **纯本地运行** — 所有日志解析、聚合运算与视图渲染均在本地机器完成，绝不向任何外部服务器上传数据。

## 安装与运行

### 环境要求
- **Python 3.11+**（已在 3.13 验证）
- **Windows**（托盘图标与窗口透明交互采用 Win32 API；未安装 WebView2 时会自动降级调用默认浏览器打开）

### 极速启动

```bash
git clone https://github.com/XHH6298/token-viewer-pro.git
cd token-viewer-pro
pip install -r requirements.txt
python app.py
```

启动后将弹出一个透明毛玻璃视窗。若当前环境缺少 WebView2，程序将自动在默认浏览器中打开 `http://127.0.0.1:<端口>`。

### 打包为独立绿色版 EXE（可选）

```powershell
.\package.ps1
```

脚本将调用 PyInstaller 打包生成独立绿色文件夹 `dist\TokenViewerPro\TokenViewerPro.exe`，并通过 `make_shortcut.ps1` 自动在桌面及开始菜单创建快捷方式。

## 配置项

支持通过环境变量自定义配置（均为可选）：

| 环境变量 | 默认值 | 用途说明 |
|---|---|---|
| `TOKEN_VIEWER_DB` | `~/.codex/token_viewer.db` | 本工具专用的 SQLite 聚合数据库存储路径 |
| `TOKEN_VIEWER_LOG` | `~/.codex/token_viewer.log` | 应用程序日志输出文件路径 |
| `TOKEN_VIEWER_BACKDROP` | `3` (Acrylic) | Windows 11 背板材质类型：`3` 为 Acrylic 亚克力透视，`4` 为 Mica Alt（失焦不降级纯灰） |

## 运行自动化测试

```bash
python test_core.py
```

覆盖各 Agent 解析适配器、不同 Agent 之间的缓存计数语义差异、模型成本折算公式，以及确保多次全量重新扫描不产生重复数据的幂等性去重逻辑。

## 技术架构

- **后端引擎**：FastAPI + uvicorn（多线程运行），轻量级 SQLite 存储层，具备自动数据表迁移能力。
- **幂等去重设计**：事件以 `(agent_type, session_id, turn_id)` 联合主键为索引；对缺失 turn_id 的事件采用字段指纹回退机制；对 Claude 多行流式响应做分块去重，即使多次全量重扫依然保持绝对幂等（`INSERT OR IGNORE`）。
- **语义严谨性**：Codex / ZCode / Pi 上报的 `input_tokens` **包含**缓存读取量（OpenAI 语义）；而 Claude / Antigravity 则将全新输入与缓存命中分开上报（Anthropic 语义）。本工具底层针对不同 Agent 执行差异化的 Token 与成本公式折算。
- **前端架构**：原生 Vanilla JS + Chart.js v4（内置 vendored，MIT 许可证）；全面采用 CSS 变量与 Backdrop Filter 实现高质感高斯模糊；主题切换时 Canvas 图表能够实时重读变量色彩。

## 开源协议

本项目基于 [MIT](LICENSE) 许可证开源。
