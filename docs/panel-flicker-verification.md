# 面板切换闪烁修复（2026-10-02）

问题：从其他菜单返回仪表盘，或切换到设置时，深色玻璃面板先变浅再恢复深色。

原因：`.view-panel` 对整页应用 200ms 的透明度渐入。子面板使用 `backdrop-filter`，父级透明度从小于 1 变为 1 时，背景取样边界发生变化。实测动画 100ms 时页面透明度约 0.685，面板明显偏浅；200ms 结束后恢复深色。

修复：移除整页透明度渐入及其未使用的关键帧。菜单切换直接显示最终深色面板，保留原有玻璃背景、卡片悬停反馈和启动动画。新版本的页面 URL、CSS URL 带资源版本标识，HTML 返回 `Cache-Control: no-store`，防止持久 WebView2 缓存继续使用旧样式。

验证：

- 真实 WebView2 中，从模型监控、Token 用量、调用日志分别返回仪表盘，以及仪表盘切换设置：每条路径采样 15 个渲染帧，页面透明度始终为 1，无整页动画。
- 90%、100%、110% 三个缩放档位下反复切换仪表盘与设置，共 24 次切换，未发现透明度变化或 JavaScript 错误。
- 视觉检查仪表盘小组件和模型定价维护表，均直接显示最终深色背景。
- 使用正常浏览器缓存复查，确认加载带新版标识的 CSS，而非旧的 `fadeIn` 样式。
- 本次不重复执行统计、日志解析和费用计算测试；相关业务逻辑未修改。

背景取样规则参考：[MDN backdrop-filter](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/backdrop-filter#backdrop_root)。

源代码备份：`D:\Desktop\Codex Work\back\tokenviewer-pro-panel-flicker-20261002\style.css`。
